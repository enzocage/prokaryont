"""FastAPI REST-API, WebSocket-Live-Stream und Auslieferung der Web-App."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from prokaryont.config import (
    ECONOMICS_PROFILES,
    SCENARIO_PROFILES,
    SEED_METADATA,
    ScalePreset,
    ScenarioPreset,
    SeedTemplate,
    ShockType,
)
from prokaryont.genetics.plasmids import PlasmidSecurityError
from prokaryont.models import (
    ConfigureRequest,
    GardenerActionRequest,
    LabMutationRequest,
    ShockTriggerRequest,
    StepRequest,
)
from prokaryont.registry import (
    STRUCTURE_REGISTRY,
    SYSTEM_NAMES_DE,
    get_registry_summary,
)
from prokaryont.simulation import SimulationEngine


def _find_frontend_dist() -> Path | None:
    here = Path(__file__).resolve()
    for parent in (here.parents[3], Path.cwd()):
        dist = parent / "frontend" / "dist"
        if (dist / "index.html").is_file():
            return dist
    return None


def create_app(engine: SimulationEngine | None = None) -> FastAPI:
    """Erstellt die FastAPI-Applikation mit optional injizierter SimulationEngine."""
    sim_engine = engine or SimulationEngine()
    app = FastAPI(
        title="PROKARYONT — Wirtschaftlicher Organismus",
        version="0.1.0",
        description="REST- und WebSocket-API für den selbstregulierenden wirtschaftlichen Prokaryonten.",
    )
    app.state.engine = sim_engine

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/state")
    def get_state() -> Any:
        return sim_engine.get_snapshot()

    @app.get("/api/registry")
    def get_registry() -> dict[str, Any]:
        return {
            "summary": get_registry_summary(),
            "systems": SYSTEM_NAMES_DE,
            "structures": [entry.model_dump() for entry in STRUCTURE_REGISTRY],
        }

    @app.get("/api/config/options")
    def get_config_options() -> dict[str, Any]:
        return {
            "seeds": [
                {"id": seed.value, **meta} for seed, meta in SEED_METADATA.items()
            ],
            "scales": [
                {
                    "id": scale.value,
                    "seed_capital_eur": ECONOMICS_PROFILES[(scale, SeedTemplate.B2B_BRIEFING)].seed_capital_eur,
                    "label_de": {
                        ScalePreset.NANO: "Nano-Prokaryont (100 €)",
                        ScalePreset.SOLOPRENEUR: "Solopreneur-Nutzpflanze (1.000 €)",
                        ScalePreset.GROWTH: "Wachstums-Kultur (10.000 €)",
                    }[scale],
                }
                for scale in ScalePreset
            ],
            "scenarios": [
                {
                    "id": scen.value,
                    "name_de": prof.name_de,
                    "description_de": prof.description_de,
                }
                for scen, prof in SCENARIO_PROFILES.items()
            ],
            "shocks": [
                {"id": ShockType.DEMAND_BOOM.value, "label_de": "Nachfrage-Boom", "default_days": 12},
                {"id": ShockType.PRICE_WAR.value, "label_de": "Preiskrieg", "default_days": 14},
                {"id": ShockType.COMPUTE_SHOCK.value, "label_de": "Compute-Preisschock", "default_days": 10},
                {"id": ShockType.CYBER_STORM.value, "label_de": "Cyber- & Fraud-Sturm", "default_days": 8},
                {"id": ShockType.COMPLIANCE_AUDIT.value, "label_de": "Compliance-Audit", "default_days": 6},
                {"id": ShockType.RECESSION_DROUGHT.value, "label_de": "Rezessions-Dürre", "default_days": 24},
            ],
        }

    @app.post("/api/sim/configure")
    def configure_sim(req: ConfigureRequest) -> Any:
        return sim_engine.configure(
            seed_template=req.seed_template,
            scale_preset=req.scale_preset,
            scenario_preset=req.scenario_preset,
            rng_seed=req.rng_seed,
            imported_spore_seed=req.imported_spore_seed,
        )

    @app.post("/api/sim/step")
    def step_sim(req: StepRequest) -> Any:
        return sim_engine.step(steps=req.steps)

    @app.post("/api/sim/shock")
    def trigger_shock(req: ShockTriggerRequest) -> Any:
        return sim_engine.trigger_shock(
            shock_type=req.shock_type,
            duration_days=req.duration_days,
            intensity=req.intensity,
        )

    @app.post("/api/gardener/action")
    def gardener_action(req: GardenerActionRequest) -> dict[str, Any]:
        snap, exported_seed = sim_engine.apply_gardener_action(req)
        return {
            "snapshot": snap.model_dump(),
            "exported_spore_seed": exported_seed,
        }

    @app.post("/api/lab/mutate")
    def lab_mutate(req: LabMutationRequest) -> Any:
        try:
            return sim_engine.apply_lab_mutation(req)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (ValueError, PlasmidSecurityError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.websocket("/ws/live")
    async def ws_live(websocket: WebSocket) -> None:
        await websocket.accept()
        playing = False
        interval_sec = 0.45
        steps_per_tick = 1
        try:
            await websocket.send_json(sim_engine.get_snapshot().model_dump())
            while True:
                try:
                    msg = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=interval_sec if playing else 5.0,
                    )
                    cmd = msg.get("cmd")
                    if cmd == "play":
                        playing = True
                        interval_sec = max(0.08, float(msg.get("interval_ms", 450)) / 1000.0)
                        steps_per_tick = max(1, min(30, int(msg.get("steps_per_tick", 1))))
                    elif cmd == "pause":
                        playing = False
                    elif cmd == "step":
                        n = max(1, min(365, int(msg.get("steps", 1))))
                        snap = sim_engine.step(steps=n)
                        await websocket.send_json(snap.model_dump())
                    elif cmd == "snapshot":
                        await websocket.send_json(sim_engine.get_snapshot().model_dump())
                except asyncio.TimeoutError:
                    if playing:
                        snap = sim_engine.step(steps=steps_per_tick)
                        await websocket.send_json(snap.model_dump())
        except WebSocketDisconnect:
            return

    dist_dir = _find_frontend_dist()
    if dist_dir is not None:
        assets_dir = dist_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(dist_dir / "index.html")

        @app.get("/{full_path:path}")
        def serve_spa_fallback(full_path: str) -> Any:
            if full_path.startswith("api/") or full_path.startswith("ws/"):
                return JSONResponse({"detail": "Not found"}, status_code=404)
            candidate = dist_dir / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(dist_dir / "index.html")
    else:

        @app.get("/")
        def serve_no_frontend() -> dict[str, str]:
            return {
                "status": "backend_ready",
                "message": "Frontend-Build (frontend/dist) noch nicht erstellt. API unter /api/state erreichbar.",
            }

    return app


app = create_app()
