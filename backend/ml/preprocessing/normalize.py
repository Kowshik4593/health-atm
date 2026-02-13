import numpy as np

def clip_and_normalize(vol):
    vol = np.clip(vol, -1000, 400)
    vol = (vol + 1000) / 1400
    return vol.astype("float32")
