import React, { useState } from 'react';
import type { OrganismSnapshot } from '../types';

interface Props {
  snapshot: OrganismSnapshot;
  busy: boolean;
  onGardenerAction: (payload: Record<string, unknown>) => Promise<Record<string, unknown> | null>;
  onLabMutate: (payload: Record<string, unknown>) => Promise<void>;
}

const DEFAULT_CUSTOM_PLASMID = `def execute(ctx):
    demand = ctx.get("demand_ratio", 1.0)
    boost = 0.08 if demand > 1.0 else 0.14
    return {"cache_hit_bonus": boost, "price_multiplier": 1.04}
`;

export const GenomeLabView: React.FC<Props> = ({
  snapshot,
  busy,
  onGardenerAction,
  onLabMutate,
}) => {
  const labEnabled = snapshot.gardener_policy.lab_mode_enabled;
  const [selectedPlasmidId, setSelectedPlasmidId] = useState<string>(
    snapshot.plasmids[0]?.plasmid_id ?? '',
  );
  const [customName, setCustomName] = useState<string>('Custom-Nischen-Booster');
  const [customCode, setCustomCode] = useState<string>(DEFAULT_CUSTOM_PLASMID);
  const [labFeedback, setLabFeedback] = useState<string>('');

  const selectedPlasmid = snapshot.plasmids.find((p) => p.plasmid_id === selectedPlasmidId) ?? snapshot.plasmids[0];

  const handleLabCall = async (payload: Record<string, unknown>, okMsg: string) => {
    setLabFeedback('');
    try {
      await onLabMutate(payload);
      setLabFeedback(okMsg);
    } catch (err) {
      setLabFeedback(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Labor-Modus Umschalter */}
      <div className="panel" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
        <div>
          <h3 className="panel-title">Adaptives Hybrid-Genom & Züchtungs-Labor</h3>
          <span style={{ fontSize: 12, color: '#94a3b8' }}>
            Standardmäßig evolviert das Bakterienchromosom autonom. Im optionalen Labor-Modus können Gene & AST-Plasmide manuell editiert werden.
          </span>
        </div>
        <button
          disabled={busy}
          className={`btn ${labEnabled ? 'btn-amber' : 'btn-violet'}`}
          onClick={() => onGardenerAction({ action: 'toggle_lab_mode', lab_mode_enabled: !labEnabled })}
        >
          {labEnabled ? '🔓 Labor-Modus AKTIV (Zurück zu Gärtner)' : '🔒 Labor-Modus aktivieren'}
        </button>
      </div>

      {/* Bakterienchromosom Operons + aktive mRNA */}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Bakterienchromosom (7 ausführbare Operons)</h3>
            <span className="badge">Genom v{snapshot.organelles.bacterial_chromosome?.metrics?.genome_version ?? 1}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {snapshot.operons.map((op) => (
              <div key={op.operon_id} style={{ background: '#08101f', padding: 10, borderRadius: 10, border: `1px solid ${op.promoter_active ? 'rgba(16,185,129,0.45)' : 'rgba(148,163,184,0.16)'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>{op.name_de}</div>
                    <div className="mono" style={{ fontSize: 11, color: '#7dd3fc' }}>
                      Promotor: {op.promoter_expression}
                    </div>
                  </div>
                  <span className={`badge ${op.promoter_active ? 'badge-active' : ''}`}>
                    {op.promoter_active ? 'TRANSKRIBIERT' : 'RUHEND'}
                  </span>
                </div>
                <div style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 4 }}>{op.description_de}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                  {Object.entries(op.parameters).map(([param, val]) => (
                    <div key={param} style={{ background: '#04070e', padding: '5px 8px', borderRadius: 7, fontSize: 11.5, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ color: '#cbd5e1' }}>{param}:</span>
                      <strong className="mono" style={{ color: '#22d3ee' }}>{val.toFixed(2)}</strong>
                      {labEnabled && (
                        <>
                          <button
                            className="chip-btn"
                            onClick={() =>
                              handleLabCall(
                                { action: 'update_operon_param', operon_id: op.operon_id, parameter: param, value: Number((val - 0.05).toFixed(2)) },
                                `${op.operon_id}.${param} gesenkt.`,
                              )
                            }
                          >
                            -
                          </button>
                          <button
                            className="chip-btn"
                            onClick={() =>
                              handleLabCall(
                                { action: 'update_operon_param', operon_id: op.operon_id, parameter: param, value: Number((val + 0.05).toFixed(2)) },
                                `${op.operon_id}.${param} erhöht.`,
                              )
                            }
                          >
                            +
                          </button>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* mRNA Pool & Mutations-Chronik */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="panel">
            <div className="panel-header">
              <h3 className="panel-title">Aktive mRNA-Transkripte (70S-Ribosom Input)</h3>
              <span className="badge badge-submodule">{snapshot.active_mrna.length} aktiv</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7, maxHeight: 240, overflowY: 'auto' }}>
              {snapshot.active_mrna.map((m) => (
                <div key={m.transcript_id} style={{ background: '#070e1c', padding: '7px 10px', borderRadius: 8, fontSize: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong className="mono" style={{ color: '#38bdf8' }}>{m.operon_id}</strong>
                    <span style={{ color: '#94a3b8' }}>TTL {m.remaining_ttl}/{m.ttl_days}d · {m.translated_count}x translatiert</span>
                  </div>
                  <div className="mono" style={{ fontSize: 11, color: '#cbd5e1', marginTop: 3 }}>
                    {JSON.stringify(m.directives)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h3 className="panel-title">Fitness-gesteuerte Mutations-Chronik</h3>
            </div>
            {snapshot.recent_mutations.length === 0 ? (
              <div style={{ fontSize: 12.5, color: '#94a3b8' }}>
                Noch keine abgeschlossenen Mutationen (erste Evaluation ab ca. Tag 11).
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 7, maxHeight: 260, overflowY: 'auto' }}>
                {snapshot.recent_mutations.map((m, idx) => (
                  <div key={idx} style={{ background: '#08101e', padding: '8px 10px', borderRadius: 8, fontSize: 12, borderLeft: `3px solid ${m.outcome === 'kept' ? '#10b981' : m.outcome === 'rolled_back' ? '#f43f5e' : '#f59e0b'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>Tag {m.day}: {m.operon_id}.{m.parameter}</strong>
                      <span className={`badge ${m.outcome === 'kept' ? 'badge-active' : m.outcome === 'rolled_back' ? 'badge-excluded' : 'badge-merged'}`}>
                        {m.outcome}
                      </span>
                    </div>
                    <div style={{ color: '#cbd5e1', marginTop: 2 }}>
                      {m.old_value} → {m.new_value} (Fitness {m.fitness_before.toFixed(3)} → {m.fitness_after.toFixed(3)})
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: 11 }}>{m.reason_de}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sexpili Plasmid-Marktplatz & AST-Sandbox Code-Inspektor */}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Plasmide & Sexpili-Ökosystem-Marktplatz</h3>
            <span className="badge badge-viability">AST-Sandboxed Python</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {snapshot.plasmids.map((p) => (
              <div
                key={p.plasmid_id}
                onClick={() => setSelectedPlasmidId(p.plasmid_id)}
                style={{
                  cursor: 'pointer',
                  padding: 10,
                  borderRadius: 10,
                  background: selectedPlasmid?.plasmid_id === p.plasmid_id ? '#15233e' : '#08101f',
                  border: `1px solid ${p.installed ? 'rgba(167,139,250,0.5)' : 'rgba(148,163,184,0.16)'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                  <strong style={{ fontSize: 13 }}>{p.name_de}</strong>
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    <span className={`badge ${p.installed ? 'badge-active' : ''}`}>
                      {p.installed ? `Installiert (${p.executions}x)` : `${p.price_eur.toFixed(0)} €`}
                    </span>
                    {labEnabled && (
                      <button
                        className="chip-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLabCall(
                            { action: p.installed ? 'remove_plasmid' : 'install_plasmid', plasmid_id: p.plasmid_id },
                            `Plasmid ${p.name_de} ${p.installed ? 'entfernt' : 'installiert'}.`,
                          );
                        }}
                      >
                        {p.installed ? 'Entfernen' : 'Installieren'}
                      </button>
                    )}
                  </div>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 3 }}>{p.description_de}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Plasmid-Quellcode & Labor-AST-Injektor</h3>
          </div>
          {selectedPlasmid && (
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 12, color: '#cbd5e1', marginBottom: 5 }}>
                Aktiver Python-Code von <strong>{selectedPlasmid.name_de}</strong>:
              </div>
              <pre className="code-box">{selectedPlasmid.source_code}</pre>
            </div>
          )}

          <div style={{ borderTop: '1px solid rgba(148,163,184,0.16)', paddingTop: 12 }}>
            <div style={{ fontSize: 12.5, fontWeight: 700, marginBottom: 6 }}>
              Custom-Plasmid im AST-Sandbox testen & injizieren {labEnabled ? '' : '(Labor-Modus erforderlich)'}
            </div>
            <input
              className="input-dark"
              style={{ width: '100%', marginBottom: 8 }}
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="Name des Custom-Plasmids"
            />
            <textarea
              className="input-dark mono"
              rows={5}
              style={{ width: '100%' }}
              value={customCode}
              onChange={(e) => setCustomCode(e.target.value)}
            />
            <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
              <button
                disabled={!labEnabled || busy}
                className="btn btn-violet"
                onClick={() =>
                  handleLabCall(
                    {
                      action: 'inject_custom_plasmid',
                      custom_name_de: customName,
                      custom_hook_point: 'pricing',
                      custom_source_code: customCode,
                    },
                    'Custom-Plasmid erfolgreich AST-validiert und injiziert!',
                  )
                }
              >
                🧪 Custom-Plasmid injizieren
              </button>
              {labFeedback && <span style={{ fontSize: 12, color: '#fde68a' }}>{labFeedback}</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
