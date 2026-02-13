import pandas as pd
import numpy as np
import SimpleITK as sitk
from pathlib import Path

from sklearn.decomposition import PCA

def load_volume(volume_path):
    img = sitk.ReadImage(str(volume_path))
    arr = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()   # (x,y,z)
    return arr, spacing[::-1]    # convert to (z,y,x)

def compute_hu_stats(arr, mask):
    vals = arr[mask > 0]
    if vals.size == 0:
        return -1000, 0
    return float(vals.mean()), float(vals.std())

def compute_long_axis_mm(mask, spacing):
    coords = np.argwhere(mask > 0)
    if coords.shape[0] < 5:
        return 0.0

    coords_mm = coords * np.array(spacing)
    pca = PCA(n_components=1)
    pca.fit(coords_mm)
    axis = pca.components_[0]
    proj = coords_mm @ axis
    return float(proj.max() - proj.min())

def compute_volume_mm3(mask, spacing):
    voxel_vol = spacing[0] * spacing[1] * spacing[2]
    count = np.sum(mask > 0)
    return float(count * voxel_vol)

def classify_type(hu_mean):
    if hu_mean > -300:
        return "solid"
    elif hu_mean > -700:
        return "subsolid"
    else:
        return "ground-glass"

def extract_lndb_features(lndb_root, save_csv):
    lndb_root = Path(lndb_root)

    # Load mapping of LNDbID → CT path
    from .load_lndb_volumes import build_volume_index
    volume_index = build_volume_index(lndb_root)

    # Read nodule metadata
    df = pd.read_csv(lndb_root / "allNods.csv")

    rows = []

    for _, row in df.iterrows():
        lndb_id = row["LNDbID"]                # 1,2,3,...
        nodule_id = row["NoduleID"]            # 0,1,...
        malignancy = row["Malignancy"]         # 0/1/2
        
        vol_key = f"LNDb-{int(lndb_id):04d}"   # LNDb-0001
        if vol_key not in volume_index:
            continue

        volume_path = volume_index[vol_key]

        # Load CT
        vol, spacing = load_volume(volume_path)

        # Load mask file
        mask_filename = row["maskfile"]
        mask_path = lndb_root / "masks" / mask_filename
        
        if not mask_path.exists():
            print("Missing mask:", mask_path)
            continue

        mask, _ = load_mask(mask_path)

        # Compute features
        hu_mean, hu_std = compute_hu_stats(vol, mask)
        long_axis = compute_long_axis_mm(mask, spacing)
        volume_mm3 = compute_volume_mm3(mask, spacing)
        n_type = classify_type(hu_mean)

        rows.append({
            "LNDbID": vol_key,
            "NoduleID": int(nodule_id),
            "hu_mean": hu_mean,
            "hu_std": hu_std,
            "long_axis_mm": long_axis,
            "volume_mm3": volume_mm3,
            "type": n_type,
            "malignancy": int(malignancy)
        })

    out_df = pd.DataFrame(rows)
    out_df.to_csv(save_csv, index=False)

    print("Saved:", save_csv)
