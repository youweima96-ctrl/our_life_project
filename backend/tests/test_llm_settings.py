from app.schemas.settings import LLMSettingsUpdate
from app.services.llm_settings import RuntimeLLMSettings


def test_llm_settings_status_never_returns_api_key():
    settings = RuntimeLLMSettings()
    status = settings.update(
        LLMSettingsUpdate(
            enabled=True,
            api_key="test-secret-key",
            base_url="https://api.example.com/v1",
            model="demo-model",
        )
    )

    assert status.enabled is True
    assert status.has_api_key is True
    assert status.base_url == "https://api.example.com/v1"
    assert status.model == "demo-model"
    assert not hasattr(status, "api_key")

