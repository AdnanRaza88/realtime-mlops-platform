# Drift Detection Strategy

**Version:** 1.0.0  
**Aligned with PRD:** Yes  

---

## 1. Objectives

- Detect feature distribution shift (covariate drift) before it degrades online metrics.
- Detect prediction / performance drift when labels are available.
- Keep false-positive rate under 5% via calibrated thresholds and adaptive baselines.
- Mean time to detect (MTTD) target: < 5 minutes for critical features.

## 2. Metrics

| Metric | Use case | Notes |
|--------|----------|-------|
| **PSI** (Population Stability Index) | Numeric & binned categorical | Primary signal; buckets from reference quantiles |
| KL divergence | Optional secondary | More sensitive; higher variance |
| Wasserstein-1 | Continuous features | Robust to binning choices |
| Chi-square / TVD | Categorical | When cardinality is low |
| Performance delta | AUC / F1 / RMSE drop | Requires delayed labels |

## 3. Thresholds (default)

| Level | PSI | Action |
|-------|-----|--------|
| Stable | < 0.10 | No action |
| Watch | 0.10 – 0.20 | Log + dashboard highlight |
| Drift | ≥ 0.20 | Alert + optional retrain trigger |

Configurable via `Settings.psi_warning` and `Settings.psi_critical`.

## 4. Reference window

- **Training / golden set**: fixed snapshot used as reference (recommended for production models).
- **Rolling baseline**: last N days of healthy traffic (useful for seasonality).
- Reference is stored in the DriftEngine and can be refreshed on approved model promotions.

## 5. Evaluation cadence

- Online features: every `drift_interval_sec` (default 300s).
- Batch features: after each offline materialization job.
- Performance drift: daily (or when enough labels arrive).

## 6. Alert routing

| Severity | Channel |
|----------|--------|
| Watch | Dashboard only |
| Drift (single feature) | Slack #ml-alerts |
| Drift (multiple / critical path) | Slack + PagerDuty |
| Performance drop > threshold | Slack + ticket |

## 7. Retrain coupling

When any production-critical feature enters **Drift** state for two consecutive windows, or performance drop exceeds `performance_drop_threshold`, the RetrainOrchestrator emits a `feature_drift` or `performance_degradation` job.

## 8. Implementation map

| Component | Location |
|-----------|----------|
| PSI + classify | `backend/app/services/drift.py` |
| API surface | `GET /api/v1/drift` |
| Dashboard | Frontend Drift page |
| Config | `psi_warning`, `psi_critical`, `drift_interval_sec` |
