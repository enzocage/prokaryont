import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { api } from './api';
import { CausalNetworkView } from './components/CausalNetworkView';
import { CellObservatorySVG } from './components/CellObservatorySVG';
import { GardenerBenchmarkView } from './components/GardenerBenchmarkView';
import { GenomeLabView } from './components/GenomeLabView';
import { OrganelleInspector } from './components/OrganelleInspector';
import { SecretionOutputView } from './components/SecretionOutputView';
import { StructureAuditView } from './components/StructureAuditView';
import type {
  ConfigOptionsResponse,
  OrganismSnapshot,
  RegistryResponse,
  ScalePreset,
  ScenarioPreset,
  SeedTemplate,
  ShockType,
  StructureRegistryEntry,
} from './types';

type TabKey = 'observatory' | 'causal' | 'gardener' | 'genome' | 'outputs' | 'audit';

const MODE_LABELS: Record<string, { text: string; cls: string }> = {
  active: { text: 'Vegetativ Aktiv', cls: 'mode-active' },
  conserving: { text: 'Sparmodus', cls: 'mode-conserving' },
  sporulating: { text: 'Sporulierung', cls: 'mode-dormant' },
  dormant_endospore: { text: 'Endospore (Ruhe)', cls: 'mode-dormant' },
  germinating: { text: 'Keimung', cls: 'mode-active' },
};

