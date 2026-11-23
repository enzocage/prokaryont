export type SeedTemplate = 'b2b_briefing' | 'micro_api';
export type ScalePreset = 'nano' | 'solopreneur' | 'growth';
export type ScenarioPreset =
  | 'realistic_ecosystem'
  | 'growth_market'
  | 'price_war_gauntlet'
  | 'drought_survival'
  | 'cyber_and_audit_storm';

export type ShockType =
  | 'demand_boom'
  | 'price_war'
  | 'compute_shock'
  | 'cyber_storm'
  | 'compliance_audit'
  | 'recession_drought';

export type OrganismMode =
  | 'active'
  | 'conserving'
  | 'sporulating'
  | 'dormant_endospore'
  | 'germinating';

export interface StructureRegistryEntry {
  id: string;
  german_name: string;
  english_name: string;
  system_id: string;
  system_name_de: string;
  category: 'prokaryote' | 'viability';
  status: 'active' | 'submodule' | 'merged' | 'excluded';
  merged_into?: string | null;
  bio_function_de: string;
  economic_analogy_de: string;
  rationale_de: string;
  code_symbol: string;
  upstream_ids: string[];
  downstream_ids: string[];
  svg_anchor: string;
}

export interface RegistryResponse {
  summary: Record<string, number>;
  systems: Record<string, string>;
  structures: StructureRegistryEntry[];
}

export interface OrganelleTelemetry {
  id: string;
  name_de: string;
  system_id: string;
  health: number;
  activity: number;
  load: number;
  efficiency: number;
  state_label_de: string;
  metrics: Record<string, number | string | boolean>;
}

export interface ShockEvent {
  shock_type: ShockType;
  label_de: string;
  start_day: number;
  end_day: number;
  intensity: number;
  source: string;
}

export interface MarketTickState {
  day: number;
  season_factor: number;
  macro_demand_index: number;
  competitor_pressure: number;
  market_reference_price_eur: number;
  compute_cost_multiplier: number;
  cyber_threat_level: number;
  fraud_share: number;
  audit_active: boolean;
  audit_severity: number;
  active_shocks: ShockEvent[];
  headline_de: string;
}

export interface ProductArtifact {
  artifact_id: string;
  day: number;
  seed_template: SeedTemplate;
  title: string;
  protocol: string;
  customer_segment: string;
  topic_key: string;
  revenue_eur: number;
  cogs_eur: number;
  net_margin_pct: number;
  quality_score: number;
  from_cache: boolean;
  synthesized_via: string;
  content_markdown?: string | null;
  content_json?: Record<string, unknown> | null;
  causal_gene_ids: string[];
}

export interface OperonSpec {
  operon_id: string;
  name_de: string;
  category: string;
  promoter_expression: string;
  promoter_active: boolean;
  activation_count: number;
  parameters: Record<string, number>;
  min_bounds: Record<string, number>;
  max_bounds: Record<string, number>;
  description_de: string;
}

export interface MessengerRNATranscript {
  transcript_id: string;
  operon_id: string;
  created_day: number;
  ttl_days: number;
  remaining_ttl: number;
  priority: number;
  directives: Record<string, number | string | boolean>;
  translated_count: number;
}

export interface PlasmidInfo {
  plasmid_id: string;
  name_de: string;
  hook_point: string;
  description_de: string;
  price_eur: number;
  daily_licensing_revenue_eur: number;
  installed: boolean;
  installed_day?: number | null;
  executions: number;
  estimated_daily_value_eur: number;
  source_code: string;
}

export interface MutationRecord {
  day: number;
  operon_id: string;
  parameter: string;
  old_value: number;
  new_value: number;
  fitness_before: number;
  fitness_after: number;
  outcome: 'kept' | 'rolled_back' | 'manual_lab';
  reason_de: string;
}

export interface CausalFlowEvent {
  step: number;
  source_id: string;
  target_id: string;
  flow_type: 'money' | 'atp' | 'mrna' | 'product' | 'defense' | 'signal' | 'harvest';
  label_de: string;
  magnitude: number;
  unit: string;
}

export interface LedgerSnapshot {
  day: number;
  cash_eur: number;
  phb_reserve_eur: number;
  tax_escrow_eur: number;
  volutin_prepaid_eur: number;
  cumulative_harvested_eur: number;
  daily_revenue_eur: number;
  daily_cogs_eur: number;
  daily_payment_fees_eur: number;
  daily_fixed_infra_eur: number;
  daily_marketing_eur: number;
  daily_tax_accrual_eur: number;
  daily_net_profit_eur: number;
  cumulative_revenue_eur: number;
  cumulative_costs_eur: number;
  cumulative_net_profit_eur: number;
  gross_margin_pct: number;
  net_margin_pct: number;
  runway_days: number;
  atp_balance: number;
  atp_generated_today: number;
  atp_consumed_today: number;
}

export interface BenchmarkPoint {
  day: number;
  gardener_profit_eur: number;
  engineer_profit_eur: number;
  gardener_attention_hours: number;
  engineer_attention_hours: number;
  gardener_profit_per_hour: number;
  engineer_profit_per_hour: number;
  gardener_complexity_score: number;
  engineer_complexity_score: number;
  gardener_active_modules: number;
  engineer_incidents_total: number;
}

export interface HistoryPoint {
  day: number;
  mode: OrganismMode;
  cash_eur: number;
  phb_reserve_eur: number;
  harvested_cumulative_eur: number;
  daily_revenue_eur: number;
  daily_costs_eur: number;
  daily_net_profit_eur: number;
  net_margin_pct: number;
  atp_balance: number;
  demand_units: number;
  fulfilled_units: number;
  blocked_threats: number;
  cache_hit_rate: number;
  active_customers: number;
  fitness_score: number;
  gardener_profit_eur: number;
  engineer_profit_eur: number;
  gardener_profit_per_hour: number;
  engineer_profit_per_hour: number;
}

export interface GardenerPolicyState {
  target_margin: number;
  harvest_threshold_eur: number;
  harvest_ratio: number;
  guardrail_strictness: number;
  auto_endospore_enabled: boolean;
  auto_plasmid_trade_enabled: boolean;
  fertilizer_boost_days: number;
  lab_mode_enabled: boolean;
}

export interface OrganismSnapshot {
  seed_template: SeedTemplate;
  scale_preset: ScalePreset;
  scenario_preset: ScenarioPreset;
  day: number;
  mode: OrganismMode;
  alive: boolean;
  fitness_score: number;
  health_score: number;
  price_eur: number;
  market: MarketTickState;
  ledger: LedgerSnapshot;
  gardener_policy: GardenerPolicyState;
  benchmark_latest: BenchmarkPoint;
  organelles: Record<string, OrganelleTelemetry>;
  operons: OperonSpec[];
  active_mrna: MessengerRNATranscript[];
  plasmids: PlasmidInfo[];
  recent_mutations: MutationRecord[];
  recent_artifacts: ProductArtifact[];
  causal_trace: CausalFlowEvent[];
  history: HistoryPoint[];
  narrative_log_de: string[];
  spore_seed_hash: string;
}

export interface ConfigOptionsResponse {
  seeds: { id: SeedTemplate; name_de: string; short_de: string; description_de: string }[];
  scales: { id: ScalePreset; seed_capital_eur: number; label_de: string }[];
  scenarios: { id: ScenarioPreset; name_de: string; description_de: string }[];
  shocks: { id: ShockType; label_de: string; default_days: number }[];
}
