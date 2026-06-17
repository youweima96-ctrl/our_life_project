from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel
import os
from typing import Optional


class Settings(BaseModel):
    app_name: str = "人生项目组 API"
    api_prefix: str = "/api"
    llm_api_key: Optional[str] = None
    prompt_version: str = "event_extract_v1"
    model_name: str = "heuristic-local"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY"),
        model_name=os.getenv("LLM_MODEL", "heuristic-local"),
    )
