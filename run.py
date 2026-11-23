"""Single-Command Launcher für das PROKARYONT Bio-Tech Observatory."""

from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

# Sicherstellen, dass src/ im Pfad liegt, falls ohne `pip install -e .` gestartet wird
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Startet PROKARYONT (Backend + interaktives Bio-Tech Observatory)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind-Host (Standard: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP-Port (Standard: 8000)")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Browser beim Start nicht automatisch öffnen.",
    )
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print("=" * 68)
    print("  PROKARYONT — Wirtschaftlicher Prokaryont & Gärtner-Observatorium")
    print(f"  Server läuft auf: {url}")
    print(f"  API-Status:       {url}/api/state")
    print("=" * 68)

    if not args.no_browser:

        def _open_delayed() -> None:
            time.sleep(1.1)
            webbrowser.open(url)

        threading.Thread(target=_open_delayed, daemon=True).start()

    uvicorn.run(
        "prokaryont.api.server:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
