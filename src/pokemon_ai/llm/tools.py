"""Tool definitions for LLM function calling.

These define the actions the AI agent can take in the game.
Uses OpenAI-compatible tool format (works with all providers).
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "press_button",
            "description": "Press a GBA button. Use for movement, menu navigation, and confirming actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "button": {
                        "type": "string",
                        "enum": ["A", "B", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT", "L", "R"],
                        "description": "The button to press. A=confirm/interact, B=cancel/back, START=menu, D-pad=movement.",
                    },
                },
                "required": ["button"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_sequence",
            "description": "Press multiple buttons in sequence. Use for complex navigation like selecting a move in battle (e.g., DOWN then A to pick bottom-left move).",
            "parameters": {
                "type": "object",
                "properties": {
                    "buttons": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["A", "B", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT", "L", "R"],
                        },
                        "description": "Buttons to press in order.",
                    },
                },
                "required": ["buttons"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait without pressing any buttons. Use during animations, transitions, or when the game needs time to process.",
            "parameters": {
                "type": "object",
                "properties": {
                    "frames": {
                        "type": "integer",
                        "description": "Number of frames to wait (60 frames = 1 second). Default 30.",
                        "default": 30,
                    },
                },
            },
        },
    },
]

# Simplified tool list for providers that need a different format
TOOL_NAMES = [t["function"]["name"] for t in TOOLS]
