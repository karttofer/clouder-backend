from fastapi import FastAPI
from src.routes.auth import authRouter
from src.routes.bot import botRouter
from src.routes.user import userRouter
from src.routes.welcome import welcome_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajusta según sea necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(welcome_router)
app.include_router(authRouter)
app.include_router(botRouter)
app.include_router(userRouter)
