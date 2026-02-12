# backend-dinesh/ml/json_builder/builder.py
import json
from datetime import datetime
import numpy as np

def compute_lung_health_metrics(volume, spacing):
    """
    Simple estimators:
    - emphysema_score = % voxels < -950 HU inside lung
    - consolidation_score = % voxels > -200 HU inside lung
    - fibrosis_score = texture roughness proxy (std of Laplacian) normalized
    """
    # volume: full resampled CT numpy array (Z,Y,X) if provided; spacing used for voxel volume
    # This function assumes you pass a masked lung volume; if None, return zeros
    if volume is None:
        return 0.0, 0.0, 0.0
    try:
        pct_emphy = float(np.mean(volume < -950))
        pct_cons = float(np.mean(volume > -200))
        # rough proxy for fibrosis: normalized std of Laplacian
        from scipy import ndimage
        lap = ndimage.laplace(volume.astype(np.float32))
        fibrosis_proxy = float(np.clip(np.std(lap) / (abs(np.mean(volume)) + 1e-6), 0.0, 1.0))
        return pct_emphy, fibrosis_proxy, pct_cons
    except Exception:
        return 0.0, 0.0, 0.0

def build_findings_json(study_id, spacing, volume_shape,
                        filtered_candidates, features,
                        malignancy_scores, uncertainties,
                        output_path, processing_time_seconds=None,
                        lung_volume_for_metrics=None):
    """
    filtered_candidates: list of centers [(z,y,x),...]
    features: list of dicts aligned with filtered_candidates
    malignancy_scores: list aligned
    uncertainties: list aligned
    lung_volume_for_metrics: optional numpy array (masked lung) to compute lung-level metrics
    """
        # ---------------------------------------
    # Standardize Python types for JSON
    # ---------------------------------------
    def py(v):
        """Convert numpy types to plain Python types."""
        if isinstance(v, (np.int32, np.int64)):
            return int(v)
        if isinstance(v, (np.float32, np.float64)):
            return float(v)
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v

    nodules = []
    for i, (center, ft, p, unc) in enumerate(zip(filtered_candidates, features, malignancy_scores, uncertainties)):
        cz, cy, cx = [py(c) for c in center]

        bbox = ft.get("bbox", None)
        if bbox:
            bbox = {
                "z": [py(bbox["z"][0]), py(bbox["z"][1])],
                "y": [py(bbox["y"][0]), py(bbox["y"][1])],
                "x": [py(bbox["x"][0]), py(bbox["x"][1])]
            }

        nodules.append({
            "id": int(i),
            "centroid": [cz, cy, cx],
            "coordinates": [cz, cy, cx],
            "bbox": bbox,
            "mask_path": None,  # mask saved later in Phase-2 (optional)
            "long_axis_mm": py(ft.get("long_axis_mm", 0.0)),
            "volume_mm3": py(ft.get("volume_mm3", 0.0)),
            "type": ft.get("type", "unknown"),
            "lobe": ft.get("lobe", "unknown"),
            "location": ft.get("lobe", "unknown"),
            "prob_malignant": py(p),
            "uncertainty": {
                "confidence": py(unc.get("confidence", 0.0)),
                "entropy": py(unc.get("entropy", 0.0)),
                "needs_review": bool(unc.get("needs_review", False))
            }
        })


    # lung-level metrics
    emphysema_score, fibrosis_score, consolidation_score = compute_lung_health_metrics(lung_volume_for_metrics, spacing) if lung_volume_for_metrics is not None else (0.0, 0.0, 0.0)
    lung_health_text = "Lungs appear within expected attenuation ranges." if emphysema_score < 0.05 else "Findings suggest increased low attenuation areas consistent with emphysema."

    largest = 0.0
    high_risk = 0
    for n in nodules:
        largest = max(largest, n["long_axis_mm"])
        if n["prob_malignant"] > 0.5:
            high_risk += 1

    impression = (
        f"{len(nodules)} nodules detected. "
        f"Largest measures {largest:.1f} mm. "
        f"{high_risk} nodules show moderate-to-high malignancy probability. "
        "Recommend clinical correlation."
    )
    summary_text = "This exam shows multiple small nodules. Please consult your clinician for follow-up."

    out = {
        "study_id": study_id,
        "metadata": {
            "volume_shape": list(map(int, volume_shape)),
            "spacing": [float(s) for s in spacing]
        },
        "num_candidates": int(len(filtered_candidates) if filtered_candidates is not None else 0),
        "num_nodules": int(len(nodules)),
        "processing_time_seconds": float(processing_time_seconds) if processing_time_seconds is not None else 0.0,
        "lung_health": lung_health_text,
        "emphysema_score": float(emphysema_score),
        "fibrosis_score": float(fibrosis_score),
        "consolidation_score": float(consolidation_score),
        "impression": impression,
        "summary_text": summary_text,
        "nodules": nodules,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)
    print("Saved findings JSON:", output_path)
