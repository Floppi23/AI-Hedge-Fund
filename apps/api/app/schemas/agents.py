import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentOutputResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    agent_name: str
    prompt_version: str | None = None
    model_version: str | None = None
    stance: str | None = None
    score: float | None = None
    confidence: float | None = None
    is_valid: bool
    validation_errors: dict[str, Any] | None = None
    output_json: dict[str, Any]
    created_at: datetime
