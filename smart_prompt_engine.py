import os
from typing import Optional, List, Dict, Any
from utils.memory_pipeline import get_memory_pipeline
from tools.shared import semantic_search, web_search
from agentlogging.unified_logger import log_event
from utils.model_service import get_default_model


def build_smart_prompt(
    prompt: str,
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    use_sensory: bool = True,
    use_stm: bool = True,
    use_working: bool = True,
    use_ltm: bool = True,
    use_vector: bool = True,
    use_web: bool = True,
    log: bool = True,
    info_model: Optional[str] = None  # New: specify model for info gathering
) -> str:
    """
    Build a smart prompt by incorporating context from multiple memory layers and web search.
    Uses the cheapest model for info gathering by default.
    Args:
        prompt (str): The user's input prompt.
        agent_id (str): Agent ID for context retrieval and logging.
        session_id (str): Session ID for context retrieval and logging.
        use_sensory, use_stm, use_working, use_ltm (bool): Which memory layers to include.
        use_vector (bool): Whether to include context from semantic search.
        use_web (bool): Whether to include recent web search results.
        log (bool): Whether to log the prompt construction event.
        info_model (str): Model to use for info gathering (defaults to cheapest).
    Returns:
        str: The combined prompt with context and user request.
    """
    context_parts = []
    sources_used = {}
    pipeline = get_memory_pipeline(agent_id=agent_id, session_id=session_id) if agent_id else None

    # Choose cheapest model for info gathering
    if info_model is None:
        info_model = get_default_model("info_gathering")  # e.g., gpt-4.1-mini-nano

    # Sensory Memory
    if use_sensory and pipeline:
        try:
            sensory = pipeline.sensory.retrieve()
            if sensory:
                context_parts.append("Sensory memory (recent raw inputs):\n" + str(sensory))
                sources_used["sensory"] = True
        except Exception as e:
            context_parts.append(f"[Error retrieving sensory memory: {e}]")
            sources_used["sensory"] = False

    # Short-Term Memory
    if use_stm and pipeline:
        try:
            stm = pipeline.short_term.retrieve()
            if stm:
                context_parts.append("Short-term memory (recent buffer):\n" + str(stm))
                sources_used["short_term"] = True
        except Exception as e:
            context_parts.append(f"[Error retrieving short-term memory: {e}]")
            sources_used["short_term"] = False

    # Working Memory
    if use_working and pipeline:
        try:
            wkm = pipeline.working.retrieve()
            if wkm:
                context_parts.append("Working memory (active context):\n" + str(wkm))
                sources_used["working"] = True
        except Exception as e:
            context_parts.append(f"[Error retrieving working memory: {e}]")
            sources_used["working"] = False

    # Long-Term Memory
    if use_ltm and pipeline:
        try:
            ltm = pipeline.long_term.retrieve(query=prompt, k=5)
            if ltm:
                context_parts.append("Long-term memory (semantic archive):\n" + str(ltm))
                sources_used["long_term"] = True
        except Exception as e:
            context_parts.append(f"[Error retrieving long-term memory: {e}]")
            sources_used["long_term"] = False

    # Semantic Search (vector)
    if use_vector:
        try:
            # Pass info_model to semantic_search if supported
            vector_matches = semantic_search(prompt, model=info_model) if "model" in semantic_search.__code__.co_varnames else semantic_search(prompt)
            if isinstance(vector_matches, str):
                context_parts.append("Semantic search context:\n" + vector_matches)
            else:
                context_parts.append("Semantic search context:\n" + "\n---\n".join(vector_matches))
            sources_used["vector"] = True
        except Exception as e:
            context_parts.append(f"[Error in semantic search: {e}]")
            sources_used["vector"] = False

    # Web Search
    if use_web:
        try:
            # Pass info_model to web_search if supported
            web_text = web_search(prompt, model=info_model) if "model" in web_search.__code__.co_varnames else web_search(prompt)
            context_parts.append("Recent research findings:\n" + web_text)
            sources_used["web"] = True
        except Exception as e:
            context_parts.append(f"[Error in web search: {e}]")
            sources_used["web"] = False

    # Compose final prompt
    full_prompt = "\n\n".join(context_parts) + f"\n\nUser request:\n{prompt}"

    # Optionally log the prompt construction event
    if log:
        log_event(
            "prompt_construction",
            {
                "prompt": prompt,
                "agent_id": agent_id,
                "session_id": session_id,
                "sources_used": sources_used,
                "info_model": info_model,
                "final_prompt_length": len(full_prompt),
                "final_prompt_preview": full_prompt[:500],
            },
            agent=agent_id,
            session_id=session_id,
            level="INFO"
        )

    return full_prompt
