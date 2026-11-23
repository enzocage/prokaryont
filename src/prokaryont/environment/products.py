"""Konkrete Produkt-Generatoren für B2B-Briefings (Markdown) und Micro-API (JSON)."""

from __future__ import annotations

from prokaryont.config import SeedTemplate
from prokaryont.models import CustomerRequest, ProductArtifact


_TOPIC_BRIEFING_DETAILS: dict[str, dict[str, str]] = {
    "eu_ai_act": {
        "headline": "EU AI Act & Governance-Compliance Briefing",
        "risk": "Mittel-Hoch (Dokumentations- & Transparenzpflichten für Hochrisiko-Modelle)",
        "action": "Modellkarten im Encapsulin-Tresor versiegeln und Output-Audit-Log aktivieren.",
    },
    "market_intel": {
        "headline": "Wettbewerbs- & Preiselastizitäts-Intelligenz-Dossier",
        "risk": "Steigender Preisdruck durch Billig-Klone im Standard-Segment",
        "action": "Positionierung via Gasvesikel ins Premium-Segment anheben (+14 % Marge).",
    },
    "supply_chain": {
        "headline": "Lieferketten- & Compute-Resilienz-Analyse",
        "risk": "Latenz- und Token-Preisspitzen bei Monopol-Providern",
        "action": "Multi-Provider-Arbitrage & Volutin-Prepaid-Puffer auf 30 Tage ausbauen.",
    },
}


def synthesize_concrete_product(
    day: int,
    request: CustomerRequest,
    seed_template: SeedTemplate,
    cogs_eur: float,
    quality_score: float,
    from_cache: bool,
    synthesized_via: str,
    summary_line: str | None,
    causal_gene_ids: list[str],
) -> ProductArtifact:
    """Erzeugt ein echtes, im Frontend inspizierbares B2B-Briefing oder API-JSON-Produkt."""
    net_margin = (
        round(((request.offered_price_eur - cogs_eur) / request.offered_price_eur) * 100.0, 2)
        if request.offered_price_eur > 0
        else 0.0
    )

    if seed_template == SeedTemplate.B2B_BRIEFING:
        info = _TOPIC_BRIEFING_DETAILS.get(
            request.topic_key,
            {
                "headline": f"Strategisches B2B-Briefing: {request.topic_key}",
                "risk": "Volatile Marktnachfrage & Margenerosion",
                "action": "Fokus auf Nischen-Differenzierung und semantisches Caching.",
            },
        )
        lead_text = summary_line or (
            f"Automatisierte Verdichtung für Segment `{request.segment}` über Kanal `{request.channel}`."
        )
        markdown = (
            f"# {info['headline']}\n\n"
            f"- **Kunde / Kohorte:** `{request.customer_id}` ({request.segment.upper()})\n"
            f"- **Tag:** {day} | **Preis:** {request.offered_price_eur:.2f} € | "
            f"**COGS:** {cogs_eur:.2f} € | **Deckungsbeitrag:** {net_margin:.1f} %\n"
            f"- **Synthese-Pfad:** {'Glykogen-Cache (Hit)' if from_cache else synthesized_via} "
            f"| **Qualität (rRNA/SLA):** {quality_score * 100:.1f} %\n\n"
            f"## Kernaussage (Carboxysom-Konzentrat)\n"
            f"{lead_text}\n\n"
            f"| Kennzahl | Bewertung | Empfehlung |\n"
            f"| --- | --- | --- |\n"
            f"| Hauptrisiko | {info['risk']} | Sofortige Absicherung |\n"
            f"| Handlungsimpuls | Priorität Hoch | {info['action']} |\n"
            f"| Aktive Gene | {', '.join(causal_gene_ids[:4]) or 'Kern-Operons'} | Kausal verifiziert |\n"
        )
        return ProductArtifact(
            artifact_id=f"art-{day}-{request.request_id}",
            day=day,
            seed_template=seed_template,
            title=info["headline"],
            protocol="briefing_markdown",
            customer_segment=request.segment,
            topic_key=request.topic_key,
            revenue_eur=round(request.offered_price_eur, 2),
            cogs_eur=round(cogs_eur, 4),
            net_margin_pct=net_margin,
            quality_score=quality_score,
            from_cache=from_cache,
            synthesized_via=synthesized_via,
            content_markdown=markdown,
            causal_gene_ids=list(causal_gene_ids),
        )

    # MICRO_API Payload
    payload = {
        "api_version": "2026.1",
        "request_id": request.request_id,
        "topic": request.topic_key,
        "segment": request.segment,
        "day": day,
        "verification": {
            "status": "VALIDATED",
            "confidence_score": round(quality_score, 4),
            "pii_redacted_by_encapsulin": request.compliance_sensitive,
            "cache_hit": from_cache,
        },
        "enrichment": {
            "risk_band": "LOW" if not request.is_fraudulent else "ELEVATED",
            "recommended_action": "AUTO_APPROVE" if quality_score >= 0.85 else "MANUAL_REVIEW",
            "summary": summary_line or f"Validiertes Payload-Paket für {request.topic_key}",
        },
        "economics": {
            "price_eur": round(request.offered_price_eur, 4),
            "cogs_eur": round(cogs_eur, 4),
            "margin_pct": net_margin,
        },
        "causal_genes": list(causal_gene_ids),
    }
    return ProductArtifact(
        artifact_id=f"art-{day}-{request.request_id}",
        day=day,
        seed_template=seed_template,
        title=f"Micro-API Response: {request.topic_key}",
        protocol="rest_json_api",
        customer_segment=request.segment,
        topic_key=request.topic_key,
        revenue_eur=round(request.offered_price_eur, 2),
        cogs_eur=round(cogs_eur, 4),
        net_margin_pct=net_margin,
        quality_score=quality_score,
        from_cache=from_cache,
        synthesized_via=synthesized_via,
        content_json=payload,
        causal_gene_ids=list(causal_gene_ids),
    )
