"""AST-Sandboxed ausführbare Code-Plasmide & horizontaler Plasmid-Marktplatz."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Callable

from prokaryont.models import OrganelleTelemetry, PlasmidInfo


class PlasmidSecurityError(ValueError):
    """Wird geworfen, wenn ein Plasmid-Code unsichere AST-Konstrukte enthält."""


_ALLOWED_BUILTINS: dict[str, Any] = {
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
    "len": len,
    "sum": sum,
    "float": float,
    "int": int,
    "bool": bool,
    "str": str,
    "dict": dict,
    "list": list,
}

_ALLOWED_AST_NODES = (
    ast.Module,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.Assign,
    ast.AugAssign,
    ast.AnnAssign,
    ast.If,
    ast.Expr,
    ast.Pass,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Subscript,
    ast.Slice,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.Call,
    ast.Attribute,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
)

_ALLOWED_METHODS = {"get", "keys", "values", "items", "lower", "upper", "strip"}


class PlasmidSandbox:
    """Validiert und kompiliert Python-Plasmide in einer strengen AST-Whitelist-Sandbox."""

    @classmethod
    def validate_and_compile(cls, source_code: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
        try:
            tree = ast.parse(source_code, mode="exec")
        except SyntaxError as exc:
            raise PlasmidSecurityError(f"Syntaxfehler im Plasmid: {exc}") from exc

        has_execute_fn = False
        for node in ast.walk(tree):
            if not isinstance(node, _ALLOWED_AST_NODES):
                raise PlasmidSecurityError(
                    f"Verbotener AST-Knoten im Plasmid: {type(node).__name__}"
                )
            if isinstance(node, ast.Name) and node.id.startswith("_"):
                raise PlasmidSecurityError(
                    f"Verbotener Bezeichner mit Unterstrich: {node.id}"
                )
            if isinstance(node, ast.Attribute):
                if node.attr.startswith("_") or node.attr not in _ALLOWED_METHODS:
                    raise PlasmidSecurityError(
                        f"Verbotener Attributzugriff im Plasmid: .{node.attr}"
                    )
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in _ALLOWED_BUILTINS:
                        raise PlasmidSecurityError(
                            f"Verbotener Funktionsaufruf im Plasmid: {node.func.id}()"
                        )
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr not in _ALLOWED_METHODS:
                        raise PlasmidSecurityError(
                            f"Verbotener Methodenaufruf: .{node.func.attr}()"
                        )
                else:
                    raise PlasmidSecurityError("Nur direkte Aufrufe erlaubter Builtins gestattet.")
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                has_execute_fn = True

        if not has_execute_fn:
            raise PlasmidSecurityError("Plasmid muss eine Funktion 'def execute(ctx):' definieren.")

        namespace: dict[str, Any] = {"__builtins__": _ALLOWED_BUILTINS}
        compiled = compile(tree, filename="<plasmid_sandbox>", mode="exec")
        exec(compiled, namespace, namespace)  # noqa: S102 — streng durch AST-Whitelist abgesichert
        fn = namespace.get("execute")
        if not callable(fn):
            raise PlasmidSecurityError("'execute' im Plasmid ist nicht aufrufbar.")
        return fn

    @classmethod
    def run_safe(
        cls,
        fn: Callable[[dict[str, Any]], dict[str, Any]],
        ctx: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            out = fn(dict(ctx))
            return out if isinstance(out, dict) else {}
        except Exception:
            return {}


@dataclass
class CodePlasmid:
    """Laufzeitinstanz eines validierten, ausführbaren Code-Plasmids."""

    info: PlasmidInfo
    _fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def compile_if_needed(self) -> None:
        if self._fn is None:
            self._fn = PlasmidSandbox.validate_and_compile(self.info.source_code)

    def execute(self, ctx: dict[str, Any]) -> dict[str, Any]:
        self.compile_if_needed()
        assert self._fn is not None
        self.info.executions += 1
        return PlasmidSandbox.run_safe(self._fn, ctx)


def _builtin_marketplace_plasmids() -> list[CodePlasmid]:
    """6 echte, im AST-Sandbox-Interpreter laufende Ökosystem-Plasmide."""
    raw_defs = [
        (
            "plasmid_semantic_cache_v2",
            "Semantisches Glykogen-Cache-v2-Plasmid",
            "cache_and_cost",
            36.0,
            14.0,
            "Erhöht die semantische Cache-Trefferquote (+18 %) und drückt Token-COGS bei Wiederholungsanfragen.",
            """def execute(ctx):
    hit_boost = 0.16 if ctx.get("repeat_share", 0.3) > 0.2 else 0.10
    cost_factor = 0.84 if ctx.get("compute_mult", 1.0) > 1.1 else 0.89
    return {"cache_hit_bonus": hit_boost, "cogs_multiplier": cost_factor}
