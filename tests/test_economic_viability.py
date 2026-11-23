"""Ökonomischer Machbarkeitsbeweis: Profitabilität, Dürre-Überleben & Gärtner-Hebel."""

from __future__ import annotations

import pytest

from prokaryont.config import ScalePreset, ScenarioPreset, SeedTemplate
from prokaryont.simulation import SimulationEngine


@pytest.mark.parametrize("seed", [SeedTemplate.B2B_BRIEFING, SeedTemplate.MICRO_API])
@pytest.mark.parametrize("scale", [ScalePreset.NANO, ScalePreset.SOLOPRENEUR, ScalePreset.GROWTH])
def test_180_day_profitability_and_gardener_leverage_all_presets(seed: SeedTemplate, scale: ScalePreset):
    eng = SimulationEngine(
        seed_template=seed,
        scale_preset=scale,
        scenario_preset=ScenarioPreset.REALISTIC_ECOSYSTEM,
        rng_seed=42,
    )
    snap = eng.step(180)
    ledger = snap.ledger
    bench = snap.benchmark_latest

    assert snap.alive is True
    assert ledger.cumulative_revenue_eur > ledger.cumulative_costs_eur * 1.35
    assert ledger.cumulative_net_profit_eur > 0.0
    assert ledger.cumulative_harvested_eur > 0.0
    assert eng.organism.cytoskeleton.ftsz.contractions_total >= 1
    assert bench.gardener_profit_per_hour > bench.engineer_profit_per_hour * 5.0


@pytest.mark.parametrize("scale", [ScalePreset.NANO, ScalePreset.SOLOPRENEUR, ScalePreset.GROWTH])
def test_drought_survival_triggers_endospore_and_germinates(scale: ScalePreset):
    eng = SimulationEngine(
        seed_template=SeedTemplate.B2B_BRIEFING,
        scale_preset=scale,
        scenario_preset=ScenarioPreset.DROUGHT_SURVIVAL,
        rng_seed=42,
    )
    snap = eng.step(180)
    assert snap.alive is True
    assert eng.organism.endospores.dormancy_episodes >= 1
    assert eng.organism.endospores.total_dormant_days >= 20
    # Nach Beendigung der Dürre erfolgreich gekeimt
    assert snap.mode == "active"
    assert snap.ledger.cumulative_net_profit_eur > 0.0

    # Kortex muss Fixkosten im Schlaf um >= 80 % reduzieren
    normal_infra = eng.economics.fixed_infra_per_day_eur
    dormant_burn = eng.organism.endospores.cortex.dehydrated_daily_burn(normal_infra)
    assert dormant_burn <= normal_infra * 0.20


def test_cyber_and_audit_storm_defense():
    eng = SimulationEngine(
        seed_template=SeedTemplate.MICRO_API,
        scale_preset=ScalePreset.SOLOPRENEUR,
        scenario_preset=ScenarioPreset.CYBER_AND_AUDIT_STORM,
        rng_seed=42,
    )
    snap = eng.step(180)
    assert snap.alive is True
    assert eng.organism.s_layer.blocked_attacks_total > 0
    assert eng.organism.compliance_guard.audits_passed > 0
    assert snap.ledger.cumulative_net_profit_eur > 0.0
