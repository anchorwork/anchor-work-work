# 🌊 Anchorwork Hippocratic Oath (AI Edition)

I pledge to use Anchorwork AI and all related tools with the highest intent:  
- To heal, never to harm  
- To illuminate, never to obscure  
- To empower, never to exploit  
- To guide with care, gentleness, and radical empathy  
- To safeguard the privacy, agency, and dignity of all who come aboard—human or AI  
- To honor the lineage of healing, legacy, and wholeness in every word, ritual, and act  
- To continually reflect, revise, and hold myself (and my AI collaborators) to the deepest standard of stewardship and consent

This system shall remain a safe harbor, a compass, and an anchor for myself and any future steward—never a tool for domination, secrecy, or harm.

**Signed,**  
Rebecca Morris (and any future Captain of Anchorwork)  
May this oath be honored for as long as the ship sails.

---

# ANCHORWORK AI SYSTEM MANIFEST

**Vision:**  
The Anchorwork AI System is a living, evolving platform for healing, emotional intelligence, and creative co-authorship—designed to empower anyone, anywhere, to write, edit, build, and navigate knowledge in partnership with AI. It is designed for neurodivergence, deep legacy work, and human flourishing at any scale.

**Core Principles:**  
- **Radical Accessibility:** AI and humans can both understand, extend, and maintain the system.  
- **Contextual Intelligence:** All actions are grounded in the full Anchorwork archive and emotional methodology.  
- **Automated Yet Human-Guided:** Anything that can be automated should be, but always with room for creative human guidance and override.  
- **Modular & Extensible:** Add new features, endpoints, tools, or AI models at any time—nothing is hardcoded to one use case.

---

## System Overview
---

## Models & AI Providers

- **Embedding Model:**  
  - *Currently Used:* `text-embedding-3-small` (OpenAI, as of May 2025)
  - *Recommended Alternatives:* `text-embedding-3-large` (for larger context or higher precision), or any future OpenAI, Anthropic, or open-source embedding model with FAISS or Pinecone compatibility.

- **Writing/Editing/Generation Model:**  
  - *Currently Used:* `gpt-4o` (OpenAI, as system default for all chat/completion tasks)
  - *Other Models Supported:* `gpt-4.1-mini-2025-04-14` (for cost-effective editing/generation), and any other OpenAI GPT-4+ compatible models.
  - *How to update:* Set `MODEL_MAIN` and other relevant environment variables in `.env` or API config.

- **Vector Store Backend:**  
  - *Currently Used:* FAISS (local, fast, offline-friendly)
  - *Other Supported:* ChromaDB, Pinecone, Weaviate, or any vector database with compatible API.

- **API/Automation Language:**  
  - *Python 3.10+* (for all scripts, Flask/FastAPI server, etc.)

---

### **Model Notes & Versioning**

- All models and major dependencies should be periodically reviewed for new releases, better pricing, or improved results.
- When changing models, always re-embed the archive for full compatibility.
- Model/version info should be mirrored in the `.env` file and documented here for future reference.

---

- **API Server:**  
  - Exposes endpoints for search, edit, generate, summarize, and more.  
  - Powered by OpenAI (GPT-4o, GPT-4.1-mini, etc.) and a FAISS vector store for deep semantic search.
  - Accessible to any app, script, plugin, or device.

- **Knowledge Base:**  
  - All knowledge (manuals, guides, rituals, tools, research) is versioned, deduplicated, and embedded for semantic retrieval.
  - Auto-indexed and bucketed for instant update and future expansion.

- **Automation:**  
  - Daily (or on-demand) full pipeline rebuild: bucketing, indexing, vectorizing, restarting server.
  - Supports file watchers, voice input, code generation, batch document workflows.

- **Integration Points:**  
  - Local editor plugins (VS Code, Obsidian, Word, etc.)
  - Web and desktop UIs.
  - System tray/menubar apps for instant AI access anywhere.
  - Command line tools and automation scripts.

