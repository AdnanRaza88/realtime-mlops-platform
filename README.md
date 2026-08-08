# Realtime MLOps Platform

End-to-end real-time data science and MLOps system: streaming ingestion, feature store, training, model registry, automated retraining, drift detection, and a light-theme monitoring dashboard.

**Repo:** https://github.com/AdnanRaza88/realtime-mlops-platform

**Figma:** https://www.figma.com/design/0KfsVcmjZeh7Fm9Dkg6yud/Realtime-MLOps-Platform---Monitoring-Dashboard

---

## Design

Light theme only. Soft neutrals. Glassmorphism panels. Claymorphism cards. No dark mode. No saturated "AI" gradients.

| Page | Role |
|------|------|
| **Overview** | KPIs, performance chart (AUC + latency), events, pipeline health |
| **Drift** | PSI table and feature status (Stable / Watch / Drift) |
| **Models** | Registry cards, stage badges, Promote / Retrain |
| **Pipelines** | Training and materialization history |
| **Alerts** | Active drift and performance alerts |

Figma file contains the same pages for handoff and review.

---

## Layout

```
backend/                 FastAPI service
  app/
    api/routes.py
    core/config.py
    models/schemas.py
    services/
      drift.py           PSI + status classification
      registry.py        version + stage transitions
      retraining.py      schedule / performance / drift triggers
      overview.py
    main.py

frontend/                Static HTML/CSS/JS (GitHub Pages ready)
  index.html
  css/styles.css
  js/api.js              API client + offline mock fallback
  js/app.js

docs/                    Planning & design
  PRD.md
  feature_store_schema.md
  drift_detection_strategy.md
  model_registry_design.md
  monitoring_dashboard_specs.md
  document_tracker.md
  validation_report.md

src/                     Library modules
  ingestion/             Stream ingest interface
  features/              Online / offline feature store
  training/              Training pipeline stub
  monitoring/            Prediction logger

.github/workflows/pages.yml
scripts/run_backend.sh
```

---

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or: `./scripts/run_backend.sh`

API base: `http://127.0.0.1:8000/api/v1`

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Liveness |
| GET | /overview | KPIs, stages, events, series |
| GET | /drift | Feature PSI results |
| GET | /models | Registry list |
| GET | /models/{name} | Single model (optional `?version=`) |
| POST | /models/{name}/versions/{version}/transition | Stage change |
| POST | /retrain | Queue retrain |
| GET | /retrain/history | Recent triggers |

OpenAPI: http://127.0.0.1:8000/docs

---

## Frontend

```bash
cd frontend
python -m http.server 5173
```

Visit http://127.0.0.1:5173

Dashboard uses `window.MLOpsConfig.apiBase` (default local API). Falls back to mock data when the API is offline so GitHub Pages still works.

---

## GitHub Pages

Workflow deploys `frontend/` on push to `main`.

Enable: **Settings → Pages → Source: GitHub Actions**

URL: https://adnanraza88.github.io/realtime-mlops-platform/

---

## Planning docs

| Doc | Path |
|-----|------|
| Product requirements | [docs/PRD.md](docs/PRD.md) |
| Feature store schema | [docs/feature_store_schema.md](docs/feature_store_schema.md) |
| Drift detection strategy | [docs/drift_detection_strategy.md](docs/drift_detection_strategy.md) |
| Model registry design | [docs/model_registry_design.md](docs/model_registry_design.md) |
| Monitoring dashboard specs | [docs/monitoring_dashboard_specs.md](docs/monitoring_dashboard_specs.md) |
| Document tracker | [docs/document_tracker.md](docs/document_tracker.md) |
| Validation report | [docs/validation_report.md](docs/validation_report.md) |

---

## Components (code map)

| Component | Location |
|-----------|----------|
| Streaming ingestion | `src/ingestion/stream.py` |
| Feature engineering / store | `src/features/store.py` |
| Training | `src/training/pipeline.py` |
| Model registry | `backend/app/services/registry.py` |
| Automated retraining | `backend/app/services/retraining.py` |
| Drift detection | `backend/app/services/drift.py` |
| Monitoring dashboard | `frontend/` |

---

## License

MIT
