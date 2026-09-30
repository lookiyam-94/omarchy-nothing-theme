#!/usr/bin/env python3
"""Generate the Nothing backgrounds.

Every wallpaper in this theme is drawn, not photographed. The vocabulary is
Nothing's own: dot matrices, halftones, the Phone (1) glyph strips, exposed
hardware. Flat geometry on a near-black ground, white ink, one red accent —
which is why twelve 4K images come to about 1 MB and carry no image rights.

    pip install pillow
    python3 tools/generate-backgrounds.py                 # default ground
    python3 tools/generate-backgrounds.py --ground 141414 # match the UI
    python3 tools/generate-backgrounds.py --only glyph sphere

Sizes are 3840x2400 (16:10). Pass --size WxH for another panel.
"""

import argparse
import math
import os

from PIL import Image, ImageDraw

INK = (237, 237, 237)
RED = (215, 25, 33)


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


class Canvas:
    def __init__(self, w, h, ground):
        self.w, self.h, self.ground = w, h, ground

    def new(self, colour=None):
        img = Image.new("RGB", (self.w, self.h), colour or self.ground)
        return img, ImageDraw.Draw(img, "RGBA")


# --- 01 ----------------------------------------------------------------
def dot_matrix(c):
    """Uniform dot grid with one red dot off-centre."""
    img, d = c.new()
    step, r = 48, 4.2
    for y in range(step, c.h, step):
        for x in range(step, c.w, step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 46))
    cx = step * (c.w // step // 2 + 7)
    cy = step * (c.h // step // 2 - 5)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED)
    return img


# --- 02 ----------------------------------------------------------------
def glyph(c):
    """The Phone (1) light-strip arrangement."""
    img, d = c.new()
    cx, cy, lw = c.w / 2, c.h / 2, 22
    d.arc([cx - 980, cy - 780, cx - 300, cy - 100], 95, 350, fill=INK, width=lw)
    d.rounded_rectangle([cx - 30, cy - 700, cx + 30, cy + 220], radius=30, fill=INK)
    d.line([cx + 260, cy - 660, cx + 760, cy - 300], fill=INK, width=lw)
    d.ellipse([cx + 330, cy - 40, cx + 930, cy + 560], outline=INK, width=lw)
    d.rounded_rectangle([cx - 900, cy + 280, cx - 420, cy + 312], radius=16, fill=INK)
    d.rounded_rectangle([cx - 900, cy + 420, cx - 640, cy + 452], radius=16, fill=INK)
    d.rounded_rectangle([cx - 560, cy + 420, cx - 420, cy + 452], radius=16, fill=RED)
    return img


# --- 03 ----------------------------------------------------------------
def dot_gradient(c):
    """Halftone bloom — the transparent-shell feel."""
    img, d = c.new()
    step = 38
    cx, cy = c.w * 0.58, c.h * 0.44
    maxd = math.hypot(c.w, c.h) * 0.52
    for y in range(step, c.h, step):
        for x in range(step, c.w, step):
            t = max(0.0, 1.0 - math.hypot(x - cx, y - cy) / maxd) ** 1.6
            r = 1.2 + t * 9.5
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(30 + t * 205)))
    return img


# --- 04 ----------------------------------------------------------------
def red_dot(c):
    """Pure black, one red dot. Nothing, literally."""
    img, d = c.new((0, 0, 0))
    cx, cy = c.w / 2, c.h / 2
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=RED)
    return img


# --- 05 ----------------------------------------------------------------
def rings(c):
    """Concentric dot rings — the camera motif."""
    img, d = c.new()
    cx, cy = c.w / 2, c.h / 2
    for i, ring in enumerate(range(3, 40, 2)):
        rad = ring * 58
        n = max(30, int(rad / 16))
        t = max(0.0, 1.0 - i / 19.0)
        s, a = 1.4 + t * 5.0, int(36 + t * 200)
        for k in range(n):
            ang = 2 * math.pi * k / n + ring * 0.11
            x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
            if -60 < x < c.w + 60 and -60 < y < c.h + 60:
                d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, a))
    d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=RED)
    return img


