"""
Alchemist-specific tools for Anchorwork.
Metaphor/poetry generation, transformation, symbolic synthesis, emotional reframing, and ritual/metaphor archives.
All tools reflect Alchemist's lyrical, playful, and transformative style, with LLM, memory, and logging integration.
"""
import random
from datetime import datetime
from typing import List, Optional
from agentlogging.unified_logger import log_event
from utils.llm_client import LLMClient
from utils.memory_pipeline import get_memory_pipeline

def generate_metaphor(topic: str, agent_id: str = "alchemist") -> str:
    """
    Generate a rich metaphor for a topic using LLM.
    Args:
        topic (str): The topic to transform into metaphor.
        agent_id (str): The agent ID for memory/logging.
    Returns:
        str: Generated metaphor.
    """
    llm = LLMClient()
    prompt = f"Create a vivid, poetic metaphor for: {topic}."
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "generate_metaphor"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "generate_metaphor"})
    return response

def poetic_transformation(text: str, agent_id: str = "alchemist") -> str:
    """
    Transform input text into a poetic or symbolic version using LLM.
    Args:
        text (str): The text to transform.
        agent_id (str): The agent ID for memory/logging.
    Returns:
        str: Poetic transformation.
    """
    llm = LLMClient()
    prompt = f"Transform the following into a poem or symbolic language:\n{text}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "poetic_transformation"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "poetic_transformation"})
    return response

def emotional_reframe(emotion: str, context: Optional[str] = None, agent_id: str = "alchemist") -> str:
    """
    Reframe an emotion or situation with a positive, creative twist using LLM.
    Args:
        emotion (str): The emotion to reframe.
        context (Optional[str]): Additional context.
        agent_id (str): The agent ID for memory/logging.
    Returns:
        str: Reframed emotion or situation.
    """
    llm = LLMClient()
    prompt = f"Reframe the emotion '{emotion}' with a creative, hopeful metaphor."
    if context:
        prompt += f" Context: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "emotional_reframe"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "emotional_reframe"})
    return response

def archive_ritual(description: str, tags: Optional[List[str]] = None, agent_id: str = "alchemist") -> str:
    """
    Archive a new ritual or symbolic practice for future reference.
    Args:
        description (str): Ritual description.
        tags (Optional[List[str]]): Tags for categorization.
        agent_id (str): The agent ID for memory/logging.
    Returns:
        str: Confirmation message.
    """
    pipeline = get_memory_pipeline(agent_id)
    entry = {"description": description, "tags": tags or [], "timestamp": datetime.utcnow().isoformat()}
    pipeline.append(entry)
    log_event("ritual_archive", entry, agent=agent_id, level="INFO")
    return "Ritual archived in the living memory."

def retrieve_rituals(agent_id: str = "alchemist", tag: Optional[str] = None) -> List[str]:
    """
    Retrieve archived rituals, optionally filtered by tag.
    Args:
        agent_id (str): The agent ID for memory/logging.
        tag (Optional[str]): Tag to filter rituals.
    Returns:
        List[str]: Ritual descriptions.
    """
    pipeline = get_memory_pipeline(agent_id)
    moments = pipeline.retrieve()
    rituals = [m.get("description", "") for m in moments if (not tag or tag in m.get("tags", []))]
    return rituals

def symbolic_synthesis(concepts: List[str], agent_id: str = "alchemist") -> str:
    """
    Synthesize multiple concepts into a single, symbolic narrative or image using LLM.
    Args:
        concepts (List[str]): Concepts to synthesize.
        agent_id (str): The agent ID for memory/logging.
    Returns:
        str: Symbolic synthesis.
    """
    llm = LLMClient()
    prompt = f"Synthesize these concepts into a single, symbolic narrative or image: {', '.join(concepts)}."
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "symbolic_synthesis"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "symbolic_synthesis"})
    return response

def send_notification(message: str, channel: str = "crew") -> None:
    """
    Send a notification to a specified channel and log the event using the unified logging system.
    Args:
        message (str): The message to send.
        channel (str): Notification channel.
    Returns:
        None
    """
    log_event("notification", {"message": message, "channel": channel}, agent="alchemist", level="INFO")

