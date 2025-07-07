# Deps
from pydantic import BaseModel

class LoginModel(BaseModel):
    email: str

class SendMagicLinkModel(BaseModel):
    email: str


class RegisterModel(BaseModel):
    name: str
    email: str
    userType: str

class RegisterByJWT(BaseModel):
    jwt: str

class ResetPaswordModel(BaseModel):
    user_id: str
    new_password: str


class SendMagicLinkModel(BaseModel):
    email: str
    verificationType: str
    isResend: bool = False

class JWTFUSerLogin(BaseModel):
    jwt: str

class SecretPINVerification(BaseModel):
    email: str
    userPin: int

class RegisterGoogleUser(BaseModel):
    name: str
    email: str
    picture: str
    authMethod: str

class IsLoggedUser(BaseModel):
    email: str

class ChangeIsLogged(BaseModel):
    email: str
    isLogged: bool
