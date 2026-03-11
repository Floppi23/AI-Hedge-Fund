import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research_run import ResearchRun


class ResearchRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, run: ResearchRun) -> ResearchRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_by_id(self, run_id: uuid.UUID) -> ResearchRun | None:
        return await self.session.get(ResearchRun, run_id)

    async def list_runs(
        self, limit: int = 50, offset: int = 0, status: str | None = None
    ) -> list[ResearchRun]:
        stmt = select(ResearchRun).order_by(ResearchRun.created_at.desc())
        if status:
            stmt = stmt.where(ResearchRun.status == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        run_id: uuid.UUID,
        status: str,
        error_message: str | None = None,
    ) -> None:
        run = await self.get_by_id(run_id)
        if run is None:
            return
        run.status = status
        if error_message:
            run.error_message = error_message
        if status == "running":
            run.started_at = datetime.now(timezone.utc)
        if status in ("completed", "blocked", "failed"):
            run.finished_at = datetime.now(timezone.utc)
        await self.session.flush()
