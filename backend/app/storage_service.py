# backend/app/storage_service.py
"""
Storage Service Module for Phase-2.

This module provides:
- Local file storage for reports
- Supabase storage integration
- Signed URL generation
- Report metadata management

Corporate Standards:
- Reports stored in organized directory structure
- All storage operations logged
- Graceful fallback when remote storage unavailable

Upgraded for Phase-2: Feb 2026
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import requests

from app.supabase_client import SUPABASE_URL, SUPABASE_SERVICE_KEY


# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent / "local_reports"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Report metadata file
METADATA_FILE = BASE_DIR / "metadata.json"


# =============================================================================
# Supabase Storage (Remote)
# =============================================================================

def download_bytes(bucket: str, path: str) -> Optional[bytes]:
    """
    Download from Supabase Storage via REST API.
    This bypasses the broken supabase-py storage client.
    """
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.content
        print(f"[storage] Download failed: {r.status_code}")
        return None
    except Exception as e:
        print(f"[storage] Download exception: {e}")
        return None


def upload_bytes(bucket: str, path: str, data: bytes, content_type: str = "application/pdf") -> bool:
    """
    Upload to Supabase Storage via REST API.
    """
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": content_type
    }

    try:
        r = requests.post(url, headers=headers, data=data, timeout=60)
        if r.status_code in [200, 201]:
            print(f"[storage] Uploaded to Supabase: {bucket}/{path}")
            return True
        print(f"[storage] Upload failed: {r.status_code} - {r.text[:200]}")
        return False
    except Exception as e:
        print(f"[storage] Upload exception: {e}")
        return False


def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> Optional[str]:
    """
    Generate a signed URL for temporary access to a file.
    
    Args:
        bucket: Storage bucket name
        path: File path within bucket
        expires_in: Expiration time in seconds (default 1 hour)
        
    Returns:
        Signed URL or None if failed
    """
    url = f"{SUPABASE_URL}/storage/v1/object/sign/{bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json"
    }
    payload = {"expiresIn": expires_in}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            signed_path = data.get("signedURL", "")
            return f"{SUPABASE_URL}/storage/v1{signed_path}"
        return None
    except Exception as e:
        print(f"[storage] Signed URL error: {e}")
        return None


# =============================================================================
# Local Storage (Primary for Reports)
# =============================================================================

def save_local(case_id: str, filename: str, data: bytes) -> str:
    """
    Saves report file locally and returns a served URL.
    
    Directory structure:
        local_reports/
        ├── {case_id}/
        │   ├── clinician_report.pdf
        │   ├── patient_en_report.pdf
        │   ├── patient_hi_report.pdf
        │   ├── findings.json
        │   └── metadata.json
    
    Args:
        case_id: Case identifier
        filename: File name to save
        data: File content as bytes
        
    Returns:
        URL path for serving: /local_reports/{case_id}/{filename}
    """
    case_dir = BASE_DIR / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    full_path = case_dir / filename
    with open(full_path, "wb") as f:
        f.write(data)
    
    # Update metadata
    _update_case_metadata(case_id, filename, len(data))

    return f"/local_reports/{case_id}/{filename}"


def load_local(case_id: str, filename: str) -> Optional[bytes]:
    """
    Load a file from local storage.
    """
    full_path = BASE_DIR / case_id / filename
    if not full_path.exists():
        return None
    with open(full_path, "rb") as f:
        return f.read()


def delete_local(case_id: str, filename: Optional[str] = None) -> bool:
    """
    Delete a file or entire case directory from local storage.
    
    Args:
        case_id: Case identifier
        filename: Specific file to delete (None = delete all)
    """
    case_dir = BASE_DIR / case_id
    
    try:
        if filename:
            file_path = case_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
        else:
            # Delete entire case directory
            import shutil
            if case_dir.exists():
                shutil.rmtree(case_dir)
                return True
        return False
    except Exception as e:
        print(f"[storage] Delete error: {e}")
        return False


def list_local_reports(case_id: str) -> List[Dict]:
    """
    List all reports for a case.
    
    Returns:
        List of dicts with file info
    """
    case_dir = BASE_DIR / case_id
    if not case_dir.exists():
        return []
    
    files = []
    for f in case_dir.iterdir():
        if f.is_file():
            files.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "url": f"/local_reports/{case_id}/{f.name}"
            })
    
    return files


def get_local_path(case_id: str, filename: str) -> Optional[Path]:
    """
    Get absolute path to a local file.
    """
    full_path = BASE_DIR / case_id / filename
    if full_path.exists():
        return full_path
    return None


# =============================================================================
# Metadata Management
# =============================================================================

def _load_metadata() -> Dict:
    """Load global metadata file."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"cases": {}}


