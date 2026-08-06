# Realtime MLOps Platform

End-to-end real-time data science and MLOps system: streaming ingestion, feature store, training, model registry, automated retraining, drift detection, and a light-theme monitoring dashboard.

**Repo:** https://github.com/AdnanRaza88/realtime-mlops-platform

**Figma:** https://www.figma.com/design/0KfsVcmjZeh7Fm9Dkg6yud/Realtime-MLOps-Platform---Monitoring-Dashboard

---

## Design

Light theme only. Soft neutrals. Glassmorphism panels. Claymorphism cards. No dark mode.

| Page | Role |
|------|------|
| Overview | KPIs, performance chart, events, pipeline health |
| Drift | PSI table and feature status |
| Models | Registry cards, stage, retrain trigger |

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

docs/                    PRD, schemas, strategies
src/                     Library modules (ingestion, training, etc.)
.github/workflows/pages.yml
```

---

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or: `./scripts/run_backend.sh`

API base: `http://127.0.0.1:8000/api/v1`

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | liveness |
| GET | /overview | KPIs, stages, events, series |
| GET | /drift | feature PSI results |
| GET | /models | registry list |
| POST | /models/{name}/versions/{version}/transition | stage change |
| POST | /retrain | queue retrain |
| GET | /retrain/history | recent triggers |

OpenAPI: http://127.0.0.1:8000/docs

---

## Frontend

```bash
cd frontend
python -m http.server 5173
```

Visit http://127.0.0.1:5173

Dashboard uses `window.MLOpsConfig.apiBase` (default local API). Falls back to mock data when API is offline so GitHub Pages still works.

---

## GitHub Pages

Workflow deploys `frontend/` on push to main.

Enable: Settings → Pages → Source: GitHub Actions

URL: https://adnanraza88.github.io/realtime-mlops-platform/

---

## Planning docs

See `docs/` for PRD, feature store schema, drift strategy, model registry, dashboard specs, tracker, validation report.
