"""Simulations-Engine: koordiniert Organismus, Marktumwelt, Gärtner-Aktionen & Labor."""

from __future__ import annotations

import random
import threading
from typing import Any

from prokaryont.config import (
    ScalePreset,
    ScenarioPreset,
    SeedTemplate,
    ShockType,
    get_economics_profile,
    get_scenario_profile,
)
from prokaryont.environment.market import RealisticEconomicEnvironment
from prokaryont.models import (
    BenchmarkPoint,
    GardenerActionRequest,
    HistoryPoint,
    LabMutationRequest,
    MarketTickState,
    OrganismSnapshot,
)
from prokaryont.organism import EconomicProkaryote
from prokaryont.viability.gardener import EngineerControlBaseline


class SimulationEngine:
    """Thread-sichere Laufzeit für Simulation, API, Gärtner-Steuerung und Labor-Modus."""

    def __init__(
        self,
        seed_template: SeedTemplate = SeedTemplate.B2B_BRIEFING,
        scale_preset: ScalePreset = ScalePreset.SOLOPRENEUR,
        scenario_preset: ScenarioPreset = ScenarioPreset.REALISTIC_ECOSYSTEM,
        rng_seed: int = 42,
        imported_spore_seed: dict[str, Any] | None = None,
    ) -> None:
        self._lock = threading.RLock()
        self.configure(
            seed_template=seed_template,
            scale_preset=scale_preset,
            scenario_preset=scenario_preset,
            rng_seed=rng_seed,
            imported_spore_seed=imported_spore_seed,
        )

    def configure(
        self,
        seed_template: SeedTemplate,
        scale_preset: ScalePreset,
        scenario_preset: ScenarioPreset,
        rng_seed: int = 42,
        imported_spore_seed: dict[str, Any] | None = None,
    ) -> OrganismSnapshot:
        with self._lock:
            self.seed_template = seed_template
            self.scale_preset = scale_preset
            self.scenario_preset = scenario_preset
            self.rng_seed = rng_seed
            self.rng = random.Random(rng_seed)

            self.economics = get_economics_profile(scale_preset, seed_template)
            self.scenario = get_scenario_profile(scenario_preset)
            self.market_env = RealisticEconomicEnvironment(
                economics=self.economics,
                scenario=self.scenario,
                rng=random.Random(rng_seed + 101),
            )
            self.organism = EconomicProkaryote(
                profile=self.economics,
                rng=self.rng,
                imported_spore_seed=imported_spore_seed,
            )
            self.engineer = EngineerControlBaseline(profile=self.economics)
            self.history: list[HistoryPoint] = []
            self.last_market: MarketTickState = MarketTickState(
                day=0,
                season_factor=1.0,
                macro_demand_index=self.scenario.demand_multiplier,
                competitor_pressure=self.scenario.competitor_pressure_base,
                market_reference_price_eur=self.economics.base_price_eur,
                compute_cost_multiplier=self.scenario.compute_inflation_base,
                cyber_threat_level=self.scenario.cyber_threat_base,
                fraud_share=0.03,
                audit_active=False,
                audit_severity=0.0,
                active_shocks=[],
                headline_de="Saatgut eingepflanzt — bereit zum Start",
            )
            self.latest_benchmark: BenchmarkPoint = BenchmarkPoint(
                day=0,
                gardener_profit_eur=0.0,
                engineer_profit_eur=0.0,
                gardener_attention_hours=self.organism.gardener.attention_hours_cumulative,
                engineer_attention_hours=self.engineer.attention_hours_cumulative,
                gardener_profit_per_hour=0.0,
                engineer_profit_per_hour=0.0,
                gardener_complexity_score=87.5,
                engineer_complexity_score=24.0,
                gardener_active_modules=53,
                engineer_incidents_total=0,
            )
            # Initial-Ledger-Snapshot für Tag 0 erzeugen
            self.organism.ledger.record_day(
                day=0,
                revenue_eur=0.0,
                cogs_eur=0.0,
                payment_fees_eur=0.0,
                fixed_infra_eur=0.0,
                marketing_eur=0.0,
                plasmid_spend_eur=0.0,
                penalties_eur=0.0,
                phb_reserve=self.organism.inclusion_bodies.phb,
                volutin_pool=self.organism.inclusion_bodies.volutin,
                atp_balance=self.organism.atp_synthase.atp_balance,
                atp_generated_today=0.0,
                atp_consumed_today=0.0,
            )
            return self.get_snapshot()

    def step(self, steps: int = 1) -> OrganismSnapshot:
        with self._lock:
            for _ in range(steps):
                if not self.organism.alive:
                    break
                next_day = self.organism.day + 1
                market = self.market_env.step_market(next_day)
                self.last_market = market
                signals = self.organism.prepare_market_signals(market)
                requests = self.market_env.generate_requests(
                    market=market,
                    organism_price_eur=signals["price_eur"],
                    elasticity_mult=signals["elasticity_mult"],
                    organic_thylakoid_mult=signals["organic_thylakoid_mult"],
                    flagellum_reach_mult=signals["flagellum_reach_mult"],
                    fimbriae_lead_mult=signals["fimbriae_lead_mult"],
                    lifecycle_mult=signals["lifecycle_mult"],
                    plasmid_demand_bonus=signals["plasmid_demand_bonus"],
                    buoyancy=signals["buoyancy"],
                    dormant=self.organism.endospores.is_dormant,
                )
                ledger = self.organism.process_day(
                    market=market,
                    requests=requests,
                    signals=signals,
                )
                bench = self.engineer.step_with_gardener(
                    market=market,
                    base_demand_units=self.economics.base_daily_demand,
                    gardener_profit_eur=ledger.cumulative_net_profit_eur,
                    gardener_attention_hours=self.organism.gardener.attention_hours_cumulative,
                    active_organelles_count=53,
                )
                self.latest_benchmark = bench
                self.history.append(
                    HistoryPoint(
                        day=next_day,
                        mode=self.organism.mode,
                        cash_eur=ledger.cash_eur,
                        phb_reserve_eur=ledger.phb_reserve_eur,
                        harvested_cumulative_eur=ledger.cumulative_harvested_eur,
                        daily_revenue_eur=ledger.daily_revenue_eur,
                        daily_costs_eur=round(
                            ledger.daily_cogs_eur
                            + ledger.daily_payment_fees_eur
                            + ledger.daily_fixed_infra_eur
                            + ledger.daily_marketing_eur
                            + ledger.daily_tax_accrual_eur,
                            2,
                        ),
                        daily_net_profit_eur=ledger.daily_net_profit_eur,
                        net_margin_pct=ledger.net_margin_pct,
                        atp_balance=ledger.atp_balance,
                        demand_units=self.organism.last_demand_count,
                        fulfilled_units=self.organism.last_fulfilled_count,
                        blocked_threats=self.organism.last_blocked_count,
                        cache_hit_rate=self.organism.inclusion_bodies.glycogen.hit_rate,
                        active_customers=self.organism.lifecycle.active_customers,
                        fitness_score=self.organism.fitness_score,
                        gardener_profit_eur=bench.gardener_profit_eur,
                        engineer_profit_eur=bench.engineer_profit_eur,
                        gardener_profit_per_hour=bench.gardener_profit_per_hour,
                        engineer_profit_per_hour=bench.engineer_profit_per_hour,
                    )
                )
            return self.get_snapshot()

    def trigger_shock(
        self, shock_type: ShockType, duration_days: int = 10, intensity: float = 0.75
    ) -> OrganismSnapshot:
        with self._lock:
            target_day = self.organism.day + 1
            ev = self.market_env.trigger_manual_shock(
                day=target_day,
                shock_type=shock_type,
                duration_days=duration_days,
                intensity=intensity,
            )
            self.last_market.active_shocks = list(self.market_env.active_shocks)
            self.last_market.headline_de = f"Schock aktiviert: {ev.label_de}"
            self.organism.narrative_log.append(
                f"Tag {self.organism.day}: Externer Schock ausgelöst — {ev.label_de} ({duration_days} Tage)."
            )
            return self.get_snapshot()

    def apply_gardener_action(
        self, req: GardenerActionRequest
    ) -> tuple[OrganismSnapshot, dict[str, Any] | None]:
        with self._lock:
            exported_seed: dict[str, Any] | None = None
            policy = self.organism.gardener.policy
            if req.action == "fertilize":
                amt = req.amount_eur if req.amount_eur > 0 else round(self.economics.seed_capital_eur * 0.15, 2)
                self.organism.ledger.inject_fertilizer(amt)
                self.organism.gardener.fertilized_total_eur = round(
                    self.organism.gardener.fertilized_total_eur + amt, 2
                )
                policy.fertilizer_boost_days = 7
                self.organism.gardener.record_gardener_action(0.15)
                self.organism.narrative_log.append(
                    f"Tag {self.organism.day}: Gärtner düngt mit {amt:.2f} € (7 Tage Wachstums-Boost)."
                )
            elif req.action == "update_policy":
                if req.target_margin is not None:
                    policy.target_margin = req.target_margin
                if req.harvest_threshold_eur is not None:
                    policy.harvest_threshold_eur = req.harvest_threshold_eur
                    self.organism.inclusion_bodies.phb.target_buffer_eur = req.harvest_threshold_eur
                if req.harvest_ratio is not None:
                    policy.harvest_ratio = req.harvest_ratio
                if req.guardrail_strictness is not None:
                    policy.guardrail_strictness = req.guardrail_strictness
                if req.auto_endospore_enabled is not None:
                    policy.auto_endospore_enabled = req.auto_endospore_enabled
                if req.auto_plasmid_trade_enabled is not None:
                    policy.auto_plasmid_trade_enabled = req.auto_plasmid_trade_enabled
                self.organism.gardener.record_gardener_action(0.10)
            elif req.action == "manual_harvest":
                amt = (
                    req.amount_eur
                    if req.amount_eur > 0
                    else round(self.organism.inclusion_bodies.phb.balance_eur * 0.30, 2)
                )
                harvested = self.organism.cytoskeleton.ftsz.force_manual_harvest(
                    day=self.organism.day,
                    phb_balance_eur=self.organism.inclusion_bodies.phb.balance_eur,
                    amount_eur=amt,
                )
                if harvested > 0:
                    self.organism.inclusion_bodies.phb.withdraw(harvested)
                    self.organism.ledger.register_harvest(harvested)
                    self.organism.narrative_log.append(
                        f"Tag {self.organism.day}: Gärtner erntet {harvested:.2f} € über FtsZ-Ring."
                    )
                self.organism.gardener.record_gardener_action(0.10)
            elif req.action == "force_dormancy":
                self.organism.enter_endospore("Manueller Gärtner-Winterschlaf")
                self.organism.gardener.record_gardener_action(0.10)
            elif req.action == "force_germinate":
                self.organism.endospores.germinate()
                self.organism.mode = "active"
                self.organism.narrative_log.append(
                    f"Tag {self.organism.day}: Gärtner weckt Endospore zur Keimung."
                )
                self.organism.gardener.record_gardener_action(0.10)
            elif req.action == "export_spore":
                exported_seed = self.organism.export_spore_seed()
                self.organism.gardener.record_gardener_action(0.05)
            elif req.action == "toggle_lab_mode":
                policy.lab_mode_enabled = (
                    req.lab_mode_enabled
                    if req.lab_mode_enabled is not None
                    else not policy.lab_mode_enabled
                )

            # Aktuellen Ledger-Snapshot synchronisieren
            if self.organism.ledger.last_snapshot is not None:
                self.organism.ledger.last_snapshot.cash_eur = self.organism.ledger.cash_eur
                self.organism.ledger.last_snapshot.phb_reserve_eur = (
                    self.organism.inclusion_bodies.phb.balance_eur
                )
                self.organism.ledger.last_snapshot.cumulative_harvested_eur = (
                    self.organism.ledger.cumulative_harvested_eur
                )
            return self.get_snapshot(), exported_seed

    def apply_lab_mutation(self, req: LabMutationRequest) -> OrganismSnapshot:
        with self._lock:
            if not self.organism.gardener.policy.lab_mode_enabled:
                raise PermissionError(
                    "Labor-Modus ist deaktiviert. Im Gärtner-Modus sind direkte Gen-Eingriffe gesperrt."
                )

            if req.action == "update_operon_param":
                if not req.operon_id or not req.parameter or req.value is None:
                    raise ValueError("operon_id, parameter und value erforderlich.")
                op = self.organism.chromosome.operons.get(req.operon_id)
                if op is None or req.parameter not in op.parameters:
                    raise ValueError("Unbekanntes Operon oder Parameter.")
                old_val = op.parameters[req.parameter]
                new_val = self.organism.nucleoid.enforce_bounds(
                    op,
                    req.parameter,
                    req.value,
                    self.organism.gardener.policy.guardrail_strictness,
                )
                self.organism.nucleoid.save_snapshot(self.organism.chromosome.operons)
                op.parameters[req.parameter] = new_val
                self.organism.chromosome.genome_version += 1
                self.organism.mutation_engine.record_manual_lab_mutation(
                    day=self.organism.day,
                    operon_id=req.operon_id,
                    parameter=req.parameter,
                    old_value=old_val,
                    new_value=new_val,
                    fitness=self.organism.fitness_score,
                    reason_de="Manuelle Labor-Anpassung durch Gärtner im Labor-Tab.",
                )
            elif req.action == "install_plasmid":
                if not req.plasmid_id:
                    raise ValueError("plasmid_id erforderlich.")
                cp = self.organism.plasmid_registry.install(req.plasmid_id, day=self.organism.day)
                if cp is None:
                    raise ValueError("Unbekanntes Plasmid.")
            elif req.action == "remove_plasmid":
                if not req.plasmid_id:
                    raise ValueError("plasmid_id erforderlich.")
                self.organism.plasmid_registry.remove(req.plasmid_id)
            elif req.action == "inject_custom_plasmid":
                if not req.custom_source_code:
                    raise ValueError("custom_source_code erforderlich.")
                self.organism.inject_custom_plasmid(
                    name_de=req.custom_name_de or "Labor-Custom-Plasmid",
                    hook_point=req.custom_hook_point,
                    source_code=req.custom_source_code,
                )
            elif req.action == "crossbreed_seed":
                if not req.partner_spore_seed:
                    raise ValueError("partner_spore_seed erforderlich.")
                self.organism.import_spore_seed(req.partner_spore_seed, crossbreed=True)
                self.organism.narrative_log.append(
                    f"Tag {self.organism.day}: Labor-Kreuzung zweier Saatgut-Genome durchgeführt."
                )

            self.organism.gardener.record_gardener_action(0.45)
            return self.get_snapshot()

    def get_snapshot(self) -> OrganismSnapshot:
        with self._lock:
            ledger = self.organism.ledger.last_snapshot
            assert ledger is not None
            return OrganismSnapshot(
                seed_template=self.seed_template,
                scale_preset=self.scale_preset,
                scenario_preset=self.scenario_preset,
                day=self.organism.day,
                mode=self.organism.mode,
                alive=self.organism.alive,
                fitness_score=self.organism.fitness_score,
                health_score=self.organism.health_score,
                price_eur=self.organism.pricing_engine.current_price_eur,
                market=self.last_market,
                ledger=ledger,
                gardener_policy=self.organism.gardener.policy,
                benchmark_latest=self.latest_benchmark,
                organelles=self.organism.collect_organelle_telemetry(),
                operons=list(self.organism.chromosome.operons.values()),
                active_mrna=list(self.organism.mrna.pool),
                plasmids=[cp.info for cp in self.organism.plasmid_registry.plasmids.values()],
                recent_mutations=list(self.organism.mutation_engine.records[-20:])[::-1],
                recent_artifacts=self.organism.secretion.get_recent(),
                causal_trace=list(self.organism.last_causal_trace),
                history=list(self.history[-220:]),
                narrative_log_de=list(self.organism.narrative_log)[::-1],
                spore_seed_hash=self.organism.endospores.coat.latest_hash,
            )
