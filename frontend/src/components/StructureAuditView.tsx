import React, { useMemo, useState } from 'react';
import type { RegistryResponse, StructureRegistryEntry } from '../types';

interface Props {
  registry: RegistryResponse | null;
  onInspectOrganelle: (id: string) => void;
}

export const StructureAuditView: React.FC<Props> = ({ registry, onInspectOrganelle }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [systemFilter, setSystemFilter] = useState<string>('all');

  const filtered = useMemo(() => {
    if (!registry) return [];
    const q = search.trim().toLowerCase();
    return registry.structures.filter((s: StructureRegistryEntry) => {
      if (statusFilter === 'viability' && s.category !== 'viability') return false;
      if (statusFilter !== 'all' && statusFilter !== 'viability' && s.status !== statusFilter) return false;
      if (systemFilter !== 'all' && s.system_id !== systemFilter) return false;
      if (!q) return true;
      return (
        s.german_name.toLowerCase().includes(q) ||
        s.english_name.toLowerCase().includes(q) ||
        s.code_symbol.toLowerCase().includes(q) ||
        s.economic_analogy_de.toLowerCase().includes(q)
      );
    });
  }, [registry, search, statusFilter, systemFilter]);

  const summary = registry?.summary ?? {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Essay: Paradigmenwechsel Ingenieur -> Gärtner */}
      <div className="panel" style={{ borderColor: 'rgba(34, 211, 238, 0.35)' }}>
        <div className="panel-header">
          <h3 className="panel-title">Der unternehmerische Paradigmenwechsel: Vom Ingenieur zum Gärtner</h3>
          <span className="badge badge-active">Ökonomische Extrapolation</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14, fontSize: 13, color: '#cbd5e1', lineHeight: 1.55 }}>
          <div style={{ background: '#08101f', padding: 12, borderRadius: 10, borderLeft: '3px solid #f43f5e' }}>
            <strong style={{ color: '#fda4af' }}>Gestern: Der Maschinen-Ingenieur</strong>
            <p style={{ margin: '6px 0 0' }}>
              Jede Regel, jede API-Route, jedes Preisupdate und jede Ausnahmebehandlung wird manuell gebaut und gewartet.
              Steigt die Komplexität, explodieren menschliche Aufmerksamkeitsstunden. Bei Marktschocks bricht die Maschine mit Latenz.
            </p>
          </div>
          <div style={{ background: '#08101f', padding: 12, borderRadius: 10, borderLeft: '3px solid #10b981' }}>
            <strong style={{ color: '#6ee7b7' }}>Morgen: Der Nutzpflanzen-Gärtner</strong>
            <p style={{ margin: '6px 0 0' }}>
              Der Unternehmer pflanzt ein validiertes Saatgut-Genom, setzt Wachstumsbedingungen (Zielmarge, Leitplanken, Ernteschwelle)
              und überlässt dem Organismus die Selbstregulation über Promotoren, mRNA, 70S-Ribosomen, Endosporen und FtsZ-Ernte.
            </p>
          </div>
          <div style={{ background: '#08101f', padding: 12, borderRadius: 10, borderLeft: '3px solid #22d3ee' }}>
            <strong style={{ color: '#67e8f9' }}>Strenge Wert-Prüfung (57 + 7)</strong>
            <p style={{ margin: '6px 0 0' }}>
              Von 57 genannten Prokaryonten-Strukturen liefern {summary.prokaryote_implemented ?? 53} echten ökonomischen Mehrwert im Code;
              4 rein biologische Doppelungen (<em>Pseudopeptidoglykan</em>, <em>Archaellen</em>, <em>Chlorosomen</em>, <em>Crescentin</em>)
              werden begründet gemergt/ausgeschlossen und durch 7 betriebswirtschaftliche Pflichtmodule ergänzt.
            </p>
          </div>
        </div>
      </div>

      {/* Filter & Vollständige Matrix */}
      <div className="panel">
        <div className="panel-header" style={{ flexWrap: 'wrap' }}>
          <div>
            <h3 className="panel-title">Vollständige 57-Prokaryonten- + 7-Viability-Matrix</h3>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              {summary.prokaryote_total ?? 57} Prokaryonten-Strukturen ({summary.prokaryote_active ?? 37} Core ·{' '}
              {summary.prokaryote_submodule ?? 16} Submodule · {summary.prokaryote_merged ?? 3} Gemergt ·{' '}
              {summary.prokaryote_excluded ?? 1} Ausgeschlossen) + {summary.viability_total ?? 7} Viability-Module
            </span>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <input
              className="input-dark"
              placeholder="Suchen (Name, Symbol, Nutzen)…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select className="select-dark" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="all">Alle Status (64)</option>
              <option value="active">Aktiv (Core)</option>
              <option value="submodule">Submodul</option>
              <option value="merged">Begründet gemergt (3)</option>
              <option value="excluded">Ausgeschlossen (1)</option>
              <option value="viability">Viability-Module (7)</option>
            </select>
            <select className="select-dark" value={systemFilter} onChange={(e) => setSystemFilter(e.target.value)}>
              <option value="all">Alle 9 Systeme</option>
              {Object.entries(registry?.systems ?? {}).map(([sid, sname]) => (
                <option key={sid} value={sid}>{sname}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Struktur (DE / EN)</th>
                <th>System</th>
                <th>Status</th>
                <th>Python-Symbol</th>
                <th>Wirtschaftliche Kausal-Funktion</th>
                <th>Wert-Begründung</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id}>
                  <td>
                    <strong style={{ color: '#f8fafc' }}>{s.german_name}</strong>
                    <div style={{ fontSize: 11, color: '#64748b' }}>{s.english_name}</div>
                  </td>
                  <td style={{ fontSize: 11.5, color: '#94a3b8' }}>{s.system_name_de}</td>
                  <td>
                    <span className={`badge badge-${s.category === 'viability' ? 'viability' : s.status}`}>
                      {s.category === 'viability' ? 'viability' : s.status}
                    </span>
                  </td>
                  <td>
                    {s.status === 'active' || s.status === 'submodule' ? (
                      <button className="chip-btn" onClick={() => onInspectOrganelle(s.id)}>
                        <code style={{ color: '#22d3ee' }}>{s.code_symbol}</code>
                      </button>
                    ) : (
                      <code style={{ color: '#94a3b8' }}>{s.code_symbol}</code>
                    )}
                  </td>
                  <td style={{ color: '#cbd5e1' }}>{s.economic_analogy_de}</td>
                  <td style={{ color: '#94a3b8', fontSize: 12 }}>{s.rationale_de}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
