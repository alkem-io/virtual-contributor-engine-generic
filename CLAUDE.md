# virtual-contributor-engine-generic Development Guidelines

## Project Overview

AI-powered generic LLM engine for the Alkemio platform. Receives questions via RabbitMQ, rephrases them using conversation history for context, sends to a configurable LLM provider (currently OpenAI via LangChain), and returns responses. Acts as a pass-through proxy with persona-defined system prompts.

## Active Technologies
- Python 3.12+ + langchain, langchain-openai, openai, aio-pika 9.5.7, alkemio-virtual-contributor-engine v0.8.0 (001-speckit-init)
- N/A (stateless LLM proxy) (001-speckit-init)

- Python 3.12+
- alkemio-virtual-contributor-engine v0.8.0 (base library)
- aio-pika 9.5.7 (RabbitMQ async client)
- LangChain / langchain-openai (LLM orchestration)
- OpenAI API (configurable per-request via external_config)

## Project Structure

```text
.
├── ai_adapter.py        # Core invocation logic (history condensation + LLM call)
├── config.py            # Environment variable loading (Env dataclass)
├── main.py              # Entry point, request handler, engine bootstrap
├── models.py            # LLM model factory
├── prompts.py           # Prompt templates (condenser system prompt)
├── pyproject.toml       # Dependencies (Poetry)
├── Dockerfile           # Container build
├── .env.default         # Environment variable documentation
└── .github/workflows/   # CI/CD pipelines
```

## Commands

```bash
# Install dependencies
poetry install

# Run the engine
poetry run python main.py

# Run linting
poetry run flake8
```

## Code Style

- Use `setup_logger(__name__)` for all logging — never `print()`/`pprint()`
- All async request handling via aio-pika — no sync HTTP endpoints
- External dependencies (LLM provider) are configured via environment variables
- LLM model selection is per-request via `input.engine` and `input.external_config`

## Key Patterns

- `Input` → history condensation (rephrase with context) → LLM invocation → `Response`
- System prompts from `input.prompt` are prepended as `SystemMessage`
- History is truncated to `HISTORY_LENGTH` most recent messages
- Model is resolved per-request from `input.engine` + `input.external_config.api_key`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Recent Changes
- 001-speckit-init: Added Python 3.12+ + langchain, langchain-openai, openai, aio-pika 9.5.7, alkemio-virtual-contributor-engine v0.8.0
