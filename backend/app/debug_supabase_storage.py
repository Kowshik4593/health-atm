# debug_supabase_storage.py
import os
from supabase_client import supabase
from dotenv import load_dotenv

# ensure env loaded (optional)
load_dotenv = None

BUCKET = "ml_json"
CASE = "a563a79b-d604-452e-903e-a0bfb15a73ca"
PATH = f"{CASE}/findings.json"

def repr_obj(x):
    try:
        return repr(x)
    except Exception:
        return str(type(x))

print("SUPABASE_URL:", os.getenv("SUPABASE_URL") is not None)
print("SUPABASE_SERVICE_KEY:", os.getenv("SUPABASE_SERVICE_KEY") is not None)

print("\n=== LIST bucket top-level (first 100) ===")
try:
    lst = supabase.storage.from_(BUCKET).list("", limit=100)
    print("list() returned type:", type(lst), repr_obj(lst))
    try:
        # storage3-style may return dict with 'data' key
        if hasattr(lst, "data"):
            print("list.data length:", len(lst.data or []))
            print("sample:", (lst.data or [])[:6])
        elif isinstance(lst, dict):
            print("list dict keys:", lst.keys())
            print("sample:", lst.get("data"))
        else:
            print("raw:", lst)
    except Exception as e:
        print("list inspect error:", e)
except Exception as e:
    print("list() raised:", e)

print("\n=== TRY download exact path ===")
try:
    res = supabase.storage.from_(BUCKET).download(PATH)
    print("download() returned type:", type(res))
    print("download() repr:", repr_obj(res))
    # If it's bytes-like
    if isinstance(res, (bytes, bytearray)):
        print("Downloaded bytes length:", len(res))
        print(res[:200])
    # If it is tuple (data,error) common in some wrappers
    elif isinstance(res, tuple):
        print("tuple elements:", [type(x) for x in res])
        try:
            print("first elem repr (len if bytes):", repr_obj(res[0])[:400])
            if isinstance(res[0], (bytes,bytearray)):
                print("first elem length:", len(res[0]))
        except Exception:
            pass
    else:
        # object with .read() or .text or .content
        try:
            if hasattr(res, "read"):
                b = res.read()
                print("res.read() len:", len(b))
            elif hasattr(res, "content"):
                print("res.content len:", len(res.content))
            elif hasattr(res, "text"):
                print("res.text first chars:", res.text[:200])
            elif hasattr(res, "data"):
                print("res.data keys:", getattr(res, "data"))
        except Exception as e:
            print("reading res object raised:", e)
except Exception as e:
    print("download() raised exception:", e)
