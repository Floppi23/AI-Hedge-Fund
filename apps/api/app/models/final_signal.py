import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID, PortableJSON


def _utcnow():
    return datetime.now(timezone.utc)


class FinalSignal(Base):
    __tablename__ = "final_signals"
    __table_args__ = (UniqueConstraint("run_id", name="uq_final_signals_run_id"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False
    )
    final_stance: Mapped[str] = mapped_column(String(20), nullable=False)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    final_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_override: Mapped[bool] = mapped_column(default=False)
    release_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    contributing_agents: Mapped[list | None] = mapped_column(PortableJSON, nullable=True)
    blocked_reasons: Mapped[list | None] = mapped_column(PortableJSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    run: Mapped["ResearchRun"] = relationship(back_populates="final_signal")  # noqa: F821
