# Nothing

Monochrome ground, one red signal, dot-matrix surfaces.

![Nothing](preview.png)

An [Omarchy](https://omarchy.org/) theme after Nothing's design language.

## Install

```bash
omarchy theme install https://github.com/lookiyam-94/omarchy-nothing-theme.git
omarchy theme set nothing
```

## Idea

Nothing's hardware is transparent shell over black, with white glyph LEDs and a
single red accent used sparingly — a record dot, a power key. The theme follows
that discipline. The desktop is near-black (`#0a0a0a`) under glyph-white text
(`#ededed`). Red (`#d71921`) is the only saturated colour on screen, and it is
spent on one thing: the focused window.

## Palette

| Role | Hex | Notes |
|---|---|---|
| `background` | `#0a0a0a` | Near-black, not pure — keeps panel edges readable |
| `darker_background` | `#000000` | True black for the deepest surfaces |
| `foreground` | `#ededed` | Glyph white, 16.9:1 on background |
| `accent` | `#d71921` | Nothing red |
| `bright_red` | `#ff3b42` | The active-border gradient's far stop |
| `selection` | `#2a2a2a` | Neutral grey — selection never tints |

Active window border is a 45° gradient `#d71921 → #ff3b42`. Inactive borders drop
to `#2a2a2a` so only one window is ever lit.

### ANSI colours

The sixteen terminal slots are desaturated hard — enough hue to separate strings
from keywords from numbers, not enough to read as colour at a glance. Red is the
exception and stays at full strength, so errors and diffs cut through a screen
that is otherwise grey. All non-red hues clear 5:1 on the background; red clears
3.8:1, which is a UI/large-text ratio suited to its role as border and indicator.

## Backgrounds

Twelve, generated rather than photographed, in Nothing's own geometric idiom.
All 3840x2400, flat vector-style art — the whole set is about 1 MB.

| File | |
|---|---|
| `01-dot-matrix.png` | Uniform dot grid with one red dot off-centre |
| `02-glyph.png` | Phone (1) light-strip arrangement |
| `03-dot-gradient.png` | Halftone bloom, transparent-shell feel |
| `04-red-dot.png` | Pure black, one red dot |
| `05-rings.png` | Concentric dot rings, camera motif |
| `06-coil.png` | Wireless-charging coil with lead-out trace |
| `07-sphere.png` | Halftone-shaded orb |
| `08-dot-type.png` | NOTHING set in a 5x7 dot matrix |
| `09-sequence.png` | Glyph composer light bars, one struck red |
| `10-exposed.png` | The transparent back as schematic |
| `11-diagonal.png` | Dot rulings on the bias, one red |
| `12-horizon.png` | Halftone density falling to a hard red rule |

Cycle with `omarchy theme bg next`, or pick one from `omarchy theme bg-switcher`.
Files are numbered because Omarchy sorts them lexically.

Extra backgrounds of your own go in `~/.config/omarchy/backgrounds/nothing/` —
they join the rotation without touching the theme.

## Notes

- Pairs well with a dot-matrix display font (Nothing ships NType82 / Ndot).
  None is installed here; `omarchy font list` shows what is.
- Red as menu `selected-text` sits at 3.8:1. If selected rows read dim, copy the
  generated `shell.toml` from `~/.local/state/omarchy/current/theme/` into this
  directory and set `selected-text` to `#ff3b42`.
