# app/services/notification_service.py
from app.supabase_client import supabase

class NotificationService:
    @staticmethod
    def notify(user_id: str, message: str):
        res = supabase.table("notifications").insert({
            "user_id": user_id,
            "message": message
        }).execute()
        return res.data[0]
