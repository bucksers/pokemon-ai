# Pokemon FireRed AI Agent

An AI agent that autonomously plays and beats Pokemon FireRed through the mGBA emulator.

## Motivation

Inspired by a YouTube video showing ChatGPT performing terribly at Pokemon — losing before the 4th gym due to no persistent state, hallucinated game knowledge, and no strategic planning. This project solves those problems with:

- **Structured game state from RAM** — no guessing what's on screen
- **Real knowledge base** — type charts, move data, progression guides
- **Tool use** — the LLM calls functions to press buttons, not free-text
- **Swappable LLM providers** — Ollama (free/local), Gemini Flash (free tier), Claude, OpenAI

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   mGBA +    │◄───►│  Emulator    │◄───►│   State     │
│  mGBA-http  │     │  Client      │     │  Manager    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐     ┌──────▼──────┐
                    │  Knowledge   │────►│   Agent     │
                    │  Base        │     │   Core      │
                    └──────────────┘     └──────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │  LLM        │
                                         │  Provider   │
                                         └─────────────┘
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [mGBA](https://mgba.io/) emulator
- [mGBA-http](https://github.com/niPokemon/mgba-http) scripting plugin
- A Pokemon FireRed ROM (not included)

## Setup

```bash
# Clone and install
git clone <repo-url>
cd pokemon-ai
uv sync

# Configure
cp .env.example .env
# Edit .env with your settings

# Verify emulator connection
uv run python scripts/test_connection.py

# Run the agent
uv run python -m pokemon_ai --provider ollama
```

## Development

```bash
uv run pytest                                    # all tests
uv run pytest -m "not integration and not llm"   # unit tests only
uv run python scripts/dump_game_state.py         # debug game state
uv run ruff check src/ tests/                    # lint
```

## LLM Providers

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| Ollama | Free | Slow | Good | Local install |
| Gemini Flash | Free tier | Fast | Good | API key |
| Claude | Paid | Fast | Best | API key |
| OpenAI | Paid | Fast | Great | API key |
