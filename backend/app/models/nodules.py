from pydantic import BaseModel
from typing import Any

class Nodule(BaseModel):
    id: int
    case_id: str
    nodule_index: int
    type: str
    location: str
    prob_malignant: float
    needs_review: bool
    long_axis_mm: float
    volume_mm3: float
    centroid: Any
    bbox: Any
    mask_path: str
