"""Doppelte Buchführung, dynamisches Pricing & Runway-Schutzschalter."""

from __future__ import annotations

from dataclasses import dataclass

from prokaryont.config import ScaleEconomicsProfile
from prokaryont.models import LedgerSnapshot, OrganelleTelemetry
from prokaryont.organelles.storage import PHBReserve, VolutinPool


@dataclass
class PricingEngine:
    """Optimiert den Produktpreis anhand Elastizität, Kapselstärke, Gasvesikeln & Zielmarge."""

    current_price_eur: float
    min_price_eur: float
    max_price_eur: float
    base_price_eur: float
    price_elasticity: float

    def compute_price(
        self,
        unit_cogs_est_eur: float,
        target_margin: float,
        operon_markup: float,
        capsule_premium: float,
        gas_buoyancy: float,
        competitor_pressure: float,
        plasmid_price_mult: float,
        fee_rate: float,
        fee_fixed_eur: float,
    ) -> float:
        # Mindestpreis zur Wahrung der angestrebten Stückmarge nach Payment-Fees
        effective_margin = min(0.84, max(0.35, target_margin))
        cost_floor = (unit_cogs_est_eur + fee_fixed_eur) / max(
            0.18, 1.0 - effective_margin - fee_rate
        )
        # Marktpreis unter Einfluss von Marken-Kapsel, Auftrieb ins Premium-Segment & Wettbewerb
        buoyancy_factor = 0.94 + gas_buoyancy * 0.22
        comp_drag = max(0.78, 1.0 - competitor_pressure * 0.28 * (1.0 - (capsule_premium - 1.0)))
        value_price = (
            self.base_price_eur
            * operon_markup
            * capsule_premium
            * buoyancy_factor
            * comp_drag
            * plasmid_price_mult
        )
        blended = max(cost_floor, value_price)
        clamped = max(self.min_price_eur, min(self.max_price_eur, blended))
        # Sanfte Glättung gegen Preissprünge
        self.current_price_eur = round(self.current_price_eur * 0.55 + clamped * 0.45, 2)
        return self.current_price_eur

    def demand_elasticity_multiplier(self, market_ref_price: float) -> float:
        ratio = max(0.5, self.current_price_eur / max(0.05, market_ref_price))
        return round(max(0.45, min(1.55, ratio ** (-self.price_elasticity * 0.55))), 4)

    def to_telemetry(self) -> OrganelleTelemetry:
        ratio = self.current_price_eur / max(0.05, self.base_price_eur)
        return OrganelleTelemetry(
            id="pricing_engine",
            name_de="Pricing- & Elastizitäts-Engine",
            system_id="viability",
            health=1.0,
            activity=0.80,
            load=0.35,
            efficiency=round(ratio, 3),
            state_label_de=f"Preis {self.current_price_eur:.2f} € ({ratio*100:.0f} % Basis)",
            metrics={
                "current_price_eur": self.current_price_eur,
                "base_price_eur": self.base_price_eur,
                "price_index": round(ratio, 3),
            },
        )


