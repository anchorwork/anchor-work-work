# Anchorwork Audit & Security Checklist

## 1. Security Hardening (Highest Priority)
- [x] Remove all hardcoded secrets (especially DB passwords) from all code.
- [x] Restrict CORS origins in production (no allow_origins=["*"]).
- [x] Implement authentication and authorization for all API endpoints (JWT, etc.).
- [x] Audit all secrets and access controls; document required environment variables.
- [ ] Periodically audit and rotate all secrets (API keys, DB passwords, JWT secrets).
- [ ] Review and restrict database user permissions to least privilege.
- [x] Ensure secrets are only set in environment/config, never in code or version control.

## 2. Logging, Concurrency & Legacy Migration
- [ ] Complete migration from file-based logs/session notes to Redis or DB-backed storage.
- [ ] Refactor any remaining file-based logging to use concurrency-safe methods (atomic writes or DB).
- [ ] Consolidate logging backends; define clear responsibilities and avoid duplication.
- [ ] Unify Redis client/manager usage.
- [ ] Archive or remove legacy/unused files and deprecated code paths.

## 3. Error Handling & Robustness
- [x] Standardize error handling and logging across all modules.
- [ ] Add retries and fallback mechanisms for all external dependencies (LLM, Redis, DB, notifications).
- [x] Replace print statements with structured logging.
- [x] Add exception middleware in FastAPI.
- [x] Add error handling and logging in all background/periodic tasks.
- [ ] Add timeout and error handling for async agent calls.

## 4. Testing & CI/CD
- [ ] Implement missing tests, especially for critical modules and empty test files.
- [ ] Add edge case and error handling tests.
- [ ] Integrate test coverage tools and CI pipelines.
- [ ] Document test running and coverage reporting in README.
- [ ] Regularly update and expand tests as features evolve.

## 5. Code Quality, Modularization & Maintainability
- [ ] Modularize large files.
- [ ] Abstract repeated code patterns (LLM calls, logging) into shared helpers.
- [ ] Add type hints and comprehensive docstrings throughout the codebase.
- [ ] Parameterize agent IDs and configuration in tools for flexibility.
- [ ] Add validation and error handling for config loading.
- [x] Document all config options and environment variables in relevant READMEs.

## 6. Performance & Scalability
- [ ] Replace threading with async for background tasks.
- [ ] Add connection pooling for database access.
- [ ] Optimize Redis usage and cleanup policies for production.

## 7. Documentation & Onboarding
- [x] Update all READMEs as you refactor, including environment variables, config options, and security practices.
- [x] Add a dedicated "Security Considerations" section to the main README.
- [x] Ensure onboarding docs include security, deployment, and operational best practices.

## 8. Monitoring, Alerting & Observability
- [x] Remove any test endpoints (e.g., /sentry-test-error) from production after verification.
- [x] Regularly review Sentry for new issues and set up alerting.
- [ ] Set up advanced monitoring/log forwarding as needed.
- [ ] Complete metrics aggregation in agentlogging/metrics.py.

## 9. Folder-Specific Enhancements
- [ ] Add concurrency-safe logging for crew history.
- [ ] Enhance ritual synthesis with AI or rule-based logic.
- [ ] Extend voting with weighted and consensus features.
- [ ] Add persistent session management for memory APIs.
- [ ] Add unit tests for BaseAgent, config classes, logging modules, and critical utilities.

---

**This checklist is based on the fullauditreview.md and all folder-level audits. Update as you complete each item.**
