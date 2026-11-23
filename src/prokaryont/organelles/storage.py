"""Einschlusskörperchen & strategische Speicher-Granula (PHB, Glykogen, Volutin, Schwefel)."""

from __future__ import annotations

from dataclasses import dataclass, field

from prokaryont.models import OrganelleTelemetry


@dataclass
class PHBReserve:
    """Polyhydroxybutyrat-Granula: langfristige Treasury- & Krisen-Liquiditätsreserve."""

    balance_eur: float = 0.0
    target_buffer_eur: float = 500.0

    def deposit(self, amount_eur: float) -> float:
        added = max(0.0, amount_eur)
        self.balance_eur = round(self.balance_eur + added, 2)
        return self.balance_eur

    def withdraw(self, amount_eur: float) -> float:
        taken = min(self.balance_eur, max(0.0, amount_eur))
        self.balance_eur = round(self.balance_eur - taken, 2)
        return taken

    def to_telemetry(self) -> OrganelleTelemetry:
        fill = min(1.0, self.balance_eur / max(1.0, self.target_buffer_eur))
        return OrganelleTelemetry(
            id="phb_reserve",
            name_de="Polyhydroxybutyrat-Granula (PHB-Reserve)",
            system_id="storage",
            health=1.0 if fill > 0.25 else 0.65,
            activity=round(fill, 3),
            load=round(fill, 3),
            efficiency=1.0,
            state_label_de=f"{self.balance_eur:.2f} € Reserve ({fill*100:.0f} % Zielpuffer)",
            metrics={
                "balance_eur": self.balance_eur,
                "target_buffer_eur": self.target_buffer_eur,
                "fill_ratio": round(fill, 3),
            },
        )


@dataclass
class GlycogenCache:
    """Glykogen-Granula: schneller semantischer Output-Cache gegen Token-Kosten."""

    cached_topics: dict[str, int] = field(default_factory=dict)
    hit_rate: float = 0.35
    hits_today: int = 0
    misses_today: int = 0

    def lookup_or_store(
        self,
        topic_key: str,
        cache_aggressiveness: float,
        plasmid_hit_bonus: float,
        rng_roll: float,
    ) -> bool:
        familiarity = min(0.28, self.cached_topics.get(topic_key, 0) * 0.025)
        effective_prob = min(
            0.84, max(0.15, cache_aggressiveness * 0.62 + familiarity + plasmid_hit_bonus)
        )
        self.cached_topics[topic_key] = self.cached_topics.get(topic_key, 0) + 1
        if rng_roll < effective_prob:
            self.hits_today += 1
            self.hit_rate = round(
                self.hits_today / max(1, self.hits_today + self.misses_today), 3
            )
            return True
        self.misses_today += 1
        self.hit_rate = round(
            self.hits_today / max(1, self.hits_today + self.misses_today), 3
        )
        return False

    def reset_daily(self) -> None:
        self.hits_today = 0
        self.misses_today = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="glycogen_cache",
            name_de="Glykogen-Granula (Semantic-Cache)",
            system_id="storage",
            health=1.0,
            activity=self.hit_rate,
            load=min(1.0, len(self.cached_topics) / 20.0),
            efficiency=round(1.0 + self.hit_rate, 3),
            state_label_de=f"Cache-Quote {self.hit_rate*100:.1f} % ({self.hits_today} Hits heute)",
            metrics={
                "hit_rate": self.hit_rate,
                "hits_today": self.hits_today,
                "misses_today": self.misses_today,
                "cached_topics": len(self.cached_topics),
            },
        )


