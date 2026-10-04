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


# --- 13 ---------------------------------------------------------------
def grid_fade(c):
    """Dot grid thinning from the top down — a vertical falloff, not radial."""
    img, d = c.new()
    step = 42
    for y in range(step, c.h, step):
        t = (1.0 - y / c.h) ** 1.4
        r = 1.0 + t * 6.5
        a = int(20 + t * 190)
        if r <= 0.7:
            continue
        for x in range(step, c.w, step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    d.ellipse([c.w * 0.5 - 12, c.h * 0.18 - 12, c.w * 0.5 + 12, c.h * 0.18 + 12], fill=RED)
    return img


# --- 14 ---------------------------------------------------------------
def aperture(c):
    """Camera iris — seven blade circles offset from centre, leaving the opening.

    Each blade is a circle of radius Rb whose centre sits d from the axis, with
    Rb < d so none reaches the middle; the hole they leave is the aperture.
    Seven blades rather than six: an odd count cannot land on the symmetric
    six-point star that evenly spaced chords produce.
    """
    img, d = c.new()
    cx, cy = c.w / 2, c.h / 2
    blades, dist, Rb = 7, 760, 640
    for i in range(blades):
        a = 2 * math.pi * i / blades
        bx, by = cx + dist * math.cos(a), cy + dist * math.sin(a)
        d.ellipse([bx - Rb, by - Rb, bx + Rb, by + Rb], outline=INK, width=9)
    d.ellipse([cx - 1040, cy - 1040, cx + 1040, cy + 1040], outline=(44, 44, 44), width=7)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=RED)
    return img


# --- 15 ---------------------------------------------------------------
def orbit(c):
    """One thin ring, one red body on it, and the dotted path it travels."""
    img, d = c.new()
    cx, cy, R = c.w * 0.5, c.h * 0.5, 720
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=8)
    R2 = R * 1.34
    n = 150
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = cx + R2 * math.cos(a), cy + R2 * math.sin(a)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 60))
    a = math.radians(-38)
    bx, by = cx + R * math.cos(a), cy + R * math.sin(a)
    d.ellipse([bx - 30, by - 30, bx + 30, by + 30], fill=RED)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255, 120))
    return img


# --- 16 ---------------------------------------------------------------
def strata(c):
    """Horizontal bands, each a ruling of dots at its own density."""
    img, d = c.new()
    densities = [0.18, 0.45, 0.26, 0.8, 0.36, 1.0, 0.55, 0.22, 0.68, 0.3]
    band = c.h / len(densities)
    for bi, dens in enumerate(densities):
        # Each band is a stack of three rulings so it reads as a layer, not a line.
        for sub in (-1, 0, 1):
            y = band * (bi + 0.5) + sub * 26
            step = int(20 + (1.0 - dens) * 74)
            r = 2.4 + dens * 5.4
            a = int(45 + dens * 200) - abs(sub) * 55
            for x in range(step, c.w, step):
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, max(12, a)))
    y = band * 5.5
    d.rounded_rectangle([c.w * 0.5 - 150, y - 8, c.w * 0.5 + 150, y + 8], radius=8, fill=RED)
    return img


# --- 17 ---------------------------------------------------------------
def reticle(c):
    """A measurement reticle — rules, ticks, one red centre."""
    img, d = c.new()
    cx, cy = c.w / 2, c.h / 2
    grey = (58, 58, 58)
    d.line([0, cy, c.w, cy], fill=grey, width=5)
    d.line([cx, 0, cx, c.h], fill=grey, width=5)
    for i in range(-18, 19):
        if i == 0:
            continue
        major = i % 5 == 0
        L = 46 if major else 22
        w = 6 if major else 4
        x = cx + i * 96
        if 0 < x < c.w:
            d.line([x, cy - L, x, cy + L], fill=INK if major else grey, width=w)
        y = cy + i * 96
        if 0 < y < c.h:
            d.line([cx - L, y, cx + L, y], fill=INK if major else grey, width=w)
    for rad in (240, 470, 700):
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=grey, width=4)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=RED)
    return img