# --- 06 ----------------------------------------------------------------
def coil(c):
    """Wireless-charging coil, with a lead-out trace to the pad edge."""
    img, d = c.new()
    cx, cy, pad = c.w / 2, c.h / 2, 900
    d.rounded_rectangle(
        [cx - pad, cy - pad, cx + pad, cy + pad], radius=130, outline=(54, 54, 54), width=7
    )
    turns, r0, r1 = 14, 70, 720
    steps = turns * 260
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a, r = t * turns * 2 * math.pi, r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(pts, fill=INK, width=9, joint="curve")
    ex, ey = pts[-1]
    d.line([(ex, ey), (cx + pad - 60, ey)], fill=INK, width=9)
    d.line([(cx + pad - 60, ey), (cx + pad - 60, cy + pad - 60)], fill=INK, width=9)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=RED)
    return img


# --- 07 ----------------------------------------------------------------
def sphere(c):
    """Halftone-shaded orb — dot radius tracks a simple lambert term."""
    img, d = c.new()
    cx, cy, R = c.w * 0.5, c.h * 0.47, 760
    step = 26
    lx, ly, lz = -0.45, -0.62, 0.65
    y = cy - R
    while y <= cy + R:
        x = cx - R
        while x <= cx + R:
            dx, dy = (x - cx) / R, (y - cy) / R
            s = dx * dx + dy * dy
            if s <= 1.0:
                dz = math.sqrt(1.0 - s)
                b = max(0.0, dx * lx + dy * ly + dz * lz) ** 0.85
                r = 1.0 + b * (step * 0.52)
                if r > 0.7:
                    d.ellipse(
                        [x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(60 + b * 195))
                    )
            x += step
        y += step
    d.ellipse([cx - R - 90, cy - R - 90, cx + R + 90, cy + R + 90], outline=(40, 40, 40), width=6)
    return img


# --- 08 ----------------------------------------------------------------
GLYPHS = {
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
}


def dot_type(c, word="NOTHING"):
    """The wordmark set in a 5x7 matrix, snapped to the ground grid."""
    img, d = c.new()
    g = 48
    for y in range(g, c.h, g):
        for x in range(g, c.w, g):
            d.ellipse([x - 2.6, y - 2.6, x + 2.6, y + 2.6], fill=(255, 255, 255, 26))
    cell, r = g, 13.0
    wpx = (sum(len(GLYPHS[ch][0]) for ch in word) + len(word) - 1) * cell
    ox = round(((c.w - wpx) / 2) / cell) * cell
    oy = round((c.h * 0.5 - 3.5 * cell) / cell) * cell
    px = ox
    for ch in word:
        rows = GLYPHS[ch]
        for ry, row in enumerate(rows):
            for rx, cellchar in enumerate(row):
                if cellchar == "#":
                    X, Y = px + rx * cell, oy + ry * cell
                    d.ellipse([X - r, Y - r, X + r, Y + r], fill=INK)
        px += (len(rows[0]) + 1) * cell
    d.ellipse([px - r, oy + 6 * cell - r, px + r, oy + 6 * cell + r], fill=RED)
    return img


# --- 09 ----------------------------------------------------------------
def sequence(c):
    """Glyph-composer light bars, the centre one struck red."""
    img, d = c.new()
    n, gap, bw = 13, 46, 92
    heights = [0.16, 0.34, 0.22, 0.62, 0.44, 0.86, 1.0, 0.78, 0.52, 0.30, 0.66, 0.24, 0.14]
    total = n * bw + (n - 1) * gap
    x, cy = (c.w - total) / 2, c.h / 2
    for i in range(n):
        h = heights[i] * 760
        d.rounded_rectangle(
            [x, cy - h / 2, x + bw, cy + h / 2], radius=bw / 2, fill=RED if i == 6 else INK
        )
        x += bw + gap
    return img


