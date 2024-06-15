from fastapi import FastAPI
from src.routes.auth import authRouter
from src.routes.bot import botRouter
from src.routes.user import userRouter
from src.routes.welcome import welcome_router

app = FastAPI()

app.include_router(welcome_router)
app.include_router(authRouter)
app.include_router(botRouter)
app.include_router(userRouter)