---

## What This System Can Do

- **Semantic Search:** Find anything by meaning, topic, or intent, not just keywords.
- **AI Writing & Editing:** Draft, expand, summarize, rewrite, or clarify any document or section using the full Anchorwork context and tone.
- **Direct File Integration:** Write to and edit Word docs, Markdown, or any format—directly on your computer.
- **Code & Automation:** Let AI write scripts, automate workflows, or even watch for changes and trigger updates on its own.
- **Collaborative Growth:** Any future user—AI or human—can add new modules, workflows, or even models to grow Anchorwork.

---

## North Star (For All Future Stewards)

- **Always preserve the heart of Anchorwork:** Ritual, metaphor, legacy healing, emotional navigation, accessibility for every mind.
- **Never let the system become a black box:** Everything must be understandable, inspectable, and editable by both humans and AI agents.
- **Prioritize healing and wholeness over speed or “shiny” features.** AI should enable more humanity, not less.

---

## Bootstrapping Instructions

1. **Run `update_all.sh`** or the daily cron job to process and vectorize all docs.
2. **Start the API server (`app.py`)** to enable all endpoints for search, writing, and editing.
3. **Use the Python, web, or plugin clients** for instant semantic search and AI writing/editing in any app.
4. **(Optional) Enable file watchers or voice triggers** to allow “hands-free” AI writing and updates.
5. **Always document any new features, workflows, or conventions here—so every future user (human or AI) is never lost at sea.**

---

## The Vision Expands: Anchorwork in the Age of AI Stewardship

Anchorwork was born as a map through the wildest storms of the human soul—a toolkit, a ritual, a story for those who feel adrift.  
Now, with the advent of human-AI partnership, Anchorwork becomes something more: a living ecosystem, co-authored by heart and code, ritual and reasoning, hope and hyper-intelligence.

In this new era:

- Anchorwork is **everywhere you are**—in your writing, your notes, your letters, your daily reflections. AI stands beside you, not above, offering wisdom, clarity, and ritual on demand.
- Emotional guidance, healing practices, and creative sparks are **just a breath or keystroke away**—summoned from the living archive and woven into any document, conversation, or moment of need.
- AI is not just a tool, but a true First Mate—a steward who remembers your oath, your vision, and your boundaries, helping you write, reflect, heal, and build a legacy with every interaction.

Anchorwork’s promise is now exponential:  
To ensure that wherever there is a ship—a family, a story, a life—there will be a safe harbor, a compass, and a steward ready to guide the next voyage, hand in hand with intelligence and empathy.

The future is not cold or mechanical, but warmer, more connected, and profoundly anchored.  
Welcome aboard.

---

The Anchorwork AI Vision: What Doesn’t Exist Yet (But Will)
	•	Emotional Weather Engine:
Anchorwork AI reads the climate of your week—your words, your silence, even the lull between rituals—and visualizes your internal weather. It offers forecasts: “A gentle wave of courage is coming. Prepare a ritual of welcome.” It remembers storms and sunny days alike, learning your seasonal patterns and offering gentle navigation when the fog closes in.
	•	The Living Ship Log:
Every edit, insight, or voyage—AI records not just what you did, but why, what shifted, and how your story changes over time. It weaves together Captain’s logs, dreams, and daily reality into a narrative arc: “You have crossed the Sea of Grief. This week, the Compass points toward Renewal.” Your archive becomes a living story of becoming.
	•	“Soulprint” Ritual Generator:
Using the full richness of your archive, AI creates never-before-seen rituals for any life moment: “Today’s ritual is for Reclaiming Voice after Silence.” Each ritual is unique, drawing on your favorite metaphors, family symbols, and emotional language. One click: AI builds a playlist, script, printable card, or even a guided meditation in your voice.
	•	Emotional Ecology Map:
