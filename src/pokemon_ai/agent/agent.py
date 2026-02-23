"""Core agent loop orchestration."""

import asyncio
import logging

from pokemon_ai.agent.context import format_state_message
from pokemon_ai.agent.history import ActionHistory
from pokemon_ai.agent.prompts import get_system_prompt
from pokemon_ai.config import settings
from pokemon_ai.emulator.buttons import Button
from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.llm.base import LLMProvider, Message
from pokemon_ai.llm.tools import TOOLS
from pokemon_ai.state.state_manager import StateManager

logger = logging.getLogger(__name__)

BUTTON_MAP = {name: btn for name, btn in [(b.name, b) for b in Button]}


class Agent:
    """The core Pokemon AI agent."""

    def __init__(
        self,
        provider: LLMProvider,
        client: EmulatorClient,
    ):
        self.provider = provider
        self.client = client
        self.state_manager = StateManager(client)
        self.history = ActionHistory(max_size=settings.max_history)
        self._running = False

    async def step(self) -> None:
        """Execute a single agent step: observe -> think -> act."""
        # 1. Observe: read game state
        state = await self.state_manager.get_state()
        logger.info(f"Mode: {state.mode.value} | Party: {len(state.party)}")

        # 2. Think: send state to LLM
        system_prompt = get_system_prompt(state.mode.value)
        history_str = self.history.format_for_prompt()
        state_message = format_state_message(state, history_str)

        messages = [
            Message(role="system", content=system_prompt),
            state_message,
        ]

        response = await self.provider.chat(
            messages=messages,
            tools=TOOLS,
            temperature=0.7,
        )

        # Log LLM reasoning
        if response.content:
            logger.info(f"LLM says: {response.content[:200]}")

        # 3. Act: execute tool calls
        if response.has_tool_calls:
            for tc in response.tool_calls:
                await self._execute_tool(tc.name, tc.arguments)
        else:
            # No tool call — press A as default (advance dialogue/confirm)
            logger.warning("No tool call from LLM, pressing A as fallback")
            await self.client.press_button(Button.A)
            self.history.add("press_button A (fallback)")

        # Check if stuck
        if self.history.is_stuck():
            logger.warning("Agent appears stuck — injecting random movement")
            import random
            direction = random.choice([Button.UP, Button.DOWN, Button.LEFT, Button.RIGHT])
            await self.client.press_button(direction)
            self.history.add(f"press_button {direction.name} (unstuck)")

    async def _execute_tool(self, name: str, args: dict) -> None:
        """Execute a tool call from the LLM."""
        if name == "press_button":
            button_name = args.get("button", "A").upper()
            button = BUTTON_MAP.get(button_name)
            if button is not None:
                await self.client.press_button(button)
                self.history.add(f"press_button {button_name}")
                logger.info(f"Pressed: {button_name}")
            else:
                logger.error(f"Unknown button: {button_name}")

        elif name == "press_sequence":
            buttons_raw = args.get("buttons", [])
            buttons = []
            for b in buttons_raw:
                btn = BUTTON_MAP.get(b.upper())
                if btn is not None:
                    buttons.append(btn)
            if buttons:
                await self.client.press_sequence(buttons)
                seq_str = " ".join(b.upper() for b in buttons_raw)
                self.history.add(f"press_sequence {seq_str}")
                logger.info(f"Sequence: {seq_str}")

        elif name == "wait":
            frames = args.get("frames", 30)
            wait_seconds = frames / 60.0
            await asyncio.sleep(wait_seconds)
            self.history.add(f"wait {frames} frames")
            logger.info(f"Waited {frames} frames")

        else:
            logger.error(f"Unknown tool: {name}")

    async def run(self) -> None:
        """Main agent loop."""
        self._running = True
        logger.info(f"Agent starting with provider: {self.provider.name()}")

        step_count = 0
        while self._running:
            try:
                await self.step()
                step_count += 1
                logger.info(f"Step {step_count} complete")
                await asyncio.sleep(settings.action_delay)
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")
                self._running = False
            except Exception as e:
                logger.error(f"Error in step {step_count}: {e}", exc_info=True)
                await asyncio.sleep(2.0)  # back off on errors

    def stop(self) -> None:
        self._running = False
