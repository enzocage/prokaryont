import React, { useState } from 'react';
import type { OrganismSnapshot } from '../types';

interface Props {
  snapshot: OrganismSnapshot;
  selectedId: string;
  onSelect: (id: string) => void;
}

type LayerFilter = 'all' | 'envelope' | 'genetics' | 'metabolism' | 'motility' | 'dormancy';

export const CellObservatorySVG: React.FC<Props> = ({ snapshot, selectedId, onSelect }) => {
  const [layer, setLayer] = useState<LayerFilter>('all');

  const org = snapshot.organelles;
  const isDormant = snapshot.mode === 'dormant_endospore';
  const phbFill = Number(org.phb_reserve?.metrics?.fill_ratio ?? 0.3);
  const glycoHit = Number(org.glycogen_cache?.metrics?.hit_rate ?? 0.35);
  const volutinFill = Number(org.volutin_pool?.metrics?.fill_ratio ?? 0.2);
  const sulfurFill = Number(org.sulfur_buffer?.metrics?.fill_ratio ?? 0.25);
  const ftszTension = Number(org.ftsz_ring?.metrics?.ring_tension ?? 0.2);
  const atpRatio = Math.min(1, snapshot.ledger.atp_balance / 80);

  const dimIf = (group: LayerFilter) => (layer === 'all' || layer === group ? 1 : 0.18);
  const selClass = (id: string) => `organelle-node ${selectedId === id ? 'selected' : ''}`;

  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
        {(
          [
            ['all', 'Alle Schichten'],
            ['envelope', 'Zellhülle & Abwehr'],
            ['genetics', 'Genetik & 70S'],
            ['metabolism', 'Stoffwechsel & Speicher'],
            ['motility', 'Motilität & Sekretion'],
            ['dormancy', 'Spore & FtsZ-Ernte'],
          ] as [LayerFilter, string][]
        ).map(([k, label]) => (
          <button
            key={k}
            className={`chip-btn ${layer === k ? 'active' : ''}`}
            onClick={() => setLayer(k)}
          >
            {label}
          </button>
        ))}
      </div>

      <svg
        viewBox="0 0 980 540"
        style={{
          width: '100%',
          height: 'auto',
          background: 'radial-gradient(circle at 50% 50%, #0d1c33 0%, #04070e 78%)',
          borderRadius: 14,
          border: '1px solid rgba(56, 189, 248, 0.22)',
        }}
      >
        <defs>
          <radialGradient id="cytoGlow" cx="50%" cy="50%" r="55%">
            <stop offset="0%" stopColor={isDormant ? '#4c1d95' : '#0f2942'} stopOpacity="0.82" />
            <stop offset="100%" stopColor="#071120" stopOpacity="0.95" />
          </radialGradient>
          <linearGradient id="harvestGlow" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#fbbf24" stopOpacity="0.2" />
          </linearGradient>
        </defs>

        {/* Hintergrund-Mikroskop-Raster */}
        <g opacity="0.12" stroke="#38bdf8" strokeWidth="0.6">
          <line x1="0" y1="270" x2="980" y2="270" />
          <line x1="490" y1="0" x2="490" y2="540" />
          <circle cx="490" cy="270" r="245" fill="none" strokeDasharray="4 6" />
        </g>

        {/* ============================================================ */}
        {/* MOTILITÄT: Flagellen, Basalkörper, Haken, Filament, Fimbrien, Pili, Sexpili */}
        {/* ============================================================ */}
        <g opacity={dimIf('motility')}>
          {/* Flagellenfilament */}
          <path
            d="M 800 270 Q 845 230 885 268 T 955 262"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="5"
            strokeLinecap="round"
            className={`flow-path ${selClass('flagellar_filament')}`}
            onClick={() => onSelect('flagellar_filament')}
          />
          {/* Haken */}
          <path
            d="M 774 270 Q 790 258 800 270"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="7"
            className={selClass('flagellar_hook')}
            onClick={() => onSelect('flagellar_hook')}
          />
          {/* Basalkörper */}
          <g className={selClass('basal_body')} onClick={() => onSelect('basal_body')}>
            <rect x="752" y="255" width="22" height="30" rx="5" fill="#0ea5e9" stroke="#e0f2fe" strokeWidth="1.5" />
            <text x="763" y="274" fontSize="9" textAnchor="middle" fill="#030712" fontWeight="700">M</text>
          </g>
          {/* Flagellum Gesamtlabel */}
          <g className={selClass('flagella')} onClick={() => onSelect('flagella')}>
            <rect x="835" y="294" width="118" height="24" rx="8" fill="#0a1628" stroke="#22d3ee" strokeOpacity="0.55" />
            <text x="894" y="310" fontSize="10" textAnchor="middle" fill="#67e8f9" fontWeight="600">
              Flagellen (Marktkurs)
            </text>
          </g>

          {/* Fimbrien rund um die Hülle */}
          {[
            [270, 88, 250, 56],
            [355, 76, 345, 42],
            [455, 72, 455, 38],
            [565, 75, 575, 42],
            [310, 458, 295, 492],
            [420, 464, 420, 498],
          ].map(([x1, y1, x2, y2], idx) => (
            <line
              key={idx}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#34d399"
              strokeWidth="2.4"
              strokeLinecap="round"
              className={selClass('fimbriae')}
              onClick={() => onSelect('fimbriae')}
            />
          ))}
          <text
            x="245"
            y="48"
            fontSize="10"
            fill="#6ee7b7"
            className={selClass('fimbriae')}
            onClick={() => onSelect('fimbriae')}
          >
            Fimbrien (Leads)
          </text>

          {/* Pili (B2B-Partner) */}
          <g className={selClass('pili')} onClick={() => onSelect('pili')}>
            <line x1="635" y1="84" x2="675" y2="42" stroke="#10b981" strokeWidth="4" strokeLinecap="round" />
            <circle cx="678" cy="39" r="5" fill="#10b981" />
            <text x="688" y="42" fontSize="10" fill="#a7f3d0">Pili (B2B-Partner)</text>
          </g>

          {/* Sexpili (Plasmid-Konjugation) */}
          <g className={selClass('sex_pili')} onClick={() => onSelect('sex_pili')}>
            <line x1="665" y1="454" x2="758" y2="500" stroke="#a78bfa" strokeWidth="4.5" strokeDasharray="5 3" />
            <circle cx="764" cy="503" r="10" fill="#1e1b4b" stroke="#a78bfa" strokeWidth="2" />
            <text x="780" y="507" fontSize="10.5" fill="#ddd6fe" fontWeight="600">
              Sexpili → Plasmid-Marktplatz
            </text>
          </g>
        </g>

        {/* ============================================================ */}
        {/* ZELLHÜLLEN-SCHICHTEN (Glykokalyx, Kapsel, Schleimschicht, S-Layer, äußere Membran, Zellwand, Periplasma, Plasmamembran) */}
        {/* ============================================================ */}
        <g opacity={dimIf('envelope')}>
          {/* Glykokalyx / Schleimschicht */}
          <rect
            x="162"
            y="68"
            width="656"
            height="404"
            rx="195"
            fill="rgba(16, 185, 129, 0.05)"
            stroke="#10b981"
            strokeWidth="4"
            strokeDasharray="10 6"
            strokeOpacity="0.4"
            className={selClass('slime_layer')}
            onClick={() => onSelect('slime_layer')}
          />
          {/* Kapsel */}
          <rect
            x="176"
            y="82"
            width="628"
            height="376"
            rx="184"
            fill="none"
            stroke="#34d399"
            strokeWidth="3.5"
            strokeOpacity="0.55"
            className={selClass('capsule')}
            onClick={() => onSelect('capsule')}
          />
          {/* S-Layer (WAF) */}
          <rect
            x="190"
            y="96"
            width="600"
            height="348"
            rx="170"
            fill="none"
            stroke="#f43f5e"
            strokeWidth="3"
            strokeDasharray="3 4"
            className={selClass('s_layer')}
            onClick={() => onSelect('s_layer')}
          />
          {/* Äußere Membran */}
          <rect
            x="202"
            y="108"
            width="576"
            height="324"
            rx="158"
            fill="none"
            stroke="#fb7185"
            strokeWidth="3.5"
            className={selClass('outer_membrane')}
            onClick={() => onSelect('outer_membrane')}
          />
          {/* Periplasma-Raum */}
          <rect
            x="213"
            y="119"
            width="554"
            height="302"
            rx="148"
            fill="rgba(56, 189, 248, 0.04)"
            stroke="#38bdf8"
            strokeWidth="1.5"
            strokeOpacity="0.45"
            className={selClass('periplasm')}
            onClick={() => onSelect('periplasm')}
          />
          {/* Zellwand + Peptidoglykan */}
          <rect
            x="222"
            y="128"
            width="536"
            height="284"
            rx="140"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="4.5"
            strokeOpacity="0.72"
            className={selClass('cell_wall')}
            onClick={() => onSelect('cell_wall')}
          />
          <rect
            x="228"
            y="134"
            width="524"
            height="272"
            rx="134"
            fill="none"
            stroke="#fcd34d"
            strokeWidth="1.5"
            strokeDasharray="6 4"
            className={selClass('peptidoglycan')}
            onClick={() => onSelect('peptidoglycan')}
          />
          {/* Plasmamembran + Cytoplasma */}
          <rect
            x="236"
            y="142"
            width="508"
            height="256"
            rx="126"
            fill="url(#cytoGlow)"
            stroke="#22d3ee"
            strokeWidth="3"
            className={selClass('plasma_membrane')}
            onClick={() => onSelect('plasma_membrane')}
          />

          {/* LPS-Rezeptoren */}
          {[245, 295, 345].map((yPos, i) => (
            <g
              key={i}
              className={selClass('lipopolysaccharides')}
              onClick={() => onSelect('lipopolysaccharides')}
            >
              <line x1="178" y1={yPos} x2="202" y2={yPos} stroke="#f43f5e" strokeWidth="3" />
              <circle cx="176" cy={yPos} r="4.5" fill="#f43f5e" />
            </g>
          ))}
          <text x="86" y="298" fontSize="10" fill="#fda4af" className={selClass('lipopolysaccharides')} onClick={() => onSelect('lipopolysaccharides')}>
            LPS-Anti-Fraud
          </text>

          {/* Porine (Eingangskanäle links) */}
          <g className={selClass('porins')} onClick={() => onSelect('porins')}>
            <rect x="195" y="218" width="46" height="26" rx="6" fill="#0c4a6e" stroke="#38bdf8" strokeWidth="2" />
            <text x="218" y="235" fontSize="9.5" textAnchor="middle" fill="#e0f2fe" fontWeight="700">PORIN</text>
            {/* Animierter Kunden-Geldfluss durch Porin */}
            <path d="M 35 231 L 245 231" stroke="#10b981" strokeWidth="3" className="flow-path" />
            <text x="42" y="222" fontSize="10.5" fill="#6ee7b7" fontWeight="700">
              Kunden-Orders & €
            </text>
          </g>

          {/* Hüllen-Labels */}
          <g className={selClass('glycocalyx')} onClick={() => onSelect('glycocalyx')}>
            <text x="490" y="60" fontSize="10.5" textAnchor="middle" fill="#6ee7b7" fontWeight="600">
              Glykokalyx (Kapsel + Schleimschicht) · S-Layer · Äußere Membran · Zellwand · Plasmamembran
            </text>
          </g>
        </g>

        {/* ============================================================ */}
        {/* ZYTOSKELETT: MreB-Filamente & FtsZ-Ernte-Ring */}
        {/* ============================================================ */}
        <g opacity={layer === 'all' || layer === 'dormancy' ? 1 : 0.2}>
          <path
            d="M 275 162 Q 490 144 705 162"
            fill="none"
            stroke="#0284c7"
            strokeWidth="2.5"
            strokeDasharray="8 5"
            className={selClass('mreb_filaments')}
            onClick={() => onSelect('mreb_filaments')}
          />
          <path
            d="M 275 378 Q 490 396 705 378"
            fill="none"
            stroke="#0284c7"
            strokeWidth="2.5"
            strokeDasharray="8 5"
            className={selClass('mreb_filaments')}
            onClick={() => onSelect('mreb_filaments')}
          />
          <text x="490" y="156" fontSize="9.5" textAnchor="middle" fill="#7dd3fc" className={selClass('mreb_filaments')} onClick={() => onSelect('mreb_filaments')}>
            MreB-Filamente (Load Balancer)
          </text>

          {/* FtsZ-Ring Kontraktion (Ernte-Ring in Zellmitte) */}
          <g className={selClass('ftsz_ring')} onClick={() => onSelect('ftsz_ring')}>
            <ellipse
              cx="490"
              cy="270"
              rx={14 + ftszTension * 8}
              ry="126"
              fill="none"
              stroke="url(#harvestGlow)"
              strokeWidth={3 + ftszTension * 4}
              strokeDasharray="6 4"
            />
            <path d="M 490 144 L 490 50" stroke="#f59e0b" strokeWidth="2.5" className="flow-path" />
            <rect x="424" y="18" width="132" height="24" rx="8" fill="#451a03" stroke="#f59e0b" />
            <text x="490" y="34" fontSize="10" textAnchor="middle" fill="#fde68a" fontWeight="700">
              FtsZ-Ernte: {snapshot.ledger.cumulative_harvested_eur.toFixed(0)} €
            </text>
          </g>
        </g>

        {/* ============================================================ */}
        {/* GENETIK: Nukleoid, Chromosom, Plasmide, mRNA, 70S-Ribosom (30S, 50S, tRNA, rRNA) */}
        {/* ============================================================ */}
        <g opacity={dimIf('genetics')}>
          {/* Nukleoid-Region */}
          <ellipse
            cx="370"
            cy="255"
            rx="82"
            ry="62"
            fill="rgba(34, 211, 238, 0.08)"
            stroke="#22d3ee"
            strokeWidth="1.5"
            strokeDasharray="4 4"
            className={selClass('nucleoid')}
            onClick={() => onSelect('nucleoid')}
          />
          {/* Bakterienchromosom (verdrillte Doppelstrang-Schleife) */}
          <path
            d="M 318 250 C 330 212, 395 208, 415 245 C 432 278, 385 304, 344 292 C 304 280, 308 232, 355 224 C 392 218, 426 264, 385 286"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="3.2"
            className={selClass('bacterial_chromosome')}
            onClick={() => onSelect('bacterial_chromosome')}
          />
          <text x="370" y="205" fontSize="10.5" textAnchor="middle" fill="#a5f3fc" fontWeight="700" className={selClass('bacterial_chromosome')} onClick={() => onSelect('bacterial_chromosome')}>
            Nukleoid & Chromosom (v{snapshot.organelles.bacterial_chromosome?.metrics?.genome_version ?? 1})
          </text>

          {/* Plasmide */}
          <g className={selClass('plasmids')} onClick={() => onSelect('plasmids')}>
            <circle cx="310" cy="316" r="14" fill="none" stroke="#a78bfa" strokeWidth="3" />
            <circle cx="344" cy="328" r="11" fill="none" stroke="#c4b5fd" strokeWidth="2.5" />
            <text x="326" y="352" fontSize="9.5" textAnchor="middle" fill="#ddd6fe" fontWeight="600">
              Plasmide ({snapshot.plasmids.filter((p) => p.installed).length} aktiv)
            </text>
          </g>

          {/* mRNA-Pfad vom Chromosom zum 70S-Ribosom */}
          <path
            d="M 418 258 Q 456 242 496 260"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.8"
            className={`flow-path ${selClass('mrna')}`}
            onClick={() => onSelect('mrna')}
          />
          <text x="455" y="236" fontSize="9.5" textAnchor="middle" fill="#7dd3fc" className={selClass('mrna')} onClick={() => onSelect('mrna')}>
            mRNA ({snapshot.active_mrna.length})
          </text>

          {/* 70S-Ribosom (50S oben + 30S unten + tRNA + rRNA) */}
          <g className={selClass('ribosome_70s')} onClick={() => onSelect('ribosome_70s')}>
            <ellipse
              cx="535"
              cy="252"
              rx="34"
              ry="20"
              fill="#0f766e"
              stroke="#2dd4bf"
              strokeWidth="2"
              className={selClass('subunit_50s')}
              onClick={(e) => {
                e.stopPropagation();
                onSelect('subunit_50s');
              }}
            />
            <text x="535" y="255" fontSize="9.5" textAnchor="middle" fill="#ccfbf1" fontWeight="700">50S</text>

            <ellipse
              cx="535"
              cy="279"
              rx="28"
              ry="14"
              fill="#0369a1"
              stroke="#38bdf8"
              strokeWidth="2"
              className={selClass('subunit_30s')}
              onClick={(e) => {
                e.stopPropagation();
                onSelect('subunit_30s');
              }}
            />
            <text x="535" y="283" fontSize="9.5" textAnchor="middle" fill="#e0f2fe" fontWeight="700">30S</text>

            <text x="535" y="305" fontSize="9.5" textAnchor="middle" fill="#5eead4" fontWeight="600">
              70S-Ribosom
            </text>
          </g>
          {/* tRNA & rRNA */}
          <g className={selClass('trna')} onClick={() => onSelect('trna')}>
            <circle cx="496" cy="287" r="8" fill="#134e4a" stroke="#5eead4" strokeWidth="1.5" />
            <text x="496" y="290" fontSize="7.5" textAnchor="middle" fill="#99f6e4">tRNA</text>
          </g>
          <g className={selClass('rrna')} onClick={() => onSelect('rrna')}>
            <circle cx="574" cy="264" r="8" fill="#1e3a8a" stroke="#93c5fd" strokeWidth="1.5" />
            <text x="574" y="267" fontSize="7.5" textAnchor="middle" fill="#dbeafe">rRNA</text>
          </g>
        </g>

        {/* ============================================================ */}
        {/* STOFFWECHSEL, MIKROKOMPARTIMENTE & SPEICHER-GRANULA */}
        {/* ============================================================ */}
        <g opacity={dimIf('metabolism')}>
          {/* Carboxysom, Metabolosom, Encapsulin (BMCs) */}
          <g className={selClass('carboxysomes')} onClick={() => onSelect('carboxysomes')}>
            <polygon points="620,210 644,224 644,250 620,264 596,250 596,224" fill="#064e3b" stroke="#10b981" strokeWidth="2" />
            <text x="620" y="236" fontSize="8.5" textAnchor="middle" fill="#a7f3d0" fontWeight="700">Carboxy-</text>
            <text x="620" y="246" fontSize="8.5" textAnchor="middle" fill="#a7f3d0" fontWeight="700">som</text>
          </g>
          <g className={selClass('metabolosomes')} onClick={() => onSelect('metabolosomes')}>
            <polygon points="668,255 688,267 688,289 668,301 648,289 648,267" fill="#422006" stroke="#f59e0b" strokeWidth="2" />
            <text x="668" y="281" fontSize="8" textAnchor="middle" fill="#fde68a" fontWeight="700">Metab.</text>
          </g>
          <g className={selClass('encapsulins')} onClick={() => onSelect('encapsulins')}>
            <circle cx="622" cy="306" r="19" fill="#2e1065" stroke="#a78bfa" strokeWidth="2" />
            <text x="622" y="309" fontSize="8" textAnchor="middle" fill="#ede9fe" fontWeight="700">Encaps.</text>
          </g>

          {/* Thylakoide + Phycobilisomen */}
          <g className={selClass('thylakoids')} onClick={() => onSelect('thylakoids')}>
            <path d="M 272 182 Q 330 168 388 182" fill="none" stroke="#10b981" strokeWidth="4" />
            <path d="M 282 192 Q 330 179 378 192" fill="none" stroke="#34d399" strokeWidth="3" />
            <text x="330" y="168" fontSize="9.5" textAnchor="middle" fill="#6ee7b7">Thylakoide (SEO)</text>
          </g>
          <g className={selClass('phycobilisomes')} onClick={() => onSelect('phycobilisomes')}>
            <circle cx="294" cy="176" r="5" fill="#2dd4bf" />
            <circle cx="362" cy="176" r="5" fill="#2dd4bf" />
          </g>

          {/* Magnetosomen & Gasvesikel */}
          <g className={selClass('magnetosomes')} onClick={() => onSelect('magnetosomes')}>
            {[0, 1, 2, 3].map((i) => (
              <rect key={i} x={410 + i * 11} y="176" width="8" height="8" rx="1.5" fill="#38bdf8" stroke="#e0f2fe" strokeWidth="0.8" />
            ))}
            <text x="430" y="170" fontSize="9" textAnchor="middle" fill="#bae6fd">Magnetosomen</text>
          </g>
          <g className={selClass('gas_vesicles')} onClick={() => onSelect('gas_vesicles')}>
            <ellipse cx="556" cy="186" rx="16" ry="8" fill="rgba(186,230,253,0.18)" stroke="#7dd3fc" strokeWidth="1.8" />
            <text x="556" y="172" fontSize="9" textAnchor="middle" fill="#bae6fd">Gasvesikel</text>
          </g>

          {/* Elektronentransportkette & ATP-Synthase in der Plasmamembran unten */}
          <g className={selClass('etc')} onClick={() => onSelect('etc')}>
            <rect x="338" y="384" width="110" height="22" rx="7" fill="#065f46" stroke="#34d399" strokeWidth="1.8" />
            <text x="393" y="399" fontSize="9.5" textAnchor="middle" fill="#ecfdf5" fontWeight="700">
              ETC (Marge)
            </text>
          </g>
          <g className={selClass('atp_synthase')} onClick={() => onSelect('atp_synthase')}>
            <circle cx="490" cy="395" r={16 + atpRatio * 5} fill="#059669" stroke="#a7f3d0" strokeWidth="2.5" />
            <text x="490" y="398" fontSize="9.5" textAnchor="middle" fill="#ffffff" fontWeight="800">
              ATP {snapshot.ledger.atp_balance.toFixed(0)}
            </text>
          </g>

          {/* 4 Speicher-Granula mit Live-Füllstand */}
          {[
            { id: 'phb_reserve', x: 392, y: 344, label: 'PHB', fill: phbFill, color: '#f59e0b' },
            { id: 'glycogen_cache', x: 454, y: 344, label: 'Glyko', fill: glycoHit, color: '#22d3ee' },
            { id: 'volutin_pool', x: 526, y: 344, label: 'Volutin', fill: volutinFill, color: '#a78bfa' },
            { id: 'sulfur_buffer', x: 588, y: 344, label: 'Schwefel', fill: sulfurFill, color: '#eab308' },
          ].map((g) => (
            <g key={g.id} className={selClass(g.id)} onClick={() => onSelect(g.id)}>
              <circle cx={g.x} cy={g.y} r="17" fill="#09111f" stroke={g.color} strokeWidth="2" />
              <circle cx={g.x} cy={g.y} r={Math.max(3, 15 * Math.min(1, g.fill))} fill={g.color} fillOpacity="0.45" />
              <text x={g.x} y={g.y + 3} fontSize="8.5" textAnchor="middle" fill="#f8fafc" fontWeight="700">{g.label}</text>
            </g>
          ))}
        </g>

        {/* ============================================================ */}
        {/* SEKRETIONSSYSTEME (Produkt-Export rechts) */}
        {/* ============================================================ */}
        <g opacity={dimIf('motility')}>
          <g className={selClass('secretion_systems')} onClick={() => onSelect('secretion_systems')}>
            <rect x="708" y="210" width="66" height="32" rx="7" fill="#065f46" stroke="#10b981" strokeWidth="2" />
            <text x="741" y="230" fontSize="9.5" textAnchor="middle" fill="#ecfdf5" fontWeight="700">SEKRETION</text>
            <path d="M 776 226 L 945 226" stroke="#10b981" strokeWidth="3" className="flow-path" />
            <text x="860" y="214" fontSize="10.5" textAnchor="middle" fill="#6ee7b7" fontWeight="700">
              Produkte → Kunden
            </text>
          </g>
        </g>

        {/* ============================================================ */}
        {/* ENDOSPOREN-SCHUTZMANTEL BEI RUHEZUSTAND */}
        {/* ============================================================ */}
        <g opacity={isDormant ? 1 : dimIf('dormancy')}>
          {isDormant && (
            <rect
              x="265"
              y="165"
              width="450"
              height="210"
              rx="105"
              fill="rgba(109, 40, 217, 0.24)"
              stroke="#c4b5fd"
              strokeWidth="4"
              strokeDasharray="10 5"
              className={selClass('endospores')}
              onClick={() => onSelect('endospores')}
            />
          )}
          <g className={selClass('endospores')} onClick={() => onSelect('endospores')}>
            <rect x="652" y="160" width="84" height="26" rx="8" fill="#1e1b4b" stroke="#a78bfa" />
            <text x="694" y="177" fontSize="9.5" textAnchor="middle" fill="#ddd6fe" fontWeight="600">
              {isDormant ? 'ENDOSPORE' : 'Sporen-Kern'}
            </text>
          </g>
        </g>
      </svg>
    </div>
  );
};
