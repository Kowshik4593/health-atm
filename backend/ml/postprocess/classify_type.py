def classify_nodule_type(hu_mean):
    if hu_mean > -300:
        return "solid"
    elif -700 < hu_mean <= -300:
        return "subsolid"
    else:
        return "ground-glass"
def classify_nodule_type(hu_mean):
    if hu_mean > -300:
        return "solid"
    elif hu_mean > -700:
        return "subsolid"
    else:
        return "ground-glass"
