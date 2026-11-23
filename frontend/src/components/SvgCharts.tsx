import React from 'react';

interface SeriesDef {
  label: string;
  color: string;
  values: number[];
}

export const MultiLineChart: React.FC<{
  title: string;
  days: number[];
  series: SeriesDef[];
  unit?: string;
  height?: number;
}> = ({ title, days, series, unit = '€', height = 220 }) => {
  const width = 640;
  const padL = 58;
  const padR = 18;
  const padT = 18;
  const padB = 28;
  const plotW = width - padL - padR;
  const plotH = height - padT - padB;

  const allVals = series.flatMap((s) => s.values);
  const rawMin = allVals.length ? Math.min(0, ...allVals) : 0;
  const rawMax = allVals.length ? Math.max(1, ...allVals) : 100;
  const span = Math.max(1e-6, rawMax - rawMin);

  const xFor = (idx: number, total: number) =>
    total <= 1 ? padL : padL + (idx / (total - 1)) * plotW;
  const yFor = (val: number) => padT + plotH - ((val - rawMin) / span) * plotH;

  const yTicks = [rawMin, rawMin + span * 0.5, rawMax];

  return (
    <div style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{title}</span>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {series.map((s) => (
            <span key={s.label} style={{ fontSize: 11, color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 9, height: 9, borderRadius: 99, background: s.color, display: 'inline-block' }} />
              {s.label}
            </span>
          ))}
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', background: '#070d18', borderRadius: 10, border: '1px solid rgba(56,189,248,0.14)' }}>
        {yTicks.map((t, i) => {
          const y = yFor(t);
          return (
            <g key={i}>
              <line x1={padL} y1={y} x2={width - padR} y2={y} stroke="rgba(148,163,184,0.14)" strokeDasharray="3 3" />
              <text x={padL - 6} y={y + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
                {t >= 1000 ? `${(t / 1000).toFixed(1)}k` : t.toFixed(0)} {unit}
              </text>
            </g>
          );
        })}
        {days.length > 0 && (
          <>
            <text x={padL} y={height - 7} fontSize="10" fill="#64748b">Tag {days[0]}</text>
            <text x={width - padR} y={height - 7} textAnchor="end" fontSize="10" fill="#64748b">
              Tag {days[days.length - 1]}
            </text>
          </>
        )}
        {series.map((s) => {
          if (s.values.length < 2) return null;
          const pts = s.values.map((v, idx) => `${xFor(idx, s.values.length).toFixed(1)},${yFor(v).toFixed(1)}`).join(' ');
          return (
            <polyline
              key={s.label}
              fill="none"
              stroke={s.color}
              strokeWidth="2.3"
              strokeLinejoin="round"
              strokeLinecap="round"
              points={pts}
            />
          );
        })}
      </svg>
    </div>
  );
};
