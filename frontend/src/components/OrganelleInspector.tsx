import React from 'react';
import type { OrganismSnapshot, ShockType, StructureRegistryEntry } from '../types';

interface Props {
  snapshot: OrganismSnapshot;
  selectedId: string;
  registryById: Record<string, StructureRegistryEntry>;
  onSelect: (id: string) => void;
  onTriggerShock: (shock: ShockType) => void;
  busy: boolean;
}

const SHOCK_BUTTONS: { id: ShockType; label: string }[] = [
  { id: 'demand_boom', label: 'Nachfrage-Boom' },
  { id: 'price_war', label: 'Preiskrieg' },
  { id: 'compute_shock', label: 'Compute-Schock' },
  { id: 'cyber_storm', label: 'Cyber-Sturm' },
  { id: 'compliance_audit', label: 'Compliance-Audit' },
  { id: 'recession_drought', label: 'Rezessions-Dürre' },
];

export const OrganelleInspector: React.FC<Props> = ({
  snapshot,
  selectedId,
  registryById,
  onSelect,
  onTriggerShock,
  busy,
}) => {
  const entry = registryById[selectedId];
  const tel = snapshot.organelles[selectedId];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">{entry ? entry.german_name : selectedId}</h3>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              {entry ? `${entry.english_name} · ${entry.system_name_de}` : ''}
            </span>
          </div>
          {entry && (
            <span className={`badge badge-${entry.category === 'viability' ? 'viability' : entry.status}`}>
              {entry.category === 'viability' ? 'Viability-Modul' : entry.status}
            </span>
          )}
        </div>

        {entry && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
            <div style={{ background: '#070d18', padding: '8px 10px', borderRadius: 8, border: '1px solid rgba(56,189,248,0.14)' }}>
              <span style={{ color: '#64748b', fontSize: 11 }}>Code-Symbol: </span>
              <code style={{ color: '#22d3ee', fontWeight: 600 }}>{entry.code_symbol}</code>
            </div>

            <div>
              <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase' }}>Biologische Funktion</div>
              <div style={{ color: '#cbd5e1', marginTop: 2 }}>{entry.bio_function_de}</div>
            </div>

            <div>
              <div style={{ fontSize: 11, color: '#10b981', textTransform: 'uppercase' }}>Ökonomische Kausal-Analogie</div>
              <div style={{ color: '#ecfdf5', marginTop: 2 }}>{entry.economic_analogy_de}</div>
            </div>

            {tel && (
              <div style={{ background: '#0c1526', padding: 10, borderRadius: 10, border: '1px solid rgba(34,211,238,0.22)' }}>
                <div style={{ fontSize: 11, color: '#22d3ee', fontWeight: 700, marginBottom: 6 }}>
                  LIVE-ZUSTAND: {tel.state_label_de}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 6, fontSize: 12 }}>
                  {Object.entries(tel.metrics).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', background: '#070d18', padding: '4px 8px', borderRadius: 6 }}>
                      <span style={{ color: '#94a3b8' }}>{k}</span>
                      <span className="mono" style={{ color: '#f8fafc', fontWeight: 600 }}>{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(entry.upstream_ids.length > 0 || entry.downstream_ids.length > 0) && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {entry.upstream_ids.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, alignItems: 'center' }}>
                    <span style={{ fontSize: 11, color: '#64748b' }}>Upstream:</span>
                    {entry.upstream_ids.map((uid) => (
                      <button key={uid} className="chip-btn" onClick={() => onSelect(uid)}>
                        {registryById[uid]?.german_name ?? uid}
                      </button>
                    ))}
                  </div>
                )}
                {entry.downstream_ids.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, alignItems: 'center' }}>
                    <span style={{ fontSize: 11, color: '#64748b' }}>Downstream:</span>
                    {entry.downstream_ids.map((did) => (
                      <button key={did} className="chip-btn" onClick={() => onSelect(did)}>
                        {registryById[did]?.german_name ?? did}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interaktive Schock-Trigger */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Umwelt-Schock manuell auslösen</h3>
          <span className="badge">{snapshot.market.active_shocks.length} aktiv</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 7 }}>
          {SHOCK_BUTTONS.map((sb) => (
            <button
              key={sb.id}
              disabled={busy}
              className={`btn ${sb.id === 'demand_boom' ? 'btn-emerald' : 'btn-rose'}`}
              onClick={() => onTriggerShock(sb.id)}
            >
              ⚡ {sb.label}
            </button>
          ))}
        </div>
        {snapshot.market.active_shocks.length > 0 && (
          <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 5 }}>
            {snapshot.market.active_shocks.map((s, i) => (
              <div key={i} style={{ fontSize: 12, color: '#fecdd3', background: 'rgba(244,63,94,0.12)', padding: '5px 8px', borderRadius: 6 }}>
                Aktiv bis Tag {s.end_day}: {s.label_de}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Live Chronik */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Kausale Lebens-Chronik</h3>
        </div>
        <div className="log-list">
          {snapshot.narrative_log_de.map((line, i) => (
            <div key={i} className="log-item">{line}</div>
          ))}
        </div>
      </div>
    </div>
  );
};
