"""Realistische Wirtschaftsumwelt mit Saisonalität, Wettbewerb, Betrug & Schocks."""

from __future__ import annotations

import math
import random

from prokaryont.config import (
    ScaleEconomicsProfile,
    ScenarioProfile,
    SeedTemplate,
    ShockType,
)
from prokaryont.models import CustomerRequest, MarketTickState, ShockEvent


_SHOCK_LABELS: dict[ShockType, str] = {
    ShockType.DEMAND_BOOM: "Nachfrage-Boom (Branchen-Hype)",
    ShockType.PRICE_WAR: "Aggressiver Preiskrieg durch Billig-Anbieter",
    ShockType.COMPUTE_SHOCK: "Compute-/Token-Preisschock (+85 %)",
    ShockType.CYBER_STORM: "Cyber-, Bot- & Chargeback-Sturm",
    ShockType.COMPLIANCE_AUDIT: "Behördliches EU-AI-Act / DSGVO-Audit",
    ShockType.RECESSION_DROUGHT: "Schwere Markt-Dürre / Rezession (-85 % Nachfrage)",
}


class RealisticEconomicEnvironment:
    """Generiert reale Marktbedingungen, externe Schocks und Kunden-Orderströme."""

    def __init__(
        self,
        economics: ScaleEconomicsProfile,
        scenario: ScenarioProfile,
        rng: random.Random,
    ) -> None:
        self.economics = economics
        self.scenario = scenario
        self.rng = rng
        self.active_shocks: list[ShockEvent] = []
        self._triggered_scheduled: set[tuple[int, ShockType]] = set()
        self._order_seq: int = 0

    def trigger_manual_shock(
        self,
        day: int,
        shock_type: ShockType,
        duration_days: int = 10,
        intensity: float = 0.75,
    ) -> ShockEvent:
        ev = ShockEvent(
            shock_type=shock_type,
            label_de=_SHOCK_LABELS[shock_type],
            start_day=day,
            end_day=day + duration_days - 1,
            intensity=intensity,
            source="manual",
        )
        self.active_shocks.append(ev)
        return ev

    def step_market(self, day: int) -> MarketTickState:
        # Abgelaufene Schocks entfernen
        self.active_shocks = [s for s in self.active_shocks if s.end_day >= day]

        # Geplante Szenario-Schocks aktivieren
        for start_day, s_type, duration, intensity in self.scenario.scheduled_shocks:
            key = (start_day, s_type)
            if start_day == day and key not in self._triggered_scheduled:
                self._triggered_scheduled.add(key)
                self.active_shocks.append(
                    ShockEvent(
                        shock_type=s_type,
                        label_de=_SHOCK_LABELS[s_type],
                        start_day=day,
                        end_day=day + duration - 1,
                        intensity=intensity,
                        source="scheduled",
                    )
                )

        # Saisonaler Rhythmus (30- und 90-Tage-B2B-Wellen) + leichtes Rauschen
        season = 1.0 + self.scenario.seasonal_amplitude * (
            0.65 * math.sin(day / 14.0) + 0.35 * math.cos(day / 45.0)
        )
        noise = self.rng.uniform(-0.05, 0.05)
        demand_idx = max(0.18, self.scenario.demand_multiplier * season + noise)

        comp_pressure = self.scenario.competitor_pressure_base + max(0.0, math.sin(day / 28.0) * 0.06)
        compute_mult = self.scenario.compute_inflation_base + self.rng.uniform(-0.04, 0.06)
        threat_level = self.scenario.cyber_threat_base + self.rng.uniform(0.0, 0.04)
        fraud_share = 0.025 + threat_level * 0.25
        audit_active = self.rng.random() < self.scenario.audit_probability_daily
        audit_severity = 0.72 if audit_active else 0.0

        for shock in self.active_shocks:
            if shock.shock_type == ShockType.DEMAND_BOOM:
                demand_idx *= 1.0 + 0.55 * shock.intensity
            elif shock.shock_type == ShockType.PRICE_WAR:
                comp_pressure = min(0.95, comp_pressure + 0.45 * shock.intensity)
            elif shock.shock_type == ShockType.COMPUTE_SHOCK:
                compute_mult *= 1.0 + 0.95 * shock.intensity
            elif shock.shock_type == ShockType.CYBER_STORM:
                threat_level = min(0.96, threat_level + 0.65 * shock.intensity)
                fraud_share = min(0.45, fraud_share + 0.24 * shock.intensity)
            elif shock.shock_type == ShockType.COMPLIANCE_AUDIT:
                audit_active = True
                audit_severity = max(audit_severity, min(0.98, 0.76 + 0.20 * shock.intensity))
            elif shock.shock_type == ShockType.RECESSION_DROUGHT:
                demand_idx *= max(0.09, 1.0 - 0.88 * shock.intensity)

        ref_price = round(
            self.economics.base_price_eur * max(0.68, 1.0 - comp_pressure * 0.28), 2
        )
        headline = (
            self.active_shocks[0].label_de
            if self.active_shocks
            else (
                "Behördliche Stichprobenprüfung aktiv"
                if audit_active
                else "Normale dynamische B2B-Marktlage"
            )
        )

        return MarketTickState(
            day=day,
            season_factor=round(season, 3),
            macro_demand_index=round(demand_idx, 3),
            competitor_pressure=round(min(1.0, comp_pressure), 3),
            market_reference_price_eur=ref_price,
            compute_cost_multiplier=round(max(0.65, compute_mult), 3),
            cyber_threat_level=round(min(1.0, threat_level), 3),
            fraud_share=round(min(0.55, fraud_share), 3),
            audit_active=audit_active,
            audit_severity=round(audit_severity, 3),
            active_shocks=list(self.active_shocks),
            headline_de=headline,
        )

    def generate_requests(
        self,
        market: MarketTickState,
        organism_price_eur: float,
        elasticity_mult: float,
        organic_thylakoid_mult: float,
        flagellum_reach_mult: float,
        fimbriae_lead_mult: float,
        lifecycle_mult: float,
        plasmid_demand_bonus: float,
        buoyancy: float,
        dormant: bool,
    ) -> list[CustomerRequest]:
        if dormant:
            return []

        raw_mult = (
            elasticity_mult
            * organic_thylakoid_mult
            * (0.62 + flagellum_reach_mult * 0.38)
            * fimbriae_lead_mult
            * lifecycle_mult
            * (1.0 + plasmid_demand_bonus)
        )
        # Realistisches B2B-Wachstumsdach (verhindert unrealistisches exponentielles Weglaufen)
        bounded_internal_mult = min(2.35, 0.55 + (raw_mult - 0.55) * 0.65)
        total_mult = market.macro_demand_index * max(0.08, bounded_internal_mult)
        legit_count = max(
            0,
            int(round(self.economics.base_daily_demand * total_mult)),
        )
        # Begrenze Order-Erzeugung auf realistische Tagesspitzen
        legit_count = min(self.economics.max_capacity_per_day * 2, legit_count)

        # Bei Micro-API bündeln wir Orders in Paketen für schnelle Simulation bei exakt skalierter Ökonomie
        topics = (
            ("eu_ai_act", "market_intel", "supply_chain")
            if self.economics.seed == SeedTemplate.B2B_BRIEFING
            else ("kyb_verify", "vat_check", "fraud_score")
        )
        channels = ("seo_thylakoid", "b2b_pili_api", "fimbriae_hook", "flagellum_outbound")

        requests: list[CustomerRequest] = []
        for i in range(legit_count):
            self._order_seq += 1
            roll = self.rng.random()
            if roll < buoyancy * 0.45:
                segment = "premium"
                price = round(organism_price_eur * 1.18, 2)
            elif roll < 0.80:
                segment = "standard"
                price = round(organism_price_eur, 2)
            else:
                segment = "niche"
                price = round(organism_price_eur * 0.92, 2)

            is_fraud = self.rng.random() < (market.fraud_share * 0.35)
            requests.append(
                CustomerRequest(
                    request_id=f"req-{self._order_seq}",
                    channel=channels[i % len(channels)],
                    segment=segment,  # type: ignore[arg-type]
                    offered_price_eur=price,
                    complexity=round(self.rng.uniform(0.30, 0.92), 2),
                    is_malicious=False,
                    is_fraudulent=is_fraud,
                    topic_key=topics[i % len(topics)],
                    customer_id=f"cust-{(self._order_seq % 45) + 1:03d}",
                    compliance_sensitive=(i % 3 == 0),
                )
            )

        # Malicious Bot-/Injection-Traffic skaliert mit Cyber-Bedrohung
        attack_count = int(round(max(1, legit_count * 0.12) * market.cyber_threat_level * 2.8))
        for j in range(attack_count):
            self._order_seq += 1
            requests.append(
                CustomerRequest(
                    request_id=f"atk-{self._order_seq}",
                    channel="public_edge",
                    segment="standard",
                    offered_price_eur=0.0 if j % 2 == 0 else organism_price_eur,
                    complexity=round(self.rng.uniform(0.35, 0.96), 2),
                    is_malicious=True,
                    is_fraudulent=(j % 2 == 1),
                    topic_key=topics[0],
                    customer_id=f"bot-{j}",
                    compliance_sensitive=True,
                )
            )

        return requests
