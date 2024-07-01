# Deps
import asyncio
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from prisma import Prisma
import bcrypt
import base64
from google.auth import jwt

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
    SecretPINVerification,
    RegisterGoogleUser
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
    
@authRouter.post("/auth/google-auth", tags=["auth"])
async def jwt(googleUser: RegisterGoogleUser):
    db = Prisma()
    await db.connect()
    print(googleUser)
    user = await db.user.find_unique(where={"email": googleUser.email})

    if user:
        await db.disconnect()
        return {"message": "backend.user_exist", "messageType":"warning", "status": 409, "user_exist": True, "user_completed_registration": user.user_completed_registration}
            
    match googleUser.auth_method:
        case "register":
            await db.user.create(data={
            "nickname": googleUser.name, 
            "email": googleUser.email, 
            "user_image": googleUser.picture,
            })
            await db.disconnect()
            return {"message": "backend.user_created", "messageType":"success", "status": 200, "user_created": True}
        case _:
            await db.disconnect()
            return {"message": "backend.invalid_method", "messageType":"error","status": 400}
    
# Possbiles features to implement
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