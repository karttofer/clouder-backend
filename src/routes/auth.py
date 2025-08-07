# Deps
import asyncio
from typing import Annotated
from urllib import request

from fastapi import APIRouter, HTTPException, status
from prisma import Prisma
import bcrypt
import base64
from google.auth import jwt
from prisma.errors import UniqueViolationError

# Helpers
from src.routes.helpers.emailConfigs import confirm_email_message
from src.routes.helpers.emailSender import send_email
from src.routes.helpers.methods import generate_4_digit_pin

# Models
from src.routes.models.auth import (
    RegisterModel,
    ResetPaswordModel,
    SendMagicLinkModel,
    LoginModel,
    SecretPINVerification,
    RegisterGoogleUser,
    IsLoggedUser,
    ChangeIsLogged
)

authRouter = APIRouter()


# Methods / Helpers
async def delete_pin_after_delay(user_id: int, delay: int = 600):
    await asyncio.sleep(delay)
    db = Prisma()
    await db.connect()
    await db.secretpins.delete(where={"user_id": user_id})
    await db.disconnect()
    print(f"Pin for user_id {user_id} deleted after {delay} seconds")


# Routes
@authRouter.post("/auth/login", tags=["auth"])
async def read_users(loginBody: LoginModel):
    db = Prisma()
    await db.connect()

    user = await db.user.find_unique(where={"email": loginBody.email})

    if user == None:
        await db.disconnect()
        return {
            "message": "backend.user_does_not_exist",
            "messageType": "error",
            "code": 404,
        }

    if user.registration_completed == False:
        await db.disconnect()
        return {
            "message": "backend.user_registration_not_completed",
            "messageType": "warning",
            "registration_completed": user.registration_completed,
            "user_email": user.email,
            "status": 400,
        }

    if user and user.registration_completed:
        db.disconnect()
        return {
            "message": "backend.user_logged_successfully",
            "messageType": "success",
            "userInfo": {
                "registration_completed": user.registration_completed,
                "email": user.email
            },
            "status": 200,
        }


@authRouter.post("/auth/register", tags=["auth"])
async def read_user(regisBody: RegisterModel):
    db = Prisma()
    await db.connect()

    if regisBody.roleId is None:
        return {
            "message": "backend.invalid_method",
            "messageType": "error",
            "status": 500,
        }

    user_exist = await db.user.find_unique(where={"email": regisBody.email})

    if user_exist:
        await db.disconnect()
        return {
            "message": "backend.user_exist",
            "messageType": "warning",
            "status": 409,
        }

    await db.user.create(
        data={
            "nickname": regisBody.name,
            "email": regisBody.email,
            "registration_completed": False,
            "roleId": regisBody.roleId
        }
    )

    user_created = await db.user.find_unique(where={"email": regisBody.email})

    await db.loggedusers.create(
        data={
            "user_id": user_created.id,
            "isLogged": False
        }
    )

    return {
        "message": "backend.user_created",
        "messageType": "success",
        "status": 200,
        "user": {
            "email": user_created.email,
            "nickname": user_created.nickname,
            "user_id": user_created.id,
            "roleId": user_created.roleId,
            "registration_completed": user_created.registration_completed,
        },
        "user_created": True,
    }


@authRouter.post("/auth/user-logged", tags=["auth"])
async def is_user_logged(isLogged: IsLoggedUser):
    db = Prisma()
    await db.connect()

    user = await db.user.find_unique(where={"email": isLogged.email})

    if user == None:
        await db.disconnect()
        return {
            "message": "backend.user_does_not_exist",
            "messageType": "error",
            "status": 404,
        }

    loggedUser = await db.loggedusers.find_unique(where={"user_id": user.id})

    if loggedUser.isLogged:
        await db.disconnect()
        return {
            "message": "backend.user_logged_successfully",
            "isLogged": True,
            "messageType": "success",
            "status": 200,
        }

    await db.disconnect()
    return {
        "message": "backend.user_registration_not_completed",
        "messageType": "warning",
        "isLogged": True,
        "status": 200,

    }


@authRouter.put("/auth/user-logged", tags=["auth"])
async def set_user_logged(isLoggedProps: ChangeIsLogged):
    db = Prisma()
    await db.connect()

    user = await db.user.find_unique(where={"email": isLoggedProps.email})

    if user == None:
        await db.disconnect()
        return {
            "message": "backend.user_does_not_exist",
            "messageType": "error",
            "status": 404,
        }

    await db.loggedusers.update(
        where={
            "user_id": user.id
        },
        data={
            "isLogged": isLoggedProps.isLogged
        }
    )
    await db.disconnect()
    return {
        "message": "backend.user_logged_successfully" if isLoggedProps.isLogged == True else "backend.user_logout_successfully",
        "isLogged": isLoggedProps.isLogged,
        "messageType": "success",
        "status": 200,
    }


