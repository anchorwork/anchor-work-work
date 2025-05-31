"""
Multi-tier MemoryPipeline coordinating Sensory, Short-Term, Working, and Long-Term memory backends.
Supports session-scoped shared memories and broadcast summaries for agent awareness.
Includes robust error handling, logging, and async wrappers.
"""
from typing import Protocol, Optional, List, Dict, Any
from utils.living_memory import MemoryMoment, LivingMemory
from utils.redis_streams import log_user_interaction, log_memory_update, get_streams_manager
from utils.vector_memory import PineconeMemory
from tools.shared import append_identity
from agentlogging.unified_logger import log_event
import redis
import os
import json
import time
import logging
import asyncio
from utils.file_utils import write_agent_summary

logger = logging.getLogger(__name__)

# --- Protocol Definition ---
class MemoryBackend(Protocol):
    def append(self, moment: MemoryMoment, **kwargs) -> None:
        ...
    def retrieve(self, query: Optional[str] = None, **opts) -> List[MemoryMoment]:
        ...

# --- Backends ---
class SensoryMemory:
    """Ephemeral store for ms–s inputs via Redis Streams, per agent."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.streams = get_streams_manager()
    def append(self, moment: MemoryMoment, **kwargs) -> None:
        try:
            log_user_interaction(
                user_id=self.agent_id,
                interaction_type="sensory",
                data={"prompt": moment.prompt, "timestamp": moment.timestamp.isoformat()}
            )
            log_event("memory_append", {"tier": "sensory", "moment": moment.__dict__}, agent=self.agent_id)
        except Exception as e:
            logger.error(f"Error appending to SensoryMemory for agent {self.agent_id}: {e}")
    def retrieve(self, count: int = 10, minutes: int = 1, **opts) -> List:
        try:
            mgr = get_streams_manager()
            events = mgr.get_recent_events("user_interactions", minutes=minutes)
            log_event("memory_retrieve", {"tier": "sensory", "count": count}, agent=self.agent_id)
            return events[:count]
        except Exception as e:
            logger.error(f"Error retrieving from SensoryMemory for agent {self.agent_id}: {e}")
            return []

class ShortTermMemory:
    """
    Short-lived buffer (seconds) of recent entries using Redis List.
    Supports optional session_id for shared short-term memory.
    """
    def __init__(self, agent_id: str, session_id: Optional[str] = None, max_items: int = 7, ttl: int = 30):
        from utils.redis_client import get_redis_client
        self.redis = get_redis_client().client
        self.session_id = session_id
        self.agent_id = agent_id
        if session_id:
            self.key = f"stm:session:{session_id}"
        else:
            self.key = f"stm:{agent_id}"
        self.max_items = max_items
        self.ttl = ttl

    def append(self, moment: MemoryMoment, **kwargs) -> None:
        try:
            self.redis.lpush(self.key, json.dumps(moment.__dict__))
            self.redis.ltrim(self.key, 0, self.max_items - 1)
            self.redis.expire(self.key, self.ttl)
            log_event("memory_append", {"tier": "short_term", "moment": moment.__dict__}, agent=self.agent_id)
        except Exception as e:
            logger.error(f"Redis error in ShortTermMemory.append for key {self.key}: {e}")

    def retrieve(self, **opts) -> List[Dict[str, Any]]:
        try:
            items = self.redis.lrange(self.key, 0, self.max_items - 1)
            log_event("memory_retrieve", {"tier": "short_term", "count": len(items)}, agent=self.agent_id)
            return [json.loads(item) for item in items]
        except Exception as e:
            logger.error(f"Redis error in ShortTermMemory.retrieve for key {self.key}: {e}")
            return []

class WorkingMemory:
    """Active conversation context and state updates, per agent."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.living = LivingMemory(agent_id=agent_id)
    def append(self, moment: MemoryMoment, **kwargs) -> None:
        try:
            self.living.append_living_moment(
                moment.prompt, moment.response, moment.model_used,
                context_tags=moment.context_tags
            )
            log_memory_update(
                agent_id=self.agent_id,
                update_type="living",
                data={"mood": self.living.state.current_mood}
            )
            log_event("memory_append", {"tier": "working", "moment": moment.__dict__}, agent=self.agent_id)
        except Exception as e:
            logger.error(f"Error appending to WorkingMemory for agent {self.agent_id}: {e}")
    def retrieve(self, **opts) -> List[MemoryMoment]:
        try:
            log_event("memory_retrieve", {"tier": "working"}, agent=self.agent_id)
            return self.living.recent_moments
        except Exception as e:
            logger.error(f"Error retrieving from WorkingMemory for agent {self.agent_id}: {e}")
            return []