# --- 10 ---------------------------------------------------------------
def exposed(c):
    """The transparent back as schematic — screws and traces."""
    img, d = c.new()
    trace = (52, 52, 52)
    nodes = [
        (0.22, 0.30, 150),
        (0.62, 0.22, 96),
        (0.80, 0.52, 190),
        (0.30, 0.70, 120),
        (0.56, 0.78, 74),
        (0.44, 0.46, 230),
    ]
    pts = [(c.w * a, c.h * b) for a, b, _ in nodes]
    for i, j in zip([0, 1, 5, 2, 4, 3], [1, 5, 2, 4, 3, 0]):
        d.line([pts[i], pts[j]], fill=trace, width=7)
    for a, b, rr in nodes:
        X, Y = c.w * a, c.h * b
        d.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=INK, width=9)
        d.ellipse(
            [X - rr * 0.42, Y - rr * 0.42, X + rr * 0.42, Y + rr * 0.42], outline=INK, width=7
        )
        for k in range(6):
            ang = k * math.pi / 3
            d.line(
                [
                    X + rr * 0.42 * math.cos(ang),
                    Y + rr * 0.42 * math.sin(ang),
                    X + rr * math.cos(ang),
                    Y + rr * math.sin(ang),
                ],
                fill=INK,
                width=4,
            )
    X, Y = c.w * 0.44, c.h * 0.46
    d.ellipse([X - 26, Y - 26, X + 26, Y + 26], fill=RED)
    return img


# --- 11 ---------------------------------------------------------------
def diagonal(c):
    """Dot rulings on the bias, one struck solid red."""
    img, d = c.new()
    spacing, ang = 72, math.radians(-35)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    L = int(math.hypot(c.w, c.h)) + 400
    n = int(L / spacing) + 2
    for li in range(-n, n + 1):
        bx, by = c.w / 2 + nx * li * spacing, c.h / 2 + ny * li * spacing
        for t in range(-L // 2, L // 2, 36):
            x, y = bx + dx * t, by + dy * t
            if -40 < x < c.w + 40 and -40 < y < c.h + 40:
                d.ellipse([x - 5.2, y - 5.2, x + 5.2, y + 5.2], fill=(255, 255, 255, 95))
    bx, by = c.w / 2 + nx * -5 * spacing, c.h / 2 + ny * -5 * spacing
    d.line([(bx - dx * L, by - dy * L), (bx + dx * L, by + dy * L)], fill=RED, width=13)
    return img


# --- 12 ---------------------------------------------------------------
def horizon(c):
    """Halftone density falling to a hard red rule."""
    img, d = c.new()
    step, hz, span = 32, c.h * 0.5, c.h * 0.46
    for y in range(step, c.h, step):
        t = max(0.0, 1.0 - abs(y - hz) / span) ** 1.7
        for x in range(step, c.w, step):
            r = 0.8 + t * 9.0
            if r > 0.7:
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(18 + t * 225)))
    d.rectangle([0, hz - 4, c.w, hz + 4], fill=RED)
    return img


PLATES = [
    ("01-dot-matrix", dot_matrix),
    ("02-glyph", glyph),
    ("03-dot-gradient", dot_gradient),
    ("04-red-dot", red_dot),
    ("05-rings", rings),
    ("06-coil", coil),
    ("07-sphere", sphere),
    ("08-dot-type", dot_type),
    ("09-sequence", sequence),
    ("10-exposed", exposed),
    ("11-diagonal", diagonal),
    ("12-horizon", horizon),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ground", default="0a0a0a", help="background hex (default 0a0a0a)")
    p.add_argument("--size", default="3840x2400", help="WxH (default 3840x2400)")
    p.add_argument("--out", default=None, help="output dir (default ../backgrounds)")
    p.add_argument("--only", nargs="*", help="generate only these (substring match)")
    args = p.parse_args()

    w, h = (int(v) for v in args.size.lower().split("x"))
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backgrounds")
    os.makedirs(out, exist_ok=True)
    canvas = Canvas(w, h, hex_rgb(args.ground))

    for name, fn in PLATES:
        if args.only and not any(k in name for k in args.only):
            continue
        img = fn(canvas)
        path = os.path.join(out, name + ".png")
        img.save(path, optimize=True)
        print(f"  {name}.png  {os.path.getsize(path) // 1024} KB")


if __name__ == "__main__":
    main()
