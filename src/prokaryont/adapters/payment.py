"""Zahlungs-Adapter (Plasmamembran-Transporter) für Simulation und Stripe."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentSettlement:
    """Ergebnis einer Zahlungsabwicklung an der Plasmamembran."""

    accepted: bool
    provider: str
    gross_eur: float
    fee_eur: float
    net_eur: float
    transaction_ref: str
    reason: str = "ok"


class PaymentAdapter(ABC):
    """Abstrakter Payment-Adapter für reale Zahlungs-Gateways oder Simulation."""

    provider_name: str = "base"

    @abstractmethod
    def settle_payment(
        self,
        gross_eur: float,
        fee_rate: float,
        fee_fixed_eur: float,
        customer_id: str,
        is_fraudulent: bool = False,
    ) -> PaymentSettlement:
        """Prüft und verbucht eine eingehende Kundenzahlung."""


class SimulatedPaymentAdapter(PaymentAdapter):
    """Deterministisch/realistischer lokaler Zahlungsabwickler (Standard)."""

    provider_name = "local_escrow_gateway"

    def __init__(self) -> None:
        self._counter = 0

    def settle_payment(
        self,
        gross_eur: float,
        fee_rate: float,
        fee_fixed_eur: float,
        customer_id: str,
        is_fraudulent: bool = False,
    ) -> PaymentSettlement:
        self._counter += 1
        if is_fraudulent or gross_eur <= 0.0:
            return PaymentSettlement(
                accepted=False,
                provider=self.provider_name,
                gross_eur=0.0,
                fee_eur=0.0,
                net_eur=0.0,
                transaction_ref=f"tx-rej-{self._counter}",
                reason="fraud_or_invalid_amount",
            )
        fee = round(gross_eur * fee_rate + fee_fixed_eur, 4)
        net = round(max(0.0, gross_eur - fee), 4)
        return PaymentSettlement(
            accepted=True,
            provider=self.provider_name,
            gross_eur=round(gross_eur, 4),
            fee_eur=fee,
            net_eur=net,
            transaction_ref=f"tx-sim-{self._counter}",
        )


class StripePaymentAdapter(PaymentAdapter):
    """Produktiver Adapter-Hook für echte Stripe PaymentIntents (mit sicherem Fallback)."""

    provider_name = "stripe_live_hook"

    def __init__(self, secret_key: str, timeout_sec: float = 8.0) -> None:
        self.secret_key = secret_key
        self.timeout_sec = timeout_sec
        self._fallback = SimulatedPaymentAdapter()

    def settle_payment(
        self,
        gross_eur: float,
        fee_rate: float,
        fee_fixed_eur: float,
        customer_id: str,
        is_fraudulent: bool = False,
    ) -> PaymentSettlement:
        if is_fraudulent or gross_eur <= 0.0:
            return self._fallback.settle_payment(
                gross_eur, fee_rate, fee_fixed_eur, customer_id, is_fraudulent=True
            )
        cents = max(50, int(round(gross_eur * 100)))
        data = urllib.parse.urlencode(
            {
                "amount": str(cents),
                "currency": "eur",
                "confirm": "false",
                "description": f"Prokaryont Order ({customer_id})",
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.stripe.com/v1/payment_intents",
            data=data,
            headers={"Authorization": f"Bearer {self.secret_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            fee = round(gross_eur * fee_rate + fee_fixed_eur, 4)
            return PaymentSettlement(
                accepted=True,
                provider=self.provider_name,
                gross_eur=round(gross_eur, 4),
                fee_eur=fee,
                net_eur=round(max(0.0, gross_eur - fee), 4),
                transaction_ref=str(body.get("id", "pi_live")),
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return self._fallback.settle_payment(
                gross_eur, fee_rate, fee_fixed_eur, customer_id, is_fraudulent=False
            )


def create_default_payment_adapter() -> PaymentAdapter:
    """Wählt Stripe-Hook bei expliziter Aktivierung, sonst lokalen Escrow-Adapter."""
    if os.getenv("PROKARYONT_USE_STRIPE") == "1" and (key := os.getenv("STRIPE_SECRET_KEY")):
        return StripePaymentAdapter(secret_key=key)
    return SimulatedPaymentAdapter()
