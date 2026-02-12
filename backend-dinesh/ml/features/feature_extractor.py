# backend-dinesh/ml/features/feature_extractor.py

import numpy as np
from sklearn.decomposition import PCA

def make_mask(patch):
    """Adaptive segmentation mask for nodule-like structures."""
    hu = patch.astype(np.float32)

    # adaptive threshold: soft tissue separation
    t = hu.mean() - 0.6 * hu.std()
    mask = (hu > t) & (hu > -850)
    # remove tiny islands
    if mask.sum() < 10:
        mask = hu > -700
    return mask

def compute_hu_stats(patch):
    vals = patch[patch > -950]
    if vals.size < 3:
        return float(patch.mean()), float(patch.std())
    return float(vals.mean()), float(vals.std())

def compute_volume_mm3(mask, spacing):
    voxel_vol = spacing[0] * spacing[1] * spacing[2]
    return float(mask.sum() * voxel_vol)

def compute_long_axis_mm(mask, spacing):
    pts = np.argwhere(mask)
    if pts.shape[0] < 5:
        return 0.0
    pts_mm = pts * spacing
    pts_center = pts_mm - pts_mm.mean(axis=0)
    pca = PCA(n_components=1)
    axis = pca.fit(pts_center).components_[0]
    proj = pts_center @ axis
    return float(proj.max() - proj.min())

def extract_patch_features(patch, spacing=[1.0,1.0,1.0]):
    mask = make_mask(patch)

    hu_mean, hu_std = compute_hu_stats(patch)
    long_axis = compute_long_axis_mm(mask, spacing)
    vol = compute_volume_mm3(mask, spacing)

    return {
        "hu_mean": hu_mean,
        "hu_std": hu_std,
        "long_axis_mm": long_axis,
        "volume_mm3": vol,
        "mask": mask
    }
import numpy as np
from sklearn.decomposition import PCA

def compute_hu_stats(patch, lung_threshold=-950):
    """
    patch: numpy array (Z,Y,X) in HU
    Returns (hu_mean, hu_std)
    """
    vals = patch[patch > lung_threshold]
    if vals.size == 0:
        return float(patch.mean()), float(patch.std())
    return float(vals.mean()), float(vals.std())


def compute_long_axis_mm(patch, spacing):
    # foreground = voxels > -300 (solid & semi-solid)
    fg = patch > -300
    coords = np.argwhere(fg)

    if coords.shape[0] < 5:
        return 0.0

    coords_mm = coords * np.array(spacing)

    # PCA-based long axis
    pca = PCA(n_components=1)
    pca.fit(coords_mm)
    axis = pca.components_[0]
    proj = coords_mm @ axis

    long_axis = proj.max() - proj.min()
    return float(long_axis)


def compute_volume_mm3(patch, spacing):
    fg = patch > -300
    voxel_volume = spacing[0] * spacing[1] * spacing[2]
    return float(fg.sum() * voxel_volume)

def compute_volume_mm3_from_mask(mask, spacing):
    """
    mask: boolean ndarray of same shape as patch or full volume (True=foreground)
    spacing: [sz, sy, sx] (mm)
    """
    voxel_vol = float(spacing[0] * spacing[1] * spacing[2])
    count = int(np.sum(mask > 0))
    return float(count * voxel_vol)

def compute_long_axis_mm_from_mask(mask, spacing):
    """
    mask: boolean ndarray
    spacing: [sz, sy, sx] (mm)
    uses PCA along voxel coordinates (converted to mm)
    """
    coords = np.argwhere(mask > 0)  # (N,3) in voxel coords z,y,x
    if coords.shape[0] < 5:
        return 0.0
    coords_mm = coords * np.array(spacing)[None, :]
    # PCA
    try:
        pca = PCA(n_components=1)
        pca.fit(coords_mm)
        axis = pca.components_[0]
        proj = coords_mm @ axis
        long_axis = float(proj.max() - proj.min())
        return long_axis
    except Exception:
        # fallback: max pairwise distance (approx)
        mins = coords_mm.min(axis=0)
        maxs = coords_mm.max(axis=0)
        return float(np.linalg.norm(maxs - mins))

# helper to use mask if available or fallback to thresholding
def extract_patch_features(patch, spacing, mask=None):
    """
    patch: (Z,Y,X) HU patch
    spacing: [sz,sy,sx] in mm
    mask: optional boolean mask same shape as patch; if None, thresholding is used
    returns dict with hu_mean, hu_std, long_axis_mm, volume_mm3
    """
    if mask is None:
        # use conservative threshold to identify nodule tissue
        fg_mask = (patch > -950) & (patch > (patch.mean() - 1.5*patch.std()))
    else:
        fg_mask = mask.astype(bool)

    hu_mean, hu_std = compute_hu_stats(patch, lung_threshold=-950)
    volume_mm3 = compute_volume_mm3_from_mask(fg_mask, spacing)
    long_axis_mm = compute_long_axis_mm_from_mask(fg_mask, spacing)
    return {
        "hu_mean": float(hu_mean),
        "hu_std": float(hu_std),
        "long_axis_mm": float(long_axis_mm),
        "volume_mm3": float(volume_mm3)
    }