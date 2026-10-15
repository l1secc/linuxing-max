# Publishing Linuxing Max in Omarchy

Omarchy's built-in theme picker lists community themes from the
[`omacom/omarchy-site`](https://github.com/omacom/omarchy-site) repo. Getting
listed is one pull request, and everything it needs lives in this folder.

> **Note:** the listing requires a *public* repository. Linuxing Max is
> currently private, so this folder is ready for the day it is made public.

## What the PR adds

1. **`assets/themes/linuxing-max.webp`** — copy of `linuxing-max.webp` here
   (16:9, 1920×1080).
2. **One entry in `src/data/themes.json`** (keep the array sorted by `name`):

```json
{ "repo": "https://github.com/l1secc/linuxing-max", "image": "/assets/themes/linuxing-max.webp", "name": "Linuxing Max" }
```

## Steps

```bash
gh repo fork omacom/omarchy-site --clone --remote
cd omarchy-site
git checkout -b add-linuxing-max
cp /path/to/linuxing-max/distribution/linuxing-max.webp assets/themes/
$EDITOR src/data/themes.json          # add the entry above, keep alphabetical
npm install && npm run build          # optional local check
git add assets/themes/linuxing-max.webp src/data/themes.json
git commit -m "Add Linuxing Max theme"
git push -u origin add-linuxing-max
gh pr create --repo omacom/omarchy-site --title "Add Linuxing Max theme" \
  --body "Linuxing Max is a dark Linux/security theme with four whole-system colour schemes and a soft glass look. Repo: https://github.com/l1secc/linuxing-max"
```

## Before submitting — checklist

- [x] `omarchy theme install <url>` works and applies the theme.
- [x] Installed theme is colours-only: no Lua, no terminal configs, no
      `vscode.json`. Wallpapers, palettes and `tools/` are the only extras.
- [x] All wallpapers are original procedural artwork (see `CREDITS.md`).
- [x] `preview.webp` / `linuxing-max.webp` are 16:9.