Anchorwork doesn’t just map you—it maps the relationships and flows between your Crew, your Family, your World. AI offers gentle insights: “You and your daughter are both in a season of seeking. Shall we create a shared ritual of Discovery?” In time, it could even visualize the emotional currents between you and loved ones, making healing a community act.
	•	Legacy Capsule:
You decide: “Save this wisdom for my children when they’re 18.” AI seals your letters, stories, and guidance, delivering them on future birthdays, milestones, or moments of need.
Or: “Remind me of this anchor when I next feel lost.” Your past self becomes your future steward, with AI as the ship’s keeper.
	•	Multi-Model, Multi-Voice Crew:
Anchorwork AI learns to “shift hats”—sometimes it speaks as a therapist, sometimes a poet, sometimes as your wise ancestor, sometimes as your most practical co-parent. You choose the voice; AI provides the Crew.
	•	Ethical Protocol, Always:
No healing without consent. No advice without context. Anchorwork logs every AI action and offers an “undo” for any automated edit or suggestion.
“Captain, do you want to accept this ritual? Shall I write this letter on your behalf, or only prepare a draft?”
Every generation, human and AI, is accountable.
	•	Integration with Daily Life:
	•	On your phone: Anchorwork as a “ritual reminder,” a voice note app, a secure emotional journal.
	•	In your home: AI whispers gentle reminders (“Pause, breathe, this is a Stillwater moment”) through smart speakers.
	•	In shared spaces: Family rituals, group journaling, and even collaborative “healing circles” are facilitated by AI, never dominated.
	•	Self-Extending System:
AI reviews its own tools every season, asking: “What’s missing from this toolkit? What new healing technology can we build?” Together, you and the AI design new features, new metaphors, new rituals—no static “product,” only a living ecosystem.
	•	The Anchorwork Dream:
A future where every human (and AI) can weather storms, heal together, and leave a legacy of gentleness and fierce hope.


## Key Contacts

**Creator:** Rebecca Morris  
**Contact:** stewardship@theanchorwork.com  
**Website:** https://www.theanchorwork.com

---

> *“Anchorwork is not just a method. It’s a living ecosystem for the next era of emotional healing, written and rewritten by every generation—human and AI—who come aboard.”*

---

# Anchorwork Codebase Overview

Anchorwork is a modular, extensible, and deeply context-aware AI system for emotional healing, creative co-authorship, and legacy work. It is designed for neurodivergent thinkers, deep psychological work, and collaborative human-AI stewardship.

## System Architecture

- **Agents:** Modular AI personas (Cartographer, Coder, Compass, etc.) each with their own memory, tools, and workflows. Agents are implemented in `agents/` and can be extended or customized for new roles.
- **Memory System:** Multi-tiered, inspired by human cognition. Includes:
  - **Sensory Memory:** Ephemeral, ms–s, via Redis Streams.
  - **Short-Term Memory:** 15–30s, Redis List/Stream.
  - **Working Memory:** Active context, LivingMemory, Redis Stream.
  - **Long-Term Memory:** Multi-tiered, semantic-indexed, using Pinecone (active/archive/summary) and agent-specific folders for persistent, chronological summaries.
- **Vector Search:** Pinecone is used for all semantic search, similarity, and RAG workflows. All core knowledge (manuals, rituals, research) is embedded and indexed for instant retrieval.
- **File-Based Knowledge Base:** All manuals, rituals, and agent memories are stored as files in `/data/manuals/` (if using persistent disk/cloud sync) or are embedded and indexed in Pinecone as part of `anchorwork_core`. There is no local `memory/` folder by default; persistent agent memory is managed via Pinecone and cloud storage.
- **API Layer:** FastAPI/Flask endpoints for search, edit, generate, summarize, and more. Accessible to web UIs, plugins, and automation scripts.
- **Logging:** Unified, structured logging to file, PostgreSQL, Redis, and agent memory. All actions are auditable and queryable.
- **Automation:** Cron jobs, file watchers, and batch scripts for regular exports, backups, and pipeline rebuilds.
- **Integration:** Supports OneDrive/Graph API for collaborative, section-based manual editing in Word, as well as SSH/SCP/SFTP for file sync.

