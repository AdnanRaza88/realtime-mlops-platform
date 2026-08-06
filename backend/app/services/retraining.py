from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Optional

from app.core.config import get_settings
from app.models.schemas import TriggerReason


class RetrainOrchestrator:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._handlers: list[Callable[[dict[str, Any]], None]] = []
        self._history: list[dict[str, Any]] = []

    def on_retrain(self, handler: Callable[[dict[str, Any]], None]) -> None:
        self._handlers.append(handler)

    def evaluate_performance(
        self,
        model_name: str,
        current: float,
        baseline: float,
        metric: str = "auc",
    ) -> Optional[dict[str, Any]]:
        drop = baseline - current
        if drop < self.settings.performance_drop_threshold:
            return None
        payload = {
            "model_name": model_name,
            "reason": TriggerReason.performance.value,
            "details": {
                "metric": metric,
                "baseline": baseline,
                "current": current,
                "drop": round(drop, 4),
            },
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": "system",
        }
        self._dispatch(payload)
        return payload

    def evaluate_drift(
        self,
        model_name: str,
        drifted_features: list[str],
        max_psi: float,
    ) -> Optional[dict[str, Any]]:
        if not drifted_features:
            return None
        payload = {
            "model_name": model_name,
            "reason": TriggerReason.feature_drift.value,
            "details": {
                "features": drifted_features,
                "max_psi": max_psi,
            },
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": "system",
        }
        self._dispatch(payload)
        return payload

    def schedule(self, model_name: str) -> dict[str, Any]:
        payload = {
            "model_name": model_name,
            "reason": TriggerReason.schedule.value,
            "details": {},
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": "scheduler",
        }
        self._dispatch(payload)
        return payload

    def manual(self, model_name: str, actor: str = "operator") -> dict[str, Any]:
        payload = {
            "model_name": model_name,
            "reason": TriggerReason.manual.value,
            "details": {},
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": actor,
        }
        self._dispatch(payload)
        return payload

    def history(self, limit: int = 20) -> list[dict[str, Any]]:
        return list(reversed(self._history[-limit:]))

    def _dispatch(self, payload: dict[str, Any]) -> None:
        self._history.append(payload)
        for h in self._handlers:
            h(payload)
