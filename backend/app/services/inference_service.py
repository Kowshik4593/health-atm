# backend/app/services/inference_service.py
"""
AI Inference Service for HealthATM.

This module handles:
- Loading the fine-tuned Full 3D UNet model
- Sliding-window inference on 3D CT volumes
- Nodule extraction from segmentation masks
- GradCAM XAI heatmap generation
- Producing structured findings dictionaries

Architecture:
    DICOM/NPY Input -> Preprocessing -> Sliding Window -> Segmentation Mask
    -> Connected Components -> Nodule List -> Classification -> XAI -> findings.json
"""

import os
import time
import json
import traceback
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np

# Lazy imports for torch (avoids startup crash if torch missing)
_model = None
_device = None
_model_loaded = False

# =============================================================================
# Configuration
# =============================================================================

ML_DIR = Path(__file__).parent.parent.parent / "ml"
MODELS_DIR = ML_DIR / "models"
MODEL_PATH = MODELS_DIR / "unet3d_finetuned.pth"
EDGE_MODEL_PATH = MODELS_DIR / "unet3d_edge.pt"

PATCH_SIZE = 64
STRIDE = 48  # Overlap for smoother predictions
HU_MIN = -1000
HU_MAX = 400


# =============================================================================
# Model Definition (Must match training)
# =============================================================================

def _build_model():
    """Build the FullUNet3D architecture."""
    import torch
    import torch.nn as nn

    class DoubleConv(nn.Module):
        def __init__(self, in_channels, out_channels):
            super().__init__()
            self.conv = nn.Sequential(
                nn.Conv3d(in_channels, out_channels, 3, padding=1),
                nn.BatchNorm3d(out_channels),
                nn.ReLU(inplace=True),
                nn.Conv3d(out_channels, out_channels, 3, padding=1),
                nn.BatchNorm3d(out_channels),
                nn.ReLU(inplace=True)
            )

        def forward(self, x):
            return self.conv(x)

    class FullUNet3D(nn.Module):
        def __init__(self, in_channels=1, out_channels=1):
            super().__init__()
            self.inc = DoubleConv(in_channels, 32)
            self.down1 = nn.Sequential(nn.MaxPool3d(2), DoubleConv(32, 64))
            self.down2 = nn.Sequential(nn.MaxPool3d(2), DoubleConv(64, 128))
            self.down3 = nn.Sequential(nn.MaxPool3d(2), DoubleConv(128, 256))
            self.up1 = nn.ConvTranspose3d(256, 128, 2, stride=2)
            self.conv1 = DoubleConv(256, 128)
            self.up2 = nn.ConvTranspose3d(128, 64, 2, stride=2)
            self.conv2 = DoubleConv(128, 64)
            self.up3 = nn.ConvTranspose3d(64, 32, 2, stride=2)
            self.conv3 = DoubleConv(64, 32)
            self.outc = nn.Conv3d(32, out_channels, 1)
            self.classifier = nn.Sequential(
                nn.AdaptiveAvgPool3d(1),
                nn.Flatten(),
                nn.Linear(256, 64),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(64, 1)
            )

        def forward(self, x):
            x1 = self.inc(x)
            x2 = self.down1(x1)
            x3 = self.down2(x2)
            x4 = self.down3(x3)
            u1 = self.up1(x4)
            u1 = torch.cat([u1, x3], dim=1)
            u1 = self.conv1(u1)
            u2 = self.up2(u1)
            u2 = torch.cat([u2, x2], dim=1)
            u2 = self.conv2(u2)
            u3 = self.up3(u2)
            u3 = torch.cat([u3, x1], dim=1)
            u3 = self.conv3(u3)
            mask = torch.sigmoid(self.outc(u3))
            risk = torch.sigmoid(self.classifier(x4))
            return mask, risk

    return FullUNet3D


# =============================================================================
# Model Loading (Singleton)
# =============================================================================

