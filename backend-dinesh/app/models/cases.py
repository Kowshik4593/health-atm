from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Case(BaseModel):
    id: str
    patient_id: str
    ct_scan_path: str
    upload_time: datetime
    status: str
    assigned_doctor: Optional[str]
    assigned_at: Optional[datetime]
    json_path: Optional[str]
    clinician_pdf: Optional[str]
    patient_pdf: Optional[str]
    processing_time_seconds: Optional[float]
class CaseCreate(BaseModel):
    patient_id: str
    ct_scan_path: str
