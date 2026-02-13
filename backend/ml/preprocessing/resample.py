import SimpleITK as sitk
import numpy as np

def resample_to_iso(volume, spacing, new_spacing=[1.0,1.0,1.0]):
    img = sitk.GetImageFromArray(volume)
    img.SetSpacing(spacing[::-1])  # simpleitk uses (x,y,z)

    original_size = img.GetSize()
    original_spacing = img.GetSpacing()

    new_size = [
        int(round(original_size[0] * original_spacing[0] / new_spacing[2])),
        int(round(original_size[1] * original_spacing[1] / new_spacing[1])),
        int(round(original_size[2] * original_spacing[2] / new_spacing[0])),
    ]

    resampler = sitk.ResampleImageFilter()
    resampler.SetOutputSpacing(new_spacing[::-1])
    resampler.SetSize(new_size[::-1])
    resampler.SetInterpolator(sitk.sitkLinear)

    new_img = resampler.Execute(img)
    new_vol = sitk.GetArrayFromImage(new_img)

    return new_vol, new_spacing
