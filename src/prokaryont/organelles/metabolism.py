"""Stoffwechsel, ATP-Energiegewinnung, Thylakoide, Mikrokompartimente & Sensorik."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.models import OrganelleTelemetry


@dataclass
class ElectronTransportChain:
    """Elektronentransportkette: berechnet echte Netto-Wertschöpfung & Protonengradient."""

    proton_gradient: float = 0.0
    conversion_efficiency: float = 0.88

    def process_flow(
        self,
        gross_revenue_eur: float,
        payment_fees_eur: float,
        cogs_eur: float,
        fixed_infra_eur: float,
        tax_rate: float,
    ) -> float:
        operating_surplus = max(
            0.0, gross_revenue_eur - payment_fees_eur - cogs_eur - fixed_infra_eur
        )
        after_tax_surplus = operating_surplus * (1.0 - tax_rate)
        self.proton_gradient = round(after_tax_surplus, 4)
        self.conversion_efficiency = (
            round(after_tax_surplus / gross_revenue_eur, 4)
            if gross_revenue_eur > 0
            else 0.0
        )
        return self.proton_gradient

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="etc",
            name_de="Elektronentransportkette",
            system_id="metabolism",
            health=1.0,
            activity=min(1.0, self.proton_gradient / 50.0),
            load=0.50,
            efficiency=self.conversion_efficiency,
            state_label_de=f"Gradient {self.proton_gradient:.2f} € · Wirkungsgrad {self.conversion_efficiency*100:.1f} %",
            metrics={
                "proton_gradient_eur": round(self.proton_gradient, 2),
                "conversion_efficiency": self.conversion_efficiency,
            },
        )


@dataclass
class ATPSynthase:
    """ATP-Synthase: wandelt den Netto-Margen-Gradienten in operationales Compute-/Wachstums-ATP."""

    atp_balance: float = 40.0
    generated_today: float = 0.0
    consumed_today: float = 0.0

    def synthesize(self, proton_gradient_eur: float, scale_factor: float) -> float:
        # 1 ATP entspricht ~0.50 € * scale_factor operativem Handlungsspielraum
        unit_scale = max(0.25, scale_factor)
        generated = round((proton_gradient_eur / unit_scale) * 0.9, 3)
        self.generated_today = generated
        self.atp_balance = round(min(220.0, self.atp_balance + generated), 3)
        return generated

    def consume(self, amount: float) -> float:
        used = min(self.atp_balance, max(0.0, amount))
        self.atp_balance = round(self.atp_balance - used, 3)
        self.consumed_today = round(self.consumed_today + used, 3)
        return used

    def reset_daily_counters(self) -> None:
        self.generated_today = 0.0
        self.consumed_today = 0.0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="atp_synthase",
            name_de="ATP-Synthase (Energie-Allokator)",
            system_id="metabolism",
            health=1.0 if self.atp_balance > 8 else 0.55,
            activity=min(1.0, self.atp_balance / 80.0),
            load=min(1.0, self.consumed_today / 40.0),
            efficiency=1.0,
            state_label_de=f"{self.atp_balance:.1f} ATP (+{self.generated_today:.1f} / -{self.consumed_today:.1f})",
            metrics={
                "atp_balance": self.atp_balance,
                "generated_today": self.generated_today,
                "consumed_today": self.consumed_today,
            },
        )


@dataclass
class Phycobilisomes:
    """Phycobilisomen (inkl. gemergter Chlorosomen): Nischen-Antennen für schwache Signale."""

    niche_sensitivity: float = 0.72
    niche_orders_harvested_today: int = 0

    def harvest_niche_demand(self, base_demand: float, capsule_strength: float) -> float:
        factor = 0.08 + self.niche_sensitivity * 0.10 + capsule_strength * 0.06
        self.niche_orders_harvested_today = max(0, int(round(base_demand * factor)))
        return round(factor, 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="phycobilisomes",
            name_de="Phycobilisomen (Nischen-Antennen)",
            system_id="metabolism",
            health=1.0,
            activity=self.niche_sensitivity,
            load=0.30,
            efficiency=round(1.0 + self.niche_sensitivity * 0.25, 3),
            state_label_de=f"+{self.niche_orders_harvested_today} Nischen-Signale (High-Sensitivity)",
            metrics={
                "niche_sensitivity": self.niche_sensitivity,
                "niche_orders_today": self.niche_orders_harvested_today,
            },
        )


class Thylakoids:
    """Thylakoide: passive organische Inbound-Flächen (SEO, API-Verzeichnisse, Evergreen-Briefings)."""

    def __init__(self) -> None:
        self.phycobilisomes = Phycobilisomes()
        self.surface_maturity: float = 0.28
        self.organic_demand_multiplier: float = 1.0

    def photosynthesize_inbound(
        self,
        day: int,
        capsule_strength: float,
        base_demand: float,
        dormant: bool,
    ) -> float:
        if dormant:
            return 0.05
        # Organische Präsenz reift über Wochen wie Pflanzenblätter
        self.surface_maturity = round(
            min(0.95, 0.25 + (day / 160.0) * 0.50 + capsule_strength * 0.20),
            4,
        )
        niche_add = self.phycobilisomes.harvest_niche_demand(base_demand, capsule_strength)
        self.organic_demand_multiplier = round(0.85 + self.surface_maturity * 0.65 + niche_add, 4)
        return self.organic_demand_multiplier

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="thylakoids",
            name_de="Thylakoide (Organischer Inbound)",
            system_id="metabolism",
            health=1.0,
            activity=self.surface_maturity,
            load=0.25,
            efficiency=self.organic_demand_multiplier,
            state_label_de=f"Reife {self.surface_maturity*100:.0f} % · Inbound ×{self.organic_demand_multiplier:.2f}",
            metrics={
                "surface_maturity": self.surface_maturity,
                "organic_demand_multiplier": self.organic_demand_multiplier,
            },
        )


@dataclass
class MicrocompartmentFramework:
    """Basis-Rahmen der Bakterien-Mikrokompartimente (BMCs) für isolierte Zonen."""

    active_compartments: int = 3
    isolation_integrity: float = 0.98

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="microcompartments",
            name_de="Mikrokompartimente (BMC-Container)",
            system_id="metabolism",
            health=self.isolation_integrity,
            activity=0.80,
            load=0.40,
            efficiency=self.isolation_integrity,
            state_label_de=f"{self.active_compartments} isolierte Protein-Kammern aktiv",
            metrics={
                "active_compartments": self.active_compartments,
                "isolation_integrity": self.isolation_integrity,
            },
        )


@dataclass
class Carboxysomes:
    """Carboxysomen: Wertkonzentrations-Kammer zur Erhöhung der Marge pro Token."""

    concentration_gain: float = 1.15
    refined_today: int = 0

    def concentrate_value(
        self,
        cache_hit: bool,
        sulfur_ready: bool,
        raw_cost_eur: float,
    ) -> float:
        self.refined_today += 1
        multiplier = 0.34 if cache_hit else 0.78
        if sulfur_ready:
            multiplier *= 0.88
        self.concentration_gain = round(1.0 / max(0.25, multiplier), 2)
        return round(raw_cost_eur * multiplier, 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="carboxysomes",
            name_de="Carboxysomen (Wert-Konzentration)",
            system_id="metabolism",
            health=1.0,
            activity=min(1.0, self.refined_today / 40.0 + 0.2),
            load=0.45,
            efficiency=self.concentration_gain,
            state_label_de=f"Konzentrations-Faktor ×{self.concentration_gain:.2f} · {self.refined_today} veredelt",
            metrics={
                "concentration_gain": self.concentration_gain,
                "refined_today": self.refined_today,
            },
        )


@dataclass
class Metabolosomes:
    """Metabolosomen: isolierte Fehler-, Retry- & Kosten-Arbitrage-Kammer."""

    arbitrage_savings_today_eur: float = 0.0
    retries_recovered_today: int = 0

    def arbitrage_and_recover(
        self,
        unit_cost_eur: float,
        arbitrage_ratio: float,
        plasmid_discount: float,
        dirty_input: bool,
    ) -> tuple[float, bool]:
        discount = min(0.45, arbitrage_ratio * 0.28 + plasmid_discount)
        new_cost = round(unit_cost_eur * (1.0 - discount), 4)
        self.arbitrage_savings_today_eur = round(
            self.arbitrage_savings_today_eur + max(0.0, unit_cost_eur - new_cost), 4
        )
        recovered = True
        if dirty_input:
            self.retries_recovered_today += 1
        return new_cost, recovered

    def reset_daily(self) -> None:
        self.arbitrage_savings_today_eur = 0.0
        self.retries_recovered_today = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="metabolosomes",
            name_de="Metabolosomen (Kosten-Arbitrage)",
            system_id="metabolism",
            health=1.0,
            activity=0.65,
            load=0.35,
            efficiency=1.2,
            state_label_de=f"{self.arbitrage_savings_today_eur:.2f} € heute durch Arbitrage gespart",
            metrics={
                "arbitrage_savings_today_eur": round(self.arbitrage_savings_today_eur, 2),
                "retries_recovered_today": self.retries_recovered_today,
            },
        )


@dataclass
class Encapsulins:
    """Encapsuline: PII-/Secret-Tresor & Entgiftung sensibler Payloads."""

    scrubbed_payloads_today: int = 0
    vault_integrity: float = 0.99

    def sanitize_and_seal(self, sensitive: bool, pii_redaction_level: float) -> bool:
        if sensitive:
            self.scrubbed_payloads_today += 1
        self.vault_integrity = round(min(0.999, 0.85 + pii_redaction_level * 0.145), 4)
        return True

    def reset_daily(self) -> None:
        self.scrubbed_payloads_today = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="encapsulins",
            name_de="Encapsuline (Secret- & PII-Tresor)",
            system_id="metabolism",
            health=self.vault_integrity,
            activity=min(1.0, self.scrubbed_payloads_today / 15.0 + 0.25),
            load=0.25,
            efficiency=self.vault_integrity,
            state_label_de=f"Tresor {self.vault_integrity*100:.1f} % · {self.scrubbed_payloads_today} PII bereinigt",
            metrics={
                "scrubbed_payloads_today": self.scrubbed_payloads_today,
                "vault_integrity": self.vault_integrity,
            },
        )


@dataclass
class Magnetosomes:
    """Magnetosomen: Makro-Trend-Kompass mit EMA-Glättung gegen Marktrauschen."""

    ema_demand: float = 1.0
    ema_competitor: float = 0.2
    trend_direction: str = "stabil"

    def sense(self, macro_demand_index: float, competitor_pressure: float) -> tuple[float, str]:
        prev = self.ema_demand
        self.ema_demand = round(self.ema_demand * 0.78 + macro_demand_index * 0.22, 4)
        self.ema_competitor = round(self.ema_competitor * 0.80 + competitor_pressure * 0.20, 4)
        if self.ema_demand > prev + 0.015:
            self.trend_direction = "wachsend"
        elif self.ema_demand < prev - 0.015:
            self.trend_direction = "rückläufig"
        else:
            self.trend_direction = "stabil"
        return self.ema_demand, self.trend_direction

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="magnetosomes",
            name_de="Magnetosomen (Trend-Kompass)",
            system_id="metabolism",
            health=1.0,
            activity=0.70,
            load=0.20,
            efficiency=1.0,
            state_label_de=f"Trend: {self.trend_direction} (EMA ×{self.ema_demand:.2f})",
            metrics={
                "ema_demand": self.ema_demand,
                "ema_competitor": self.ema_competitor,
                "trend_direction": self.trend_direction,
            },
        )


@dataclass
class GasVesicles:
    """Gasvesikel: dynamische Schwebehöhe zwischen Volumen- und Premium-Segment."""

    buoyancy: float = 0.55
    active_tier: str = "standard_und_premium"

    def adjust_buoyancy(
        self,
        competitor_pressure: float,
        capsule_strength: float,
        premium_bias: float,
    ) -> float:
        # Bei starkem Preiskrieg auftreiben ins margenstarke Premium-Segment
        target = min(
            0.95,
            max(0.25, 0.42 + competitor_pressure * 0.35 + capsule_strength * 0.22 + premium_bias * 0.25),
        )
        self.buoyancy = round(self.buoyancy * 0.7 + target * 0.3, 3)
        if self.buoyancy >= 0.68:
            self.active_tier = "premium_fokus"
        elif self.buoyancy >= 0.42:
            self.active_tier = "ausgewogen"
        else:
            self.active_tier = "volumen_tiefe"
        return self.buoyancy

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="gas_vesicles",
            name_de="Gasvesikel (Segment-Auftrieb)",
            system_id="metabolism",
            health=1.0,
            activity=self.buoyancy,
            load=0.25,
            efficiency=round(0.95 + self.buoyancy * 0.25, 3),
            state_label_de=f"Auftrieb {self.buoyancy*100:.0f} % ({self.active_tier})",
            metrics={
                "buoyancy": self.buoyancy,
                "active_tier": self.active_tier,
            },
        )
