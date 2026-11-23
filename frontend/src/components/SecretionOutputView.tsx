import React, { useState } from 'react';
import { MultiLineChart } from './SvgCharts';
import type { OrganismSnapshot } from '../types';

interface Props {
  snapshot: OrganismSnapshot;
}

export const SecretionOutputView: React.FC<Props> = ({ snapshot }) => {
  const [selectedArtIdx, setSelectedArtIdx] = useState<number>(0);
  const artifacts = snapshot.recent_artifacts;
  const activeArt = artifacts[selectedArtIdx] ?? artifacts[0] ?? null;
  const l = snapshot.ledger;
  const days = snapshot.history.map((h) => h.day);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Umsatz- vs. Kosten-Entwicklung */}
      <div className="grid-2">
        <div className="panel">
          <MultiLineChart
            title="Tagesumsatz vs. Tageskosten & Netto-Gewinn"
            days={days}
            series={[
              { label: 'Tagesumsatz', color: '#10b981', values: snapshot.history.map((h) => h.daily_revenue_eur) },
              { label: 'Tageskosten', color: '#f43f5e', values: snapshot.history.map((h) => h.daily_costs_eur) },
              { label: 'Netto-Gewinn', color: '#22d3ee', values: snapshot.history.map((h) => h.daily_net_profit_eur) },
            ]}
          />
        </div>

        {/* Doppelte Buchführung & GuV */}
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Doppelte Buchführung & Stück-Ökonomie (Tag {snapshot.day})</h3>
            <span className="badge badge-active">Nettomarge {l.net_margin_pct.toFixed(1)} %</span>
          </div>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Heute (€)</th>
                  <th>Kumuliert / Bestand</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Umsatz (Kunden + Sexpili-Lizenzen)</td>
                  <td className="mono" style={{ color: '#10b981' }}>{l.daily_revenue_eur.toFixed(2)} €</td>
                  <td className="mono">{l.cumulative_revenue_eur.toFixed(2)} €</td>
                </tr>
                <tr>
                  <td>Variable Compute-COGS (nach Cache & Arbitrage)</td>
                  <td className="mono">{l.daily_cogs_eur.toFixed(2)} €</td>
                  <td className="mono">Bruttomarge {l.gross_margin_pct.toFixed(1)} %</td>
                </tr>
                <tr>
                  <td>Payment-Fees (Plasmamembran) + Infra + Marketing</td>
                  <td className="mono">{(l.daily_payment_fees_eur + l.daily_fixed_infra_eur + l.daily_marketing_eur).toFixed(2)} €</td>
                  <td className="mono">Gesamtkosten {l.cumulative_costs_eur.toFixed(2)} €</td>
                </tr>
                <tr>
                  <td>Steuer-Rückstellung (25 % Escrow)</td>
                  <td className="mono" style={{ color: '#a78bfa' }}>{l.daily_tax_accrual_eur.toFixed(2)} €</td>
                  <td className="mono">{l.tax_escrow_eur.toFixed(2)} €</td>
                </tr>
                <tr>
                  <td><strong>Netto-Gewinn (nach Steuern)</strong></td>
                  <td className="mono" style={{ color: '#22d3ee', fontWeight: 700 }}>{l.daily_net_profit_eur.toFixed(2)} €</td>
                  <td className="mono" style={{ color: '#22d3ee', fontWeight: 700 }}>{l.cumulative_net_profit_eur.toFixed(2)} €</td>
                </tr>
                <tr>
                  <td>Liquidität (Kasse + PHB + Volutin)</td>
                  <td className="mono">{l.cash_eur.toFixed(2)} € Kasse</td>
                  <td className="mono">{l.phb_reserve_eur.toFixed(2)} € PHB · {l.volutin_prepaid_eur.toFixed(2)} € Volutin</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Live Produkt-Output Inspektor */}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Sekretions-Produkte (reale Kunden-Outputs)</h3>
            <span className="badge">{artifacts.length} letzte Artefakte</span>
          </div>
          {artifacts.length === 0 ? (
            <div style={{ fontSize: 13, color: '#94a3b8' }}>
              Noch keine Produkte ausgeliefert — lasse die Simulation 1+ Tag laufen.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7, maxHeight: 390, overflowY: 'auto' }}>
              {artifacts.map((art, idx) => (
                <div
                  key={art.artifact_id}
                  onClick={() => setSelectedArtIdx(idx)}
                  style={{
                    cursor: 'pointer',
                    padding: '9px 11px',
                    borderRadius: 9,
                    background: activeArt?.artifact_id === art.artifact_id ? '#152542' : '#08101f',
                    border: `1px solid ${activeArt?.artifact_id === art.artifact_id ? '#10b981' : 'rgba(148,163,184,0.14)'}`,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                    <strong style={{ fontSize: 13 }}>{art.title}</strong>
                    <span className="badge badge-active mono">+{art.net_margin_pct.toFixed(1)} % Marge</span>
                  </div>
                  <div style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 3 }}>
                    Tag {art.day} · {art.customer_segment.toUpperCase()} · {art.revenue_eur.toFixed(2)} € (COGS {art.cogs_eur.toFixed(3)} €) ·{' '}
                    {art.from_cache ? '⚡ Glykogen-Cache' : art.synthesized_via}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Produkt-Inspektor (Markdown / JSON-Payload)</h3>
            {activeArt && <span className="badge badge-submodule">Qualität {(activeArt.quality_score * 100).toFixed(1)} %</span>}
          </div>
          {activeArt ? (
            <div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 8 }}>
                Auslösende Gene: <span className="mono" style={{ color: '#22d3ee' }}>{activeArt.causal_gene_ids.join(', ')}</span>
              </div>
              <pre className="code-box" style={{ maxHeight: 350 }}>
                {activeArt.content_markdown
                  ? activeArt.content_markdown
                  : JSON.stringify(activeArt.content_json, null, 2)}
              </pre>
            </div>
          ) : (
            <div style={{ fontSize: 13, color: '#94a3b8' }}>Kein Produkt ausgewählt.</div>
          )}
        </div>
      </div>
    </div>
  );
};
