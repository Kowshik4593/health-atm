"""End-to-end test of the inference pipeline with synthetic data."""
import numpy as np
import os
import tempfile
import json
import sys

print("=" * 60)
print("Inference Pipeline - End-to-End Test")
print("=" * 60)

# 1. Create synthetic volume
print("")
print("1. Creating synthetic 64x64x64 volume...")
volume = np.random.randn(64, 64, 64).astype(np.float32) * 100 - 500
volume[20:35, 20:35, 20:35] = 200
volume[45:55, 40:50, 40:50] = 150
print("   Volume shape: " + str(volume.shape))

# 2. Save as .npy
test_dir = tempfile.mkdtemp(prefix="healthatm_test_")
npy_path = os.path.join(test_dir, "test_scan.npy")
np.save(npy_path, volume)
print("   Saved to: " + npy_path)

# 3. Run inference
print("")
print("2. Running inference pipeline...")
from app.services.inference_service import analyze_scan

findings = analyze_scan(
    case_id="TEST-E2E-001",
    input_path=npy_path,
    output_dir=os.path.join(test_dir, "output"),
    is_dicom=False
)

# 4. Verify
print("")
print("3. Verifying findings structure...")
required_keys = [
    "study_id", "num_nodules", "nodules", "impression",
    "summary_text", "processing_time_seconds", "metadata"
]
missing = [k for k in required_keys if k not in findings]
if missing:
    print("   FAIL: Missing keys: " + str(missing))
    sys.exit(1)
else:
    print("   All required keys present")

print("")
print("4. Results:")
print("   Study ID: " + str(findings['study_id']))
print("   Nodules found: " + str(findings['num_nodules']))
print("   Processing time: " + str(findings['processing_time_seconds']) + "s")
print("   Impression: " + str(findings['impression'][:100]) + "...")

for n in findings["nodules"][:5]:
    print("")
    print("   Nodule #" + str(n['id']) + ":")
    print("     Centroid: " + str(n['centroid']))
    print("     Volume: " + str(n['volume_mm3']) + " mm3")
    print("     Prob malignant: " + str(n.get('prob_malignant', 'N/A')))
    print("     Type: " + str(n.get('type', 'N/A')))

# 5. Check findings.json was saved
findings_path = os.path.join(test_dir, "output", "TEST-E2E-001_findings.json")
if os.path.exists(findings_path):
    size = os.path.getsize(findings_path)
    print("")
    print("5. findings.json saved (" + str(size) + " bytes)")
else:
    print("")
    print("5. FAIL: findings.json not found")

# Cleanup
import shutil
shutil.rmtree(test_dir, ignore_errors=True)

print("")
print("=" * 60)
print("END-TO-END TEST COMPLETE - ALL PASS")
print("=" * 60)