# --- 18 ---------------------------------------------------------------
def weave(c):
    """Two dot rulings crossed on the bias — a lattice, not a stripe."""
    img, d = c.new()
    spacing = 88
    L = int(math.hypot(c.w, c.h)) + 400
    for sign in (1, -1):
        ang = math.radians(38 * sign)
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        n = int(L / spacing) + 2
        for li in range(-n, n + 1):
            bx = c.w / 2 + nx * li * spacing
            by = c.h / 2 + ny * li * spacing
            for t in range(-L // 2, L // 2, 40):
                x, y = bx + dx * t, by + dy * t
                if -40 < x < c.w + 40 and -40 < y < c.h + 40:
                    d.ellipse([x - 4.4, y - 4.4, x + 4.4, y + 4.4], fill=(255, 255, 255, 62))
    d.ellipse([c.w * 0.5 - 14, c.h * 0.5 - 14, c.w * 0.5 + 14, c.h * 0.5 + 14], fill=RED)
    return img


# --- 19 ---------------------------------------------------------------
def dial(c):
    """A watch face in dots — sixty minute marks, twelve hour bars, one red second."""
    img, d = c.new()
    cx, cy, R = c.w / 2, c.h / 2, 820
    for i in range(60):
        a = 2 * math.pi * i / 60 - math.pi / 2
        if i % 5 == 0:
            for k in range(4):
                rr = R - k * 30
                x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
                d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=INK)
        else:
            x, y = cx + R * math.cos(a), cy + R * math.sin(a)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, 90))
    a = 2 * math.pi * 37 / 60 - math.pi / 2
    x, y = cx + (R + 70) * math.cos(a), cy + (R + 70) * math.sin(a)
    d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=RED)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 255, 255, 140))
    return img


# --- 20 ---------------------------------------------------------------
def waveform(c):
    """An audio waveform as stacked dot columns, mirrored about the centre line."""
    img, d = c.new()
    step, r = 40, 7.0
    cy, cols = c.h / 2, int(c.w * 0.72 / step)
    x0 = (c.w - (cols - 1) * step) / 2
    peak = cols // 2 + 6
    for i in range(cols):
        t = i / (cols - 1)
        env = math.sin(math.pi * t) ** 1.3
        amp = env * (0.55 + 0.45 * abs(math.sin(t * 23.0) * math.cos(t * 7.3)))
        n = max(1, int(amp * 14))
        x = x0 + i * step
        for k in range(-n, n + 1):
            y = cy + k * step
            fade = 1.0 - abs(k) / (n + 1)
            fill = RED if i == peak else (255, 255, 255, int(50 + fade * 205))
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    return img


# --- 21 ---------------------------------------------------------------
def crescent(c):
    """The halftone orb lit from behind — only a rim of dots survives."""
    img, d = c.new()
    cx, cy, R = c.w * 0.5, c.h * 0.5, 820
    step = 24
    lx, ly, lz = 0.86, -0.38, -0.34
    y = cy - R
    while y <= cy + R:
        x = cx - R
        while x <= cx + R:
            dx, dy = (x - cx) / R, (y - cy) / R
            s = dx * dx + dy * dy
            if s <= 1.0:
                dz = math.sqrt(1.0 - s)
                b = max(0.0, dx * lx + dy * ly + dz * lz) ** 0.9
                r = b * (step * 0.5)
                if r > 0.8:
                    d.ellipse(
                        [x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(70 + b * 185))
                    )
            x += step
        y += step
    return img


# --- 22 ---------------------------------------------------------------
def viewfinder(c):
    """Four corner brackets framing nothing, and a red record dot."""
    img, d = c.new()
    cx, cy = c.w / 2, c.h / 2
    hw, hh, L, lw = 1180, 700, 170, 8
    for sx in (-1, 1):
        for sy in (-1, 1):
            X, Y = cx + sx * hw, cy + sy * hh
            d.line([(X, Y), (X - sx * L, Y)], fill=INK, width=lw)
            d.line([(X, Y), (X, Y - sy * L)], fill=INK, width=lw)
    d.ellipse([cx - hw + 40, cy - hh + 40, cx - hw + 72, cy - hh + 72], fill=RED)
    g = (60, 60, 60)
    d.line([cx - 40, cy, cx + 40, cy], fill=g, width=4)
    d.line([cx, cy - 40, cx, cy + 40], fill=g, width=4)
    return img


# --- 23 ---------------------------------------------------------------
def scatter(c):
    """A sparse field of dots at three sizes — night sky in a dot matrix."""
    import random

    rnd = random.Random(23)
    img, d = c.new()
    g = 48
    for y in range(g, c.h, g):
        for x in range(g, c.w, g):
            v = rnd.random()
            if v < 0.82:
                continue
            r, a = (2.2, 50) if v < 0.95 else (4.0, 130) if v < 0.99 else (7.0, 235)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    x, y = g * (c.w // g // 2 - 11), g * (c.h // g // 2 + 6)
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=RED)
    return img


