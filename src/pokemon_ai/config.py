"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # mGBA-http
    mgba_host: str = "localhost"
    mgba_port: int = 5001

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2-vision"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Agent
    action_delay: float = 1.5  # seconds between actions
    max_history: int = 50  # action history ring buffer size
    log_level: str = "INFO"

    @property
    def mgba_url(self) -> str:
        return f"http://{self.mgba_host}:{self.mgba_port}"


settings = Settings()
