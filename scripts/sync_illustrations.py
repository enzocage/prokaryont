"""Synchronisiert und verifiziert erzeugte Illustrationen aus dem Artifact-Ordner nach docs/illustrations/fig_XX.png."""

from __future__ import annotations

import re
from pathlib import Path
from PIL import Image


ARTIFACT_DIR = Path(
    r"C:\Users\enzoc\.gemini\antigravity\brain\e44c27a2-8bc3-46e5-9a14-cd370a78a065"
)
TARGET_DIR = Path(__file__).resolve().parents[1] / "docs" / "illustrations"


def sync_all() -> list[int]:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"^fig_(\d{2})_.*\.(png|jpe?g|webp)$", re.IGNORECASE)
    found: dict[int, Path] = {}

    for p in ARTIFACT_DIR.iterdir():
        if not p.is_file():
            continue
        m = pattern.match(p.name)
        if not m:
            continue
        idx = int(m.group(1))
        prev = found.get(idx)
        if prev is None or p.stat().st_mtime > prev.stat().st_mtime:
            found[idx] = p

    verified: list[int] = []
    for idx in sorted(found):
        src = found[idx]
        dst = TARGET_DIR / f"fig_{idx:02d}.png"
        with Image.open(src) as im:
            im.verify()
        with Image.open(src) as im:
            rgb = im.convert("RGB")
            # Sanfte einheitliche Breite 1376px für kompaktes, gestochen scharfes .docx
            if rgb.width > 1440:
                new_h = int(round(rgb.height * (1408 / rgb.width)))
                rgb = rgb.resize((1408, new_h), Image.Resampling.LANCZOS)
            rgb.save(dst, format="PNG", optimize=True)
        with Image.open(dst) as check_im:
            check_im.verify()
        verified.append(idx)

    missing = [i for i in range(1, 51) if i not in verified]
    print(f"Verifiziert: {len(verified)}/50 -> {verified}")
    print(f"Ausstehend: {len(missing)} -> {missing}")
    return verified


if __name__ == "__main__":
    sync_all()
