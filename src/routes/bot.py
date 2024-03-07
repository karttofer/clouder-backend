from fastapi import APIRouter

botRouter = APIRouter()

@botRouter.post("/bot/send-message", tags=["bot"])
def read_user():
    return [{"message": "auth-register"}]


