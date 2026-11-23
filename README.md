# PROKARYONT — Selbstregulierender Wirtschaftlicher Agenten-Organismus

Ein lauffähiger, kausal geschlossener digitaler Wirtschaftsorganismus nach dem exakten Vorbild einer prokaryotischen Zelle (**Nutzpflanze & Gärtner**), inkl. interaktiver **Bio-Tech Dark Observatory** Web-App, adaptivem Hybrid-Genom (Operons + AST-sandboxed Python-Plasmide), Endosporen-Ruhesystem, FtsZ-Ernte und quantitativem **Ingenieur-vs.-Gärtner-Benchmark**.

## Schnellstart

Einmalige Einrichtung nach einem frischen Clone (Python `>= 3.12` und Node.js):

```bash
pip install -e ".[dev]"
cd frontend && npm install && npm run build && cd ..
```

Starten mit einem Befehl:

```bash
python run.py
```

Anschließend öffnet sich das Observatorium automatisch unter [http://127.0.0.1:8000](http://127.0.0.1:8000).  
Für headless/Server-Start ohne automatischen Browser-Tab:

```bash
python run.py --port 8000 --no-browser
```

## Tests & Ökonomischer Machbarkeitsbeweis

```bash
pytest -v
```

Prüft u. a.:
- Exakte 57-Strukturen-Registry (53 aktive Module/Submodule + 4 begründete Redundanzen) + 7 Viability-Module
- Kausale Genexpression (`BacterialChromosome` → `mRNA` → `70S-Ribosom`) und AST-Sandbox-Sicherheit gegen schädlichen Plasmid-Code
- 180-Tage-Profitabilität über beide Saatgut-Templates (`b2b_briefing`, `micro_api`) und alle 3 Skalen (`nano` 100 €, `solopreneur` 1.000 €, `growth` 10.000 €)
- Dürre-Überleben per Endospore (`~93 %` Fixkosten-Reduktion) + anschließende Keimung
- Quantitative Überlegenheit des Gärtner-Modells gegenüber dem klassischen Ingenieurs-Kontrollmodell

## Projektstruktur

- `src/prokaryont/registry.py` — Kanonische 57+7-Matrix mit Bio- & Wirtschafts-Analogien
- `src/prokaryont/genetics/` — `Nucleoid`, `BacterialChromosome`, `MutationEngine`, `MessengerRNA`, `Ribosome70S` (`30S`/`50S`/`tRNA`/`rRNA`) & AST-sandboxed `CodePlasmid`s
- `src/prokaryont/organelles/` — Alle 8 biologischen Organsysteme (`envelope`, `cytoskeleton`, `motility`, `metabolism`, `storage`, `dormancy`, `secretion`)
- `src/prokaryont/viability/` — `DoubleEntryLedger`, `PricingEngine`, `QualityGate`, `ComplianceGuard`, `CustomerLifecycleManager`, `RunwayCircuitBreaker`, `GardenerInterface` & `EngineerControlBaseline`
- `src/prokaryont/environment/` — Realistische Marktumwelt, Schocks & Produkt-Synthese (`b2b_briefing`, `micro_api`)
- `src/prokaryont/adapters/` — Plug-in-Adapter für LLMs (Offline-Hybrid + Gemini/OpenAI) & Payment (Lokal + Stripe)
- `src/prokaryont/api/server.py` — FastAPI REST- & WebSocket-Server
- `frontend/` — React + TypeScript + Vite Bio-Tech Dark Observatory UI
- `docs/ARCHITEKTUR_HANDBUCH.md` — Ausführliches Handbuch mit Mermaid-Diagrammen, 57er-Matrix und Paradigmenwechsel-Essay
