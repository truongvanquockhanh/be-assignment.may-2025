# Test message-related functionality
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_message_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        # Create sender and recipient
        sender_resp = await client.post(
            "/users", json={"email": "sender@example.com", "name": "Sender"}
        )
        assert sender_resp.status_code == 200
        sender = sender_resp.json()

        recipient_resp = await client.post(
            "/users", json={"email": "recipient@example.com", "name": "Recipient"}
        )
        assert recipient_resp.status_code == 200
        recipient = recipient_resp.json()

        # Login sender to get JWT token
        login_resp = await client.post(
            "/auths/login", json={"email": "sender@example.com", "name": "Sender"}
        )
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        token = token_data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Login recipient to get JWT token
        login_resp_recipient = await client.post(
            "/auths/login", json={"email": "recipient@example.com", "name": "Recipient"}
        )
        assert login_resp_recipient.status_code == 200
        token_data_recipient = login_resp_recipient.json()
        token_recipient = token_data_recipient["token"]
        headers_recipient = {"Authorization": f"Bearer {token_recipient}"}

        # Send message (POST /messages)
        send_payload = {
            "subject": "Test Subject",
            "content": "Test message content",
            "recipient_ids": [recipient["id"]],
        }
        send_resp = await client.post("/messages", json=send_payload, headers=headers)
        assert send_resp.status_code == 200
        sent_message = send_resp.json()
        message_id = sent_message["id"]
        assert sent_message["subject"] == "Test Subject"
        assert sent_message["content"] == "Test message content"

        # Get sent messages of current user (GET /messages/sent)
        sent_messages_resp = await client.get("/messages/sent", headers=headers)
        assert sent_messages_resp.status_code == 200
        sent_messages = sent_messages_resp.json()
        assert any(m["subject"] == "Test Subject" for m in sent_messages)
        assert any(m["content"] == "Test message content" for m in sent_messages)
        assert any(m["id"] == message_id for m in sent_messages)

        # Get inbox messages of current user (GET /messages/inbox)
        inbox_messages_resp = await client.get(
            "/messages/inbox", headers=headers_recipient
        )
        assert inbox_messages_resp.status_code == 200
        inbox_messages = inbox_messages_resp.json()
        inbox_messages_id = inbox_messages[0]["id"]
        assert any(m["subject"] == "Test Subject" for m in inbox_messages)
        assert any(m["content"] == "Test message content" for m in inbox_messages)
        assert any(m["id"] == inbox_messages_id for m in inbox_messages)

        # get unread messages of current user (GET /messages/unread)
        unread_messages_resp = await client.get(
            "/messages/unread", headers=headers_recipient
        )
        assert unread_messages_resp.status_code == 200
        unread_messages = unread_messages_resp.json()
        assert any(m["subject"] == "Test Subject" for m in unread_messages)
        assert any(m["content"] == "Test message content" for m in unread_messages)
        assert any(m["read"] == False for m in unread_messages)

        # Mark message recipient as read (PUT /message-recipients/{id}/read)
        read_resp = await client.put(
            f"/message-recipients/{inbox_messages_id}/read", headers=headers_recipient
        )
        assert read_resp.status_code == 200
        read_message = read_resp.json()
        assert read_message["id"] == inbox_messages_id
        assert read_message["read"] == True
        assert read_message["read_at"] is not None

        # Get a specific message (GET /messages/{id})
        specific_message_resp = await client.get(
            f"/messages/{message_id}", headers=headers
        )
        assert specific_message_resp.status_code == 200
        specific_message = specific_message_resp.json()
        assert specific_message["subject"] == "Test Subject"
        assert specific_message["content"] == "Test message content"
        assert specific_message["id"] == message_id
