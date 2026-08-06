from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

import numpy as np

from app.services.drift import DriftEngine
from app.services.registry import ModelRegistry


class OverviewService:
    def __init__(self, registry: ModelRegistry, drift: DriftEngine) -> None:
        self.registry = registry
        self.drift = drift
        self._events: list[dict[str, str]] = [
            {"message": "Model v2.4.1 promoted to Production", "timestamp": self._ts(-2), "severity": "info"},
            {"message": "Feature drift detected on transaction_amt", "timestamp": self._ts(-1), "severity": "warning"},
            {"message": "Retrain job started for fraud-detector", "timestamp": self._ts(-0.5), "severity": "info"},
            {"message": "New batch materialization completed", "timestamp": self._ts(-0.3), "severity": "info"},
            {"message": "Latency spike resolved on serving tier", "timestamp": self._ts(-0.1), "severity": "info"},
        ]

    def _ts(self, hours_ago: float) -> str:
        t = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def build(self) -> dict[str, Any]:
        drift_results = self.drift.snapshot_for_api()
        drift_count = sum(1 for r in drift_results if r.status.value == "Drift")

        rng = np.random.default_rng(7)
        series = []
        base = 0.93
        for i in range(24):
            base += rng.normal(0, 0.004)
            series.append({
                "hour": f"{i:02d}:00",
                "auc": round(float(np.clip(base, 0.85, 0.98)), 4),
                "latency_ms": round(float(45 + rng.normal(0, 6)), 1),
            })

        return {
            "kpis": {
                "active_models": self.registry.active_count(),
                "avg_latency_ms": 48.2,
                "drift_alerts": drift_count,
                "throughput_per_sec": 24500.0,
                "active_models_delta": "+2",
                "latency_delta": "-6ms",
                "drift_delta": f"+{drift_count}" if drift_count else "0",
                "throughput_delta": "+12%",
            },
            "stages": [
                {"name": "Ingestion", "status": "Healthy", "last_run": self._ts(0.05)},
                {"name": "Feature Eng", "status": "Healthy", "last_run": self._ts(0.08)},
                {"name": "Training", "status": "Healthy", "last_run": self._ts(2)},
                {"name": "Registry", "status": "Healthy", "last_run": self._ts(0.5)},
                {"name": "Serving", "status": "Healthy", "last_run": self._ts(0.02)},
            ],
            "events": self._events,
            "performance_series": series,
        }
