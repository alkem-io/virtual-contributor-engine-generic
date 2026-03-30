# Research: speckit-init

**Feature Branch**: `001-speckit-init`
**Date**: 2026-03-27

## 1. CI Pipeline Pattern

**Decision**: Mirror expert engine's `ci.yml` (checkout -> setup-python 3.12 -> install poetry -> install deps -> flake8 -> pytest --cov).

**Rationale**: Consistency across VC engines. Both engines share the same base library, language, and dependency manager. A uniform CI pipeline reduces cognitive overhead when switching between repositories and ensures the same quality gates apply everywhere.

**Alternative considered**: Pre-commit hooks only -- rejected because CI provides an authoritative coverage gate that cannot be bypassed locally. Pre-commit hooks are complementary but not sufficient as the sole enforcement mechanism.

## 2. Test Framework

**Decision**: pytest + pytest-cov with mocked LLM calls.

**Rationale**: Standard Python testing framework, matches expert engine. pytest's fixture system and assertion introspection make tests more readable and maintainable than alternatives.

**Alternative considered**: unittest -- rejected, less ergonomic. No fixture injection, verbose assertion methods, and class-based test organization adds boilerplate without benefit for this codebase.

## 3. Flake8 Configuration

**Decision**: max-line-length=100, matching expert engine's `.flake8`.

**Rationale**: Consistency across VC engine repositories. 100-character lines are a practical balance between readability and modern screen widths.

**Alternative considered**: ruff -- possible future migration but flake8 matches existing repos. Switching linters would introduce unnecessary divergence from the expert engine without immediate benefit.

## 4. Test Coverage Strategy

**Decision**: Mock OpenAI/LangChain calls at the model boundary. Test config loading, history condensation logic, prompt assembly, error handling.

**Rationale**: External API calls are non-deterministic and require credentials. Mocking at the adapter boundary isolates testable logic from external dependencies, enabling fast and reliable CI runs.

**Key test boundaries**:
- `config.py`: Test environment variable loading with various combinations
- `ai_adapter.py`: Mock the LangChain model invocation, test history condensation and prompt assembly
- `main.py`: Test handler registration and message processing with mocked adapter
- `models.py`: Test model factory returns correct model types for given configurations

## 5. Pre-existing Changes

**Decision**: Include all uncommitted changes (.env.default, Dockerfile, pyproject.toml, poetry.lock) in this branch.

**Rationale**: These are prerequisite infrastructure changes that should ship together. They represent the Python 3.12 migration, base library upgrade to v0.8.0, and container simplification -- all of which are foundational for the CI pipeline and test infrastructure being added by this feature.

**Changes included**:
- `.env.default`: Fixed typo (ANGCHAIN -> LANGCHAIN), removed LOCAL_PATH, added RabbitMQ result queue and event bus settings
- `Dockerfile`: Switched to python:3.12-slim-bookworm, removed distroless runtime, simplified build
- `pyproject.toml`: Python ^3.12, removed langchain-community, upgraded base lib to v0.8.0
- `poetry.lock`: Regenerated for dependency changes
