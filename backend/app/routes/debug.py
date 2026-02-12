from fastapi import APIRouter
import inspect
import app.storage_service as ss

router = APIRouter()

@router.get("/debug/storage_path")
def debug_storage_path():
    return {
        "imported_file": inspect.getfile(ss.upload_bytes),
        "source": inspect.getsource(ss.upload_bytes)
    }
