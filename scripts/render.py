#!/usr/bin/env python3
"""Render keyboard diagrams from a .keylayout file.

    python3 scripts/render.py src/*.keylayout docs/images

Output is deterministic — no timestamps, no generated ids — so a diagram that
changes means a mapping changed, and CI can enforce that with `git diff`.

Two styles off one geometry:

  combined   base + shift + option on one keycap, for the README
  plane      one character per keycap, one file per plane, for the docs

Each is emitted twice, light and dark. A single SVG carrying a
prefers-color-scheme media query does not reliably follow the theme when GitHub
renders it through an <img>, so the theme is baked in and the README picks with
<picture>.
"""

import pathlib
import sys
from xml.sax.saxutils import escape

import keylayout
from keylayout import ROWS, ROW_UNITS, KeyLayout, check_geometry

# Geometry, in px. UNIT is a 1u keycap; everything else is derived.
UNIT = 60
GAP = 5
PAD = 24
TITLE_HEIGHT = 34
RADIUS = 8

FONT = (
    "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'SF Pro Text', "
    "'Helvetica Neue', 'Segoe UI', Arial, sans-serif"
)

THEMES = {
    "light": {
        "bg": "#ffffff",
        "cap": "#f7f8fa",
        "cap_edge": "#d5dae1",
        "mod": "#eceef2",
        "mod_edge": "#d5dae1",
        "ink": "#16191d",
        "dim": "#6d7480",
        "faint": "#98a0ad",
        "title": "#454c57",
        "held": "#dce8fb",
        "held_edge": "#8fb2e8",
        "held_ink": "#1a4c9e",
    },
    "dark": {
        "bg": "#0d1117",
        "cap": "#1b2028",
        "cap_edge": "#333b45",
        "mod": "#141920",
        "mod_edge": "#2b323b",
        "ink": "#e8eef5",
        "dim": "#9aa4b2",
        "faint": "#6d7784",
        "title": "#aeb7c2",
        "held": "#1d3055",
        "held_edge": "#3f6198",
        "held_ink": "#9dc2f7",
    },
}

# The glyph each modifier bit wears on the bottom-row keycaps, so a plane
# diagram can light up the keys you actually hold to reach it.
HELD_GLYPHS = {
    "shift": "⇧",
    "option": "⌥",
    "caps": "⇪",
    "command": "⌘",
    "control": "⌃",
}

# Outputs that exist but cannot be drawn as themselves.
BLANK_OUTPUTS = frozenset({" ", " "})


def legend(output):
    """The string to draw on a keycap for a key's output, or '' for nothing."""
    if not output or output in BLANK_OUTPUTS:
        return ""
    if len(output) == 1 and (ord(output) < 0x20 or ord(output) == 0x7F):
        return ""
    return output


def text(x, y, content, *, size, fill, anchor="middle", weight=None, opacity=None):
    if not content:
        return []
    attrs = [
        f'x="{fmt(x)}"',
        f'y="{fmt(y)}"',
        f'font-size="{fmt(size)}"',
        f'fill="{fill}"',
        f'text-anchor="{anchor}"',
    ]
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if opacity is not None:
        attrs.append(f'opacity="{fmt(opacity)}"')
    return [f'<text {" ".join(attrs)}>{escape(content)}</text>']


