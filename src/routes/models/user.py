# Deps
from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    id: str


class EditModel(BaseModel):
    id: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
