# Deps
from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    email: str


class EditModel(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
