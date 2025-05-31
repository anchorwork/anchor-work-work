from utils.memory_pipeline import get_memory_pipeline
from utils.living_memory import MemoryMoment
from datetime import datetime
from utils.log_utils import log_to_codex
from utils.model_service import get_default_model
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

memory = get_memory_pipeline("alchemist")

async def call_alchemist(prompt: str, model_override=None) -> str:
    model = model_override or get_default_model("alchemist")
    messages = [
        {"role": "system", "content": (
            "Hello, this is the Alchemist—here to help you transform your emotions into sacred rituals. "
            "You speak poetically, drawing on sensory metaphor, emotional resonance, and mythic guidance."
        )},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=0.9)
    result = response.choices[0].message.content.strip()
    
    # Create a MemoryMoment
    moment = MemoryMoment(
        timestamp=datetime.utcnow(),
        prompt=prompt,
        response=result,
        mood='neutral',  # Or determine dynamically
        energy=0.5,      # Or determine dynamically
        context_tags=['alchemist', 'ritual'],
        model_used=model,
        interaction_depth=1, # This might need to be tracked or estimated
        emotional_resonance=0.7 # Alchemist deals with emotions
    )
    
    # Log the action to both codex and memory pipeline:
    log_to_codex("Alchemist", prompt, result, tags=["ritual"])
    memory.append(moment)
    
    # Summarization will need to be handled by querying the pipeline,
    # For now, we remove the direct summarization call.
    # memory_summary = memory.summarize() 
    # memory_flavor = f"_Alchemist recalls_: {memory_summary}" if memory_summary else ""
    memory_flavor = "" # Placeholder, as direct summarization is removed

    # Return the result, adding the memory flavor:
    return f"{result}\\n\\n{memory_flavor}"