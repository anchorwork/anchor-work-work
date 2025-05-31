import os
import json
from utils.redis_streams import RedisStreamsManager
from datetime import datetime

# --- Redis Streams Logger ---
_redis_manager = None

def get_redis_manager():
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisStreamsManager()
    return _redis_manager

def log_event_redis(event_type, payload, agent=None, session_id=None, level="INFO"):
    """
    Log event to Redis Streams for real-time event streaming.
    """
    manager = get_redis_manager()
    timestamp = datetime.utcnow().isoformat() + "Z"
    event_data = {
        "timestamp": timestamp,
        "agent_id": agent,
        "session_id": session_id,
        "event_type": event_type,
        "level": level,
        "message": payload.get("message", "") if isinstance(payload, dict) else str(payload),
        "metadata": json.dumps(payload if isinstance(payload, dict) else {"data": payload})
    }
    # Use system_logs for general events, agent_events for agent-specific
    if agent:
        manager.publish_agent_event(agent, event_type, event_data)
    else:
        manager.publish_system_log(level, event_data["message"], event_data)
