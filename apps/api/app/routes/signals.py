from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.repositories.final_signal import FinalSignalRepository
from app.schemas.signals import FinalSignalResponse

router = APIRouter(prefix="/signals")


@router.get("", response_model=list[FinalSignalResponse])
async def list_signals(
    limit: int = 50,
    offset: int = 0,
    release_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    repo = FinalSignalRepository(db)
    return await repo.list_signals(limit=limit, offset=offset, release_status=release_status)
