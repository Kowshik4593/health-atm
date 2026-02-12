from pydantic import BaseModel
from datetime import datetime

class DoctorAssignment(BaseModel):
    id: str
    case_id: str
    doctor_id: str
    accepted_at: datetime
    status: str
