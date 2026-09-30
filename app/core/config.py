from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    PROJECT_NAME: str = "OliveSoft RFP Intelligence API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Ayoub2004"
    POSTGRES_DB: str = "rfp_db"

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    N8N_RESEARCH_WEBHOOK_URL: str = "http://localhost:5678/webhook/prospect-research"
    N8N_PROPOSAL_WEBHOOK_URL: str = "http://localhost:5678/webhook/generate-proposal"


settings = Settings()