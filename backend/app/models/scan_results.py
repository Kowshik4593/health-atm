from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class ScanResults(BaseModel):
    id: str
    case_id: str
    findings_json: Any
    num_nodules: Optional[int] = None
    high_risk_count: Optional[int] = None
    impression: Optional[str] = None
    summary_text: Optional[str] = None
    generated_at: datetime
