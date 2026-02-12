"""Test script to verify all FastAPI endpoints are registered."""
import requests

BASE = "http://localhost:8000"

print("=" * 60)
print("HealthATM Backend - Endpoint Verification")
print("=" * 60)

# 1. Check all registered routes via OpenAPI
print("\n1. All registered routes:")
r = requests.get(f"{BASE}/openapi.json", timeout=5)
data = r.json()
paths = sorted(data["paths"].keys())
for p in paths:
    methods = list(data["paths"][p].keys())
    print(f"   {', '.join(m.upper() for m in methods):10s} {p}")
print(f"\n   Total: {len(paths)} endpoints")

# 2. Test key endpoints
print("\n2. Key endpoint tests:")

tests = [
    ("GET", "/", 200, "Root"),
    ("GET", "/health", 200, "Health Check"),
    ("GET", "/version", 200, "Version"),
    ("POST", "/upload/scan", 422, "Upload (no file=422)"),
    ("POST", "/process/case/test-id", 404, "Process (bad id=404)"),
    ("GET", "/process/status/test-id", 404, "Status (bad id=404)"),
    ("GET", "/cases/test-id", 404, "Get Case (bad id=404)"),
]

for method, path, expected, label in tests:
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", timeout=5)
        else:
            r = requests.post(f"{BASE}{path}", timeout=5)
        status = "PASS" if r.status_code == expected else "FAIL"
        icon = "+" if status == "PASS" else "x"
        print(f"   [{icon}] {label}: {r.status_code} (expected {expected})")
    except Exception as e:
        print(f"   [x] {label}: ERROR - {e}")

print("\nDone!")
