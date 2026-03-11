import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.eval_case import EvalCase
from app.models.eval_result import EvalResult


class EvalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_cases(self, agent_name: str | None = None) -> list[EvalCase]:
        stmt = select(EvalCase)
        if agent_name:
            stmt = stmt.where(EvalCase.agent_name == agent_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_result(self, result: EvalResult) -> EvalResult:
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_results_for_case(self, case_id: uuid.UUID) -> list[EvalResult]:
        stmt = (
            select(EvalResult)
            .where(EvalResult.eval_case_id == case_id)
            .order_by(EvalResult.run_timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
