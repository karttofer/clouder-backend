from fastapi import FastAPI
from routes.auth import authRouter
from routes.bot import botRouter
from routes.user import userRouter

app = FastAPI()

app.include_router(authRouter)
app.include_router(botRouter)
app.include_router(userRouter)
