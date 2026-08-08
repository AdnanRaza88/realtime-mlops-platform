"""Training pipeline stub — produces metrics + artifact URI for registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
import hashlib


@dataclass
class TrainingResult:
    model_name: str
    version: str
    metrics: dict[str, float]
    params: dict[str, Any]
    feature_refs: list[str]
    artifact_uri: str
    trained_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TrainingPipeline:
    def __init__(self, model_name: str, feature_refs: Optional[list[str]] = None) -> None:
        self.model_name = model_name
        self.feature_refs = feature_refs or []
        self.params: dict[str, Any] = {}

    def with_params(self, **params: Any) -> "TrainingPipeline":
        self.params.update(params)
        return self

    def run(self, dataset_uri: str = "offline://default") -> TrainingResult:
        seed = hashlib.sha256(f"{self.model_name}:{dataset_uri}:{self.params}".encode()).hexdigest()
        auc = 0.85 + (int(seed[:4], 16) % 120) / 1000.0
        version = f"1.{int(seed[4:6], 16) % 10}.0"
        return TrainingResult(
            model_name=self.model_name,
            version=version,
            metrics={"val_auc": round(auc, 4), "val_logloss": round(0.35 - (auc - 0.85), 4)},
            params=dict(self.params),
            feature_refs=list(self.feature_refs),
            artifact_uri=f"s3://ml-artifacts/{self.model_name}/{version}/",
        )
