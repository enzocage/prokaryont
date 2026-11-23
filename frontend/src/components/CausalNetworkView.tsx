import React, { useState } from 'react';
import type { OrganismSnapshot, StructureRegistryEntry } from '../types';

interface Props {
  snapshot: OrganismSnapshot;
  registryById: Record<string, StructureRegistryEntry>;
  onNavigateToOrganelle: (id: string) => void;
}

const REGELKREISE = [
  {
    id: 'growth',
    title: '1. Wachstums- & Nachfrage-Kreislauf',
    color: '#10b981',
    chain: ['Thylakoide / Phycobilisomen', 'Flagellen & Fimbrien', 'Kundenorders', 'Plasmamembran', 'ATP-Synthase', 'Basalkörper'],
    explanation: 'Umsatz erzeugt Netto-Marge (ETC) → ATP treibt den Flagellen-Motor & Fimbrien-Hooks → mehr Kundenanfragen.',
  },
  {
    id: 'margin',
    title: '2. Margen- & Cache-Homöostase',
    color: '#22d3ee',
    chain: ['Magnetosomen', 'OP_PRICING & OP_METABOLIC', 'mRNA → 70S-Ribosom', 'Glykogen-Cache', 'Carboxysomen / Metabolosomen'],
    explanation: 'Sinkt die Marge oder steigen API-Preise, schalten Promotoren Caching & Kosten-Arbitrage automatisch hoch.',
  },
  {
    id: 'immune',
    title: '3. Immun- & Compliance-Abwehrkreis',
    color: '#f43f5e',
    chain: ['S-Layer (WAF)', 'Äußere Membran + LPS', 'Porin-Drossel', 'Periplasma-KYC', 'Encapsuline + Peptidoglykan'],
    explanation: 'Bot-Stürme und Fraud werden an der Hülle kostenlos gestoppt; PII/Audits landen versiegelt im Encapsulin-Tresor.',
  },
  {
    id: 'evolution',
    title: '4. Adaptiver Evolutions- & Konjugationskreis',
    color: '#a78bfa',
    chain: ['Fitness-Bewertung', 'Nukleoid-Snapshot', 'MutationEngine / Rollback', 'Sexpili-Marktplatz', 'AST-Plasmide'],
    explanation: 'Erfolgreiche Parameter-Mutationen bleiben erhalten, schädliche werden zurückgerollt; Sexpili handelt profitable Plasmide.',
  },
  {
    id: 'dormancy',
    title: '5. Dürre- & Endosporen-Überlebenskreis',
    color: '#f59e0b',
    chain: ['RunwayCircuitBreaker', 'OP_CRISIS_SPORULATION', 'Sporenkortex (-93 % Burn)', 'Protoplast + PHB', 'Exosporium → Keimung'],
    explanation: 'In Rezessionen dehydriert der Kortex die Fixkosten auf ein Minimum; das Exosporium weckt die Zelle bei Erholung.',
  },
];

