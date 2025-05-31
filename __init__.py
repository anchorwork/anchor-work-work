from agentlogging.file_logger import log_event_file
from agentlogging.db_logger import log_event_db
from agentlogging.redis_logger import log_event_redis
from agentlogging.memory_logger import log_event_memory
from agentlogging.metrics import log_metrics, get_system_health
from agentlogging.config import IMPORTANT_EVENTS


def log_event(event_type, payload, agent=None, session_id=None, memory=False, level="INFO"):
    """
    Unified logging interface for Anchorwork.
    Logs to file, Redis Streams, PostgreSQL DB, and (optionally) memory pipeline.
    """
    log_event_file(event_type, payload, agent, session_id, level)
    log_event_redis(event_type, payload, agent, session_id, level)
    log_event_db(event_type, payload, agent, session_id, level)
    if memory or event_type in IMPORTANT_EVENTS:
        log_event_memory(event_type, payload, agent, session_id, level)
    log_metrics(event_type, agent, session_id, level)