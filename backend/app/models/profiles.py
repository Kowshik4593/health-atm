from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Profile(BaseModel):
    id: str
    full_name: str
    role: str
    phone: str
    gender: str
    state: str
    city: str
    country: str
    primary_language: Optional[str] = None
    created_at: Optional[datetime] = None
