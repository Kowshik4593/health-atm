def notify(user_id, msg):
    supabase.table("notifications").insert({
        "user_id": user_id,
        "message": msg
    }).execute()
