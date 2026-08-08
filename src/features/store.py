"""Feature store interface — online lookup + offline materialization stubs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class FeatureView:
    name: str
    entities: list[str]
    features: list[str]
    ttl_seconds: int = 86400
    version: int = 1
    online: bool = True
    offline: bool = True


@dataclass
class FeatureStore:
    """In-memory online store for demos. Swap for Redis / Feast in production."""

    views: dict[str, FeatureView] = field(default_factory=dict)
    _online: dict[str, dict[str, Any]] = field(default_factory=dict)

    def register_view(self, view: FeatureView) -> None:
        self.views[view.name] = view

    def put(self, entity_key: str, features: dict[str, Any], view: str = "default") -> None:
        bucket = self._online.setdefault(view, {})
        bucket[entity_key] = {
            **features,
            "_ts": datetime.now(timezone.utc).isoformat(),
        }

    def get(self, entity_key: str, view: str = "default", features: Optional[list[str]] = None) -> dict[str, Any]:
        row = self._online.get(view, {}).get(entity_key, {})
        if not features:
            return {k: v for k, v in row.items() if not k.startswith("_")}
        return {k: row[k] for k in features if k in row}

    def materialize_offline(self, view: str, path: str) -> dict[str, Any]:
        """Stub: would write Parquet / Delta to path."""
        rows = self._online.get(view, {})
        return {
            "view": view,
            "path": path,
            "row_count": len(rows),
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
