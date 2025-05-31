# watcher_tools.py
"""
Watcher agent tools for system and memory health monitoring.
Implements periodic checks for memory summary thresholds and background job heartbeats.
"""
from pathlib import Path
from datetime import datetime, timedelta
from utils.file_utils import check_agent_summary_threshold
from agentlogging.unified_logger import log_event
import asyncio

# Example notification tool (replace with actual Watcher notification logic)
def risk_signal(message: str):
    log_event("watcher_risk_signal", {"message": message}, agent="watcher", level="WARNING")
    print(f"[Watcher Risk Signal] {message}")

def monitor_memory_and_jobs(agent_id: str, summary_threshold: int = 10, heartbeat_path: str = None, heartbeat_interval_sec: int = 600):
    """
    Checks agent memory summary threshold and background job heartbeat.
    Notifies if threshold is exceeded or heartbeat is missing/stale.
    """
    # Check summary threshold
    def notify(agent_id, count):
        risk_signal(f"Agent {agent_id} has {count} summaries in /data/memory/{agent_id}/ (threshold: {summary_threshold})")
    check_agent_summary_threshold(agent_id, threshold=summary_threshold, notify_callback=notify)

    # Check background job heartbeat
    if heartbeat_path:
        heartbeat_file = Path(heartbeat_path)
        if heartbeat_file.exists():
            try:
                last_beat = datetime.fromisoformat(heartbeat_file.read_text().strip())
                if (datetime.utcnow() - last_beat) > timedelta(seconds=heartbeat_interval_sec * 2):
                    risk_signal(f"Memory maintenance worker heartbeat is stale (last: {last_beat.isoformat()})")
            except Exception as e:
                risk_signal(f"Error reading heartbeat: {e}")
        else:
            risk_signal("No heartbeat detected from memory maintenance worker.")

def start_periodic_monitoring(agent_id: str, summary_threshold: int = 10, heartbeat_path: str = None, heartbeat_interval_sec: int = 600, interval_minutes: int = 10):
    """
    Starts a background task that runs monitor_memory_and_jobs every interval_minutes.
    """
    async def periodic_task():
        while True:
            monitor_memory_and_jobs(agent_id, summary_threshold, heartbeat_path, heartbeat_interval_sec)
            await asyncio.sleep(interval_minutes * 60)
    asyncio.create_task(periodic_task())
