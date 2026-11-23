"""Nukleoid, Bakterienchromosom (Operon-AST) und Fitness-selektierte Mutation."""

from __future__ import annotations

import ast
import copy
import operator
import random
from dataclasses import dataclass, field
from typing import Any

from prokaryont.models import MutationRecord, OperonSpec, OrganelleTelemetry


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_CMP_OPS = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}


class PromoterEvaluator:
    """Sicherer AST-Interpreter für Operon-Promoter-Bedingungen ohne eval()."""

    @classmethod
    def evaluate(cls, expr: str, context: dict[str, float | bool]) -> bool:
        stripped = expr.strip()
        if stripped.lower() in ("always", "true"):
            return True
        if stripped.lower() in ("never", "false"):
            return False
        tree = ast.parse(stripped, mode="eval")
        result = cls._eval_node(tree.body, context)
        return bool(result)

    @classmethod
    def _eval_node(cls, node: ast.AST, context: dict[str, float | bool]) -> Any:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, bool)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise KeyError(f"Unbekannte Promotor-Variable: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not bool(cls._eval_node(node.operand, context))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -float(cls._eval_node(node.operand, context))
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(bool(cls._eval_node(v, context)) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(bool(cls._eval_node(v, context)) for v in node.values)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left = float(cls._eval_node(node.left, context))
            right = float(cls._eval_node(node.right, context))
            return _BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.Compare):
            left = cls._eval_node(node.left, context)
            for op_node, comparator in zip(node.ops, node.comparators):
                if type(op_node) not in _CMP_OPS:
                    raise ValueError(f"Nicht unterstützter Vergleichsoperator: {type(op_node)}")
                right = cls._eval_node(comparator, context)
                if not _CMP_OPS[type(op_node)](left, right):
                    return False
                left = right
            return True
        raise ValueError(f"Nicht erlaubter AST-Knoten im Promotor: {type(node).__name__}")


def build_default_operons() -> dict[str, OperonSpec]:
    """Erzeugt die 7 Kern-Operons des wirtschaftlichen Bakterienchromosoms."""
    specs = [
        OperonSpec(
            operon_id="OP_PRICING_HOMEOSTASIS",
            name_de="Preis- & Margen-Homöostase-Operon",
            category="pricing",
            promoter_expression="always",
            parameters={
                "target_markup": 1.04,
                "elasticity_sensitivity": 0.42,
                "premium_bias": 0.25,
            },
            min_bounds={"target_markup": 0.85, "elasticity_sensitivity": 0.15, "premium_bias": 0.0},
            max_bounds={"target_markup": 1.38, "elasticity_sensitivity": 0.85, "premium_bias": 0.75},
            description_de=(
                "Steuert dynamisch Verkaufspreise und Segment-Auftrieb (Gasvesikel), "
                "um Zielmarge gegen Preiskriege und Elastizität zu stabilisieren."
            ),
        ),
        OperonSpec(
            operon_id="OP_METABOLIC_EFFICIENCY",
            name_de="Stoffwechsel- & Cache-Effizienz-Operon",
            category="metabolism",
            promoter_expression="always",
            parameters={
                "cache_aggressiveness": 0.72,
                "arbitrage_routing": 0.48,
                "volutin_hedge_ratio": 0.18,
            },
            min_bounds={"cache_aggressiveness": 0.25, "arbitrage_routing": 0.10, "volutin_hedge_ratio": 0.05},
            max_bounds={"cache_aggressiveness": 0.92, "arbitrage_routing": 0.85, "volutin_hedge_ratio": 0.45},
            description_de=(
                "Aktiviert Glykogen-Caching, Metabolosomen-Kostenarbitrage und "
                "Volutin-Vorauszahlung gegen Compute-Preisschocks."
            ),
        ),
        OperonSpec(
            operon_id="OP_CHEMOTAXIS_GROWTH",
            name_de="Chemotaxis- & Wachstums-Operon",
            category="motility",
            promoter_expression="runway_days > 22 and not dormant",
            parameters={
                "marketing_atp_share": 0.34,
                "fimbriae_hook_intensity": 0.62,
                "pili_retention_focus": 0.68,
            },
            min_bounds={"marketing_atp_share": 0.08, "fimbriae_hook_intensity": 0.20, "pili_retention_focus": 0.25},
            max_bounds={"marketing_atp_share": 0.60, "fimbriae_hook_intensity": 0.95, "pili_retention_focus": 0.95},
            description_de=(
                "Lenkt Flagellen-Chemotaxis, Fimbrien-Lead-Hooks und Pili-B2B-Bindung, "
                "sobald ausreichend Sicherheits-Runway besteht."
            ),
        ),
        OperonSpec(
            operon_id="OP_IMMUNE_DEFENSE",
            name_de="Hüllen- & Immun-Abwehr-Operon",
            category="defense",
            promoter_expression="threat_level > 0.12 or fraud_share > 0.06",
            parameters={
                "s_layer_strictness": 0.78,
                "lps_fraud_threshold": 0.80,
                "porin_throttle_floor": 0.52,
            },
            min_bounds={"s_layer_strictness": 0.40, "lps_fraud_threshold": 0.45, "porin_throttle_floor": 0.25},
            max_bounds={"s_layer_strictness": 0.98, "lps_fraud_threshold": 0.99, "porin_throttle_floor": 0.90},
            description_de=(
                "Fährt bei Bot-Wellen oder Chargeback-Signalen sofort S-Layer-WAF, "
                "LPS-Signaturprüfung und Porin-Drosselung hoch."
            ),
        ),
        OperonSpec(
            operon_id="OP_COMPLIANCE_SHIELD",
            name_de="Compliance- & Encapsulin-Schutz-Operon",
            category="compliance",
            promoter_expression="audit_active or guardrail_strictness > 0.5",
            parameters={
                "audit_rigor": 0.84,
                "pii_redaction_level": 0.90,
                "escrow_buffer_factor": 1.05,
            },
            min_bounds={"audit_rigor": 0.50, "pii_redaction_level": 0.60, "escrow_buffer_factor": 1.00},
            max_bounds={"audit_rigor": 0.99, "pii_redaction_level": 0.99, "escrow_buffer_factor": 1.25},
            description_de=(
                "Aktiviert Encapsulin-Tresore, Steuer-Escrow und prüffähige DSGVO/AI-Act-Antworten."
            ),
        ),
        OperonSpec(
            operon_id="OP_CRISIS_SPORULATION",
            name_de="Endosporen-Überlebens-Operon",
            category="dormancy",
            promoter_expression="runway_days < 20 or demand_ratio < 0.36",
            parameters={
                "dormancy_runway_trigger": 18.0,
                "dormancy_demand_trigger": 0.34,
                "germination_demand_trigger": 0.62,
            },
            min_bounds={
                "dormancy_runway_trigger": 10.0,
                "dormancy_demand_trigger": 0.20,
                "germination_demand_trigger": 0.48,
            },
            max_bounds={
                "dormancy_runway_trigger": 32.0,
                "dormancy_demand_trigger": 0.45,
                "germination_demand_trigger": 0.85,
            },
            description_de=(
                "Schützt das Leben des Organismus in schweren Dürren durch Kortex-Kostenkompression "
                "und überwacht Exosporium-Keimung."
            ),
        ),
        OperonSpec(
            operon_id="OP_FTSZ_HARVEST",
            name_de="FtsZ-Ernte- & Spin-Off-Operon",
            category="harvest",
            promoter_expression="phb_reserve > harvest_threshold and not dormant",
            parameters={
                "harvest_aggression": 1.0,
                "reinvest_reserve_share": 0.35,
            },
            min_bounds={"harvest_aggression": 0.50, "reinvest_reserve_share": 0.15},
            max_bounds={"harvest_aggression": 1.25, "reinvest_reserve_share": 0.65},
            description_de=(
                "Löst bei gesättigter PHB-Reserve die FtsZ-Ring-Kontraktion aus und liefert "
                "Spin-Off-Gewinne an den Gärtner."
            ),
        ),
    ]
    return {s.operon_id: s for s in specs}


class Nucleoid:
    """Nukleoid: Geschützte Genom-Region mit Snapshots, Rollback und Leitplanken."""

    def __init__(self) -> None:
        self.snapshots: list[dict[str, dict[str, float]]] = []
        self.rollbacks_triggered: int = 0
        self.guardrail_clamps: int = 0

    def save_snapshot(self, operons: dict[str, OperonSpec]) -> None:
        state = {op_id: dict(op.parameters) for op_id, op in operons.items()}
        self.snapshots.append(state)
        if len(self.snapshots) > 30:
            self.snapshots.pop(0)

    def restore_last_snapshot(self, operons: dict[str, OperonSpec]) -> bool:
        if not self.snapshots:
            return False
        prev = self.snapshots[-1]
        for op_id, params in prev.items():
            if op_id in operons:
                operons[op_id].parameters = dict(params)
        self.rollbacks_triggered += 1
        return True

    def enforce_bounds(
        self,
        operon: OperonSpec,
        param: str,
        value: float,
        guardrail_strictness: float,
    ) -> float:
        lo = operon.min_bounds.get(param, value)
        hi = operon.max_bounds.get(param, value)
        # Bei strikteren Gärtner-Leitplanken wird der Spielraum verengt
        if guardrail_strictness > 0.6 and lo < hi:
            span = hi - lo
            shrink = (guardrail_strictness - 0.6) * 0.25 * span
            lo = lo + shrink * 0.5
            hi = hi - shrink * 0.5
        clamped = max(lo, min(hi, float(value)))
        if abs(clamped - value) > 1e-6:
            self.guardrail_clamps += 1
        return round(clamped, 4)

    def to_telemetry(self, genome_version: int) -> OrganelleTelemetry:
        return OrganelleTelemetry(
            id="nucleoid",
            name_de="Nukleoid (Genom-Vault)",
            system_id="genetics",
            health=1.0,
            activity=0.65,
            load=min(1.0, len(self.snapshots) / 30.0),
            efficiency=1.0,
            state_label_de=f"Genom v{genome_version} · {self.rollbacks_triggered} Rollbacks",
            metrics={
                "snapshots_stored": len(self.snapshots),
                "rollbacks_triggered": self.rollbacks_triggered,
                "guardrail_clamps": self.guardrail_clamps,
            },
        )


@dataclass
class PendingTrial:
    """Laufender Fitness-Vergleich für eine kürzlich durchgeführte Parameter-Mutation."""

    day_started: int
    operon_id: str
    parameter: str
    old_value: float
    new_value: float
    fitness_before: float
    fitness_samples: list[float] = field(default_factory=list)


class BacterialChromosome:
    """Ausführbares Operon-Chromosom: prüft Promotoren & steuert Anpassung."""

    def __init__(self, operons: dict[str, OperonSpec] | None = None) -> None:
        self.operons: dict[str, OperonSpec] = operons or build_default_operons()
        self.genome_version: int = 1
        self.total_transcriptions: int = 0

    def evaluate_promoters(self, context: dict[str, float | bool]) -> list[OperonSpec]:
        """Wertet alle Promotoren aus und gibt die aktiven Operons zurück."""
        active: list[OperonSpec] = []
        for operon in self.operons.values():
            is_active = PromoterEvaluator.evaluate(operon.promoter_expression, context)
            operon.promoter_active = is_active
            if is_active:
                operon.activation_count += 1
                active.append(operon)
        self.total_transcriptions += len(active)
        return active

    def get_param(self, operon_id: str, param: str, default: float = 0.0) -> float:
        op = self.operons.get(operon_id)
        if not op:
            return default
        return float(op.parameters.get(param, default))

    def export_genes(self) -> dict[str, dict[str, float]]:
        return {op_id: copy.deepcopy(op.parameters) for op_id, op in self.operons.items()}

    def import_genes(
        self,
        gene_map: dict[str, dict[str, float]],
        nucleoid: Nucleoid,
        guardrail_strictness: float,
    ) -> None:
        for op_id, params in gene_map.items():
            if op_id in self.operons:
                op = self.operons[op_id]
                for k, v in params.items():
                    if k in op.parameters:
                        op.parameters[k] = nucleoid.enforce_bounds(
                            op, k, float(v), guardrail_strictness
                        )
        self.genome_version += 1

    def to_telemetry(self) -> OrganelleTelemetry:
        active_count = sum(1 for op in self.operons.values() if op.promoter_active)
        return OrganelleTelemetry(
            id="bacterial_chromosome",
            name_de="Bakterienchromosom (Operons)",
            system_id="genetics",
            health=1.0,
            activity=round(active_count / max(1, len(self.operons)), 2),
            load=round(active_count / max(1, len(self.operons)), 2),
            efficiency=1.0,
            state_label_de=f"{active_count}/{len(self.operons)} Operons aktiv",
            metrics={
                "genome_version": self.genome_version,
                "active_operons": active_count,
                "total_transcriptions": self.total_transcriptions,
            },
        )


class MutationEngine:
    """Adaptive Fitness-gesteuerte Mutation mit Shadow-Test & automatischem Rollback."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.records: list[MutationRecord] = []
        self.pending: PendingTrial | None = None
        self.last_mutation_day: int = 0

    def step(
        self,
        day: int,
        fitness: float,
        chromosome: BacterialChromosome,
        nucleoid: Nucleoid,
        guardrail_strictness: float,
        dormant: bool,
    ) -> MutationRecord | None:
        if dormant:
            return None

        # Laufende Trial-Mutation nach 5 Tagen auswerten
        if self.pending is not None:
            self.pending.fitness_samples.append(fitness)
            if day - self.pending.day_started >= 5:
                avg_after = sum(self.pending.fitness_samples) / len(self.pending.fitness_samples)
                trial = self.pending
                self.pending = None
                if avg_after >= trial.fitness_before - 0.015:
                    chromosome.genome_version += 1
                    rec = MutationRecord(
                        day=day,
                        operon_id=trial.operon_id,
                        parameter=trial.parameter,
                        old_value=trial.old_value,
                        new_value=trial.new_value,
                        fitness_before=round(trial.fitness_before, 4),
                        fitness_after=round(avg_after, 4),
                        outcome="kept",
                        reason_de="Fitness stabil oder verbessert — Anpassung im Chromosom verankert.",
                    )
                else:
                    nucleoid.restore_last_snapshot(chromosome.operons)
                    rec = MutationRecord(
                        day=day,
                        operon_id=trial.operon_id,
                        parameter=trial.parameter,
                        old_value=trial.old_value,
                        new_value=trial.new_value,
                        fitness_before=round(trial.fitness_before, 4),
                        fitness_after=round(avg_after, 4),
                        outcome="rolled_back",
                        reason_de="Fitness gefallen — Nukleoid hat auf stabilen Snapshot zurückgerollt.",
                    )
                self.records.append(rec)
                return rec
            return None

        # Alle 7 Tage (oder häufiger bei schwacher Fitness) kontrollierte Mutation starten
        interval = 5 if fitness < 0.55 else 8
        if day < 6 or day - self.last_mutation_day < interval:
            return None

        nucleoid.save_snapshot(chromosome.operons)
        candidate_ops = [
            op
            for op in chromosome.operons.values()
            if op.operon_id
            in (
                "OP_PRICING_HOMEOSTASIS",
                "OP_METABOLIC_EFFICIENCY",
                "OP_CHEMOTAXIS_GROWTH",
                "OP_IMMUNE_DEFENSE",
            )
        ]
        chosen_op = self.rng.choice(candidate_ops)
        param = self.rng.choice(list(chosen_op.parameters.keys()))
        old_val = chosen_op.parameters[param]
        lo = chosen_op.min_bounds[param]
        hi = chosen_op.max_bounds[param]
        step_delta = (hi - lo) * self.rng.choice([-0.12, -0.07, 0.08, 0.14])
        # Sanfter adaptiver Bias hin zu höherer Cache- und Retention-Effizienz
        if param in ("cache_aggressiveness", "pili_retention_focus", "s_layer_strictness"):
            step_delta = abs(step_delta) * 0.9 if old_val < (lo + hi) * 0.72 else step_delta

        new_val = nucleoid.enforce_bounds(
            chosen_op, param, old_val + step_delta, guardrail_strictness
        )
        if abs(new_val - old_val) < 1e-4:
            return None

        chosen_op.parameters[param] = new_val
        self.last_mutation_day = day
        self.pending = PendingTrial(
            day_started=day,
            operon_id=chosen_op.operon_id,
            parameter=param,
            old_value=round(old_val, 4),
            new_value=round(new_val, 4),
            fitness_before=fitness,
        )
        return None

    def record_manual_lab_mutation(
        self,
        day: int,
        operon_id: str,
        parameter: str,
        old_value: float,
        new_value: float,
        fitness: float,
        reason_de: str,
    ) -> MutationRecord:
        rec = MutationRecord(
            day=day,
            operon_id=operon_id,
            parameter=parameter,
            old_value=round(old_value, 4),
            new_value=round(new_value, 4),
            fitness_before=round(fitness, 4),
            fitness_after=round(fitness, 4),
            outcome="manual_lab",
            reason_de=reason_de,
        )
        self.records.append(rec)
        return rec
