"""Zellhülle, Firewall, Periplasma, Zahlungsgrenze & Glykokalyx-Bindung."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.adapters.payment import PaymentAdapter, PaymentSettlement
from prokaryont.models import CustomerRequest, OrganelleTelemetry


@dataclass
class SLayer:
    """Kristalline WAF-Außenpanzerung gegen Bot-Stürme und Rate-Limit-Verstöße."""

    strictness: float = 0.78
    blocked_attacks_total: int = 0
    blocked_today: int = 0
    passed_today: int = 0

    def filter_traffic(
        self,
        requests: list[CustomerRequest],
        strictness_override: float,
        firewall_bonus: float,
    ) -> list[CustomerRequest]:
        self.strictness = min(0.99, max(0.35, strictness_override + firewall_bonus))
        self.blocked_today = 0
        self.passed_today = 0
        survivors: list[CustomerRequest] = []
        for req in requests:
            if req.is_malicious:
                # S-Layer fängt den Großteil reiner Bot-/DDoS-Angriffe sofort kostenlos ab
                if req.complexity <= self.strictness + 0.08:
                    self.blocked_today += 1
                    self.blocked_attacks_total += 1
                    continue
            self.passed_today += 1
            survivors.append(req)
        return survivors

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="s_layer",
            name_de="S-Layer (Edge-WAF)",
            system_id="envelope",
            health=1.0,
            activity=min(1.0, (self.passed_today + self.blocked_today) / 80.0),
            load=min(1.0, self.blocked_today / 25.0),
            efficiency=self.strictness,
            state_label_de=f"{self.blocked_today} Angriffe heute gestoppt",
            metrics={
                "strictness": round(self.strictness, 3),
                "blocked_today": self.blocked_today,
                "blocked_total": self.blocked_attacks_total,
            },
        )


@dataclass
class LipopolysaccharideGuard:
    """LPS-Endotoxin-Signaturprüfung: erkennt Fraud-, Chargeback- & Injection-Payloads."""

    sensitivity: float = 0.82
    fraud_blocked_today: int = 0
    fraud_blocked_total: int = 0

    def inspect(
        self,
        req: CustomerRequest,
        lps_threshold: float,
        fraud_block_bonus: float,
    ) -> bool:
        effective = min(0.99, lps_threshold + fraud_block_bonus)
        self.sensitivity = effective
        if req.is_fraudulent or req.is_malicious:
            if effective >= 0.72 or req.complexity < effective:
                self.fraud_blocked_today += 1
                self.fraud_blocked_total += 1
                return False
        return True

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="lipopolysaccharides",
            name_de="Lipopolysaccharide (LPS-Fraud-Guard)",
            system_id="envelope",
            health=1.0,
            activity=min(1.0, self.fraud_blocked_today / 10.0 + 0.2),
            load=min(1.0, self.fraud_blocked_today / 15.0),
            efficiency=self.sensitivity,
            state_label_de=f"{self.fraud_blocked_today} Fraud-Versuche blockiert",
            metrics={
                "sensitivity": round(self.sensitivity, 3),
                "fraud_blocked_today": self.fraud_blocked_today,
                "fraud_blocked_total": self.fraud_blocked_total,
            },
        )


class OuterMembrane:
    """Public Edge / DMZ zwischen Außenwelt und Periplasma (enthält LPS-Guard)."""

    def __init__(self) -> None:
        self.lps_guard = LipopolysaccharideGuard()
        self.inspected_today: int = 0
        self.rejected_today: int = 0

    def screen_requests(
        self,
        requests: list[CustomerRequest],
        lps_threshold: float,
        fraud_block_bonus: float,
    ) -> list[CustomerRequest]:
        self.inspected_today = len(requests)
        self.lps_guard.fraud_blocked_today = 0
        passed: list[CustomerRequest] = []
        for req in requests:
            if self.lps_guard.inspect(req, lps_threshold, fraud_block_bonus):
                passed.append(req)
        self.rejected_today = self.inspected_today - len(passed)
        return passed

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="outer_membrane",
            name_de="Äußere Membran (DMZ)",
            system_id="envelope",
            health=1.0,
            activity=min(1.0, self.inspected_today / 80.0),
            load=min(1.0, self.rejected_today / 20.0),
            efficiency=round(
                (self.inspected_today - self.rejected_today) / max(1, self.inspected_today),
                3,
            ),
            state_label_de=f"{self.inspected_today} geprüft · {self.rejected_today} abgewiesen",
            metrics={
                "inspected_today": self.inspected_today,
                "rejected_today": self.rejected_today,
            },
        )


@dataclass
class PorinChannel:
    """Selektive Eingangs-Kanäle mit dynamischer Apertur je nach ATP & Überlast."""

    aperture: float = 1.0
    admitted_today: int = 0
    throttled_today: int = 0

    def admit(
        self,
        requests: list[CustomerRequest],
        max_capacity: int,
        atp_balance: float,
        throttle_floor: float,
    ) -> list[CustomerRequest]:
        if atp_balance < 4.0:
            self.aperture = max(throttle_floor, 0.45)
        elif atp_balance < 12.0:
            self.aperture = max(throttle_floor, 0.78)
        else:
            self.aperture = 1.0

        allowed_cap = max(1, int(round(max_capacity * self.aperture)))
        if len(requests) <= allowed_cap:
            self.admitted_today = len(requests)
            self.throttled_today = 0
            return requests

        # Priorisiere Premium & Standard vor Nische/Low-Price
        ranked = sorted(requests, key=lambda r: r.offered_price_eur, reverse=True)
        admitted = ranked[:allowed_cap]
        self.admitted_today = len(admitted)
        self.throttled_today = len(requests) - len(admitted)
        return admitted

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="porins",
            name_de="Porine (API-Kanäle)",
            system_id="envelope",
            health=1.0,
            activity=self.aperture,
            load=min(1.0, self.throttled_today / 25.0),
            efficiency=self.aperture,
            state_label_de=f"Apertur {self.aperture * 100:.0f} % · {self.admitted_today} durchgelassen",
            metrics={
                "aperture": round(self.aperture, 2),
                "admitted_today": self.admitted_today,
                "throttled_today": self.throttled_today,
            },
        )


@dataclass
class Periplasm:
    """Pre-Processing-, KYC- & Profitabilitäts-Vorfilter vor dem Compute-Verbrauch."""

    accepted_today: int = 0
    filtered_unprofitable_today: int = 0

    def preprocess(
        self,
        requests: list[CustomerRequest],
        estimated_unit_cogs: float,
        min_margin_ratio: float,
    ) -> list[CustomerRequest]:
        self.accepted_today = 0
        self.filtered_unprofitable_today = 0
        viable: list[CustomerRequest] = []
        for req in requests:
            # Lehnt Anfragen ab, deren Preis nicht einmal Variable Kosten + Mindestmarge deckt
            floor_price = estimated_unit_cogs / max(0.15, (1.0 - min_margin_ratio))
            if req.offered_price_eur < floor_price * 0.65:
                self.filtered_unprofitable_today += 1
                continue
            self.accepted_today += 1
            viable.append(req)
        return viable

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="periplasm",
            name_de="Periplasma (KYC & Vorfilter)",
            system_id="envelope",
            health=1.0,
            activity=min(1.0, self.accepted_today / 60.0),
            load=0.35,
            efficiency=1.0,
            state_label_de=f"{self.accepted_today} valide · {self.filtered_unprofitable_today} unrentabel",
            metrics={
                "accepted_today": self.accepted_today,
                "filtered_unprofitable_today": self.filtered_unprofitable_today,
            },
        )


@dataclass
class PeptidoglycanLayer:
    """Quervernetzte Policy- & Leitplanken-Matrix (inkl. gemergter Pseudopeptidoglykan-Rolle)."""

    integrity: float = 1.0
    policies_enforced_today: int = 0
    tax_escrow_rate: float = 0.25

    def verify_crosslinks(
        self,
        guardrail_strictness: float,
        available_cash: float,
        planned_spend: float,
    ) -> float:
        """Begrenzt Ausgaben hart gegen Liquidität und Gärtner-Leitplanken."""
        self.policies_enforced_today += 1
        max_allowed = available_cash * max(0.15, 0.72 - guardrail_strictness * 0.25)
        approved = min(planned_spend, max(0.0, max_allowed))
        self.integrity = 1.0 if available_cash > 0 else 0.4
        return round(approved, 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="peptidoglycan",
            name_de="Peptidoglykan-Schicht (Policy-Matrix)",
            system_id="envelope",
            health=self.integrity,
            activity=0.75,
            load=0.30,
            efficiency=self.integrity,
            state_label_de=f"Integrität {self.integrity * 100:.0f} % · Steuer-Escrow {self.tax_escrow_rate*100:.0f} %",
            metrics={
                "integrity": self.integrity,
                "policies_enforced_today": self.policies_enforced_today,
                "tax_escrow_rate": self.tax_escrow_rate,
            },
        )


class CellWall:
    """Zellwand gegen finanzielle Lyse (Überschuldung / Kapazitätssprengung)."""

    def __init__(self) -> None:
        self.peptidoglycan = PeptidoglycanLayer()
        self.osmotic_pressure: float = 0.25
        self.lysis_prevented_count: int = 0

    def protect_against_lysis(
        self,
        requests_count: int,
        max_capacity: int,
        cash_eur: float,
        daily_fixed_burn: float,
    ) -> float:
        self.osmotic_pressure = round(
            min(1.0, (requests_count / max(1, max_capacity)) * 0.6 + (daily_fixed_burn / max(1.0, cash_eur)) * 0.8),
            3,
        )
        if requests_count > max_capacity:
            self.lysis_prevented_count += 1
        return self.osmotic_pressure

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="cell_wall",
            name_de="Zellwand (Budget-Strukturgrenze)",
            system_id="envelope",
            health=round(max(0.2, 1.0 - self.osmotic_pressure * 0.35), 3),
            activity=0.80,
            load=self.osmotic_pressure,
            efficiency=1.0,
            state_label_de=f"Osmotischer Druck {self.osmotic_pressure * 100:.0f} %",
            metrics={
                "osmotic_pressure": self.osmotic_pressure,
                "lysis_prevented_count": self.lysis_prevented_count,
            },
        )


class PlasmaMembrane:
    """Plasmamembran: prüft echte Kundenzahlungen und koppelt sie ans Zellinnere."""

    def __init__(self, payment_adapter: PaymentAdapter) -> None:
        self.payment_adapter = payment_adapter
        self.settled_today: int = 0
        self.rejected_today: int = 0
        self.gross_today_eur: float = 0.0
        self.fees_today_eur: float = 0.0

    def settle_orders(
        self,
        requests: list[CustomerRequest],
        fee_rate: float,
        fee_fixed_eur: float,
    ) -> list[tuple[CustomerRequest, PaymentSettlement]]:
        self.settled_today = 0
        self.rejected_today = 0
        self.gross_today_eur = 0.0
        self.fees_today_eur = 0.0
        paid: list[tuple[CustomerRequest, PaymentSettlement]] = []
        for req in requests:
            settlement = self.payment_adapter.settle_payment(
                gross_eur=req.offered_price_eur,
                fee_rate=fee_rate,
                fee_fixed_eur=fee_fixed_eur,
                customer_id=req.customer_id,
                is_fraudulent=req.is_fraudulent,
            )
            if settlement.accepted:
                self.settled_today += 1
                self.gross_today_eur += settlement.gross_eur
                self.fees_today_eur += settlement.fee_eur
                paid.append((req, settlement))
            else:
                self.rejected_today += 1
        return paid

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="plasma_membrane",
            name_de="Plasmamembran (Payment-Transporter)",
            system_id="envelope",
            health=1.0,
            activity=min(1.0, self.settled_today / 50.0),
            load=0.45,
            efficiency=round(
                1.0 - (self.fees_today_eur / max(0.01, self.gross_today_eur)), 4
            )
            if self.gross_today_eur > 0
            else 0.97,
            state_label_de=f"{self.settled_today} bezahlt · {self.gross_today_eur:.2f} €",
            metrics={
                "settled_today": self.settled_today,
                "rejected_today": self.rejected_today,
                "gross_today_eur": round(self.gross_today_eur, 2),
                "fees_today_eur": round(self.fees_today_eur, 2),
                "payment_provider": self.payment_adapter.provider_name,
            },
        )


@dataclass
class Capsule:
    """Markenreputation & SLA-Vertrauenssiegel — schützt Preissetzungsmacht."""

    strength: float = 0.56

    def update(self, avg_quality: float, trust_bonus: float, fulfillment_ratio: float) -> float:
        target = min(0.98, max(0.25, avg_quality * 0.65 + fulfillment_ratio * 0.30 + trust_bonus))
        self.strength = round(self.strength * 0.85 + target * 0.15, 4)
        return self.strength

    def price_premium_multiplier(self) -> float:
        return round(1.0 + max(0.0, self.strength - 0.45) * 0.42, 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="capsule",
            name_de="Kapsel (Marke & SLA-Siegel)",
            system_id="envelope",
            health=self.strength,
            activity=self.strength,
            load=0.25,
            efficiency=self.price_premium_multiplier(),
            state_label_de=f"Markenstärke {self.strength * 100:.0f} % (+{(self.price_premium_multiplier()-1)*100:.0f} % Preis)",
            metrics={
                "strength": self.strength,
                "price_premium_multiplier": self.price_premium_multiplier(),
            },
        )


@dataclass
class SlimeLayer:
    """Schleimschicht: Kunden-Kontext-Stickiness & Wiederkaufrate."""

    stickiness: float = 0.52

    def update(self, satisfaction: float, pili_focus: float) -> float:
        target = min(0.96, max(0.20, satisfaction * 0.7 + pili_focus * 0.3))
        self.stickiness = round(self.stickiness * 0.82 + target * 0.18, 4)
        return self.stickiness

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="slime_layer",
            name_de="Schleimschicht (Kunden-Stickiness)",
            system_id="envelope",
            health=self.stickiness,
            activity=self.stickiness,
            load=0.20,
            efficiency=self.stickiness,
            state_label_de=f"Kontext-Haftung {self.stickiness * 100:.0f} %",
            metrics={"stickiness": self.stickiness},
        )


class Glycocalyx:
    """Glykokalyx: Kombination aus Kapsel (Marke) & Schleimschicht (Bindung)."""

    def __init__(self) -> None:
        self.capsule = Capsule()
        self.slime_layer = SlimeLayer()

    def total_protection_index(self) -> float:
        return round((self.capsule.strength * 0.55 + self.slime_layer.stickiness * 0.45), 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        idx = self.total_protection_index()
        return OrganelleTelemetry(
            id="glycocalyx",
            name_de="Glykokalyx (Marken-Ökosystem)",
            system_id="envelope",
            health=idx,
            activity=idx,
            load=0.22,
            efficiency=round(1.0 + idx * 0.35, 3),
            state_label_de=f"Schutz- & Bindungsindex {idx * 100:.0f} %",
            metrics={
                "protection_index": idx,
                "capsule_strength": self.capsule.strength,
                "slime_stickiness": self.slime_layer.stickiness,
            },
        )
