# FastAPI routes
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import LoginResponse, UserCreate, UserResponse, MessageResponse, MessageCreate, SentMessageResponse, InboxMessageResponse, MessageRecipientResponse
from app.service import create_token, create_user, get_all_users, get_user, send_message, mark_message_as_read_service, get_sent_messages_service, get_a_messages_service, get_unread_messages_current_user_service
from app.service import get_sent_messages_service_one_user, get_inbox_messages_service, get_sent_messages_service, get_inbox_messages_service_one_user, get_unread_messages_service
from app.dependencies import get_current_user
from app.db import get_db

router = APIRouter()

# login to get token for get current user
@router.post("/auths/login", response_model=LoginResponse, summary="Login to get token")
async def login(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
  ) -> LoginResponse:
  return await create_token(db, user)

# create user
@router.post("/users", response_model=LoginResponse)
async def create_users(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
  ) -> LoginResponse:
  return await create_user(db, user)

# get all users
@router.get("/users", response_model=list[UserResponse], summary="Get all users")
async def get_users(
    db: AsyncSession = Depends(get_db),
  ) -> list[UserResponse]:
  return await get_all_users(db)

# get users details
@router.get("/users/{user_id}", response_model=UserResponse, summary="Get user details")
async def get_user_details(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db)
  ) -> UserResponse:
  return await get_user(db, user_id)

# send message
@router.post("/messages", response_model=MessageResponse, summary="Send message")
async def send_messages(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
  ) -> MessageResponse:
    return await send_message(db, sender_id=current_user, message_data=message)

# Mark a message as read
@router.put("/message-recipients/{messagerecipient_id}/read", summary="Mark message as read", response_model=MessageRecipientResponse)
async def mark_message_as_read(
    messagerecipient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
  ) -> MessageRecipientResponse:
    return await mark_message_as_read_service(db, messagerecipient_id, current_user)

# View sent messages of current user
@router.get("/messages/sent", response_model=list[SentMessageResponse], summary="Get sent messages of current user")
async def get_sent_messages(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
  ) -> list[SentMessageResponse]:
    return await get_sent_messages_service(db, current_user)

# View sent messages of one user
@router.get("/messages/sent/{user_id}", response_model=list[SentMessageResponse], summary="Get sent messages of one user")
async def get_sent_messages(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
  ) -> list[SentMessageResponse]:
    return await get_sent_messages_service_one_user(db, user_id)

# View inbox of current user
@router.get("/messages/inbox", summary="Get inbox messages of current user", response_model=list[InboxMessageResponse])
async def get_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> list[InboxMessageResponse]:
    return await get_inbox_messages_service(db, current_user)

# View inbox of one user
@router.get("/messages/inbox/{user_id}", summary="Get inbox messages of one user", response_model=list[InboxMessageResponse])
async def get_inbox(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[InboxMessageResponse]:
    return await get_inbox_messages_service_one_user(db, user_id)

#View unread messages
@router.get("/messages/unread/{user_id}", summary="Get unread messages", response_model=list[InboxMessageResponse])
async def get_unread_messages(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[InboxMessageResponse]:
    return await get_unread_messages_service(db, user_id)

# View unread messages of current user
@router.get("/messages/unread", summary="Get unread messages of current user", response_model=list[InboxMessageResponse])
async def get_unread_messages(
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
) -> list[InboxMessageResponse]:
    return await get_unread_messages_current_user_service(db, current_user)

# View a messgae with all recipients
@router.get("/messages/{message_id}", summary="Get a specific message with all recipients for the authenticated user", response_model=SentMessageResponse)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
) -> SentMessageResponse:
    return await get_a_messages_service(db, message_id, current_user)