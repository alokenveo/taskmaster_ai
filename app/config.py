from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Gemini
    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()