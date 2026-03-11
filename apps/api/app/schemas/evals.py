import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class EvalCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_name: str
    ticker: str
    input_data: dict[str, Any]
    expected_stance: str | None = None
    expected_score_min: float | None = None
    expected_score_max: float | None = None
    description: str | None = None
    created_at: datetime


class EvalResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    eval_case_id: uuid.UUID
    actual_stance: str | None = None
    actual_score: float | None = None
    passed: bool
    failure_reason: str | None = None
    model_version: str | None = None
    run_timestamp: datetime


class EvalRunSummary(BaseModel):
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    results: list[EvalResultResponse]
