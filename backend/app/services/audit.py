def log(user_id, action, details=None):
    supabase.table("audit_logs").insert({
        "user_id": user_id,
        "action": action,
        "details": details
    }).execute()
