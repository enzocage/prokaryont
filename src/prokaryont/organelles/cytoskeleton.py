"""Cytoplasma, Cytosol, Zytoskelett-Homologe, MreB-Filamente & FtsZ-Ernte-Ring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from prokaryont.models import OrganelleTelemetry


@dataclass
class Cytosol:
    """Flüssiges In-Memory-Transport- & Event-Medium zwischen den Organellen."""

    events_routed_today: int = 0
    working_memory: dict[str, Any] = field(default_factory=dict)

    def publish(self, key: str, value: Any) -> None:
        self.working_memory[key] = value
        self.events_routed_today += 1

    def reset_tick(self) -> None:
        self.events_routed_today = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="cytosol",
            name_de="Cytosol (Event-Bus)",
            system_id="cytoskeleton",
            health=1.0,
            activity=min(1.0, self.events_routed_today / 25.0),
            load=0.35,
            efficiency=1.0,
            state_label_de=f"{self.events_routed_today} Signale heute vermittelt",
            metrics={
                "events_routed_today": self.events_routed_today,
                "state_keys": len(self.working_memory),
            },
        )


class Cytoplasm:
    """Interne Laufzeitumgebung aller produktiven Organellen."""

    def __init__(self) -> None:
        self.cytosol = Cytosol()
        self.utilization: float = 0.5

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="cytoplasm",
            name_de="Cytoplasma (Laufzeitraum)",
            system_id="cytoskeleton",
            health=1.0,
            activity=self.utilization,
            load=self.utilization,
            efficiency=1.0,
            state_label_de=f"Auslastung {self.utilization * 100:.0f} %",
            metrics={"utilization": round(self.utilization, 3)},
        )


@dataclass
class MreBFilaments:
    """MreB-Filamente: dynamische Kapazitäts- & Parallelitäts-Skalierung (Load Balancer)."""

    current_workers: int = 2
    utilization: float = 0.5

    def balance_capacity(
        self,
        queued_orders: int,
        base_max_capacity: int,
        atp_balance: float,
    ) -> int:
        # Skaliert Produktionskapazität sanft nach Auftragslast & ATP-Budget
        if atp_balance < 3.0:
            scale_factor = 0.55
            self.current_workers = 1
        elif queued_orders > base_max_capacity * 0.75:
            scale_factor = 1.25
            self.current_workers = 4
        else:
            scale_factor = 1.0
            self.current_workers = 2
        effective_cap = max(1, int(round(base_max_capacity * scale_factor)))
        self.utilization = round(min(1.0, queued_orders / max(1, effective_cap)), 3)
        return effective_cap

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="mreb_filaments",
            name_de="MreB-Filamente (Load Balancer)",
            system_id="cytoskeleton",
            health=1.0,
            activity=self.utilization,
            load=self.utilization,
            efficiency=1.0,
            state_label_de=f"{self.current_workers} Worker · Last {self.utilization * 100:.0f} %",
            metrics={
                "current_workers": self.current_workers,
                "utilization": self.utilization,
            },
        )


@dataclass
class FtsZRing:
    """FtsZ-Ring: schnürt bei gesättigter Reserve Überschuss-Ertrag als Ernte ab."""

    contractions_total: int = 0
    last_harvest_day: int | None = None
    last_harvest_eur: float = 0.0
    total_harvested_eur: float = 0.0
    ring_tension: float = 0.0

    def evaluate_and_harvest(
        self,
        day: int,
        phb_balance_eur: float,
        harvest_threshold_eur: float,
        harvest_ratio: float,
        operon_aggression: float,
        dormant: bool,
    ) -> float:
        if dormant or phb_balance_eur <= harvest_threshold_eur:
            self.ring_tension = round(
                min(0.99, phb_balance_eur / max(1.0, harvest_threshold_eur)), 3
            )
            return 0.0

        excess = phb_balance_eur - harvest_threshold_eur
        # Schnürt anteilig Überschuss ab, ohne den sicheren Kern-Runway anzugreifen
        harvest = round(excess * min(0.75, harvest_ratio * operon_aggression), 2)
        if harvest <= 0.5:
            return 0.0

        self.contractions_total += 1
        self.last_harvest_day = day
        self.last_harvest_eur = harvest
        self.total_harvested_eur = round(self.total_harvested_eur + harvest, 2)
        self.ring_tension = 1.0
        return harvest

    def force_manual_harvest(self, day: int, phb_balance_eur: float, amount_eur: float) -> float:
        safe_amount = round(min(max(0.0, amount_eur), max(0.0, phb_balance_eur * 0.5)), 2)
        if safe_amount <= 0.0:
            return 0.0
        self.contractions_total += 1
        self.last_harvest_day = day
        self.last_harvest_eur = safe_amount
        self.total_harvested_eur = round(self.total_harvested_eur + safe_amount, 2)
        return safe_amount

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="ftsz_ring",
            name_de="FtsZ-Ring (Ernte-Kontraktion)",
            system_id="cytoskeleton",
            health=1.0,
            activity=self.ring_tension,
            load=self.ring_tension,
            efficiency=1.0,
            state_label_de=(
                f"{self.contractions_total} Ernten · {self.total_harvested_eur:.2f} € abgeschöpft"
            ),
            metrics={
                "contractions_total": self.contractions_total,
                "last_harvest_eur": self.last_harvest_eur,
                "total_harvested_eur": self.total_harvested_eur,
                "ring_tension": self.ring_tension,
            },
        )


class Cytoskeleton:
    """Zytoskelett-Homologe: vereint MreB-Skalierung & FtsZ-Ernte (Crescentin ausgeschlossen)."""

    def __init__(self) -> None:
        self.mreb = MreBFilaments()
        self.ftsz = FtsZRing()

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="cytoskeleton_homologs",
            name_de="Zytoskelett-Homologe",
            system_id="cytoskeleton",
            health=1.0,
            activity=round((self.mreb.utilization + self.ftsz.ring_tension) / 2, 3),
            load=self.mreb.utilization,
            efficiency=1.0,
            state_label_de=f"Spannung {self.ftsz.ring_tension * 100:.0f} % · {self.mreb.current_workers} Lanes",
            metrics={
                "workers": self.mreb.current_workers,
                "harvest_tension": self.ftsz.ring_tension,
            },
        )