""",
        ),
        (
            "plasmid_dynamic_surge_pricer",
            "Elastizitäts-Surge-Pricing-Plasmid",
            "pricing",
            44.0,
            18.5,
            "Nutzt hohe Marken-Kapselstärke und Nachfrage-Peaks für +6–12 % Aufschlag ohne Churn.",
            """def execute(ctx):
    demand_idx = ctx.get("demand_ratio", 1.0)
    capsule = ctx.get("capsule_strength", 0.6)
    comp = ctx.get("competitor_pressure", 0.2)
    mult = 1.0
    if demand_idx > 1.10 and capsule > 0.55:
        mult = 1.0 + min(0.14, (demand_idx - 1.0) * 0.25 + capsule * 0.05)
    elif comp > 0.45 and capsule > 0.65:
        mult = 1.03
    return {"price_multiplier": round(mult, 4)}
""",
        ),
        (
            "plasmid_lps_honeypot_shield",
            "LPS-Honeypot & Chargeback-Schild-Plasmid",
            "security",
            32.0,
            12.0,
            "Blockiert betrügerische Bots schon an der äußeren Membran und reduziert Chargeback-Verluste um 75 %.",
            """def execute(ctx):
    threat = ctx.get("threat_level", 0.1)
    boost = 0.18 if threat > 0.25 else 0.11
    return {"firewall_bonus": boost, "fraud_block_bonus": 0.22}
""",
        ),
        (
            "plasmid_eu_compliance_autopilot",
            "EU-AI-Act & DSGVO-Autopilot-Plasmid",
            "compliance",
            38.0,
            13.5,
            "Erzeugt prüffähige Audit-Belege in Encapsulinen und verhindert Bußgelder bei Compliance-Audits.",
            """def execute(ctx):
    audit = ctx.get("audit_active", False)
    return {"audit_defense_bonus": 0.30 if audit else 0.15, "trust_bonus": 0.04}
""",
        ),
        (
            "plasmid_viral_fimbriae_loop",
            "Virale Fimbrien-Referral-Schleife",
            "acquisition",
            48.0,
            21.0,
            "Verankert Empfehlungs-Hooks an gelieferten Produkten und steigert organische Neukunden um +16 %.",
            """def execute(ctx):
    sat = ctx.get("satisfaction", 0.75)
    demand_boost = 0.18 if sat > 0.75 else 0.08
    return {"organic_demand_bonus": demand_boost}
""",
        ),
        (
            "plasmid_cost_arbitrage_router",
            "Metabolosom-Multi-Model-Arbitrage-Plasmid",
            "routing",
            40.0,
            16.0,
            "Routet einfache Payloads automatisch über günstige Light-Modelle und spart bis zu 24 % Compute-COGS.",
            """def execute(ctx):
    compute_mult = ctx.get("compute_mult", 1.0)
    reduction = 0.24 if compute_mult > 1.15 else 0.15
    return {"arbitrage_cogs_discount": reduction}
