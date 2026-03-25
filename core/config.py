import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepCoffee Backend"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "deepcoffee_user"
    POSTGRES_PASSWORD: str = "deepcoffee_password"
    POSTGRES_DB: str = "deepcoffee"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+pg8000://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32) # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Loyalty rules
    LOYALTY_INVOICE_REQUIRED: int = 10
    LOYALTY_DAYS_WINDOW: int = 30

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
