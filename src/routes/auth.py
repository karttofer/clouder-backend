from fastapi import APIRouter

authRouter = APIRouter()

@authRouter.post("/auth", tags=["auth"])
def read_users():
    return [{"message": "auth-login"}]


@authRouter.post("/auth/register",tags=["auth"])
def read_user():
    return [{"message": "auth-register"}]


@authRouter.post("/auth/magic-link",tags=["auth"])
def read_user():
    return [{"message": "auth-magic-link"}]


@authRouter.post("/auth/reset-password",tags=["auth"])
def read_user():
    return [{"message": "auth-magic-link"}]
