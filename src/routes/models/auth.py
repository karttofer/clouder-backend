# Deps
from pydantic import BaseModel

class LoginModel(BaseModel):
    email: str
    password: bytes


class SendMagicLinkModel(BaseModel):
    email: str


class RegisterModel(BaseModel):
    nickname: str
    password: str
    email: str


class ResetPaswordModel(BaseModel):
    user_id: str
    new_password: str


class SendMagicLinkModel(BaseModel):
    email: str
