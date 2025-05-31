# utils/file_utils.py

from pathlib import Path
from typing import Any
import os
from tools.shared import summarize_text
from datetime import datetime
import json

def read_project_file(agent: Any, path: str) -> str:
    """
    Read the contents of a file at the given path if the agent has permission.
    Returns the file content as a string, or an error message string.
    """
    if not agent.has_permission("read_files"):
        return "Access denied: Agent cannot read files."
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def save_modified_file(agent: Any, original_path: str, content: str) -> str:
    """
    Save the modified content to a file in the agent_outputs directory,
    maintaining the relative path from 'anchorwork'. Returns the path to the saved file as a string,
    or an error message string.
    """
    if not agent.has_permission("write_to_agent_outputs"):
        return "Access denied: Agent cannot write output."

    try:
        rel_path = Path(original_path).relative_to("anchorwork")
    except Exception as e:
        return f"Error: The file path '{original_path}' is not under the 'anchorwork' directory. Details: {e}"
    base = Path("agent_outputs") / rel_path
    try:
        base.parent.mkdir(parents=True, exist_ok=True)
        with open(base, "w", encoding="utf-8") as f:
            f.write(content)
        return str(base)
    except Exception as e:
        return f"Error writing file: {e}"

def write_agent_summary(agent_id: str, events: list) -> str:
    """
    Summarizes recent events for an agent and writes the summary to /data/memory/{agent_id}/ as a JSON file.
    Returns the path to the written summary file.
    """
    # Concatenate events into a single text block
    text = "\n".join(str(e) for e in events)
    summary = summarize_text(text, agent_id=agent_id)
    # Prepare output directory and filename
    out_dir = Path("/data/memory") / agent_id
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"summary_{timestamp}.json"
    # Write summary as JSON
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "agent_id": agent_id,
            "timestamp": timestamp,
            "summary": summary,
            "events": events
        }, f, ensure_ascii=False, indent=2)
    return str(out_file)

def check_agent_summary_threshold(agent_id: str, threshold: int = 10, notify_callback=None) -> bool:
    """
    Checks if the number of summary files for the agent in /data/memory/{agent_id}/ exceeds the threshold.
    If so, calls notify_callback(agent_id, count) if provided.
    Returns True if threshold is reached/exceeded, else False.
    """
    summary_dir = Path("/data/memory") / agent_id
    if not summary_dir.exists():
        return False
    summary_files = list(summary_dir.glob("summary_*.json"))
    count = len(summary_files)
    if count >= threshold:
        if notify_callback:
            notify_callback(agent_id, count)
        return True
    return False
