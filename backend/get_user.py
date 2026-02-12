from app.supabase_client import supabase
import sys
import os

# Add parent dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_valid_user():
    print("Checking for existing users...")
    
    # Try getting from profiles first (common pattern)
    try:
        resp = supabase.table("profiles").select("id").limit(1).execute()
        if resp.data:
            print(f"Found user in profiles: {resp.data[0]['id']}")
            return
    except Exception as e:
        print(f"Profiles check failed: {e}")

    # Try getting from existing scans
    try:
        resp = supabase.table("patient_ct_scans").select("patient_id").limit(1).execute()
        if resp.data:
            print(f"Found patient_id in existing scans: {resp.data[0]['patient_id']}")
            return
    except Exception as e:
        print(f"Scans check failed: {e}")

    print("Could not find a valid user ID. You may need to sign up a user in the frontend first.")

if __name__ == "__main__":
    get_valid_user()
