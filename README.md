# Linuxing Max

A **Linux / software / cyber-security** theme for [Omarchy](https://omarchy.org/).
Every scheme is **wallpaper-driven**: it reads its bundled wallpaper, pulls that
photo's own colour palette, and retints the *entire* desktop to match — the
terminal, editor, browser, the bar / menu / launcher / lock / OSD, the Hyprland
window borders and the native GTK apps. Soft squircle corners, glassmorphism
blur, reduced window opacity and a rich animation set round out the "Linuxing
glides through the terminal" feel.

> Installs through Omarchy's own `omarchy theme install` (a `colors.toml`-driven,
> code-free theme); a one-time bootstrap then puts the scheme switcher and the
> soft look in place.

---

## Quick start

```bash
# one-command install (clones + bootstraps)
bash <(curl -fsSL https://raw.githubusercontent.com/l1secc/linuxing-max/main/bootstrap.sh)

# …or, step by step:
omarchy theme install https://github.com/l1secc/linuxing-max
~/.config/omarchy/themes/linuxing-max/install.sh

# switch the whole system colour scheme (photo + palette together)
linuxing-scheme             # next scheme
linuxing-scheme sunset      # jump to a scheme
linuxing-scheme prev        # previous
linuxing-scheme list        # show them
```

---

## The schemes

Switching a scheme swaps the wallpaper **and** repaints the whole system from
that photo's palette. The terminal canvas stays true black and the ink stays a
photo-tinted near-white; the accent, the desktop-chrome surfaces, the selection,
the cursor and the 3-stop window border all follow the photo:

| Scheme | Wallpaper | Feels like |
|--------|-----------|------------|
| **Kernel Green** (default) | terminal | the Linux console signature |
| **Sunset Amber** | warm sun over a hill line | golden hour over the mainframe |
| **Neon Synthwave** | striped sun + neon grid | hot-pink wires |
| **Deep Ocean** | sonar rings in the abyss | a sweep in the deep |
| **Crimson Root** | circuit traces + glitch | red-hot root access |
| **Frostbite** | snowflake lattice | cold storage at the north pole |

The ANSI syntax slots stay fixed and semantic across schemes, so an error never
changes colour when you switch.

---

## How it works

### What `omarchy theme install` does

Omarchy clones this repo into `~/.config/omarchy/themes/linuxing-max`, keeps
every colour/config file, and **drops the files that would run code** —
`*.lua`, terminal configs and `vscode.json` are regenerated from `colors.toml`
by Omarchy itself. That is deliberate: a theme pulled from a repo can never run
code on your machine by itself.

### What the bootstrap adds (the one-time step you run yourself)

`install.sh` → `tools/linuxing-bootstrap` installs, idempotently:

- **`~/.config/hypr/looknfeel.lua`** — rounded squircle corners (`rounding 16`),
  glassmorphism blur, soft shadows, reduced window opacity (`0.92 / 0.85`) and
  the full animation set. This is the only thing a cloned theme cannot ship.
- **foot terminal translucency** — `alpha=0.82`, text stays crisp.
- **eza file-kind colours** — folders phosphor green, text stays white.
- **native GTK overrides** — symlinked at `~/.config/gtk-{3,4}.0/gtk.css` so
  they follow both `omarchy theme set` and `linuxing-scheme`.
- **`linuxing-scheme` on your PATH**, plus a `theme-set` hook so
  `omarchy theme update` / re-applying the theme keeps everything current.

Uninstall with `~/.config/omarchy/themes/linuxing-max/install.sh --uninstall`.

### The generator — photo → palette

`tools/linuxing_generate.py` reads each scheme's wallpaper, extracts its
dominant colours with ImageMagick, picks a vivid accent plus two harmonising
accents, derives the whole palette from the accent hue (a neutral accent yields
neutral grey surfaces, a vivid one yields photo-tinted dark glass), and renders
every file from `tools/template/*` by swapping `@token@` placeholders. Add a
wallpaper and a line in `SCHEMES`, then:

```bash
python3 tools/linuxing_generate.py               # every scheme + root (default)
python3 tools/linuxing_generate.py --only sunset # one scheme
```

### The switcher

`tools/linuxing-scheme` copies the scheme's bundle
(`colors` + `shell` + `waybar` + `hyprland` + `gtk` + `chromium`) onto the theme
root, re-applies the theme with `OMARCHY_THEME_SKIP_BACKGROUND=1` so Omarchy
regenerates every config and hot-reloads the running shell, then pins the
scheme's own wallpaper. `--light` hot-reloads without the full app-restart chain.

---

## Layout

```
linuxing-max/
├── colors.toml            # active palette (green by default) — drives everything
├── shell.toml             # bar / menu / launcher / lock / OSD glass surfaces
├── waybar.css             # waybar parity (frosted-glass cards)
├── hyprland.conf          # legacy/non-Omarchy Hyprland parity
├── gtk.css + gtk-3.0/ + gtk-4.0/   # native GTK tokens
├── icons.theme            # Yaru-prussiangreen (change to taste)
├── chromium.theme         # browser chrome tint
├── eza/theme.yml          # file-kind colours
├── foot/linuxing-foot.ini # translucent terminal block
├── hypr/looknfeel.lua     # animations + rounding + blur + opacity
├── backgrounds/           # the wallpapers, one per scheme
├── palettes/              # one bundle per scheme (colors + shell + waybar + hyprland + gtk + chromium)
├── tools/
│   ├── linuxing_generate.py      # photo → palette → scheme generator
│   ├── linuxing-scheme           # scheme + wallpaper switcher (on PATH)
│   ├── linuxing-bootstrap        # soft look installer
│   └── generate-wallpapers.sh    # wallpaper generator
├── install.sh             # bootstrap + hook
├── bootstrap.sh           # curl one-liner
├── preview.webp / .jpg    # theme-picker thumbnail
└── distribution/          # for the omarchy-site community listing
```

---

## Tuning

**Softer / more rounded** — edit `hypr/looknfeel.lua` and re-run
`tools/linuxing-bootstrap`:

- `decoration.rounding` — `10` subtle, `16` this, `22` bubbly.
- `o.window(... { opacity = "0.92 0.85" })` — `"0.96 0.92"` barely there,
  `"0.88 0.80"` bold.
- `foot/linuxing-foot.ini` `alpha` — `0.82` default, `0.78` more transparent.

**More/less translucent surfaces** — the `*-alpha` keys in
`tools/template/shell.toml`, then `python3 tools/linuxing_generate.py`.

**A new photo scheme** — drop a wallpaper in `backgrounds/`, add an entry to
`SCHEMES` in `tools/linuxing_generate.py`, run it. The palette is extracted for
you.

**Different icons** — edit `icons.theme` (any installed icon theme).

---

## Wallpapers

Original, procedurally generated 1920×1080 wallpapers (terminal, sunset,
synthwave, ocean, crimson, frost) — dark enough to sit behind the glass UI.
Regenerate with `tools/generate-wallpapers.sh` (needs ImageMagick 7 and the
JetBrainsMono Nerd Font). Drop your own into
`~/.config/omarchy/backgrounds/linuxing-max/`.

---

## License

MIT — see [LICENSE](LICENSE). The wallpapers are original procedural artwork
generated for this theme.
