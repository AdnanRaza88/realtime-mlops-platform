"""Prediction logging for latency and eventual ground-truth join."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from collections import deque


@dataclass
class PredictionRecord:
    model_name: str
    version: str
    features: dict[str, Any]
    prediction: Any
    latency_ms: float
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    label: Any = None


class PredictionLogger:
    def __init__(self, maxlen: int = 10_000) -> None:
        self._buf: deque[PredictionRecord] = deque(maxlen=maxlen)

    def log(
        self,
        model_name: str,
        version: str,
        features: dict[str, Any],
        prediction: Any,
        latency_ms: float,
    ) -> PredictionRecord:
        rec = PredictionRecord(
            model_name=model_name,
            version=version,
            features=features,
            prediction=prediction,
            latency_ms=latency_ms,
        )
        self._buf.append(rec)
        return rec

    def attach_label(self, index: int, label: Any) -> None:
        if 0 <= index < len(self._buf):
            self._buf[index].label = label

    def recent(self, n: int = 100) -> list[PredictionRecord]:
        return list(self._buf)[-n:]

    def avg_latency(self, model_name: str | None = None) -> float:
        items = [r for r in self._buf if model_name is None or r.model_name == model_name]
        if not items:
            return 0.0
        return sum(r.latency_ms for r in items) / len(items)
