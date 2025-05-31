import logging
import logging.handlers
import json

logger = logging.getLogger("anchorwork")
handler = logging.handlers.RotatingFileHandler(
    "anchorwork.log", maxBytes=10*1024*1024, backupCount=5
)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_event_file(event_type, payload, agent=None, session_id=None, level="INFO"):
    log_entry = {
        "event_type": event_type,
        "agent": agent,
        "session_id": session_id,
        "level": level,
        **payload
    }
    logger.info(json.dumps(log_entry))