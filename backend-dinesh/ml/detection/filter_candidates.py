import numpy as np

def filter_candidates(cands, volume, lung_mask, min_hu=-700, min_dist=3):
    filtered = []
    for (z,y,x) in cands:
        # ignore outside lung
        if lung_mask[z,y,x] == 0:
            continue

        # intensity check
        if volume[z,y,x] < min_hu:  # too soft, not a solid nodule
            continue

        # merge very close peaks
        if filtered:
            dist = np.min([np.linalg.norm(np.array([z,y,x]) - np.array(f)) for f in filtered])
            if dist < min_dist:
                continue

        filtered.append((z,y,x))

    return filtered
