"""Sekretionssysteme: Multi-Protokoll-Auslieferung fertiger Kundenprodukte."""

from __future__ import annotations

from collections import deque

from prokaryont.models import OrganelleTelemetry, ProductArtifact


class SecretionSystem:
    """Typ I–VII Sekretionssysteme: liefert Briefings (Markdown) & API-Payloads aus."""

    def __init__(self, history_limit: int = 24) -> None:
        self.delivered_total: int = 0
        self.delivered_today: int = 0
        self.recent_artifacts: deque[ProductArtifact] = deque(maxlen=history_limit)
        self.protocols_used: dict[str, int] = {
            "briefing_markdown": 0,
            "rest_json_api": 0,
            "webhook_push": 0,
        }

    def begin_tick(self) -> None:
        self.delivered_today = 0

    def secrete(self, artifact: ProductArtifact | None, protocol: str) -> None:
        self.delivered_total += 1
        self.delivered_today += 1
        self.protocols_used[protocol] = self.protocols_used.get(protocol, 0) + 1
        if artifact is not None:
            self.recent_artifacts.appendleft(artifact)

    def get_recent(self) -> list[ProductArtifact]:
        return list(self.recent_artifacts)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="secretion_systems",
            name_de="Sekretionssysteme (Produkt-Export)",
            system_id="secretion",
            health=1.0,
            activity=min(1.0, self.delivered_today / 40.0),
            load=min(1.0, self.delivered_today / 50.0),
            efficiency=1.0,
            state_label_de=f"{self.delivered_today} heute · {self.delivered_total} gesamt ausgeliefert",
            metrics={
                "delivered_today": self.delivered_today,
                "delivered_total": self.delivered_total,
                "markdown_count": self.protocols_used.get("briefing_markdown", 0),
                "rest_json_count": self.protocols_used.get("rest_json_api", 0),
            },
        )
