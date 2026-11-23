"""Endosporen-Ruhesystem (Exosporium, Sporenmantel, Kortex, Protoplast) & Seed-Export."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from prokaryont.models import OrganelleTelemetry


@dataclass
class Exosporium:
    """Äußerster Keimungs-Rezeptor: tastet Markt im Schlaf für <0,05 €/Tag ab."""

    heartbeat_cost_eur: float = 0.04
    last_signal_strength: float = 1.0
    recovery_streak_days: int = 0

    def sense_germination(
        self,
        demand_ratio: float,
        germination_trigger: float,
        drought_active: bool,
    ) -> bool:
        self.last_signal_strength = round(demand_ratio, 3)
        if not drought_active and demand_ratio >= germination_trigger:
            self.recovery_streak_days += 1
        else:
            self.recovery_streak_days = 0
        return self.recovery_streak_days >= 2

    def to_telemetry(self, dormant: bool) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="exosporium",
            name_de="Exosporium (Keimungs-Sensor)",
            system_id="dormancy",
            health=1.0,
            activity=0.95 if dormant else 0.20,
            load=0.10,
            efficiency=1.0,
            state_label_de=(
                f"Wacht im Schlaf (Signal {self.last_signal_strength:.2f})"
                if dormant
                else "Standby"
            ),
            metrics={
                "last_signal_strength": self.last_signal_strength,
                "recovery_streak_days": self.recovery_streak_days,
            },
        )


@dataclass
class SporeCoat:
    """Sporenmantel: SHA-256-Integritätssicherung & portabler Saatgut-Snapshot."""

    latest_hash: str = ""
    exports_count: int = 0

    def seal_seed(self, payload: dict[str, Any]) -> dict[str, Any]:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        self.latest_hash = digest
        self.exports_count += 1
        return {
            "schema": "prokaryont.spore.v1",
            "sha256": digest,
            "payload": payload,
        }

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="spore_coat",
            name_de="Sporenmantel (Saatgut-Schutz)",
            system_id="dormancy",
            health=1.0,
            activity=0.60 if self.latest_hash else 0.25,
            load=0.15,
            efficiency=1.0,
            state_label_de=f"Hash {self.latest_hash[:10]}…" if self.latest_hash else "Bereit",
            metrics={
                "latest_hash": self.latest_hash[:16],
                "exports_count": self.exports_count,
            },
        )


@dataclass
class SporeCortex:
    """Kortex: Kosten-Dehydrierung um ~93 % im Endosporen-Ruhezustand."""

    compression_factor: float = 0.07  # nur noch 7 % des normalen Fix-Burns!

    def dehydrated_daily_burn(self, normal_fixed_infra_eur: float) -> float:
        return round(max(0.04, normal_fixed_infra_eur * self.compression_factor), 4)

    def to_telemetry(self, dormant: bool) -> OrganelleTelemetry:
        reduction = (1.0 - self.compression_factor) * 100.0
        return OrganelleTelemetry(
            id="spore_cortex",
            name_de="Kortex (Kosten-Dehydrierung)",
            system_id="dormancy",
            health=1.0,
            activity=1.0 if dormant else 0.15,
            load=0.07 if dormant else 0.20,
            efficiency=round(1.0 - self.compression_factor, 3),
            state_label_de=(
                f"AKTIV: -{reduction:.0f} % Fixkosten"
                if dormant
                else f"Bereit (-{reduction:.0f} % Burn)"
            ),
            metrics={
                "burn_reduction_pct": round(reduction, 1),
                "dormant_active": dormant,
            },
        )


@dataclass
class SporeProtoplast:
    """Protoplast: versiegelter Minimal-Kern aus Chromosom, Plasmiden & PHB-Index."""

    sealed_state: dict[str, Any] = field(default_factory=dict)

    def seal_core(
        self,
        day: int,
        genes: dict[str, dict[str, float]],
        plasmid_ids: list[str],
        phb_eur: float,
        active_customers: int,
    ) -> dict[str, Any]:
        self.sealed_state = {
            "sealed_day": day,
            "genes": genes,
            "plasmid_ids": list(plasmid_ids),
            "phb_eur": round(phb_eur, 2),
            "active_customers": active_customers,
        }
        return self.sealed_state

    def to_telemetry(self, dormant: bool) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="spore_protoplast",
            name_de="Protoplast (Versiegelter Kern)",
            system_id="dormancy",
            health=1.0,
            activity=0.90 if dormant else 0.20,
            load=0.15,
            efficiency=1.0,
            state_label_de="Kern versiegelt" if dormant else "Vegetativ aktiv",
            metrics={
                "has_sealed_core": bool(self.sealed_state),
                "sealed_day": self.sealed_state.get("sealed_day", 0),
            },
        )


class EndosporeSystem:
    """Vollständiges Endosporen-System für Dürre-Überleben & Saatgut-Vererbung."""

    def __init__(self) -> None:
        self.exosporium = Exosporium()
        self.coat = SporeCoat()
        self.cortex = SporeCortex()
        self.protoplast = SporeProtoplast()
        self.is_dormant: bool = False
        self.dormancy_episodes: int = 0
        self.total_dormant_days: int = 0

    def enter_dormancy(
        self,
        day: int,
        genes: dict[str, dict[str, float]],
        plasmid_ids: list[str],
        phb_eur: float,
        active_customers: int,
    ) -> dict[str, Any]:
        self.is_dormant = True
        self.dormancy_episodes += 1
        self.exosporium.recovery_streak_days = 0
        core = self.protoplast.seal_core(day, genes, plasmid_ids, phb_eur, active_customers)
        return self.coat.seal_seed(core)

    def germinate(self) -> None:
        self.is_dormant = False
        self.exosporium.recovery_streak_days = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="endospores",
            name_de="Endosporen-System (Krisen-Ruhe)",
            system_id="dormancy",
            health=1.0,
            activity=1.0 if self.is_dormant else 0.20,
            load=0.10 if self.is_dormant else 0.05,
            efficiency=1.0,
            state_label_de=(
                f"RUHEZUSTAND aktiv ({self.total_dormant_days} Tage total)"
                if self.is_dormant
                else f"Bereit ({self.dormancy_episodes} Ruhepausen überlebt)"
            ),
            metrics={
                "is_dormant": self.is_dormant,
                "dormancy_episodes": self.dormancy_episodes,
                "total_dormant_days": self.total_dormant_days,
            },
        )
