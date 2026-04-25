import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    cors_origins: str = "http://localhost:5173"
    gemini_retry_attempts: int = 3
    gemini_retry_base_delay_ms: int = 800
    assessment_skill_limit: int = 1
    questions_per_skill: int = 2
    session_db_path: str = "data/sessions.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173"),
        gemini_retry_attempts=int(os.getenv("GEMINI_RETRY_ATTEMPTS", "3")),
        gemini_retry_base_delay_ms=int(os.getenv("GEMINI_RETRY_BASE_DELAY_MS", "800")),
        assessment_skill_limit=int(os.getenv("ASSESSMENT_SKILL_LIMIT", "1")),
        questions_per_skill=int(os.getenv("QUESTIONS_PER_SKILL", "2")),
        session_db_path=os.getenv("SESSION_DB_PATH", "data/sessions.db"),
    )
