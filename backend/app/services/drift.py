from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

from app.core.config import get_settings


class DriftStatus(str, Enum):
    STABLE = "Stable"
    WATCH = "Watch"
    DRIFT = "Drift"


@dataclass
class FeatureDriftResult:
    feature_name: str
    feature_type: str
    psi: float
    status: DriftStatus
    reference_size: int
    current_size: int


def _safe_hist(values: np.ndarray, breakpoints: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=breakpoints)
    return counts.astype(float)


def population_stability_index(
    expected: np.ndarray,
    actual: np.ndarray,
    buckets: int = 10,
) -> float:
    expected = np.asarray(expected, dtype=float).ravel()
    actual = np.asarray(actual, dtype=float).ravel()

    if expected.size == 0 or actual.size == 0:
        return 0.0

    expected = expected[np.isfinite(expected)]
    actual = actual[np.isfinite(actual)]
    if expected.size < 2 or actual.size < 2:
        return 0.0

    quantiles = np.linspace(0.0, 1.0, buckets + 1)
    breakpoints = np.unique(np.quantile(expected, quantiles))
    if breakpoints.size < 2:
        return 0.0

    exp_counts = _safe_hist(expected, breakpoints)
    act_counts = _safe_hist(actual, breakpoints)

    exp_total = exp_counts.sum()
    act_total = act_counts.sum()
    if exp_total <= 0 or act_total <= 0:
        return 0.0

    exp_pct = exp_counts / exp_total
    act_pct = act_counts / act_total

    eps = 1e-6
    exp_pct = np.clip(exp_pct, eps, None)
    act_pct = np.clip(act_pct, eps, None)

    psi = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return max(0.0, psi)


def classify_psi(psi: float, warning: Optional[float] = None, critical: Optional[float] = None) -> DriftStatus:
    settings = get_settings()
    w = warning if warning is not None else settings.psi_warning
    c = critical if critical is not None else settings.psi_critical
    if psi >= c:
        return DriftStatus.DRIFT
    if psi >= w:
        return DriftStatus.WATCH
    return DriftStatus.STABLE


class DriftEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._reference: dict[str, np.ndarray] = {}
        self._seed_reference()

    def _seed_reference(self) -> None:
        rng = np.random.default_rng(42)
        self._reference = {
            "user_age": rng.normal(35, 12, 5000),
            "transaction_amt": rng.lognormal(3.5, 0.8, 5000),
            "session_duration": rng.exponential(180, 5000),
            "click_rate": rng.beta(2, 8, 5000),
            "device_type_hash": rng.integers(0, 5, 5000).astype(float),
            "geo_region_hash": rng.integers(0, 12, 5000).astype(float),
        }

    def evaluate(
        self,
        feature_name: str,
        current: np.ndarray,
        feature_type: str = "numeric",
    ) -> FeatureDriftResult:
        ref = self._reference.get(feature_name)
        if ref is None:
            ref = current.copy()
            self._reference[feature_name] = ref

        psi = population_stability_index(ref, current)
        status = classify_psi(psi)
        return FeatureDriftResult(
            feature_name=feature_name,
            feature_type=feature_type,
            psi=round(psi, 4),
            status=status,
            reference_size=int(ref.size),
            current_size=int(np.asarray(current).size),
        )

    def evaluate_batch(
        self,
        current_map: dict[str, np.ndarray],
        types: Optional[dict[str, str]] = None,
    ) -> list[FeatureDriftResult]:
        types = types or {}
        results = []
        for name, arr in current_map.items():
            ftype = types.get(name, "numeric")
            results.append(self.evaluate(name, arr, ftype))
        return results

    def snapshot_for_api(self) -> list[FeatureDriftResult]:
        rng = np.random.default_rng()
        n = 2000
        current = {
            "user_age": self._reference["user_age"][:n] + rng.normal(0, 0.3, n),
            "transaction_amt": self._reference["transaction_amt"][:n] * rng.uniform(0.85, 1.4, n),
            "session_duration": self._reference["session_duration"][:n] + rng.normal(40, 25, n),
            "click_rate": np.clip(self._reference["click_rate"][:n] + rng.normal(0, 0.02, n), 0, 1),
            "device_type_hash": self._reference["device_type_hash"][:n],
            "geo_region_hash": np.clip(
                self._reference["geo_region_hash"][:n] + rng.integers(-1, 2, n), 0, 11
            ).astype(float),
        }
        types = {
            "user_age": "numeric",
            "transaction_amt": "numeric",
            "session_duration": "numeric",
            "click_rate": "numeric",
            "device_type_hash": "categorical",
            "geo_region_hash": "categorical",
        }
        return self.evaluate_batch(current, types)
