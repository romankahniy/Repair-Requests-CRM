from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True,
    )

    ENVIRONMENT: str = Field(default="dev", description="Environment: dev, prod")

    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="repair_crm_db", description="Database name")
    POSTGRES_USER: str = Field(default="postgres", description="Database user")
    POSTGRES_PASSWORD: str = Field(default="", description="Database password")

    JWT_SECRET_KEY: str = Field(..., description="Secret key for JWT token generation")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=24, description="Token expiration time in hours")

    PROJECT_NAME: str = Field(default="Repair Requests CRM", description="Project name")

    @computed_field
    @property
    def database_url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "prod"


settings = Settings()
