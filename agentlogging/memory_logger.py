from utils.memory_pipeline import get_memory_pipeline
from .config import IMPORTANT_EVENTS

def log_event_memory(event_type, payload, agent=None, session_id=None, level="INFO"):
    memory_pipeline = get_memory_pipeline()
    memory_moment = {
        "event_type": event_type,
        "payload": payload,
        "agent": agent,
        "session_id": session_id,
        "level": level
    }
    # Only add to working memory if event is important or flagged
    if event_type in IMPORTANT_EVENTS or level in ("ERROR", "CRITICAL"):
        memory_pipeline.append(memory_moment)