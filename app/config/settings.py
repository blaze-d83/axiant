from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings

    Read from .env at root

    Defaults below
    """
    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            )

    sqlite_database_url: str = Field(default="sqlite+aiosqlite:///./notes.db", alias="DATABASE_URL")
    token: str = "quick_notes_token"
    debug: bool = False
    

settings = Settings()