class LongTermMemory:
    """
    Durable semantic store: dual Pinecone indexes.
    Supports optional session_id for shared long-term memory.
    """
    def __init__(self, agent_id: str, session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.session_id = session_id
        index_suffix = f"session-{session_id}" if session_id else agent_id
        self.active = PineconeMemory(f"{index_suffix}-active")
        self.archive = PineconeMemory(f"{index_suffix}-archive")
        self.size_threshold = int(os.getenv("ACTIVE_SIZE_THRESHOLD", "100000"))
        self.batch_size = int(os.getenv("SUMMARY_BATCH_SIZE", "50"))
        self._buffer = []

    def append(self, moment: MemoryMoment, **kwargs) -> None:
        try:
            text = f"{moment.timestamp}: {moment.prompt}\n{moment.response}"
            self.active.add(text=text, metadata=moment.__dict__)
            self._buffer.append(text)
            log_event("memory_append", {"tier": "long_term", "moment": moment.__dict__}, agent=self.agent_id)
            if len(self._buffer) >= self.batch_size:
                self._summarize_batch()
        except Exception as e:
            logger.error(f"Error appending to LongTermMemory for agent {self.agent_id} session {self.session_id}: {e}")

    def _summarize_batch(self):
        try:
            old_docs = self.active.fetch_oldest(self.batch_size)
            if not old_docs:
                return
            summary_text = self._summarize_texts([doc.text for doc in old_docs])
            self.archive.add(text=summary_text, metadata={"batch": time.time()})
            self.active.delete(doc_ids=[d.id for d in old_docs])
            self._buffer.clear()
            log_event("memory_summarize", {"tier": "long_term", "batch_size": self.batch_size}, agent=self.agent_id)
        except Exception as e:
            logger.error(f"Error summarizing batch for agent {self.agent_id} session {self.session_id}: {e}")

    def _summarize_texts(self, texts: List[str]) -> str:
        return "\n".join(texts[:3]) + "\n... [summary truncated]"

    def retrieve(self, query: Optional[str] = None, k: int = 5, **opts) -> List[Any]:
        try:
            active_results = self.active.query(query, top_k=k)
            archive_results = self.archive.query(query, top_k=k)
            log_event("memory_retrieve", {"tier": "long_term", "query": query, "k": k}, agent=self.agent_id)
            return active_results + archive_results
        except Exception as e:
            logger.error(f"Error retrieving from LongTermMemory for agent {self.agent_id} session {self.session_id}: {e}")
            return []

# --- Broadcast Summaries for Agent Awareness ---
class BroadcastSummaries:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "broadcast:agent"

    def update_summary(self, agent_id: str, summary_text: str, ttl: int = 120):
        try:
            key = f"{self.prefix}:{agent_id}"
            self.redis.set(key, summary_text, ex=ttl)
        except Exception as e:
            logger.error(f"Redis error in BroadcastSummaries.update_summary for agent {agent_id}: {e}")

    def get_all_summaries(self) -> Dict[str, str]:
        try:
            keys = self.redis.keys(f"{self.prefix}:*")
            summaries = {}
            for key in keys:
                agent = key.decode().split(":")[-1]
                val = self.redis.get(key)
                if val:
                    summaries[agent] = val.decode()
            return summaries
        except Exception as e:
            logger.error(f"Redis error in BroadcastSummaries.get_all_summaries: {e}")
            return {}

class MemoryPipeline:
    def __init__(self, agent_id: str, session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.session_id = session_id
        self.sensory = SensoryMemory(agent_id)
        self.short_term = ShortTermMemory(agent_id, session_id=session_id)
        self.working = WorkingMemory(agent_id)
        self.long_term = LongTermMemory(agent_id, session_id=session_id)
        from utils.redis_client import get_redis_client
        self.redis = get_redis_client().client
        self.broadcast = BroadcastSummaries(self.redis)

    def append(self, moment: MemoryMoment):
        try:
            logger.debug(f"Appending moment for agent {self.agent_id} session {self.session_id}")
            self.sensory.append(moment)
            self.short_term.append(moment)
            self.working.append(moment)
            self.long_term.append(moment)
            log_event("memory_pipeline_append", {"agent_id": self.agent_id, "session_id": self.session_id, "moment": moment.__dict__}, agent=self.agent_id)
            logger.debug("Append successful")
        except Exception as e:
            logger.error(f"Error appending moment: {e}")

    def retrieve_context(self, query: Optional[str] = None, k: int = 5) -> List[Any]:
        try:
            logger.debug(f"Retrieving context for agent {self.agent_id} session {self.session_id} query={query}")
            stm = self.sensory.retrieve()
            wkm = self.working.retrieve()
            candidates = self.long_term.retrieve(query=query, k=k)
            log_event("memory_pipeline_retrieve", {"agent_id": self.agent_id, "session_id": self.session_id, "query": query, "k": k}, agent=self.agent_id)
            logger.debug("Retrieve successful")
            return stm + wkm + candidates
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    async def append_async(self, moment: MemoryMoment):
        await asyncio.to_thread(self.append, moment)

    async def retrieve_context_async(self, query: Optional[str] = None, k: int = 5) -> List[Any]:
        return await asyncio.to_thread(self.retrieve_context, query, k)

    def update_broadcast_summary(self, summary_text: str, ttl: int = 120):
        self.broadcast.update_summary(self.agent_id, summary_text, ttl)

    def get_broadcast_summaries(self) -> Dict[str, str]:
        return self.broadcast.get_all_summaries()

    def write_summary_to_disk(self, events: list) -> str:
        """
        Summarizes recent events for this agent and writes the summary to /data/memory/{agent_id}/ as a JSON file.
        Returns the path to the written summary file.
        """
        return write_agent_summary(self.agent_id, events)

_pipeline_cache: Dict[str, MemoryPipeline] = {}

def get_memory_pipeline(agent_id: str = None, session_id: Optional[str] = None) -> MemoryPipeline:
    key = f"{agent_id}:{session_id}"
    if key not in _pipeline_cache:
        _pipeline_cache[key] = MemoryPipeline(agent_id, session_id=session_id)
    return _pipeline_cache[key]
