#!/usr/bin/env python3
"""Linuxing Max — wallpaper-driven whole-system colour-scheme generator.

One theme, several whole-system colour schemes. Each photo-driven scheme reads
its bundled wallpaper, extracts the wallpaper's own colour palette and derives
an entire Omarchy theme palette from it: the terminal, the bar / menu / launcher
/ lock / OSD, the Hyprland window borders, the native GTK apps and the browser
chrome are all retinted to match the photo.

The first scheme (`green`) keeps the hand-tuned palette the theme shipped with
and simply pairs it with the terminal wallpaper.

Every scheme is rendered from `tools/template/*` by swapping `@token@`
placeholders. The terminal canvas is true black and the ink is a near-white
tinted toward the scheme's hue; the scheme's identity lives in the accent, the
desktop-chrome surfaces, the selection/cursor and the 3-stop border gradient.
The ANSI syntax slots (red/yellow/green/…) stay fixed and semantic, so an error
never changes colour when you switch schemes.

Usage:
    python3 tools/linuxing_generate.py               # render every scheme + root (default)
    python3 tools/linuxing_generate.py --only sunset # render one scheme
    python3 tools/linuxing_generate.py --dry-run     # print what would change, write nothing
"""

from __future__ import annotations

import argparse
import colorsys
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_DIR = os.path.join(REPO, "tools", "template")
PALETTES_DIR = os.path.join(REPO, "palettes")
BG_DIR = os.path.join(REPO, "backgrounds")
SLUG = "linuxing-max"

# --------------------------------------------------------------------------- #
#  schemes — the identities. Order is the on-disk and `next/prev` order.
#
#  A scheme with an explicit `accent` keeps its hand-tuned palette. A scheme
#  with only a `wallpaper` has its accent / primary / secondary extracted from
#  that image at generation time.
# --------------------------------------------------------------------------- #
SCHEMES = {
    "green": {
        "order": 1,
        "title": "Kernel Green",
        "blurb": "the Linux console signature",
        "accent": "#3ddc84",
        "primary": "#22d3ee",
        "secondary": "#a3e635",
        "wallpaper": "Linuxing-01-terminal.jpg",
    },
    "sunset": {
        "order": 2,
        "title": "Sunset Amber",
        "blurb": "golden hour over the mainframe",
        "wallpaper": "Linuxing-02-sunset.jpg",
    },
    "synthwave": {
        "order": 3,
        "title": "Neon Synthwave",
        "blurb": "hot-pink wires under a striped sun",
        "wallpaper": "Linuxing-03-synthwave.jpg",
    },
    "ocean": {
        "order": 4,
        "title": "Deep Ocean",
        "blurb": "a sonar sweep in the abyss",
        "wallpaper": "Linuxing-04-ocean.jpg",
    },
    "crimson": {
        "order": 5,
        "title": "Crimson Root",
        "blurb": "red-hot root access",
        "wallpaper": "Linuxing-05-crimson.jpg",
    },
    "frost": {
        "order": 6,
        "title": "Frostbite",
        "blurb": "cold storage at the north pole",
        "wallpaper": "Linuxing-06-frost.jpg",
    },
}

DEFAULT_SCHEME = "green"

# --------------------------------------------------------------------------- #
#  fixed semantic ANSI palette — shared by every scheme so code stays legible
# --------------------------------------------------------------------------- #
ANSI = {
    "red": "#ff5c7a",
    "yellow": "#e5c07b",
    "orange": "#f6a86b",
    "green": "#3ddc84",
    "cyan": "#56b6c2",
    "blue": "#61afef",
    "magenta": "#c678dd",
    "brown": "#b08d6a",
    "bright_red": "#ff7a93",
    "bright_yellow": "#f0d9a0",
    "bright_green": "#7ce8a8",
    "bright_cyan": "#7fd8e0",
    "bright_blue": "#82c8ff",
    "bright_magenta": "#e0a8ee",
    "color0": "#000000",
    "color1": "#ff5c7a",
    "color2": "#3ddc84",
    "color3": "#e5c07b",
    "color4": "#61afef",
    "color5": "#c678dd",
    "color6": "#56b6c2",
    "color7": "#d8dee9",
    "color8": "#6b7280",
    "color9": "#ff7a93",
    "color10": "#7ce8a8",
    "color11": "#f0d9a0",
    "color12": "#82c8ff",
    "color13": "#e0a8ee",
    "color14": "#7fd8e0",
    "color15": "#ffffff",
}

# Chrome-only semantic colours (bar/menu/lock error & success indicators).
CHROME = {
    "surface_red": "#d17374",
    "surface_blue": "#82aaff",
    "surface_green": "#5fbf8f",
}

# --------------------------------------------------------------------------- #
#  colour helpers
# --------------------------------------------------------------------------- #
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def hex_to_rgb(hx: str) -> tuple[float, float, float]:
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0, int(hx[4:6], 16) / 255.0)


