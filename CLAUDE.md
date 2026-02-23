# Pokemon AI - Development Practices

## Project
AI agent that autonomously plays Pokemon FireRed through mGBA-http emulator API.

## Commands
- `uv run pytest` — run all tests
- `uv run pytest -m "not integration and not llm"` — unit tests only
- `uv run python -m pokemon_ai` — start the agent
- `uv run ruff check src/ tests/` — lint
- `uv run ruff format src/ tests/` — format

## Architecture
- `src/pokemon_ai/emulator/` — mGBA-http client, button inputs, screenshots
- `src/pokemon_ai/memory/` — RAM address constants, Gen III decryption, parsers
- `src/pokemon_ai/state/` — unified GameState, mode detection
- `src/pokemon_ai/llm/` — swappable LLM providers (Ollama, Gemini, Claude, OpenAI)
- `src/pokemon_ai/agent/` — core agent loop, prompts, context formatting
- `src/pokemon_ai/knowledge/` — type chart, moves, pokemon data, progression
- `data/` — JSON data files for knowledge base
- `scripts/` — utility scripts (test_connection, dump_game_state, fetch data)

## Git Workflow
- Commit frequently — small, logical commits after each meaningful unit of work
- Use feature branches for each implementation phase (e.g., `phase-1/project-setup`, `phase-2/ram-parsing`)
- Write clear commit messages describing what and why
- Never commit directly to `main` — always branch and merge
- Run `uv run ruff check src/ tests/` before committing

## Conventions
- Python 3.12, async/await throughout
- Pydantic models for all structured data
- TDD for memory parsing, knowledge lookups, mode detection
- Integration tests marked with `@pytest.mark.integration`
- LLM tests marked with `@pytest.mark.llm`
- Use `httpx.AsyncClient` for all HTTP calls
- Type hints everywhere, ruff for linting/formatting
