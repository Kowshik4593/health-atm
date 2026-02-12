def classify_lobe(center, vol_shape):
    z, y, x = center
    Z, Y, X = vol_shape

    # left vs right
    mid_x = X // 2
    side = "left" if x >= mid_x else "right"

    # vertical thirds
    if z < Z * 0.33:
        level = "upper"
    elif z < Z * 0.66:
        level = "middle"
    else:
        level = "lower"

    # correct anatomy
    if side == "left":
        if level == "middle":
            return "left lingula"
        return f"left {level} lobe"
    else:
        return f"right {level} lobe"
def classify_lobe(center_vox, volume_shape):
    z, y, x = center_vox
    Z, Y, X = volume_shape

    # left vs right
    side = "left" if x > X//2 else "right"

    # upper / middle / lower
    if z < Z * 0.33:
        lobe = "upper"
    elif z < Z * 0.66:
        lobe = "middle"
    else:
        lobe = "lower"

    return f"{side} {lobe} lobe"
