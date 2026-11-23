"""Pydantic-Domänenmodelle für den Wirtschaftsorganismus, Simulation & API."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

from prokaryont.config import ScalePreset, ScenarioPreset, SeedTemplate, ShockType


OrganelleStatus = Literal["active", "submodule", "merged", "excluded"]
OrganismMode = Literal["active", "conserving", "sporulating", "dormant_endospore", "germinating"]


class StructureRegistryEntry(BaseModel):
    """Kanonischer Eintrag in der 57-Prokaryonten- + 7-Viability-Matrix."""

    id: str
    german_name: str
    english_name: str
    system_id: str
    system_name_de: str
    category: Literal["prokaryote", "viability"]
    status: OrganelleStatus
    merged_into: str | None = None
    bio_function_de: str
    economic_analogy_de: str
    rationale_de: str
    code_symbol: str
    upstream_ids: list[str] = Field(default_factory=list)
    downstream_ids: list[str] = Field(default_factory=list)
    svg_anchor: str = ""


class OrganelleTelemetry(BaseModel):
    """Laufzeit-Telemetrie einer einzelnen Organelle oder eines Viability-Moduls."""

    id: str
    name_de: str
    system_id: str
    health: float = Field(ge=0.0, le=1.0)
    activity: float = Field(ge=0.0, le=1.0)
    load: float = Field(ge=0.0, le=1.0)
    efficiency: float = Field(ge=0.0, le=20.0)
    state_label_de: str
    metrics: dict[str, float | int | str | bool] = Field(default_factory=dict)


class ShockEvent(BaseModel):
    """Aktiver oder historischer externer Schock in der Wirtschaftsumwelt."""

    shock_type: ShockType
    label_de: str
    start_day: int
    end_day: int
    intensity: float = Field(ge=0.0, le=1.5)
    source: Literal["scheduled", "stochastic", "manual"] = "scheduled"


class MarketTickState(BaseModel):
    """Zustand der realistischen Wirtschaftsumwelt in einem Tag-Tick."""

    day: int
    season_factor: float
    macro_demand_index: float
    competitor_pressure: float
    market_reference_price_eur: float
    compute_cost_multiplier: float
    cyber_threat_level: float
    fraud_share: float
    audit_active: bool
    audit_severity: float
    active_shocks: list[ShockEvent] = Field(default_factory=list)
    headline_de: str


class CustomerRequest(BaseModel):
    """Eingehende Kundenanfrage oder Angriffspaket an der äußeren Membran."""

    request_id: str
    channel: str
    segment: Literal["standard", "premium", "niche"]
    offered_price_eur: float
    complexity: float
    is_malicious: bool = False
    is_fraudulent: bool = False
    topic_key: str
    customer_id: str
    compliance_sensitive: bool = False


class ProductArtifact(BaseModel):
    """Reales, inspizierbares Produkt aus dem Sekretionssystem."""

    artifact_id: str
    day: int
    seed_template: SeedTemplate
    title: str
    protocol: str
    customer_segment: str
    topic_key: str
    revenue_eur: float
    cogs_eur: float
    net_margin_pct: float
    quality_score: float
    from_cache: bool
    synthesized_via: str
    content_markdown: str | None = None
    content_json: dict[str, Any] | None = None
    causal_gene_ids: list[str] = Field(default_factory=list)


class OperonSpec(BaseModel):
    """Ein ausführbares Gen-Operon auf dem Bakterienchromosom."""

    operon_id: str
    name_de: str
    category: str
    promoter_expression: str
    promoter_active: bool = False
    activation_count: int = 0
    parameters: dict[str, float] = Field(default_factory=dict)
    min_bounds: dict[str, float] = Field(default_factory=dict)
    max_bounds: dict[str, float] = Field(default_factory=dict)
    description_de: str


class MessengerRNATranscript(BaseModel):
    """Transkribierter, zeitbegrenzter Ausführungsplan aus einem Operon."""

    transcript_id: str
    operon_id: str
    created_day: int
    ttl_days: int
    remaining_ttl: int
    priority: float
    directives: dict[str, float | str | bool] = Field(default_factory=dict)
    translated_count: int = 0


class PlasmidInfo(BaseModel):
    """Metadaten & sandboxed Python-Quellcode eines Plasmids."""

    plasmid_id: str
    name_de: str
    hook_point: Literal[
        "pricing",
        "cache_and_cost",
        "security",
        "compliance",
        "acquisition",
        "routing",
    ]
    description_de: str
    price_eur: float
    daily_licensing_revenue_eur: float = 0.0
    installed: bool = False
    installed_day: int | None = None
    executions: int = 0
    estimated_daily_value_eur: float = 0.0
    source_code: str


class MutationRecord(BaseModel):
    """Protokolleintrag einer adaptiven Genom-Mutation."""

    day: int
    operon_id: str
    parameter: str
    old_value: float
    new_value: float
    fitness_before: float
    fitness_after: float
    outcome: Literal["kept", "rolled_back", "manual_lab"]
    reason_de: str


class CausalFlowEvent(BaseModel):
    """Ein Schritt in der kausalen Ursache-Wirkungs-Kette des letzten Ticks."""

    step: int
    source_id: str
    target_id: str
    flow_type: Literal["money", "atp", "mrna", "product", "defense", "signal", "harvest"]
    label_de: str
    magnitude: float
    unit: str


class LedgerSnapshot(BaseModel):
    """Doppelte Buchführung & GuV-Stand des Organismus."""

    day: int
    cash_eur: float
    phb_reserve_eur: float
    tax_escrow_eur: float
    volutin_prepaid_eur: float
    cumulative_harvested_eur: float
    daily_revenue_eur: float
    daily_cogs_eur: float
    daily_payment_fees_eur: float
    daily_fixed_infra_eur: float
    daily_marketing_eur: float
    daily_tax_accrual_eur: float
    daily_net_profit_eur: float
    cumulative_revenue_eur: float
    cumulative_costs_eur: float
    cumulative_net_profit_eur: float
    gross_margin_pct: float
    net_margin_pct: float
    runway_days: float
    atp_balance: float
    atp_generated_today: float
    atp_consumed_today: float


class BenchmarkPoint(BaseModel):
    """Vergleich zwischen Gärtner-Nutzpflanze und klassischer Ingenieurs-Maschine."""

    day: int
    gardener_profit_eur: float
    engineer_profit_eur: float
    gardener_attention_hours: float
    engineer_attention_hours: float
    gardener_profit_per_hour: float
    engineer_profit_per_hour: float
    gardener_complexity_score: float
    engineer_complexity_score: float
    gardener_active_modules: int
    engineer_incidents_total: int


class HistoryPoint(BaseModel):
    """Kompakter Zeitreihenpunkt für Verlaufs-Diagramme."""

    day: int
    mode: OrganismMode
    cash_eur: float
    phb_reserve_eur: float
    harvested_cumulative_eur: float
    daily_revenue_eur: float
    daily_costs_eur: float
    daily_net_profit_eur: float
    net_margin_pct: float
    atp_balance: float
    demand_units: int
    fulfilled_units: int
    blocked_threats: int
    cache_hit_rate: float
    active_customers: int
    fitness_score: float
    gardener_profit_eur: float
    engineer_profit_eur: float
    gardener_profit_per_hour: float
    engineer_profit_per_hour: float


class GardenerPolicyState(BaseModel):
    """Aktuelle Leitplanken und Pflege-Parameter des Gärtners."""

    target_margin: float = 0.58
    harvest_threshold_eur: float = 1400.0
    harvest_ratio: float = 0.35
    guardrail_strictness: float = 0.75
    auto_endospore_enabled: bool = True
    auto_plasmid_trade_enabled: bool = True
    fertilizer_boost_days: int = 0
    lab_mode_enabled: bool = False


class OrganismSnapshot(BaseModel):
    """Gesamtzustand des Organismus, Markts, Genoms und Benchmarks für die UI."""

    seed_template: SeedTemplate
    scale_preset: ScalePreset
    scenario_preset: ScenarioPreset
    day: int
    mode: OrganismMode
    alive: bool
    fitness_score: float
    health_score: float
    price_eur: float
    market: MarketTickState
    ledger: LedgerSnapshot
    gardener_policy: GardenerPolicyState
    benchmark_latest: BenchmarkPoint
    organelles: dict[str, OrganelleTelemetry]
    operons: list[OperonSpec]
    active_mrna: list[MessengerRNATranscript]
    plasmids: list[PlasmidInfo]
    recent_mutations: list[MutationRecord]
    recent_artifacts: list[ProductArtifact]
    causal_trace: list[CausalFlowEvent]
    history: list[HistoryPoint]
    narrative_log_de: list[str]
    spore_seed_hash: str


class ConfigureRequest(BaseModel):
    seed_template: SeedTemplate = SeedTemplate.SOLOPRENEUR if False else SeedTemplate.B2B_BRIEFING
    scale_preset: ScalePreset = ScalePreset.SOLOPRENEUR
    scenario_preset: ScenarioPreset = ScenarioPreset.REALISTIC_ECOSYSTEM
    rng_seed: int = 42
    imported_spore_seed: dict[str, Any] | None = None


class StepRequest(BaseModel):
    steps: int = Field(default=1, ge=1, le=365)


class ShockTriggerRequest(BaseModel):
    shock_type: ShockType
    duration_days: int = Field(default=10, ge=1, le=60)
    intensity: float = Field(default=0.75, ge=0.1, le=1.4)


class GardenerActionRequest(BaseModel):
    action: Literal[
        "fertilize",
        "update_policy",
        "manual_harvest",
        "force_dormancy",
        "force_germinate",
        "export_spore",
        "toggle_lab_mode",
    ]
    amount_eur: float = Field(default=0.0, ge=0.0, le=100000.0)
    target_margin: float | None = Field(default=None, ge=0.2, le=0.88)
    harvest_threshold_eur: float | None = Field(default=None, ge=20.0, le=200000.0)
    harvest_ratio: float | None = Field(default=None, ge=0.05, le=0.80)
    guardrail_strictness: float | None = Field(default=None, ge=0.1, le=1.0)
    auto_endospore_enabled: bool | None = None
    auto_plasmid_trade_enabled: bool | None = None
    lab_mode_enabled: bool | None = None


class LabMutationRequest(BaseModel):
    action: Literal[
        "update_operon_param",
        "install_plasmid",
        "remove_plasmid",
        "inject_custom_plasmid",
        "crossbreed_seed",
    ]
    operon_id: str | None = None
    parameter: str | None = None
    value: float | None = None
    plasmid_id: str | None = None
    custom_name_de: str | None = None
    custom_hook_point: Literal[
        "pricing",
        "cache_and_cost",
        "security",
        "compliance",
        "acquisition",
        "routing",
    ] = "pricing"
    custom_source_code: str | None = None
    partner_spore_seed: dict[str, Any] | None = None
