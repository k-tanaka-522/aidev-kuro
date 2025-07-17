from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.utils.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()


class Message(BaseModel):
    message_id: str
    channel_id: str
    sender_id: str
    sender_name: str
    content: str
    message_type: str = "text"
    timestamp: datetime
    parent_message_id: Optional[str] = None
    attachments: List[str] = []


class CreateMessageRequest(BaseModel):
    channel_id: str
    content: str
    message_type: str = "text"
    parent_message_id: Optional[str] = None
    attachments: List[str] = []


class Channel(BaseModel):
    channel_id: str
    name: str
    project_id: str
    channel_type: str = "general"
    participants: List[str] = []
    created_at: datetime


@router.get("/channels", response_model=List[Channel])
async def list_channels(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List channels"""
    try:
        # Mock channels
        mock_channels = [
            Channel(
                channel_id="channel_001",
                name="General Discussion",
                project_id=project_id or "proj_001",
                channel_type="general",
                participants=["user_123", "agent_pm_001"],
                created_at=datetime.utcnow()
            ),
            Channel(
                channel_id="channel_002",
                name="Agent Collaboration",
                project_id=project_id or "proj_001",
                channel_type="agent",
                participants=["agent_pm_001", "agent_arch_001", "agent_sec_001"],
                created_at=datetime.utcnow()
            )
        ]
        
        return mock_channels
    except Exception as e:
        logger.error("Failed to list channels", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{channel_id}", response_model=List[Message])
async def get_messages(
    channel_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get messages from a channel"""
    try:
        # Mock messages
        mock_messages = [
            Message(
                message_id="msg_001",
                channel_id=channel_id,
                sender_id="user_123",
                sender_name="Admin User",
                content="Hello, let's start the project planning.",
                timestamp=datetime.utcnow()
            ),
            Message(
                message_id="msg_002",
                channel_id=channel_id,
                sender_id="agent_pm_001",
                sender_name="Project Manager Agent",
                content="I'll analyze the requirements and create a project plan. What are the key objectives?",
                timestamp=datetime.utcnow()
            )
        ]
        
        return mock_messages
    except Exception as e:
        logger.error("Failed to get messages", channel_id=channel_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Message)
async def send_message(
    message_data: CreateMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to a channel"""
    try:
        # Mock message creation
        message = Message(
            message_id=f"msg_{hash(message_data.content) % 10000:04d}",
            channel_id=message_data.channel_id,
            sender_id=current_user["user_id"],
            sender_name=current_user["name"],
            content=message_data.content,
            message_type=message_data.message_type,
            timestamp=datetime.utcnow(),
            parent_message_id=message_data.parent_message_id,
            attachments=message_data.attachments
        )
        
        logger.info(
            "Message sent",
            message_id=message.message_id,
            channel_id=message.channel_id,
            sender_id=message.sender_id
        )
        
        return message
    except Exception as e:
        logger.error("Failed to send message", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")