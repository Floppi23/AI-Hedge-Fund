from fastapi import APIRouter

router = APIRouter(prefix="/evals")


@router.post("/run")
async def run_evals():
    """Stub: run evaluation suite. Full implementation in Phase 7."""
    return {
        "status": "stub",
        "message": "Eval system not yet implemented",
        "total_cases": 0,
        "passed": 0,
        "failed": 0,
    }
