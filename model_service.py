# utils/model_service.py
"""
Unified Model Management Service for Anchorwork

Combines configuration, routing, state management, and interactive switching
into a single, well-organized service while maintaining clear separation of concerns.
"""

import os
import re
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from agentlogging.unified_logger import log_event

# ================================================================
# CONFIGURATION & REGISTRY
# ================================================================

MODEL_REGISTRY = {
    "gpt-4o-mini": {
        "context": 32_000,
        "speed": "💨",
        "cost": "low",
        "notes": "routing / meta",
    },
    "gpt-4o-2024-11-20": {
        "context": 128_000,
        "speed": "fast",
        "cost": "med",
        "notes": "balanced default",
    },
    "gpt-4.1-long": {
        "context": 200_000,
        "speed": "slow",
        "cost": "high",
        "notes": "huge ctx",
    },
    "gpt-4.1-2025-04-14": {
        "context": 128_000,
        "speed": "fast",
        "cost": "med",
        "notes": "latest stable",
    },
    "gpt-4.1-mini-2025-04-14": {
        "context": 64_000,
        "speed": "💨",
        "cost": "low",
        "notes": "mini latest",
    },
    "o4-mini-2025-04-16": {
        "context": 128_000,
        "speed": "med",
        "cost": "med",
        "notes": "reasoning",
    },
    "o3-mini-2025-01-31": {
        "context": 64_000,
        "speed": "fast",
        "cost": "low",
        "notes": "lightweight generation",
    },
}

def _ensure_model_registered(mid: str):
    """Ensure that a model ID exists in the MODEL_REGISTRY."""
    if mid not in MODEL_REGISTRY:
        MODEL_REGISTRY[mid] = {
            "context": 0, "speed": "?", "cost": "?", "notes": "from .env"
        }

# Load main and agent-specific models from environment variables
MODEL_MAIN = os.getenv("MODEL_MAIN", "gpt-4o-2024-11-20")
MODEL_CODER = os.getenv("MODEL_CODER", MODEL_MAIN)
MODEL_FIRST_MATE = os.getenv("MODEL_FIRST_MATE", MODEL_MAIN)
MODEL_CARTOGRAPHER = os.getenv("MODEL_CARTOGRAPHER", "gpt-4.1-long")
MODEL_ALCHEMIST = os.getenv("MODEL_ALCHEMIST", MODEL_MAIN)
MODEL_COMPASS = os.getenv("MODEL_COMPASS", MODEL_MAIN)
MODEL_WATCHER = os.getenv("MODEL_WATCHER", MODEL_MAIN)
MODEL_RESEARCHER = os.getenv("MODEL_RESEARCHER", MODEL_MAIN)

# Specialized task models
MODEL_IMAGE = os.getenv("MODEL_IMAGE", "dall-e-3")
MODEL_AUDIO = os.getenv("MODEL_AUDIO", "whisper-1")
MODEL_SEARCH = os.getenv("MODEL_SEARCH", "bing-chat")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-large")

# Ensure all models are registered
for _mid in (
    MODEL_MAIN, MODEL_CODER, MODEL_FIRST_MATE, MODEL_CARTOGRAPHER,
    MODEL_ALCHEMIST, MODEL_COMPASS, MODEL_WATCHER, MODEL_RESEARCHER,
    MODEL_IMAGE, MODEL_AUDIO, MODEL_SEARCH, EMBED_MODEL,
):
    _ensure_model_registered(_mid)

# ================================================================
# ROUTING CONFIGURATION
# ================================================================

IMAGE_KEYWORDS = ["draw", "generate an image", "visual", "scene"]
AUDIO_KEYWORDS = ["transcribe", "audio", "recording", "voice note"]
SEARCH_KEYWORDS = ["search", "look up", "find on the web"]
CODER_KEYWORDS = ["debug", "fix", "code", "script", "function"]

AGENT_MODEL_MAP = {
    "first mate": MODEL_FIRST_MATE,
    "cartographer": MODEL_CARTOGRAPHER,
    "alchemist": MODEL_ALCHEMIST,
    "compass": MODEL_COMPASS,
    "watcher": MODEL_WATCHER,
    "researcher": MODEL_RESEARCHER,
}

AVAILABLE_MODELS = [
    "gpt-4.1-2025-04-14",
    "gpt-4.1-mini-2025-04-14",
    "gpt-4.1-mini (long context)",
    "o4-mini-2025-04-16",
    "o3-mini-2025-01-31",
    "gpt-4o"
]

# Explicit task-to-model mapping for cost efficiency
TASK_MODEL_MAP = {
    "info_gathering": "gpt-4.1-mini-2025-04-14",
    "summarization": "gpt-4.1-mini-2025-04-14",
    "embedding": EMBED_MODEL,
    "vector": "gpt-4.1-mini-2025-04-14",
    "web_search": "gpt-4.1-mini-2025-04-14",
    "final_answer": MODEL_MAIN,  # Use main model for user-facing answers
    "chat": MODEL_MAIN,
    "code_reasoning": "o4-mini-2025-04-16",
    "docs": "o3-mini-2025-01-31",
    "tests": "o3-mini-2025-01-31",
    "checklist": "o3-mini-2025-01-31",
}