""",
        ),
    ]
    out: list[CodePlasmid] = []
    for pid, name, hook, price, est_val, desc, code in raw_defs:
        info = PlasmidInfo(
            plasmid_id=pid,
            name_de=name,
            hook_point=hook,  # type: ignore[arg-type]
            description_de=desc,
            price_eur=price,
            estimated_daily_value_eur=est_val,
            source_code=code,
        )
        cp = CodePlasmid(info=info)
        cp.compile_if_needed()
        out.append(cp)
    return out


class PlasmidRegistry:
    """Verwaltet alle installierten und im Ökosystem verfügbaren Code-Plasmide."""

    def __init__(self, scale_factor: float = 1.0) -> None:
        self.plasmids: dict[str, CodePlasmid] = {}
        for cp in _builtin_marketplace_plasmids():
            # Skaliert Preis & geschätzten ROI realistisch mit Nano/Solopreneur/Growth
            cp.info.price_eur = round(cp.info.price_eur * scale_factor, 2)
            cp.info.estimated_daily_value_eur = round(
                cp.info.estimated_daily_value_eur * scale_factor, 2
            )
            self.plasmids[cp.info.plasmid_id] = cp

    def install(self, plasmid_id: str, day: int) -> CodePlasmid | None:
        cp = self.plasmids.get(plasmid_id)
        if cp is None:
            return None
        cp.compile_if_needed()
        cp.info.installed = True
        cp.info.installed_day = day
        return cp

    def remove(self, plasmid_id: str) -> bool:
        cp = self.plasmids.get(plasmid_id)
        if cp is None:
            return False
        cp.info.installed = False
        return True

    def register_custom_plasmid(
        self,
        plasmid_id: str,
        name_de: str,
        hook_point: str,
        source_code: str,
        day: int,
    ) -> CodePlasmid:
        info = PlasmidInfo(
            plasmid_id=plasmid_id,
            name_de=name_de,
            hook_point=hook_point,  # type: ignore[arg-type]
            description_de="Vom Gärtner/Labor injiziertes benutzerdefiniertes Code-Plasmid.",
            price_eur=0.0,
            estimated_daily_value_eur=10.0,
            installed=True,
            installed_day=day,
            source_code=source_code,
        )
        cp = CodePlasmid(info=info)
        cp.compile_if_needed()
        self.plasmids[plasmid_id] = cp
        return cp

    def execute_installed(self, ctx: dict[str, Any]) -> tuple[dict[str, float], dict[str, dict[str, Any]]]:
        """Führt alle aktiven Plasmide in der Sandbox aus und aggregiert Effekte."""
        effects: dict[str, float] = {
            "cache_hit_bonus": 0.0,
            "cogs_multiplier": 1.0,
            "price_multiplier": 1.0,
            "firewall_bonus": 0.0,
            "fraud_block_bonus": 0.0,
            "audit_defense_bonus": 0.0,
            "trust_bonus": 0.0,
            "organic_demand_bonus": 0.0,
            "arbitrage_cogs_discount": 0.0,
        }
        per_plasmid: dict[str, dict[str, Any]] = {}
        for pid, cp in self.plasmids.items():
            if not cp.info.installed:
                continue
            res = cp.execute(ctx)
            per_plasmid[pid] = res
            for k, v in res.items():
                if not isinstance(v, (int, float)):
                    continue
                if k in ("cogs_multiplier", "price_multiplier"):
                    effects[k] *= float(v)
                elif k in effects:
                    effects[k] += float(v)
        return effects, per_plasmid

    def installed_list(self) -> list[CodePlasmid]:
        return [cp for cp in self.plasmids.values() if cp.info.installed]

    def export_installed_ids(self) -> list[str]:
        return [pid for pid, cp in self.plasmids.items() if cp.info.installed]

    def to_telemetry(self) -> OrganelleTelemetry:
        installed = self.installed_list()
        return OrganelleTelemetry(
            id="plasmids",
            name_de="Plasmide (Code-Module)",
            system_id="genetics",
            health=1.0,
            activity=min(1.0, len(installed) / 6.0),
            load=min(1.0, len(installed) / 6.0),
            efficiency=1.0,
            state_label_de=f"{len(installed)}/{len(self.plasmids)} Plasmide aktiv",
            metrics={
                "installed_count": len(installed),
                "available_count": len(self.plasmids),
                "total_executions": sum(cp.info.executions for cp in installed),
            },
        )


class PlasmidMarketplace:
    """Externer Ökosystem-Marktplatz für den horizontalen Plasmid-Handel über Sexpili."""

    def __init__(self, scale_factor: float = 1.0) -> None:
        self.scale_factor = scale_factor
        self.total_spent_eur: float = 0.0
        self.total_licensing_income_eur: float = 0.0

    def pick_best_acquisition(
        self,
        registry: PlasmidRegistry,
        available_cash_eur: float,
        available_atp: float,
        market_threat: float,
        audit_active: bool,
        compute_mult: float,
        competitor_pressure: float,
    ) -> CodePlasmid | None:
        """Wählt bei ausreichender Liquidität das Plasmid mit höchstem ROI-Bedarf."""
        candidates = [cp for cp in registry.plasmids.values() if not cp.info.installed]
        if not candidates:
            return None

        def score(cp: CodePlasmid) -> float:
            roi = cp.info.estimated_daily_value_eur / max(1.0, cp.info.price_eur)
            hook = cp.info.hook_point
            if hook == "security" and market_threat > 0.22:
                roi *= 2.0
            elif hook == "compliance" and audit_active:
                roi *= 2.1
            elif hook == "routing" and compute_mult > 1.1:
                roi *= 1.8
            elif hook == "cache_and_cost":
                roi *= 1.45
            elif hook == "pricing" and competitor_pressure > 0.25:
                roi *= 1.5
            elif hook == "acquisition":
                roi *= 1.35
            return roi

        best = max(candidates, key=score)
        # Kauf nur, wenn ein deutlicher Liquiditätspuffer verbleibt
        if available_cash_eur >= best.info.price_eur * 2.8 and available_atp >= 8.0:
            return best
        return None

    def compute_daily_licensing_revenue(
        self,
        registry: PlasmidRegistry,
        fitness_score: float,
        capsule_strength: float,
    ) -> float:
        """Berechnet Lizenz-Einnahmen, wenn starke eigene Anpassungen am Markt nachgefragt werden."""
        installed = registry.installed_list()
        if not installed or fitness_score < 0.62:
            return 0.0
        # Je höher Fitness & Kapsel-Reputation, desto mehr Zellen lizenzieren über Sexpili mit
        income = (
            len(installed)
            * 1.45
            * self.scale_factor
            * max(0.0, fitness_score - 0.45)
            * (0.6 + capsule_strength)
        )
        income = round(income, 4)
        self.total_licensing_income_eur += income
        for cp in installed:
            cp.info.daily_licensing_revenue_eur = round(income / len(installed), 4)
        return income
