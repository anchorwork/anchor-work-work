"""
agents/base_agent.py

Anchorwork BaseAgent:
- Unified boot-up: identity, dynamic notes, education, memory moments.
- Dynamic education ingestion (on boot, scheduled, or on demand).
- Agent-to-agent teaching (recommendations).
- Self-reflection (on boot, after session, or on demand).
- Logging integration for all key events.
- API-ready for /whoami and /self_reflect.
"""

import asyncio
import json
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime

from utils import toolkit
from utils.memory_pipeline import get_memory_pipeline
from utils.vector_memory import PineconeMemory
from agentlogging.unified_logger import log_event
from tools import shared
from utils.system_runner import SystemRunner

class BaseAgent:
    def __init__(self, agent_id: str, memory_dir: str = "memory", education_refresh_hours: int = 24):
        self.agent_id = agent_id
        self.memory_dir = Path(memory_dir)
        self.identity_path = self.memory_dir / f"{agent_id}_identity.md"
        self.identity_text = ""
        self.dynamic_notes: List[str] = []
        self.education_docs: List[str] = []
        self.memory_moments: List[str] = []
        self.identity_context: str = ""
        self._mood: str = "neutral"
        self._energy: float = 0.5
        self._confidence: float = 0.5
        self._stress: float = 0.0
        self._focus: float = 0.5
        self._creative_momentum: float = 0.5
        self._goals: List[str] = []
        self._learning_insights: List[str] = []
        self._interaction_depth: int = 0
        self._last_active: Optional[datetime] = None
        self._autonomy_level: float = 0.5
        self._error_count: int = 0
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._register_default_tools()
        self._event_listeners: Dict[str, List[Callable[..., Any]]] = {}
        self._autonomy_enabled: bool = True
        self._moderation_callback: Optional[Callable[[str, Dict[str, Any]], Union[bool, asyncio.Future]]] = None
        self.system_runner = SystemRunner()  # Safe system command runner for all agents
        self._load_dynamic_state()
        self.boot_up()
        self.periodic_education_ingestion(interval_hours=education_refresh_hours)

    # --- Unified Boot-Up ---
    def boot_up(self):
        """Unified agent boot-up: builds self-awareness and learning context."""
        self.identity_text = self._load_static_identity()
        self.dynamic_notes = shared.get_dynamic_identity_notes(self.agent_id)
        self.education_docs = shared.load_education_from_pinecone(self.agent_id)
        self.memory_moments = self._load_memory_moments()
        self.identity_context = self._build_identity_context()
        self._log_identity_summary()
        log_event(
            "boot_up",
            {"timestamp": shared.current_timestamp()},
            agent=self.agent_id,
            level="INFO"
        )

    def _load_static_identity(self) -> str:
        if self.identity_path.exists():
            return self.identity_path.read_text(encoding="utf-8")
        try:
            profile = shared.load_agent_profile(self.agent_id)
            return profile.get("identity", "")
        except Exception:
            return ""

    def _load_education_from_pinecone(self) -> List[str]:
        return shared.load_education_from_pinecone(self.agent_id)

    def _load_memory_moments(self, num: int = 5) -> List[str]:
        try:
            pipeline = get_memory_pipeline(agent_id=self.agent_id)
            moments = pipeline.working.retrieve()[-num:]
            return [f"{m.timestamp}: {m.prompt} → {m.response}" for m in moments]
        except Exception:
            return []

    def _build_identity_context(self) -> str:
        context = [
            "## Core Identity\n" + (self.identity_text or "[No identity found]"),
            "## Recent Notes\n" + ("\n".join(self.dynamic_notes) if self.dynamic_notes else "[No recent notes]"),
            "## Recent Education\n" + ("\n".join(self.education_docs) if self.education_docs else "[No education docs found]"),
            "## Recent Memory Moments\n" + ("\n".join(self.memory_moments) if self.memory_moments else "[No memory moments found]")
        ]
        return "\n\n".join(context)

    def _log_identity_summary(self):
        print(f"[{self.agent_id}] Booted up with identity:\n{self.identity_context}")

    # --- Dynamic Education Ingestion ---
    def periodic_education_ingestion(self, interval_hours: int = 24):
        """Background thread to periodically ingest new education docs."""
        def run():
            while True:
                self.education_docs = shared.load_education_from_pinecone(self.agent_id)
                log_event(
                    "education_ingestion",
                    {"timestamp": shared.current_timestamp()},
                    agent=self.agent_id,
                    level="INFO"
                )
                time.sleep(interval_hours * 3600)
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def refresh_education(self):
        """On-demand education ingestion (e.g., after session or on API call)."""
        self.education_docs = shared.load_education_from_pinecone(self.agent_id)
        log_event(
            "education_refresh",
            {"timestamp": shared.current_timestamp()},
            agent=self.agent_id,
            level="INFO"
        )

    # --- Agent-to-Agent Teaching ---
    def append_education(self, title: str, content: str, tags: Optional[List[str]] = None):
        """Append a new lesson, insight, or case study to the agent's education in Pinecone."""
        return shared.append_education(self.agent_id, title, content, tags)

    def recommend_to_agent(self, recipient_agent_id: str, title: str, content: str, tags: Optional[List[str]] = None):
        """Recommend a doc/tool to another agent by appending to their education in Pinecone."""
        return shared.recommend_to_agent(self.agent_id, recipient_agent_id, title, content, tags)

    # --- Self-Reflection & Growth ---
    def self_reflect(self) -> Dict[str, str]:
        """Reflect on recent learning and suggest next steps for growth."""
        return shared.self_reflect(self.agent_id, self.identity_context)

    # --- Dynamic Identity Notes ---
    def append_dynamic_identity_note(self, note: str):
        shared.append_dynamic_identity_note(self.agent_id, note)

    def get_dynamic_identity_notes(self) -> List[str]:
        return shared.get_dynamic_identity_notes(self.agent_id)

    def get_identity_context(self) -> str:
        return self.identity_context

    def _current_timestamp(self) -> str:
        return shared.current_timestamp()

    # --- Cognitive State Properties (unchanged) ---
    # ... (properties for mood, energy, etc. as in previous versions) ...
    # (Omitted here for brevity, but include all from previous full version.)

    # --- Persistence methods, Tool Registration, Event System, Autonomy, Growth, Introspection ---
    # ... (all unchanged from previous full version) ...