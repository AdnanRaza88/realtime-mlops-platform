# Realtime MLOps Platform

Complete real-time data science and MLOps pipeline covering streaming ingestion, feature engineering, model training, model registry, automated retraining, and production monitoring.

**Repository:** https://github.com/AdnanRaza88/realtime-mlops-platform  

---

## Design

**Figma Design File**  
https://www.figma.com/design/0KfsVcmjZeh7Fm9Dkg6yud/Realtime-MLOps-Platform---Monitoring-Dashboard

### Design Pages

| Page | Description |
|------|-------------|
| **01 – Overview Dashboard** | Primary operational home with KPI cards (claymorphism), performance chart panel (glassmorphism), recent events, and pipeline health status. |
| **02 – Drift Detection** | Feature-level drift monitoring with summary KPIs and detailed PSI / status table. |
| **03 – Model Registry** | Model cards showing version, stage, accuracy, and last update. |

**Visual language**  
- Light theme only (no dark mode)  
- Soft neutral palette: off-white base (`#F7F7F5`), pure white surfaces, near-black text, muted slate accent  
- Glassmorphism for secondary panels (blur + translucency)  
- Claymorphism for primary cards (soft dual shadows)  
- No high-saturation or “AI-feel” colors  

Full design tokens and interaction notes are in [`docs/monitoring_dashboard_specs.md`](docs/monitoring_dashboard_specs.md).

---

## Planning Documents

All planning and schema documents live inside the repository:

| Document | Path |
|----------|------|
| Product Requirements Document | [docs/PRD.md](docs/PRD.md) |
| Feature Store Schema | [docs/feature_store_schema.md](docs/feature_store_schema.md) |
| Drift Detection Strategy | [docs/drift_detection_strategy.md](docs/drift_detection_strategy.md) |
| Model Registry Design | [docs/model_registry_design.md](docs/model_registry_design.md) |
| Monitoring Dashboard Specs | [docs/monitoring_dashboard_specs.md](docs/monitoring_dashboard_specs.md) |
| Document Tracker | [docs/document_tracker.md](docs/document_tracker.md) |
| Validation Report | [docs/validation_report.md](docs/validation_report.md) |

---

## Architecture Components

```
src/
├── ingestion/          # Streaming consumers (Kafka-compatible)
├── feature_engineering/# Online + offline feature service
├── training/           # Reproducible training entry points
├── registry/           # Model versioning & stage transitions
├── retraining/         # Automated triggers (schedule / drift / performance)
├── monitoring/         # Drift detection (PSI and related metrics)
└── common/             # Config, logging
```

```
frontend/               # Light-theme React dashboard
infrastructure/         # Docker, Kubernetes, Terraform stubs
configs/                # Environment and pipeline configs
```

---

## Quick Start

### Backend (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at http://localhost:5173 with the soft light theme matching the Figma designs.

---

## Key Design Decisions

- Dual feature store (online low-latency + offline point-in-time correct).
- Stage-based model lifecycle (`Development → Staging → Production → Archived`).
- Drift detection centered on PSI with configurable warning/critical thresholds.
- Retraining triggered by schedule, performance drop, or feature drift.
- Dashboard deliberately calm and professional for long operational use.

---

## License

MIT (or company-internal as applicable).
