from fastapi import APIRouter

from app.schemas.settings import LLMSettingsStatus, LLMSettingsUpdate
from app.services.llm_settings import runtime_llm_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/llm", response_model=LLMSettingsStatus)
def get_llm_settings() -> LLMSettingsStatus:
    return runtime_llm_settings.status()


@router.put("/llm", response_model=LLMSettingsStatus)
def update_llm_settings(payload: LLMSettingsUpdate) -> LLMSettingsStatus:
    return runtime_llm_settings.update(payload)

