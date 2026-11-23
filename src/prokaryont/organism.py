"""Zentraler Wirtschaftlicher Prokaryont (EconomicProkaryote): kausaler Organismus-Zyklus."""

from __future__ import annotations

import random
from collections import deque
from typing import Any

from prokaryont.adapters.llm import LLMAdapter, create_default_llm_adapter
from prokaryont.adapters.payment import PaymentAdapter, create_default_payment_adapter
from prokaryont.config import ScaleEconomicsProfile, ScalePreset, SeedTemplate
from prokaryont.genetics.chromosome import (
    BacterialChromosome,
    MutationEngine,
    Nucleoid,
)
from prokaryont.genetics.expression import MessengerRNA, Ribosome70S
from prokaryont.genetics.plasmids import (
    PlasmidMarketplace,
    PlasmidRegistry,
    PlasmidSecurityError,
)
from prokaryont.models import (
    CausalFlowEvent,
    CustomerRequest,
    LedgerSnapshot,
    MarketTickState,
    OrganelleTelemetry,
    OrganismMode,
)
from prokaryont.organelles.cytoskeleton import Cytoplasm, Cytoskeleton
from prokaryont.organelles.dormancy import EndosporeSystem
from prokaryont.organelles.envelope import (
    CellWall,
    Glycocalyx,
    OuterMembrane,
    Periplasm,
    PlasmaMembrane,
    PorinChannel,
    SLayer,
)
from prokaryont.organelles.metabolism import (
    ATPSynthase,
    Carboxysomes,
    ElectronTransportChain,
    Encapsulins,
    GasVesicles,
    Magnetosomes,
    Metabolosomes,
    MicrocompartmentFramework,
    Thylakoids,
)
from prokaryont.organelles.motility import Fimbriae, FlagellumSystem, Pili, SexPili
from prokaryont.organelles.secretion import SecretionSystem
from prokaryont.organelles.storage import InclusionBodies
from prokaryont.viability.economics import (
    DoubleEntryLedger,
    PricingEngine,
    RunwayCircuitBreaker,
)
from prokaryont.viability.gardener import GardenerInterface
from prokaryont.viability.quality_compliance import (
    ComplianceGuard,
    CustomerLifecycleManager,
    QualityGate,
)


