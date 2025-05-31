# Anchorwork Agents Overview

The `agents/` folder contains all modular AI personas (agents) that power the Anchorwork system. Each agent is designed for a specific role, workflow, or psychological function, but all share a common architecture for extensibility, memory, and tool use.

---

## Folder Structure

- `base_agent.py` — The abstract base class and core logic for all agents.
- `alchemist/`, `cartographer/`, `coder/`, `compass/`, `firstmate/`, `researcher/`, `watcher/` — Subfolders for each specialized agent, containing their unique tools, workflows, and memory extensions.
- `__init__.py` — For package/module imports.

---

## Agent Architecture

### **BaseAgent (base_agent.py)**
- **Purpose:** Provides the foundational logic for all agents, including:
  - Identity and profile management
  - Memory pipeline integration (short-term, working, long-term)
  - Education ingestion and self-reflection
  - Logging and event tracking
  - Tool registration and permission management
  - Model switching (via ModelSwitchingMixin)
- **Key Methods:**
  - `boot_up()`: Loads identity, notes, education, and memory context.
  - `periodic_education_ingestion()`: Background thread for ongoing learning.
  - `self_reflect()`: Generates agent-specific summaries and next steps.
  - `append_dynamic_identity_note()`: Adds new notes to agent identity.
  - `log_event()`: Unified logging for all agent actions.
  - `system_runner`: Safe system command execution for agent workflows.
- **Extensibility:**
  - Agents inherit from `BaseAgent` and can override or extend any method.
  - New tools, workflows, or memory strategies can be added per agent.

### **Agent Memory**
- Each agent integrates with the `memory_pipeline` for multi-tiered memory (sensory, STM, working, LTM).
- Summaries and education are stored in agent-specific folders or upserted to Pinecone for semantic recall.
- Agents can retrieve, summarize, and reflect on their own history for context-aware reasoning.

---

## Specialized Agents

Each agent subfolder contains:
- **Agent definition** (e.g., `cartographer.py`, `coder.py`): Implements the agent’s persona, tools, and workflows.
- **Tools and utilities**: All shared tools and agent-specific tools are located in the `tools/` folder. Each agent imports and registers the tools it needs from there (e.g., `tools/cartographer_tools.py`, `tools/coder_tools.py`, etc.).
- **Memory extensions**: Custom memory handling or education ingestion as needed.

### **Example Agents**
- **Cartographer:** Structure, outline, and map knowledge; guides manual writing and context navigation.
- **Coder:** Code generation, static analysis, and automation; integrates with static_analysis and system_runner.
- **Compass:** Values alignment, ethical scenario analysis, and affirmation; supports reflection and decision-making.
- **Firstmate, Alchemist, Watcher, Researcher:** Each with unique tools and workflows for emotional support, ritual, research, or monitoring.

---

## Adding a New Agent

1. Create a new subfolder (e.g., `agents/newagent/`).
2. Inherit from `BaseAgent` and implement your agent’s persona, tools, and workflows.
3. Register any new tools or memory strategies.
4. Document the agent’s purpose and usage in a README or docstring.

---

## Best Practices
- Always inherit from `BaseAgent` for consistency and access to core features.
- Use the memory pipeline for all agent memory operations.
- Register new tools and workflows in the agent’s subfolder.
- Log all important actions using the unified logging system.
- Keep agent logic modular and extensible for future growth.

---

## Coder Agent: Safe Code Update Workflow

The Coder agent now follows a modern, production-grade workflow for all code changes:

1. **Branching:** All changes are made in a new feature branch (never directly to main).
2. **Pull Request (PR):** The agent pushes the branch and opens a PR on GitHub.
3. **Automated CI/CD:** The PR triggers automated tests (CI) via GitHub Actions or your configured CI system.
4. **CI Status Checks:** The agent can wait for all CI checks to pass before proceeding.
5. **Auto-Merge:** If enabled, the agent will automatically merge the PR after all checks pass.
6. **Auditability:** All actions are logged and auditable; no code is merged without passing tests.

### Example Usage

```python
agent.safe_code_update(
    repo="yourusername/yourrepo",
    code={"agents/coder/coder.py": "new code here"},
    message="Refactor coder agent logic",
    wait_for_ci=True,        # Wait for CI to pass
    auto_merge=True          # Auto-merge after CI passes
)
```

### Best Practices
- Always use the safe code update workflow for agent-driven changes.
- Review PRs on GitHub if human/agent review is desired before merging.
- Ensure your CI/CD is configured to run tests on every PR.
- The agent requires a GitHub token with repo and PR permissions (set in `.env` as `GITHUB_TOKEN`).

For more details, see the implementation in `agents/coder/coder.py` and `tools/coder_tools.py`.

---

For more details, see `base_agent.py`, the `utils/README.md` for memory and backend architecture, the `tools/README.md` for shared and agent-specific tools, and each agent’s subfolder for specialized workflows.