# ================================================================
# STATE MANAGEMENT
# ================================================================

@dataclass
class ModelState:
    """Model state management with memory and locking."""
    current: str = field(default_factory=lambda: MODEL_MAIN)
    locked: bool = False
    last_used: float = field(default_factory=time.time)
    history: List[str] = field(default_factory=list)

    def update(self, model: str):
        """Update current model and timestamp."""
        self.current = model
        self.last_used = time.time()
        if not self.history or self.history[-1] != model:
            self.history.append(model)
            # Keep history manageable
            if len(self.history) > 10:
                self.history = self.history[-10:]

    def lock(self, model: str):
        """Lock to a specific model."""
        self.current = model
        self.locked = True
        self.update(model)

    def unlock(self):
        """Unlock model selection."""
        self.locked = False
        self.last_used = time.time()

    def reset_if_idle(self, idle_minutes: int = 15):
        """Reset to main model if idle."""
        if not self.locked and (time.time() - self.last_used) > idle_minutes * 60:
            self.current = MODEL_MAIN

# ================================================================
# UNIFIED MODEL SERVICE
# ================================================================

class ModelService:
    """
    Unified model management service that combines configuration,
    routing, state management, and interactive switching.
    """
    
    def __init__(self):
        self.state = ModelState()
        self.confirm_switches = True

    # Configuration methods
    def describe_model(self, mid: str) -> str:
        """Return a short description string for the given model ID."""
        if mid in MODEL_REGISTRY:
            return f"{mid} · {MODEL_REGISTRY[mid]['notes']}"
        return f"{mid} · unknown model"

    def get_default_model(self, agent_id: str = "main") -> str:
        """Retrieve the default model ID for a given agent ID."""
        return {
            "main": MODEL_MAIN,
            "coder": MODEL_CODER,
            "first_mate": MODEL_FIRST_MATE,
            "cartographer": MODEL_CARTOGRAPHER,
            "alchemist": MODEL_ALCHEMIST,
            "compass": MODEL_COMPASS,
            "watcher": MODEL_WATCHER,
            "researcher": MODEL_RESEARCHER,
            "image": MODEL_IMAGE,
            "audio": MODEL_AUDIO,
            "search": MODEL_SEARCH,
            "embed": EMBED_MODEL,
        }.get(agent_id.lower(), MODEL_MAIN)

    def list_available_models(self) -> List[str]:
        """Get list of available models."""
        return AVAILABLE_MODELS.copy()

    # Routing methods
    def choose_model_by_task(self, task_type: str, token_estimate: int = 0, max_cost: str = "med") -> str:
        """Smart model chooser based on task type, token size, and cost policy."""
        # Prefer explicit mapping for efficiency
        if task_type in TASK_MODEL_MAP:
            model = TASK_MODEL_MAP[task_type]
            # Optionally check cost if needed
            if max_cost == "low" and MODEL_REGISTRY[model]["cost"] != "low":
                # Fallback to lowest cost model
                for m, meta in MODEL_REGISTRY.items():
                    if meta["cost"] == "low":
                        model = m
                        break
            log_event("model_routing", {"task_type": task_type, "chosen_model": model, "max_cost": max_cost}, level="INFO")
            return model
        # Fallback to legacy logic
        if task_type == "chat":
            return MODEL_MAIN
        if task_type == "scan" or token_estimate > 3000:
            return "gpt-4.1-mini-2025-04-14"
        if task_type in {"fix_plan", "code_reasoning"}:
            return "o4-mini-2025-04-16"
        if task_type in {"docs", "tests", "checklist"}:
            return "o3-mini-2025-01-31"
        return MODEL_MAIN

    def choose_model_by_prompt(self, prompt: str, max_cost: str = "med") -> str:
        """
        Choose the appropriate model based on the content of the prompt and cost policy.
        """
        prompt_lower = prompt.lower()
        if self.state.locked:
            return self.state.current
        for agent_phrase, agent_model in AGENT_MODEL_MAP.items():
            if agent_phrase in prompt_lower:
                self.state.update(agent_model)
                log_event("model_switch", {"reason": "agent_keyword", "to": agent_model}, level="INFO")
                return agent_model
        switch_prefix = "switch to "
        if switch_prefix in prompt_lower:
            idx = prompt_lower.find(switch_prefix)
            after_switch = prompt_lower[idx + len(switch_prefix):].strip()
            model_candidate = after_switch.split()[0] if after_switch else ""
            if model_candidate in MODEL_REGISTRY:
                self.state.update(model_candidate)
                log_event("model_switch", {"reason": "manual_switch", "to": model_candidate}, level="INFO")
                return model_candidate
        # Task-specific keywords
        for task, model in TASK_MODEL_MAP.items():
            if task in prompt_lower:
                if max_cost == "low" and MODEL_REGISTRY[model]["cost"] != "low":
                    for m, meta in MODEL_REGISTRY.items():
                        if meta["cost"] == "low":
                            model = m
                            break
                self.state.update(model)
                log_event("model_switch", {"reason": "task_keyword", "to": model}, level="INFO")
                return model
        # Fallback to main
        self.state.update(MODEL_MAIN)
        log_event("model_switch", {"reason": "default", "to": MODEL_MAIN}, level="INFO")
        return MODEL_MAIN

    # Interactive switching methods
    def override_model(self, model_name: str) -> str:
        """Override the current model with the specified model name."""
        if model_name in MODEL_REGISTRY:
            self.state.update(model_name)
            return f"🔁 Model switched to: {model_name}"
        return f"❌ Unknown model: {model_name}"

    def recommend_model(self, based_on: str = "long") -> str:
        """Recommend a model based on a given criterion."""
        current = self.state.current
        preferred = {
            "long": "gpt-4.1-long" if "4.1" in current else "gpt-4o-long",
            "mini": "gpt-4.1-mini-2025-04-14" if "4.1" in current else "gpt-4o-mini-2024-07-18",
            "realtime": "gpt-4o-mini-realtime-preview-2024-12-17"
        }.get(based_on, current)
        return f"⚠️ Based on '{based_on}', I suggest using `{preferred}`."

    def handle_model_prompt(self, prompt: str) -> Optional[str]:
        """Handle a prompt that may contain commands to switch or describe models."""
        lowered = prompt.lower()
        
        if "switch to" in lowered:
            match = re.search(r"switch to ([\w\-\.]+)", prompt)
            if match:
                return self.override_model(match.group(1))
        
        if "use long" in lowered:
            long_model = "gpt-4.1-long" if "4.1" in self.state.current else "gpt-4o-long"
            return self.override_model(long_model)
        
        if "use mini" in lowered:
            mini_model = "gpt-4.1-mini-2025-04-14" if "4.1" in self.state.current else "gpt-4o-mini-2024-07-18"
            return self.override_model(mini_model)
        
        if "use realtime" in lowered:
            return self.override_model("gpt-4o-mini-realtime-preview-2024-12-17")
        
        if "describe model" in lowered:
            return self.describe_model(self.state.current)
        
        return None

    # State management methods
    def lock_model(self, model_name: str) -> str:
        """Lock the model selection to a specific model."""
        if model_name in MODEL_REGISTRY:
            self.state.lock(model_name)
            return f"🔒 Model locked to: {model_name}"
        return f"❌ Unknown model: {model_name}"

    def unlock_model(self) -> str:
        """Unlock the model selection."""
        self.state.unlock()
        return "🔓 Model selection unlocked"

    def get_current_model(self) -> str:
        """Get the current model."""
        return self.state.current

    def get_model_state(self) -> Dict:
        """Get current model state information."""
        return {
            "current": self.state.current,
            "locked": self.state.locked,
            "last_used": self.state.last_used,
            "history": self.state.history.copy(),
            "description": self.describe_model(self.state.current)
        }

    def reset_if_idle(self, idle_minutes: int = 15):
        """Reset to main model if idle."""
        self.state.reset_if_idle(idle_minutes)

