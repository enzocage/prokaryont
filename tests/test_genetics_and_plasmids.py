"""Tests für Chromosom, kausale mRNA->70S Expression, Evolution & AST-Plasmid-Sandbox."""

from __future__ import annotations

import random
import pytest

from prokaryont.config import ScalePreset, SeedTemplate, get_economics_profile
from prokaryont.genetics.chromosome import PromoterEvaluator
from prokaryont.genetics.plasmids import PlasmidSandbox, PlasmidSecurityError
from prokaryont.organism import EconomicProkaryote
from prokaryont.simulation import SimulationEngine


def test_promoter_evaluator_and_causal_mrna_to_70s_ribosome():
    assert PromoterEvaluator.evaluate("always", {}) is True
    assert PromoterEvaluator.evaluate("threat_level > 0.2 and not dormant", {"threat_level": 0.4, "dormant": False}) is True
    assert PromoterEvaluator.evaluate("runway_days < 20", {"runway_days": 45.0}) is False

    # Beide Saatgut-Templates müssen über 70S-Ribosom konkrete Produkte liefern
    for seed in (SeedTemplate.B2B_BRIEFING, SeedTemplate.MICRO_API):
        eng = SimulationEngine(seed_template=seed, scale_preset=ScalePreset.SOLOPRENEUR, rng_seed=19)
        snap = eng.step(3)
        assert len(snap.active_mrna) > 0
        assert len(snap.recent_artifacts) > 0
        art = snap.recent_artifacts[0]
        assert art.seed_template == seed
        assert len(art.causal_gene_ids) > 0
        if seed == SeedTemplate.B2B_BRIEFING:
            assert art.content_markdown is not None and "# " in art.content_markdown
        else:
            assert art.content_json is not None and art.content_json["verification"]["status"] == "VALIDATED"


def test_plasmid_sandbox_blocks_unsafe_code_and_runs_safe_code():
    unsafe_samples = [
        "import os\ndef execute(ctx):\n    return {}",
        "from sys import exit\ndef execute(ctx):\n    return {}",
        "def execute(ctx):\n    return {'x': ().__class__.__bases__}",
        "def execute(ctx):\n    while True:\n        pass\n    return {}",
        "def execute(ctx):\n    return {'x': eval('1+1')}",
        "def not_execute(ctx):\n    return {}",
    ]
    for code in unsafe_samples:
        with pytest.raises(PlasmidSecurityError):
            PlasmidSandbox.validate_and_compile(code)

    # Gültiger Code inkl. Laufzeitfehler-Isolation (ZeroDivisionError crasht Organismus nicht)
    fn_ok = PlasmidSandbox.validate_and_compile(
        "def execute(ctx):\n    return {'price_multiplier': 1.07 if ctx.get('demand_ratio', 1.0) > 0.5 else 1.0}\n"
    )
    assert PlasmidSandbox.run_safe(fn_ok, {"demand_ratio": 1.2}) == {"price_multiplier": 1.07}

    fn_div_zero = PlasmidSandbox.validate_and_compile("def execute(ctx):\n    return {'x': 1 / 0}\n")
    assert PlasmidSandbox.run_safe(fn_div_zero, {}) == {}


def test_mutation_engine_records_and_nucleoid_enforces_guardrails():
    eng = SimulationEngine(
        seed_template=SeedTemplate.B2B_BRIEFING,
        scale_preset=ScalePreset.SOLOPRENEUR,
        rng_seed=42,
    )
    snap = eng.step(35)
    assert len(snap.recent_mutations) >= 1
    assert eng.organism.chromosome.genome_version >= 1
    assert len(eng.organism.nucleoid.snapshots) >= 1

    # Sporen-Export & Import/Crossbreeding
    exported = eng.organism.export_spore_seed()
    assert "sha256" in exported and len(exported["sha256"]) == 64

    child_profile = get_economics_profile(ScalePreset.SOLOPRENEUR, SeedTemplate.B2B_BRIEFING)
    child = EconomicProkaryote(profile=child_profile, rng=random.Random(99), imported_spore_seed=exported)
    assert child.endospores.coat.latest_hash != ""
