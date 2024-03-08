from pydantic import BaseModel

class SendMagicLink(BaseModel):
    nickname: str
    email: str

class Register(BaseModel):
    nickname: str
    password: str
    email: str


class ResetPasword(BaseModel):
    user_id: str
    new_password: str


class SendMagicLink(BaseModel):
    user_id: str
    email: str