export default function App() {
  const [snapshot, setSnapshot] = useState<OrganismSnapshot | null>(null);
  const [registry, setRegistry] = useState<RegistryResponse | null>(null);
  const [options, setOptions] = useState<ConfigOptionsResponse | null>(null);
  const [tab, setTab] = useState<TabKey>('observatory');
  const [selectedOrganelle, setSelectedOrganelle] = useState<string>('bacterial_chromosome');
  const [playing, setPlaying] = useState<boolean>(false);
  const [busy, setBusy] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);

  const registryById = useMemo(() => {
    const map: Record<string, StructureRegistryEntry> = {};
    for (const s of registry?.structures ?? []) {
      map[s.id] = s;
    }
    return map;
  }, [registry]);

  useEffect(() => {
    Promise.all([api.getState(), api.getRegistry(), api.getOptions()])
      .then(([st, reg, opts]) => {
        setSnapshot(st);
        setRegistry(reg);
        setOptions(opts);
      })
      .catch((err) => setErrorMsg(String(err)));
  }, []);

  useEffect(() => {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${proto}//${window.location.host}/ws/live`);
    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data) as OrganismSnapshot;
        setSnapshot(data);
      } catch {
        // ignore malformed frames
      }
    };
    wsRef.current = ws;
    return () => {
      ws.close();
    };
  }, []);

  const togglePlay = useCallback(() => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      if (playing) {
        ws.send(JSON.stringify({ cmd: 'pause' }));
        setPlaying(false);
      } else {
        ws.send(JSON.stringify({ cmd: 'play', interval_ms: 420, steps_per_tick: 1 }));
        setPlaying(true);
      }
    }
  }, [playing]);

  const pauseIfPlaying = useCallback(() => {
    if (playing && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ cmd: 'pause' }));
      setPlaying(false);
    }
  }, [playing]);

  const handleStep = async (steps: number) => {
    pauseIfPlaying();
    setBusy(true);
    try {
      const next = await api.step(steps);
      setSnapshot(next);
    } catch (e) {
      setErrorMsg(String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleConfigure = async (
    seed_template: SeedTemplate,
    scale_preset: ScalePreset,
    scenario_preset: ScenarioPreset,
    imported_spore_seed?: Record<string, unknown> | null,
  ) => {
    pauseIfPlaying();
    setBusy(true);
    try {
      const next = await api.configure({
        seed_template,
        scale_preset,
        scenario_preset,
        rng_seed: 42,
        imported_spore_seed: imported_spore_seed ?? null,
      });
      setSnapshot(next);
    } catch (e) {
      setErrorMsg(String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleTriggerShock = async (shock: ShockType) => {
    setBusy(true);
    try {
      const next = await api.triggerShock(shock, shock === 'recession_drought' ? 22 : 10, 0.82);
      setSnapshot(next);
    } catch (e) {
      setErrorMsg(String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleGardenerAction = async (payload: Record<string, unknown>) => {
    setBusy(true);
    try {
      const res = await api.gardenerAction(payload);
      setSnapshot(res.snapshot);
      return res.exported_spore_seed;
    } catch (e) {
      setErrorMsg(String(e));
      return null;
    } finally {
      setBusy(false);
    }
  };

  const handleLabMutate = async (payload: Record<string, unknown>) => {
    setBusy(true);
    try {
      const next = await api.labMutate(payload);
      setSnapshot(next);
    } finally {
      setBusy(false);
    }
  };

  if (!snapshot) {
    return (
      <div className="app-shell">
        <div className="panel">
          {errorMsg ? `Fehler beim Laden: ${errorMsg}` : 'Initialisiere PROKARYONT Zell-Observatorium…'}
        </div>
      </div>
    );
  }

  const l = snapshot.ledger;
  const b = snapshot.benchmark_latest;
  const modeInfo = MODE_LABELS[snapshot.mode] ?? MODE_LABELS.active;

  return (
    <div className="app-shell">
      {/* Header & globale Simulationssteuerung */}
      <header className="topbar">
        <div className="brand-group">
          <div className="brand-orb">P</div>
          <div>
            <h1 className="brand-title">PROKARYONT</h1>
            <div className="brand-sub">
              Wirtschaftlicher Organismus · Nutzpflanze & Gärtner-Observatorium
            </div>
          </div>
          <span className={`mode-pill ${modeInfo.cls}`}>{modeInfo.text}</span>
        </div>

        <div className="controls-bar">
          <select
            className="select-dark"
            aria-label="Saatgut"
            value={snapshot.seed_template}
            onChange={(e) =>
              handleConfigure(
                e.target.value as SeedTemplate,
                snapshot.scale_preset,
                snapshot.scenario_preset,
              )
            }
          >
            {(options?.seeds ?? []).map((s) => (
              <option key={s.id} value={s.id}>{s.name_de}</option>
            ))}
          </select>

          <select
            className="select-dark"
            aria-label="Skala"
            value={snapshot.scale_preset}
            onChange={(e) =>
              handleConfigure(
                snapshot.seed_template,
                e.target.value as ScalePreset,
                snapshot.scenario_preset,
              )
            }
          >
            {(options?.scales ?? []).map((s) => (
              <option key={s.id} value={s.id}>{s.label_de}</option>
            ))}
          </select>

          <select
            className="select-dark"
            aria-label="Szenario"
            value={snapshot.scenario_preset}
            onChange={(e) =>
              handleConfigure(
                snapshot.seed_template,
                snapshot.scale_preset,
                e.target.value as ScenarioPreset,
              )
            }
          >
            {(options?.scenarios ?? []).map((s) => (
              <option key={s.id} value={s.id}>{s.name_de}</option>
            ))}
          </select>

          <button className={`btn ${playing ? 'btn-amber' : 'btn-primary'}`} onClick={togglePlay}>
            {playing ? '⏸ Pause' : '▶ Live'}
          </button>
          <button disabled={busy} className="btn" onClick={() => handleStep(1)}>+1 Tag</button>
          <button disabled={busy} className="btn" onClick={() => handleStep(30)}>+30 Tage</button>
          <button disabled={busy} className="btn btn-emerald" onClick={() => handleStep(180)}>
            ⏩ 180 Tage Simulation
          </button>
          <button
            disabled={busy}
            className="btn"
            onClick={() =>
              handleConfigure(
                snapshot.seed_template,
                snapshot.scale_preset,
                snapshot.scenario_preset,
              )
            }
          >
            ↺ Reset
          </button>
        </div>
      </header>

      {errorMsg && (
        <div className="panel" style={{ marginTop: 10, borderColor: '#f43f5e', color: '#fecdd3' }}>
          {errorMsg}
        </div>
      )}

      {/* Top KPI Ticker */}
      <section className="kpi-strip">
        <div className="kpi-card">
          <div className="kpi-label">Simulationstag & Markt</div>
          <div className="kpi-val">Tag {snapshot.day}</div>
          <div className="kpi-sub">{snapshot.market.headline_de}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Kasse + PHB-Reserve</div>
          <div className="kpi-val" style={{ color: '#22d3ee' }}>
            {(l.cash_eur + l.phb_reserve_eur).toFixed(0)} €
          </div>
          <div className="kpi-sub">Runway: {l.runway_days.toFixed(0)} Tage · Preis {snapshot.price_eur.toFixed(2)} €</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">FtsZ-Ernte (Gärtner)</div>
          <div className="kpi-val" style={{ color: '#f59e0b' }}>
            {l.cumulative_harvested_eur.toFixed(0)} €
          </div>
          <div className="kpi-sub">Steuer-Escrow: {l.tax_escrow_eur.toFixed(0)} €</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Netto-Gewinn & Marge</div>
          <div className="kpi-val" style={{ color: '#10b981' }}>
            {l.cumulative_net_profit_eur.toFixed(0)} €
          </div>
          <div className="kpi-sub">Heute: {l.net_margin_pct.toFixed(1)} % Marge · Umsatz {l.cumulative_revenue_eur.toFixed(0)} €</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">ATP & Cache-Effizienz</div>
          <div className="kpi-val" style={{ color: '#a78bfa' }}>
            {l.atp_balance.toFixed(1)} ATP
          </div>
          <div className="kpi-sub">
            Glykogen-Hit: {Number(snapshot.organelles.glycogen_cache?.metrics?.hit_rate ?? 0) * 100 | 0} % · Fitness {(snapshot.fitness_score * 100).toFixed(0)} %
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Gärtner vs. Ingenieur</div>
          <div className="kpi-val" style={{ color: '#6ee7b7' }}>
            {b.gardener_profit_per_hour.toFixed(0)} vs {b.engineer_profit_per_hour.toFixed(1)} €/h
          </div>
          <div className="kpi-sub">
            Aufwand {b.gardener_attention_hours.toFixed(1)}h vs {b.engineer_attention_hours.toFixed(0)}h
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <nav className="tabs-nav">
        {(
          [
            ['observatory', '1. Zell-Observatorium'],
            ['causal', '2. Kausal-Netzwerk'],
            ['gardener', '3. Gärtner & Benchmark'],
            ['genome', '4. Genom & Labor'],
            ['outputs', '5. Sekretions-Outputs & Bilanz'],
            ['audit', '6. 57-Strukturen-Audit & Essay'],
          ] as [TabKey, string][]
        ).map(([k, label]) => (
          <button
            key={k}
            className={`tab-btn ${tab === k ? 'active' : ''}`}
            onClick={() => setTab(k)}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Active Tab Content */}
      {tab === 'observatory' && (
        <div className="grid-observatory">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3 className="panel-title">Schematische Multi-Layer-Zellkarte (Prokaryont)</h3>
                <span style={{ fontSize: 12, color: '#94a3b8' }}>
                  Klicke eine Organelle an, um ihre biologische & kausale wirtschaftliche Funktion live zu inspizieren
                </span>
              </div>
              <span className="badge badge-active">53 aktive Strukturen</span>
            </div>
            <CellObservatorySVG
              snapshot={snapshot}
              selectedId={selectedOrganelle}
              onSelect={setSelectedOrganelle}
            />
          </div>

          <OrganelleInspector
            snapshot={snapshot}
            selectedId={selectedOrganelle}
            registryById={registryById}
            onSelect={setSelectedOrganelle}
            onTriggerShock={handleTriggerShock}
            busy={busy}
          />
        </div>
      )}

      {tab === 'causal' && (
        <CausalNetworkView
          snapshot={snapshot}
          registryById={registryById}
          onNavigateToOrganelle={(id) => {
            setSelectedOrganelle(id);
            setTab('observatory');
          }}
        />
      )}

      {tab === 'gardener' && (
        <GardenerBenchmarkView
          snapshot={snapshot}
          options={options}
          busy={busy}
          onConfigure={handleConfigure}
          onGardenerAction={handleGardenerAction}
        />
      )}

      {tab === 'genome' && (
        <GenomeLabView
          snapshot={snapshot}
          busy={busy}
          onGardenerAction={handleGardenerAction}
          onLabMutate={handleLabMutate}
        />
      )}

      {tab === 'outputs' && <SecretionOutputView snapshot={snapshot} />}

      {tab === 'audit' && (
        <StructureAuditView
          registry={registry}
          onInspectOrganelle={(id) => {
            setSelectedOrganelle(id);
            setTab('observatory');
          }}
        />
      )}
    </div>
  );
}
