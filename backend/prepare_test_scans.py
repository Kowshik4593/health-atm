"""
Extract LIDC patches into standalone .npy files for manual frontend upload testing.
"""
import numpy as np
from pathlib import Path

PATCHES_DIR = Path(__file__).parent / "ml" / "data" / "lidc_patches"
OUTPUT_DIR = Path(__file__).parent.parent / "test_scans"

SAMPLES = [
    ("01-01-2000-NA-NA-98329_nodule_6.npz",  "patient_arun_menon.npy"),
    ("01-01-2000-NA-NA-94866_nodule_0.npz",  "patient_priya_sharma.npy"),
    ("01-01-2000-NA-NA-92500_nodule_7.npz",  "patient_ravi_krishnan.npy"),
    ("01-01-2000-NA-NA-75952_nodule_0.npz",  "patient_meena_patel.npy"),
    ("01-01-2000-NA-NA-50667_nodule_9.npz",  "patient_suresh_gupta.npy"),
]

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for src_name, dst_name in SAMPLES:
        src = PATCHES_DIR / src_name
        dst = OUTPUT_DIR / dst_name

        if not src.exists():
            print(f"SKIP: {src_name} not found")
            continue

        data = np.load(str(src))
        image = data["image"]  # (64,64,64) int16
        np.save(str(dst), image)
        print(f"Created: {dst.name}  ({image.shape}, {image.dtype})")

    print(f"\nAll files saved to: {OUTPUT_DIR.resolve()}")
    print("You can now upload these .npy files through the frontend Upload page.")

if __name__ == "__main__":
    main()
