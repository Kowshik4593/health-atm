"""
Seed Test Cases for Frontend Testing
=====================================
Uses real LIDC-IDRI patches from the dataset to create multiple
test cases visible in the frontend dashboard.

Each case goes through: Upload -> Process -> Completed
"""

import requests
import time
import numpy as np
import io
import os
import sys
from pathlib import Path

API_URL = "http://localhost:8000"

# --- Valid user ID from your database ---
USER_ID = "b21f958e-c469-43fa-bd42-1c531b69f810"

# LIDC patches directory
PATCHES_DIR = Path(__file__).parent / "ml" / "data" / "lidc_patches"

# Pick 5 diverse patches (different patients, different nodules)
TEST_PATCHES = [
    "01-01-2000-NA-NA-98329_nodule_6.npz",   # Patient 1
    "01-01-2000-NA-NA-94866_nodule_0.npz",   # Patient 2
    "01-01-2000-NA-NA-92500_nodule_7.npz",   # Patient 3
    "01-01-2000-NA-NA-75952_nodule_0.npz",   # Patient 4
    "01-01-2000-NA-NA-50667_nodule_9.npz",   # Patient 5
]

# Simulated patient names for display
PATIENT_NAMES = [
    "Arun Menon",
    "Priya Sharma",
    "Ravi Krishnan",
    "Meena Patel",
    "Suresh Gupta",
]


def load_patch_as_npy(npz_path: str) -> bytes:
    """Load a .npz patch and convert the 'image' array to .npy bytes."""
    data = np.load(npz_path)
    image = data['image']  # shape: (64, 64, 64), dtype: int16
    
    # Save to in-memory buffer as .npy
    buf = io.BytesIO()
    np.save(buf, image)
    buf.seek(0)
    return buf.read()


def upload_scan(scan_bytes: bytes, filename: str) -> str:
    """Upload a scan and return the case_id."""
    files = {'file': (filename, scan_bytes, 'application/octet-stream')}
    headers = {'x-user-id': USER_ID, 'x-user-role': 'patient'}
    
    resp = requests.post(f"{API_URL}/upload/scan", files=files, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data['case_id']


def trigger_processing(case_id: str):
    """Trigger the AI pipeline for a case."""
    resp = requests.post(f"{API_URL}/process/case/{case_id}")
    resp.raise_for_status()


def wait_for_completion(case_id: str, timeout: int = 180) -> str:
    """Poll until the case is completed or failed."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{API_URL}/process/status/{case_id}")
        status = resp.json().get('status', 'unknown')
        
        if status == 'completed':
            return 'completed'
        elif status == 'failed':
            return 'failed'
        
        time.sleep(3)
    
    return 'timeout'


def main():
    print("=" * 60)
    print("  HealthATM - Seed Test Cases")
    print("  Creating 5 test cases from real LIDC-IDRI data")
    print("=" * 60)
    
    if not PATCHES_DIR.exists():
        print(f"\nError: Patches directory not found: {PATCHES_DIR}")
        sys.exit(1)
    
    # Verify API is running
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        print(f"\nBackend Status: {resp.json().get('status', 'unknown')}")
    except Exception as e:
        print(f"\nError: Backend not reachable at {API_URL}")
        print(f"Make sure the server is running: python -m uvicorn app.main:app --port 8000")
        sys.exit(1)
    
    results = []
    
    for i, (patch_file, patient_name) in enumerate(zip(TEST_PATCHES, PATIENT_NAMES)):
        patch_path = PATCHES_DIR / patch_file
        
        if not patch_path.exists():
            print(f"\n[{i+1}/5] SKIP: {patch_file} not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"[{i+1}/5] Patient: {patient_name}")
        print(f"       Source:  {patch_file}")
        print(f"{'='*60}")
        
        # 1. Load and convert
        print(f"  [1/3] Loading patch...")
        scan_bytes = load_patch_as_npy(str(patch_path))
        print(f"        Size: {len(scan_bytes) / 1024:.1f} KB")
        
        # 2. Upload
        print(f"  [2/3] Uploading scan...")
        try:
            case_id = upload_scan(scan_bytes, f"scan_{patient_name.replace(' ', '_').lower()}.npy")
            print(f"        Case ID: {case_id}")
        except Exception as e:
            print(f"        Upload failed: {e}")
            continue
        
        # 3. Trigger processing
        print(f"  [3/3] Triggering AI pipeline...")
        try:
            trigger_processing(case_id)
            print(f"        Pipeline started!")
        except Exception as e:
            print(f"        Trigger failed: {e}")
            continue
        
        results.append({
            'index': i + 1,
            'patient': patient_name,
            'case_id': case_id,
            'source': patch_file,
        })
    
    if not results:
        print("\nNo cases were created. Check the errors above.")
        return
    
    # Now wait for all cases to complete
    print(f"\n{'='*60}")
    print(f"  Waiting for {len(results)} case(s) to complete...")
    print(f"  (This may take 1-3 minutes per case)")
    print(f"{'='*60}")
    
    for r in results:
        print(f"\n  Waiting: Case {r['case_id'][:8]}... ({r['patient']})")
        status = wait_for_completion(r['case_id'])
        r['status'] = status
        
        if status == 'completed':
            print(f"  -> Completed!")
        elif status == 'failed':
            print(f"  -> Failed!")
        else:
            print(f"  -> Timeout (may still be processing)")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    
    completed = sum(1 for r in results if r.get('status') == 'completed')
    failed = sum(1 for r in results if r.get('status') == 'failed')
    pending = sum(1 for r in results if r.get('status') not in ('completed', 'failed'))
    
    print(f"  Completed: {completed}")
    print(f"  Failed:    {failed}")
    print(f"  Pending:   {pending}")
    
    print(f"\n  Case IDs for frontend testing:")
    for r in results:
        status_icon = "[OK]" if r.get('status') == 'completed' else "[!!]"
        print(f"    {status_icon} {r['patient']:20s} -> {r['case_id']}")
    
    print(f"\n  Open your frontend dashboard to see these cases!")
    print(f"  URL: http://localhost:3000/dashboard")


if __name__ == "__main__":
    main()
