# Deps
import asyncio
from typing import Annotated
from fastapi import APIRouter, HTTPException, Header, Request, Response, status
from prisma import Prisma
import bcrypt
import base64
from google.auth import jwt as g_jwt

# Helpers
from src.routes.helpers.configs import reset_password_messages, confirm_email_message
from src.routes.helpers.emailSender import send_email
from src.routes.helpers.methods import generate_4_digit_pin

# Models
from src.routes.models.auth import (
    RegisterModel,
    ResetPaswordModel,
    SendMagicLinkModel,
    LoginModel,
    JWTFUSerLogin,
    SecretPINVerification,
    RegisterByJWT
)

authRouter = APIRouter()

def salt_password(password):
    password = password
    bytes_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash_password_bytes = bcrypt.hashpw(bytes_password, salt)

    return base64.b64encode(hash_password_bytes).decode("utf-8")

# TODO: Is this really secure? We need to test this to break, this can affect registation and the way we are making the passwords
@authRouter.post("/auth/login", tags=["auth"])
async def read_users(loginBody: LoginModel):
    db = Prisma()
    await db.connect()

    user = await db.user.find_unique(where={"email": loginBody.email})
    decoded_bytes = base64.b64decode(user.password)

    if user and bcrypt.checkpw(loginBody.password, decoded_bytes):
        await db.disconnect()
        return [{"message": "User logged successfully", "status": 200}]
    
    else:
        await db.disconnect()
        return [{"message": "Password or username does not exist", "code": 404}]

# TODO: Validate that all the requirements are met in relation to fields, not only nickname (Frontend Doing this)
# FIXME: A secret pin is created in SecretPins table, this isn't right. I think we should delete the conncetion between these tables

# TODO: (DONE) This one should return the user ID to save it in the frontend, then in we will save this in the localStore of Frontend to use it
# later
@authRouter.post("/auth/register", tags=["auth"])
async def read_user(regisBody: RegisterModel):
    print(regisBody)
    db = Prisma()
    await db.connect()
    
    nickname_exist = await db.user.find_unique(
        where={"nickname": regisBody.nickname}
    )
    
    email_exist = await db.user.find_unique(
        where={"email": regisBody.email}
    )
    
    final_user = None
    
    if nickname_exist or email_exist:
        await db.disconnect()
        return {"message": "User already exist", "status": 409}

    try:
        regisBody.password = salt_password(regisBody.password)

        await db.user.create(data=regisBody.model_dump(exclude_none=True))
        
        final_user = await db.user.find_unique(where={"email": regisBody.email})

        await db.disconnect()
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return {"message": "User created", "status": 200, "payload": {
        "user_id": final_user.id,
        "user_nickname": final_user.nickname,
        "user_email":final_user.email
    }}

## Create Magic Links - PIN
async def delete_pin_after_delay(user_id: int, delay: int = 600):
    await asyncio.sleep(delay)
    db = Prisma()
    await db.connect()
    await db.secretpins.delete(where={"user_id": user_id})
    await db.disconnect()
    print(f"Pin for user_id {user_id} deleted after {delay} seconds")

@authRouter.post("/auth/magic-link", tags=["auth"])
async def read_user(magicLinkRestBody: SendMagicLinkModel):
    db = Prisma()
    await db.connect()
    user = await db.user.find_unique(where={"email": magicLinkRestBody.email})
    
    if magicLinkRestBody.verification_type is None:
        await db.disconnect()
        raise HTTPException(status_code=400, detail="Verification type is required")
    
    if user is not None:
        exist_pin = await db.secretpins.find_unique(where={"user_id": user.id})
        
        if exist_pin:
            await db.secretpins.delete(where={"user_id": user.id})
            print("Pin found it, process to delete and create a new one")     
        
        pin = generate_4_digit_pin()
        
        if magicLinkRestBody.verification_type == "confirm-email":
            email_subject_body = confirm_email_message(pin)
        elif magicLinkRestBody.verification_type == "reset-password":
            email_subject_body= reset_password_messages(pin)
        else:
            await db.disconnect()
            raise HTTPException(status_code=400, detail="Invalid verification type")
             
        await db.secretpins.create(data={"user_id": user.id, "pin": pin})
        send_email(
            magicLinkRestBody.email,
            email_subject_body["subject"],
            email_subject_body["body"],
        )
        asyncio.create_task(delete_pin_after_delay(user.id, 600))
        
        await db.disconnect()
        return {
            "message": f"Pin for {magicLinkRestBody.verification_type} was sent to {magicLinkRestBody.email}, please check your email.",
            "code": 200,
        }


# As note, we are doing the validation of pin in the Frontend, right now we need to create
# Alerts when the pin is already created and it is valid to not create another one until it expires or the user comsumes
# There is an error with the stepper

@authRouter.post("/auth/pin-verification", tags=["auth"])
async def read_user(verificationPin: SecretPINVerification):
    
    db = Prisma()
    await db.connect()
    
    if verificationPin.email is None or verificationPin.user_pin is None:
        await db.disconnect()
        return {"message": "Email and pin are required", "status": 400}

    user_id_exist = await db.user.find_unique(where={"email": verificationPin.email})
    pin_exist = await db.secretpins.find_unique(where={"user_id": user_id_exist.id, "pin": verificationPin.user_pin})
    
    if pin_exist:
        await db.secretpins.delete(where={"user_id": user_id_exist.id, "pin": verificationPin.user_pin})
        await db.disconnect()
        return {"message": "PIN is valid, user can continue","is_valid_pin":True, "status": 200}
    else:
        await db.disconnect()
        return {"message": "PIN is invalid, please try again","is_valid_pin":False, "status": 404}
    
# Frontend should check password validation
@authRouter.post("/auth/reset-password", tags=["auth"])
async def read_user(resetPassBody: ResetPaswordModel):
    
    db = Prisma()
    await db.connect()

    new_password = salt_password(resetPassBody.new_password)

    await db.user.update(
        where={"id": resetPassBody.user_id}, data={"password": new_password}
    )

    await db.disconnect()
    return [{"message": "auth-magic-link", "code": 200}]


# JWT AUTHENTICATION - Route
async def check_user_exist(jwt_user_token):
    db = Prisma()
    try:
        await db.connect()

        user_exist = await db.user.find_unique(where={"email": jwt_user_token["email"]})

        if user_exist:
            print('User exists')
            return 'User already exists', 409
        
        google_user = {
            "email": jwt_user_token["email"],
            "nickname": jwt_user_token["given_name"],
            "google_picture_src": jwt_user_token["picture"],
            "password": ""
        }

        await db.user.create(data=google_user)
        
        print('User created')
        return 'User created', 200

    except Exception as e:
        print(f"Error: {e}")
        return 'Internal Server Error', 500

    finally:
        await db.disconnect()
# Here there is an problem, in Frontend for any reason we can't get the response description
# This is an GET just for now while I find a better solutions for this one
@authRouter.get("/auth/jwt-auth-registration", tags=["auth"], status_code=204)
async def jwt(request: Request, response: Response):
    try:
        jwt_user_token = g_jwt.decode(request.headers.get('authorization'), verify=False)
        response_description, status_code = await check_user_exist(jwt_user_token)
        response.status_code = status_code
        return {"message": response_description, "status": status_code, "payload":{
            "user_email": jwt_user_token["email"],
        }}
    except Exception as e:
        response.headers['response_description'] = str(e)
        response.status_code = 500