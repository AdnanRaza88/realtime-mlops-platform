# Model Registry Design

**Version:** 1.0.0  

---

## 1. Purpose

Central, versioned store of model artifacts, metrics, parameters, feature references, and lifecycle stage. Supports promotion workflows and zero-downtime serving handoff.

## 2. Stages

```
Development → Staging → Production → Archived
```

Rules:

- Only one version per model name may be in **Production** at a time.
- Promoting a new version to Production automatically moves the previous Production version to **Archived**.
- Staging is used for shadow / canary evaluation.
- Development is the default on register.

## 3. Record schema

| Field | Type | Description |
|-------|------|-------------|
| name | string | Model family (e.g. fraud-detector) |
| version | semver string | e.g. 3.0.0 |
| stage | enum | Development / Staging / Production / Archived |
| accuracy | float | Primary metric (AUC or accuracy) |
| metrics | map[string, float] | Full eval suite |
| params | map | Hyperparameters |
| feature_refs | list[string] | Feature view versions used |
| artifact_uri | string | S3 / GCS / local path |
| created_by | string | Actor or system |
| updated_at | ISO timestamp | Last stage or metadata change |

## 4. API

| Method | Path | Action |
|--------|------|--------|
| GET | /models | List latest version per name |
| GET | /models/{name} | Get specific (optional ?version=) |
| POST | /models/{name}/versions/{version}/transition | Change stage |
| POST | /retrain | Queue retrain (feeds registry on success) |

## 5. Implementation

In-memory store for the demo platform (`backend/app/services/registry.py`). Production deployment swaps the backend for PostgreSQL + object storage while keeping the same interface.

## 6. Promotion checklist (operational)

1. Metrics meet gate thresholds.
2. Feature refs match current online store versions.
3. Shadow traffic healthy for ≥ 24h (Staging).
4. Operator or automated policy approves transition to Production.
5. Previous Production archived; serving config updated.
