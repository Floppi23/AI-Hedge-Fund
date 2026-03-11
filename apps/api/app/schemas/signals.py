import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FinalSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    final_stance: str
    final_score: float
    final_confidence: float
    risk_override: bool
    release_status: str
    summary: str | None = None
    contributing_agents: list[str] | None = None
    blocked_reasons: list[str] | None = None
    created_at: datetime
