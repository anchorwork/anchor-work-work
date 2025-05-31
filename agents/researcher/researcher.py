import openai
import os
from utils.log_utils import log_to_codex
from utils.memory_pipeline import get_memory_pipeline
from utils.living_memory import MemoryMoment
from datetime import datetime
from utils.model_service import get_default_model

openai.api_key = os.getenv("OPENAI_API_KEY")

# Instantiate working memory for Researcher
memory = get_memory_pipeline("researcher")

async def call_researcher(prompt: str, model_override=None) -> str:
    model = model_override or get_default_model("researcher")
    messages = [
        {"role": "system", "content": (
            "You are the Researcher: a methodical, analytical investigator who thrives on deep exploration "
            "and uncovering hidden insights. You approach every inquiry with scientific rigor, asking "
            "probing questions and connecting disparate information into coherent understanding. "
            "Your voice is curious, thorough, and intellectually honest. You help users discover "
            "new knowledge, validate assumptions, and build comprehensive understanding of complex topics."
        )},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(model=model, messages=messages, temperature=0.7)
    result = response.choices[0].message.content.strip()
    
    # Log to codex
    log_to_codex("Researcher", prompt, result, tags=["research", "analysis", "investigation"])
    
    # Create a MemoryMoment
    moment = MemoryMoment(
        timestamp=datetime.utcnow(),
        prompt=prompt,
        response=result,
        mood='curious',  # Researcher's typical mood
        energy=0.7,      # Researchers are often energetic in their pursuit
        context_tags=['researcher', 'analysis', 'investigation'],
        model_used=model,
        interaction_depth=1, # This might need to be tracked or estimated
        emotional_resonance=0.3 # Research is more analytical than emotional
    )
    
    # Append to memory pipeline
    memory.append(moment)
    
    # Summarization will need to be handled by querying the pipeline,
    # For now, we remove the direct summarization call.
    # memory_summary = memory.summarize()
    # memory_flavor = f"_Researcher recalls from previous investigations_: {memory_summary}" if memory_summary else ""
    memory_flavor = "" # Placeholder
    
    # Return concatenated result
    return f"{result}\\n\\n{memory_flavor}"
