# extract_lndb_fast.py
import zipfile
import pandas as pd
import SimpleITK as sitk
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA

def build_volume_index(lndb_root):
    volume_index = {}
    for i in range(6):
        data_dir = Path(lndb_root) / f"data{i}"
        if not data_dir.exists(): continue
        for f in data_dir.iterdir():
            if f.suffix == ".mhd":
                key = f.stem  # LNDb-0001
                volume_index[key] = str(f)
    return volume_index

def world_to_index(img, x, y, z):
    # img is SimpleITK image
    # LNDb coordinates appear as (x,y,z) physical coordinates
    # SimpleITK expects a 3-tuple (x,y,z) in image physical space
    try:
        idx = img.TransformPhysicalPointToIndex((float(x), float(y), float(z)))
        # TransformPhysicalPointToIndex returns indices as (i,j,k) in x,y,z coordinates -> need (z,y,x) for numpy
        return (idx[2], idx[1], idx[0])
    except Exception:
        # fallback: round dividing by spacing (less accurate)
        sp = img.GetSpacing()
        origin = img.GetOrigin()
        ix = int(round((float(x) - origin[0]) / sp[0]))
        iy = int(round((float(y) - origin[1]) / sp[1]))
        iz = int(round((float(z) - origin[2]) / sp[2]))
        return (iz, iy, ix)

def extract_features_spherical(img_path, cx_mm, cy_mm, cz_mm, radius_mm=8.0):
    img = sitk.ReadImage(str(img_path))
    arr = sitk.GetArrayFromImage(img).astype(np.float32)   # (z,y,x)
    spacing = img.GetSpacing()  # (x,y,z)
    spacing = [spacing[2], spacing[1], spacing[0]]  # convert to (z,y,x) spacing

    # convert world coords -> voxel index (z,y,x)
    zc, yc, xc = world_to_index(img, cx_mm, cy_mm, cz_mm)

    # radius in voxels (approx z,y,x using per-axis spacing)
    rz = int(max(1, round(radius_mm / spacing[0])))
    ry = int(max(1, round(radius_mm / spacing[1])))
    rx = int(max(1, round(radius_mm / spacing[2])))

    z1, z2 = max(0, zc-rz), min(arr.shape[0], zc+rz+1)
    y1, y2 = max(0, yc-ry), min(arr.shape[1], yc+ry+1)
    x1, x2 = max(0, xc-rx), min(arr.shape[2], xc+rx+1)

    patch = arr[z1:z2, y1:y2, x1:x2]

    # build spherical mask in voxel coordinates
    zz, yy, xx = np.meshgrid(
        np.arange(z1, z2), np.arange(y1, y2), np.arange(x1, x2), indexing='ij'
    )
    dist_mm = np.sqrt(((zz - zc) * spacing[0])**2 + ((yy - yc) * spacing[1])**2 + ((xx - xc) * spacing[2])**2)
    sph_mask = dist_mm <= radius_mm

    # HU stats inside sphere
    vals = patch[sph_mask]
    if vals.size == 0:
        hu_mean, hu_std = -1000.0, 0.0
    else:
        hu_mean = float(vals.mean())
        hu_std = float(vals.std())

    # approximate long axis using PCA on voxels inside mask with HU > -950
    coords = np.argwhere(sph_mask & (patch > -950))
    if coords.shape[0] < 5:
        long_axis = 0.0
    else:
        coords_mm = coords * np.array([spacing[0], spacing[1], spacing[2]])
        pca = PCA(n_components=1)
        pca.fit(coords_mm)
        axis = pca.components_[0]
        proj = coords_mm @ axis
        long_axis = float(proj.max() - proj.min())

    # approx volume: voxels inside mask with HU > -950
    voxel_vol = spacing[0] * spacing[1] * spacing[2]
    vol_count = int(np.sum(sph_mask & (patch > -950)))
    vol_mm3 = float(vol_count * voxel_vol)

    # type by hu_mean
    if hu_mean > -300:
        ntype = "solid"
    elif hu_mean > -700:
        ntype = "subsolid"
    else:
        ntype = "ground-glass"

    return {
        "hu_mean": hu_mean,
        "hu_std": hu_std,
        "long_axis_mm": long_axis,
        "volume_mm3": vol_mm3,
        "type": ntype
    }

def extract_lndb_fast(lndb_root, save_csv, radius_mm=8.0):
    lndb_root = Path(lndb_root)
    z = zipfile.ZipFile(lndb_root / "trainset_csv.zip")
    df_nod = pd.read_csv(z.open("trainNodules.csv"))
    df_gt = pd.read_csv(z.open("trainNodules_gt.csv"))

    # build volume index
    volume_index = build_volume_index(lndb_root)

    rows = []
    # iterate ground-truth rows (use df_gt to get AgrLevel)
    for _, r in df_gt.iterrows():
        lnid = int(r["LNDbID"])
        # build key
        vol_key = f"LNDb-{lnid:04d}"
        if vol_key not in volume_index:
            continue
        vol_path = volume_index[vol_key]

        x = r["x"]; y = r["y"]; zcoord = r["z"]
        agr = r.get("AgrLevel", np.nan)
        label = 1 if (not pd.isna(agr) and float(agr) >= 3.0) else 0

        feats = extract_features_spherical(vol_path, x, y, zcoord, radius_mm=radius_mm)
        rows.append({
            "LNDbID": vol_key,
            "x": x, "y": y, "z": zcoord,
            "hu_mean": feats["hu_mean"],
            "hu_std": feats["hu_std"],
            "long_axis_mm": feats["long_axis_mm"],
            "volume_mm3": feats["volume_mm3"],
            "type": feats["type"],
            "malignancy": int(label)
        })

    out = pd.DataFrame(rows)
    Path(save_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(save_csv, index=False)
    print("Saved:", save_csv)
