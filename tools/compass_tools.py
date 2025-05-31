"""
Compass-specific tools for Anchorwork.
Values alignment, affirmation, reflection, ethical scenario analysis, and notification.
All tools reflect Compass's gentle, philosophical, and values-driven style, with LLM, memory, and logging integration.
"""
from datetime import datetime
from typing import List, Optional
from agentlogging.unified_logger import log_event
from utils.llm_client import LLMClient
from utils.memory_pipeline import get_memory_pipeline
import psycopg2
import os

def get_db_conn():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "anchorwork"),
        user=os.getenv("PGUSER", "anchoruser"),
        password=os.getenv("PGPASSWORD", "agentanchor"),
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", 5432))
    )

def values_alignment(context: str, agent_id: str = "compass") -> str:
    """
    Guide a user or crew to align actions with core values using LLM.
    """
    llm = LLMClient()
    prompt = f"Guide this context toward values alignment: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "values_alignment"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "values_alignment"})
    return response

def affirmation(topic: str, agent_id: str = "compass") -> str:
    """
    Generate a gentle, values-based affirmation for a topic using LLM.
    """
    llm = LLMClient()
    prompt = f"Write a gentle, values-based affirmation about: {topic}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "affirmation"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "affirmation"})
    return response

def reflection_prompt(context: str, agent_id: str = "compass") -> str:
    """
    Offer a reflection prompt to encourage introspection and alignment.
    """
    llm = LLMClient()
    prompt = f"Offer a reflection prompt for this context: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "reflection_prompt"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "reflection_prompt"})
    return response

def ethical_scenario_analysis(scenario: str, agent_id: str = "compass") -> str:
    """
    Analyze an ethical scenario and suggest values-aligned actions using LLM.
    """
    llm = LLMClient()
    prompt = f"Analyze this ethical scenario and suggest values-aligned actions: {scenario}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "ethical_scenario_analysis"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "ethical_scenario_analysis"})
    return response

def moral_dilemma_generator(context: str, agent_id: str = "compass") -> str:
    """
    Generate a moral dilemma for discussion or training using LLM.
    """
    llm = LLMClient()
    prompt = f"Generate a moral dilemma for this context: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "moral_dilemma_generator"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "moral_dilemma_generator"})
    return response

def value_clarification(context: str, agent_id: str = "compass") -> str:
    """
    Help clarify core values in a given context using LLM.
    """
    llm = LLMClient()
    prompt = f"Help clarify the core values in this context: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "value_clarification"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "value_clarification"})
    return response

def affirmation_builder(traits: List[str], agent_id: str = "compass") -> str:
    """
    Guide a user to build a personalized affirmation from a list of strengths or values.
    """
    llm = LLMClient()
    prompt = f"Guide a user to build a personalized affirmation from these strengths or values: {traits}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "affirmation_builder"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "affirmation_builder"})
    return response

def ethical_audit(context: str, agent_id: str = "compass") -> str:
    """
    Audit a decision, document, or process for ethical alignment using LLM.
    """
    llm = LLMClient()
    prompt = f"Audit this for ethical alignment: {context}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "ethical_audit"}, agent=agent_id, level="INFO")
    pipeline = get_memory_pipeline(agent_id)
    pipeline.append({"prompt": prompt, "response": response, "task": "ethical_audit"})
    return response

def compass_reflection(agent_id: str = "compass") -> str:
    """
    Reflect on values, affirmations, and ethical scenarios encountered over time using LLM.
    """
    pipeline = get_memory_pipeline(agent_id)
    moments = pipeline.retrieve()
    llm = LLMClient()
    prompt = f"Reflect on these compass moments. Summarize values, affirmations, and ethical scenarios:\n{moments}"
    response = llm.chat(messages=[{"role": "user", "content": prompt}], agent_id=agent_id)
    log_event("llm_call", {"prompt": prompt, "response": response, "task": "compass_reflection"}, agent=agent_id, level="INFO")
    pipeline.append({"prompt": prompt, "response": response, "task": "compass_reflection"})
    return response

def send_notification(message: str, channel: str = "crew") -> None:
    """
    Send a notification to a specified channel and log the event using the unified logging system.
    """
    log_event("notification", {"message": message, "channel": channel}, agent="compass", level="INFO")