export const CausalNetworkView: React.FC<Props> = ({
  snapshot,
  registryById,
  onNavigateToOrganelle,
}) => {
  const [selectedStep, setSelectedStep] = useState<number>(1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Interaktives SVG-Kausal-Systemdiagramm der 9 Organsysteme */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">Kausale Wirkarchitektur aller 9 Organsysteme</h3>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              Biolumineszente Flüsse: Geld (Smaragd), mRNA/Gene (Cyan), Abwehr (Rose), ATP & Ernte (Amber), Plasmide (Violett)
            </span>
          </div>
          <span className="badge badge-active">Kausal geschlossen</span>
        </div>

        <svg viewBox="0 0 980 340" style={{ width: '100%', height: 'auto', background: '#060c17', borderRadius: 12, border: '1px solid rgba(56,189,248,0.16)' }}>
          {/* Kausale Verbindungspfade */}
          <path d="M 155 95 L 285 95" stroke="#10b981" strokeWidth="2.5" className="flow-path" />
          <path d="M 435 95 L 555 95" stroke="#22d3ee" strokeWidth="2.5" className="flow-path" />
          <path d="M 705 95 L 825 95" stroke="#10b981" strokeWidth="2.5" className="flow-path" />
          <path d="M 630 132 L 630 205" stroke="#f59e0b" strokeWidth="2.5" className="flow-path" />
          <path d="M 555 245 L 435 245" stroke="#f59e0b" strokeWidth="2.5" className="flow-path" />
          <path d="M 285 245 L 155 245" stroke="#22d3ee" strokeWidth="2.5" className="flow-path" />
          <path d="M 105 205 L 105 132" stroke="#a78bfa" strokeWidth="2" className="flow-path" />
          <path d="M 360 205 L 360 132" stroke="#22d3ee" strokeWidth="2" className="flow-path" />
          <path d="M 880 132 L 880 205" stroke="#f59e0b" strokeWidth="2.5" className="flow-path" />

          {[
            { x: 30, y: 58, w: 135, h: 74, title: '1. Umwelt & Markt', sub: 'Orders · Schocks · Audits', color: '#94a3b8', target: 'magnetosomes' },
            { x: 285, y: 58, w: 150, h: 74, title: '2. Zellhülle (DMZ)', sub: 'S-Layer · LPS · Porin · Payment', color: '#f43f5e', target: 's_layer' },
            { x: 555, y: 58, w: 150, h: 74, title: '3. Stoffwechsel & 70S', sub: '30S/50S · Carboxy · Metab.', color: '#22d3ee', target: 'ribosome_70s' },
            { x: 825, y: 58, w: 130, h: 74, title: '4. Sekretion', sub: 'Briefing MD & REST JSON', color: '#10b981', target: 'secretion_systems' },
            { x: 825, y: 205, w: 130, h: 74, title: '5. Zytoskelett & FtsZ', sub: 'MreB & Spin-Off-Ernte', color: '#f59e0b', target: 'ftsz_ring' },
            { x: 555, y: 205, w: 150, h: 74, title: '6. ETC & ATP + Speicher', sub: 'PHB · Glykogen · Volutin', color: '#f59e0b', target: 'atp_synthase' },
            { x: 285, y: 205, w: 150, h: 74, title: '7. Genetik & Plasmide', sub: 'Nukleoid · Operons · mRNA', color: '#22d3ee', target: 'bacterial_chromosome' },
            { x: 30, y: 205, w: 135, h: 74, title: '8. Motilität & Spore', sub: 'Flagellen · Sexpili · Kortex', color: '#a78bfa', target: 'sex_pili' },
          ].map((box) => (
            <g
              key={box.title}
              className="organelle-node"
              onClick={() => onNavigateToOrganelle(box.target)}
            >
              <rect
                x={box.x}
                y={box.y}
                width={box.w}
                height={box.h}
                rx="10"
                fill="#0d172a"
                stroke={box.color}
                strokeWidth="2"
              />
              <text x={box.x + box.w / 2} y={box.y + 30} textAnchor="middle" fontSize="11.5" fontWeight="700" fill="#f8fafc">
                {box.title}
              </text>
              <text x={box.x + box.w / 2} y={box.y + 50} textAnchor="middle" fontSize="9.5" fill="#94a3b8">
                {box.sub}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div className="grid-2">
        {/* Live Einzel-Tick Kausal-Trace */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Kausaler Tages-Trace (Tag {snapshot.day})</h3>
            <span className="badge">Klick auf Schritt → Zellinspektor</span>
          </div>
          {snapshot.causal_trace.length === 0 ? (
            <div style={{ color: '#94a3b8', fontSize: 13 }}>
              Führe mindestens 1 Simulationstag aus, um den Live-Kausalpfad zu sehen.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {snapshot.causal_trace.map((ev) => (
                <div
                  key={ev.step}
                  onClick={() => {
                    setSelectedStep(ev.step);
                    onNavigateToOrganelle(ev.target_id);
                  }}
                  style={{
                    cursor: 'pointer',
                    padding: '9px 12px',
                    borderRadius: 10,
                    background: selectedStep === ev.step ? '#162542' : '#0b1424',
                    border: `1px solid ${selectedStep === ev.step ? '#22d3ee' : 'rgba(56,189,248,0.14)'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: 10,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#f1f5f9' }}>
                      Schritt {ev.step}: {registryById[ev.source_id]?.german_name ?? ev.source_id} →{' '}
                      {registryById[ev.target_id]?.german_name ?? ev.target_id}
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>{ev.label_de}</div>
                  </div>
                  <span className="badge badge-active mono">
                    {ev.magnitude} {ev.unit}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Die 5 selbstregulierenden Regelkreise */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Die 5 geschlossenen Regelkreise</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {REGELKREISE.map((loop) => (
              <div
                key={loop.id}
                style={{
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: '#08101e',
                  borderLeft: `4px solid ${loop.color}`,
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>{loop.title}</div>
                <div style={{ fontSize: 11.5, color: loop.color, marginTop: 3 }}>
                  {loop.chain.join(' → ')}
                </div>
                <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 4 }}>{loop.explanation}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
