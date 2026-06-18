from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepCoffee Backend"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "deepcoffee_user"
    POSTGRES_PASSWORD: str = "deepcoffee_password"
    POSTGRES_DB: str = "deepcoffee"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+pg8000://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    BACKEND_CORS_ORIGIN_REGEX: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    LOYAL_CUSTOMER_MIN_ORDERS: int = 10
    LOYAL_CUSTOMER_PERIOD_DAYS: int = 30

    FACE_RECOGNITION_THRESHOLD: float = 0.80
    INSIGHTFACE_MODEL_NAME: str = "buffalo_l"
    INSIGHTFACE_MODEL_ROOT: str = "storage/models/insightface"
    INSIGHTFACE_DET_SIZE: int = 640
    RECOGNITION_THROTTLE_MS: int = 3000
    GREETING_COOLDOWN_MINUTES: int = 5
    RECOGNITION_DUPLICATE_WINDOW_SECONDS: int = 30
    DASHBOARD_EVENT_BUFFER_SIZE: int = 100
    AUTO_CREATE_TABLES: bool = True
    FACE_EMBEDDING_SIZE: int = 64
    YOLO_MODEL_PATH: Optional[str] = None
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

    @property
    def LOYALTY_INVOICE_REQUIRED(self) -> int:
        return self.LOYAL_CUSTOMER_MIN_ORDERS

    @property
    def LOYALTY_DAYS_WINDOW(self) -> int:
        return self.LOYAL_CUSTOMER_PERIOD_DAYS

    @property
    def FACE_MATCH_THRESHOLD(self) -> float:
        return self.FACE_RECOGNITION_THRESHOLD

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
