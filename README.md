# Linuxing Max

A **Linux / software / cyber-security** theme for [Omarchy](https://omarchy.org/).
One theme, four whole-system colour schemes — **green**, **blue**, **white**,
**red** — each retints the *entire* desktop: terminal, editor, browser, the bar
/ menu / launcher / lock / OSD, the Hyprland window borders and the native GTK
apps. Soft squircle corners, glassmorphism blur, reduced window opacity and a
rich animation set round out the "Linuxing glides through the terminal" feel.

> **This is the Linuxing Max theme.** It installs through Omarchy's own
> `omarchy theme install` (a `colors.toml`-driven, code-free theme) and then a
> one-time bootstrap puts the scheme switcher and the soft look in place.

---

## Quick start

```bash
# one-command install (clones + bootstraps)
bash <(curl -fsSL https://raw.githubusercontent.com/l1secc/linuxing-max/main/bootstrap.sh)

# …or, step by step:
omarchy theme install https://github.com/l1secc/linuxing-max
~/.config/omarchy/themes/linuxing-max/install.sh

# apply (install already applies it, this is for later)
omarchy theme set 'Linuxing Max'

# switch the whole system colour scheme
linuxing-scheme            # next scheme
linuxing-scheme blue       # jump to a scheme
linuxing-scheme prev       # previous
linuxing-scheme list       # show them
```

---

## The four schemes

Every scheme is a complete palette — the terminal canvas stays true black and
the ink stays a scheme-tinted near-white, but the accent, the desktop-chrome
surfaces, the selection, the cursor and the 3-stop window border all follow the
scheme:

| Scheme | Accent | Feels like |
|--------|--------|------------|
| **Kernel Green** (default) | `#3ddc84` | the Linux console signature |
| **Security Blue** | `#4dabf7` | the SOC / neon-ops blue |
| **Mono White** | `#e8e8e8` | the clean monochrome lab |
| **Root Red** | `#ff6b6b` | the exploit / root prompt |

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

### The generator

`tools/linuxing_generate.py` renders every scheme from `tools/template/*` by
swapping `@token@` placeholders. The whole palette is derived from each
scheme's accent hue (a neutral accent yields neutral grey surfaces, a vivid one
yields scheme-tinted dark glass), so the four identities stay coherent and
adding a scheme is a handful of lines. Re-run it after editing the templates:

```bash
python3 tools/linuxing_generate.py            # all schemes + root (default green)
python3 tools/linuxing_generate.py --only red
```

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
├── backgrounds/           # 8 procedural wallpapers (tools/generate-wallpapers.sh)
├── palettes/              # one bundle per scheme (colors + shell + waybar + hyprland + gtk)
├── tools/
│   ├── linuxing_generate.py      # scheme generator
│   ├── linuxing-scheme           # scheme switcher (installed to PATH)
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

**Different icons** — edit `icons.theme` (any installed icon theme).

---

## Wallpapers

Eight original, procedurally generated 1920×1080 wallpapers (terminal, circuit,
network graph, matrix, grid, glitch, radar, hex lattice) — dark and
near-monochrome so they sit quietly behind the glass and read well under all
four schemes. Regenerate with `tools/generate-wallpapers.sh` (needs ImageMagick
7 and the JetBrainsMono Nerd Font). Drop your own into
`~/.config/omarchy/backgrounds/linuxing-max/`.

---

## License

MIT — see [LICENSE](LICENSE). The wallpapers are original procedural artwork
generated for this theme.
