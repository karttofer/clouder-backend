# Deps
import datetime
import asyncio
from typing import Annotated
from urllib import request

from fastapi import APIRouter, HTTPException, status
from prisma import Prisma

from google.auth import jwt
from prisma.errors import UniqueViolationError

# Helpers
from src.routes.helpers.email.emailSender import send_email
from src.routes.helpers.methods import generate_4_digit_pin, delete_pin_after_delay

# Models
from src.routes.models.auth import (
    RegisterModel,
    SendMagicLinkModel,
    LoginModel,
    SecretPINVerification,
    RegisterGoogleUser,
    IsLoggedUser,
    ChangeIsLogged,
)

authRouter = APIRouter()

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
                "email": user.email,
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
            "roleId": regisBody.roleId,
        }
    )

    user_created = await db.user.find_unique(where={"email": regisBody.email})

    await db.loggedusers.create(data={"user_id": user_created.id, "isLogged": False})

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
        where={"user_id": user.id}, data={"isLogged": isLoggedProps.isLogged}
    )
    await db.disconnect()
    return {
        "message": (
            "backend.user_logged_successfully"
            if isLoggedProps.isLogged == True
            else "backend.user_logout_successfully"
        ),
        "isLogged": isLoggedProps.isLogged,
        "messageType": "success",
        "status": 200,
    }


# Knowledge
# If frontend send this request twice, supabase sometimes does not have the time
# to process the first request, and the second request will throw a constraint error in
# user_id - UniqueViolationError <- avoids that
# TODO - We need to change this file isnt working for the new features or way to create messages
@authRouter.post("/auth/magic-link", tags=["auth"])
async def read_user(magicLinkRestBody: SendMagicLinkModel):
    db = Prisma()
    await db.connect()

    user_data = {}
    try:
        user = await db.user.find_unique(where={"email": magicLinkRestBody.email})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        loggedUser = await db.loggedusers.find_unique(where={"user_id": user.id})
        secret_pin_exist = await db.secretpins.find_unique(where={"user_id": user.id})

        if secret_pin_exist:
            await db.disconnect()
            return {
                "message":  f"A pin has already been sent to {magicLinkRestBody.email}. Please check your inbox.",
                "code": 200,
            }

        if user.registration_completed and loggedUser and loggedUser.isLogged:
            await db.disconnect()
            return {
                "message": "User is already verified and logged",
                "redirect": True,
                "code": 200,
            }

        if not magicLinkRestBody.verificationType:
            await db.disconnect()
            return HTTPException(status_code=400, detail="Verification type is required")

        pin = generate_4_digit_pin()

        if magicLinkRestBody.verificationType == "confirm-email":
            user_data["email"] = user.email
            user_data["subject"] = "Ajoooy, welcome to the platform"
            user_data["template_name"] = "verifyEmail.html"
        else:
            await db.disconnect()
            raise HTTPException(status_code=400, detail="Invalid verification type")

        try:
            now = datetime.datetime.now()
            year = now.strftime("%Y")

            send_email(
                recipient_email=user_data["email"],
                subject=user_data["subject"],
                template_name=user_data["template_name"],
                website_url="www.youtube.com",
                linkedin_url="www.google.com",
                policies_url="www.google.com",
                help_url="www.youtube.com",
                year=year,
                pin_minutes_expiration=30,
                validation_code=pin,
            )

            await db.secretpins.create(data={"user_id": user.id, "pin": pin})

        except UniqueViolationError:
            return {
                "message": "An error occurred while sending the pin",
                "code": 500,
            }

        asyncio.create_task(delete_pin_after_delay(Prisma, user.id, 600))

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

        await db.loggedusers.update(where={"user_id": user.id}, data={"isLogged": True})
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
                    "registration_completed": True,
                }
            )
            just_created_user = await db.user.find_unique(
                where={"email": googleUser.email}
            )

            await db.loggedusers.create(
                data={"user_id": just_created_user.id, "isLogged": True}
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
