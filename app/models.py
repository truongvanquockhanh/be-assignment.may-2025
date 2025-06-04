# SQLAlchemy or Tortoise models
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sent_messages = relationship(
        "Message", back_populates="sender", cascade="all, delete"
    )
    received_messages = relationship(
        "MessageRecipient", back_populates="recipient", cascade="all, delete"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", back_populates="sent_messages")
    recipients = relationship(
        "MessageRecipient", back_populates="message", cascade="all, delete"
    )


class MessageRecipient(Base):
    __tablename__ = "message_recipients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipient_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    message = relationship("Message", back_populates="recipients")
    recipient = relationship("User", back_populates="received_messages")
