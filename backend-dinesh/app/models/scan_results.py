from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class ScanResults(BaseModel):
    id: str
    case_id: str
    findings_json: Any
    num_nodules: Optional[int]
    high_risk_count: Optional[int]
    impression: Optional[str]
    summary_text: Optional[str]
    generated_at: datetime
