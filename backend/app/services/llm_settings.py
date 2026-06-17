from __future__ import annotations

import os
from dataclasses import dataclass

from app.schemas.settings import LLMSettingsStatus, LLMSettingsUpdate


@dataclass
class RuntimeLLMSettings:
    enabled: bool = False
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"

    def __post_init__(self) -> None:
        env_key = os.getenv("LLM_API_KEY", "")
        env_base_url = os.getenv("LLM_BASE_URL", self.base_url)
        env_model = os.getenv("LLM_MODEL", self.model)
        self.api_key = env_key
        self.base_url = env_base_url.rstrip("/")
        self.model = env_model
        self.enabled = bool(env_key)

    def update(self, payload: LLMSettingsUpdate) -> LLMSettingsStatus:
        self.enabled = payload.enabled
        self.base_url = payload.base_url.rstrip("/")
        self.model = payload.model
        if payload.api_key is not None:
            self.api_key = payload.api_key.strip()
        return self.status()

    def status(self) -> LLMSettingsStatus:
        return LLMSettingsStatus(
            enabled=self.enabled,
            has_api_key=bool(self.api_key),
            base_url=self.base_url,
            model=self.model,
            mode="llm" if self.enabled and self.api_key else "heuristic",
        )


runtime_llm_settings = RuntimeLLMSettings()

