# Virtual Contributor Engine Generic Constitution

## Core Principles

### I. Generic LLM Proxy Integrity

The engine MUST faithfully relay user queries to the configured LLM provider and
return responses without modification beyond formatting. The system MUST NOT
inject hidden instructions, alter user intent, or filter responses beyond the
persona-defined system prompt. When the LLM provider is unreachable, the system
MUST return a clear unavailability message rather than fabricate a response.

**Rationale**: The generic engine is a pass-through to configurable LLM providers.
Users and platform operators trust that the engine transparently mediates
conversations without hidden manipulation.

### II. Async Message-Driven Architecture

All request handling MUST be fully asynchronous, using RabbitMQ as the message
broker. The engine MUST NOT expose synchronous HTTP endpoints or block the event
loop. New features MUST integrate with the existing `aio-pika` message consumer
pattern and the `alkemio-virtual-contributor-engine` base library.

**Rationale**: The engine runs as one of potentially many virtual contributors
within the Alkemio platform. Async message-driven design ensures the system
scales horizontally and integrates cleanly with the platform's event bus.

### III. Conversation Context Management

The engine MUST correctly maintain conversation history within configured bounds
(`HISTORY_LENGTH`). History condensation via the rephrasing chain MUST preserve
user intent while adding context. The system MUST gracefully handle conversations
with no history (initial interaction) and long histories (truncation).

**Rationale**: Conversation coherence is critical for user experience. Incorrect
history handling leads to confusing responses and lost context, directly
impacting the quality of the virtual contributor persona.

### IV. Observability

All LLM interactions MUST use structured logging at appropriate levels. New
features MUST NOT degrade existing logging coverage. Error conditions MUST
produce actionable log entries with sufficient context for debugging.

**Rationale**: LLM-based systems are inherently non-deterministic. Without
observability, diagnosing quality regressions, latency issues, or incorrect
answers becomes impractical in production.

### V. Security & Prompt Integrity

The system MUST enforce prompt boundaries that prevent user input from
overriding system instructions or persona definitions. The combined prompt
MUST constrain the LLM to respond only within the defined persona scope.
New prompt modifications MUST be reviewed for injection vulnerabilities.
Sensitive configuration (API keys, credentials) MUST be loaded from environment
variables or secrets — never hardcoded.

**Rationale**: The engine processes untrusted user input and passes it to an
LLM. Without prompt integrity enforcement, adversarial inputs could leak system
prompts or cause the persona to behave outside its intended role.

### VI. Test Coverage

All production code MUST maintain a minimum of 90% test coverage as measured by
line coverage (`pytest --cov`). New features and bug fixes MUST include tests
that cover the changed code paths. Coverage MUST NOT decrease on any pull
request — if a PR reduces coverage below the 90% threshold, it MUST be blocked
until tests are added. Critical paths (history condensation, prompt assembly,
model invocation) SHOULD target 95%+ coverage.

**Rationale**: The engine relies on non-deterministic LLM interactions and
async message processing, making untested code paths high-risk for silent
regressions. A strict coverage floor ensures that refactors, dependency
upgrades, and prompt changes are validated against known-good behavior.

## Technology Stack Constraints

- **Language**: Python 3.12+
- **LLM Provider**: OpenAI (via LangChain, configurable per-request via `external_config`)
- **Orchestration**: LangChain for prompt template compilation and model invocation
- **Base Library**: `alkemio-virtual-contributor-engine` v0.8.0 — engine lifecycle,
  message handling, and shared types
- **Containerization**: Docker, deployed on Kubernetes
- **License**: EUPL-1.2

Changes to the core technology stack (LLM provider, orchestration framework,
or base library) MUST be treated as a major architectural decision requiring
explicit justification and a migration plan.

## Development Workflow

- All changes MUST be developed on feature branches and merged via pull request
  into `develop`.
- Version bumps follow semantic versioning (MAJOR.MINOR.PATCH).
- The `Dockerfile` MUST remain buildable and produce a working container after
  every merge to `develop`.
- Environment configuration MUST be documented in `.env.default` with sensible
  placeholder values for all required variables.
- Dependencies are managed via Poetry (`pyproject.toml` / `poetry.lock`).
  Dependency additions or upgrades MUST not break the existing lock file
  without explicit intent.
- CI MUST run linting (`flake8`) and tests with coverage (`pytest --cov`) on
  every push and pull request. CI failures MUST block merges.

## Governance

This constitution defines the non-negotiable principles for the
virtual-contributor-engine-generic project. All feature specifications,
implementation plans, and code changes MUST be evaluated against these
principles.

**Amendment procedure**:
1. Propose the change with rationale in a pull request modifying this file.
2. Document the version bump (MAJOR for principle removal/redefinition,
   MINOR for new principles or material expansion, PATCH for clarifications).
3. Update the Sync Impact Report at the top of this file.
4. Verify dependent templates still align with updated principles.

**Compliance**: All PRs and reviews SHOULD verify that changes do not violate
the core principles. The Constitution Check section in implementation plans
MUST reference these principles by number.

**Version**: 1.1.0 | **Ratified**: 2026-03-27 | **Last Amended**: 2026-03-27
