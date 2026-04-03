from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

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
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Loyalty rules
    LOYALTY_INVOICE_REQUIRED: int = 10
    LOYALTY_DAYS_WINDOW: int = 30

    # AI/CV and greeting rules
    FACE_MATCH_THRESHOLD: float = 0.82
    GREETING_COOLDOWN_HOURS: int = 12
    RECOGNITION_DUPLICATE_WINDOW_SECONDS: int = 30
    DASHBOARD_EVENT_BUFFER_SIZE: int = 100
    AUTO_CREATE_TABLES: bool = True
    FACE_EMBEDDING_SIZE: int = 64
    YOLO_MODEL_PATH: str | None = None
    STORAGE_DIR: str = "storage"
    FACE_STORAGE_SUBDIR: str = "faces"
    RECOGNITION_STORAGE_SUBDIR: str = "recognitions"

    @property
    def STORAGE_PATH(self) -> Path:
        return Path(self.STORAGE_DIR)

    @property
    def FACE_STORAGE_PATH(self) -> Path:
        return self.STORAGE_PATH / self.FACE_STORAGE_SUBDIR

    @property
    def RECOGNITION_STORAGE_PATH(self) -> Path:
        return self.STORAGE_PATH / self.RECOGNITION_STORAGE_SUBDIR

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
