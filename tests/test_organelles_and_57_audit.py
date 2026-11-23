"""Tests für die 57-Strukturen-Prüfung, 7 Viability-Module und Kausalität der Organellen."""

from __future__ import annotations

import random

from prokaryont.config import ScalePreset, ScenarioPreset, SeedTemplate, ShockType, get_economics_profile
from prokaryont.models import CustomerRequest
from prokaryont.organism import EconomicProkaryote
from prokaryont.registry import REGISTRY_BY_ID, STRUCTURE_REGISTRY, get_registry_summary


def test_57_structures_and_7_viability_audit():
    summary = get_registry_summary()
    assert summary["prokaryote_total"] == 57
    assert summary["prokaryote_implemented"] == 53
    assert summary["prokaryote_merged"] == 3
    assert summary["prokaryote_excluded"] == 1
    assert summary["viability_total"] == 7
    assert summary["total_all"] == 64

    # Exakte Überprüfung der 4 begründet gemergten / ausgeschlossenen Strukturen
    assert REGISTRY_BY_ID["pseudopeptidoglycan"].status == "merged"
    assert REGISTRY_BY_ID["pseudopeptidoglycan"].merged_into == "peptidoglycan"
    assert REGISTRY_BY_ID["archaella"].status == "merged"
    assert REGISTRY_BY_ID["archaella"].merged_into == "flagella"
    assert REGISTRY_BY_ID["chlorosomes"].status == "merged"
    assert REGISTRY_BY_ID["chlorosomes"].merged_into == "phycobilisomes"
    assert REGISTRY_BY_ID["crescentin"].status == "excluded"


def test_all_60_active_modules_emit_live_telemetry():
    profile = get_economics_profile(ScalePreset.SOLOPRENEUR, SeedTemplate.B2B_BRIEFING)
    org = EconomicProkaryote(profile=profile, rng=random.Random(42))
    telemetry = org.collect_organelle_telemetry()

    expected_ids = {
        entry.id
        for entry in STRUCTURE_REGISTRY
        if entry.status in ("active", "submodule")
    }
    assert len(expected_ids) == 60
    assert set(telemetry.keys()) == expected_ids


def test_envelope_blocks_malicious_and_fraudulent_requests():
    profile = get_economics_profile(ScalePreset.SOLOPRENEUR, SeedTemplate.B2B_BRIEFING)
    org = EconomicProkaryote(profile=profile, rng=random.Random(7))

    reqs = [
        CustomerRequest(
            request_id="legit-1",
            channel="seo",
            segment="standard",
            offered_price_eur=49.0,
            complexity=0.4,
            is_malicious=False,
            is_fraudulent=False,
            topic_key="eu_ai_act",
            customer_id="c1",
        ),
        CustomerRequest(
            request_id="bot-1",
            channel="edge",
            segment="standard",
            offered_price_eur=0.0,
            complexity=0.5,
            is_malicious=True,
            is_fraudulent=False,
            topic_key="eu_ai_act",
            customer_id="b1",
        ),
        CustomerRequest(
            request_id="fraud-1",
            channel="edge",
            segment="standard",
            offered_price_eur=49.0,
            complexity=0.5,
            is_malicious=False,
            is_fraudulent=True,
            topic_key="eu_ai_act",
            customer_id="f1",
        ),
    ]
    survived_s = org.s_layer.filter_traffic(reqs, strictness_override=0.85, firewall_bonus=0.05)
    assert len(survived_s) == 2
    assert org.s_layer.blocked_today == 1

    survived_outer = org.outer_membrane.screen_requests(survived_s, lps_threshold=0.85, fraud_block_bonus=0.05)
    assert len(survived_outer) == 1
    assert survived_outer[0].request_id == "legit-1"
    assert org.outer_membrane.lps_guard.fraud_blocked_today == 1


def test_glycogen_cache_and_metabolosomes_reduce_cogs():
    profile = get_economics_profile(ScalePreset.SOLOPRENEUR, SeedTemplate.B2B_BRIEFING)
    org = EconomicProkaryote(profile=profile, rng=random.Random(11))

    # Wiederholte Hits müssen im Schnitt deutlich unter Rohkosten liegen
    hit_count = 0
    for i in range(40):
        if org.inclusion_bodies.glycogen.lookup_or_store("eu_ai_act", 0.80, 0.12, (i % 10) / 10.0):
            hit_count += 1
    assert hit_count >= 25

    cost_uncached = org.carboxysomes.concentrate_value(cache_hit=False, sulfur_ready=False, raw_cost_eur=4.0)
    cost_cached = org.carboxysomes.concentrate_value(cache_hit=True, sulfur_ready=True, raw_cost_eur=4.0)
    assert cost_cached < cost_uncached

    arb_cost, ok = org.metabolosomes.arbitrage_and_recover(
        unit_cost_eur=cost_uncached, arbitrage_ratio=0.6, plasmid_discount=0.15, dirty_input=True
    )
    assert ok is True
    assert arb_cost < cost_uncached
