"""
Unified logging entrypoint for Anchorwork.
Routes events to file, Redis, and memory pipeline loggers as configured.
Usage:
    from agentlogging.unified_logger import log_event
    log_event("event_type", payload, agent="agent_id", session_id="session", level="INFO")
"""
import os
from agentlogging.file_logger import log_event_file
from agentlogging.redis_logger import log_event_redis
from agentlogging.memory_logger import log_event_memory

LOG_TO_FILE = os.getenv("LOG_TO_FILE", "1") == "1"
LOG_TO_REDIS = os.getenv("LOG_TO_REDIS", "1") == "1"
LOG_TO_MEMORY = os.getenv("LOG_TO_MEMORY", "1") == "1"


def log_event(event_type, payload, agent=None, session_id=None, level="INFO"):
    """
    Unified logging function for Anchorwork.
    Routes to file, Redis, and memory pipeline loggers as configured.
    """
    if LOG_TO_FILE:
        log_event_file(event_type, payload, agent, session_id, level)
    if LOG_TO_REDIS:
        log_event_redis(event_type, payload, agent, session_id, level)
    if LOG_TO_MEMORY:
        log_event_memory(event_type, payload, agent, session_id, level)
