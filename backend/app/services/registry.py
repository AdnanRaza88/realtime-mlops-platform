from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.models.schemas import ModelStage, ModelVersionOut


class ModelRegistry:
    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._seed()

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _seed(self) -> None:
        seeds = [
            {
                "name": "fraud-detector",
                "version": "2.4.1",
                "stage": ModelStage.production,
                "accuracy": 0.942,
                "metrics": {"val_auc": 0.942, "val_f1": 0.871, "val_logloss": 0.214},
                "params": {"learning_rate": 0.03, "max_depth": 8},
                "feature_refs": ["user_features:v3", "txn_features:v2"],
                "updated_at": self._now(),
                "created_by": "ml-engineer",
                "artifact_uri": "s3://ml-artifacts/fraud-detector/2.4.1/",
            },
            {
                "name": "churn-predictor",
                "version": "1.8.0",
                "stage": ModelStage.staging,
                "accuracy": 0.897,
                "metrics": {"val_auc": 0.897, "val_f1": 0.812},
                "params": {"learning_rate": 0.05, "max_depth": 6},
                "feature_refs": ["user_features:v3", "engagement:v1"],
                "updated_at": self._now(),
                "created_by": "ml-engineer",
                "artifact_uri": "s3://ml-artifacts/churn-predictor/1.8.0/",
            },
            {
                "name": "recsys-ranker",
                "version": "3.1.2",
                "stage": ModelStage.production,
                "accuracy": 0.915,
                "metrics": {"val_auc": 0.915, "ndcg": 0.78},
                "params": {"embedding_dim": 64, "layers": 3},
                "feature_refs": ["item_features:v4", "user_features:v3"],
                "updated_at": self._now(),
                "created_by": "recsys-team",
                "artifact_uri": "s3://ml-artifacts/recsys-ranker/3.1.2/",
            },
            {
                "name": "price-optimizer",
                "version": "0.9.3",
                "stage": ModelStage.development,
                "accuracy": 0.871,
                "metrics": {"val_rmse": 0.42, "val_mae": 0.31},
                "params": {"learning_rate": 0.01, "n_estimators": 200},
                "feature_refs": ["market_features:v1", "product_features:v2"],
                "updated_at": self._now(),
                "created_by": "pricing-team",
                "artifact_uri": "s3://ml-artifacts/price-optimizer/0.9.3/",
            },
        ]
        for s in seeds:
            self._store.setdefault(s["name"], []).append(s)

    def list_models(self) -> list[ModelVersionOut]:
        out: list[ModelVersionOut] = []
        for versions in self._store.values():
            if not versions:
                continue
            latest = versions[-1]
            out.append(ModelVersionOut(**latest))
        return out

    def get(self, name: str, version: Optional[str] = None) -> Optional[ModelVersionOut]:
        versions = self._store.get(name, [])
        if not versions:
            return None
        if version is None:
            return ModelVersionOut(**versions[-1])
        for v in versions:
            if v["version"] == version:
                return ModelVersionOut(**v)
        return None

    def get_production(self, name: str) -> Optional[ModelVersionOut]:
        for v in reversed(self._store.get(name, [])):
            if v["stage"] == ModelStage.production:
                return ModelVersionOut(**v)
        return None

    def register(
        self,
        name: str,
        metrics: dict[str, float],
        params: dict[str, Any],
        feature_refs: list[str],
        artifact_uri: str,
        created_by: str = "system",
    ) -> ModelVersionOut:
        versions = self._store.setdefault(name, [])
        major = len(versions) + 1
        version = f"{major}.0.0"
        accuracy = float(metrics.get("val_auc", metrics.get("accuracy", 0.0)))
        record = {
            "name": name,
            "version": version,
            "stage": ModelStage.development,
            "accuracy": accuracy,
            "metrics": metrics,
            "params": params,
            "feature_refs": feature_refs,
            "updated_at": self._now(),
            "created_by": created_by,
            "artifact_uri": artifact_uri,
        }
        versions.append(record)
        return ModelVersionOut(**record)

    def transition(
        self,
        name: str,
        version: str,
        stage: ModelStage,
        actor: str = "system",
        comment: Optional[str] = None,
    ) -> ModelVersionOut:
        versions = self._store.get(name)
        if not versions:
            raise KeyError(f"model {name} not found")

        target = None
        for v in versions:
            if v["version"] == version:
                target = v
                break
        if target is None:
            raise KeyError(f"version {version} not found for {name}")

        if stage == ModelStage.production:
            for v in versions:
                if v["stage"] == ModelStage.production and v["version"] != version:
                    v["stage"] = ModelStage.archived
                    v["updated_at"] = self._now()

        target["stage"] = stage
        target["updated_at"] = self._now()
        return ModelVersionOut(**target)

    def active_count(self) -> int:
        count = 0
        for versions in self._store.values():
            for v in versions:
                if v["stage"] in (ModelStage.production, ModelStage.staging):
                    count += 1
                    break
        return count
