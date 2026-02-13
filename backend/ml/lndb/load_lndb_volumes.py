import os
from pathlib import Path

def build_volume_index(lndb_root):
    """
    Searches data0/..data5 folders and maps LNDb-xxxx → full .mhd path
    """
    lndb_root = Path(lndb_root)
    volume_index = {}

    for i in range(6):   # data0 → data5
        data_dir = lndb_root / f"data{i}"
        if not data_dir.exists():
            continue

        for f in os.listdir(data_dir):
            if f.endswith(".mhd"):
                vol_id = f.replace(".mhd", "")   # LNDb-0001
                volume_index[vol_id] = str(data_dir / f)

    return volume_index
