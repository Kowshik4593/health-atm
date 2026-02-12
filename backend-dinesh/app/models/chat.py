from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatMessage(BaseModel):
    id: str
    assignment_id: str
    sender_id: str
    message: Optional[str]
    attachment_url: Optional[str]
    sent_at: datetime

class ChatMessageCreate(BaseModel):
    assignment_id: str
    sender_id: str
    message: Optional[str]
