# config/coder_config.py
"""
Configuration management for the coder agent.
Centralizes paths, models, and other configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# ────────────────────────────────────────────────
# Directory Structure Management
# ────────────────────────────────────────────────

def get_coder_directories() -> Dict[str, Path]:
    """
    Get standardized coder directory paths.
    Ensures directories exist and handles legacy/new structure.
    
    Returns:
        Dictionary with keys: base_dir, root_coder, nested_coder, coder_dir, src_dir, refs_dir
    """
    # Determine base directory (where coder.py lives)
    base_dir = Path(__file__).parent.parent / "agents"  # …/agents
    
    # Define possible coder locations
    root_coder = base_dir.parent / "coder"          # …/coder  (sibling to agents)
    nested_coder = base_dir / "coder"               # …/agents/coder  (legacy)
    
    # Prefer root‑level /coder if it exists, else use nested path
    coder_dir = root_coder if root_coder.exists() else nested_coder
    
    # Define subdirectories
    src_dir = coder_dir / "src"
    refs_dir = coder_dir / "references"
    
    # Create folders if they were moved or deleted
    for directory in (coder_dir, src_dir, refs_dir):
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        'base_dir': base_dir,
        'root_coder': root_coder,
        'nested_coder': nested_coder,
        'coder_dir': coder_dir,
        'src_dir': src_dir,
        'refs_dir': refs_dir
    }

# ────────────────────────────────────────────────
# Model Configuration
# ────────────────────────────────────────────────

class CoderModelConfig:
    """Manages model selection and configuration for the coder agent."""
    
    def __init__(self):
        # Default models from environment or fallbacks
        self.default_model = os.environ.get("MODEL_CODER", "gpt-4o")
        self.creative_model = os.environ.get("MODEL_CODER_CREATIVE", "gpt-4o")
        self.light_model = os.environ.get("MODEL_CODER_LIGHT", "gpt-4o-mini")
        self.stable_model = os.environ.get("MODEL_CODER_STABLE", "gpt-4o")
        
        # Context limits
        self.max_context = 128000  # Context window for gpt-4o
        self.hard_cap = int(self.max_context * 0.90)   # 90% refuse/ask
        self.warn_cap = int(self.max_context * 0.75)   # 75% log warning
        
        # Model selection thresholds
        self.creative_threshold = 0.7  # creative_momentum > this = creative model
        self.low_energy_threshold = 0.3  # energy < this = light model
    
    def select_model_for_task(self, task_type: str = "general") -> str:
        """
        Select appropriate model based on task type.
        
        Args:
            task_type: Type of task (general, creative, analysis, light)
            
        Returns:
            Model name string
        """
        task_model_map = {
            'creative': self.creative_model,
            'analysis': self.stable_model,
            'light': self.light_model,
            'general': self.default_model
        }
        
        return task_model_map.get(task_type, self.default_model)
    
    def get_model_for_living_state(self, creative_momentum: float, energy_level: float) -> str:
        """
        Select model based on living memory state.
        
        Args:
            creative_momentum: Current creative momentum (0-1)
            energy_level: Current energy level (0-1)
            
        Returns:
            Appropriate model name
        """
        if creative_momentum > self.creative_threshold:
            return self.creative_model
        elif energy_level < self.low_energy_threshold:
            return self.light_model
        else:
            return self.stable_model

# ────────────────────────────────────────────────
# Phase Configuration
# ────────────────────────────────────────────────

class CoderPhaseConfig:
    """Configuration for coder phases and steps."""
    
    # Phase step definitions
    TOTAL_STEPS_P1 = 6  # docs, routes, static, tests, report, audit
    STEP_LONG_THRESHOLD = 30  # seconds before a step logs a slow-warning
    
    # Static analysis targets
    STATIC_ANALYSIS_TARGETS = ["src", "routes"]
    
    # Test configuration
    TEST_COMMAND = ["python", "-m", "pytest", "-q"]
    
    # Education topics for knowledge enhancement
    EDUCATION_TOPICS = [
        "secure Python practices",
        "modular architecture", 
        "error‑handling in APIs",
        "refactoring techniques"
    ]

# ────────────────────────────────────────────────
# System Access Configuration
# ────────────────────────────────────────────────

class CoderSecurityConfig:
    """Security and system access configuration."""
    
    # Default safe commands (allow-list)
    SAFE_COMMANDS = {
        "ls", "pwd", "whoami", "python", "pip", "poetry", 
        "git", "echo", "cat", "grep", "find", "wc", "head", "tail"
    }
    
    # Command timeout (seconds)
    COMMAND_TIMEOUT = 60
    
    # Maximum log file size (bytes)
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# ────────────────────────────────────────────────
# Global Configuration Instance
# ────────────────────────────────────────────────

class CoderConfig:
    """Main configuration class combining all coder settings."""
    
    def __init__(self):
        self.directories = get_coder_directories()
        self.models = CoderModelConfig()
        self.phases = CoderPhaseConfig()
        self.security = CoderSecurityConfig()
        
        # Agent profile defaults
        self.default_profile = {
            "full_system_access": False,
            "mood": "optimistic",
            "status": "Healthy"
        }
    
    def get_directory(self, name: str) -> Path:
        """Get a directory path by name."""
        return self.directories[name]
    
    def get_model(self, model_type: str = "default") -> str:
        """Get a model by type."""
        if model_type == "creative":
            return self.models.creative_model
        elif model_type == "light":
            return self.models.light_model
        elif model_type == "stable":
            return self.models.stable_model
        else:
            return self.models.default_model

# Global configuration instance
_global_config: Optional[CoderConfig] = None

def get_coder_config() -> CoderConfig:
    """Get or create the global coder configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = CoderConfig()
    return _global_config

# Convenience functions for backward compatibility
def get_coder_dir() -> Path:
    """Get the main coder directory path."""
    return get_coder_config().get_directory('coder_dir')

def get_refs_dir() -> Path:
    """Get the references directory path."""
    return get_coder_config().get_directory('refs_dir')

def get_src_dir() -> Path:
    """Get the source directory path."""
    return get_coder_config().get_directory('src_dir')
