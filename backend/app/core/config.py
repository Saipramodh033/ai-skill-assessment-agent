import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    cors_origins: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173"),
    )