def hls_to_hex(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, clamp(l), clamp(s))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def hue_of(hx: str) -> float:
    r, g, b = hex_to_rgb(hx)
    h, _l, _s = colorsys.rgb_to_hls(r, g, b)
    return h


def hue_dist(a: float, b: float) -> float:
    d = abs(a - b) % 1.0
    return min(d, 1.0 - d)


def strip(hx: str) -> str:
    return hx.lstrip("#").lower()


def rgba(hx: str, alpha: str) -> str:
    return "rgba(%s%s)" % (strip(hx), alpha)


def gradient(*colors: str, angle: str = "45deg") -> str:
    return " ".join(rgba(c, "ee") for c in colors) + " " + angle


def rgb_triplet(hx: str) -> str:
    r, g, b = hex_to_rgb(hx)
    return "%d,%d,%d" % (round(r * 255), round(g * 255), round(b * 255))


# --------------------------------------------------------------------------- #
#  wallpaper → palette  (ImageMagick dominant colours)
# --------------------------------------------------------------------------- #
def _vivid(c: dict, min_s: float) -> str:
    """A usable, vivid hex from a candidate {h,l,s}."""
    return hls_to_hex(c["h"], clamp(c["l"], 0.52, 0.68), max(c["s"], min_s))


def extract_palette(image_path: str) -> tuple[str, str, str]:
    import math
    out = subprocess.run(
        ["magick", image_path, "-resize", "200x200", "-colors", "24", "-unique-colors", "txt:-"],
        capture_output=True, text=True, check=True,
    ).stdout

    cands = []
    seen = set()
    for hx in re.findall(r"#([0-9A-Fa-f]{6})", out):
        hx = "#" + hx.lower()
        if hx in seen:
            continue
        seen.add(hx)
        r, g, b = hex_to_rgb(hx)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        cands.append({"hex": hx, "h": h, "l": l, "s": s})
    if not cands:
        raise SystemExit(f"could not read any colours from {image_path}")

    def weight(c: dict) -> float:
        return c["s"] * (0.35 + 0.65 * c["l"])

    # Dominant hue as a circular mean weighted by chromatic strength, so a
    # tinted (dark) terminal background and its vivid prompt both contribute.
    wx = sum(weight(c) * math.cos(2 * math.pi * c["h"]) for c in cands)
    wy = sum(weight(c) * math.sin(2 * math.pi * c["h"]) for c in cands)
    dom_h = (math.atan2(wy, wx) / (2 * math.pi)) % 1.0

    near = [c for c in cands if hue_dist(c["h"], dom_h) < 0.22]
    if near:
        best = max(near, key=weight)
        sat = clamp(max(best["s"], 0.62), 0.62, 0.92)
        lig = clamp(max(best["l"], 0.55), 0.52, 0.70)
    else:
        sat, lig = 0.72, 0.60
    accent = hls_to_hex(dom_h, lig, sat)

    # primary/secondary: strongest hues clearly away from the accent; fall back
    # to analogous shimmers of the accent for a tasteful gradient.
    others = []
    for c in sorted(cands, key=weight, reverse=True):
        if hue_dist(c["h"], dom_h) <= 0.10:
            continue
        if any(hue_dist(c["h"], o["h"]) < 0.10 for o in others):
            continue
        others.append({"h": c["h"], "l": clamp(max(c["l"], 0.52), 0.52, 0.70), "s": clamp(max(c["s"], 0.50), 0.50, 0.85)})
        if len(others) == 2:
            break
    while len(others) < 2:
        shift = (0.075, -0.09)[len(others)]
        others.append({"h": (dom_h + shift) % 1.0, "l": 0.60, "s": 0.60})

    primary = hls_to_hex(others[0]["h"], others[0]["l"], others[0]["s"])
    secondary = hls_to_hex(others[1]["h"], others[1]["l"], others[1]["s"])
    return accent, primary, secondary