class EconomicProkaryote:
    """Selbstregulierender agentischer Wirtschaftsorganismus nach Prokaryonten-Vorbild."""

    def __init__(
        self,
        profile: ScaleEconomicsProfile,
        rng: random.Random,
        llm_adapter: LLMAdapter | None = None,
        payment_adapter: PaymentAdapter | None = None,
        imported_spore_seed: dict[str, Any] | None = None,
    ) -> None:
        self.profile = profile
        self.rng = rng
        self.day: int = 0
        self.alive: bool = True
        self.mode: OrganismMode = "active"
        self.scale_factor: float = (
            0.28
            if profile.scale == ScalePreset.NANO
            else (1.0 if profile.scale == ScalePreset.SOLOPRENEUR else 4.2)
        )

        # 1. Genetisches System & Expression
        self.nucleoid = Nucleoid()
        self.chromosome = BacterialChromosome()
        self.plasmid_registry = PlasmidRegistry(scale_factor=self.scale_factor)
        self.plasmid_marketplace = PlasmidMarketplace(scale_factor=self.scale_factor)
        self.mrna = MessengerRNA()
        self.ribosome_70s = Ribosome70S(llm_adapter=llm_adapter or create_default_llm_adapter())
        self.mutation_engine = MutationEngine(rng=rng)

        # 2. Zellhülle & Bindung
        self.s_layer = SLayer()
        self.outer_membrane = OuterMembrane()
        self.porins = PorinChannel()
        self.periplasm = Periplasm()
        self.cell_wall = CellWall()
        self.plasma_membrane = PlasmaMembrane(
            payment_adapter=payment_adapter or create_default_payment_adapter()
        )
        self.glycocalyx = Glycocalyx()

        # 3. Cytoplasma & Zytoskelett
        self.cytoplasm = Cytoplasm()
        self.cytoskeleton = Cytoskeleton()

        # 4. Motilität & Konjugation
        self.flagellum = FlagellumSystem()
        self.fimbriae = Fimbriae()
        self.pili = Pili()
        self.sex_pili = SexPili(marketplace=self.plasmid_marketplace)

        # 5. Stoffwechsel & Mikrokompartimente
        self.etc = ElectronTransportChain()
        self.atp_synthase = ATPSynthase(atp_balance=round(35.0 * max(0.6, self.scale_factor**0.4), 1))
        self.thylakoids = Thylakoids()
        self.microcompartments = MicrocompartmentFramework()
        self.carboxysomes = Carboxysomes()
        self.metabolosomes = Metabolosomes()
        self.encapsulins = Encapsulins()
        self.magnetosomes = Magnetosomes()
        self.gas_vesicles = GasVesicles()

        # 6. Einschlusskörperchen & Speicher
        self.inclusion_bodies = InclusionBodies(
            target_phb_eur=profile.harvest_threshold_eur,
            volutin_cap_eur=round(profile.seed_capital_eur * 0.25, 2),
        )
        # Startkapital sauber auf Arbeitskasse (65 %), PHB (30 %) & Volutin (5 %) verteilen
        self.inclusion_bodies.phb.balance_eur = round(profile.seed_capital_eur * 0.30, 2)
        self.inclusion_bodies.volutin.prepaid_eur = round(profile.seed_capital_eur * 0.05, 2)

        # 7. Endospore & Sekretion
        self.endospores = EndosporeSystem()
        self.secretion = SecretionSystem()

        # 8. Ökonomische Viability-Module
        self.pricing_engine = PricingEngine(
            current_price_eur=profile.base_price_eur,
            min_price_eur=profile.min_price_eur,
            max_price_eur=profile.max_price_eur,
            base_price_eur=profile.base_price_eur,
            price_elasticity=profile.price_elasticity,
        )
        self.ledger = DoubleEntryLedger(profile=profile)
        self.quality_gate = QualityGate()
        self.compliance_guard = ComplianceGuard()
        self.lifecycle = CustomerLifecycleManager(
            active_customers=14 if profile.scale == ScalePreset.NANO else (28 if profile.scale == ScalePreset.SOLOPRENEUR else 65)
        )
        self.runway_breaker = RunwayCircuitBreaker()
        self.gardener = GardenerInterface(harvest_threshold_eur=profile.harvest_threshold_eur)

        self.fitness_score: float = 0.64
        self.health_score: float = 0.96
        self.last_causal_trace: list[CausalFlowEvent] = []
        self.narrative_log: deque[str] = deque(maxlen=28)
        self.last_demand_count: int = 0
        self.last_fulfilled_count: int = 0
        self.last_blocked_count: int = 0
        self.last_plasmid_effects: dict[str, float] = {}

        if imported_spore_seed:
            self.import_spore_seed(imported_spore_seed)
        else:
            # Initialer Saatgut-Hash über Sporenmantel
            self.endospores.coat.seal_seed(
                {
                    "seed_template": profile.seed.value,
                    "genes": self.chromosome.export_genes(),
                    "plasmid_ids": [],
                }
            )
        self.narrative_log.append(
            f"Tag 0: Saatgut '{profile.label_de}' ins Gewächshaus gepflanzt "
            f"(Startkapital {profile.seed_capital_eur:.0f} €)."
        )

    def _compute_fitness(self, ledger: LedgerSnapshot) -> float:
        margin_norm = max(0.0, min(1.0, ledger.net_margin_pct / 70.0))
        runway_norm = max(0.0, min(1.0, ledger.runway_days / 90.0))
        quality_norm = self.quality_gate.avg_quality
        retention_norm = self.lifecycle.retention_rate
        profit_pos = 1.0 if ledger.daily_net_profit_eur > 0 else 0.35
        return round(
            margin_norm * 0.36
            + runway_norm * 0.22
            + quality_norm * 0.18
            + retention_norm * 0.14
            + profit_pos * 0.10,
            4,
        )

    def prepare_market_signals(
        self, market: MarketTickState
    ) -> dict[str, float]:
        """Sensorik, Transkription, Pricing & Navigation vor der Order-Generierung."""
        self.day = market.day
        self.cytoplasm.cytosol.reset_tick()
        self.atp_synthase.reset_daily_counters()
        self.inclusion_bodies.glycogen.reset_daily()
        self.inclusion_bodies.volutin.reset_daily()
        self.metabolosomes.reset_daily()
        self.encapsulins.reset_daily()
        self.quality_gate.reset_daily()
        self.secretion.begin_tick()

        # 1. Endospore-Wachzustand prüfen (Exosporium-Keimung)
        germination_trigger = self.chromosome.get_param(
            "OP_CRISIS_SPORULATION", "germination_demand_trigger", 0.62
        )
        drought_active = any(s.shock_type.value == "recession_drought" for s in market.active_shocks)
        if self.endospores.is_dormant:
            self.endospores.total_dormant_days += 1
            should_germinate = self.endospores.exosporium.sense_germination(
                demand_ratio=market.macro_demand_index,
                germination_trigger=germination_trigger,
                drought_active=drought_active,
            )
            if should_germinate:
                self.endospores.germinate()
                self.mode = "germinating"
                self.narrative_log.append(
                    f"Tag {market.day}: Exosporium erkennt Markterholung — Endospore keimt wieder auf!"
                )
            else:
                self.mode = "dormant_endospore"

        # 2. Magnetosomen & Gasvesikel orientieren am Trend
        ema_demand, _ = self.magnetosomes.sense(
            market.macro_demand_index, market.competitor_pressure
        )
        self.cytoplasm.cytosol.publish("ema_demand", ema_demand)

        # 3. Aktive Code-Plasmide in der AST-Sandbox ausführen
        p_ctx = {
            "demand_ratio": market.macro_demand_index,
            "capsule_strength": self.glycocalyx.capsule.strength,
            "competitor_pressure": market.competitor_pressure,
            "threat_level": market.cyber_threat_level,
            "audit_active": market.audit_active,
            "compute_mult": market.compute_cost_multiplier,
            "satisfaction": self.lifecycle.satisfaction,
            "repeat_share": self.lifecycle.retention_rate * 0.45,
        }
        plasmid_effects, per_plasmid = self.plasmid_registry.execute_installed(p_ctx)
        self.last_plasmid_effects = plasmid_effects

        # 4. Chromosom-Promotoren auswerten & mRNA transkribieren -> 70S-Translation
        last_snap = self.ledger.last_snapshot
        last_margin = (last_snap.net_margin_pct / 100.0) if last_snap else 0.55
        promoter_ctx: dict[str, float | bool] = {
            "margin": last_margin,
            "target_margin": self.gardener.policy.target_margin,
            "threat_level": market.cyber_threat_level,
            "fraud_share": market.fraud_share,
            "runway_days": self.runway_breaker.runway_days,
            "phb_reserve": self.inclusion_bodies.phb.balance_eur,
            "harvest_threshold": self.gardener.policy.harvest_threshold_eur,
            "audit_active": market.audit_active,
            "guardrail_strictness": self.gardener.policy.guardrail_strictness,
            "demand_ratio": market.macro_demand_index,
            "compute_multiplier": market.compute_cost_multiplier,
            "competitor_pressure": market.competitor_pressure,
            "dormant": self.endospores.is_dormant,
        }
        active_operons = self.chromosome.evaluate_promoters(promoter_ctx)
        self.mrna.transcribe(market.day, active_operons, per_plasmid)
        directives = self.ribosome_70s.translate_directives(self.mrna)
        self.cytoplasm.cytosol.publish("directives_count", len(directives))

        if self.endospores.is_dormant:
            return {
                "price_eur": self.pricing_engine.current_price_eur,
                "elasticity_mult": 0.0,
                "organic_thylakoid_mult": 0.0,
                "flagellum_reach_mult": 0.0,
                "fimbriae_lead_mult": 0.0,
                "lifecycle_mult": 1.0,
                "plasmid_demand_bonus": 0.0,
                "buoyancy": self.gas_vesicles.buoyancy,
                "marketing_eur": 0.0,
                "marketing_atp": 0.0,
            }

        # 5. Gasvesikel & Pricing-Engine
        buoyancy = self.gas_vesicles.adjust_buoyancy(
            competitor_pressure=market.competitor_pressure,
            capsule_strength=self.glycocalyx.capsule.strength,
            premium_bias=float(directives.get("premium_bias", 0.25)),
        )
        est_cogs = (
            self.profile.raw_compute_cost_per_unit_eur
            * market.compute_cost_multiplier
            * (1.0 - self.inclusion_bodies.glycogen.hit_rate * 0.55)
        )
        price = self.pricing_engine.compute_price(
            unit_cogs_est_eur=est_cogs,
            target_margin=self.gardener.policy.target_margin,
            operon_markup=float(directives.get("target_markup", 1.04)),
            capsule_premium=self.glycocalyx.capsule.price_premium_multiplier(),
            gas_buoyancy=buoyancy,
            competitor_pressure=market.competitor_pressure,
            plasmid_price_mult=plasmid_effects.get("price_multiplier", 1.0),
            fee_rate=self.profile.payment_fee_rate,
            fee_fixed_eur=self.profile.payment_fee_fixed_eur,
        )
        elasticity_mult = self.pricing_engine.demand_elasticity_multiplier(
            market.market_reference_price_eur
        )

        # 6. Thylakoide, Flagellen & Fimbrien erzeugen Nachfrage-Multiplikatoren
        organic_mult = self.thylakoids.photosynthesize_inbound(
            day=market.day,
            capsule_strength=self.glycocalyx.capsule.strength,
            base_demand=self.profile.base_daily_demand,
            dormant=False,
        )
        mkt_share = float(directives.get("marketing_atp_share", 0.34))
        if self.runway_breaker.conserving_active:
            mkt_share *= 0.35
        fertilizer_active = self.gardener.policy.fertilizer_boost_days > 0
        if fertilizer_active:
            self.gardener.policy.fertilizer_boost_days -= 1

        preferred_channel = (
            "b2b_enterprise_direct"
            if buoyancy >= 0.65
            else ("api_verzeichnis" if self.profile.seed == SeedTemplate.MICRO_API else "nischen_research")
        )
        raw_mkt_eur, reach_mult, mkt_atp = self.flagellum.navigate(
            atp_available=self.atp_synthase.atp_balance,
            target_share=mkt_share,
            base_marketing_budget_eur=self.profile.base_marketing_budget_eur,
            preferred_channel=preferred_channel,
            competitor_pressure=market.competitor_pressure,
            fertilizer_active=fertilizer_active,
        )
        approved_mkt_eur = self.cell_wall.peptidoglycan.verify_crosslinks(
            guardrail_strictness=self.gardener.policy.guardrail_strictness,
            available_cash=self.ledger.cash_eur,
            planned_spend=raw_mkt_eur,
        )
        self.atp_synthase.consume(mkt_atp)

        fimbriae_mult = self.fimbriae.capture(
            intensity=float(directives.get("fimbriae_hook_intensity", 0.62)),
            organic_bonus=plasmid_effects.get("organic_demand_bonus", 0.0),
            base_demand=self.profile.base_daily_demand,
        )
        self.inclusion_bodies.sulfur.replenish(
            leads_captured=self.fimbriae.leads_captured_today, dormant=False
        )
        pili_boost = self.pili.engage(
            focus=float(directives.get("pili_retention_focus", 0.68)),
            active_customers=self.lifecycle.active_customers,
        )
        lifecycle_mult = round(
            min(1.65, 0.88 + self.lifecycle.active_customers / 120.0 + pili_boost * 0.5),
            4,
        )

        return {
            "price_eur": price,
            "elasticity_mult": elasticity_mult,
            "organic_thylakoid_mult": organic_mult,
            "flagellum_reach_mult": reach_mult,
            "fimbriae_lead_mult": fimbriae_mult,
            "lifecycle_mult": lifecycle_mult,
            "plasmid_demand_bonus": plasmid_effects.get("organic_demand_bonus", 0.0),
            "buoyancy": buoyancy,
            "marketing_eur": approved_mkt_eur,
            "marketing_atp": mkt_atp,
        }

    def process_day(
        self,
        market: MarketTickState,
        requests: list[CustomerRequest],
        signals: dict[str, float],
    ) -> LedgerSnapshot:
        """Verarbeitet den vollständigen kausalen Tageszyklus von Hülle über Stoffwechsel bis Ernte."""
        self.gardener.record_passive_observation_tick(dormant=self.endospores.is_dormant)

        if self.endospores.is_dormant:
            # Minimal-Burn durch Sporen-Kortex + Exosporium-Sensor
            dehydrated_infra = self.endospores.cortex.dehydrated_daily_burn(
                self.profile.fixed_infra_per_day_eur
            )
            self.last_demand_count = 0
            self.last_fulfilled_count = 0
            self.last_blocked_count = 0
            snap = self.ledger.record_day(
                day=market.day,
                revenue_eur=0.0,
                cogs_eur=0.0,
                payment_fees_eur=0.0,
                fixed_infra_eur=dehydrated_infra,
                marketing_eur=0.0,
                plasmid_spend_eur=0.0,
                penalties_eur=0.0,
                phb_reserve=self.inclusion_bodies.phb,
                volutin_pool=self.inclusion_bodies.volutin,
                atp_balance=self.atp_synthase.atp_balance,
                atp_generated_today=0.0,
                atp_consumed_today=0.0,
            )
            self.lifecycle.update(0, self.quality_gate.avg_quality, self.glycocalyx.slime_layer.stickiness, 0.0, 0.0, self.pricing_engine.current_price_eur, dormant=True)
            self.fitness_score = self._compute_fitness(snap)
            self._build_dormant_trace(dehydrated_infra)
            return snap

        directives = self.ribosome_70s.active_directives
        p_fx = self.last_plasmid_effects
        self.last_demand_count = len([r for r in requests if not r.is_malicious])

        # 1. Hüllen-Verteidigung: S-Layer -> Äußere Membran/LPS -> Porine -> Periplasma -> Zellwand
        after_s_layer = self.s_layer.filter_traffic(
            requests=requests,
            strictness_override=float(directives.get("s_layer_strictness", 0.78)),
            firewall_bonus=p_fx.get("firewall_bonus", 0.0),
        )
        after_outer = self.outer_membrane.screen_requests(
            requests=after_s_layer,
            lps_threshold=float(directives.get("lps_fraud_threshold", 0.80)),
            fraud_block_bonus=p_fx.get("fraud_block_bonus", 0.0),
        )
        self.last_blocked_count = self.s_layer.blocked_today + self.outer_membrane.rejected_today

        balanced_cap = self.cytoskeleton.mreb.balance_capacity(
            queued_orders=len(after_outer),
            base_max_capacity=self.profile.max_capacity_per_day,
            atp_balance=self.atp_synthase.atp_balance,
        )
        self.cell_wall.protect_against_lysis(
            requests_count=len(after_outer),
            max_capacity=balanced_cap,
            cash_eur=self.ledger.cash_eur + self.inclusion_bodies.phb.balance_eur,
            daily_fixed_burn=self.profile.fixed_infra_per_day_eur,
        )
        after_porins = self.porins.admit(
            requests=after_outer,
            max_capacity=balanced_cap,
            atp_balance=self.atp_synthase.atp_balance,
            throttle_floor=float(directives.get("porin_throttle_floor", 0.52)),
        )
        est_unit_cost = (
            self.profile.raw_compute_cost_per_unit_eur
            * market.compute_cost_multiplier
            * 0.65
        )
        after_periplasm = self.periplasm.preprocess(
            requests=after_porins,
            estimated_unit_cogs=est_unit_cost,
            min_margin_ratio=self.gardener.policy.target_margin * 0.55,
        )

        # 2. Plasmamembran wickelt echte Zahlungen ab
        paid_orders = self.plasma_membrane.settle_orders(
            requests=after_periplasm,
            fee_rate=self.profile.payment_fee_rate,
            fee_fixed_eur=self.profile.payment_fee_fixed_eur,
        )

        # 3. Stoffwechsel & 70S-Ribosom-Produktion -> Carboxysomen -> QualityGate -> Sekretion
        active_gene_ids = [
            op.operon_id for op in self.chromosome.operons.values() if op.promoter_active
        ]
        cache_aggr = float(directives.get("cache_aggressiveness", 0.72))
        arb_ratio = float(directives.get("arbitrage_routing", 0.48))
        pii_level = float(directives.get("pii_redaction_level", 0.90))
        protocol = (
            "briefing_markdown"
            if self.profile.seed == SeedTemplate.B2B_BRIEFING
            else "rest_json_api"
        )

        total_cogs = 0.0
        qualities: list[float] = []
        fulfilled = 0

        for idx, (req, _settlement) in enumerate(paid_orders):
            cache_hit = self.inclusion_bodies.glycogen.lookup_or_store(
                topic_key=req.topic_key,
                cache_aggressiveness=cache_aggr,
                plasmid_hit_bonus=p_fx.get("cache_hit_bonus", 0.0),
                rng_roll=self.rng.random(),
            )
            sulfur_ready = self.inclusion_bodies.sulfur.consume_for_production()
            raw_unit_cost = (
                self.profile.raw_compute_cost_per_unit_eur * market.compute_cost_multiplier
            )
            hedged_cost = self.inclusion_bodies.volutin.hedge_compute(
                raw_unit_cost, market.compute_cost_multiplier
            )
            concentrated_cost = self.carboxysomes.concentrate_value(
                cache_hit=cache_hit,
                sulfur_ready=sulfur_ready,
                raw_cost_eur=hedged_cost,
            )
            arb_cost, _ = self.metabolosomes.arbitrage_and_recover(
                unit_cost_eur=concentrated_cost,
                arbitrage_ratio=arb_ratio,
                plasmid_discount=p_fx.get("arbitrage_cogs_discount", 0.0),
                dirty_input=req.complexity > 0.84,
            )
            final_unit_cost = round(arb_cost * p_fx.get("cogs_multiplier", 1.0), 4)

            self.encapsulins.sanitize_and_seal(
                sensitive=req.compliance_sensitive, pii_redaction_level=pii_level
            )

            # Vollständige LLM-/Template-Synthese für die ersten 2 Orders pro Tag (für Output-Inspektor)
            gen_full = idx < 2
            artifact, synth_cost = self.ribosome_70s.synthesize_order(
                request=req,
                seed_template=self.profile.seed,
                day=market.day,
                available_atp=max(10.0, self.atp_synthase.atp_balance),
                target_cost_eur=final_unit_cost,
                quality_boost=p_fx.get("trust_bonus", 0.0),
                from_cache=cache_hit,
                active_gene_ids=active_gene_ids,
                generate_full_payload=gen_full,
            )
            order_cogs = final_unit_cost if not gen_full else min(final_unit_cost * 1.1, synth_cost)
            q_score = artifact.quality_score if artifact else round(0.91 - req.complexity * 0.04, 3)
            q_final, order_cogs = self.quality_gate.inspect_and_ensure(
                quality_score=q_score,
                unit_cost_eur=order_cogs,
                metabolosomes=self.metabolosomes,
                arbitrage_ratio=arb_ratio,
                plasmid_discount=p_fx.get("arbitrage_cogs_discount", 0.0),
            )
            if artifact is not None:
                artifact.quality_score = q_final
                artifact.cogs_eur = round(order_cogs, 4)
            self.secretion.secrete(artifact, protocol=protocol)
            total_cogs += order_cogs
            qualities.append(q_final)
            fulfilled += 1

        self.last_fulfilled_count = fulfilled
        avg_quality = (sum(qualities) / len(qualities)) if qualities else 0.90

        # 4. Sexpili-Plasmid-Konjugation (Erwerb & Lizenzerlös)
        acquired_plasmid, plasmid_spent, plasmid_lic_rev = self.sex_pili.conjugate(
            day=market.day,
            registry=self.plasmid_registry,
            auto_trade=self.gardener.policy.auto_plasmid_trade_enabled,
            available_cash_eur=self.ledger.cash_eur,
            available_atp=self.atp_synthase.atp_balance,
            market_threat=market.cyber_threat_level,
            audit_active=market.audit_active,
            compute_mult=market.compute_cost_multiplier,
            competitor_pressure=market.competitor_pressure,
            fitness_score=self.fitness_score,
            capsule_strength=self.glycocalyx.capsule.strength,
        )
        if acquired_plasmid is not None:
            self.narrative_log.append(
                f"Tag {market.day}: Sexpili erwarb Plasmid '{acquired_plasmid.info.name_de}' "
                f"für {plasmid_spent:.2f} €."
            )

        # 5. Compliance-Prüfung (Encapsuline + Peptidoglykan)
        gross_sales = self.plasma_membrane.gross_today_eur
        total_revenue = round(gross_sales + plasmid_lic_rev, 2)
        penalties = self.compliance_guard.handle_audit(
            audit_active=market.audit_active,
            audit_severity=market.audit_severity,
            audit_rigor=float(directives.get("audit_rigor", 0.84)),
            encapsulin_integrity=self.encapsulins.vault_integrity,
            plasmid_audit_bonus=p_fx.get("audit_defense_bonus", 0.0),
            guardrail_strictness=self.gardener.policy.guardrail_strictness,
            revenue_base_eur=max(self.profile.base_price_eur, total_revenue),
        )
        if market.audit_active and penalties == 0.0:
            self.narrative_log.append(
                f"Tag {market.day}: Compliance-Audit über Encapsuline & Peptidoglykan ohne Bußgeld bestanden."
            )

        # 6. Elektronentransportkette & ATP-Synthase
        fixed_infra = self.profile.fixed_infra_per_day_eur
        proton_grad = self.etc.process_flow(
            gross_revenue_eur=total_revenue,
            payment_fees_eur=self.plasma_membrane.fees_today_eur,
            cogs_eur=total_cogs,
            fixed_infra_eur=fixed_infra,
            tax_rate=self.profile.tax_reserve_rate,
        )
        atp_gen = self.atp_synthase.synthesize(proton_grad, scale_factor=self.scale_factor)

        # Volutin-Compute-Puffer bei Überschuss sanft auffüllen
        volutin_ratio = float(directives.get("volutin_hedge_ratio", 0.18))
        if proton_grad > fixed_infra * 1.2 and self.ledger.cash_eur > self.profile.seed_capital_eur * 0.5:
            topup = min(proton_grad * volutin_ratio * 0.25, self.ledger.cash_eur * 0.05)
            added_vol = self.inclusion_bodies.volutin.top_up(topup)
            self.ledger.cash_eur = round(max(0.0, self.ledger.cash_eur - added_vol), 2)

        # 7. Doppelte Buchführung
        snap = self.ledger.record_day(
            day=market.day,
            revenue_eur=total_revenue,
            cogs_eur=total_cogs,
            payment_fees_eur=self.plasma_membrane.fees_today_eur,
            fixed_infra_eur=fixed_infra,
            marketing_eur=signals["marketing_eur"],
            plasmid_spend_eur=plasmid_spent,
            penalties_eur=penalties,
            phb_reserve=self.inclusion_bodies.phb,
            volutin_pool=self.inclusion_bodies.volutin,
            atp_balance=self.atp_synthase.atp_balance,
            atp_generated_today=atp_gen,
            atp_consumed_today=self.atp_synthase.consumed_today,
        )

        # 8. Kunden-Lebenszyklus, Kapsel & Schleimschicht aktualisieren
        self.lifecycle.update(
            fulfilled_orders=fulfilled,
            avg_quality=avg_quality,
            slime_stickiness=self.glycocalyx.slime_layer.stickiness,
            pili_retention_boost=self.pili.retention_boost,
            marketing_spend_eur=signals["marketing_eur"],
            avg_price_eur=self.pricing_engine.current_price_eur,
            dormant=False,
        )
        fulfillment_ratio = fulfilled / max(1, self.last_demand_count)
        self.glycocalyx.capsule.update(
            avg_quality=avg_quality,
            trust_bonus=p_fx.get("trust_bonus", 0.0),
            fulfillment_ratio=min(1.0, fulfillment_ratio),
        )
        self.glycocalyx.slime_layer.update(
            satisfaction=self.lifecycle.satisfaction,
            pili_focus=float(directives.get("pili_retention_focus", 0.68)),
        )

        # 9. Fitness, Evolution & Runway-Schutz / Endospore / FtsZ-Ernte
        self.fitness_score = self._compute_fitness(snap)
        self.health_score = round(
            min(
                1.0,
                max(
                    0.15,
                    avg_quality * 0.45
                    + min(1.0, snap.runway_days / 60.0) * 0.35
                    + self.glycocalyx.total_protection_index() * 0.20,
                ),
            ),
            3,
        )
        self.cytoplasm.utilization = self.cytoskeleton.mreb.utilization

        mut_rec = self.mutation_engine.step(
            day=market.day,
            fitness=self.fitness_score,
            chromosome=self.chromosome,
            nucleoid=self.nucleoid,
            guardrail_strictness=self.gardener.policy.guardrail_strictness,
            dormant=False,
        )
        if mut_rec is not None:
            self.narrative_log.append(
                f"Tag {market.day}: Genom-Mutation {mut_rec.operon_id}.{mut_rec.parameter} "
                f"({mut_rec.old_value}→{mut_rec.new_value}) -> {mut_rec.outcome}."
            )

        conserving, recommend_spore = self.runway_breaker.evaluate(
            liquid_funds_eur=snap.cash_eur + snap.phb_reserve_eur,
            daily_fixed_burn_eur=fixed_infra,
            recent_net_profit_eur=snap.daily_net_profit_eur,
            demand_ratio=market.macro_demand_index,
            dormancy_runway_trigger=self.chromosome.get_param(
                "OP_CRISIS_SPORULATION", "dormancy_runway_trigger", 18.0
            ),
            dormancy_demand_trigger=self.chromosome.get_param(
                "OP_CRISIS_SPORULATION", "dormancy_demand_trigger", 0.34
            ),
        )
        if recommend_spore and self.gardener.policy.auto_endospore_enabled:
            self.enter_endospore(reason="Automatischer Dürre-/Runway-Schutz")
        elif conserving:
            self.mode = "conserving"
        else:
            self.mode = "active"

        # FtsZ-Ring schüttet Überschuss als Ernte an den Gärtner ab
        harvested = self.cytoskeleton.ftsz.evaluate_and_harvest(
            day=market.day,
            phb_balance_eur=self.inclusion_bodies.phb.balance_eur,
            harvest_threshold_eur=self.gardener.policy.harvest_threshold_eur,
            harvest_ratio=self.gardener.policy.harvest_ratio,
            operon_aggression=float(directives.get("harvest_aggression", 1.0)),
            dormant=self.endospores.is_dormant,
        )
        if harvested > 0:
            self.inclusion_bodies.phb.withdraw(harvested)
            self.ledger.register_harvest(harvested)
            snap.phb_reserve_eur = self.inclusion_bodies.phb.balance_eur
            snap.cumulative_harvested_eur = self.ledger.cumulative_harvested_eur
            self.narrative_log.append(
                f"Tag {market.day}: FtsZ-Ring schnürt {harvested:.2f} € Spin-Off-Ernte für den Gärtner ab!"
            )

        if snap.cash_eur + snap.phb_reserve_eur <= 0.0 and not self.endospores.is_dormant:
            self.alive = False

        self._build_active_trace(
            market=market,
            snap=snap,
            total_cogs=total_cogs,
            atp_gen=atp_gen,
            harvested=harvested,
        )
        return snap

    def enter_endospore(self, reason: str) -> dict[str, Any]:
        seed_pkg = self.endospores.enter_dormancy(
            day=self.day,
            genes=self.chromosome.export_genes(),
            plasmid_ids=self.plasmid_registry.export_installed_ids(),
            phb_eur=self.inclusion_bodies.phb.balance_eur,
            active_customers=self.lifecycle.active_customers,
        )
        self.mode = "dormant_endospore"
        self.narrative_log.append(
            f"Tag {self.day}: Endosporen-Bildung ({reason}) — Kortex senkt Fixkosten um 93 %."
        )
        return seed_pkg

    def export_spore_seed(self) -> dict[str, Any]:
        return self.endospores.coat.seal_seed(
            {
                "seed_template": self.profile.seed.value,
                "scale_preset": self.profile.scale.value,
                "genes": self.chromosome.export_genes(),
                "plasmid_ids": self.plasmid_registry.export_installed_ids(),
                "fitness_score": self.fitness_score,
                "capsule_strength": self.glycocalyx.capsule.strength,
            }
        )

    def import_spore_seed(self, seed_pkg: dict[str, Any], crossbreed: bool = False) -> None:
        payload = seed_pkg.get("payload", seed_pkg)
        gene_map = payload.get("genes")
        if isinstance(gene_map, dict):
            if crossbreed:
                current = self.chromosome.export_genes()
                blended: dict[str, dict[str, float]] = {}
                for op_id, params in current.items():
                    blended[op_id] = {}
                    partner = gene_map.get(op_id, {})
                    for p, v in params.items():
                        pv = partner.get(p, v)
                        blended[op_id][p] = round((float(v) + float(pv)) / 2.0, 4)
                self.chromosome.import_genes(
                    blended, self.nucleoid, self.gardener.policy.guardrail_strictness
                )
            else:
                self.chromosome.import_genes(
                    gene_map, self.nucleoid, self.gardener.policy.guardrail_strictness
                )
        for pid in payload.get("plasmid_ids", []):
            if pid in self.plasmid_registry.plasmids:
                self.plasmid_registry.install(pid, day=self.day)
        self.endospores.coat.seal_seed(
            {
                "seed_template": self.profile.seed.value,
                "genes": self.chromosome.export_genes(),
                "plasmid_ids": self.plasmid_registry.export_installed_ids(),
            }
        )

    def inject_custom_plasmid(
        self,
        name_de: str,
        hook_point: str,
        source_code: str,
    ) -> str:
        pid = f"plasmid_custom_{len(self.plasmid_registry.plasmids) + 1}"
        try:
            self.plasmid_registry.register_custom_plasmid(
                plasmid_id=pid,
                name_de=name_de,
                hook_point=hook_point,
                source_code=source_code,
                day=self.day,
            )
        except PlasmidSecurityError:
            raise
        self.narrative_log.append(f"Tag {self.day}: Labor-Plasmid '{name_de}' im AST validiert & geladen.")
        return pid

    def _build_dormant_trace(self, dehydrated_infra: float) -> None:
        self.last_causal_trace = [
            CausalFlowEvent(
                step=1,
                source_id="exosporium",
                target_id="spore_protoplast",
                flow_type="signal",
                label_de="Exosporium überwacht Markt-Heartbeat",
                magnitude=self.endospores.exosporium.last_signal_strength,
                unit="Index",
            ),
            CausalFlowEvent(
                step=2,
                source_id="endospores",
                target_id="spore_cortex",
                flow_type="defense",
                label_de="Kortex reduziert Fixkosten auf Minimal-Erhalt",
                magnitude=dehydrated_infra,
                unit="€/Tag",
            ),
            CausalFlowEvent(
                step=3,
                source_id="spore_protoplast",
                target_id="phb_reserve",
                flow_type="money",
                label_de="PHB-Notreserve schützt versiegeltes Genom",
                magnitude=self.inclusion_bodies.phb.balance_eur,
                unit="€",
            ),
        ]

    def _build_active_trace(
        self,
        market: MarketTickState,
        snap: LedgerSnapshot,
        total_cogs: float,
        atp_gen: float,
        harvested: float,
    ) -> None:
        trace = [
            CausalFlowEvent(
                step=1,
                source_id="magnetosomes",
                target_id="bacterial_chromosome",
                flow_type="signal",
                label_de="Trend-Kompass aktiviert Operon-Promotoren",
                magnitude=market.macro_demand_index,
                unit="Nachfrage",
            ),
            CausalFlowEvent(
                step=2,
                source_id="bacterial_chromosome",
                target_id="mrna",
                flow_type="mrna",
                label_de="Transkription aktiver Gen-Operons in mRNA",
                magnitude=float(len(self.mrna.pool)),
                unit="Transkripte",
            ),
            CausalFlowEvent(
                step=3,
                source_id="s_layer",
                target_id="outer_membrane",
                flow_type="defense",
                label_de="S-Layer & LPS-Guard wehren Angriffe ab",
                magnitude=float(self.last_blocked_count),
                unit="Abgewehrt",
            ),
            CausalFlowEvent(
                step=4,
                source_id="plasma_membrane",
                target_id="ribosome_70s",
                flow_type="money",
                label_de="Bezahlte Kundenorders erreichen 70S-Ribosom",
                magnitude=snap.daily_revenue_eur,
                unit="€",
            ),
            CausalFlowEvent(
                step=5,
                source_id="glycogen_cache",
                target_id="carboxysomes",
                flow_type="product",
                label_de="Semantic Cache & Carboxysom senken Compute-COGS",
                magnitude=round(total_cogs, 2),
                unit="€ COGS",
            ),
            CausalFlowEvent(
                step=6,
                source_id="ribosome_70s",
                target_id="secretion_systems",
                flow_type="product",
                label_de="Qualitätsgeprüfte Briefings/API-Payloads exportiert",
                magnitude=float(self.last_fulfilled_count),
                unit="Produkte",
            ),
            CausalFlowEvent(
                step=7,
                source_id="etc",
                target_id="atp_synthase",
                flow_type="atp",
                label_de="Netto-Marge treibt ATP-Synthase an",
                magnitude=round(atp_gen, 2),
                unit="ATP",
            ),
            CausalFlowEvent(
                step=8,
                source_id="phb_reserve",
                target_id="ftsz_ring",
                flow_type="harvest",
                label_de=(
                    "FtsZ-Ring schnürt Ernte für Gärtner ab"
                    if harvested > 0
                    else "PHB-Reserve wächst bis zur Ernte-Schwelle"
                ),
                magnitude=harvested if harvested > 0 else snap.phb_reserve_eur,
                unit="€",
            ),
        ]
        self.last_causal_trace = trace

    def collect_organelle_telemetry(self) -> dict[str, OrganelleTelemetry]:
        """Liefert Telemetrie für alle 53 aktiven Prokaryonten-Strukturen + 7 Viability-Module."""
        dormant = self.endospores.is_dormant
        gardener_profit = self.ledger.cumulative_net_profit_eur
        items = [
            # Envelope (11)
            self.s_layer.to_telemetry(),
            self.outer_membrane.to_telemetry(),
            self.outer_membrane.lps_guard.to_telemetry(),
            self.porins.to_telemetry(),
            self.periplasm.to_telemetry(),
            self.cell_wall.to_telemetry(),
            self.cell_wall.peptidoglycan.to_telemetry(),
            self.plasma_membrane.to_telemetry(),
            self.glycocalyx.to_telemetry(),
            self.glycocalyx.capsule.to_telemetry(),
            self.glycocalyx.slime_layer.to_telemetry(),
            # Cytoskeleton (5)
            self.cytoplasm.to_telemetry(),
            self.cytoplasm.cytosol.to_telemetry(),
            self.cytoskeleton.to_telemetry(),
            self.cytoskeleton.ftsz.to_telemetry(),
            self.cytoskeleton.mreb.to_telemetry(),
            # Genetics (9)
            self.nucleoid.to_telemetry(self.chromosome.genome_version),
            self.chromosome.to_telemetry(),
            self.plasmid_registry.to_telemetry(),
            self.mrna.to_telemetry(),
            self.ribosome_70s.to_telemetry(),
            self.ribosome_70s.subunit_30s.to_telemetry(),
            self.ribosome_70s.subunit_50s.to_telemetry(),
            self.ribosome_70s.trna.to_telemetry(),
            self.ribosome_70s.rrna.to_telemetry(),
            # Motility (7)
            self.flagellum.to_telemetry(),
            self.flagellum.basal_body.to_telemetry(),
            self.flagellum.hook.to_telemetry(),
            self.flagellum.filament.to_telemetry(),
            self.fimbriae.to_telemetry(),
            self.pili.to_telemetry(),
            self.sex_pili.to_telemetry(),
            # Metabolism (10)
            self.etc.to_telemetry(),
            self.atp_synthase.to_telemetry(),
            self.thylakoids.to_telemetry(),
            self.thylakoids.phycobilisomes.to_telemetry(),
            self.microcompartments.to_telemetry(),
            self.carboxysomes.to_telemetry(),
            self.metabolosomes.to_telemetry(),
            self.encapsulins.to_telemetry(),
            self.magnetosomes.to_telemetry(),
            self.gas_vesicles.to_telemetry(),
            # Storage (5)
            self.inclusion_bodies.to_telemetry(),
            self.inclusion_bodies.phb.to_telemetry(),
            self.inclusion_bodies.glycogen.to_telemetry(),
            self.inclusion_bodies.volutin.to_telemetry(),
            self.inclusion_bodies.sulfur.to_telemetry(),
            # Dormancy (5)
            self.endospores.to_telemetry(),
            self.endospores.exosporium.to_telemetry(dormant),
            self.endospores.coat.to_telemetry(),
            self.endospores.cortex.to_telemetry(dormant),
            self.endospores.protoplast.to_telemetry(dormant),
            # Secretion (1)
            self.secretion.to_telemetry(),
            # Viability (7)
            self.pricing_engine.to_telemetry(),
            self.ledger.to_telemetry(),
            self.quality_gate.to_telemetry(),
            self.lifecycle.to_telemetry(),
            self.runway_breaker.to_telemetry(),
            self.compliance_guard.to_telemetry(),
            self.gardener.to_telemetry(gardener_profit),
        ]
        return {t.id: t for t in items}
