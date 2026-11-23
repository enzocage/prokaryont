"""API- und WebSocket-Integrationstests für den FastAPI-Server."""

from __future__ import annotations

from fastapi.testclient import TestClient

from prokaryont.api.server import create_app
from prokaryont.simulation import SimulationEngine


def test_rest_endpoints_lifecycle_and_lab_guardrail():
    client = TestClient(create_app(SimulationEngine()))

    r_state = client.get("/api/state")
    assert r_state.status_code == 200
    assert r_state.json()["day"] == 0

    r_reg = client.get("/api/registry")
    assert r_reg.status_code == 200
    assert r_reg.json()["summary"]["prokaryote_total"] == 57

    r_opts = client.get("/api/config/options")
    assert r_opts.status_code == 200
    assert len(r_opts.json()["seeds"]) == 2
    assert len(r_opts.json()["scales"]) == 3

    r_step = client.post("/api/sim/step", json={"steps": 5})
    assert r_step.status_code == 200
    assert r_step.json()["day"] == 5

    r_shock = client.post("/api/sim/shock", json={"shock_type": "cyber_storm", "duration_days": 5, "intensity": 0.8})
    assert r_shock.status_code == 200
    assert len(r_shock.json()["market"]["active_shocks"]) == 1

    # Gärtner-Aktionen: Düngen & Export
    r_fert = client.post("/api/gardener/action", json={"action": "fertilize", "amount_eur": 250.0})
    assert r_fert.status_code == 200
    r_exp = client.post("/api/gardener/action", json={"action": "export_spore"})
    assert r_exp.status_code == 200
    assert "sha256" in r_exp.json()["exported_spore_seed"]

    # Labor-Modus gesperrt -> 403
    r_lab_locked = client.post(
        "/api/lab/mutate",
        json={"action": "install_plasmid", "plasmid_id": "plasmid_semantic_cache_v2"},
    )
    assert r_lab_locked.status_code == 403

    # Labor-Modus entsperren -> Custom Plasmid testen
    client.post("/api/gardener/action", json={"action": "toggle_lab_mode", "lab_mode_enabled": True})
    r_lab_ok = client.post(
        "/api/lab/mutate",
        json={
            "action": "inject_custom_plasmid",
            "custom_name_de": "Test-Plasmid",
            "custom_hook_point": "pricing",
            "custom_source_code": "def execute(ctx):\n    return {'price_multiplier': 1.03}\n",
        },
    )
    assert r_lab_ok.status_code == 200

    # Unsicheres Plasmid -> 400
    r_lab_bad = client.post(
        "/api/lab/mutate",
        json={
            "action": "inject_custom_plasmid",
            "custom_name_de": "Evil-Plasmid",
            "custom_hook_point": "pricing",
            "custom_source_code": "import os\ndef execute(ctx):\n    return {}\n",
        },
    )
    assert r_lab_bad.status_code == 400


def test_websocket_live_stream():
    client = TestClient(create_app(SimulationEngine()))
    with client.websocket_connect("/ws/live") as ws:
        initial = ws.receive_json()
        assert initial["day"] == 0
        ws.send_json({"cmd": "step", "steps": 3})
        updated = ws.receive_json()
        assert updated["day"] == 3
