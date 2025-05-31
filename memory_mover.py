# utils/memory_mover.py

import asyncio
import logging
from typing import List, Optional
from fastapi import FastAPI

from utils.memory_mover import get_memory_pipeline

logger = logging.getLogger(__name__)

class MemoryMover:
    def __init__(self, agent_ids: List[str], session_ids: Optional[List[str]] = None, interval_seconds: int = 300):
        self.agent_ids = agent_ids
        self.session_ids = session_ids or [None]
        self.interval_seconds = interval_seconds
        self._running = False
        self._task = None

    async def _summarize_agent_session(self, agent_id: str, session_id: Optional[str]):
        pipeline = get_memory_pipeline(agent_id, session_id=session_id)
        try:
            pipeline.long_term._summarize_batch()
            logger.info(f"Summarized memory batch for agent {agent_id} session {session_id}")
        except Exception as e:
            logger.error(f"Error summarizing memory for agent {agent_id} session {session_id}: {e}")

    async def _run_loop(self):
        self._running = True
        while self._running:
            for agent_id in self.agent_ids:
                for session_id in self.session_ids:
                    await self._summarize_agent_session(agent_id, session_id)
            await asyncio.sleep(self.interval_seconds)

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run_loop())
            logger.info("MemoryMover started")

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
            logger.info("MemoryMover stopped")

# FastAPI integration example
def register_memory_mover(app: FastAPI, agent_ids: List[str], session_ids: Optional[List[str]] = None, interval_seconds: int = 300):
    mover = MemoryMover(agent_ids, session_ids, interval_seconds)

    @app.on_event("startup")
    async def startup_event():
        mover.start()

    @app.on_event("shutdown")
    async def shutdown_event():
        await mover.stop()

    return mover