#!/usr/bin/env python3
"""Linuxing Max — green theme renderer.

Renders the single green palette from `tools/template/*` into the repo root:
`colors.toml`, `shell.toml`, `waybar.css`, `hyprland.conf`, `gtk.css` (and the
`gtk-3.0` / `gtk-4.0` mirrors) plus `chromium.theme`.

The whole system — terminal, bar / menu / launcher / lock / OSD, the Hyprland
window borders and native GTK apps — uses one coherent green palette, and the
bundled wallpapers are all green terminal scenes, so every wallpaper shares the
same look.

Usage:
    python3 tools/linuxing_generate.py            # render green to the repo root
    python3 tools/linuxing_generate.py --dry-run  # show the accent, write nothing
"""

from __future__ import annotations

import argparse
import colorsys
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_DIR = os.path.join(REPO, "tools", "template")

TITLE = "Linuxing Max"
BLURB = "the Linux console signature"

GREEN = {"accent": "#3ddc84", "primary": "#22d3ee", "secondary": "#a3e635"}

# fixed semantic ANSI palette — code stays legible
ANSI = {
    "red": "#ff5c7a", "yellow": "#e5c07b", "orange": "#f6a86b", "green": "#3ddc84",
    "cyan": "#56b6c2", "blue": "#61afef", "magenta": "#c678dd", "brown": "#b08d6a",
    "bright_red": "#ff7a93", "bright_yellow": "#f0d9a0", "bright_green": "#7ce8a8",
    "bright_cyan": "#7fd8e0", "bright_blue": "#82c8ff", "bright_magenta": "#e0a8ee",
    "color0": "#000000", "color1": "#ff5c7a", "color2": "#3ddc84", "color3": "#e5c07b",
    "color4": "#61afef", "color5": "#c678dd", "color6": "#56b6c2", "color7": "#d8dee9",
    "color8": "#6b7280", "color9": "#ff7a93", "color10": "#7ce8a8", "color11": "#f0d9a0",
    "color12": "#82c8ff", "color13": "#e0a8ee", "color14": "#7fd8e0", "color15": "#ffffff",
}

CHROME = {"surface_red": "#d17374", "surface_blue": "#82aaff", "surface_green": "#5fbf8f"}

TEMPLATES = ("colors.toml", "shell.toml", "waybar.css", "hyprland.conf", "gtk.css")


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def hex_to_rgb(hx: str) -> tuple[float, float, float]:
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0, int(hx[4:6], 16) / 255.0)


def hls_to_hex(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, clamp(l), clamp(s))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def strip(hx: str) -> str:
    return hx.lstrip("#").lower()


def rgba(hx: str, alpha: str) -> str:
    return "rgba(%s%s)" % (strip(hx), alpha)


def gradient(*colors: str, angle: str = "45deg") -> str:
    return " ".join(rgba(c, "ee") for c in colors) + " " + angle


def rgb_triplet(hx: str) -> str:
    r, g, b = hex_to_rgb(hx)
    return "%d,%d,%d" % (round(r * 255), round(g * 255), round(b * 255))


def compute_tokens() -> dict[str, str]:
    accent = GREEN["accent"]
    primary = GREEN["primary"]
    secondary = GREEN["secondary"]
    hue, _l, chroma = colorsys.rgb_to_hls(*hex_to_rgb(accent))
    sec_hue, _l2, sec_chroma = colorsys.rgb_to_hls(*hex_to_rgb(secondary))

    def tint(lightness: float, sat_scale: float) -> str:
        return hls_to_hex(hue, lightness, chroma * sat_scale)

    tokens = dict(ANSI)
    tokens.update(CHROME)
    tokens.update({
        "title": TITLE,
        "blurb": BLURB,
        "bg": "#000000",
        "fg": tint(0.93, 0.10),
        "bright_fg": tint(0.97, 0.05),
        "accent": accent,
        "primary": primary,
        "secondary": secondary,
        "secondary_bright": hls_to_hex(sec_hue, 0.84, sec_chroma * 0.85),
        "surface": tint(0.10, 0.30),
        "darker": tint(0.055, 0.28),
        "dark": tint(0.135, 0.25),
        "lighter": tint(0.18, 0.30),
        "bg_alt": tint(0.08, 0.26),
        "bg_surface": tint(0.155, 0.28),
        "surface_fg": tint(0.84, 0.10),
        "surface_bright_fg": tint(0.92, 0.07),
        "light_fg": tint(0.72, 0.13),
        "dark_fg": tint(0.47, 0.20),
        "muted": tint(0.33, 0.22),
        "surface_muted": tint(0.40, 0.19),
        "selection": tint(0.27, 0.45),
        "selection_fg": "#ffffff",
        "cursor": accent,
        "border_active": gradient(accent, primary, secondary),
        "border_inactive": rgba(tint(0.40, 0.19), "aa"),
    })
    for name in ("accent", "primary", "secondary", "surface", "dark", "surface_red", "muted", "light_fg"):
        tokens[name + "_rgb"] = rgb_triplet(tokens[name])
    return tokens


def render(tokens: dict[str, str], name: str) -> str:
    with open(os.path.join(TPL_DIR, name), encoding="utf-8") as fh:
        text = fh.read()
    for key, value in tokens.items():
        text = text.replace("@" + key + "@", value)
    leftover = set(re.findall(r"@([a-z_]+)@", text))
    if leftover:
        raise SystemExit(f"template {name} has unresolved tokens: {sorted(leftover)}")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description="Linuxing Max green renderer")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tokens = compute_tokens()
    if args.dry_run:
        print("accent %s  primary %s  secondary %s" % (tokens["accent"], tokens["primary"], tokens["secondary"]))
        return 0

    written = []
    for tpl in TEMPLATES:
        out = os.path.join(REPO, tpl)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render(tokens, tpl))
        written.append(os.path.relpath(out, REPO))

    gtk = render(tokens, "gtk.css")
    for sub in ("gtk-3.0", "gtk-4.0"):
        os.makedirs(os.path.join(REPO, sub), exist_ok=True)
        out = os.path.join(REPO, sub, "gtk.css")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(gtk)
        written.append(os.path.relpath(out, REPO))

    with open(os.path.join(REPO, "chromium.theme"), "w", encoding="utf-8") as fh:
        fh.write(rgb_triplet(tokens["surface"]) + "\n")
    written.append("chromium.theme")

    print("✓ green — %s (accent %s)" % (TITLE, tokens["accent"]))
    print("wrote %d files" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