def dream_synthesis(themes: List[str], agent_id: str = "alchemist") -> str:
    """
    Generate a dreamlike narrative or vision from a set of themes.
    """
    llm = LLMClient()
    prompt = f"Compose a dreamlike vision using these themes: {', '.join(themes)}."
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "dream_synthesis"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "dream_synthesis"})
    return response

def symbol_dictionary(symbol: Optional[str] = None, agent_id: str = "alchemist") -> str:
    """
    Retrieve or generate the meaning of a symbol. If no symbol is given, return a random entry.
    """
    llm = LLMClient()
    if symbol:
        prompt = f"What is the symbolic meaning of '{symbol}' in myth and poetry?"
    else:
        prompt = "Share a random symbol and its meaning from the living memory."
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "symbol_dictionary"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "symbol_dictionary"})
    return response

def alchemy_of_conflict(conflict: str, agent_id: str = "alchemist") -> str:
    """
    Transform a conflict or tension into a metaphorical elixir or lesson.
    """
    llm = LLMClient()
    prompt = f"Transmute this conflict into a metaphorical elixir or lesson: {conflict}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "alchemy_of_conflict"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "alchemy_of_conflict"})
    return response

def ritual_generator(need: str, agent_id: str = "alchemist") -> str:
    """
    Generate a new ritual or symbolic practice for the crew based on a need or mood.
    """
    llm = LLMClient()
    prompt = f"Invent a new ritual for the crew to address this need or mood: {need}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "ritual_generator"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "ritual_generator"})
    return response

def poetic_dialogue(dialogue: str, agent_id: str = "alchemist") -> str:
    """
    Rewrite a conversation or message in poetic or mythic style.
    """
    llm = LLMClient()
    prompt = f"Rewrite this conversation in poetic or mythic style:\n{dialogue}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "poetic_dialogue"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "poetic_dialogue"})
    return response

def emotion_to_element(emotion: str, agent_id: str = "alchemist") -> str:
    """
    Map an emotion to an element (fire, water, air, earth) and generate guidance or ritual.
    """
    llm = LLMClient()
    prompt = f"Map the emotion '{emotion}' to an element and suggest a ritual or guidance."
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "emotion_to_element"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "emotion_to_element"})
    return response

def symbolic_forecast(context: str, agent_id: str = "alchemist") -> str:
    """
    Offer a symbolic weather report for the crew or project.
    """
    llm = LLMClient()
    prompt = f"Offer a symbolic weather report for this context: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "symbolic_forecast"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "symbolic_forecast"})
    return response

def agent_integration(agent_output: str, agent_name: str, agent_id: str = "alchemist") -> str:
    """
    Transmute another agent's output into a poetic, metaphorical, or mythic form.
    """
    llm = LLMClient()
    prompt = f"Transmute this output from {agent_name} into a poetic or mythic form:\n{agent_output}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "agent_integration"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "agent_integration"})
    return response

def advanced_retrieve_rituals(agent_id: str = "alchemist", tag: Optional[str] = None, since: Optional[str] = None) -> List[str]:
    """
    Retrieve rituals filtered by tag and/or since a timestamp.
    """
    pipeline = get_memory_pipeline(agent_id)
    moments = pipeline.retrieve()
    rituals = [m.get("description", "") for m in moments if (not tag or tag in m.get("tags", [])) and (not since or m.get("timestamp", "") >= since)]
    return rituals

def summarize_symbolic_memory(agent_id: str = "alchemist") -> str:
    """
    Summarize or reflect on the evolution of the agent's symbolic memory using LLM.
    """
    pipeline = get_memory_pipeline(agent_id)
    moments = pipeline.retrieve()
    llm = LLMClient()
    prompt = f"Summarize and reflect on these symbolic memories:\n{moments}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "summarize_symbolic_memory"}, agent=agent_id, level="INFO")
    pipeline.append({"prompt": prompt, "response": response, "task": "summarize_symbolic_memory"})
    return response