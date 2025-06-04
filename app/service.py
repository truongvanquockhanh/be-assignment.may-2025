from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, MessageCreate, SentMessageResponse
from app.models import User, Message, MessageRecipient
from app.dependencies import create_access_token
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import selectinload

# check if user exists
async def check_user(db: AsyncSession, user: UserCreate):
  result = await db.execute(
        select(User).where(
            and_(
                User.email == user.email,
                User.name == user.name
            )
        )
    )
  db_user = result.scalars().first()
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

# create token
async def create_token(db: AsyncSession, user: UserCreate):
  db_user = await check_user(db, user)
  if db_user:
    to_token = {
      "email": db_user.email,
      "name": db_user.name,
      "id": str(db_user.id),
    }
    return {
      "id": db_user.id,
      "email": db_user.email,
      "token": create_access_token(to_token)
    }

# create user
async def create_user(db: AsyncSession, user: UserCreate):
  try:
    print(user)
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
  except IntegrityError:
    await db.rollback()
    raise HTTPException(status_code=400, detail="Email already registered.")
  to_token = {
      "email": db_user.email,
      "name": db_user.name,
      "id": str(db_user.id),
  }
  token = create_access_token(to_token)
  return {
      "id": db_user.id,
      "email": db_user.email,
      "token": token
    }

# get all users
async def get_all_users(db: AsyncSession):
  result = await db.execute(select(User))
  users = result.scalars().all()
  if not users:
    raise HTTPException(status_code=404, detail="Users not found")
  return users

# get user details
async def get_user(db: AsyncSession, user_id: UUID):
  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalars().first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

# send message
async def send_message(db: AsyncSession, sender_id: UUID, message_data: MessageCreate):
    message = Message(
        sender_id=sender_id,
        subject=message_data.subject,
        content=message_data.content,
        timestamp=datetime.utcnow(),
    )
    db.add(message)
    await db.flush()
    recipients = [
      MessageRecipient(
        message_id=message.id,
        recipient_id=recipient_id,
      )
      for recipient_id in message_data.recipient_ids
    ]
    db.add_all(recipients)
    await db.commit()
    await db.refresh(message)
    return message

# mark message as read
async def mark_message_as_read_service(db: AsyncSession, messagerecipient_id: UUID, current_user: UUID):
  result = await db.execute(
        select(MessageRecipient).where(
            and_(
                MessageRecipient.id == messagerecipient_id,
                MessageRecipient.recipient_id == UUID(current_user)
            )
        )
    )
  message = result.scalars().first()
  if not message:
    raise HTTPException(status_code=404, detail="Message not found or you are not the recipient")
  message.read = True
  message.read_at = datetime.utcnow()
  await db.commit()
  await db.refresh(message)
  return message

# View sent messages of current user
async def get_sent_messages_service(db: AsyncSession, current_user: UUID):
    # Query all messages sent by the current user
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.recipients))
        .where(Message.sender_id == current_user)
        .order_by(Message.timestamp.desc())
    )
    
    sent_messages = result.scalars().all()

    # Convert ORM models to Pydantic models
    response = []
    for message in sent_messages:
        recipients = [
            {
                "recipient_id": recipient.recipient_id,
                "read": recipient.read,
                "read_at": recipient.read_at
            }
            for recipient in message.recipients
        ]
        response.append(SentMessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            subject=message.subject,
            content=message.content,
            timestamp=message.timestamp,
            recipients=recipients
        ))

    return response

# View sent messages of one user
async def get_sent_messages_service_one_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.recipients))
        .where(Message.sender_id == user_id)
        .order_by(Message.timestamp.desc())
    )
    sent_messages = result.scalars().all()
    response = []
    for message in sent_messages:
        recipients = [
            {
                "recipient_id": recipient.recipient_id,
                "read": recipient.read,
                "read_at": recipient.read_at
            }
            for recipient in message.recipients
        ]
        response.append(SentMessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            subject=message.subject,
            content=message.content,
            timestamp=message.timestamp,
            recipients=recipients
        ))

    return response

# View inbox messages of current user
async def get_inbox_messages_service(db: AsyncSession, current_user: UUID):
    result = await db.execute(
        select(Message)
        .join(Message.recipients)
        .options(selectinload(Message.recipients))
        .where(MessageRecipient.recipient_id == current_user)
        .order_by(Message.timestamp.desc())
    )

    datas = result.scalars().all()
    messages = []
    for data in datas:
        for recipient in data.recipients:
            if str(recipient.recipient_id) == current_user:
                messages.append({
                    "id": data.id,
                    "sender_id": data.sender_id,
                    "subject": data.subject,
                    "content": data.content,
                    "timestamp": data.timestamp,
                    "read": recipient.read,
                    "read_at": recipient.read_at
                })
                break
    return messages

# View inbox messages of one user
async def get_inbox_messages_service_one_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Message)
        .join(Message.recipients)
        .options(selectinload(Message.recipients))
        .where(MessageRecipient.recipient_id == user_id)
        .order_by(Message.timestamp.desc())
    )

    datas = result.scalars().all()
    messages = []
    for data in datas:
        for recipient in data.recipients:
            if str(recipient.recipient_id) == str(user_id):
                messages.append({
                    "id": data.id,
                    "sender_id": data.sender_id,
                    "subject": data.subject,
                    "content": data.content,
                    "timestamp": data.timestamp,
                    "read": recipient.read,
                    "read_at": recipient.read_at
                })
                break
    return messages

# View unread messages of one user
async def get_unread_messages_service(db: AsyncSession, user_id: UUID):
  
    result = await db.execute(
        select(Message)
        .join(Message.recipients)
        .options(selectinload(Message.recipients))
        .where(MessageRecipient.recipient_id == user_id, MessageRecipient.read == False)
        .order_by(Message.timestamp.desc())
    )

    datas = result.scalars().all()
    messages = []
    for data in datas:
        for recipient in data.recipients:
            if str(recipient.recipient_id) == str(user_id):
                messages.append({
                    "id": data.id,
                    "sender_id": data.sender_id,
                    "subject": data.subject,
                    "content": data.content,
                    "timestamp": data.timestamp,
                    "read": recipient.read,
                    "read_at": recipient.read_at
                })
                break
    return messages

# View unread messages of current user
async def get_unread_messages_current_user_service(db: AsyncSession, current_user: UUID):
   
    result = await db.execute(
        select(Message)
        .join(Message.recipients)
        .options(selectinload(Message.recipients))
        .where(MessageRecipient.recipient_id == current_user, MessageRecipient.read == False)
        .order_by(Message.timestamp.desc())
    )

    datas = result.scalars().all()
    messages = []
    for data in datas:
        for recipient in data.recipients:
            if str(recipient.recipient_id) == str(current_user):
                messages.append({
                    "id": data.id,
                    "sender_id": data.sender_id,
                    "subject": data.subject,
                    "content": data.content,
                    "timestamp": data.timestamp,
                    "read": recipient.read,
                    "read_at": recipient.read_at
                })
                break
    return messages


# View a specific message
async def get_a_messages_service(db, message_id, current_user):
  result = await db.execute(
        select(Message)
        .join(Message.recipients)
        .options(selectinload(Message.recipients))
        .where(
           Message.id == message_id,
           or_(
             Message.sender_id == current_user,
             MessageRecipient.recipient_id == current_user
           )
        )
    )
  message = result.scalars().first()
  if not message:
    raise HTTPException(status_code=404, detail="Message not found or you are not authorized to view it")
  return message