class DoubleEntryLedger:
    """Doppelte Buchführung inkl. 25 % Steuer-Escrow, ATP-Kopplung & Reserve-Fluss."""

    def __init__(self, profile: ScaleEconomicsProfile) -> None:
        self.profile = profile
        self.cash_eur: float = round(profile.seed_capital_eur * 0.65, 2)
        self.tax_escrow_eur: float = 0.0
        self.cumulative_harvested_eur: float = 0.0
        self.cumulative_revenue_eur: float = 0.0
        self.cumulative_costs_eur: float = 0.0
        self.cumulative_net_profit_eur: float = 0.0
        self.last_snapshot: LedgerSnapshot | None = None

    def record_day(
        self,
        day: int,
        revenue_eur: float,
        cogs_eur: float,
        payment_fees_eur: float,
        fixed_infra_eur: float,
        marketing_eur: float,
        plasmid_spend_eur: float,
        penalties_eur: float,
        phb_reserve: PHBReserve,
        volutin_pool: VolutinPool,
        atp_balance: float,
        atp_generated_today: float,
        atp_consumed_today: float,
    ) -> LedgerSnapshot:
        total_operating_costs = round(
            cogs_eur
            + payment_fees_eur
            + fixed_infra_eur
            + marketing_eur
            + plasmid_spend_eur
            + penalties_eur,
            2,
        )
        operating_profit = revenue_eur - total_operating_costs
        tax_accrual = round(max(0.0, operating_profit * self.profile.tax_reserve_rate), 2)
        net_profit = round(operating_profit - tax_accrual, 2)

        self.tax_escrow_eur = round(self.tax_escrow_eur + tax_accrual, 2)
        self.cumulative_revenue_eur = round(self.cumulative_revenue_eur + revenue_eur, 2)
        self.cumulative_costs_eur = round(
            self.cumulative_costs_eur + total_operating_costs + tax_accrual, 2
        )
        self.cumulative_net_profit_eur = round(self.cumulative_net_profit_eur + net_profit, 2)

        if net_profit >= 0:
            # Sobald Liquidität für mind. 20 Tage Fixkosten reicht, fließt Hauptteil in PHB-Reserve
            target_working_cash = max(self.profile.seed_capital_eur * 0.5, fixed_infra_eur * 22.0)
            if self.cash_eur < target_working_cash:
                to_cash = round(net_profit * 0.65, 2)
                to_phb = round(net_profit - to_cash, 2)
            else:
                to_cash = round(net_profit * 0.25, 2)
                to_phb = round(net_profit - to_cash, 2)
            self.cash_eur = round(self.cash_eur + to_cash, 2)
            phb_reserve.deposit(to_phb)
        else:
            deficit = abs(net_profit)
            if self.cash_eur >= deficit:
                self.cash_eur = round(self.cash_eur - deficit, 2)
            else:
                remainder = deficit - self.cash_eur
                self.cash_eur = 0.0
                phb_reserve.withdraw(remainder)

        gross_margin_pct = (
            round(((revenue_eur - cogs_eur - payment_fees_eur) / revenue_eur) * 100.0, 2)
            if revenue_eur > 0
            else 0.0
        )
        net_margin_pct = (
            round((net_profit / revenue_eur) * 100.0, 2) if revenue_eur > 0 else 0.0
        )
        liquid_total = self.cash_eur + phb_reserve.balance_eur
        daily_burn = max(0.05, fixed_infra_eur + (marketing_eur if net_profit < 0 else 0.0))
        runway = round(min(999.0, liquid_total / daily_burn), 1)

        snap = LedgerSnapshot(
            day=day,
            cash_eur=self.cash_eur,
            phb_reserve_eur=phb_reserve.balance_eur,
            tax_escrow_eur=self.tax_escrow_eur,
            volutin_prepaid_eur=volutin_pool.prepaid_eur,
            cumulative_harvested_eur=self.cumulative_harvested_eur,
            daily_revenue_eur=round(revenue_eur, 2),
            daily_cogs_eur=round(cogs_eur, 2),
            daily_payment_fees_eur=round(payment_fees_eur, 2),
            daily_fixed_infra_eur=round(fixed_infra_eur, 2),
            daily_marketing_eur=round(marketing_eur, 2),
            daily_tax_accrual_eur=tax_accrual,
            daily_net_profit_eur=net_profit,
            cumulative_revenue_eur=self.cumulative_revenue_eur,
            cumulative_costs_eur=self.cumulative_costs_eur,
            cumulative_net_profit_eur=self.cumulative_net_profit_eur,
            gross_margin_pct=gross_margin_pct,
            net_margin_pct=net_margin_pct,
            runway_days=runway,
            atp_balance=round(atp_balance, 2),
            atp_generated_today=round(atp_generated_today, 2),
            atp_consumed_today=round(atp_consumed_today, 2),
        )
        self.last_snapshot = snap
        return snap

    def inject_fertilizer(self, amount_eur: float) -> None:
        self.cash_eur = round(self.cash_eur + max(0.0, amount_eur), 2)

    def register_harvest(self, amount_eur: float) -> None:
        self.cumulative_harvested_eur = round(self.cumulative_harvested_eur + amount_eur, 2)

    def to_telemetry(self) -> OrganelleTelemetry:
        snap = self.last_snapshot
        profit = snap.cumulative_net_profit_eur if snap else 0.0
        margin = snap.net_margin_pct if snap else 0.0
        return OrganelleTelemetry(
            id="double_entry_ledger",
            name_de="Doppelte Buchführung & Steuer-Escrow",
            system_id="viability",
            health=1.0 if (snap is None or snap.cash_eur + snap.phb_reserve_eur > 0) else 0.1,
            activity=0.85,
            load=0.35,
            efficiency=max(0.0, min(2.0, 1.0 + margin / 100.0)),
            state_label_de=f"Gewinn {profit:.2f} € · Nettomarge {margin:.1f} %",
            metrics={
                "cumulative_net_profit_eur": profit,
                "net_margin_pct": margin,
                "tax_escrow_eur": self.tax_escrow_eur,
            },
        )


@dataclass
class RunwayCircuitBreaker:
    """Runway-Schutzschalter: drosselt Burn oder triggert Endospore vor Insolvenz."""

    state: str = "gruen"
    conserving_active: bool = False
    endospore_recommended: bool = False
    runway_days: float = 120.0

    def evaluate(
        self,
        liquid_funds_eur: float,
        daily_fixed_burn_eur: float,
        recent_net_profit_eur: float,
        demand_ratio: float,
        dormancy_runway_trigger: float,
        dormancy_demand_trigger: float,
    ) -> tuple[bool, bool]:
        burn = max(0.05, daily_fixed_burn_eur + max(0.0, -recent_net_profit_eur * 0.4))
        self.runway_days = round(min(999.0, liquid_funds_eur / burn), 1)

        # Empfehle Endospore bei schwerer akuter Marktdürre ODER niedrigem Runway mit Verlust
        if (demand_ratio < dormancy_demand_trigger) or (
            self.runway_days < dormancy_runway_trigger and recent_net_profit_eur < 0.0
        ):
            self.state = "rot_endospore"
            self.conserving_active = True
            self.endospore_recommended = True
        elif self.runway_days < dormancy_runway_trigger * 1.8 or recent_net_profit_eur < 0.0:
            self.state = "gelb_sparen"
            self.conserving_active = True
            self.endospore_recommended = False
        else:
            self.state = "gruen"
            self.conserving_active = False
            self.endospore_recommended = False
        return self.conserving_active, self.endospore_recommended

    def to_telemetry(self) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="runway_breaker",
            name_de="Runway- & Insolvenz-Schutzschalter",
            system_id="viability",
            health=1.0 if self.state == "gruen" else (0.7 if self.state == "gelb_sparen" else 0.4),
            activity=0.90 if self.conserving_active else 0.35,
            load=0.25,
            efficiency=1.0,
            state_label_de=f"Status {self.state} · Runway {self.runway_days:.0f} Tage",
            metrics={
                "state": self.state,
                "runway_days": self.runway_days,
                "conserving_active": self.conserving_active,
            },
        )