# --- 24 ---------------------------------------------------------------
def phyllotaxis(c):
    """Golden-angle dot spiral, growing outward and fading at the edge."""
    img, d = c.new()
    cx, cy = c.w / 2, c.h / 2
    golden = math.pi * (3 - math.sqrt(5))
    n, k = 1400, 26.0
    for i in range(1, n):
        rad = k * math.sqrt(i)
        a = i * golden
        x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
        t = i / n
        r = 2.0 + 9.0 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.8
        alpha = int(255 * (1.0 - t) ** 0.7 + 30)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, min(255, alpha)))
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)
    return img


# --- 25 ---------------------------------------------------------------
def ripple(c):
    """A drop off-centre — dot size rides the wave and dies away with distance."""
    img, d = c.new()
    step = 34
    cx, cy = c.w * 0.38, c.h * 0.56
    for y in range(step, c.h, step):
        for x in range(step, c.w, step):
            dist = math.hypot(x - cx, y - cy)
            wave = 0.5 + 0.5 * math.cos(dist / 70.0)
            fall = math.exp(-dist / 1500.0)
            t = wave * fall
            r = 0.9 + t * 8.5
            if r > 1.0:
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(20 + t * 215)))
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=RED)
    return img


# --- 26 ---------------------------------------------------------------
def case(c):
    """Ear (1) case from above — a clear pill, two buds seated, one red stem."""
    img, d = c.new()
    cx, cy, hw, hh = c.w / 2, c.h / 2, 820, 560
    d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=hh, outline=INK, width=9)
    d.rounded_rectangle(
        [cx - hw + 60, cy - hh + 60, cx + hw - 60, cy + hh - 60],
        radius=hh - 60,
        outline=(56, 56, 56),
        width=5,
    )
    for sx, colour in ((-1, INK), (1, RED)):
        bx = cx + sx * 330
        d.ellipse([bx - 200, cy - 200, bx + 200, cy + 200], outline=INK, width=9)
        d.ellipse([bx - 70, cy - 70, bx + 70, cy + 70], outline=(80, 80, 80), width=6)
        d.rounded_rectangle([bx - 26, cy + 120, bx + 26, cy + 360], radius=26, fill=colour)
    return img


# --- 27 ---------------------------------------------------------------
def level(c):
    """An LED level meter — rows of segments, the last lit one struck red."""
    img, d = c.new()
    rows, segs, sw, sh, gx, gy = 7, 24, 86, 34, 22, 40
    lit = [9, 15, 21, 12, 18, 6, 14]
    total_w = segs * sw + (segs - 1) * gx
    total_h = rows * sh + (rows - 1) * gy
    x0, y0 = (c.w - total_w) / 2, (c.h - total_h) / 2
    for r in range(rows):
        y = y0 + r * (sh + gy)
        for s in range(segs):
            x = x0 + s * (sw + gx)
            if s < lit[r] - 1:
                fill = INK
            elif s == lit[r] - 1:
                fill = RED if r == 2 else INK
            else:
                fill = (40, 40, 40)
            d.rounded_rectangle([x, y, x + sw, y + sh], radius=sh / 2, fill=fill)
    return img


# --- 28 ---------------------------------------------------------------
def prompt(c):
    """A shell prompt in the 5x7 matrix — chevron, and a red cursor block."""
    img, d = c.new()
    g = 48
    for y in range(g, c.h, g):
        for x in range(g, c.w, g):
            d.ellipse([x - 2.6, y - 2.6, x + 2.6, y + 2.6], fill=(255, 255, 255, 22))
    chevron = ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."]
    cell, r = g * 2, 28.0
    ox = round((c.w / 2 - 5.5 * cell) / g) * g
    oy = round((c.h / 2 - 3 * cell) / g) * g
    for ry, row in enumerate(chevron):
        for rx, ch in enumerate(row):
            if ch == "#":
                X, Y = ox + rx * cell, oy + ry * cell
                d.ellipse([X - r, Y - r, X + r, Y + r], fill=INK)
    cx0 = ox + 8 * cell
    for ry in range(7):
        for rx in range(4):
            X, Y = cx0 + rx * cell, oy + ry * cell
            d.ellipse([X - r, Y - r, X + r, Y + r], fill=RED)
    return img