def load_model():
    """Load model into memory (singleton pattern)."""
    global _model, _device, _model_loaded
    import torch

    if _model_loaded and _model is not None:
        return _model, _device

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[inference] Loading model on: {_device}")

    FullUNet3D = _build_model()
    _model = FullUNet3D().to(_device)

    if MODEL_PATH.exists():
        _model.load_state_dict(torch.load(str(MODEL_PATH), map_location=_device))
        print(f"[inference] [OK] Model loaded from {MODEL_PATH}")
    elif EDGE_MODEL_PATH.exists():
        # Try JIT model
        _model = torch.jit.load(str(EDGE_MODEL_PATH), map_location=_device)
        print(f"[inference] [OK] JIT Model loaded from {EDGE_MODEL_PATH}")
    else:
        print(f"[inference] [WARN] No model weights found! Using random weights.")

    _model.eval()
    _model_loaded = True
    return _model, _device


# =============================================================================
# Preprocessing
# =============================================================================

def normalize_hu(volume: np.ndarray) -> np.ndarray:
    """Normalize HU values to [0, 1]."""
    volume = volume.astype(np.float32)
    volume = (volume - HU_MIN) / (HU_MAX - HU_MIN)
    volume = np.clip(volume, 0, 1)
    return volume


def load_npy_volume(path: str) -> np.ndarray:
    """Load a .npy volume file."""
    data = np.load(path, allow_pickle=True)
    if isinstance(data, np.lib.npyio.NpzFile):
        # .npz file
        if 'image' in data:
            return data['image']
        return data[data.files[0]]
    return data


def load_dicom_volume(dicom_dir: str) -> Tuple[np.ndarray, List[float]]:
    """
    Load DICOM series from a directory.

    Returns:
        Tuple of (volume_array, spacing)
    """
    try:
        import pydicom
        import glob as globmod

        dcm_files = sorted(globmod.glob(os.path.join(dicom_dir, "*.dcm")))
        if not dcm_files:
            raise FileNotFoundError(f"No DICOM files in {dicom_dir}")

        slices = [pydicom.dcmread(f) for f in dcm_files]
        slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))

        # Get spacing
        try:
            slice_thickness = abs(
                slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2]
            )
        except Exception:
            slice_thickness = float(slices[0].SliceThickness)

        pixel_spacing = [float(x) for x in slices[0].PixelSpacing]
        spacing = [slice_thickness, pixel_spacing[0], pixel_spacing[1]]

        # Build volume
        image = np.stack([s.pixel_array for s in slices]).astype(np.int16)

        # Convert to HU
        intercept = float(slices[0].RescaleIntercept)
        slope = float(slices[0].RescaleSlope)
        if slope != 1:
            image = slope * image.astype(np.float64)
            image = image.astype(np.int16)
        image += np.int16(intercept)

        return image.astype(np.float32), spacing

    except ImportError:
        raise ImportError("pydicom is required for DICOM loading. Install with: pip install pydicom")


# =============================================================================
# Sliding Window Inference
# =============================================================================

