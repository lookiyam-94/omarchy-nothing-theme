#!/usr/bin/env python3
"""Build the Nothing theme for Vivaldi.

Vivaldi is not themed by Omarchy, so this packs the palette into a theme
archive Vivaldi can import: Settings > Themes > Import Theme...

The colours are read from colors.toml, so the browser follows the palette
rather than keeping its own copy. Same discipline as the desktop: grey
chrome, and red spent on one thing — the highlight.

A Vivaldi theme carries one Start Page image. The shipped theme uses the
shell prompt; any other background in --background becomes its own
theme, named after it.

    python3 tools/build-vivaldi.py                         # vivaldi/nothing.zip
    python3 tools/build-vivaldi.py --background 01-glyph   # another Start Page
    python3 tools/build-vivaldi.py --background none       # flat ground
"""

import argparse
import json
import os
import tomllib
import uuid
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Theme IDs are derived from the name, so re-importing a rebuilt archive is
# recognisably the same theme.
ID_NAMESPACE = uuid.UUID("6e6f7468-696e-4700-8000-d71921000000")


# The background the shipped theme is built with, under the plain name.
DEFAULT_BACKGROUND = "10-prompt"


def build(c, background, out):
    """Write one theme archive; background is a backgrounds/ name or 'none'."""
    path = ""
    title = "Nothing"
    if background != "none":
        stem = background.removesuffix(".png")
        path = os.path.join(ROOT, "backgrounds", stem + ".png")
        if not os.path.isfile(path):
            raise SystemExit(f"no such background: backgrounds/{stem}.png")
        if stem != DEFAULT_BACKGROUND:
            # "01-glyph" -> "Nothing · Glyph"
            title = "Nothing · " + stem.split("-", 1)[-1].replace("-", " ").title()

    settings = {
        "accentFromPage": False,  # pages never tint the chrome
        "accentOnWindow": True,
        "accentSaturationLimit": 1,
        "alpha": 1,
        "backgroundImage": "background.png" if path else "",
        "backgroundPosition": "stretch",
        "blur": 0,
        "colorAccentBg": c["background"],  # tab bar: the desktop's ground
        "colorBg": c["lighter_background"],  # toolbars, panels, address field
        "colorFg": c["foreground"],
        "colorHighlightBg": c["accent"],  # the one red signal
        "colorPosition": "unified",
        "colorWindowBg": c["background"],
        "contrast": 0,  # higher draws light strokes around the chrome
        "dimBlurred": False,
        "engineVersion": 1,
        "id": str(uuid.uuid5(ID_NAMESPACE, title)),
        "name": title,
        "preferSystemAccent": False,
        "radius": 4,
        "simpleScrollbar": True,
        "transparencyTabBar": False,
        "transparencyTabs": False,
        "url": "",
        "version": 1,
    }

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("settings.json", json.dumps(settings, indent=2) + "\n")
        if path:
            z.write(path, "background.png")
    print(f"  {os.path.relpath(out, ROOT)}  {title}  {os.path.getsize(out) // 1024} KB")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--background",
        nargs="+",
        default=[DEFAULT_BACKGROUND],
        help=f"Start Page images from backgrounds/, by name, or 'none' (default {DEFAULT_BACKGROUND})",
    )
    p.add_argument("--out", default=os.path.join(ROOT, "vivaldi"), help="output dir")
    args = p.parse_args()

    with open(os.path.join(ROOT, "colors.toml"), "rb") as f:
        c = tomllib.load(f)

    os.makedirs(args.out, exist_ok=True)
    for background in args.background:
        stem = background.removesuffix(".png")
        name = "nothing-flat" if stem == "none" else "nothing" if stem == DEFAULT_BACKGROUND else "nothing-" + stem.split("-", 1)[-1]
        build(c, background, os.path.join(args.out, name + ".zip"))


if __name__ == "__main__":
    main()
