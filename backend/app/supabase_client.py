from supabase import create_client
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
