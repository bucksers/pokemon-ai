"""CLI entry point for the Pokemon AI agent."""

import argparse
import asyncio
import logging
import sys

from pokemon_ai.agent.agent import Agent
from pokemon_ai.config import settings
from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.llm.base import LLMProvider


def create_provider(name: str) -> LLMProvider:
    """Create an LLM provider by name."""
    if name == "ollama":
        from pokemon_ai.llm.ollama import OllamaProvider
        return OllamaProvider()
    elif name == "gemini":
        from pokemon_ai.llm.gemini import GeminiProvider
        if not settings.gemini_api_key:
            print("ERROR: GEMINI_API_KEY not set in .env")
            sys.exit(1)
        return GeminiProvider()
    elif name == "claude":
        from pokemon_ai.llm.claude import ClaudeProvider
        if not settings.anthropic_api_key:
            print("ERROR: ANTHROPIC_API_KEY not set in .env")
            sys.exit(1)
        return ClaudeProvider()
    elif name == "openai":
        from pokemon_ai.llm.openai_provider import OpenAIProvider
        if not settings.openai_api_key:
            print("ERROR: OPENAI_API_KEY not set in .env")
            sys.exit(1)
        return OpenAIProvider()
    else:
        print(f"ERROR: Unknown provider '{name}'")
        print("Available: ollama, gemini, claude, openai")
        sys.exit(1)


async def async_main(provider_name: str) -> None:
    provider = create_provider(provider_name)
    print(f"Using LLM provider: {provider.name()}")

    async with EmulatorClient() as client:
        if not await client.is_connected():
            print("ERROR: Cannot connect to mGBA-http")
            print(f"Make sure mGBA is running with mGBA-http at {settings.mgba_url}")
            sys.exit(1)

        print("Connected to emulator!")
        agent = Agent(provider=provider, client=client)

        try:
            await agent.run()
        except KeyboardInterrupt:
            print("\nStopping agent...")
            agent.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pokemon FireRed AI Agent")
    parser.add_argument(
        "--provider", "-p",
        default="ollama",
        choices=["ollama", "gemini", "claude", "openai"],
        help="LLM provider to use (default: ollama)",
    )
    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(async_main(args.provider))


if __name__ == "__main__":
    main()
