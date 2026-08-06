from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ModelStage(str, Enum):
    development = "Development"
    staging = "Staging"
    production = "Production"
    archived = "Archived"


class DriftStatus(str, Enum):
    stable = "Stable"
    watch = "Watch"
    drift = "Drift"


class TriggerReason(str, Enum):
    schedule = "schedule"
    performance = "performance_degradation"
    feature_drift = "feature_drift"
    manual = "manual"


class KPIResponse(BaseModel):
    active_models: int
    avg_latency_ms: float
    drift_alerts: int
    throughput_per_sec: float
    active_models_delta: str
    latency_delta: str
    drift_delta: str
    throughput_delta: str


class PipelineStage(BaseModel):
    name: str
    status: str
    last_run: Optional[str] = None


class EventItem(BaseModel):
    message: str
    timestamp: str
    severity: str = "info"


class OverviewResponse(BaseModel):
    kpis: KPIResponse
    stages: list[PipelineStage]
    events: list[EventItem]
    performance_series: list[dict[str, Any]]


class FeatureDriftItem(BaseModel):
    feature: str
    feature_type: str
    psi: float
    status: DriftStatus
    last_updated: str
    reference_size: int = 0
    current_size: int = 0


class DriftSummary(BaseModel):
    features_monitored: int
    drift_detected: int
    psi_threshold: float
    last_check: str
    items: list[FeatureDriftItem]


class ModelVersionOut(BaseModel):
    name: str
    version: str
    stage: ModelStage
    accuracy: float
    metrics: dict[str, float] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    feature_refs: list[str] = Field(default_factory=list)
    updated_at: str
    created_by: str = "system"
    artifact_uri: str = ""


class ModelListResponse(BaseModel):
    models: list[ModelVersionOut]


class StageTransitionRequest(BaseModel):
    stage: ModelStage
    actor: str = "operator"
    comment: Optional[str] = None


class RetrainRequest(BaseModel):
    model_name: str
    reason: TriggerReason
    details: dict[str, Any] = Field(default_factory=dict)


class RetrainResponse(BaseModel):
    accepted: bool
    model_name: str
    reason: str
    message: str
    requested_at: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    timestamp: str
