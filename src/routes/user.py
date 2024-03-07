from fastapi import APIRouter

userRouter = APIRouter()

@userRouter.get("/user",tags=["user"])
def read_user():
    return [{"message": "auth-register"}]

@userRouter.post("/user/edit",tags=["user"])
def read_users():
    return [{"message": "auth-login"}]

@userRouter.post("/user/conversations",tags=["user"])
def read_user():
    return [{"message": "auth-magic-link"}]

@userRouter.post("/user/archived-conversations",tags=["user"])
def read_user():
    return [{"message": "auth-magic-link"}]
