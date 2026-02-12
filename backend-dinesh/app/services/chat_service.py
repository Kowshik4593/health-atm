# app/services/chat_service.py
from app.supabase_client import supabase

class ChatService:

    @staticmethod
    def send_message(assignment_id: str, sender_id: str, message: str, attachment_url: str = None):
        data = {
            "assignment_id": assignment_id,
            "sender_id": sender_id,
            "message": message,
            "attachment_url": attachment_url
        }

        res = supabase.table("chat_messages").insert(data).execute()
        return res.data[0]


    @staticmethod
    def get_messages(assignment_id: str):
        res = supabase.table("chat_messages").select("*") \
            .eq("assignment_id", assignment_id) \
            .order("sent_at") \
            .execute()
        return res.data
    @staticmethod
    def get_history(assignment_id):
        res = (
            supabase
            .table("chat_messages")
            .select("*")
            .eq("assignment_id", assignment_id)
            .order("sent_at", desc=False)
            .execute()
        )
        return res.data
