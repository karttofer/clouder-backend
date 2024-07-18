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

@authRouter.post("/auth/login", tags=["auth"])
async def read_users(loginBody: LoginModel):
    db = Prisma()
    await db.connect()

    user = await db.user.find_unique(where={"email": loginBody.email})
    
    if user == None:
        await db.disconnect()
        return {"message": "backend.user_does_not_exist","messageType": "error", "code": 404}
    
    if user.user_completed_registration == False:
        await db.disconnect()
        return {"message": "backend.user_registration_not_completed","messageType": "warning", "user_completed_registration": user.user_completed_registration,"user_email":user.email, "status": 400}
    
    if user and user.user_completed_registration:
        db.disconnect()
        return {"message": "backend.user_logged_successfully","messageType": "success", "user_completed_registration": user.user_completed_registration,"status": 200}

@authRouter.post("/auth/register", tags=["auth"])
async def read_user(regisBody: RegisterModel):
    db = Prisma()
    await db.connect()
    
    nickname_exist = await db.user.find_unique(where={"nickname": regisBody.nickname})
    email_exist = await db.user.find_unique(where={"email": regisBody.email})
    
    if nickname_exist or email_exist:
        await db.disconnect()
        return {"message": "backend.user_exist", "messageType":"warning", "status": 409}
    
    await db.user.create(data={"nickname": regisBody.nickname, "email": regisBody.email})
    
    user_created = await db.user.find_unique(where={"email": regisBody.email})

    return {"message": "backend.user_created", "messageType":"success", "status": 200,"user": { "email":user_created.email, "nickname":user_created.nickname, "user_id": user_created.id, "user_completed_registration": user_created.user_completed_registration },"user_created": True}

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
    
    if verificationPin.email == None or verificationPin.user_pin == None:
        await db.disconnect()
        return {"message": "Email and pin are required", "status": 400}

    user_id_exist = await db.user.find_unique(where={"email": verificationPin.email})
    
    if user_id_exist == None:
        await db.disconnect()
        return {"message": "User does not exist", "status": 404}
    
    pin_exist = await db.secretpins.find_unique(where={"user_id": user_id_exist.id, "pin": verificationPin.user_pin})
    
    if pin_exist:
        await db.secretpins.delete(where={"user_id": user_id_exist.id, "pin": verificationPin.user_pin})
        await db.disconnect()
        return {"message": "PIN is valid, user can continue","is_valid_pin":True, "status": 200}
    else:
        await db.disconnect()
        return {"message": "PIN is invalid, please try again","is_valid_pin":False, "status": 404}
    
@authRouter.post("/auth/google-auth", tags=["auth"])
async def googleAuth(googleUser: RegisterGoogleUser):
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
            "nickname": googleUser.nickname, 
            "email": googleUser.email, 
            "user_image": googleUser.picture,
            })
            await db.disconnect()
            return {"message": "backend.user_created", "messageType":"success", "status": 200, "user_created": True}
        case _:
            await db.disconnect()
            return {"message": "backend.invalid_method", "messageType":"error","status": 400}
    

    new_password = salt_password(resetPassBody.new_password)

    await db.user.update(
        where={"id": resetPassBody.user_id}, data={"password": new_password}
    )

    await db.disconnect()
    return [{"message": "auth-magic-link", "code": 200}]