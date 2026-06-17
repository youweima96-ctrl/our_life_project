from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LLMSettingsUpdate(BaseModel):
    enabled: bool = True
    api_key: Optional[str] = Field(default=None, max_length=4000)
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"


class LLMSettingsStatus(BaseModel):
    enabled: bool
    has_api_key: bool
    base_url: str
    model: str
    mode: str

