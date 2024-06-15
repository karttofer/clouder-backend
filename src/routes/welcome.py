# Dependencies
from fastapi import APIRouter

# Declaration
welcome_router = APIRouter()

@welcome_router.get("/", tags=["root"])
def read_welcome():
    return {"response": "Hi, this is the version 0.01 of Cloder Backend, if you see this it is because it's working well :)."}