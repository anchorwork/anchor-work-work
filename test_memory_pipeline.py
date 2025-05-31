import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from utils.memory_pipeline import MemoryPipeline, get_memory_pipeline
from utils.living_memory import MemoryMoment

@pytest.fixture
def sample_moment():
    return MemoryMoment(
        timestamp=None,
        prompt="Hello",
        response="Hi there!",
        mood="optimistic",
        energy=0.8,
        context_tags=[],
        model_used="test-model",
        interaction_depth=1,
        emotional_resonance=0.5
    )

def test_append_and_retrieve(sample_moment):
    pipeline = get_memory_pipeline("test_agent")
    pipeline.append(sample_moment)
    context = pipeline.retrieve_context()
    assert any(m.prompt == "Hello" for m in context if hasattr(m, 'prompt'))

@pytest.mark.asyncio
async def test_async_append_and_retrieve(sample_moment):
    pipeline = get_memory_pipeline("test_agent_async")
    await pipeline.append_async(sample_moment)
    context = await pipeline.retrieve_context_async()
    assert any(m.prompt == "Hello" for m in context if hasattr(m, 'prompt'))