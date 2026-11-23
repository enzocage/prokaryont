"""Motilität, Marktnavigation, Lead-Hooks, Partner-Pili & Sexpili-Plasmidhandel."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.genetics.plasmids import CodePlasmid, PlasmidMarketplace, PlasmidRegistry
from prokaryont.models import OrganelleTelemetry


@dataclass
class BasalBody:
    """Basalkörper: ATP-getriebener Marketing- & Wachstums-Budget-Motor."""

    atp_spent_today: float = 0.0
    eur_budget_today: float = 0.0
    rpm: float = 0.45

    def spin(
        self,
        atp_available: float,
        target_share: float,
        base_marketing_budget_eur: float,
        fertilizer_active: bool,
    ) -> float:
        atp_to_burn = min(atp_available * 0.45, max(0.0, atp_available * target_share))
        self.atp_spent_today = round(atp_to_burn, 3)
        boost = 1.45 if fertilizer_active else 1.0
        # Wandelt ATP-Antrieb direkt in effektives Outbound-Budget um
        atp_factor = min(1.85, max(0.25, atp_to_burn / 12.0))
        self.eur_budget_today = round(base_marketing_budget_eur * atp_factor * boost, 2)
        self.rpm = round(min(1.0, atp_factor / 1.6), 3)
        return self.eur_budget_today

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="basal_body",
            name_de="Basalkörper (Growth-Motor)",
            system_id="motility",
            health=1.0,
            activity=self.rpm,
            load=self.rpm,
            efficiency=1.0,
            state_label_de=f"Drehzahl {self.rpm * 100:.0f} % · {self.eur_budget_today:.2f} €/Tag",
            metrics={
                "atp_spent_today": self.atp_spent_today,
                "eur_budget_today": self.eur_budget_today,
                "rpm": self.rpm,
            },
        )


@dataclass
class FlagellarHook:
    """Haken: überträgt Strategie-Richtung auf konkrete Akquisitionskanäle."""

    active_channel: str = "b2b_direct_search"
    coupling_efficiency: float = 0.90

    def couple(self, heading_channel: str, competitor_pressure: float) -> str:
        self.active_channel = heading_channel
        self.coupling_efficiency = round(max(0.72, 0.96 - competitor_pressure * 0.25), 3)
        return self.active_channel

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="flagellar_hook",
            name_de="Haken (Kanal-Kupplung)",
            system_id="motility",
            health=1.0,
            activity=0.75,
            load=0.30,
            efficiency=self.coupling_efficiency,
            state_label_de=f"Kanal: {self.active_channel}",
            metrics={
                "active_channel": self.active_channel,
                "coupling_efficiency": self.coupling_efficiency,
            },
        )


@dataclass
class FlagellarFilament:
    """Flagellenfilament: erzeugt reale Outbound-Reichweite im externen Markt."""

    reach_multiplier: float = 1.0

    def propel(self, motor_rpm: float, coupling_eff: float, fertilizer_active: bool) -> float:
        boost = 1.18 if fertilizer_active else 1.0
        self.reach_multiplier = round((0.78 + motor_rpm * 0.58 * coupling_eff) * boost, 4)
        return self.reach_multiplier

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="flagellar_filament",
            name_de="Flagellenfilament (Outbound-Propeller)",
            system_id="motility",
            health=1.0,
            activity=min(1.0, self.reach_multiplier / 1.5),
            load=0.45,
            efficiency=self.reach_multiplier,
            state_label_de=f"Reichweite ×{self.reach_multiplier:.2f}",
            metrics={"reach_multiplier": self.reach_multiplier},
        )


class FlagellumSystem:
    """Chemotaxis-Marktnavigation (inkl. gemergter Archaellen-Rolle)."""

    def __init__(self) -> None:
        self.basal_body = BasalBody()
        self.hook = FlagellarHook()
        self.filament = FlagellarFilament()
        self.chemotaxis_score: float = 0.65

    def navigate(
        self,
        atp_available: float,
        target_share: float,
        base_marketing_budget_eur: float,
        preferred_channel: str,
        competitor_pressure: float,
        fertilizer_active: bool,
    ) -> tuple[float, float, float]:
        budget = self.basal_body.spin(
            atp_available=atp_available,
            target_share=target_share,
            base_marketing_budget_eur=base_marketing_budget_eur,
            fertilizer_active=fertilizer_active,
        )
        self.hook.couple(preferred_channel, competitor_pressure)
        reach = self.filament.propel(
            self.basal_body.rpm,
            self.hook.coupling_efficiency,
            fertilizer_active=fertilizer_active,
        )
        self.chemotaxis_score = round(min(1.0, reach * 0.65), 3)
        return budget, reach, self.basal_body.atp_spent_today

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="flagella",
            name_de="Flagellen (Chemotaxis-Navigation)",
            system_id="motility",
            health=1.0,
            activity=self.basal_body.rpm,
            load=self.basal_body.rpm,
            efficiency=self.filament.reach_multiplier,
            state_label_de=f"Kurs: {self.hook.active_channel} · ×{self.filament.reach_multiplier:.2f}",
            metrics={
                "channel": self.hook.active_channel,
                "reach_multiplier": self.filament.reach_multiplier,
                "marketing_spend_eur": self.basal_body.eur_budget_today,
            },
        )


@dataclass
class Fimbriae:
    """Fimbrien: hochfrequente Lead-Capture-Hooks, Free-Tools & Viralschleifen."""

    capture_rate: float = 0.14
    leads_captured_today: int = 0

    def capture(self, intensity: float, organic_bonus: float, base_demand: float) -> float:
        self.capture_rate = round(min(0.45, 0.08 + intensity * 0.14 + organic_bonus), 4)
        self.leads_captured_today = int(round(base_demand * self.capture_rate))
        return round(1.0 + self.capture_rate, 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="fimbriae",
            name_de="Fimbrien (Lead-Capture-Hooks)",
            system_id="motility",
            health=1.0,
            activity=min(1.0, self.capture_rate * 2.5),
            load=0.35,
            efficiency=round(1.0 + self.capture_rate, 3),
            state_label_de=f"+{self.leads_captured_today} Warm-Leads heute ({self.capture_rate*100:.0f} %)",
            metrics={
                "capture_rate": self.capture_rate,
                "leads_captured_today": self.leads_captured_today,
            },
        )


@dataclass
class Pili:
    """Pili: aktive B2B-Partner- & API-/Webhook-Verbindungen für Stammkunden."""

    active_integrations: int = 2
    retention_boost: float = 0.08

    def engage(self, focus: float, active_customers: int) -> float:
        self.active_integrations = max(1, int(round(active_customers * (0.04 + focus * 0.05))))
        self.retention_boost = round(min(0.24, 0.04 + focus * 0.14), 4)
        return self.retention_boost

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="pili",
            name_de="Pili (B2B-Partner-Brücken)",
            system_id="motility",
            health=1.0,
            activity=min(1.0, self.active_integrations / 15.0),
            load=0.30,
            efficiency=round(1.0 + self.retention_boost, 3),
            state_label_de=f"{self.active_integrations} Partner-Links · +{self.retention_boost*100:.0f} % Retention",
            metrics={
                "active_integrations": self.active_integrations,
                "retention_boost": self.retention_boost,
            },
        )


class SexPili:
    """Sexpili: Konjugationsbrücke für Plasmid-Erwerb & Lizenz-Erlöse am Marktplatz."""

    def __init__(self, marketplace: PlasmidMarketplace) -> None:
        self.marketplace = marketplace
        self.acquired_count: int = 0
        self.last_trade_day: int | None = None
        self.licensing_revenue_today_eur: float = 0.0

    def conjugate(
        self,
        day: int,
        registry: PlasmidRegistry,
        auto_trade: bool,
        available_cash_eur: float,
        available_atp: float,
        market_threat: float,
        audit_active: bool,
        compute_mult: float,
        competitor_pressure: float,
        fitness_score: float,
        capsule_strength: float,
    ) -> tuple[CodePlasmid | None, float, float]:
        """Kauft bei Bedarf ein ROI-starkes Plasmid und erzielt Lizenz-Einnahmen."""
        spent = 0.0
        acquired: CodePlasmid | None = None
        if auto_trade and day >= 4 and (self.last_trade_day is None or day - self.last_trade_day >= 10):
            candidate = self.marketplace.pick_best_acquisition(
                registry=registry,
                available_cash_eur=available_cash_eur,
                available_atp=available_atp,
                market_threat=market_threat,
                audit_active=audit_active,
                compute_mult=compute_mult,
                competitor_pressure=competitor_pressure,
            )
            if candidate is not None:
                registry.install(candidate.info.plasmid_id, day=day)
                spent = candidate.info.price_eur
                self.marketplace.total_spent_eur += spent
                self.acquired_count += 1
                self.last_trade_day = day
                acquired = candidate

        lic_income = self.marketplace.compute_daily_licensing_revenue(
            registry=registry,
            fitness_score=fitness_score,
            capsule_strength=capsule_strength,
        )
        self.licensing_revenue_today_eur = lic_income
        return acquired, spent, lic_income

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="sex_pili",
            name_de="Sexpili (Plasmid-Konjugation)",
            system_id="motility",
            health=1.0,
            activity=0.70 if self.acquired_count > 0 else 0.25,
            load=0.25,
            efficiency=1.0,
            state_label_de=(
                f"{self.acquired_count} Plasmide erworben · "
                f"{self.marketplace.total_licensing_income_eur:.1f} € Lizenzerlös"
            ),
            metrics={
                "acquired_count": self.acquired_count,
                "licensing_revenue_today_eur": self.licensing_revenue_today_eur,
                "total_licensing_income_eur": round(self.marketplace.total_licensing_income_eur, 2),
                "total_spent_eur": round(self.marketplace.total_spent_eur, 2),
            },
        )
