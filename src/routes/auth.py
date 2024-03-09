# Deps
from fastapi import APIRouter, HTTPException, status
from prisma import Prisma
import bcrypt
import base64

# Helpers
from src.routes.helpers.configs import reset_password_messages
from src.routes.helpers.emailSender import send_email
from src.routes.helpers.methods import generate_4_digit_pin

# Models
from src.routes.models.auth import Register, ResetPasword, SendMagicLink

authRouter = APIRouter()


def salt_password(password):
    password = password
    bytes_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash_password_bytes = bcrypt.hashpw(bytes_password, salt)

    return base64.b64encode(hash_password_bytes).decode("utf-8")


@authRouter.post("/auth", tags=["auth"])
def read_users():
    return [{"message": ""}]

# TODO: We need to check first if the user does no exist in the database
@authRouter.post("/auth/register", tags=["auth"])
async def read_user(regisBody: Register):
    try:
        regisBody.password = salt_password(regisBody.password)
        db = Prisma()
        await db.connect()

        await db.user.create(data=regisBody.model_dump(exclude_none=True))

        await db.disconnect()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return {"message": "User created", "status": 200}


@authRouter.post("/auth/magic-link", tags=["auth"])
async def read_user(magicLinkRestBody: SendMagicLink):
    db = Prisma()
    await db.connect()
    user = await db.user.find_unique(where={"email": magicLinkRestBody.email})
    if user != None:
        pin = generate_4_digit_pin()
        email_subject_body = reset_password_messages(pin)
        await db.secretpins.create(data={"user_id": user.id, "pin": pin})
        send_email(
            magicLinkRestBody.email,
            email_subject_body["subject"],
            email_subject_body["body"],
        )
        return {
            "message": f"Pin reset-password was sent to {magicLinkRestBody.email}, please take a look to your email.",
            "code": 200,
        }
    await db.disconnect()
    return {"message": "User does no exist", "code": 404}

# Frontend should check password validation
@authRouter.post("/auth/reset-password", tags=["auth"])
async def read_user(resetPassBody: ResetPasword):
    db = Prisma()
    await db.connect()

    new_password = salt_password(resetPassBody.new_password)

    await db.user.update(
        where={"id": resetPassBody.user_id}, data={"password": new_password}
    )

    await db.disconnect()
    return [{"message": "auth-magic-link", "code": 200}]
