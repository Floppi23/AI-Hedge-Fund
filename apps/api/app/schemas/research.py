import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateRunRequest(BaseModel):
    asset_id: str = Field(pattern=r"^[A-Z]{1,10}$", description="Ticker symbol, e.g. AAPL")
    analysis_mode: str = "full"
    time_horizon: str = "medium_term"
    model_bundle_version: str | None = None


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID | None = None
    asset_id: str
    status: str
    analysis_mode: str
    time_horizon: str
    model_bundle_version: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
