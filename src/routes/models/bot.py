# Deps
from typing import List, Optional
from pydantic import BaseModel


class CreateThreadModelMessagesValuesModel(BaseModel):
    role: str
    content: str
    file_ids: Optional[List[str]]


class CreateThreadModelMessagesModel(BaseModel):
    thread_name: str
    user_id: str
    messages: List[CreateThreadModelMessagesValuesModel]


class SendMessageModel(BaseModel):
    thread_id: str
    role: str
    content: str


class MessageListBodyModel(BaseModel):
    thread_id: str


class DeleteThreadModel(BaseModel):
    thread_id: str
