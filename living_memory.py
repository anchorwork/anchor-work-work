# utils/living_memory.py
"""
Enhanced "Living" Memory System for Anchorwork Agents

This module creates a more dynamic, contextual memory system that makes agents feel
more alive and soulful through real-time memory integration, mood tracking,
contextual awareness, and broadcast summaries for agent awareness.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from utils.memory_pipeline import get_memory_pipeline


@dataclass
class MemoryMoment:
    """A single moment in an agent's memory with rich context."""
    timestamp: datetime
    prompt: str
    response: str
    mood: str
    energy: float  # 0.0 to 1.0
    context_tags: List[str]
    model_used: str
    interaction_depth: int  # How deep into a conversation thread
    emotional_resonance: float  # How emotionally significant this was


@dataclass
class LivingState:
    """Dynamic, living state that evolves with interactions."""
    current_mood: str = "optimistic"
    energy_level: float = 0.8
    recent_focus: List[str] = field(default_factory=list)
    conversation_thread: List[str] = field(default_factory=list)
    learning_insights: List[str] = field(default_factory=list)
    creative_momentum: float = 0.5
    last_creative_spark: Optional[datetime] = None
    active_goals: List[str] = field(default_factory=list)


class LivingMemory:
    """
    Enhanced memory system that creates a more "living" agent experience
    through dynamic memory retrieval, mood evolution, contextual awareness,
    and broadcast summaries.
    """

    def __init__(self, agent_id: str, memory_dir: str = "memory", session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.session_id = session_id
        self.memory_dir = Path(memory_dir)
        self.state_path = self.memory_dir / f"{agent_id}_living_state.json"

        # Living state management
        self.state = self._load_living_state()
        self.recent_moments: List[MemoryMoment] = []
        self.contextual_memories: Dict[str, List[MemoryMoment]] = {}

        # Memory personality traits
        self.memory_traits = {
            "creativity_weight": 0.7,
            "emotional_retention": 0.8,
            "technical_precision": 0.9,
            "conversational_flow": 0.6,
        }

        self._load_recent_moments()

        # Get memory pipeline for session-aware short-term memory
        self.pipeline = get_memory_pipeline(agent_id, session_id=session_id)

    def _load_living_state(self) -> LivingState:
        """Load the agent's living state from disk."""
        if not self.state_path.exists():
            return LivingState()

        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                state = LivingState()
                state.current_mood = data.get('current_mood', 'optimistic')
                state.energy_level = data.get('energy_level', 0.8)
                state.recent_focus = data.get('recent_focus', [])
                state.conversation_thread = data.get('conversation_thread', [])
                state.learning_insights = data.get('learning_insights', [])
                state.creative_momentum = data.get('creative_momentum', 0.5)

                spark_str = data.get('last_creative_spark')
                if spark_str:
                    state.last_creative_spark = datetime.fromisoformat(spark_str)

                state.active_goals = data.get('active_goals', [])
                return state
        except Exception:
            return LivingState()

    def _save_living_state(self):
        """Persist the agent's living state to disk."""
        data = {
            'current_mood': self.state.current_mood,
            'energy_level': self.state.energy_level,
            'recent_focus': self.state.recent_focus,
            'conversation_thread': self.state.conversation_thread,
            'learning_insights': self.state.learning_insights,
            'creative_momentum': self.state.creative_momentum,
            'last_creative_spark': self.state.last_creative_spark.isoformat() if self.state.last_creative_spark else None,
            'active_goals': self.state.active_goals,
        }

        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_recent_moments(self):
        """Load recent memory moments for contextual awareness."""
        # Recent moments are managed by the pipeline's STM; initialize empty here.
        self.recent_moments = []

    def append_living_moment(self, prompt: str, response: str, model_used: str,
                             context_tags: Optional[List[str]] = None,
                             emotional_resonance: float = 0.5):
        """
        Add a new memory moment with living context analysis.
        """
        mood_shift = self._analyze_mood_impact(prompt, response)
        energy_change = self._analyze_energy_impact(prompt, response)

        self.state.energy_level = max(0.1, min(1.0, self.state.energy_level + energy_change))
        self._evolve_mood(mood_shift)
        self._update_conversation_thread(prompt)
        self._extract_learning_insights(prompt, response)

        if self._is_creative_moment(prompt, response):
            self.state.last_creative_spark = datetime.utcnow()
            self.state.creative_momentum = min(1.0, self.state.creative_momentum + 0.2)

        moment = MemoryMoment(
            timestamp=datetime.utcnow(),
            prompt=prompt,
            response=response,
            mood=self.state.current_mood,
            energy=self.state.energy_level,
            context_tags=context_tags or [],
            model_used=model_used,
            interaction_depth=len(self.state.conversation_thread),
            emotional_resonance=emotional_resonance
        )

        self.recent_moments.append(moment)
        self.recent_moments = self.recent_moments[-15:]

        # Append to the memory pipeline (includes STM with session support)
        self.pipeline.append(moment)

        # Update broadcast summary for agent awareness
        summary_text = self.generate_broadcast_summary()
        self.pipeline.update_broadcast_summary(summary_text)

        self._save_living_state()

    def generate_broadcast_summary(self) -> str:
        """
        Generate a concise summary of recent moments and mood for broadcast.
        """
        recent_prompts = [m.prompt for m in self.recent_moments[-3:]]
        mood = self.state.current_mood
        energy = self.state.energy_level
        summary = f"Mood: {mood}, Energy: {energy:.2f}\nRecent: " + "; ".join(recent_prompts)
        return summary

    def _analyze_mood_impact(self, prompt: str, response: str) -> float:
        # Placeholder: simplistic mood impact analysis
        if any(word in prompt.lower() for word in ["happy", "great", "love"]):
            return 0.1
        if any(word in prompt.lower() for word in ["sad", "bad", "hate"]):
            return -0.1
        return 0.0

    def _analyze_energy_impact(self, prompt: str, response: str) -> float:
        # Placeholder: simplistic energy impact analysis
        if len(response) > 100:
            return 0.05
        return -0.02

    def _evolve_mood(self, mood_shift: float):
        moods = ["sad", "neutral", "optimistic", "happy", "excited"]
        idx = moods.index(self.state.current_mood) if self.state.current_mood in moods else 2
        idx = max(0, min(len(moods) - 1, idx + int(mood_shift * 10)))
        self.state.current_mood = moods[idx]

    def _update_conversation_thread(self, prompt: str):
        self.state.conversation_thread.append(prompt)
        if len(self.state.conversation_thread) > 20:
            self.state.conversation_thread = self.state.conversation_thread[-20:]

    def _extract_learning_insights(self, prompt: str, response: str):
        # Placeholder: simplistic learning insights extraction
        if "important" in prompt.lower():
            self.state.learning_insights.append(prompt)
            if len(self.state.learning_insights) > 10:
                self.state.learning_insights = self.state.learning_insights[-10:]