from utils.log_utils import search_codex
from utils.memory_pipeline import get_memory_pipeline
from utils.living_memory import MemoryMoment
from datetime import datetime

memory = get_memory_pipeline("watcher")

async def summarize_logs(keyword: str) -> str:
    entries = search_codex(keyword)
    if not entries:
        return "No matching logs found."
    summary = f"Found {len(entries)} entries related to '{keyword}':\\n"
    for e in entries[-5:]:  # show latest 5
        summary += f"- [{e['timestamp']}] {e['agent']}: {e['response'][:100]}...\\n"
    
    memory_flavor = "" # Placeholder
    
    moment = MemoryMoment(
        timestamp=datetime.utcnow(),
        prompt=f"summarize_logs({keyword})",
        response=summary,
        mood='focused', 
        energy=0.5,
        context_tags=['watcher', 'summary'],
        model_used='system', # Watcher is a system utility
        interaction_depth=0, 
        emotional_resonance=0.1
    )
    memory.append(moment)
    return f"{summary}\\n{memory_flavor}"