# --- 29 ---------------------------------------------------------------
def contour(c):
    """Topographic contours, traced in dots across a few soft hills."""
    img, d = c.new()
    hills = [(0.30, 0.38, 520, 1.0), (0.66, 0.60, 640, 0.9), (0.78, 0.24, 360, 0.6),
             (0.18, 0.78, 420, 0.5)]
    step, bands = 14, 13

    def field(x, y):
        return sum(
            a * math.exp(-((x - c.w * hx) ** 2 + (y - c.h * hy) ** 2) / (2 * s * s))
            for hx, hy, s, a in hills
        )

    for y in range(0, c.h, step):
        for x in range(0, c.w, step):
            v = field(x, y) * bands
            frac = v - math.floor(v)
            if v > 0.6 and (frac < 0.07 or frac > 0.93) and (x // step + y // step) % 2 == 0:
                a = int(60 + min(1.0, v / bands) * 190)
                d.ellipse([x - 3.4, y - 3.4, x + 3.4, y + 3.4], fill=(255, 255, 255, a))
    X, Y = c.w * 0.30, c.h * 0.38
    d.ellipse([X - 14, Y - 14, X + 14, Y + 14], fill=RED)
    return img


# --- 30 ---------------------------------------------------------------
def split(c):
    """Half the field set in dots, half left empty — a red dot on the seam."""
    img, d = c.new()
    step, r = 44, 5.0
    ang = math.radians(62)
    nx, ny = math.cos(ang), math.sin(ang)
    cx, cy = c.w * 0.52, c.h * 0.5
    for y in range(step, c.h, step):
        for x in range(step, c.w, step):
            s = (x - cx) * nx + (y - cy) * ny
            if s < 0:
                t = min(1.0, -s / 900.0)
                a = int(200 - t * 150)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=RED)
    return img


# (name, function, ground override).  The first twelve were drawn against the
# original #0a0a0a and stay there; the later set is built on the softened UI
# ground so it sits flush with the palette the theme ships today.
PLATES = [
    ("01-dot-matrix", dot_matrix, None),
    ("02-glyph", glyph, None),
    ("03-dot-gradient", dot_gradient, None),
    ("04-red-dot", red_dot, None),
    ("05-rings", rings, None),
    ("06-coil", coil, None),
    ("07-sphere", sphere, None),
    ("08-dot-type", dot_type, None),
    ("09-sequence", sequence, None),
    ("10-exposed", exposed, None),
    ("11-diagonal", diagonal, None),
    ("12-horizon", horizon, None),
    ("13-grid-fade", grid_fade, "141414"),
    ("14-aperture", aperture, "141414"),
    ("15-orbit", orbit, "141414"),
    ("16-strata", strata, "141414"),
    ("17-reticle", reticle, "141414"),
    ("18-weave", weave, "141414"),
    # Full black: true #000000, for OLED panels and the darkest desk.
    ("19-dial", dial, "000000"),
    ("20-waveform", waveform, "000000"),
    ("21-crescent", crescent, "000000"),
    ("22-viewfinder", viewfinder, "000000"),
    ("23-scatter", scatter, "000000"),
    ("24-phyllotaxis", phyllotaxis, "000000"),
    # Back on the softened UI ground.
    ("25-ripple", ripple, "141414"),
    ("26-case", case, "141414"),
    ("27-level", level, "141414"),
    ("28-prompt", prompt, "141414"),
    ("29-contour", contour, "141414"),
    ("30-split", split, "141414"),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--ground",
        default=None,
        help="background hex; overrides each plate's own default (0a0a0a for 01-12, "
        "141414 for 13-18)",
    )
    p.add_argument("--size", default="3840x2400", help="WxH (default 3840x2400)")
    p.add_argument("--out", default=None, help="output dir (default ../backgrounds)")
    p.add_argument("--only", nargs="*", help="generate only these (substring match)")
    args = p.parse_args()

    w, h = (int(v) for v in args.size.lower().split("x"))
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backgrounds")
    os.makedirs(out, exist_ok=True)
    for name, fn, own_ground in PLATES:
        if args.only and not any(k in name for k in args.only):
            continue
        canvas = Canvas(w, h, hex_rgb(args.ground or own_ground or "0a0a0a"))
        img = fn(canvas)
        path = os.path.join(out, name + ".png")
        img.save(path, optimize=True)
        print(f"  {name}.png  {os.path.getsize(path) // 1024} KB")


if __name__ == "__main__":
    main()
