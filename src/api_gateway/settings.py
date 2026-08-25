"""
Fail-fast configuration. No default fallback values for anything that would let the
app silently run against a fake/no-op backend — see ARCHITECTURE.md rule 6.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    redis_url: str
    gemini_api_key: str


REQUIRED_ENV_VARS = [
    "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "REDIS_URL", "GEMINI_API_KEY",
]


def load_settings() -> Settings:
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill in real values — the app will not "
            f"start with fake/default config."
        )
    return Settings(
        neo4j_uri=os.environ["NEO4J_URI"],
        neo4j_user=os.environ["NEO4J_USER"],
        neo4j_password=os.environ["NEO4J_PASSWORD"],
        redis_url=os.environ["REDIS_URL"],
        gemini_api_key=os.environ["GEMINI_API_KEY"],
    )
