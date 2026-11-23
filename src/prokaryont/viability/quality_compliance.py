"""Qualitäts-Gate, Compliance-Wächter & Kunden-Lebenszyklus (LTV/CAC)."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.models import OrganelleTelemetry
from prokaryont.organelles.metabolism import Metabolosomes


@dataclass
class QualityGate:
    """SLA-Prüfung vor Auslieferung — leitet fehlerhafte Outputs in Metabolosomes um."""

    min_sla_score: float = 0.80
    passed_today: int = 0
    retried_today: int = 0
    avg_quality: float = 0.93

    def inspect_and_ensure(
        self,
        quality_score: float,
        unit_cost_eur: float,
        metabolosomes: Metabolosomes,
        arbitrage_ratio: float,
        plasmid_discount: float,
    ) -> tuple[float, float]:
        if quality_score < self.min_sla_score:
            self.retried_today += 1
            new_cost, _ = metabolosomes.arbitrage_and_recover(
                unit_cost_eur=unit_cost_eur * 1.15,
                arbitrage_ratio=arbitrage_ratio,
                plasmid_discount=plasmid_discount,
                dirty_input=True,
            )
            repaired_score = min(0.95, quality_score + 0.14)
            self.passed_today += 1
            self.avg_quality = round(self.avg_quality * 0.8 + repaired_score * 0.2, 4)
            return repaired_score, new_cost

        self.passed_today += 1
        self.avg_quality = round(self.avg_quality * 0.85 + quality_score * 0.15, 4)
        return quality_score, unit_cost_eur

    def reset_daily(self) -> None:
        self.passed_today = 0
        self.retried_today = 0

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="quality_gate",
            name_de="SLA- & Qualitäts-Gate",
            system_id="viability",
            health=self.avg_quality,
            activity=min(1.0, self.passed_today / 40.0 + 0.2),
            load=min(1.0, self.retried_today / 8.0),
            efficiency=self.avg_quality,
            state_label_de=f"Qualität {self.avg_quality*100:.1f} % ({self.retried_today} Retries)",
            metrics={
                "avg_quality": self.avg_quality,
                "passed_today": self.passed_today,
                "retried_today": self.retried_today,
            },
        )


@dataclass
class ComplianceGuard:
    """Prüft Gärtner-Leitplanken und wehrt regulatorische Audit-Bußgelder ab."""

    readiness_score: float = 0.88
    audits_passed: int = 0
    penalties_today_eur: float = 0.0

    def handle_audit(
        self,
        audit_active: bool,
        audit_severity: float,
        audit_rigor: float,
        encapsulin_integrity: float,
        plasmid_audit_bonus: float,
        guardrail_strictness: float,
        revenue_base_eur: float,
    ) -> float:
        self.readiness_score = round(
            min(
                0.995,
                audit_rigor * 0.45
                + encapsulin_integrity * 0.30
                + guardrail_strictness * 0.20
                + plasmid_audit_bonus,
            ),
            4,
        )
        self.penalties_today_eur = 0.0
        if not audit_active:
            return 0.0

        if self.readiness_score >= audit_severity * 0.85:
            self.audits_passed += 1
            return 0.0

        gap = max(0.0, audit_severity - self.readiness_score)
        penalty = round(max(1.5, revenue_base_eur * 0.18 * gap), 2)
        self.penalties_today_eur = penalty
        return penalty

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="compliance_guard",
            name_de="Compliance- & Leitplanken-Wächter",
            system_id="viability",
            health=self.readiness_score,
            activity=0.75,
            load=0.25,
            efficiency=self.readiness_score,
            state_label_de=f"Audit-Readiness {self.readiness_score*100:.1f} % ({self.audits_passed} bestanden)",
            metrics={
                "readiness_score": self.readiness_score,
                "audits_passed": self.audits_passed,
                "penalties_today_eur": self.penalties_today_eur,
            },
        )


@dataclass
class CustomerLifecycleManager:
    """Verwaltet aktive Kundenkohorten, Retention, Zufriedenheit & LTV/CAC."""

    active_customers: int = 18
    satisfaction: float = 0.84
    retention_rate: float = 0.88
    ltv_cac_ratio: float = 5.4

    def update(
        self,
        fulfilled_orders: int,
        avg_quality: float,
        slime_stickiness: float,
        pili_retention_boost: float,
        marketing_spend_eur: float,
        avg_price_eur: float,
        dormant: bool,
    ) -> float:
        if dormant:
            # Im Schlaf bleiben Stammkunden über Protoplast-Index großteils erhalten
            self.active_customers = max(6, int(round(self.active_customers * 0.992)))
            return 1.0

        self.satisfaction = round(
            min(0.99, max(0.45, self.satisfaction * 0.72 + avg_quality * 0.28)), 4
        )
        self.retention_rate = round(
            min(0.97, max(0.58, 0.68 + slime_stickiness * 0.22 + pili_retention_boost * 0.40)),
            4,
        )
        retained = int(round(self.active_customers * (0.94 + (self.retention_rate - 0.85) * 0.2)))
        new_added = max(0, int(round(fulfilled_orders * 0.14)))
        self.active_customers = max(8, min(5000, int(round(retained * 0.88 + self.active_customers * 0.12 + new_added))))

        monthly_arpu = max(avg_price_eur, avg_price_eur * 2.2)
        ltv = monthly_arpu / max(0.04, 1.0 - self.retention_rate)
        cac = max(1.5, marketing_spend_eur / max(1, new_added)) if marketing_spend_eur > 0 else 3.0
        self.ltv_cac_ratio = round(min(24.0, max(1.2, ltv / cac)), 2)

        # Organischer Stammkunden-Multiplikator für zukünftige Nachfrage
        return round(min(1.85, 0.88 + (self.active_customers / 85.0) * 0.45 + (self.satisfaction - 0.75) * 0.4), 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="customer_lifecycle",
            name_de="Kunden-Kohorten & LTV/CAC",
            system_id="viability",
            health=self.satisfaction,
            activity=min(1.0, self.active_customers / 80.0),
            load=0.35,
            efficiency=min(2.0, self.ltv_cac_ratio / 4.0),
            state_label_de=f"{self.active_customers} Kunden · LTV/CAC {self.ltv_cac_ratio:.1f}x",
            metrics={
                "active_customers": self.active_customers,
                "satisfaction": self.satisfaction,
                "retention_rate": self.retention_rate,
                "ltv_cac_ratio": self.ltv_cac_ratio,
            },
        )
