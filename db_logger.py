import logging
import logging.handlers
import json
import os
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

# --- Logging Configuration ---
logger = logging.getLogger("anchorwork")
handler = logging.handlers.RotatingFileHandler(
    "anchorwork.log", maxBytes=10*1024*1024, backupCount=5
)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- PostgreSQL Logger Setup ---
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = int(os.getenv("PGPORT", 5432))
DB_NAME = os.getenv("PGDATABASE", "anchorwork")
DB_USER = os.getenv("PGUSER", "anchoruser")
DB_PASSWORD = os.getenv("PGPASSWORD")  # No default! Must be set in environment

if not DB_PASSWORD:
    raise RuntimeError("PGPASSWORD environment variable must be set for database access. Remove hardcoded default passwords.")

def get_db_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def ensure_log_table():
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                agent_id TEXT,
                session_id TEXT,
                event_type TEXT NOT NULL,
                level TEXT DEFAULT 'INFO',
                message TEXT,
                metadata JSONB
            );
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
            CREATE INDEX IF NOT EXISTS idx_logs_agent ON logs(agent_id);
            CREATE INDEX IF NOT EXISTS idx_logs_event_type ON logs(event_type);
            """)
            conn.commit()

ensure_log_table()

def log_event_file(event_type, payload, agent=None, session_id=None, level="INFO"):
    """
    Log event to file.
    """
    log_entry = {
        "event_type": event_type,
        "agent": agent,
        "session_id": session_id,
        "level": level,
        **payload
    }
    logger.info(json.dumps(log_entry))

def log_event_db(event_type, payload, agent=None, session_id=None, level="INFO"):
    """
    Log event to PostgreSQL database.
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO logs (timestamp, agent_id, session_id, event_type, level, message, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    datetime.utcnow(),
                    agent,
                    session_id,
                    event_type,
                    level,
                    payload.get("message", "") if isinstance(payload, dict) else str(payload),
                    Json(payload if isinstance(payload, dict) else {"data": payload})
                )
            )
            conn.commit()