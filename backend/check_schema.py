from app.supabase_client import supabase

try:
    # Fetch one row to see columns
    res = supabase.table("scan_results").select("*").limit(1).execute()
    if res.data:
        print("Columns:", res.data[0].keys())
    else:
        print("Table empty, cannot infer columns easily via select. Trying to insert dummy to get error?")
        # Just assume standard columns or check error
except Exception as e:
    print(e)
