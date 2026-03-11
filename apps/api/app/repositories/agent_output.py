import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_output import AgentOutput


class AgentOutputRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, output: AgentOutput) -> AgentOutput:
        self.session.add(output)
        await self.session.flush()
        return output

    async def get_by_run_id(self, run_id: uuid.UUID) -> list[AgentOutput]:
        stmt = (
            select(AgentOutput)
            .where(AgentOutput.run_id == run_id)
            .order_by(AgentOutput.agent_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
