#!/usr/bin/env python3
"""Linuxing Max — 4-system colour-scheme generator.

One theme, four whole-system colour schemes (green / blue / white / red).
Each scheme is a complete Omarchy theme palette: it retints the terminal, the
bar / menu / launcher / lock / OSD, the Hyprland window borders, the native
GTK apps and the browser chrome — not just a single accent.

Every scheme is rendered from `tools/template/*` by swapping `@token@`
placeholders. The terminal canvas is true black and the ink is a near-white
tinted toward the scheme's hue; the scheme's identity lives in the accent,
the desktop-chrome surfaces, the selection/cursor and the 3-stop border
gradient. The ANSI syntax slots (red/yellow/green/…) stay fixed and semantic,
so an error never changes colour when you switch schemes.

Usage:
    python3 tools/linuxing_generate.py               # render all four schemes + root (default)
    python3 tools/linuxing_generate.py --only green  # render one scheme
    python3 tools/linuxing_generate.py --dry-run     # print what would change, write nothing
"""

from __future__ import annotations

import argparse
import colorsys
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_DIR = os.path.join(REPO, "tools", "template")
PALETTES_DIR = os.path.join(REPO, "palettes")
SLUG = "linuxing-max"

# --------------------------------------------------------------------------- #
#  schemes — the four identities. Order is the on-disk and `next/prev` order.
# --------------------------------------------------------------------------- #
SCHEMES = {
    "green": {
        "order": 1,
        "title": "Kernel Green",
        "blurb": "the Linux console signature",
        "accent": "#3ddc84",
        "primary": "#22d3ee",
        "secondary": "#a3e635",
    },
    "blue": {
        "order": 2,
        "title": "Security Blue",
        "blurb": "the SOC / neon-ops blue",
        "accent": "#4dabf7",
        "primary": "#22d3ee",
        "secondary": "#a78bfa",
    },
    "white": {
        "order": 3,
        "title": "Mono White",
        "blurb": "the clean monochrome lab",
        "accent": "#e8e8e8",
        "primary": "#9aa0a6",
        "secondary": "#c9ccd1",
    },
    "red": {
        "order": 4,
        "title": "Root Red",
        "blurb": "the exploit / root prompt",
        "accent": "#ff6b6b",
        "primary": "#ffa94d",
        "secondary": "#ff8787",
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


def strip(hx: str) -> str:
    return hx.lstrip("#").lower()


def rgba(hx: str, alpha: str) -> str:
    return "rgba(%s%s)" % (strip(hx), alpha)


def gradient(*colors: str, angle: str = "45deg") -> str:
    return " ".join(rgba(c, "ee") for c in colors) + " " + angle


# --------------------------------------------------------------------------- #
#  token computation — the whole scheme is derived from its accent hue
# --------------------------------------------------------------------------- #
def compute_tokens(scheme: dict) -> dict[str, str]:
    accent = scheme["accent"]
    primary = scheme["primary"]
    secondary = scheme["secondary"]
    hue, _l, chroma = colorsys.rgb_to_hls(*hex_to_rgb(accent))
    sec_hue, _l2, sec_chroma = colorsys.rgb_to_hls(*hex_to_rgb(secondary))

    # Tint from the accent's own hue and saturation: a neutral accent (the
    # "Mono White" scheme) yields neutral grey surfaces, a vivid accent yields
    # visibly scheme-tinted dark glass. sat_scale is relative to the accent's
    # own chroma, so every scheme stays coherent.
    def tint(lightness: float, sat_scale: float) -> str:
        return hls_to_hex(hue, lightness, chroma * sat_scale)

    tokens = dict(ANSI)
    tokens.update(CHROME)

    tokens.update({
        # provenance for headers
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

    # comma RGB triplets for CSS rgba() surfaces (waybar, etc.)
    for name in ("accent", "primary", "secondary", "surface", "dark", "surface_red", "muted", "light_fg"):
        r, g, b = hex_to_rgb(tokens[name])
        tokens[name + "_rgb"] = "%d,%d,%d" % (round(r * 255), round(g * 255), round(b * 255))
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
    path = os.path.join(TPL_DIR, name)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for key, value in tokens.items():
        text = text.replace("@" + key + "@", value)
    leftover = set(__import__("re").findall(r"@([a-z_]+)@", text))
    if leftover:
        raise SystemExit(f"template {name} has unresolved tokens: {sorted(leftover)}")
    return text


def chromium_rgb(tokens: dict[str, str]) -> str:
    r, g, b = (int(tokens["surface"][i : i + 2], 16) for i in (1, 3, 5))
    return f"{r},{g},{b}"


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

        # gtk-3.0 / gtk-4.0 mirror the root gtk.css (bootstrap symlinks these in)
        gtk = render(tokens, "gtk.css")
        for sub in ("gtk-3.0", "gtk-4.0"):
            os.makedirs(os.path.join(dest_dir, sub), exist_ok=True)
            out = os.path.join(dest_dir, sub, "gtk.css")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(gtk)
            written.append(os.path.relpath(out, REPO))

        if is_root:
            with open(os.path.join(dest_dir, "chromium.theme"), "w", encoding="utf-8") as fh:
                fh.write(chromium_rgb(tokens) + "\n")
            written.append(os.path.relpath(os.path.join(dest_dir, "chromium.theme"), REPO))

    # meta.json — provenance for the scheme switcher
    meta = {
        "num": "%02d" % scheme["order"],
        "slug": "%s-%s" % (SLUG, slug),
        "scheme": slug,
        "theme": "Linuxing Max — %s" % scheme["title"],
        "title": scheme["title"],
        "blurb": scheme["blurb"],
        "accent": scheme["accent"],
        "primary": scheme["primary"],
        "secondary": scheme["secondary"],
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

    if args.only:
        slugs = [args.only]
    else:
        slugs = sorted(SCHEMES, key=lambda s: SCHEMES[s]["order"])

    total: list[str] = []
    for slug in slugs:
        scheme = SCHEMES[slug]
        tokens = compute_tokens(scheme)
        if args.dry_run:
            print("would render %s (%s)" % (slug, scheme["title"]))
            continue
        written = write_scheme(slug, scheme, tokens, default=(slug == DEFAULT_SCHEME))
        total.extend(written)
        print("✓ %s — %s (accent %s)" % (slug, scheme["title"], scheme["accent"]))

    if args.dry_run:
        return 0
    print("\nwrote %d files" % len(total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