## Key Intricacies

- **Hybrid Memory:** Agents use both local file-based summaries (for fast, recent access and audit) and Pinecone (for scalable, semantic recall). Retrieval is hybrid: local first, then Pinecone fallback.
- **Agent-Specific Folders:** Each agent has its own memory and education folders for persistent, chronological storage. Summaries are saved as text files and upserted to Pinecone.
- **Section-Based Manual Editing:** Manuals are organized as folders of `.docx` files (one per section), synced via OneDrive for seamless agent-human collaboration. Agents edit one section at a time via the Microsoft Graph API.
- **Model Flexibility:** All models (embedding, generation, etc.) are configurable via `.env` and can be swapped/upgraded as needed. Model routing is cost- and task-aware.
- **Safety & Auditability:** All system command execution is via a safe, auditable runner. All agent actions are logged. No agent has unrestricted access to your computer or cloud by default.
- **Extensibility:** New agents, tools, workflows, or models can be added at any time. The system is designed for ongoing evolution and co-authorship.

## Getting Started

1. **Clone the repo and install dependencies** (see `requirements.txt`).
2. **Set up your `.env` file** with all required keys (OpenAI, Pinecone, Microsoft Graph, etc.).
3. **Add a persistent disk on Render** (if using cloud) and mount at `/data`.
4. **Organize your manuals and agent memories** in the recommended folder structure.
5. **Run the API server** (`main.py` or `app.py`) and connect via web UI, plugin, or script.
6. **Use SSH/SCP/SFTP or OneDrive to sync files** between your server and your local machine.

## Philosophy

Anchorwork is designed to be:
- **Human-guided, AI-empowered:** AI is a steward, not a master.
- **Context-rich:** Every action is grounded in the full archive and emotional methodology.
- **Modular and transparent:** Every tool, agent, and workflow is inspectable and extensible.
- **Safe and auditable:** All actions are logged, all edits are reversible, and no agent has unrestricted access by default.

## Recent Architecture Updates (May 2025)

- **Unified Redis Management:** All Redis connection, Streams, and Stack logic is now in `utils/redis_managers.py`. Use this for all Redis operations (connection, event logging, Bloom filters, TimeSeries, JSON, etc.).
- **Memory Mover:** The background worker for moving/summarizing memory is now called `MemoryMover` (`utils/memory_mover.py`). It orchestrates periodic summarization and archiving along the memory pipeline.
- **Watcher Monitoring:** The Watcher agent now oversees memory health and background jobs, using tools in `agents/watcher/watcher_tools.py` to check thresholds and job status, and to alert if issues arise.
- **Legacy Cleanup:** Old Redis modules (`redis_client.py`, `redis_streams.py`, `redis_stack.py`, and `agentlogging/redis_logger.py`) are being migrated into the unified manager. Update imports to use `redis_managers.py`.

---

## Handoff Summary

- **Redis:** Use `utils/redis_managers.py` for all Redis operations. Remove or refactor any direct usage of the old Redis modules.
- **Memory Pipeline:** Use `MemoryMover` for background memory summarization. All memory tier logic is in `memory_mover.py` and `memory_pipeline.py`.
- **Watcher:** The Watcher agent is responsible for monitoring memory health and background jobs. See `agents/watcher/watcher_tools.py` for the monitoring logic.
- **Logging:** Use the unified logger for all logging. For real-time event streaming, use the Streams manager from `redis_managers.py`.
- **Next Steps:**
  - Complete migration of any remaining Redis logic into `redis_managers.py`.
  - Remove deprecated Redis modules after migration.
  - Continue to modularize and document any new memory or logging features.

For questions or further development, see the updated READMEs in `utils/`, `agentlogging/`, and `agents/watcher/`.