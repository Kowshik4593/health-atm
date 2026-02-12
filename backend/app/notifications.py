# backend/app/notifications.py
from app.supabase_client import supabase

def notify(user_id: str, message: str):
    supabase.table("notifications").insert({
        "user_id": user_id,
        "message": message
    }).execute()
