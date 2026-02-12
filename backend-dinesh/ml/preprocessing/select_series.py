import os

def find_main_ct_series(patient_folder):
    """
    Returns the path to the main CT series folder for a LIDC-IDRI patient.
    We pick the folder with the highest number of DICOM slices (usually > 50).
    """
    best_folder = None
    best_count = 0

    for root, dirs, files in os.walk(patient_folder):
        # Count how many files look like DICOM slices
        dcm_files = [f for f in files if f.lower().endswith(".dcm")]

        if len(dcm_files) > best_count:
            best_count = len(dcm_files)
            best_folder = root

    return best_folder, best_count
