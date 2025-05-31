from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from utils.memory_pipeline import get_memory_pipeline
from tools.shared import append_identity
from utils.living_memory import MemoryMoment

router = APIRouter(prefix="/memory", tags=["memory"])

# In-memory session store for demo purposes; replace with persistent store as needed
_sessions: Dict[str, List[str]] = {}

class MemoryAppendRequest(BaseModel):
    prompt: str
    response: str
    model_used: Optional[str] = None
    context_tags: Optional[List[str]] = []

class MemoryQueryResponse(BaseModel):
    prompt: Optional[str]
    response: Optional[str]
    timestamp: Optional[datetime]
    model_used: Optional[str]
    context_tags: Optional[List[str]]
    metadata: Optional[dict]

class IdentityNoteRequest(BaseModel):
    agent_id: str
    note: str

class SessionRequest(BaseModel):
    session_id: str
    agent_id: str

@router.post("/append", summary="Append a new memory moment to the pipeline")
async def append_memory(req: MemoryAppendRequest, agent_id: str = Body(...), session_id: Optional[str] = Body(None)):
    moment = MemoryMoment(
        timestamp=datetime.utcnow(),
        prompt=req.prompt,
        response=req.response,
        mood="",
        energy=0.5,
        context_tags=req.context_tags or [],
        model_used=req.model_used or "",
        interaction_depth=1,
        emotional_resonance=0.5
    )
    pipeline = get_memory_pipeline(agent_id, session_id=session_id)
    await pipeline.append_async(moment)
    return {"ok": True}

@router.get("/query", summary="Query memory context semantically")
async def query_memory(q: str, agent_id: str, session_id: Optional[str] = None, k: int = 5):
    pipeline = get_memory_pipeline(agent_id, session_id=session_id)
    raw = await pipeline.retrieve_context_async(query=q, k=k)
    results = []
    for item in raw:
        if isinstance(item, MemoryMoment):
            results.append(item.__dict__)
        else:
            results.append(item)
    return {"results": results}

@router.post("/identity/note", summary="Append a note to an agent's identity profile")
async def add_identity_note(req: IdentityNoteRequest):
    append_identity(req.agent_id, req.note)
    return {"ok": True}

@router.post("/session/create", summary="Create a new session")
async def create_session(req: SessionRequest):
    if req.session_id in _sessions:
        raise HTTPException(status_code=400, detail="Session already exists")
    _sessions[req.session_id] = [req.agent_id]
    return {"ok": True, "session_id": req.session_id}

@router.post("/session/join", summary="Join an existing session")
async def join_session(req: SessionRequest):
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.agent_id not in _sessions[req.session_id]:
        _sessions[req.session_id].append(req.agent_id)
    return {"ok": True, "session_id": req.session_id}

@router.post("/session/leave", summary="Leave a session")
async def leave_session(req: SessionRequest):
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.agent_id in _sessions[req.session_id]:
        _sessions[req.session_id].remove(req.agent_id)
    return {"ok": True, "session_id": req.session_id}

@router.get("/broadcast_summaries", summary="Get broadcast summaries for all agents")
async def get_broadcast_summaries(agent_id: str):
    pipeline = get_memory_pipeline(agent_id)
    summaries = pipeline.get_broadcast_summaries()
    return {"summaries": summaries}