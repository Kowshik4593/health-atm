# fyp.py
import os
import glob
import json
import nibabel as nib
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
import numpy as np
import torch.nn.functional as F

try:
    from ml.report_utils import add_report_fields
except ImportError:
    # Fallback if report_utils not available
    def add_report_fields(findings, volume):
        findings['lung_health'] = "Assessment not available"
        findings['airway_wall_thickness'] = "normal"
        findings['emphysema_score'] = 0.0
        findings['fibrosis_score'] = 0.0
        findings['consolidation_score'] = 0.0
        findings['impression'] = "Automated analysis completed."
        findings['summary_text'] = "Please consult with your physician for interpretation."
        for nodule in findings.get('nodules', []):
            nodule['type'] = 'solid'
            nodule['location'] = 'unspecified'
        return findings


class LunaDataset(Dataset):
    def __init__(self, folder, patch_size=(64,64,64)):
        self.files = glob.glob(f"{folder}/*.nii.gz")
        self.patch_size = patch_size

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        vol = nib.load(self.files[idx]).get_fdata()
        D,H,W = vol.shape
        dz, dy, dx = self.patch_size
        startz = np.random.randint(0, max(D-dz,1))
        starth = np.random.randint(0, max(H-dy,1))
        startw = np.random.randint(0, max(W-dx,1))
        patch = vol[startz:startz+dz, starth:starth+dy, startw:startw+dx]
        patch = torch.tensor(patch, dtype=torch.float32).unsqueeze(0)  # channel dim
        target = torch.zeros_like(patch)  # placeholder segmentation
        return patch, target


