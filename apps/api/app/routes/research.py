import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.research_run import ResearchRun
from app.repositories.agent_output import AgentOutputRepository
from app.repositories.final_signal import FinalSignalRepository
from app.repositories.research_run import ResearchRunRepository
from app.schemas.agents import AgentOutputResponse
from app.schemas.research import CreateRunRequest, RunResponse
from app.schemas.signals import FinalSignalResponse

router = APIRouter(prefix="/research")


@router.post("/runs", response_model=RunResponse, status_code=201)
async def create_run(
    body: CreateRunRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRunRepository(db)
    run = ResearchRun(
        asset_id=body.asset_id,
        analysis_mode=body.analysis_mode,
        time_horizon=body.time_horizon,
        model_bundle_version=body.model_bundle_version,
        status="pending",
    )
    created = await repo.create(run)
    await db.commit()
    await db.refresh(created)

    # Enqueue to worker pool
    worker = request.app.state.worker_pool
    worker.submit_run(created.id)

    return created


@router.get("/runs", response_model=list[RunResponse])
async def list_runs(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRunRepository(db)
    return await repo.list_runs(limit=limit, offset=offset, status=status)


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ResearchRunRepository(db)
    run = await repo.get_by_id(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs/{run_id}/agents", response_model=list[AgentOutputResponse])
async def get_run_agents(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = AgentOutputRepository(db)
    return await repo.get_by_run_id(run_id)


@router.get("/runs/{run_id}/final-signal", response_model=FinalSignalResponse)
async def get_run_final_signal(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = FinalSignalRepository(db)
    signal = await repo.get_by_run_id(run_id)
    if signal is None:
        raise HTTPException(status_code=404, detail="Final signal not yet available")
    return signal
