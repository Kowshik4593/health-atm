"""
Synthetic Fix Script for Findings JSON (Phase-1 Demo)
-----------------------------------------------------
This script corrects the following issues synthetically:

- long_axis_mm variation
- volume_mm3 variation
- prob_malignant variation (0.2–0.95)
- uncertainty (confidence, entropy, needs_review)
- lobe name fixes (left middle lobe -> left lingula)
- mask_path set to 'not_available'

Usage:
python synthetic_fix_findings.py --input backend-dinesh/outputs/LIDC-IDRI-0001_findings.json
"""

import json
import argparse
import numpy as np
import copy
from pathlib import Path

def synthetic_fix(data):

    nods = data["nodules"]

    for n in nods:
        # --------------------------------------
        # 1) Fix lobe names
        # --------------------------------------
        lob = n.get("location", "")
        if lob == "left middle lobe":
            n["location"] = "left lingula"

        # --------------------------------------
        # 2) Mask path – Phase-1 placeholder
        # --------------------------------------
        n["mask_path"] = "not_available"

        # --------------------------------------
        # 3) Synthetic size/volume variation
        # --------------------------------------
        la = float(n.get("long_axis_mm", 15))
        vol = float(n.get("volume_mm3", 2000))

        # add slight jitter
        la = la * np.random.uniform(0.85, 1.15)
        vol = vol * np.random.uniform(0.75, 1.25)

        # clamp reasonable ranges
        la = float(np.clip(la, 5, 60))
        vol = float(np.clip(vol, 200, 60000))

        n["long_axis_mm"] = round(la, 2)
        n["volume_mm3"] = int(vol)

        # --------------------------------------
        # 4) Synthetic malignancy variation
        # --------------------------------------
        # Assign more realistic spread
        pm = float(np.random.normal(0.55, 0.20))   # centered around 0.55
        pm = float(np.clip(pm, 0.20, 0.95))
        n["prob_malignant"] = round(pm, 3)

        # --------------------------------------
        # 5) Synthetic uncertainty variation
        # --------------------------------------
        # entropy increases when pm is mid-range
        entropy = float(pm * (1 - pm) * 2.0)  # synthetic bell curve
        entropy += float(np.random.uniform(-0.05, 0.05))
        entropy = float(np.clip(entropy, 0.0, 1.0))

        conf = float(np.clip(pm + np.random.uniform(-0.1, 0.1), 0.05, 0.99))
        needs_review = bool(entropy > 0.4)

        n["uncertainty"] = {
            "confidence": round(conf, 3),
            "entropy": round(entropy, 3),
            "needs_review": needs_review
        }

    # Update num_nodules if needed
    data["num_nodules"] = len(nods)

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to findings.json")
    args = parser.parse_args()

    inp = Path(args.input)
    out = inp.with_name(inp.stem + "_synthetic.json")

    with open(inp, "r") as f:
        data = json.load(f)

    fixed = synthetic_fix(data)

    with open(out, "w") as f:
        json.dump(fixed, f, indent=2)

    print(f"[DONE] Synthetic JSON saved to: {out}")


if __name__ == "__main__":
    main()
