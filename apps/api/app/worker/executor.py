"""Background worker pool for processing research runs."""

import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from app.config import Settings
from app.worker.run_pipeline import execute_run_pipeline

logger = logging.getLogger(__name__)


class WorkerPool:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._executor = ThreadPoolExecutor(
            max_workers=settings.worker_pool_size,
            thread_name_prefix="run-worker",
        )

    def submit_run(self, run_id: uuid.UUID) -> None:
        """Submit a research run for background processing."""
        logger.info(f"Submitting run {run_id} to worker pool")
        self._executor.submit(self._run_in_thread, run_id)

    def _run_in_thread(self, run_id: uuid.UUID) -> None:
        """Sync wrapper that creates an event loop for the async pipeline."""
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(execute_run_pipeline(run_id, self.settings))
        except Exception as e:
            logger.error(f"Worker thread for run {run_id} failed: {e}")
        finally:
            loop.close()

    def shutdown(self) -> None:
        """Graceful shutdown of the worker pool."""
        logger.info("Shutting down worker pool...")
        self._executor.shutdown(wait=True)
        logger.info("Worker pool shut down")
