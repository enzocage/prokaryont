import React, { useState } from 'react';
import { MultiLineChart } from './SvgCharts';
import type {
  ConfigOptionsResponse,
  OrganismSnapshot,
  ScalePreset,
  ScenarioPreset,
  SeedTemplate,
} from '../types';

interface Props {
  snapshot: OrganismSnapshot;
  options: ConfigOptionsResponse | null;
  busy: boolean;
  onConfigure: (seed: SeedTemplate, scale: ScalePreset, scenario: ScenarioPreset, importedSeed?: Record<string, unknown> | null) => void;
  onGardenerAction: (payload: Record<string, unknown>) => Promise<Record<string, unknown> | null>;
}

export const GardenerBenchmarkView: React.FC<Props> = ({
  snapshot,
  options,
  busy,
  onConfigure,
  onGardenerAction,
}) => {
  const [seed, setSeed] = useState<SeedTemplate>(snapshot.seed_template);
  const [scale, setScale] = useState<ScalePreset>(snapshot.scale_preset);
  const [scenario, setScenario] = useState<ScenarioPreset>(snapshot.scenario_preset);
  const [targetMargin, setTargetMargin] = useState<number>(snapshot.gardener_policy.target_margin);
  const [harvestThreshold, setHarvestThreshold] = useState<number>(snapshot.gardener_policy.harvest_threshold_eur);
  const [harvestRatio, setHarvestRatio] = useState<number>(snapshot.gardener_policy.harvest_ratio);
  const [strictness, setStrictness] = useState<number>(snapshot.gardener_policy.guardrail_strictness);
  const [exportedSeedJson, setExportedSeedJson] = useState<string>('');
  const [importSeedText, setImportSeedText] = useState<string>('');
  const [statusMsg, setStatusMsg] = useState<string>('');

  const b = snapshot.benchmark_latest;
  const days = snapshot.history.map((h) => h.day);
  const ratioProfitPerHr =
    b.engineer_profit_per_hour > 0
      ? (b.gardener_profit_per_hour / b.engineer_profit_per_hour).toFixed(1)
      : '∞';

  const handleSavePolicy = async () => {
    await onGardenerAction({
      action: 'update_policy',
      target_margin: targetMargin,
      harvest_threshold_eur: harvestThreshold,
      harvest_ratio: harvestRatio,
      guardrail_strictness: strictness,
    });
    setStatusMsg('Gärtner-Leitplanken & Ernteschwelle aktualisiert.');
  };

  const handleExportSeed = async () => {
    const exported = await onGardenerAction({ action: 'export_spore' });
    if (exported) {
      setExportedSeedJson(JSON.stringify(exported, null, 2));
      setStatusMsg('Signiertes Endosporen-Saatgut exportiert.');
    }
  };

  const handlePlantWithSeed = () => {
    try {
      const parsed = importSeedText.trim() ? JSON.parse(importSeedText) : null;
      onConfigure(seed, scale, scenario, parsed);
      setStatusMsg('Neues Saatgut im Gewächshaus gepflanzt.');
    } catch {
      setStatusMsg('Ungültiges JSON im Saatgut-Import.');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Paradigmenwechsel-KPI-Banner */}
      <div className="panel" style={{ borderColor: 'rgba(16, 185, 129, 0.45)', background: 'linear-gradient(135deg, rgba(16,185,129,0.10), rgba(10,18,32,0.95))' }}>
        <div className="panel-header">
          <div>
            <h3 className="panel-title">Paradigmenwechsel-Benchmark: Gärtner (Nutzpflanze) vs. Ingenieur (Maschine)</h3>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              Identischer Marktpfad, identische Schocks — quantitativer Vergleich von Ertrag je menschlicher Aufmerksamkeitsstunde
            </span>
          </div>
          <span className="badge badge-active">{ratioProfitPerHr}x Hebel je Aufmerksamkeitsstunde</span>
        </div>

        <div className="kpi-strip">
          <div className="kpi-card">
            <div className="kpi-label">Gärtner-Gewinn / Stunde</div>
            <div className="kpi-val" style={{ color: '#10b981' }}>{b.gardener_profit_per_hour.toFixed(1)} €/Std.</div>
            <div className="kpi-sub">Aufwand gesamt: {b.gardener_attention_hours.toFixed(1)} Std.</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Ingenieur-Gewinn / Stunde</div>
            <div className="kpi-val" style={{ color: '#f59e0b' }}>{b.engineer_profit_per_hour.toFixed(1)} €/Std.</div>
            <div className="kpi-sub">Aufwand gesamt: {b.engineer_attention_hours.toFixed(1)} Std.</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Kumulierter Netto-Gewinn</div>
            <div className="kpi-val" style={{ color: '#22d3ee' }}>{b.gardener_profit_eur.toFixed(0)} €</div>
            <div className="kpi-sub">Ingenieur-Maschine: {b.engineer_profit_eur.toFixed(0)} €</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Beherrschte Komplexität</div>
            <div className="kpi-val" style={{ color: '#a78bfa' }}>{b.gardener_complexity_score} Pkt.</div>
            <div className="kpi-sub">Ingenieur-Limit: {b.engineer_complexity_score} Pkt. ({b.engineer_incidents_total} Vorfälle)</div>
          </div>
        </div>
      </div>

      {/* Live Benchmark Charts */}
      <div className="grid-2">
        <div className="panel">
          <MultiLineChart
            title="Kumulierter Gewinn: Gärtner-Nutzpflanze vs. Ingenieurs-Maschine"
            days={days}
            series={[
              { label: 'Gärtner (Prokaryont)', color: '#10b981', values: snapshot.history.map((h) => h.gardener_profit_eur) },
              { label: 'Ingenieur (statisch)', color: '#f43f5e', values: snapshot.history.map((h) => h.engineer_profit_eur) },
              { label: 'FtsZ-Ernte kumuliert', color: '#f59e0b', values: snapshot.history.map((h) => h.harvested_cumulative_eur) },
            ]}
          />
        </div>
        <div className="panel">
          <MultiLineChart
            title="Ökonomischer Aufmerksamkeits-Hebel (€ Gewinn pro Menschen-Stunde)"
            days={days}
            unit="€/h"
            series={[
              { label: 'Gärtner €/Std.', color: '#22d3ee', values: snapshot.history.map((h) => h.gardener_profit_per_hour) },
              { label: 'Ingenieur €/Std.', color: '#f59e0b', values: snapshot.history.map((h) => h.engineer_profit_per_hour) },
            ]}
          />
        </div>
      </div>

      {/* Gärtner-Pflegepult & Saatgut-Pflanzung */}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Gärtner-Pflegepult (Niedrig-Aufmerksamkeits-Steuerung)</h3>
          </div>

          <div className="slider-row">
            <label style={{ fontSize: 12 }}>
              Ziel-Stückmarge: <strong>{(targetMargin * 100).toFixed(0)} %</strong>
            </label>
            <input type="range" min={0.30} max={0.85} step={0.01} value={targetMargin} onChange={(e) => setTargetMargin(Number(e.target.value))} />
          </div>

          <div className="slider-row">
            <label style={{ fontSize: 12 }}>
              FtsZ-Ernte-Schwelle (PHB-Reserve): <strong>{harvestThreshold.toFixed(0)} €</strong>
            </label>
            <input type="range" min={50} max={25000} step={25} value={harvestThreshold} onChange={(e) => setHarvestThreshold(Number(e.target.value))} />
          </div>

          <div className="slider-row">
            <label style={{ fontSize: 12 }}>
              Abschöpfungsquote bei Ernte: <strong>{(harvestRatio * 100).toFixed(0)} %</strong>
            </label>
            <input type="range" min={0.10} max={0.75} step={0.05} value={harvestRatio} onChange={(e) => setHarvestRatio(Number(e.target.value))} />
          </div>

          <div className="slider-row">
            <label style={{ fontSize: 12 }}>
              Leitplanken-Strenge (Peptidoglykan & Nukleoid): <strong>{(strictness * 100).toFixed(0)} %</strong>
            </label>
            <input type="range" min={0.20} max={0.98} step={0.02} value={strictness} onChange={(e) => setStrictness(Number(e.target.value))} />
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
            <button disabled={busy} className="btn btn-primary" onClick={handleSavePolicy}>
              Leitplanken speichern
            </button>
            <button disabled={busy} className="btn btn-emerald" onClick={() => onGardenerAction({ action: 'fertilize' })}>
              🌱 Düngen (+Startkapital-Boost)
            </button>
            <button disabled={busy} className="btn btn-amber" onClick={() => onGardenerAction({ action: 'manual_harvest' })}>
              🌾 Jetzt ernten (FtsZ)
            </button>
            {snapshot.mode === 'dormant_endospore' ? (
              <button disabled={busy} className="btn btn-violet" onClick={() => onGardenerAction({ action: 'force_germinate' })}>
                ☀️ Endospore keimen lassen
              </button>
            ) : (
              <button disabled={busy} className="btn btn-violet" onClick={() => onGardenerAction({ action: 'force_dormancy' })}>
                ❄️ In Endospore legen
              </button>
            )}
          </div>
          {statusMsg && <div style={{ marginTop: 10, fontSize: 12, color: '#6ee7b7' }}>{statusMsg}</div>}
        </div>

        {/* Saatgut pflanzen & Sporen-Vererbung */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Neues Saatgut pflanzen & Endosporen-Export</h3>
          </div>
          <div style={{ display: 'grid', gap: 10 }}>
            <div>
              <label style={{ fontSize: 11, color: '#94a3b8' }}>Saatgut-Template (Produkt)</label>
              <select className="select-dark" style={{ width: '100%', marginTop: 3 }} value={seed} onChange={(e) => setSeed(e.target.value as SeedTemplate)}>
                {(options?.seeds ?? []).map((s) => (
                  <option key={s.id} value={s.id}>{s.name_de}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 11, color: '#94a3b8' }}>Ökonomische Skala</label>
              <select className="select-dark" style={{ width: '100%', marginTop: 3 }} value={scale} onChange={(e) => setScale(e.target.value as ScalePreset)}>
                {(options?.scales ?? []).map((s) => (
                  <option key={s.id} value={s.id}>{s.label_de}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 11, color: '#94a3b8' }}>Marktszenario</label>
              <select className="select-dark" style={{ width: '100%', marginTop: 3 }} value={scenario} onChange={(e) => setScenario(e.target.value as ScenarioPreset)}>
                {(options?.scenarios ?? []).map((s) => (
                  <option key={s.id} value={s.id}>{s.name_de}</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button disabled={busy} className="btn btn-primary" onClick={handlePlantWithSeed}>
                🌱 Saatgut neu pflanzen
              </button>
              <button disabled={busy} className="btn btn-violet" onClick={handleExportSeed}>
                🧬 Spore-Saatgut exportieren
              </button>
            </div>
            {exportedSeedJson && (
              <pre className="code-box" style={{ maxHeight: 130 }}>{exportedSeedJson}</pre>
            )}
            <textarea
              className="input-dark mono"
              rows={3}
              placeholder="Optional: Exportiertes Sporen-JSON hier einfügen, um vererbtes Saatgut einzupflanzen…"
              value={importSeedText}
              onChange={(e) => setImportSeedText(e.target.value)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
