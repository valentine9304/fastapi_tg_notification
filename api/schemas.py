from pydantic import BaseModel, Field
from datetime import datetime


class TaskPost(BaseModel):
    datetime_to_do: datetime
    task_info: str


class TaskPatch(BaseModel):
    datetime_to_do: datetime | None = None
    task_info: str | None = None


class TaskGet(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime | None
    datetime_to_do: datetime
    task_info: str

    class Config:
        from_attributes = True


class MessagePost(BaseModel):
    telegram_user_id: str = Field(..., examples=["279371399"])
    notification_id: str = Field(..., examples=["uuid-1234-5678"])
    message_text: str = Field(..., examples=["Привет, это тест!"])


class MessageGet(BaseModel):
    id: int
    telegram_user_id: str
    notification_id: str
    message_text: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class TokenRequest(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
