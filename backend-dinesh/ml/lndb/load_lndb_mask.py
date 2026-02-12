import SimpleITK as sitk
from pathlib import Path

def load_mask(mask_path):
    img = sitk.ReadImage(str(mask_path))
    arr = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()  # (x,y,z)
    return arr, spacing[::-1]    # convert to (z,y,x)