def sliding_window_inference(
    model,
    volume: np.ndarray,
    device,
    patch_size: int = PATCH_SIZE,
    stride: int = STRIDE,
    threshold: float = 0.5
) -> Tuple[np.ndarray, float]:
    """
    Run sliding window inference on a 3D volume.

    Args:
        model: PyTorch model
        volume: Normalized 3D numpy array (D, H, W)
        device: torch device
        patch_size: Size of cubic patches
        stride: Step size between patches
        threshold: Binarization threshold

    Returns:
        Tuple of (binary_mask, average_risk_score)
    """
    import torch

    D, H, W = volume.shape
    output_mask = np.zeros_like(volume, dtype=np.float32)
    count_map = np.zeros_like(volume, dtype=np.float32)
    risk_scores = []

    # Pad volume if smaller than patch_size
    pad_d = max(0, patch_size - D)
    pad_h = max(0, patch_size - H)
    pad_w = max(0, patch_size - W)
    if pad_d > 0 or pad_h > 0 or pad_w > 0:
        volume = np.pad(volume, ((0, pad_d), (0, pad_h), (0, pad_w)), mode='constant')
        output_mask = np.pad(output_mask, ((0, pad_d), (0, pad_h), (0, pad_w)), mode='constant')
        count_map = np.pad(count_map, ((0, pad_d), (0, pad_h), (0, pad_w)), mode='constant')

    pD, pH, pW = volume.shape
    total_patches = 0

    # Calculate total patches for logging
    z_steps = list(range(0, pD - patch_size + 1, stride))
    y_steps = list(range(0, pH - patch_size + 1, stride))
    x_steps = list(range(0, pW - patch_size + 1, stride))
    if not z_steps:
        z_steps = [0]
    if not y_steps:
        y_steps = [0]
    if not x_steps:
        x_steps = [0]
    total_expected = len(z_steps) * len(y_steps) * len(x_steps)
    print(f"[inference] Sliding window: {total_expected} patches ({pD}x{pH}x{pW})")

    with torch.no_grad():
        for z in z_steps:
            for y in y_steps:
                for x in x_steps:
                    patch = volume[z:z+patch_size, y:y+patch_size, x:x+patch_size]

                    # Ensure exact size
                    if patch.shape != (patch_size, patch_size, patch_size):
                        continue

                    tensor = torch.tensor(patch, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
                    mask_pred, risk_pred = model(tensor)

                    mask_np = mask_pred.squeeze().cpu().numpy()
                    risk_val = risk_pred.item()

                    output_mask[z:z+patch_size, y:y+patch_size, x:x+patch_size] += mask_np
                    count_map[z:z+patch_size, y:y+patch_size, x:x+patch_size] += 1
                    risk_scores.append(risk_val)
                    total_patches += 1

    # Average overlapping regions
    count_map[count_map == 0] = 1
    output_mask /= count_map

    # Remove padding
    output_mask = output_mask[:D, :H, :W]

    # Binarize
    binary_mask = (output_mask > threshold).astype(np.uint8)

    avg_risk = float(np.mean(risk_scores)) if risk_scores else 0.0
    print(f"[inference] Processed {total_patches} patches, avg risk: {avg_risk:.4f}")

    return binary_mask, avg_risk


# =============================================================================
# Nodule Extraction
# =============================================================================

def extract_nodules(
    mask: np.ndarray,
    spacing: List[float] = None,
    min_volume_mm3: float = 10.0
) -> List[Dict]:
    """
    Extract individual nodules from binary segmentation mask.

    Uses connected components to identify separate nodules.

    Args:
        mask: Binary 3D mask
        spacing: Voxel spacing [z, y, x] in mm
        min_volume_mm3: Minimum nodule volume to keep

    Returns:
        List of nodule dictionaries
    """
    from scipy import ndimage

    if spacing is None:
        spacing = [1.0, 1.0, 1.0]

    voxel_volume_mm3 = spacing[0] * spacing[1] * spacing[2]

    # Label connected components
    labeled, num_features = ndimage.label(mask)
    print(f"[inference] Found {num_features} connected components")

    nodules = []
    for i in range(1, num_features + 1):
        component = (labeled == i)
        voxel_count = int(np.sum(component))
        volume_mm3 = voxel_count * voxel_volume_mm3

        if volume_mm3 < min_volume_mm3:
            continue

        # Centroid
        coords = np.argwhere(component)
        centroid = coords.mean(axis=0).tolist()

        # Bounding box
        z_coords, y_coords, x_coords = coords[:, 0], coords[:, 1], coords[:, 2]
        bbox = {
            "z": [int(z_coords.min()), int(z_coords.max())],
            "y": [int(y_coords.min()), int(y_coords.max())],
            "x": [int(x_coords.min()), int(x_coords.max())]
        }

        # Long axis (approximate)
        extent_z = (z_coords.max() - z_coords.min()) * spacing[0]
        extent_y = (y_coords.max() - y_coords.min()) * spacing[1]
        extent_x = (x_coords.max() - x_coords.min()) * spacing[2]
        long_axis_mm = float(max(extent_z, extent_y, extent_x))

        nodules.append({
            "id": len(nodules) + 1,
            "centroid": [round(c, 1) for c in centroid],
            "bbox": bbox,
            "volume_mm3": round(volume_mm3, 2),
            "long_axis_mm": round(long_axis_mm, 2),
            "voxel_count": voxel_count,
        })

    # Sort by volume (largest first)
    nodules.sort(key=lambda n: n["volume_mm3"], reverse=True)

    # Re-assign IDs
    for i, n in enumerate(nodules):
        n["id"] = i + 1

    print(f"[inference] Extracted {len(nodules)} nodules (min vol: {min_volume_mm3} mm3)")
    return nodules


# =============================================================================
# Per-Nodule Classification
# =============================================================================

def classify_nodules(
    model,
    volume: np.ndarray,
    nodules: List[Dict],
    device,
    patch_size: int = PATCH_SIZE
) -> List[Dict]:
    """
    Run classification on each extracted nodule.

    Extracts a patch centered on each nodule and runs the classifier head.
    """
    import torch

    for nodule in nodules:
        centroid = nodule["centroid"]
        cz, cy, cx = int(centroid[0]), int(centroid[1]), int(centroid[2])

        half = patch_size // 2
        z_start = max(0, cz - half)
        y_start = max(0, cy - half)
        x_start = max(0, cx - half)

        patch = volume[z_start:z_start+patch_size, y_start:y_start+patch_size, x_start:x_start+patch_size]

        # Pad if needed
        if patch.shape != (patch_size, patch_size, patch_size):
            padded = np.zeros((patch_size, patch_size, patch_size), dtype=np.float32)
            padded[:patch.shape[0], :patch.shape[1], :patch.shape[2]] = patch
            patch = padded

        with torch.no_grad():
            tensor = torch.tensor(patch, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
            _, risk = model(tensor)
            prob = risk.item()

        nodule["prob_malignant"] = round(prob, 4)
        nodule["p_malignant"] = round(prob, 4)

        # Classify risk
        if prob >= 0.7:
            nodule["type"] = "suspicious"
            nodule["location"] = _estimate_lobe(centroid, volume.shape)
        elif prob >= 0.4:
            nodule["type"] = "indeterminate"
            nodule["location"] = _estimate_lobe(centroid, volume.shape)
        else:
            nodule["type"] = "benign"
            nodule["location"] = _estimate_lobe(centroid, volume.shape)

        # Uncertainty estimate (simplified)
        nodule["uncertainty"] = {
            "confidence": round(max(prob, 1 - prob), 4),
            "entropy": round(-prob * np.log(prob + 1e-8) - (1 - prob) * np.log(1 - prob + 1e-8), 4),
            "needs_review": prob >= 0.4
        }

    return nodules


def _estimate_lobe(centroid: List[float], volume_shape: Tuple) -> str:
    """Estimate lung lobe from centroid position."""
    D, H, W = volume_shape
    z, y, x = centroid

    # Simple heuristic based on position
    is_upper = z < D * 0.4
    is_right = x > W * 0.5

    if is_upper and is_right:
        return "RUL"
    elif is_upper and not is_right:
        return "LUL"
    elif not is_upper and is_right:
        return "RLL"
    else:
        return "LLL"


# =============================================================================
# GradCAM XAI Generation
# =============================================================================

def generate_gradcam(
    model,
    volume: np.ndarray,
    nodule: Dict,
    device,
    output_dir: str,
    patch_size: int = PATCH_SIZE
) -> Optional[str]:
    """
    Generate GradCAM heatmap for a nodule.

    Returns path to saved heatmap image, or None if failed.
    """
    import torch
    from scipy import ndimage as ndi

    try:
        centroid = nodule["centroid"]
        cz, cy, cx = int(centroid[0]), int(centroid[1]), int(centroid[2])

        half = patch_size // 2
        z_start = max(0, cz - half)
        y_start = max(0, cy - half)
        x_start = max(0, cx - half)

        patch = volume[z_start:z_start+patch_size, y_start:y_start+patch_size, x_start:x_start+patch_size]

        if patch.shape != (patch_size, patch_size, patch_size):
            padded = np.zeros((patch_size, patch_size, patch_size), dtype=np.float32)
            padded[:patch.shape[0], :patch.shape[1], :patch.shape[2]] = patch
            patch = padded

        img_tensor = torch.tensor(patch, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
        img_tensor.requires_grad = True

        # Hooks
        gradients = [None]
        activations = [None]

        def backward_hook(module, grad_input, grad_output):
            gradients[0] = grad_output[0]

        def forward_hook(module, input, output):
            activations[0] = output

        # Target layer: last ReLU in bottleneck
        target_layer = model.down3[1].conv[5]
        h1 = target_layer.register_forward_hook(forward_hook)
        h2 = target_layer.register_full_backward_hook(backward_hook)

        model.zero_grad()
        _, risk = model(img_tensor)
        risk.backward()

        h1.remove()
        h2.remove()

        # Compute CAM
        weights = torch.mean(gradients[0], dim=(2, 3, 4), keepdim=True)
        cam = torch.sum(weights * activations[0], dim=1, keepdim=True)
        cam = torch.relu(cam)
        cam = cam.squeeze().cpu().detach().numpy()

        # Resize to patch size
        zoom_factors = np.array(patch.shape) / np.array(cam.shape)
        cam_resized = ndi.zoom(cam, zoom_factors, order=1)

        # Normalize
        if cam_resized.max() > 0:
            cam_resized = cam_resized / cam_resized.max()

        # Save as numpy
        os.makedirs(output_dir, exist_ok=True)
        cam_path = os.path.join(output_dir, f"nodule_{nodule['id']}_gradcam.npy")
        np.save(cam_path, cam_resized)

        # Also save a PNG of the middle slice
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            mid = patch.shape[0] // 2
            fig, ax = plt.subplots(1, 1, figsize=(4, 4))
            ax.imshow(patch[mid], cmap='gray')
            ax.imshow(cam_resized[mid], cmap='jet', alpha=0.4)
            ax.set_title(f"Nodule #{nodule['id']} GradCAM")
            ax.axis('off')

            png_path = os.path.join(output_dir, f"nodule_{nodule['id']}_gradcam.png")
            fig.savefig(png_path, bbox_inches='tight', dpi=100)
            plt.close(fig)

            return png_path

        except Exception:
            return cam_path

    except Exception as e:
        print(f"[inference] GradCAM failed for nodule {nodule.get('id')}: {e}")
        return None


# =============================================================================
# Main Analysis Pipeline
# =============================================================================

def analyze_scan(
    case_id: str,
    input_path: str,
    output_dir: str = None,
    is_dicom: bool = False
) -> Dict:
    """
    Full analysis pipeline for a CT scan.

    Args:
        case_id: Unique case identifier
        input_path: Path to .npy/.npz file or DICOM directory
        output_dir: Directory to save outputs (findings.json, XAI images)
        is_dicom: Whether input is a DICOM directory

    Returns:
        Complete findings dictionary
    """
    start_time = time.time()
    print(f"[inference] >>> Starting analysis for case: {case_id}")

    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), "healthatm", case_id)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load model
    model, device = load_model()

    # 2. Load volume
    spacing = [1.0, 1.0, 1.0]
    if is_dicom:
        volume, spacing = load_dicom_volume(input_path)
        print(f"[inference] DICOM loaded: {volume.shape}, spacing: {spacing}")
    else:
        volume = load_npy_volume(input_path)
        print(f"[inference] Volume loaded: {volume.shape}")

    # 3. Normalize
    volume_norm = normalize_hu(volume)

    # 4. Sliding window inference
    mask, avg_risk = sliding_window_inference(model, volume_norm, device)
    print(f"[inference] Segmentation complete. Mask sum: {mask.sum()}")

    # 5. Extract nodules
    nodules = extract_nodules(mask, spacing)

    # 6. Classify each nodule
    if nodules:
        nodules = classify_nodules(model, volume_norm, nodules, device)

    # 7. Generate XAI for high-risk nodules
    xai_dir = os.path.join(output_dir, "xai")
    for nodule in nodules:
        if nodule.get("prob_malignant", 0) >= 0.4:
            cam_path = generate_gradcam(model, volume_norm, nodule, device, xai_dir)
            if cam_path:
                nodule["gradcam_path"] = cam_path
            else:
                nodule["gradcam_path"] = "not_available"
        else:
            nodule["gradcam_path"] = "not_available"

        nodule["saliency_path"] = "not_available"
        nodule["overlay_path"] = "not_available"
        nodule["mask_path"] = "not_available"

    # 8. Save mask
    mask_path = os.path.join(output_dir, f"{case_id}_mask.npy")
    np.save(mask_path, mask)

    # 9. Build findings
    processing_time = round(time.time() - start_time, 2)

    # Determine overall impression
    high_risk = [n for n in nodules if n.get("prob_malignant", 0) >= 0.7]
    moderate_risk = [n for n in nodules if 0.4 <= n.get("prob_malignant", 0) < 0.7]

    if high_risk:
        impression = f"AI detected {len(nodules)} nodule(s), {len(high_risk)} classified as high-risk for malignancy. Clinical correlation and follow-up recommended."
        summary_text = f"The AI scan found {len(nodules)} spot(s) in your lungs. {len(high_risk)} need(s) attention. Please consult your doctor for next steps."
    elif moderate_risk:
        impression = f"AI detected {len(nodules)} nodule(s), {len(moderate_risk)} with moderate risk. Monitoring recommended."
        summary_text = f"The AI scan found {len(nodules)} spot(s). Some may need monitoring. Your doctor will advise on follow-up."
    elif nodules:
        impression = f"AI detected {len(nodules)} nodule(s), all classified as low risk. Routine follow-up suggested."
        summary_text = f"The AI scan found {len(nodules)} small spot(s) that appear low risk. Regular check-ups are recommended."
    else:
        impression = "No significant nodules detected by AI analysis."
        summary_text = "The AI scan did not find any concerning spots in your lungs. Continue with regular health check-ups."

    findings = {
        "study_id": case_id,
        "study_uid": case_id,
        "patient_name": "N/A",
        "patient_age": "N/A",
        "patient_sex": "N/A",
        "scan_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "num_nodules": len(nodules),
        "num_candidates": len(nodules),
        "nodules": nodules,
        "lung_health": "AI-Analyzed",
        "emphysema_score": 0.0,
        "fibrosis_score": 0.0,
        "consolidation_score": 0.0,
        "airway_wall_thickness": "Normal",
        "impression": impression,
        "summary_text": summary_text,
        "processing_time_seconds": processing_time,
        "metadata": {
            "model": "FullUNet3D-v1",
            "model_path": str(MODEL_PATH),
            "spacing": spacing,
            "volume_shape": list(volume.shape),
            "analyzed_at": datetime.utcnow().isoformat() + "Z"
        }
    }

    # 10. Save findings.json
    findings_path = os.path.join(output_dir, f"{case_id}_findings.json")
    with open(findings_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    print(f"[inference] [OK] Analysis complete in {processing_time}s")
    print(f"[inference]    Nodules: {len(nodules)}, High-risk: {len(high_risk)}")
    print(f"[inference]    Findings: {findings_path}")

    return findings


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HealthATM Inference Service - Self Test")
    print("=" * 60)

    # Test with synthetic data
    print("\n1. Loading model...")
    model, device = load_model()
    print(f"   Model loaded on {device}")

    print("\n2. Creating synthetic volume...")
    import torch
    test_vol = np.random.randn(64, 64, 64).astype(np.float32) * 0.1
    # Add a "nodule" blob
    test_vol[25:40, 25:40, 25:40] = 0.8

    print("\n3. Running inference...")
    test_vol_norm = normalize_hu(test_vol * 1400 - 1000)
    mask, risk = sliding_window_inference(model, test_vol_norm, device, stride=32)
    print(f"   Mask shape: {mask.shape}, sum: {mask.sum()}, risk: {risk:.4f}")

    print("\n4. Extracting nodules...")
    nodules = extract_nodules(mask)
    print(f"   Found {len(nodules)} nodules")

    print("\n[OK] Self-test complete!")
