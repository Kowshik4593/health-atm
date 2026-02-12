from app.supabase_client import supabase

resp = supabase.table("patient_ct_scans").select("id, status, uploaded_at").order("uploaded_at", desc=True).limit(10).execute()

for r in resp.data:
    cid = r['id'][:8]
    st = r['status']
    dt = r['uploaded_at'][:16] if r['uploaded_at'] else 'N/A'
    print(f"{cid}  {st:12s}  {dt}")

print(f"\nTotal: {len(resp.data)} cases")
