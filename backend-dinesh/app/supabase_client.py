from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
