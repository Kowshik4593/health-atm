import numpy as np
from sklearn.cluster import DBSCAN

def smart_filter(filtered_centers, features):
    """
    filtered_centers: list of (z,y,x)
    features: list of dicts [{hu_mean, long_axis_mm, volume_mm3, ...}]
    """

    # Stage 1 — remove air/noise
    cand = []
    for c, f in zip(filtered_centers, features):
        if f["hu_mean"] > -800:   # keep only real tissue
            cand.append((c, f))

    if not cand:
        return [], []

    centers = [c for c, f in cand]
    feats   = [f for c, f in cand]

    # Stage 2 — remove tiny candidates (<4 mm)
    cand2_centers = []
    cand2_feats   = []
    for c, f in zip(centers, feats):
        if f["long_axis_mm"] >= 4:
            cand2_centers.append(c)
            cand2_feats.append(f)

    if not cand2_centers:
        return [], []

    # Stage 3 — cluster to remove duplicates
    coords = np.array(cand2_centers)
    clustering = DBSCAN(eps=10, min_samples=1).fit(coords)  # 10 mm
    labels = clustering.labels_

    final_centers = []
    final_feats   = []

    for lab in np.unique(labels):
        idxs = np.where(labels == lab)[0]
        # choose the candidate with highest hu_mean (most solid)
        best_idx = max(idxs, key=lambda i: cand2_feats[i]["hu_mean"])
        final_centers.append(cand2_centers[best_idx])
        final_feats.append(cand2_feats[best_idx])

    return final_centers, final_feats
