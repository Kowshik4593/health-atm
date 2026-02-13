import numpy as np

def extract_patch(volume, center, size=32):
    z,y,x = center
    half = size//2

    z1, z2 = max(0,z-half), min(volume.shape[0], z+half)
    y1, y2 = max(0,y-half), min(volume.shape[1], y+half)
    x1, x2 = max(0,x-half), min(volume.shape[2], x+half)

    patch = volume[z1:z2, y1:y2, x1:x2]
    return patch
