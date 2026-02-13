import numpy as np
from scipy.ndimage import gaussian_laplace, maximum_filter

def log_nodule_candidates(volume, lung_mask, sigma=1.0, threshold=0.001):
    """
    Detects spherical nodule candidates using 3D LoG filter + NMS.
    volume     - normalized CT volume (float32)
    lung_mask  - binary mask of lungs (0/1)
    """
    # Apply LoG inside lung only
    masked = volume * (lung_mask > 0)

    # 3D Laplacian of Gaussian
    log_response = -gaussian_laplace(masked, sigma=sigma)

    # Normalize
    log_response = (log_response - log_response.min()) / (log_response.max() - log_response.min() + 1e-5)

    # Threshold to keep only high responses
    candidates = (log_response > threshold)

    # Non-Maximum Suppression
    local_max = maximum_filter(log_response, size=5) == log_response
    peaks = np.where(candidates & local_max)

    # Return as list of (z,y,x)
    cand_list = list(zip(peaks[0], peaks[1], peaks[2]))
    return cand_list, log_response