#  token computation — the whole scheme is derived from its accent hue
# --------------------------------------------------------------------------- #
def compute_tokens(scheme: dict) -> dict[str, str]:
    accent = scheme.get("accent")
    primary = scheme.get("primary")
    secondary = scheme.get("secondary")
    if not (accent and primary and secondary):
        wall = os.path.join(BG_DIR, scheme["wallpaper"])
        accent, primary, secondary = extract_palette(wall)

    hue, _l, chroma = colorsys.rgb_to_hls(*hex_to_rgb(accent))
    sec_hue, _l2, sec_chroma = colorsys.rgb_to_hls(*hex_to_rgb(secondary))

    # Tint from the accent's own hue and saturation: a neutral accent yields
    # neutral grey surfaces, a vivid accent yields visibly scheme-tinted dark
    # glass. sat_scale is relative to the accent's own chroma.
    def tint(lightness: float, sat_scale: float) -> str:
        return hls_to_hex(hue, lightness, chroma * sat_scale)

    tokens = dict(ANSI)
    tokens.update(CHROME)

    tokens.update({
        "title": scheme["title"],
        "blurb": scheme["blurb"],

        # terminal canvas + ink
        "bg": "#000000",
        "fg": tint(0.93, 0.10),
        "bright_fg": tint(0.97, 0.05),

        # identity
        "accent": accent,
        "primary": primary,
        "secondary": secondary,
        "secondary_bright": hls_to_hex(sec_hue, 0.84, sec_chroma * 0.85),

        # desktop chrome surfaces (scheme-tinted dark glass)
        "surface": tint(0.10, 0.30),
        "darker": tint(0.055, 0.28),
        "dark": tint(0.135, 0.25),
        "lighter": tint(0.18, 0.30),
        "bg_alt": tint(0.08, 0.26),
        "bg_surface": tint(0.155, 0.28),

        # foregrounds
        "surface_fg": tint(0.84, 0.10),
        "surface_bright_fg": tint(0.92, 0.07),
        "light_fg": tint(0.72, 0.13),
        "dark_fg": tint(0.47, 0.20),
        "muted": tint(0.33, 0.22),
        "surface_muted": tint(0.40, 0.19),

        # selection + cursor
        "selection": tint(0.27, 0.45),
        "selection_fg": "#ffffff",
        "cursor": accent,

        # Hyprland borders
        "border_active": gradient(accent, primary, secondary),
        "border_inactive": rgba(tint(0.40, 0.19), "aa"),
    })

    for name in ("accent", "primary", "secondary", "surface", "dark", "surface_red", "muted", "light_fg"):
        tokens[name + "_rgb"] = rgb_triplet(tokens[name])
    return tokens


# --------------------------------------------------------------------------- #
#  render + write
# --------------------------------------------------------------------------- #
TEMPLATES = (
    "colors.toml",
    "shell.toml",
    "waybar.css",
    "hyprland.conf",
    "gtk.css",
)


def render(tokens: dict[str, str], name: str) -> str:
    with open(os.path.join(TPL_DIR, name), encoding="utf-8") as fh:
        text = fh.read()
    for key, value in tokens.items():
        text = text.replace("@" + key + "@", value)
    leftover = set(re.findall(r"@([a-z_]+)@", text))
    if leftover:
        raise SystemExit(f"template {name} has unresolved tokens: {sorted(leftover)}")
    return text


def write_scheme(slug: str, scheme: dict, tokens: dict[str, str], default: bool) -> list[str]:
    written: list[str] = []

    bundle_dir = os.path.join(PALETTES_DIR, "%02d-%s-%s" % (scheme["order"], SLUG, slug))
    os.makedirs(bundle_dir, exist_ok=True)

    targets = [(bundle_dir, False)]
    if default:
        targets.append((REPO, True))

    for dest_dir, is_root in targets:
        for tpl in TEMPLATES:
            out = os.path.join(dest_dir, tpl)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(render(tokens, tpl))
            written.append(os.path.relpath(out, REPO))

        gtk = render(tokens, "gtk.css")
        for sub in ("gtk-3.0", "gtk-4.0"):
            os.makedirs(os.path.join(dest_dir, sub), exist_ok=True)
            out = os.path.join(dest_dir, sub, "gtk.css")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(gtk)
            written.append(os.path.relpath(out, REPO))

        with open(os.path.join(dest_dir, "chromium.theme"), "w", encoding="utf-8") as fh:
            fh.write(rgb_triplet(tokens["surface"]) + "\n")
        written.append(os.path.relpath(os.path.join(dest_dir, "chromium.theme"), REPO))

    meta = {
        "num": "%02d" % scheme["order"],
        "slug": "%s-%s" % (SLUG, slug),
        "scheme": slug,
        "theme": "Linuxing Max — %s" % scheme["title"],
        "title": scheme["title"],
        "blurb": scheme["blurb"],
        "wallpaper": scheme["wallpaper"],
        "accent": tokens["accent"],
        "primary": tokens["primary"],
        "secondary": tokens["secondary"],
        "generator": "tools/linuxing_generate.py",
    }
    meta_path = os.path.join(bundle_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    written.append(os.path.relpath(meta_path, REPO))

    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="Linuxing Max scheme generator")
    ap.add_argument("--only", choices=sorted(SCHEMES), help="render a single scheme")
    ap.add_argument("--dry-run", action="store_true", help="list changes, write nothing")
    args = ap.parse_args()

    slugs = [args.only] if args.only else sorted(SCHEMES, key=lambda s: SCHEMES[s]["order"])

    total: list[str] = []
    for slug in slugs:
        scheme = SCHEMES[slug]
        tokens = compute_tokens(scheme)
        if args.dry_run:
            print("would render %-10s %s (accent %s)" % (slug, scheme["title"], tokens["accent"]))
            continue
        total.extend(write_scheme(slug, scheme, tokens, default=(slug == DEFAULT_SCHEME)))
        print("✓ %-10s %-16s accent %s  wallpaper %s" % (slug, scheme["title"], tokens["accent"], scheme["wallpaper"]))

    if args.dry_run:
        return 0
    print("\nwrote %d files" % len(total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
