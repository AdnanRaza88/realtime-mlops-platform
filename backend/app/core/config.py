from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Realtime MLOps Platform"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    kafka_bootstrap: str = "localhost:9092"
    prediction_topic: str = "predictions.features"
    dlq_topic: str = "predictions.dlq"

    online_store_url: str = "redis://localhost:6379/0"
    offline_store_uri: str = "s3://feature-store/offline"
    registry_db: str = "postgresql://localhost/model_registry"

    psi_warning: float = 0.1
    psi_critical: float = 0.2
    drift_interval_sec: int = 300
    performance_drop_threshold: float = 0.03

    metrics_port: int = 9090
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
