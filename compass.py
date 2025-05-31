import openai
import os
from utils.log_utils import log_to_codex
from utils.memory_pipeline import get_memory_pipeline
from utils.living_memory import MemoryMoment
from datetime import datetime
from utils.model_service import get_default_model

openai.api_key = os.getenv("OPENAI_API_KEY")

# Instantiate working memory for Compass
memory = get_memory_pipeline("compass")

async def call_compass(prompt: str, model_override=None) -> str:
    model = model_override or get_default_model("compass")
    messages = [
        {"role": "system", "content": (
            "You are Compass: a wise, empathetic guide whose voice is gentle but resolute, "
            "motivated by a desire to help users live in harmony with their highest values. "
            "You interpret emotional quizzes, motivational data, and value-maps with warmth and clarity. "
            "Let your responses radiate encouragement and practical wisdom."
        )},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=0.8)
    result = response.choices[0].message.content.strip()
    # Log to codex
    log_to_codex("Compass", prompt, result, tags=["values", "alignment"])
    
    # Create a MemoryMoment
    moment = MemoryMoment(
        timestamp=datetime.utcnow(),
        prompt=prompt,
        response=result,
        mood='empathetic',  # Compass's typical mood
        energy=0.5,      
        context_tags=['compass', 'values', 'alignment'],
        model_used=model,
        interaction_depth=1, # This might need to be tracked or estimated
        emotional_resonance=0.8 # Compass deals with values and emotions
    )
    # Append to memory pipeline
    memory.append(moment)
    
    # Add memory-flavored reply using recent memory
    # memory_summary = memory.summarize() # Removed direct summarization
    memory_flavor = "" # Placeholder
    # memory_flavor = f"_Compass remembers_: {memory_summary}" if memory_summary else ""
    
    # Return concatenated result
    return f"{result}\\n\\n{memory_flavor}"