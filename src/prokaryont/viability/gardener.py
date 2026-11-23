"""Gärtner-Schnittstelle & quantitativer Ingenieur-Vergleichs-Benchmark."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.config import ScaleEconomicsProfile
from prokaryont.models import (
    BenchmarkPoint,
    GardenerPolicyState,
    MarketTickState,
    OrganelleTelemetry,
)


class GardenerInterface:
    """Kapselt alle High-Level-Eingriffe des Gärtners und trackt Aufmerksamkeitsstunden."""

    def __init__(self, harvest_threshold_eur: float) -> None:
        self.policy = GardenerPolicyState(harvest_threshold_eur=harvest_threshold_eur)
        self.attention_hours_cumulative: float = 1.5  # Initiales Pflanzen des Samens
        self.actions_taken: int = 1
        self.fertilized_total_eur: float = 0.0

    def record_passive_observation_tick(self, dormant: bool) -> None:
        # Gärtner schaut im Schnitt nur wenige Minuten pro Tag auf den Erntestatus
        self.attention_hours_cumulative = round(
            self.attention_hours_cumulative + (0.03 if dormant else 0.08), 3
        )

    def record_gardener_action(self, hours: float = 0.25) -> None:
        self.actions_taken += 1
        self.attention_hours_cumulative = round(self.attention_hours_cumulative + hours, 3)

    def to_telemetry(self, gardener_profit_eur: float) -> OrganelleTelemetry:
        eur_per_hr = gardener_profit_eur / max(0.5, self.attention_hours_cumulative)
        return OrganelleTelemetry(
            id="gardener_interface",
            name_de="Gärtner-Schnittstelle & Benchmark",
            system_id="viability",
            health=1.0,
            activity=0.40,
            load=0.10,
            efficiency=round(min(2.0, eur_per_hr / 100.0), 3),
            state_label_de=f"{self.attention_hours_cumulative:.1f} Std. Aufwand · {eur_per_hr:.1f} €/Std.",
            metrics={
                "attention_hours_cumulative": round(self.attention_hours_cumulative, 2),
                "actions_taken": self.actions_taken,
                "fertilized_total_eur": self.fertilized_total_eur,
                "profit_per_attention_hour": round(eur_per_hr, 2),
            },
        )


@dataclass
class EngineerControlBaseline:
    """Kontrollgruppe: klassische manuell gesteuerte Ingenieurs-Maschine auf demselben Markt."""

    profile: ScaleEconomicsProfile
    cumulative_profit_eur: float = 0.0
    attention_hours_cumulative: float = 18.0  # Aufbau der statischen Pipeline
    incidents_total: int = 0
    _lagged_price: float = 0.0
    _sprint_day_counter: int = 0
    _cached_efficiency: float = 0.18
    _manual_defense: float = 0.48

    def __post_init__(self) -> None:
        self._lagged_price = self.profile.base_price_eur

    def step(
        self,
        market: MarketTickState,
        base_demand_units: float,
    ) -> BenchmarkPoint:
        raise NotImplementedError("Nutze step_with_gardener()")

    def step_with_gardener(
        self,
        market: MarketTickState,
        base_demand_units: float,
        gardener_profit_eur: float,
        gardener_attention_hours: float,
        active_organelles_count: int,
    ) -> BenchmarkPoint:
        self._sprint_day_counter += 1
        # Ingenieur braucht täglich ~1.9 Std. Monitoring, Prompt-Pflege & Tickets
        daily_hours = 1.95
        if market.active_shocks:
            # Bei Schocks eskaliert manueller Firefighting-Aufwand
            daily_hours += 2.2 * len(market.active_shocks)

        # Ingenieur reagiert träge im 7-Tage-Sprint auf Marktänderungen
        if self._sprint_day_counter % 7 == 0:
            self._lagged_price = round(
                max(
                    self.profile.min_price_eur,
                    self.profile.base_price_eur * (1.0 - market.competitor_pressure * 0.35),
                ),
                2,
            )
            self._cached_efficiency = min(0.32, self._cached_efficiency + 0.02)
            self._manual_defense = min(0.75, self._manual_defense + 0.03)
            daily_hours += 1.5

        self.attention_hours_cumulative = round(self.attention_hours_cumulative + daily_hours, 2)

        # Nachfrage des statischen Systems ohne Thylakoide/Fimbrien/Kapsel-Zinseszins
        demand_mult = max(0.12, market.macro_demand_index * (1.0 - market.competitor_pressure * 0.25))
        orders = min(
            self.profile.max_capacity_per_day,
            max(0, int(round(base_demand_units * 0.72 * demand_mult))),
        )
        revenue = orders * self._lagged_price

        # Höhere COGS (kein starker Glykogen-Cache, keine Metabolosom-Arbitrage)
        unit_cogs = (
            self.profile.raw_compute_cost_per_unit_eur
            * market.compute_cost_multiplier
            * (1.0 - self._cached_efficiency)
        )
        cogs = orders * unit_cogs
        fees = orders * (self._lagged_price * self.profile.payment_fee_rate + self.profile.payment_fee_fixed_eur)

        # Ingenieur kann Infrastruktur in Rezessionen nicht automatisch um 93 % dehydrieren
        infra = self.profile.fixed_infra_per_day_eur * 1.15
        marketing = self.profile.base_marketing_budget_eur * (0.85 if market.macro_demand_index > 0.5 else 0.40)

        # Incident-Verluste durch fehlende autonome S-Layer/LPS/Encapsulin-Reflexe
        incident_loss = 0.0
        if market.cyber_threat_level > 0.22:
            leak = max(0.05, market.cyber_threat_level - self._manual_defense * 0.65)
            incident_loss += revenue * leak * 0.25 + infra * 0.45
            self.incidents_total += 1
        if market.audit_active:
            incident_loss += max(2.0, revenue * 0.14)
            self.incidents_total += 1

        op_profit = revenue - cogs - fees - infra - marketing - incident_loss
        tax = max(0.0, op_profit * self.profile.tax_reserve_rate)
        net_profit = op_profit - tax
        self.cumulative_profit_eur = round(self.cumulative_profit_eur + net_profit, 2)

        g_hr = max(0.5, gardener_attention_hours)
        e_hr = max(0.5, self.attention_hours_cumulative)

        return BenchmarkPoint(
            day=market.day,
            gardener_profit_eur=round(gardener_profit_eur, 2),
            engineer_profit_eur=self.cumulative_profit_eur,
            gardener_attention_hours=round(gardener_attention_hours, 2),
            engineer_attention_hours=self.attention_hours_cumulative,
            gardener_profit_per_hour=round(gardener_profit_eur / g_hr, 2),
            engineer_profit_per_hour=round(self.cumulative_profit_eur / e_hr, 2),
            gardener_complexity_score=round(active_organelles_count * 1.65, 1),
            engineer_complexity_score=24.0,
            gardener_active_modules=active_organelles_count,
            engineer_incidents_total=self.incidents_total,
        )
