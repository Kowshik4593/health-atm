from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Case(BaseModel):
    id: str
    patient_id: str
    ct_scan_path: str
    upload_time: datetime
    status: str
    assigned_doctor: Optional[str] = None
    assigned_at: Optional[datetime] = None
    json_path: Optional[str] = None
    clinician_pdf: Optional[str] = None
    patient_pdf: Optional[str] = None
    processing_time_seconds: Optional[float] = None

class CaseCreate(BaseModel):
    patient_id: str
    ct_scan_path: str
