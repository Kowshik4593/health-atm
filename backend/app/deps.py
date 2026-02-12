from fastapi import Header, HTTPException
from pydantic import BaseModel
from typing import Optional

class CurrentUser(BaseModel):
    id: str
    role: Optional[str]

def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    if x_user_id is None:
        raise HTTPException(401, "Missing x-user-id")

    return CurrentUser(id=x_user_id, role=x_user_role)
