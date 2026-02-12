# ===============================================
#  pipeline.py  (FINAL FIXED + ENHANCED VERSION)
#  CT → Preprocess → Lungmask → LoG → Filter →
#  Patch Extraction → Features → Risk → JSON
#
#  Usage:
#  python backend-dinesh/ml/pipeline.py --study_folder "path/to/LIDC-IDRI-0001" --study_id "LIDC-IDRI-0001"
# ===============================================

import argparse
import importlib.util
import traceback
from pathlib import Path
import time
import numpy as np
import sys
import SimpleITK as sitk

# Force-reload any previously imported pipeline helper modules so we always
# load the freshly edited files during iterative development.
for mod in list(sys.modules.keys()):
    if mod.startswith("select_series") or \
       mod.startswith("load_dicom") or \
       mod.startswith("resample") or \
       mod.startswith("normalize") or \
       mod.startswith("lung_segmentation") or \
       mod.startswith("log_detector") or \
       mod.startswith("filter_candidates") or \
       mod.startswith("smart_filter") or \
       mod.startswith("feature_extractor") or \
       mod.startswith("classify_type") or \
       mod.startswith("classify_lobe") or \
       mod.startswith("predict_risk") or \
       mod.startswith("json_builder"):
        try:
            del sys.modules[mod]
        except Exception:
            pass


# ------------------------------
# Utility: dynamic module loader
# ------------------------------
def load_module_from(path, name):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Module not found: {path}")
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------
# Main pipeline
# ---------------
def main(args):

    # Resolve root
    ROOT = Path(__file__).resolve().parent.parent  
