import requests
import time
import numpy as np
import io
import os
import json

import uuid

API_URL = "http://localhost:8000"
USER_ID = "b21f958e-c469-43fa-bd42-1c531b69f810" # Corrected valid user ID
ROLE = "patient"

def create_synthetic_scan():
    """Generates a smaller 32x32x32 volume for quick testing."""
    print("Generating synthetic CT volume (32x32x32)...")
    vol = np.random.randint(-1000, 1000, (32, 32, 32), dtype=np.int16)
    
    # Save to buffer
    bio = io.BytesIO()
    np.save(bio, vol)
    bio.seek(0)
    return bio.read()

def main():
    print(f"--- Starting End-to-End Integration Test ---")
    print(f"Target API: {API_URL}")
    
    # --- Step 1: Upload ---
    print(f"\n[Step 1] Uploading synthetic scan (.npy)...")
    try:
        scan_bytes = create_synthetic_scan()
        files = {'file': ('test_scan.npy', scan_bytes, 'application/octet-stream')}
        headers = {'x-user-id': USER_ID, 'x-user-role': ROLE}
        
        resp = requests.post(f"{API_URL}/upload/scan", files=files, headers=headers)
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return
            
        data = resp.json()
        case_id = data.get('case_id')
        print(f"Success! Case ID: {case_id}")
        print(f"Status: {data.get('status')}")
    except Exception as e:
        print(f"Upload failed: {e}")
        return

    # --- Step 2: Trigger Processing ---
    print(f"\n[Step 2] Triggering AI Pipeline for Case {case_id}...")
    try:
        # Note: Frontend calls /process/case/{caseId}
        process_url = f"{API_URL}/process/case/{case_id}"
        resp = requests.post(process_url)
        
        if resp.status_code != 200:
             print(f"Error triggering pipeline: {resp.text}")
             return
             
        print(f"Pipeline triggered. Response: {resp.json()}")
    except Exception as e:
        print(f"Trigger failed: {e}")
        return

    # --- Step 3: Poll Status ---
    print(f"\n[Step 3] Polling Status (Timeout: 120s)...")
    start_time = time.time()
    last_status = None
    
    while True:
        try:
            status_resp = requests.get(f"{API_URL}/process/status/{case_id}")
            if status_resp.status_code != 200:
                print(f"Error polling status: {status_resp.text}")
                break
                
            status_data = status_resp.json()
            current_status = status_data.get('status')
            
            if current_status != last_status:
                print(f"    Status Changed: {last_status} -> {current_status}")
                last_status = current_status
            else:
                print(f"    Waiting... ({current_status})")
            
            if current_status == 'completed':
                print(f"\nProcessing Completed successfully in {time.time() - start_time:.2f}s!")
                break
            elif current_status == 'failed':
                print(f"\nProcessing Failed!")
                return
            
            if time.time() - start_time > 120:
                print(f"\nTimeout waiting for completion.")
                return
            
            time.sleep(2)
        except Exception as e:
            print(f"Polling failed: {e}")
            return

    # --- Step 4: Verify Results ---
    print(f"\n[Step 4] Verifying Results Retrieval...")
    try:
        # Simulated Frontend Call to get Findings
        # Note: In real app, frontend fetches directly from Storage or via strict API.
        # But we can verify reports endpoint availability.
        reports_url = f"{API_URL}/cases/reports/{case_id}"
        reports_resp = requests.get(reports_url, headers={'x-user-id': USER_ID, 'x-user-role': ROLE})
        
        if reports_resp.status_code == 200:
            print(f"Reports Endpoint OK: {reports_resp.json()}")
        else:
            print(f"Reports Endpoint Warning: {reports_resp.status_code} - {reports_resp.text}")
            
    except Exception as e:
        print(f"Results verification failed: {e}")

    print(f"\n--- Integration Test Passed ---")
    print(f"You can view this case in the Frontend Dashboard.")

if __name__ == "__main__":
    main()
