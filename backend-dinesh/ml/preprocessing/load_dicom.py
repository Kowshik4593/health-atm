import SimpleITK as sitk
import numpy as np
import os

def load_dicom_series(dicom_folder):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()

    volume = sitk.GetArrayFromImage(image).astype(np.int16)  # (Z,Y,X)
    spacing = list(image.GetSpacing())[::-1]  # (Z,Y,X)

    return volume, spacing
