#!/usr/bin/env python3
"""Create the 1200x630 link-preview image for each project page from its cover photo.

    python3 tools/make_og.py

Run after adding or changing a project in src/projects.json. build.py picks up
site/assets/og/portfolio_<slug>.jpg automatically and falls back to assets/og.jpg.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = json.loads((ROOT / "src" / "images.json").read_text())
OUT = ROOT / "site" / "assets" / "og"
OUT.mkdir(parents=True, exist_ok=True)
for p in json.loads((ROOT / "src" / "projects.json").read_text()):
    cover = p["cover"]
    src = ROOT / "site" / "assets" / "img" / f"{cover}-{IMAGES[cover]['widths'][-1]}.webp"
    ImageOps.fit(Image.open(src).convert("RGB"), (1200, 630), Image.LANCZOS).save(
        OUT / f"portfolio_{p['slug']}.jpg", "JPEG", quality=82, optimize=True)
    print("ok", p["slug"])