# ================================================================
# MIXIN CLASS FOR AGENTS
# ================================================================

class ModelSwitchingMixin:
    """
    Mixin class to add model switching capabilities to agents.
    Now uses the unified ModelService.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_service = ModelService()
        self.model = self.model_service.get_current_model()

    def override_model(self, model_name: str) -> str:
        """Override the current model with the specified model name."""
        result = self.model_service.override_model(model_name)
        self.model = self.model_service.get_current_model()
        return result

    def recommend_model(self, based_on: str = "long") -> str:
        """Recommend a model based on a given criterion."""
        return self.model_service.recommend_model(based_on)

    def handle_model_prompt(self, prompt: str) -> Optional[str]:
        """Handle a prompt that may contain commands to switch or describe models."""
        result = self.model_service.handle_model_prompt(prompt)
        if result:
            self.model = self.model_service.get_current_model()
        return result

# ================================================================
# GLOBAL SERVICE INSTANCE & CONVENIENCE FUNCTIONS
# ================================================================

# Global service instance for backward compatibility
_model_service = ModelService()

# Convenience functions that maintain the original API
def choose_model(prompt: str) -> str:
    """Choose model based on prompt content."""
    return _model_service.choose_model_by_prompt(prompt)

def get_default_model(agent_id: str = "main") -> str:
    """Get default model for agent."""
    return _model_service.get_default_model(agent_id)

def describe_model(mid: str) -> str:
    """Describe a model."""
    return _model_service.describe_model(mid)

def lock_model(model_name: str) -> str:
    """Lock to a specific model."""
    return _model_service.lock_model(model_name)

def unlock_model() -> str:
    """Unlock model selection."""
    return _model_service.unlock_model()

def get_model_state() -> Dict:
    """Get current model state."""
    return _model_service.get_model_state()

# Export the service for direct use
model_service = _model_service
