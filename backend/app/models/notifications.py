from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    id: str
    user_id: str
    message: str
    is_read: bool
    created_at: datetime

class NotificationCreate(BaseModel):
    user_id: str
    message: str
