from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase AI"
    debug: bool = True

    backend_host: str = "127.0.0.1"
    backend_port: int = 8001
    backend_url: str = "http://127.0.0.1:8001"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    use_mock_ai: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_settings():
    return Settings()