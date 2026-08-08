"""Streaming ingestion stubs — Kafka / PubSub ready interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterator
import json


@dataclass
class Event:
    key: str
    payload: dict[str, Any]
    topic: str
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StreamIngester:
    """Minimal ingest abstraction. Replace _poll with real Kafka consumer in production."""

    def __init__(self, bootstrap: str = "localhost:9092", topic: str = "events.raw") -> None:
        self.bootstrap = bootstrap
        self.topic = topic
        self._handlers: list[Callable[[Event], None]] = []
        self._buffer: list[Event] = []

    def on_event(self, handler: Callable[[Event], None]) -> None:
        self._handlers.append(handler)

    def publish_demo(self, key: str, payload: dict[str, Any]) -> Event:
        event = Event(key=key, payload=payload, topic=self.topic)
        self._buffer.append(event)
        for h in self._handlers:
            h(event)
        return event

    def drain(self, limit: int = 100) -> list[Event]:
        out = self._buffer[:limit]
        self._buffer = self._buffer[limit:]
        return out

    def iter_json_lines(self, lines: Iterator[str]) -> Iterator[Event]:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            key = str(data.get("id") or data.get("user_id") or "")
            yield self.publish_demo(key, data)
