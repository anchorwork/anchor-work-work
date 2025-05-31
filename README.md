# Anchorwork Logging System

## Overview

The Anchorwork logging system provides robust, multi-backend, and queryable logging for all agents, APIs, and system components. It is designed for full auditability, real-time monitoring, and analytics in a multi-agent, memory-centric AI platform.

## Features
- **Unified logging interface**: All logs are routed through `log_event` in `logging/__init__.py`.
- **Multi-backend support**:
  - **File logging** (`file_logger.py`): Persistent, rotating file logs for audit and backup.
  - **PostgreSQL logging** (`db_logger.py`): Structured, queryable logs for analytics, dashboards, and compliance.
  - **Redis Streams logging** (`redis_logger.py`): Real-time event streaming for monitoring and live dashboards.
  - **Memory pipeline logging** (`memory_logger.py`): Logs important events to the agent memory system.
- **Structured event schema**: All logs include timestamp, agent, session, event_type, level, and metadata.
- **Role-based access**: Only authorized agents (e.g., Cartographer) can write to protected indexes like anchorwork core.
- **Retention and health**: Metrics and health checks for all log backends.

## Usage

Import and use the unified logging interface:
```python
from logging import log_event
log_event("event_type", {"message": "Something happened", ...}, agent="coder", session_id="abc123", level="INFO")
```

## Backends
- **file_logger.py**: Rotating file handler for `anchorwork.log`.
- **db_logger.py**: Inserts logs into a PostgreSQL `logs` table with indexes for fast queries.
- **redis_logger.py**: Publishes logs to Redis Streams for real-time consumption.
- **memory_logger.py**: Appends important events to the agent memory pipeline.
- **metrics.py**: Aggregates log metrics and provides health checks.
- **config.py**: Centralizes logging configuration and important event types.

## Event Types
- `event_type`: The type of event (e.g., `memory_append`, `api_call`, `error`, `session_end`).
- `level`: Log level (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `metadata`: Structured JSON with all relevant event data.

## Best Practices
- Always use `log_event` for all logging needs.
- Use structured metadata for easy querying and analytics.
- Only milestone summaries (not full logs) should be upserted to Pinecone for semantic memory.
- Use PostgreSQL for analytics, Redis Streams for real-time, and file logs for backup/audit.

## Extending
- Add new log sinks by implementing a new logger and calling it from `log_event`.
- Use metrics and health checks to monitor log ingestion and backend status.

## Example Query (PostgreSQL)
```sql
SELECT * FROM logs WHERE agent_id = 'coder' AND event_type = 'memory_append' ORDER BY timestamp DESC LIMIT 100;
```

---

## Recent Updates (May 2025)

- **Unified Redis Logging:** Use `utils/redis_managers.py` for all Redis Streams and Stack logging. The old `redis_logger.py` is being migrated.
- **MemoryMover:** Background memory summarization is handled by `MemoryMover`.
- **Watcher Monitoring:** The Watcher agent now monitors memory and job health, alerting on issues.

---

## Handoff Summary

- Use the Streams manager in `redis_managers.py` for real-time event logging.
- Remove or refactor any direct usage of `redis_logger.py` after migration.
- See `README.md` and `utils/README.md` for more details on the new architecture and next steps.

---
For more details, see the code in each logger file or contact the Anchorwork maintainers.