@dataclass
class VolutinPool:
    """Volutin-Granula: vorausbezahlte Compute-/Token-Kontingente als Preisschock-Hedge."""

    prepaid_eur: float = 0.0
    max_capacity_eur: float = 120.0
    hedged_savings_today_eur: float = 0.0

    def top_up(self, amount_eur: float) -> float:
        room = max(0.0, self.max_capacity_eur - self.prepaid_eur)
        added = min(room, max(0.0, amount_eur))
        self.prepaid_eur = round(self.prepaid_eur + added, 2)
        return added

    def hedge_compute(self, raw_cost_eur: float, compute_multiplier: float) -> float:
        """Schützt gegen externe Compute-Preisschocks durch abgesicherte Prepaid-Kontingente."""
        if compute_multiplier <= 1.05 or self.prepaid_eur <= 0.1:
            return raw_cost_eur
        extra_spike = raw_cost_eur * (1.0 - 1.0 / compute_multiplier)
        covered = min(self.prepaid_eur, extra_spike * 0.85)
        self.prepaid_eur = round(self.prepaid_eur - covered, 4)
        self.hedged_savings_today_eur = round(self.hedged_savings_today_eur + covered, 4)
        return round(max(0.01, raw_cost_eur - covered), 4)

    def reset_daily(self) -> None:
        self.hedged_savings_today_eur = 0.0

    def to_telemetry(self) -> OrganelleTelemetry:
        fill = min(1.0, self.prepaid_eur / max(1.0, self.max_capacity_eur))
        return OrganelleTelemetry(
            id="volutin_pool",
            name_de="Volutin-Granula (Compute-Prepaid)",
            system_id="storage",
            health=1.0,
            activity=round(fill, 3),
            load=round(fill, 3),
            efficiency=1.15 if self.prepaid_eur > 0 else 1.0,
            state_label_de=f"{self.prepaid_eur:.2f} € Compute-Kontingent",
            metrics={
                "prepaid_eur": round(self.prepaid_eur, 2),
                "hedged_savings_today_eur": round(self.hedged_savings_today_eur, 2),
                "fill_ratio": round(fill, 3),
            },
        )


@dataclass
class SulfurBuffer:
    """Schwefel-Globuli: Vorrat an kuratierten Rohdaten, Benchmarks & Warm-Leads."""

    units_ready: float = 25.0
    max_units: float = 100.0

    def replenish(self, leads_captured: int, dormant: bool) -> None:
        if dormant:
            return
        self.units_ready = round(min(self.max_units, self.units_ready + 2.5 + leads_captured * 0.5), 2)

    def consume_for_production(self) -> bool:
        if self.units_ready >= 1.0:
            self.units_ready = round(self.units_ready - 0.8, 2)
            return True
        return False

    def to_telemetry(self) -> OrganelleTelemetry:
        fill = min(1.0, self.units_ready / max(1.0, self.max_units))
        return OrganelleTelemetry(
            id="sulfur_buffer",
            name_de="Schwefel-Globuli (Rohdaten-Vorrat)",
            system_id="storage",
            health=1.0,
            activity=round(fill, 3),
            load=round(fill, 3),
            efficiency=1.12 if self.units_ready > 5 else 1.0,
            state_label_de=f"{self.units_ready:.0f}/{self.max_units:.0f} Daten-Pakete bereit",
            metrics={
                "units_ready": self.units_ready,
                "fill_ratio": round(fill, 3),
            },
        )


class InclusionBodies:
    """Einschlusskörperchen: übergeordneter Container aller 4 Speicher-Granula."""

    def __init__(self, target_phb_eur: float, volutin_cap_eur: float) -> None:
        self.phb = PHBReserve(balance_eur=0.0, target_buffer_eur=target_phb_eur)
        self.glycogen = GlycogenCache()
        self.volutin = VolutinPool(prepaid_eur=round(volutin_cap_eur * 0.2, 2), max_capacity_eur=volutin_cap_eur)
        self.sulfur = SulfurBuffer()

    def to_telemetry(self) -> OrganelleTelemetry:
        avg_fill = (
            min(1.0, self.phb.balance_eur / max(1.0, self.phb.target_buffer_eur))
            + self.glycogen.hit_rate
            + min(1.0, self.volutin.prepaid_eur / max(1.0, self.volutin.max_capacity_eur))
            + min(1.0, self.sulfur.units_ready / max(1.0, self.sulfur.max_units))
        ) / 4.0
        return OrganelleTelemetry(
            id="inclusion_bodies",
            name_de="Einschlusskörperchen (Speicher-Verbund)",
            system_id="storage",
            health=1.0,
            activity=round(avg_fill, 3),
            load=round(avg_fill, 3),
            efficiency=1.0,
            state_label_de=f"Speichersättigung {avg_fill*100:.0f} %",
            metrics={"average_fill": round(avg_fill, 3)},
        )
