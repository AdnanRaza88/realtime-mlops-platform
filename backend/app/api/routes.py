from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.schemas import (
    DriftSummary,
    FeatureDriftItem,
    HealthResponse,
    ModelListResponse,
    ModelStage,
    OverviewResponse,
    RetrainRequest,
    RetrainResponse,
    StageTransitionRequest,
)
from app.services.drift import DriftEngine
from app.services.overview import OverviewService
from app.services.registry import ModelRegistry
from app.services.retraining import RetrainOrchestrator

router = APIRouter()

registry = ModelRegistry()
drift_engine = DriftEngine()
retrain_orch = RetrainOrchestrator()
overview_svc = OverviewService(registry, drift_engine)


@router.get("/health", response_model=HealthResponse)
def health():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


@router.get("/overview", response_model=OverviewResponse)
def overview():
    return overview_svc.build()


@router.get("/drift", response_model=DriftSummary)
def drift_summary():
    settings = get_settings()
    results = drift_engine.snapshot_for_api()
    items = [
        FeatureDriftItem(
            feature=r.feature_name,
            feature_type=r.feature_type,
            psi=r.psi,
            status=r.status.value,
            last_updated=datetime.now(timezone.utc).strftime("%H:%M:%S"),
            reference_size=r.reference_size,
            current_size=r.current_size,
        )
        for r in results
    ]
    drift_count = sum(1 for i in items if i.status.value == "Drift")
    return DriftSummary(
        features_monitored=len(items),
        drift_detected=drift_count,
        psi_threshold=settings.psi_critical,
        last_check="just now",
        items=items,
    )


@router.get("/models", response_model=ModelListResponse)
def list_models():
    return ModelListResponse(models=registry.list_models())


@router.get("/models/{name}")
def get_model(name: str, version: str | None = None):
    m = registry.get(name, version)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    return m


@router.post("/models/{name}/versions/{version}/transition")
def transition_stage(name: str, version: str, body: StageTransitionRequest):
    try:
        return registry.transition(name, version, body.stage, body.actor, body.comment)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/retrain", response_model=RetrainResponse)
def trigger_retrain(body: RetrainRequest):
    if body.reason.value == "manual":
        payload = retrain_orch.manual(body.model_name)
    elif body.reason.value == "schedule":
        payload = retrain_orch.schedule(body.model_name)
    else:
        payload = {
            "model_name": body.model_name,
            "reason": body.reason.value,
            "details": body.details,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": "api",
        }
        retrain_orch._dispatch(payload)

    return RetrainResponse(
        accepted=True,
        model_name=payload["model_name"],
        reason=payload["reason"],
        message="retrain job queued",
        requested_at=payload["requested_at"],
    )


@router.get("/retrain/history")
def retrain_history(limit: int = 20):
    return {"items": retrain_orch.history(limit)}