class UNet3D(nn.Module):
    def __init__(self, in_channels=1, out_channels=1, base_features=16):
        super(UNet3D, self).__init__()
        # Encoder
        self.enc1 = nn.Sequential(
            nn.Conv3d(in_channels, base_features, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv3d(base_features, base_features, 3, padding=1),
            nn.ReLU(inplace=True)
        )
        self.pool1 = nn.MaxPool3d(2)

        self.enc2 = nn.Sequential(
            nn.Conv3d(base_features, base_features*2, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv3d(base_features*2, base_features*2, 3, padding=1),
            nn.ReLU(inplace=True)
        )
        self.pool2 = nn.MaxPool3d(2)

        self.enc3 = nn.Sequential(
            nn.Conv3d(base_features*2, base_features*4, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv3d(base_features*4, base_features*4, 3, padding=1),
            nn.ReLU(inplace=True)
        )

        # Decoder
        self.up2 = nn.ConvTranspose3d(base_features*4, base_features*2, 2, stride=2)
        self.dec2 = nn.Sequential(
            nn.Conv3d(base_features*4, base_features*2, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv3d(base_features*2, base_features*2, 3, padding=1),
            nn.ReLU(inplace=True)
        )

        self.up1 = nn.ConvTranspose3d(base_features*2, base_features, 2, stride=2)
        self.dec1 = nn.Sequential(
            nn.Conv3d(base_features*2, base_features, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv3d(base_features, base_features, 3, padding=1),
            nn.ReLU(inplace=True)
        )

        self.out = nn.Conv3d(base_features, out_channels, 1)

    def forward(self, x):
        # Encoder
        x1 = self.enc1(x)
        x2 = self.enc2(self.pool1(x1))
        x3 = self.enc3(self.pool2(x2))

        # Decoder with safe skip connections
        x = self.up2(x3)
        if x.shape[2:] != x2.shape[2:]:
            x = F.interpolate(x, size=x2.shape[2:], mode='trilinear', align_corners=False)
        x = self.dec2(torch.cat([x, x2], dim=1))

        x = self.up1(x)
        if x.shape[2:] != x1.shape[2:]:
            x = F.interpolate(x, size=x1.shape[2:], mode='trilinear', align_corners=False)
        x = self.dec1(torch.cat([x, x1], dim=1))

        x = self.out(x)
        return x


def train_model(processed_folder, epochs=2, patch_size=(64,64,64)):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = LunaDataset(processed_folder, patch_size)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

    model = UNet3D().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    scaler = GradScaler()

    for epoch in range(epochs):
        loop = tqdm(dataloader, desc=f"Training Epoch {epoch+1}")
        for x, y in loop:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            with autocast():
                out = model(x)
                loss = criterion(out, y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            loop.set_postfix(loss=loss.item())
            torch.cuda.empty_cache()
    return model


def infer_single_scan(model, scan_path, output_folder):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    os.makedirs(output_folder, exist_ok=True)

    vol = nib.load(scan_path).get_fdata()
    spacing_mm = [1.0, 0.7, 0.7]  # example spacing
    input_tensor = torch.tensor(vol, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)

    with torch.no_grad():
        with autocast():
            pred = model(input_tensor)

    # Convert prediction to float32 for nibabel
    pred_vol = pred.squeeze().cpu().numpy().astype(np.float32)

    # Postprocessing
    centroid = np.array(np.unravel_index(np.argmax(pred_vol), pred_vol.shape))
    slices = [centroid[0]-1, centroid[0], centroid[0]+1]  # example slices
    risk_score = float(np.max(pred_vol))
    detection_score = 0.91  # dummy detection score

    # Save mask
    mask_path = os.path.join(output_folder, "nodule_0_mask.nii.gz")
    nib.save(nib.Nifti1Image(pred_vol, affine=np.eye(4)), mask_path)

    # Grad-CAM / saliency placeholder
    saliency_path = os.path.join(output_folder, "nodule_0_saliency.png")
    np.save(saliency_path, np.zeros_like(pred_vol))  # placeholder

    centroid_list=[int(c) for c in centroid]
    slices_list=[int(s) for s in slices]

    findings = {
        'study_id': 'luna_inference',
        'metadata': {
            'volume_shape': list(vol.shape),
            'spacing': spacing_mm
        },
        'num_candidates': 1,
        'num_nodules': 1,
        'nodules': [{
            "id": 0,
            "centroid": centroid_list,
            "coordinates": centroid_list,
            "prob_malignant": float(risk_score),
            "volume_mm3": float(np.sum(pred_vol > 0.5)),
            "mask_path": mask_path,
            "slices": slices_list,
            "saliency_path": saliency_path
        }]
    }

    # Add report fields (lung health, impression, summary, nodule types/locations)
    findings = add_report_fields(findings, vol)

    # Save JSON
    json_path = os.path.join(output_folder, "findings.json")
    with open(json_path, "w") as f:
        json.dump(findings, f, indent=4)

    return findings


if __name__ == "__main__":
    processed_folder = "LUNA16_preprocessed"  # path to preprocessed NIfTI
    output_folder = "output_results"
    
    print("=" * 60)
    print("LUNG NODULE DETECTION - FYP PIPELINE")
    print("=" * 60)
    
    # Check if trained model exists
    model_path = "models/unet3d_trained.pth"
    os.makedirs("models", exist_ok=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = UNet3D()
    model.to(device)
    
    if os.path.exists(model_path):
        print(f"\nLoading trained model from {model_path}...")
        model.load_state_dict(torch.load(model_path, map_location=device))
    else:
        print("\nStep 1: Training model on LUNA16 dataset...")
        print(f"Found {len(os.listdir(processed_folder))} scans")
        model = train_model(processed_folder, epochs=2, patch_size=(64,64,64))
        
        # Save trained model
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path}")
    
    print("\nStep 2: Running inference on sample scan...")
    scan_path = os.path.join(processed_folder, os.listdir(processed_folder)[0])
    findings = infer_single_scan(model, scan_path, output_folder)
    
    print("\n" + "=" * 60)
    print("Pipeline complete! Results saved to:", output_folder)
    print("=" * 60)
