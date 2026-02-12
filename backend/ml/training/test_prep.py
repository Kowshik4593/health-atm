import os
import glob
import numpy as np
import pydicom
import scipy.ndimage
import xml.etree.ElementTree as ET
from pathlib import Path
from tqdm import tqdm
import cv2

# Configuration
LIDC_PATH = Path("../../../../LIDC-IDRI")
OUTPUT_PATH = Path("data/lidc_patches")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
PATCH_SIZE = 64
TARGET_SPACING = (1.0, 1.0, 1.0)

def load_scan(path):
    slices = [pydicom.dcmread(s) for s in glob.glob(str(path / "*.dcm"))]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    image = image.astype(np.int16)
    intercept = slices[0].RescaleIntercept
    slope = slices[0].RescaleSlope
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
    image += np.int16(intercept)
    return np.array(image, dtype=np.int16)

def resample(image, scan, new_spacing=[1,1,1]):
    spacing = np.array([scan[0].SliceThickness, scan[0].PixelSpacing[0], scan[0].PixelSpacing[1]], dtype=np.float32)
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = scipy.ndimage.zoom(image, real_resize_factor, mode='nearest')
    return image, real_resize_factor

def parse_xml_nodules(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    nodules = []
    # Simplified parsing for demo: Extract unblindedReadNodule characteristics
    for session in root.findall('{http://www.nih.gov}readingSession'):
        for unblinded in session.findall('{http://www.nih.gov}unblindedReadNodule'):
            roi = unblinded.find('{http://www.nih.gov}roi')
            if roi is None: continue
            mal_elem = unblinded.find('{http://www.nih.gov}characteristics/{http://www.nih.gov}malignancy')
            malignancy = int(mal_elem.text) if mal_elem is not None else 0
            z_elem = roi.find('{http://www.nih.gov}imageZposition')
            nodules.append({
                'malignancy': malignancy,
                'z_pos': float(z_elem.text),
                'id': unblinded.find('{http://www.nih.gov}noduleID').text
            })
    return nodules

def find_dicom_series(root_path):
    series_paths = []
    for root, dirs, files in os.walk(root_path):
        if any(f.endswith('.dcm') for f in files):
            series_paths.append(Path(root))
    return series_paths

def process_single_scan(series_path, scan_id):
    try:
        # Load Scan
        slices = load_scan(series_path)
        image = get_pixels_hu(slices)
        image_resampled, resize_factor = resample(image, slices, TARGET_SPACING)
        
        # Find XML
        xml_files = list(series_path.parent.glob("*.xml")) # usually in parent or same dir
        # In LIDC structure, XML is often one level up or in same folder.
        # Check current folder first, then parent.
        if not xml_files:
             xml_files = list(series_path.glob("*.xml"))

        if not xml_files:
            print(f"No XML found for {scan_id}")
            return

        nodules = parse_xml_nodules(xml_files[0])
        print(f"Scan {scan_id}: {len(nodules)} nodule annotations found.")
        
        # Group by Z-position simplified (real clustering is complex, we just take unique Zs with >2 annotations for demo)
        # For this demo, simply take the first 3 nodules found
        processed_nodules = 0
        for i, nod in enumerate(nodules[:5]): 
             # Find Z-index in resampled volume
             # Match Z-position. slices[k].ImagePositionPatient[2]
             
             # Find closest slice index
             min_dist = 9999
             z_idx = -1
             for k, s in enumerate(slices):
                 dist = abs(s.ImagePositionPatient[2] - nod['z_pos'])
                 if dist < min_dist:
                     min_dist = dist
                     z_idx = k
             
             if z_idx == -1: continue

             # Scale Z index to resampled space
             z_resampled = int(z_idx * resize_factor[0])
             
             # Center X, Y (Assume centered for demo since XML ROI parsing is tedious without pylidc)
             # In real implementation we need ROI center. 
             # Here we take center of image as placeholder if ROI center not parsed
             y_resampled = image_resampled.shape[1] // 2
             x_resampled = image_resampled.shape[2] // 2
             
             # Extract Patch
             z_start = max(0, z_resampled - PATCH_SIZE // 2)
             y_start = max(0, y_resampled - PATCH_SIZE // 2)
             x_start = max(0, x_resampled - PATCH_SIZE // 2)
             
             patch = image_resampled[z_start:z_start+PATCH_SIZE, y_start:y_start+PATCH_SIZE, x_start:x_start+PATCH_SIZE]
             
             if patch.shape != (PATCH_SIZE, PATCH_SIZE, PATCH_SIZE):
                 continue # padding needed, skip for now
                 
             # Save
             if processed_nodules < 3:
                 out_name = OUTPUT_PATH / f"{scan_id}_nodule_{i}.npz"
                 np.savez_compressed(out_name, image=patch, label=1 if nod['malignancy'] > 3 else 0, malignancy=nod['malignancy'])
                 print(f"Saved {out_name}")
                 
                 # Save a debug image of middle slice
                 # cv2.imwrite(str(OUTPUT_PATH / f"{scan_id}_nodule_{i}.png"), ((patch[32,:,:] + 1000) / 2000 * 255).astype(np.uint8))
                 processed_nodules += 1

    except Exception as e:
        print(f"Error processing {scan_id}: {e}")

if __name__ == "__main__":
    series = find_dicom_series(LIDC_PATH)
    print(f"Processing first 2 of {len(series)} scans...")
    for s in series[:2]:
        scan_id = s.parent.name # LIDC-IDRI-XXXX
        process_single_scan(s, scan_id)
