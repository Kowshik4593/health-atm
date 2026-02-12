import SimpleITK as sitk
from lungmask import mask

def segment_lungs(volume):
    # Convert numpy array → SITK image
    img = sitk.GetImageFromArray(volume)

    # This is the correct API for older lungmask versions
    mask_array = mask.apply(img)     # <-- THIS WORKS FOR YOUR VERSION

    return mask_array