def fmt(value):
    """Trim floats so the SVG diffs cleanly (60.0 -> 60, 1.5 -> 1.5)."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def cap(x, y, width, theme, *, modifier=False, held=False):
    if held:
        fill, edge = theme["held"], theme["held_edge"]
    elif modifier:
        fill, edge = theme["mod"], theme["mod_edge"]
    else:
        fill, edge = theme["cap"], theme["cap_edge"]
    return [
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{UNIT - GAP}" '
        f'rx="{RADIUS}" fill="{fill}" stroke="{edge}" stroke-width="1"/>'
    ]


def render(layout, style, theme_name, *, plane=None, title=None):
    """Return an SVG document as a string.

    style is 'combined' (three legends per cap) or 'plane' (one).
    """
    theme = THEMES[theme_name]
    width = int(ROW_UNITS * UNIT) - GAP + 2 * PAD
    height = len(ROWS) * UNIT - GAP + 2 * PAD + (TITLE_HEIGHT if title else 0)

    if style == "combined":
        planes = {name: layout.plane(name) for name in ("base", "shift", "option")}
        held = frozenset()
    else:
        planes = {"single": layout.plane(plane)}
        held = frozenset(HELD_GLYPHS[bit] for bit in keylayout.PLANES[plane])

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" '
        f'role="img" aria-label="{escape(aria_label(layout, style, plane))}">',
        f'<rect width="{width}" height="{height}" fill="{theme["bg"]}"/>',
    ]

    top = PAD
    if title:
        glyphs = "".join(HELD_GLYPHS[bit] for bit in keylayout.PLANES[plane])
        prefix = (
            f'<tspan fill="{theme["held_ink"]}">{escape(glyphs)}</tspan>  ' if glyphs else ""
        )
        out.append(
            f'<text x="{PAD}" y="{PAD + 16}" font-size="15" fill="{theme["title"]}" '
            f'text-anchor="start" font-weight="600">{prefix}{escape(title)}</text>'
        )
        top += TITLE_HEIGHT

    for row_index, row in enumerate(ROWS):
        x = PAD
        y = top + row_index * UNIT
        for what, units in row:
            w = units * UNIT - GAP
            if isinstance(what, str):
                is_held = what in held
                out += cap(x, y, w, theme, modifier=True, held=is_held)
                out += text(
                    x + w / 2,
                    y + (UNIT - GAP) / 2 + 6,
                    what,
                    size=18 if is_held else 16,
                    fill=theme["held_ink"] if is_held else theme["faint"],
                    weight="600" if is_held else None,
                )
            elif style == "combined":
                out += cap(x, y, w, theme)
                out += combined_legends(x, y, w, what, planes, theme)
            else:
                out += cap(x, y, w, theme)
                out += text(
                    x + w / 2,
                    y + (UNIT - GAP) / 2 + 8,
                    legend(planes["single"].get(what)),
                    size=22,
                    fill=theme["ink"],
                )
            x += units * UNIT

    out.append("</svg>")
    return "\n".join(out) + "\n"


def combined_legends(x, y, w, code, planes, theme):
    """Base bottom-left, shift above it, option bottom-right and dimmed.

    Shift is omitted where it only capitalises the base letter — printing Й over
    й on every cap is noise that buries the keys where shift does something."""
    base = legend(planes["base"].get(code))
    shift = legend(planes["shift"].get(code))
    option = legend(planes["option"].get(code))

    if shift and base and shift == base.upper() and shift != base:
        shift = ""

    parts = []
    parts += text(x + 11, y + UNIT - GAP - 12, base, size=21, fill=theme["ink"], anchor="start")
    parts += text(x + 11, y + 20, shift, size=14, fill=theme["dim"], anchor="start")
    parts += text(
        x + w - 10,
        y + UNIT - GAP - 12,
        option,
        size=13,
        fill=theme["faint"],
        anchor="end",
    )
    return parts


def aria_label(layout, style, plane):
    if style == "combined":
        return (
            f"{layout.name} keyboard diagram: each key shows its unmodified "
            "character, its shifted character where it differs, and its option character."
        )
    return f"{layout.name} keyboard diagram, {plane} layer."


TITLES = {
    "base": "Base — no modifier held",
    "shift": "Shift",
    "option": "Option",
    "shift+option": "Shift + Option",
}


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    layout = KeyLayout(argv[1])
    check_geometry(layout)

    outdir = pathlib.Path(argv[2])
    outdir.mkdir(parents=True, exist_ok=True)

    written = []
    for theme in THEMES:
        written.append(
            write(outdir / f"layout-combined-{theme}.svg", render(layout, "combined", theme))
        )
        for plane, title in TITLES.items():
            written.append(
                write(
                    outdir / f"layout-{plane.replace('+', '-')}-{theme}.svg",
                    render(layout, "plane", theme, plane=plane, title=title),
                )
            )

    for path in written:
        print(f"    {path}")
    return 0


def write(path, content):
    path.write_text(content, encoding="utf-8")
    return path


if __name__ == "__main__":
    sys.exit(main(sys.argv))
