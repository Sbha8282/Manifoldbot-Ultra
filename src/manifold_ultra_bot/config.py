from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    MANIFOLD_BOT_USERNAME: str = Field("ManifoldUltraBot", description="The bot's public username")
    TARGET_CREATOR: str = Field("MikhailTal", description="Only participate in markets created by this user")
    MANIFOLD_BASE_URL: str = Field("https://manifold.markets", description="Base URL for Manifold")
    MANIFOLD_SESSION_COOKIE: str | None = Field(None, description="Session cookie value for placing bets; optional")
    OPENAI_API_KEY: str | None = Field(None, description="OpenAI API key for optional LLM estimates")
    DRY_RUN: bool = Field(True, description="If true, do not place real bets; only simulate")
    MAX_MARKETS_PER_RUN: int = Field(50, description="Max markets to fetch per run")

    class Config:
        env_file = ".env"


settings = Settings()
