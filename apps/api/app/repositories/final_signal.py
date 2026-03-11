import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.final_signal import FinalSignal


class FinalSignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, signal: FinalSignal) -> FinalSignal:
        self.session.add(signal)
        await self.session.flush()
        return signal

    async def get_by_run_id(self, run_id: uuid.UUID) -> FinalSignal | None:
        stmt = select(FinalSignal).where(FinalSignal.run_id == run_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_signals(
        self, limit: int = 50, offset: int = 0, release_status: str | None = None
    ) -> list[FinalSignal]:
        stmt = select(FinalSignal).order_by(FinalSignal.created_at.desc())
        if release_status:
            stmt = stmt.where(FinalSignal.release_status == release_status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
