from fastapi import APIRouter, HTTPException, status
from prisma import Prisma
import asyncio
import bcrypt
import base64

# Models
from src.routes.model.auth import Register, ResetPasword

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
def read_user():
    return [{"message": "auth-magic-link"}]


@authRouter.post("/auth/reset-password", tags=["auth"])
async def read_user(resetPassBody: ResetPasword):
    db = Prisma()
    await db.connect()
    new_password = salt_password(resetPassBody.new_password)
    print(new_password,'asdasdasdasdas')
    await db.user.update(
        where={"id": resetPassBody.user_id}, data={"password": new_password}
    )

    await db.disconnect()
    return [{"message": "auth-magic-link"}]
