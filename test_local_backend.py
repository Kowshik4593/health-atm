import requests
import time
import os

BASE_URL = "http://127.0.0.1:8050"

CASE_ID     = "a563a79b-d604-452e-903e-a0bfb15a73ca"
PATIENT_ID  = "72db6e64-a103-419f-8c25-0ed0b9d1b849"
DOCTOR_ID   = "626799fd-a8f7-4fdd-bc09-dc14624c00fc"
OPERATOR_ID = "7e9f1e32-6bc0-4b85-8e42-93f3117cb73a"

OUTPUT_DIR = "test_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def pretty(resp):
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text


# ---------------------------
# 1. Trigger case
# ---------------------------
def trigger_case(case_id, operator_id):
    print(f"[1] Triggering case {case_id}")
    r = requests.post(f"{BASE_URL}/cases/process/{case_id}",
                      params={"triggered_by": operator_id})
    print("->", pretty(r))
    if r.status_code not in (200, 201):
        raise RuntimeError("Failed to trigger case!")


# ---------------------------
# 2. Wait for DB update
# ---------------------------
def wait_for_scan_results(case_id, timeout=120, poll=3):
    print(f"[2] Waiting for scan_results update (timeout {timeout}s)...")
    start = time.time()

    while True:
        r = requests.get(f"{BASE_URL}/cases/scan_results/{case_id}")
        status, data = pretty(r)

        if status == 200:
            clinician = data.get("clinician_pdf")
            patient = data.get("patient_pdf")
            print(f"   clinician_pdf={clinician} | patient_pdf={patient}")

            if clinician and patient:
                return data

        if time.time() - start > timeout:
            raise TimeoutError("Timed out waiting for scan_results update")

        time.sleep(poll)


# ---------------------------
# 3. Fetch & download PDFs
# ---------------------------
def fetch_and_download(case_id, user_id, role):
    print(f"[3] Fetching {role} PDF as user {user_id}")

    r = requests.get(f"{BASE_URL}/cases/reports/{case_id}",
                     params={"user_id": user_id})
    status, data = pretty(r)
    print("->", status, data)

    if status != 200:
        raise RuntimeError("Failed getting report URLs")

    # support {"url": "..."} or plain string
    if role == "patient":
        url = data["patient_report"].get("url", data["patient_report"])
        out_path = os.path.join(OUTPUT_DIR, f"patient_{case_id}.pdf")

    elif role == "doctor":
        url = data["clinician_report"].get("url", data["clinician_report"])
        out_path = os.path.join(OUTPUT_DIR, f"clinician_{case_id}.pdf")

    else:
        raise ValueError("Invalid role")

    print("   Downloading:", url)

    # FULL URL FIXED HERE
    pdf_resp = requests.get(f"{BASE_URL}{url}")

    if pdf_resp.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(pdf_resp.content)
        print(f"   Saved -> {out_path} ({os.path.getsize(out_path)} bytes)")
    else:
        print("   FAILED download:", pdf_resp.status_code)

    return out_path


# ---------------------------
# MAIN FLOW
# ---------------------------
def full_test():
    print("\n========== LOCAL BACKEND TEST ==========\n")

    trigger_case(CASE_ID, OPERATOR_ID)

    scan = wait_for_scan_results(CASE_ID)

    print("\n[Patient Report Test]")
    patient_pdf = fetch_and_download(CASE_ID, PATIENT_ID, "patient")

    print("\n[Doctor Report Test]")
    doctor_pdf = fetch_and_download(CASE_ID, DOCTOR_ID, "doctor")

    print("\n========== COMPLETED ==========")
    print("Patient PDF:", patient_pdf)
    print("Doctor  PDF:", doctor_pdf)


if __name__ == "__main__":
    full_test()
