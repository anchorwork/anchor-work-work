"""
utils/vector_memory.py

Provides a managed Pinecone-based vector memory store for agent long-term embeddings.
Enhanced with index size estimation and async support.
"""
import os
import asyncio
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec
from typing import Optional
import time
from agentlogging.unified_logger import log_event

# --- PineconeMemory Factory with Role-Based Access ---
_pinecone_cache = {}

def get_pinecone_memory(agent_id: str, purpose: str = "memory", role: Optional[str] = None):
    """
    Factory for PineconeMemory with enforced naming and access control.
    - agent_id: agent or 'anchorwork core'
    - purpose: 'memory', 'education', etc.
    - role: agent role (e.g., 'cartographer')
    """
    index_name = f"anchorwork-{agent_id}-{purpose}".lower().replace("_", "-")
    key = (index_name, role)
    if key not in _pinecone_cache:
        _pinecone_cache[key] = PineconeMemory(index_name, role=role)
    return _pinecone_cache[key]

class PineconeMemory:
    def __init__(self, index_name: str, role: str = None):
        embedding_model = os.getenv("EMBEDDING_MODEL", os.getenv("EMBED_MODEL", "text-embedding-ada-002"))
        self.embedder = OpenAIEmbeddings(model=embedding_model)
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = index_name
        self.role = role
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
        except Exception as e:
            log_event("pinecone_index_list_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
            existing_indexes = []
        if self.index_name not in existing_indexes:
            dimension = 1536
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=os.getenv("PINECONE_REGION", "us-west-2")
                    )
                )
                time.sleep(5)
            except Exception as e:
                log_event("pinecone_create_index_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
        try:
            self.store = LangChainPinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embedder
            )
        except Exception as e:
            log_event("pinecone_connect_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
            self.store = None

    def add(self, text: str, metadata: dict = None):
        """
        Add a single document to Pinecone. Always includes agent_id and timestamp in metadata.
        """
        if self.index_name == "anchorwork-anchorwork core-memory" and (self.role is None or self.role.lower() != "cartographer"):
            log_event("pinecone_write_denied", {"index": self.index_name, "role": self.role}, agent=self.role, level="WARNING")
            return
        if self.store is None:
            log_event("pinecone_store_unavailable", {"index": self.index_name}, agent=self.role, level="ERROR")
            return
        try:
            meta = metadata.copy() if metadata else {}
            meta.setdefault("agent_id", self.role)
            meta.setdefault("timestamp", time.time())
            doc = Document(page_content=text, metadata=meta)
            self.store.add_documents([doc])
        except Exception as e:
            log_event("pinecone_add_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")

    def add_batch(self, texts: list, metadatas: list = None):
        """
        Add a batch of documents to Pinecone.
        """
        if self.store is None:
            log_event("pinecone_store_unavailable", {"index": self.index_name}, agent=self.role, level="ERROR")
            return
        try:
            docs = []
            for i, text in enumerate(texts):
                meta = (metadatas[i] if metadatas and i < len(metadatas) else {})
                meta.setdefault("agent_id", self.role)
                meta.setdefault("timestamp", time.time())
                docs.append(Document(page_content=text, metadata=meta))
            self.store.add_documents(docs)
        except Exception as e:
            log_event("pinecone_add_batch_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")

    def query(self, text: str, k: int = 5):
        """
        Query Pinecone for similar documents.
        """
        if self.store is None:
            log_event("pinecone_store_unavailable", {"index": self.index_name}, agent=self.role, level="ERROR")
            return []
        try:
            return self.store.similarity_search(text, k)
        except Exception as e:
            log_event("pinecone_query_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
            return []

    def query_batch(self, texts: list, k: int = 5):
        """
        Query Pinecone for a batch of prompts.
        """
        results = []
        for text in texts:
            results.append(self.query(text, k))
        return results

    def estimated_size(self) -> int:
        """
        Estimate the number of vectors/documents in the Pinecone index.
        """
        try:
            index_stats = self.pc.describe_index(self.index_name)
            return index_stats.get('total_vector_count', -1)
        except Exception as e:
            log_event("pinecone_index_size_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
            return -1

    async def estimated_size_async(self) -> int:
        """
        Async wrapper for estimated_size using asyncio.to_thread.
        """
        return await asyncio.to_thread(self.estimated_size)

    def health_check(self) -> bool:
        """
        Check Pinecone connectivity and index status.
        """
        try:
            self.pc.describe_index(self.index_name)
            return True
        except Exception as e:
            log_event("pinecone_health_error", {"index": self.index_name, "error": str(e)}, agent=self.role, level="ERROR")
            return False

# --- Utility: Summarize and Upsert Milestone Events to Pinecone ---
def upsert_milestone_summary_to_pinecone(agent_id: str, event: dict, role: Optional[str] = None):
    """
    Summarize a milestone event and upsert to agent's Pinecone memory index.
    Only for important events (not full logs).
    """
    summary = f"[{event.get('timestamp')}] {event.get('event_type')}: {event.get('message', '')}"
    pinecone_mem = get_pinecone_memory(agent_id, purpose="memory", role=role)
    pinecone_mem.add(text=summary, metadata=event)

# --- Usage Pattern (documented for agents) ---
# - For agent education: get_pinecone_memory(agent_id, purpose="education").add(...)
# - For agent memory: get_pinecone_memory(agent_id, purpose="memory").add(...)
# - For anchorwork core: get_pinecone_memory("anchorwork core", purpose="memory", role=role)
#   (Only Cartographer should use role="cartographer" for writes)