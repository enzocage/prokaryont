"""Kausale Genexpression: mRNA-Transkripte, tRNA-Adapter, rRNA & 70S-Ribosomen (30S + 50S)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from prokaryont.adapters.llm import LLMAdapter, LLMSynthesisResult
from prokaryont.config import SeedTemplate
from prokaryont.environment.products import synthesize_concrete_product
from prokaryont.models import (
    CustomerRequest,
    MessengerRNATranscript,
    OperonSpec,
    OrganelleTelemetry,
    ProductArtifact,
)


class MessengerRNA:
    """Verwaltet kurzlebige transkribierte Arbeits- & Strategie-Pläne mit TTL-Zerfall."""

    def __init__(self) -> None:
        self.pool: list[MessengerRNATranscript] = []
        self._seq: int = 0
        self.total_transcribed: int = 0
        self.total_decayed: int = 0

    def transcribe(
        self,
        day: int,
        active_operons: list[OperonSpec],
        plasmid_directives: dict[str, dict[str, Any]],
    ) -> list[MessengerRNATranscript]:
        # Bestehende mRNA altert um 1 Tag und zerfällt bei TTL == 0
        surviving: list[MessengerRNATranscript] = []
        for item in self.pool:
            item.remaining_ttl -= 1
            if item.remaining_ttl > 0:
                surviving.append(item)
            else:
                self.total_decayed += 1
        self.pool = surviving

        existing_ops = {m.operon_id for m in self.pool}
        newly_created: list[MessengerRNATranscript] = []
        for op in active_operons:
            directives: dict[str, float | str | bool] = {
                k: float(v) for k, v in op.parameters.items()
            }
            # Wenn bereits frische mRNA existiert, aktualisieren; sonst neu transkribieren
            if op.operon_id in existing_ops:
                for m in self.pool:
                    if m.operon_id == op.operon_id:
                        m.directives = directives
                        m.remaining_ttl = m.ttl_days
                continue
            self._seq += 1
            ttl = 2 if op.category in ("defense", "harvest", "dormancy") else 3
            priority = 0.95 if op.category in ("defense", "dormancy") else 0.72
            transcript = MessengerRNATranscript(
                transcript_id=f"mrna-{day}-{self._seq}",
                operon_id=op.operon_id,
                created_day=day,
                ttl_days=ttl,
                remaining_ttl=ttl,
                priority=priority,
                directives=directives,
            )
            self.pool.append(transcript)
            newly_created.append(transcript)
            self.total_transcribed += 1

        # Aktive Plasmide emittieren ebenfalls transiente mRNA-Direktiven
        for plasmid_id, p_dir in plasmid_directives.items():
            key = f"PLASMID::{plasmid_id}"
            self.pool = [m for m in self.pool if m.operon_id != key]
            self._seq += 1
            clean_dir = {
                k: v for k, v in p_dir.items() if isinstance(v, (float, int, str, bool))
            }
            transcript = MessengerRNATranscript(
                transcript_id=f"mrna-p-{day}-{self._seq}",
                operon_id=key,
                created_day=day,
                ttl_days=1,
                remaining_ttl=1,
                priority=0.82,
                directives=clean_dir,
            )
            self.pool.append(transcript)
            newly_created.append(transcript)
            self.total_transcribed += 1

        return newly_created

    def get_merged_directives(self) -> dict[str, float | str | bool]:
        merged: dict[str, float | str | bool] = {}
        for m in sorted(self.pool, key=lambda x: x.priority):
            merged.update(m.directives)
            m.translated_count += 1
        return merged

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="mrna",
            name_de="mRNA-Transkripte",
            system_id="genetics",
            health=1.0,
            activity=min(1.0, len(self.pool) / 10.0),
            load=min(1.0, len(self.pool) / 14.0),
            efficiency=1.0,
            state_label_de=f"{len(self.pool)} aktive Transkripte",
            metrics={
                "active_transcripts": len(self.pool),
                "total_transcribed": self.total_transcribed,
                "total_decayed": self.total_decayed,
            },
        )


@dataclass
class TransferRNA:
    """tRNA-Codon-Adapter: bindet Kundenanfragen an typisierte Domänen-Skills."""

    adapter_catalog: dict[str, dict[str, str]] = field(
        default_factory=lambda: {
            "eu_ai_act": {"skill": "regulatory_synthesis", "template": "compliance_matrix_v2"},
            "market_intel": {"skill": "competitor_benchmark", "template": "executive_brief_v3"},
            "supply_chain": {"skill": "risk_scoring", "template": "resilience_dossier_v2"},
            "kyb_verify": {"skill": "entity_enrichment", "template": "json_schema_strict_v2"},
            "vat_check": {"skill": "tax_validation", "template": "json_schema_strict_v2"},
            "fraud_score": {"skill": "anomaly_scoring", "template": "json_schema_strict_v2"},
        }
    )
    bindings_count: int = 0

    def match_codon(self, topic_key: str, seed_template: SeedTemplate) -> dict[str, str]:
        self.bindings_count += 1
        if topic_key in self.adapter_catalog:
            return self.adapter_catalog[topic_key]
        if seed_template == SeedTemplate.B2B_BRIEFING:
            return {"skill": "domain_briefing", "template": "executive_brief_v3"}
        return {"skill": "payload_enrichment", "template": "json_schema_strict_v2"}

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="trna",
            name_de="tRNA (Skill-Adapter)",
            system_id="genetics",
            health=1.0,
            activity=min(1.0, self.bindings_count / 500.0),
            load=0.35,
            efficiency=1.0,
            state_label_de=f"{len(self.adapter_catalog)} Skill-Codons bereit",
            metrics={
                "codons_available": len(self.adapter_catalog),
                "bindings_total": self.bindings_count,
            },
        )


@dataclass
class RibosomalRNA:
    """rRNA: Strukturelles Rückgrat & Formatierungs-Fidelität des 70S-Ribosoms."""

    fidelity_level: float = 0.96
    schema_checks_passed: int = 0

    def verify_structure(self, seed_template: SeedTemplate, quality_bias: float) -> float:
        self.schema_checks_passed += 1
        base = self.fidelity_level if seed_template == SeedTemplate.MICRO_API else 0.94
        return round(min(0.995, max(0.75, base + quality_bias * 0.03)), 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="rrna",
            name_de="rRNA (Synthese-Fidelität)",
            system_id="genetics",
            health=1.0,
            activity=0.75,
            load=0.40,
            efficiency=self.fidelity_level,
            state_label_de=f"Fidelität {self.fidelity_level * 100:.1f} %",
            metrics={
                "fidelity_level": self.fidelity_level,
                "schema_checks_passed": self.schema_checks_passed,
            },
        )


class Subunit30S:
    """Kleine 30S-Ribosomen-Untereinheit: decodiert mRNA, prüft Budget & bindet tRNA."""

    def __init__(self) -> None:
        self.decoded_orders: int = 0
        self.rejected_budget: int = 0

    def decode(
        self,
        request: CustomerRequest,
        trna: TransferRNA,
        seed_template: SeedTemplate,
        available_atp: float,
        estimated_atp_needed: float,
    ) -> dict[str, Any] | None:
        if available_atp < estimated_atp_needed * 0.35:
            self.rejected_budget += 1
            return None
        codon = trna.match_codon(request.topic_key, seed_template)
        self.decoded_orders += 1
        return {
            "request": request,
            "codon": codon,
            "seed_template": seed_template,
        }

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="subunit_30s",
            name_de="30S-Untereinheit (mRNA-Decoder)",
            system_id="genetics",
            health=1.0,
            activity=min(1.0, self.decoded_orders / 200.0),
            load=0.45,
            efficiency=1.0,
            state_label_de=f"{self.decoded_orders} Aufträge decodiert",
            metrics={
                "decoded_orders": self.decoded_orders,
                "rejected_budget": self.rejected_budget,
            },
        )


class Subunit50S:
    """Große 50S-Ribosomen-Untereinheit: katalysiert das konkrete Produkt über LLM/Pipeline."""

    def __init__(self, llm_adapter: LLMAdapter) -> None:
        self.llm_adapter = llm_adapter
        self.synthesized_count: int = 0

    def catalyze(
        self,
        decoded_bundle: dict[str, Any],
        rrna: RibosomalRNA,
        day: int,
        target_cost_eur: float,
        quality_boost: float,
        from_cache: bool,
        active_gene_ids: list[str],
        generate_full_payload: bool = True,
    ) -> tuple[ProductArtifact | None, LLMSynthesisResult | None, float]:
        req: CustomerRequest = decoded_bundle["request"]
        seed: SeedTemplate = decoded_bundle["seed_template"]
        fidelity = rrna.verify_structure(seed, quality_boost)

        synth_res: LLMSynthesisResult | None = None
        if not from_cache and generate_full_payload:
            prompt = (
                f"Erzeuge {seed.value} für Thema '{req.topic_key}' im Segment '{req.segment}' "
                f"mit Skill {decoded_bundle['codon']['skill']}."
            )
            synth_res = self.llm_adapter.synthesize(
                prompt=prompt,
                context={
                    "topic_key": req.topic_key,
                    "segment": req.segment,
                    "seed_template": seed.value,
                    "quality_boost": fidelity,
                    "target_cost_eur": target_cost_eur,
                },
                budget_eur=max(0.05, req.offered_price_eur * 0.45),
            )
            cogs = synth_res.cost_eur
            provider = synth_res.provider_name
        else:
            cogs = target_cost_eur
            provider = "glycogen_semantic_cache" if from_cache else self.llm_adapter.provider_name

        self.synthesized_count += 1
        quality = round(min(0.99, max(0.68, fidelity - req.complexity * 0.04 + quality_boost * 0.04)), 4)

        artifact: ProductArtifact | None = None
        if generate_full_payload:
            artifact = synthesize_concrete_product(
                day=day,
                request=req,
                seed_template=seed,
                cogs_eur=cogs,
                quality_score=quality,
                from_cache=from_cache,
                synthesized_via=provider,
                summary_line=synth_res.content_text if synth_res else None,
                causal_gene_ids=active_gene_ids,
            )
        return artifact, synth_res, cogs

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="subunit_50s",
            name_de="50S-Untereinheit (Produkt-Katalyse)",
            system_id="genetics",
            health=1.0,
            activity=min(1.0, self.synthesized_count / 200.0),
            load=0.55,
            efficiency=1.0,
            state_label_de=f"{self.synthesized_count} Produkte synthetisiert",
            metrics={
                "synthesized_count": self.synthesized_count,
                "llm_provider": self.llm_adapter.provider_name,
            },
        )


class Ribosome70S:
    """70S-Ribosomen-Komplex (30S + 50S + tRNA + rRNA): kausale Produktionsfabrik."""

    def __init__(self, llm_adapter: LLMAdapter) -> None:
        self.trna = TransferRNA()
        self.rrna = RibosomalRNA()
        self.subunit_30s = Subunit30S()
        self.subunit_50s = Subunit50S(llm_adapter=llm_adapter)
        self.active_directives: dict[str, float | str | bool] = {}

    def translate_directives(self, mrna: MessengerRNA) -> dict[str, float | str | bool]:
        self.active_directives = mrna.get_merged_directives()
        return self.active_directives

    def synthesize_order(
        self,
        request: CustomerRequest,
        seed_template: SeedTemplate,
        day: int,
        available_atp: float,
        target_cost_eur: float,
        quality_boost: float,
        from_cache: bool,
        active_gene_ids: list[str],
        generate_full_payload: bool = True,
    ) -> tuple[ProductArtifact | None, float]:
        decoded = self.subunit_30s.decode(
            request=request,
            trna=self.trna,
            seed_template=seed_template,
            available_atp=available_atp,
            estimated_atp_needed=max(0.05, target_cost_eur),
        )
        if decoded is None:
            return None, 0.0
        artifact, _, cogs = self.subunit_50s.catalyze(
            decoded_bundle=decoded,
            rrna=self.rrna,
            day=day,
            target_cost_eur=target_cost_eur,
            quality_boost=quality_boost,
            from_cache=from_cache,
            active_gene_ids=active_gene_ids,
            generate_full_payload=generate_full_payload,
        )
        return artifact, cogs

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="ribosome_70s",
            name_de="70S-Ribosomen-Komplex",
            system_id="genetics",
            health=1.0,
            activity=0.80 if self.active_directives else 0.25,
            load=min(1.0, self.subunit_50s.synthesized_count / 500.0),
            efficiency=self.rrna.fidelity_level,
            state_label_de=f"{len(self.active_directives)} aktive Gen-Direktiven",
            metrics={
                "active_directives_count": len(self.active_directives),
                "synthesized_total": self.subunit_50s.synthesized_count,
                "decoder_rejections": self.subunit_30s.rejected_budget,
            },
        )
