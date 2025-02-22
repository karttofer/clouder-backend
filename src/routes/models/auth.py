# Deps
from pydantic import BaseModel

class LoginModel(BaseModel):
    email: str

class SendMagicLinkModel(BaseModel):
    email: str


class RegisterModel(BaseModel):
    name: str
    email: str
    user_type: str

class RegisterByJWT(BaseModel):
    jwt: str

class ResetPaswordModel(BaseModel):
    user_id: str
    new_password: str


class SendMagicLinkModel(BaseModel):
    email: str
    verification_type: str
    isResend: bool = False

class JWTFUSerLogin(BaseModel):
    jwt: str

class SecretPINVerification(BaseModel):
    email: str
    user_pin: int

class RegisterGoogleUser(BaseModel):
    name: str
    email: str
    picture: str
    auth_method: str