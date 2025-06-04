# Pydantic models
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    name: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    id: UUID
    email: str
    token: str

class MessageCreate(BaseModel):
    subject: Optional[str] = None
    content: str
    recipient_ids: List[UUID]  # list of user UUIDs


class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    subject: Optional[str]
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class MessageRecipientResponse(BaseModel):
    id: UUID
    message_id: UUID
    recipient_id: UUID
    read: bool
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

class InboxMessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    subject: Optional[str] = None
    content: str
    timestamp: datetime
    read: bool
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

class RecipientInfo(BaseModel):
    recipient_id: UUID
    read: bool
    read_at: datetime | None = None

    class Config:
        from_attributes = True

class SentMessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    subject: str | None
    content: str
    timestamp: datetime
    recipients: List[RecipientInfo]

    class Config:
        from_attributes = True