def _save_metadata(metadata: Dict):
    """Save global metadata file."""
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"[storage] Metadata save error: {e}")


def _update_case_metadata(case_id: str, filename: str, size: int):
    """Update metadata for a case file."""
    metadata = _load_metadata()
    
    if case_id not in metadata["cases"]:
        metadata["cases"][case_id] = {
            "created": datetime.utcnow().isoformat() + "Z",
            "files": {}
        }
    
    metadata["cases"][case_id]["files"][filename] = {
        "size": size,
        "checksum": None,  # Could add MD5 for verification
        "saved_at": datetime.utcnow().isoformat() + "Z"
    }
    metadata["cases"][case_id]["updated"] = datetime.utcnow().isoformat() + "Z"
    
    _save_metadata(metadata)


def get_case_metadata(case_id: str) -> Optional[Dict]:
    """Get metadata for a specific case."""
    metadata = _load_metadata()
    return metadata["cases"].get(case_id)


def get_all_cases() -> List[str]:
    """Get list of all case IDs with local reports."""
    metadata = _load_metadata()
    return list(metadata["cases"].keys())


# =============================================================================
# Report Organization Helpers
# =============================================================================

def save_report_set(
    case_id: str,
    clinician_pdf: Optional[bytes] = None,
    patient_en_pdf: Optional[bytes] = None,
    patient_hi_pdf: Optional[bytes] = None,
    findings_json: Optional[bytes] = None
) -> Dict[str, str]:
    """
    Save a complete set of reports for a case.
    
    Returns:
        Dict mapping report type to URL
    """
    urls = {}
    
    if clinician_pdf:
        urls["clinician"] = save_local(case_id, "clinician_report.pdf", clinician_pdf)
    
    if patient_en_pdf:
        urls["patient_en"] = save_local(case_id, "patient_en_report.pdf", patient_en_pdf)
    
    if patient_hi_pdf:
        urls["patient_hi"] = save_local(case_id, "patient_hi_report.pdf", patient_hi_pdf)
    
    if findings_json:
        urls["findings"] = save_local(case_id, "findings.json", findings_json)
    
    return urls


def get_report_urls(case_id: str) -> Dict[str, str]:
    """
    Get URLs for all available reports for a case.
    """
    reports = list_local_reports(case_id)
    urls = {}
    
    for r in reports:
        name = r["filename"]
        if "clinician" in name:
            urls["clinician"] = r["url"]
        elif "patient_en" in name or (name == "patient_report.pdf"):
            urls["patient_en"] = r["url"]
        elif "patient_hi" in name:
            urls["patient_hi"] = r["url"]
        elif "findings" in name:
            urls["findings"] = r["url"]
    
    return urls


# =============================================================================
# Storage Statistics
# =============================================================================

def get_storage_stats() -> Dict:
    """
    Get storage usage statistics.
    """
    total_size = 0
    total_files = 0
    total_cases = 0
    
    for case_dir in BASE_DIR.iterdir():
        if case_dir.is_dir() and case_dir.name != "__pycache__":
            total_cases += 1
            for f in case_dir.iterdir():
                if f.is_file():
                    total_files += 1
                    total_size += f.stat().st_size
    
    return {
        "total_cases": total_cases,
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "storage_path": str(BASE_DIR)
    }


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("🔍 Testing Storage Service\n")
    
    # Test local storage
    test_data = b"Test PDF content"
    url = save_local("TEST-001", "test_report.pdf", test_data)
    print(f"Saved test file: {url}")
    
    # Test load
    loaded = load_local("TEST-001", "test_report.pdf")
    print(f"Loaded: {len(loaded) if loaded else 0} bytes")
    
    # Test list
    files = list_local_reports("TEST-001")
    print(f"Files in TEST-001: {files}")
    
    # Test stats
    stats = get_storage_stats()
    print(f"\nStorage stats: {json.dumps(stats, indent=2)}")
    
    # Cleanup
    delete_local("TEST-001")
    print("\nCleanup complete")