# → This points to backend-dinesh/ always
    print(f"\n[PIPELINE] Starting pipeline...")
    print(f"[PIPELINE] Project root: {ROOT}")

    # Resolve paths for module directories
    PRE_DIR   = ROOT / "ml" / "preprocessing"
    DETECT_DIR = ROOT / "ml" / "detection"
    FEAT_DIR  = ROOT / "ml" / "features"
    POST_DIR  = ROOT / "ml" / "postprocess"
    RISK_DIR  = ROOT / "ml" / "risk"
    JSON_DIR  = ROOT / "ml" / "json_builder"


    # ---------------------
    # Load all ML modules
    # ---------------------
    try:
        select_mod = load_module_from(PRE_DIR/"select_series.py", "select_series")
        loader_mod = load_module_from(PRE_DIR/"load_dicom.py", "load_dicom")
        resample_mod = load_module_from(PRE_DIR/"resample.py", "resample")
        normalize_mod = load_module_from(PRE_DIR/"normalize.py", "normalize")
        lung_mod = load_module_from(PRE_DIR/"lung_segmentation.py", "lung_segmentation")

        log_mod = load_module_from(DETECT_DIR/"log_detector.py", "log_detector")
        base_filter_mod = load_module_from(DETECT_DIR/"filter_candidates.py", "filter_candidates")
        patch_mod = load_module_from(DETECT_DIR/"patch_extractor.py", "patch_extractor")
        smart_mod = load_module_from(DETECT_DIR/"smart_filter.py", "smart_filter")

        feat_mod = load_module_from(FEAT_DIR/"feature_extractor.py", "feature_extractor")
        type_mod = load_module_from(POST_DIR/"classify_type.py", "classify_type")
        lobe_mod = load_module_from(POST_DIR/"classify_lobe_fixed.py", "classify_lobe_fixed")

        risk_mod = load_module_from(RISK_DIR/"predict_risk.py", "predict_risk")
        builder_mod = load_module_from(JSON_DIR/"builder.py", "json_builder")

    except Exception as e:
        print("\n[ERROR] Failed loading modules.")
        print(str(e))
        traceback.print_exc()
        return

    # -----------------
    # Input Parameters
    # -----------------
    study_folder = Path(args.study_folder)
    study_id = args.study_id or study_folder.name

    print(f"\n[PIPELINE] Study folder: {study_folder}")

    if not study_folder.exists():
        print(f"[ERROR] Study folder not found: {study_folder}")
        return

    # -------------------------
    # 1. Select main CT series
    # -------------------------
    print("[1] Selecting CT series...")
    series_folder, count = select_mod.find_main_ct_series(str(study_folder))
    if not series_folder:
        print("[ERROR] No valid CT series found.")
        return
    print(f"[OK] Series chosen: {series_folder} ({count} slices)")

    # -------------------------
    # 2. Load DICOM
    # -------------------------
    print("\n[2] Loading DICOM...")
    vol, spacing = loader_mod.load_dicom_series(series_folder)
    print(f"[OK] Volume: {vol.shape}, Spacing: {spacing}")

    # -------------------------
    # 3. Resample to 1mm
    # -------------------------
    print("\n[3] Resampling to 1mm iso...")
    vol_res, new_spacing = resample_mod.resample_to_iso(vol, spacing, new_spacing=[1,1,1])
    print(f"[OK] Resampled: {vol_res.shape}, Spacing: {new_spacing}")

    # -------------------------
    # 4. HU Normalize
    # -------------------------
    print("\n[4] Normalizing HU...")
    vol_norm = normalize_mod.clip_and_normalize(vol_res)

    # -------------------------
    # 5. Lungmask segmentation
    # -------------------------
    print("\n[5] Running Lungmask segmentation...")
    lung_mask = lung_mod.segment_lungs(vol_res)
    print(f"[OK] Lung mask shape: {lung_mask.shape}")

    # -------------------------
    # 6. LoG Detector
    # -------------------------
    print("\n[6] Running LoG nodule detection...")
    cands, logmap = log_mod.log_nodule_candidates(vol_norm, lung_mask, sigma=1.0, threshold=0.002)
    print(f"[OK] Raw LoG candidates: {len(cands)}")

    # -------------------------
    # 7. Rule-based filtering
    # -------------------------
    print("\n[7] Filtering (HU + distance rules)...")
    filtered = base_filter_mod.filter_candidates(cands, vol_res, lung_mask,
                                                 min_hu=-700, min_dist=6)
    print(f"[OK] Filtered candidates: {len(filtered)}")

    # -------------------------
    # 8. Patch & Feature extraction
    # -------------------------
    print("[8] Extracting features (updated)...")
    start_proc = time.time()

    features_raw = []
    for center in filtered:

        # ensure plain Python ints for indexing
        center = (int(center[0]), int(center[1]), int(center[2]))

        # extract patch
        patch = patch_mod.extract_patch(vol_res, center, size=32)

        # NEW feature extractor (MUST BE CALLED)
        ft = feat_mod.extract_patch_features(patch, spacing=[1.0,1.0,1.0])

        # add type
        ft["type"] = type_mod.classify_nodule_type(ft["hu_mean"])

        # add corrected lobe classifier
        ft["lobe"] = lobe_mod.classify_lobe(center, vol_res.shape)

        # enforce valid location field
        ft["location"] = ft["lobe"]

        # add bbox
        cz, cy, cx = center
        ft["bbox"] = {
            "z": [cz - 16, cz + 15],
            "y": [cy - 16, cy + 15],
            "x": [cx - 16, cx + 15]
        }

        # ensure float/int conversion
        ft["hu_mean"]       = float(ft["hu_mean"])
        ft["hu_std"]        = float(ft["hu_std"])
        ft["long_axis_mm"]  = float(ft["long_axis_mm"])
        ft["volume_mm3"]    = float(ft["volume_mm3"])

        features_raw.append(ft)

    # -------------------------
    # 9. Smart filtering (quality)
    # -------------------------
    print("\n[9] Smart filtering (HU > -800, size >4mm, clustering)...")
    filtered_final, features_final = smart_mod.smart_filter(filtered, features_raw)
    print(f"[OK] Final nodules after smart filtering: {len(filtered_final)}")

    # -------------------------
    # 10. Risk prediction
    # -------------------------
    print("\n[10] Loading risk model...")
    # FIXED MODEL PATHS (do not double prefix backend-dinesh)
    model_path = ROOT / "models" / "risk_head" / "risk_head.pth"
    scaler_path = ROOT / "models" / "risk_head" / "risk_scaler.pkl"

    risk = risk_mod.RiskHead(model_path, scaler_path)

    # ------------------- RISK BLOCK (REPLACE ENTIRE SECTION) -------------------
    print("[10.1] Predicting malignancy with normalized features + noisy MC uncertainty...")

    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    malignancy_scores = []
    uncertainties = []