# Knowledge
# If frontend send this request twice, supabase sometimes does not have the time
# to process the first request, and the second request will throw a constraint error in
# user_id - UniqueViolationError <- avoids that
@authRouter.post("/auth/magic-link", tags=["auth"])
async def read_user(magicLinkRestBody: SendMagicLinkModel):
    db = Prisma()
    await db.connect()

    try:
        user = await db.user.find_unique(where={"email": magicLinkRestBody.email})
        print("User found:", user)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        loggedUser = await db.loggedusers.find_unique(where={"user_id": user.id})

        if user.registration_completed and loggedUser and loggedUser.isLogged:
            return {
                "message": "User is already verified and logged",
                "redirect": True,
                "code": 200,
            }

        if magicLinkRestBody.verificationType is None:
            raise HTTPException(
                status_code=400, detail="Verification type is required")

        pin = generate_4_digit_pin()

        if magicLinkRestBody.verificationType == "confirm-email":
            email_subject_body = confirm_email_message(pin)
        else:
            raise HTTPException(
                status_code=400, detail="Invalid verification type")

        try:
            await db.secretpins.create(data={"user_id": user.id, "pin": pin})

            send_email(
                magicLinkRestBody.email,
                email_subject_body["subject"],
                email_subject_body["body"],
            )
        except UniqueViolationError:
            return {
                "message": f"A pin has already been sent to {magicLinkRestBody.email}. Please check your inbox.",
                "code": 200,
            }

        asyncio.create_task(delete_pin_after_delay(user.id, 600))

        return {
            "message": f"Pin for {magicLinkRestBody.verificationType} was sent to {magicLinkRestBody.email}, please check your email.",
            "code": 200,
        }

    finally:
        await db.disconnect()
        print("Disconnecting DB...")


@authRouter.post("/auth/pin-verification", tags=["auth"])
async def read_user(verificationPin: SecretPINVerification):
    db = Prisma()
    await db.connect()

    if verificationPin.email == None or verificationPin.userPin == None:
        await db.disconnect()
        return {"message": "Email and pin are required", "status": 400}

    user = await db.user.find_unique(where={"email": verificationPin.email})

    if user == None:
        await db.disconnect()
        return {"message": "User does not exist", "status": 404}

    pin_exist = await db.secretpins.find_unique(
        where={"user_id": user.id, "pin": verificationPin.userPin}
    )

    if pin_exist:
        await db.user.update(
            where={"email": verificationPin.email},
            data={"registration_completed": True},
        )
        await db.secretpins.delete(
            where={"user_id": user.id, "pin": verificationPin.userPin}
        )

        await db.loggedusers.update(
            where={
                "user_id": user.id
            },
            data={
                "isLogged": True
            }
        )
        await db.disconnect()
        return {
            "message": "PIN is valid, user can continue",
            "isValidPin": True,
            "user": {
                "isLogged": True,
                "registrationCompleted": True,
            },
            "status": 200,
        }
    else:
        await db.disconnect()
        return {
            "message": "PIN is invalid, please try again",
            "user": {
                "isLogged": False,
                "registrationCompleted": user.registration_completed,
            },
            "status": 404,
        }


@authRouter.post("/auth/google-auth", tags=["auth"])
async def googleAuth(googleUser: RegisterGoogleUser):
    db = Prisma()
    await db.connect()
    print(googleUser)
    user = await db.user.find_unique(where={"email": googleUser.email})

    if user:
        await db.disconnect()
        return {
            "message": "backend.user_exist",
            "messageType": "warning",
            "status": 409,
            "user_exist": True,
            "registration_completed": user.registration_completed,
        }

    match googleUser.authMethod:
        case "register":
            await db.user.create(
                data={
                    "nickname": googleUser.name,
                    "email": googleUser.email,
                    "user_image": googleUser.picture,
                    "user_type": "company",
                    "registration_completed": True
                }
            )
            just_created_user = await db.user.find_unique(where={"email": googleUser.email})

            await db.loggedusers.create(
                data={
                    "user_id": just_created_user.id,
                    "isLogged": True
                }
            )
            await db.disconnect()
            return {
                "message": "backend.user_created",
                "messageType": "success",
                "status": 200,
                "user_created": True,
            }
        case _:
            await db.disconnect()
            return {
                "message": "backend.invalid_method",
                "messageType": "error",
                "status": 400,
            }

    await db.disconnect()
    return [{"message": "auth-magic-link", "code": 200}]
