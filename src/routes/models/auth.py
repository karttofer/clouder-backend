# Deps
from pydantic import BaseModel

class LoginModel(BaseModel):
    email: str

class SendMagicLinkModel(BaseModel):
    email: str


class RegisterModel(BaseModel):
    nickname: str
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
    nickname: str
    email: str
    picture: str
    auth_method: str