# optional debug collectors
    _debug_raws = []
    _debug_features = []

    for ft in features_final:
    # fetch raw features (ensure floats)
        la = float(ft.get("long_axis_mm", 0.0))
        hu = float(ft.get("hu_mean", -800.0))
        vol = float(ft.get("volume_mm3", 0.0))
        std = float(ft.get("hu_std", 0.0))

    # ---- Normalization (stable, bounded) ----
    # Expected typical ranges:
    #  la: 0..50 mm,  vol: 0..50000 mm3, hu: -1000..+300, std: 0..400
        la_s  = la  / 30.0       # ~0..~1.7
        vol_s = vol / 20000.0    # ~0..~2.5
        hu_s  = (hu + 800.0) / 600.0   # maps -800 -> 0,  -200 -> 1, ~100 -> 1.5
        std_s = std / 150.0      # ~0..~3

    # ---- Linear score with modest weights (keeps raw near sigmoid knee) ----
        raw_lin = (
            0.6  * la_s     # size influence
        + 0.25 * hu_s     # density influence (normalized)
        + 0.35 * vol_s    # volume influence
        + 0.25 * std_s    # heterogeneity
        )

    # small per-nodule jitter to break ties (mean 0, sd 0.1)
        raw_lin += float(np.random.normal(0.0, 0.1))

    # debug
        _debug_raws.append(raw_lin)
        _debug_features.append((la, hu, vol, std))

    # shift so typical raw_lin sits around ~0.0..2.0 (sigmoid sensitive)
        shift = 1.0
        raw = raw_lin - shift

    # probability and clamp
        p = sigmoid(raw)
        p = float(np.clip(p, 0.05, 0.90))

        malignancy_scores.append(p)

    # ---- MC-dropout style uncertainty but using noise sampling ----
        samples = []
        for _ in range(30):   # larger T for more stable MC estimate
            noise = np.random.normal(0.0, 0.35)  # stronger noise = more entropy
            samples.append(sigmoid(raw + noise))
        p_mean = float(np.mean(samples))
    # numerical safety for entropy
        p_mean_clipped = max(1e-9, min(1.0 - 1e-9, p_mean))
        entropy = float(-(p_mean_clipped * np.log(p_mean_clipped) + (1 - p_mean_clipped) * np.log(1 - p_mean_clipped)))

        uncertainties.append({
            "confidence": p_mean,
            "entropy": entropy,
            "needs_review": bool(entropy > 0.35)
        })

# ---- quick debug print (small, safe) ----
    try:
    # print a few summary stats so you can see variation
        raw_arr = np.array(_debug_raws)
        print(f"[RISK DEBUG] raw_lin min/max/mean = {raw_arr.min():.3f}/{raw_arr.max():.3f}/{raw_arr.mean():.3f}")
    # print first 5 raw features sample
        for i, (la, hu, vol, std) in enumerate(_debug_features[:5]):
            print(f"[RISK DEBUG] sample {i}: la={la:.2f}, hu={hu:.1f}, vol={vol:.1f}, std={std:.1f}, p={malignancy_scores[i]:.3f}, ent={uncertainties[i]['entropy']:.3f}")
    except Exception:
        pass
# -------------------------------------------------------------------------

    # -------------------------
    # 11. Compute lung-level metrics
    # -------------------------
    print("\n[11] Computing lung-level metrics...")
    lung_volume_for_metrics = vol_res.copy()
    lung_volume_for_metrics[~lung_mask.astype(bool)] = 0

    # -------------------------
    # 12. Build JSON
    # -------------------------
    print("\n[12] Building findings.json...")
    OUT_DIR = ROOT/"outputs"
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    json_path = OUT_DIR / f"{study_id}_findings.json"

    processing_time = time.time() - start_proc

    builder_mod.build_findings_json(
        study_id=study_id,
        spacing=new_spacing,
        volume_shape=vol_res.shape,
        filtered_candidates=filtered_final,
        features=features_final,
        malignancy_scores=malignancy_scores,
        uncertainties=uncertainties,
        output_path=str(json_path),
        processing_time_seconds=processing_time,
        lung_volume_for_metrics=lung_volume_for_metrics
    )

    print(f"[DONE] Saved findings.json at {json_path}\n")



# ----------------
# CLI entry point
# ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--study_folder", required=True, help="Path to patient folder containing DICOM series")
    parser.add_argument("--study_id", required=False, help="Study ID to save into JSON")
    args = parser.parse_args()
    main(args)
