#!/usr/bin/env python3
"""Turn a source photo into responsive WebP files for the site.

Usage:
    python3 tools/optimize_images.py path/to/photo.jpg my-project-cover [more pairs...]

Writes site/assets/img/<name>-<width>.webp at up to four widths and records the
image in src/images.json so build.py can emit srcset/width/height automatically.
Then reference it in a page with {{img:my-project-cover|Alt text}} or in projects.json.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "assets" / "img"
MANIFEST = ROOT / "src" / "images.json"
WIDTHS = (480, 960, 1600)


def optimize(src, name, manifest):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    widths = [x for x in WIDTHS if x < w] + [min(w, WIDTHS[-1])]
    widths = sorted(set(widths))
    for tw in widths:
        th = round(h * tw / w)
        im.resize((tw, th), Image.LANCZOS).save(OUT / f"{name}-{tw}.webp", "WEBP", quality=78, method=6)
    manifest[name] = {"w": widths[-1], "h": round(h * widths[-1] / w), "widths": widths}


def main(args):
    if not args or len(args) % 2:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for src, name in zip(args[::2], args[1::2]):
        optimize(src, name, manifest)
        print("ok", name, manifest[name]["widths"])
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
