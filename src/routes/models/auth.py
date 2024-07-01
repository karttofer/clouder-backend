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

class RegisterByJWT(BaseModel):
    jwt: str

class ResetPaswordModel(BaseModel):
    user_id: str
    new_password: str


class SendMagicLinkModel(BaseModel):
    email: str
    verification_type: str

class JWTFUSerLogin(BaseModel):
    jwt: str

class SecretPINVerification(BaseModel):
    email: str
    user_pin: int

class RegisterGoogleUser(BaseModel):
    name: str
    email: str
    picture: str
    email_verified: bool
    auth_method: str