import os
import sys
from app.supabase_client import supabase

# Correct bucket names used in the app
BUCKETS = ["ct_scans", "ml_json", "reports"]

def check_buckets():
    print("=" * 60)
    print("Supabase Storage Bucket Verification")
    print("=" * 60)

    try:
        # List buckets
        res = supabase.storage.list_buckets()
        existing_buckets = [b.name for b in res]
        print(f"Found Buckets: {existing_buckets}")
        
        all_good = True
        
        for bucket in BUCKETS:
            if bucket in existing_buckets:
                print(f"✅ Bucket FOUND: {bucket}")
                # Test write permission
                try:
                    test_path = "bucket_check.txt"
                    supabase.storage.from_(bucket).upload(test_path, b"ok", file_options={"content-type": "text/plain", "upsert": "true"})
                    supabase.storage.from_(bucket).remove([test_path])
                    print(f"   -> Write/Delete Permission: OK")
                except Exception as e:
                    print(f"   -> Write Error: {e}")
            else:
                print(f"❌ Bucket MISSING: {bucket}")
                all_good = False

        if all_good:
            print("\nAll required buckets exist and are accessible!")
        else:
            print("\nSome buckets are missing. Please creating them in Supabase Dashboard.")
            
    except Exception as e:
        print(f"\nError listing buckets: {e}")

if __name__ == "__main__":
    check_buckets()
