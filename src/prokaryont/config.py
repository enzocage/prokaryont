"""Konfiguration, Saatgut-Templates, Skalen-Presets und Szenarien."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SeedTemplate(str, Enum):
    """Konkrete Saatgut-Produktvorlagen für den Stoffwechsel des Organismus."""

    B2B_BRIEFING = "b2b_briefing"
    MICRO_API = "micro_api"


class ScalePreset(str, Enum):
    """Ökonomische Größenordnungen (Saatkapital & Unit Economics)."""

    NANO = "nano"
    SOLOPRENEUR = "solopreneur"
    GROWTH = "growth"


class ScenarioPreset(str, Enum):
    """Kuratierte Simulationsszenarien der Wirtschaftsumwelt."""

    REALISTIC_ECOSYSTEM = "realistic_ecosystem"
    GROWTH_MARKET = "growth_market"
    PRICE_WAR_GAUNTLET = "price_war_gauntlet"
    DROUGHT_SURVIVAL = "drought_survival"
    CYBER_AND_AUDIT_STORM = "cyber_and_audit_storm"


class ShockType(str, Enum):
    """Auslösbare externe Schocks der Wirtschaftsumwelt."""

    DEMAND_BOOM = "demand_boom"
    PRICE_WAR = "price_war"
    COMPUTE_SHOCK = "compute_shock"
    CYBER_STORM = "cyber_storm"
    COMPLIANCE_AUDIT = "compliance_audit"
    RECESSION_DROUGHT = "recession_drought"


@dataclass(frozen=True)
class ScaleEconomicsProfile:
    """Realistische Unit Economics für eine Kombination aus Saatgut und Skala."""

    scale: ScalePreset
    seed: SeedTemplate
    label_de: str
    seed_capital_eur: float
    fixed_infra_per_day_eur: float
    base_price_eur: float
    min_price_eur: float
    max_price_eur: float
    raw_compute_cost_per_unit_eur: float
    base_daily_demand: float
    max_capacity_per_day: int
    payment_fee_rate: float
    payment_fee_fixed_eur: float
    base_marketing_budget_eur: float
    harvest_threshold_eur: float
    tax_reserve_rate: float
    price_elasticity: float


@dataclass(frozen=True)
class ScenarioProfile:
    """Rahmenparameter eines wirtschaftlichen Umweltszenarios."""

    scenario: ScenarioPreset
    name_de: str
    description_de: str
    demand_multiplier: float
    seasonal_amplitude: float
    competitor_pressure_base: float
    cyber_threat_base: float
    audit_probability_daily: float
    compute_inflation_base: float
    scheduled_shocks: tuple[tuple[int, ShockType, int, float], ...]
    # (start_day, shock_type, duration_days, intensity)


SEED_METADATA: dict[SeedTemplate, dict[str, str]] = {
    SeedTemplate.B2B_BRIEFING: {
        "name_de": "B2B-Wissens- & Compliance-Briefing",
        "short_de": "Automatisierte Dossiers & Marktanalysen",
        "product_unit_de": "Briefing-Dossier",
        "delivery_protocol": "briefing_markdown",
        "description_de": (
            "Verdichtet regulatorische Signale, Wettbewerbsdaten und Branchentrends "
            "zu sofort nutzbaren Markdown-/JSON-Entscheidungsbriefings."
        ),
    },
    SeedTemplate.MICRO_API: {
        "name_de": "Pay-per-Call Daten- & Validierungs-Micro-API",
        "short_de": "Echtzeit-Anreicherung & Risiko-Scoring",
        "product_unit_de": "API-Payload-Paket",
        "delivery_protocol": "rest_json_api",
        "description_de": (
            "Verarbeitet Firmen-, Transaktions- oder Compliance-Datensätze per "
            "Pay-per-Call-API mit deterministischer Schema-Garantie."
        ),
    },
}


ECONOMICS_PROFILES: dict[tuple[ScalePreset, SeedTemplate], ScaleEconomicsProfile] = {
    (ScalePreset.NANO, SeedTemplate.B2B_BRIEFING): ScaleEconomicsProfile(
        scale=ScalePreset.NANO,
        seed=SeedTemplate.B2B_BRIEFING,
        label_de="Nano-Prokaryont (100 € Saatgut · Micro-Briefings)",
        seed_capital_eur=100.0,
        fixed_infra_per_day_eur=2.40,
        base_price_eur=11.50,
        min_price_eur=6.50,
        max_price_eur=24.00,
        raw_compute_cost_per_unit_eur=1.75,
        base_daily_demand=1.8,
        max_capacity_per_day=14,
        payment_fee_rate=0.029,
        payment_fee_fixed_eur=0.25,
        base_marketing_budget_eur=2.8,
        harvest_threshold_eur=140.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.25,
    ),
    (ScalePreset.NANO, SeedTemplate.MICRO_API): ScaleEconomicsProfile(
        scale=ScalePreset.NANO,
        seed=SeedTemplate.MICRO_API,
        label_de="Nano-Prokaryont (100 € Saatgut · Micro-API)",
        seed_capital_eur=100.0,
        fixed_infra_per_day_eur=2.20,
        base_price_eur=0.55,
        min_price_eur=0.30,
        max_price_eur=1.40,
        raw_compute_cost_per_unit_eur=0.085,
        base_daily_demand=38.0,
        max_capacity_per_day=240,
        payment_fee_rate=0.029,
        payment_fee_fixed_eur=0.01,
        base_marketing_budget_eur=2.6,
        harvest_threshold_eur=140.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.30,
    ),
    (ScalePreset.SOLOPRENEUR, SeedTemplate.B2B_BRIEFING): ScaleEconomicsProfile(
        scale=ScalePreset.SOLOPRENEUR,
        seed=SeedTemplate.B2B_BRIEFING,
        label_de="Solopreneur-Nutzpflanze (1.000 € Saatgut · B2B-Briefings)",
        seed_capital_eur=1000.0,
        fixed_infra_per_day_eur=15.50,
        base_price_eur=49.00,
        min_price_eur=29.00,
        max_price_eur=119.00,
        raw_compute_cost_per_unit_eur=5.60,
        base_daily_demand=3.1,
        max_capacity_per_day=26,
        payment_fee_rate=0.029,
        payment_fee_fixed_eur=0.30,
        base_marketing_budget_eur=24.0,
        harvest_threshold_eur=1400.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.18,
    ),
    (ScalePreset.SOLOPRENEUR, SeedTemplate.MICRO_API): ScaleEconomicsProfile(
        scale=ScalePreset.SOLOPRENEUR,
        seed=SeedTemplate.MICRO_API,
        label_de="Solopreneur-Nutzpflanze (1.000 € Saatgut · Micro-API)",
        seed_capital_eur=1000.0,
        fixed_infra_per_day_eur=14.80,
        base_price_eur=0.98,
        min_price_eur=0.55,
        max_price_eur=2.40,
        raw_compute_cost_per_unit_eur=0.14,
        base_daily_demand=155.0,
        max_capacity_per_day=950,
        payment_fee_rate=0.029,
        payment_fee_fixed_eur=0.015,
        base_marketing_budget_eur=22.0,
        harvest_threshold_eur=1400.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.22,
    ),
    (ScalePreset.GROWTH, SeedTemplate.B2B_BRIEFING): ScaleEconomicsProfile(
        scale=ScalePreset.GROWTH,
        seed=SeedTemplate.B2B_BRIEFING,
        label_de="Wachstums-Kultur (10.000 € Saatgut · Enterprise-Briefings)",
        seed_capital_eur=10000.0,
        fixed_infra_per_day_eur=82.00,
        base_price_eur=175.00,
        min_price_eur=95.00,
        max_price_eur=420.00,
        raw_compute_cost_per_unit_eur=18.50,
        base_daily_demand=5.2,
        max_capacity_per_day=48,
        payment_fee_rate=0.024,
        payment_fee_fixed_eur=0.35,
        base_marketing_budget_eur=155.0,
        harvest_threshold_eur=12500.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.12,
    ),
    (ScalePreset.GROWTH, SeedTemplate.MICRO_API): ScaleEconomicsProfile(
        scale=ScalePreset.GROWTH,
        seed=SeedTemplate.MICRO_API,
        label_de="Wachstums-Kultur (10.000 € Saatgut · Enterprise-API)",
        seed_capital_eur=10000.0,
        fixed_infra_per_day_eur=78.00,
        base_price_eur=2.40,
        min_price_eur=1.30,
        max_price_eur=5.80,
        raw_compute_cost_per_unit_eur=0.34,
        base_daily_demand=340.0,
        max_capacity_per_day=2600,
        payment_fee_rate=0.024,
        payment_fee_fixed_eur=0.015,
        base_marketing_budget_eur=145.0,
        harvest_threshold_eur=12500.0,
        tax_reserve_rate=0.25,
        price_elasticity=1.15,
    ),
}


SCENARIO_PROFILES: dict[ScenarioPreset, ScenarioProfile] = {
    ScenarioPreset.REALISTIC_ECOSYSTEM: ScenarioProfile(
        scenario=ScenarioPreset.REALISTIC_ECOSYSTEM,
        name_de="Realistisches Ökosystem",
        description_de=(
            "Saisonale Zyklen, allmählicher Wettbewerbsdruck, sporadische Bot-Wellen, "
            "Compute-Schwankungen und jährliche Compliance-Prüfungen."
        ),
        demand_multiplier=1.0,
        seasonal_amplitude=0.16,
        competitor_pressure_base=0.18,
        cyber_threat_base=0.08,
        audit_probability_daily=0.022,
        compute_inflation_base=1.0,
        scheduled_shocks=(
            (38, ShockType.COMPUTE_SHOCK, 10, 0.55),
            (72, ShockType.CYBER_STORM, 8, 0.65),
            (108, ShockType.PRICE_WAR, 14, 0.50),
            (142, ShockType.COMPLIANCE_AUDIT, 6, 0.70),
        ),
    ),
    ScenarioPreset.GROWTH_MARKET: ScenarioProfile(
        scenario=ScenarioPreset.GROWTH_MARKET,
        name_de="Wachstumsmarkt (Rückenwind)",
        description_de=(
            "Starke B2B-Adaption von KI-Briefings & APIs bei moderatem Wettbewerb "
            "und wiederkehrenden Nachfrage-Schüben."
        ),
        demand_multiplier=1.28,
        seasonal_amplitude=0.12,
        competitor_pressure_base=0.12,
        cyber_threat_base=0.05,
        audit_probability_daily=0.015,
        compute_inflation_base=0.95,
        scheduled_shocks=(
            (25, ShockType.DEMAND_BOOM, 18, 0.75),
            (95, ShockType.DEMAND_BOOM, 16, 0.60),
        ),
    ),
    ScenarioPreset.PRICE_WAR_GAUNTLET: ScenarioProfile(
        scenario=ScenarioPreset.PRICE_WAR_GAUNTLET,
        name_de="Preiskrieg & Margendruck",
        description_de=(
            "Aggressive Wettbewerber drücken Marktpreise; nur Cache-Effizienz, "
            "Kosten-Arbitrage und Marken-Kapsel sichern die Marge."
        ),
        demand_multiplier=0.98,
        seasonal_amplitude=0.14,
        competitor_pressure_base=0.42,
        cyber_threat_base=0.10,
        audit_probability_daily=0.02,
        compute_inflation_base=1.12,
        scheduled_shocks=(
            (24, ShockType.PRICE_WAR, 25, 0.80),
            (75, ShockType.COMPUTE_SHOCK, 14, 0.65),
            (120, ShockType.PRICE_WAR, 22, 0.70),
        ),
    ),
    ScenarioPreset.DROUGHT_SURVIVAL: ScenarioProfile(
        scenario=ScenarioPreset.DROUGHT_SURVIVAL,
        name_de="Dürre & Rezessions-Überleben",
        description_de=(
            "Nach einem Startfenster folgt eine tiefe Rezession (-84 % Nachfrage). "
            "Der Organismus muss in den Endosporen-Ruhezustand schalten und später keimen."
        ),
        demand_multiplier=0.95,
        seasonal_amplitude=0.12,
        competitor_pressure_base=0.22,
        cyber_threat_base=0.07,
        audit_probability_daily=0.018,
        compute_inflation_base=1.05,
        scheduled_shocks=(
            (35, ShockType.RECESSION_DROUGHT, 34, 0.88),
            (115, ShockType.DEMAND_BOOM, 20, 0.55),
        ),
    ),
    ScenarioPreset.CYBER_AND_AUDIT_STORM: ScenarioProfile(
        scenario=ScenarioPreset.CYBER_AND_AUDIT_STORM,
        name_de="Cyber- & Compliance-Sturm",
        description_de=(
            "Massive DDoS-/Prompt-Injection-/Chargeback-Wellen kombiniert mit "
            "strengen EU-AI-Act- und DSGVO-Audits."
        ),
        demand_multiplier=1.02,
        seasonal_amplitude=0.14,
        competitor_pressure_base=0.20,
        cyber_threat_base=0.26,
        audit_probability_daily=0.05,
        compute_inflation_base=1.02,
        scheduled_shocks=(
            (20, ShockType.CYBER_STORM, 16, 0.90),
            (55, ShockType.COMPLIANCE_AUDIT, 10, 0.90),
            (95, ShockType.CYBER_STORM, 14, 0.85),
            (130, ShockType.COMPLIANCE_AUDIT, 8, 0.85),
        ),
    ),
}


def get_economics_profile(scale: ScalePreset, seed: SeedTemplate) -> ScaleEconomicsProfile:
    """Liefert das kalibrierte Ökonomie-Profil für Skala und Saatgut."""
    return ECONOMICS_PROFILES[(scale, seed)]


def get_scenario_profile(scenario: ScenarioPreset) -> ScenarioProfile:
    """Liefert das Szenario-Profil für die Wirtschaftsumwelt."""
    return SCENARIO_PROFILES[scenario]
