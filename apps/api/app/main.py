import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_settings
from app.routes.evals import router as evals_router
from app.routes.health import router as health_router
from app.routes.research import router as research_router
from app.routes.signals import router as signals_router
from app.worker.executor import WorkerPool

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables exist (SQLite dev — idempotent)
    from app.db.init_db import create_tables
    await create_tables()

    # Startup: initialize worker pool
    settings = get_settings()
    app.state.worker_pool = WorkerPool(settings)
    logging.info("Worker pool started")
    yield
    # Shutdown: clean up worker pool
    app.state.worker_pool.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Alpha Copilot API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all routes under /api
    app.include_router(health_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    app.include_router(signals_router, prefix="/api")
    app.include_router(evals_router, prefix="/api")

    return app


app = create_app()
