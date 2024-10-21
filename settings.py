from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    qdrant_host: str
    qdrant_port: str
    openai_api_key: str
    postgres_test_db: str = "test"

    class Config:
        # last file will overwrite the previous ones
        env_file = [".env.example", ".env"]
        extra = "allow"


settings = Settings()
