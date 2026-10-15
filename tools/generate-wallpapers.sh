#!/usr/bin/env bash
# ============================================================================
#  Linuxing Max · wallpaper generator
#
#  Produces the bundled 1920×1080 wallpapers. Each one carries a distinct
#  colour vibe; `tools/linuxing_generate.py` reads the wallpaper and derives
#  that scheme's whole-system palette from it. Dark enough to sit behind the
#  glass UI under every scheme.
#
#  Requires ImageMagick 7 (`magick`) and the JetBrainsMono Nerd Font.
#
#  Usage:
#    tools/generate-wallpapers.sh
# ============================================================================
set -euo pipefail

OUT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)/backgrounds"
mkdir -p "$OUT"
W=1920
H=1080
MONO="/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
MONO_B="/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# base3 <top> <mid> <bottom> <out> — a 3-stop vertical gradient
base3() {
  magick -size ${W}x$((H / 2)) gradient:"$1"-"$2" "$WORK/a.png"
  magick -size ${W}x$((H / 2)) gradient:"$2"-"$3" "$WORK/b.png"
  magick "$WORK/a.png" "$WORK/b.png" -append "$4"
}

# glow <top> <mid> <bottom> <glow-colour> <cx> <cy> <radius> <out>
glow() {
  local top=$1 mid=$2 bot=$3 color=$4 cx=$5 cy=$6 r=$7 out=$8
  base3 "$top" "$mid" "$bot" "$WORK/base.png"
  magick -size $((r * 2))x$((r * 2)) radial-gradient:"${color}ff"-"${color}00" "$WORK/glow.png"
  magick "$WORK/base.png" "$WORK/glow.png" -gravity NorthWest \
    -geometry +$((cx - r))+$((cy - r)) -composite "$out"
}

# ------------------------------------------------------------------ 01 terminal
# A dark terminal panel with a green prompt, faded at the edges.
magick -size ${W}x${H} radial-gradient:'#101613'-'#050706' \
  -fill '#0a100c' -stroke '#1c2a21' -strokewidth 1 \
  -draw "roundrectangle 420,190 1500,890 20,20" \
  -fill '#060a07' -draw "roundrectangle 420,190 1500,244 20,20" \
  -fill '#1c2a21' -draw "circle 446,217 446,211" \
  -fill '#2a3d31' -draw "circle 486,217 486,211" \
  -fill '#3d2a2e' -draw "circle 526,217 526,211" \
  -gravity NorthWest \
  -font "$MONO_B" -pointsize 30 -fill '#3ddc84' -annotate +460+300 "linuxing@max:~$" \
  -font "$MONO" -pointsize 26 -fill '#9fb3a6' -annotate +460+356 "sudo systemctl start the-future" \
  -font "$MONO" -pointsize 26 -fill '#5f7366' -annotate +460+412 "[ ok ] kernel · hyprland · omarchy" \
  -font "$MONO" -pointsize 26 -fill '#5f7366' -annotate +460+468 "[ ok ] shell · bar · launcher · lock" \
  -font "$MONO_B" -pointsize 30 -fill '#3ddc84' -annotate +460+540 "linuxing@max:~$" \
  -font "$MONO" -pointsize 26 -fill '#c8d6cc' -annotate +790+544 "_" \
  -attenuate 0.3 +noise Gaussian \
  "$OUT/Linuxing-01-terminal.jpg"

# -------------------------------------------------------------------- 02 sunset
# Warm amber sun sinking behind a hill line.
glow '#150a20' '#5a1e2e' '#d4601e' '#ffb347' 960 760 620 "$WORK/sunset.png"
magick "$WORK/sunset.png" \
  -stroke '#ffcf80' -strokewidth 1 -fill none \
  -draw "circle 960,760 960,700" \
  -fill '#120610' -stroke none \
  -draw "polygon 0,1080 0,930 360,1000 820,900 1320,1010 1620,940 1920,1010 1920,1080" \
  -attenuate 0.28 +noise Gaussian \
  "$OUT/Linuxing-02-sunset.jpg"

# ---------------------------------------------------------------- 03 synthwave
# Neon purple grid under a striped sun.
glow '#0d0118' '#2a0750' '#6a0a7a' '#ff2d95' 960 700 560 "$WORK/synth.png"
magick "$WORK/synth.png" \
  -stroke '#8a30d0' -strokewidth 1 -fill none \
  -draw "$(for i in $(seq 1 26); do y=$((560 + i * i * 2)); printf 'line 0,%d 1920,%d ' "$y" "$y"; done)" \
  -draw "line 960,560 0,1080 line 960,560 380,1080 line 960,560 760,1080 line 960,560 1160,1080 line 960,560 1540,1080 line 960,560 1920,1080" \
  -stroke '#22d3ee' -strokewidth 1 -fill none -draw "line 0,560 1920,560" \
  -attenuate 0.28 +noise Gaussian \
  "$OUT/Linuxing-03-synthwave.jpg"

# --------------------------------------------------------------------- 04 ocean
# Deep teal with a sonar sweep.
glow '#03121a' '#073a4a' '#0e6a7a' '#35e0d0' 1200 420 620 "$WORK/ocean.png"
magick "$WORK/ocean.png" \
  -stroke '#2ad0c0' -strokewidth 1 -fill none \
  -draw "circle 1200,420 1200,180 circle 1200,420 1200,300 circle 1200,420 1200,540 circle 1200,420 1200,820" \
  -stroke '#7af0e4' -strokewidth 2 -draw "line 1200,420 1680,180" \
  -attenuate 0.28 +noise Gaussian \
  "$OUT/Linuxing-04-ocean.jpg"

# ------------------------------------------------------------------- 05 crimson
# Crimson glow with circuit traces and a glitch band.
glow '#0a0204' '#3a0610' '#7a0f1a' '#ff3040' 900 780 600 "$WORK/crimson.png"
magick "$WORK/crimson.png" \
  -stroke '#ff3b3b' -strokewidth 1 -fill none \
  -draw "$(for i in $(seq 1 26); do x1=$((RANDOM % W)); y1=$((RANDOM % H)); x2=$((x1 + (RANDOM % 200 - 100))); y2=$((y1 + (RANDOM % 200 - 100))); printf 'line %d,%d %d,%d ' "$x1" "$y1" "$x2" "$y2"; done)" \
  -fill '#ff3040' -stroke none \
  -draw "$(for i in $(seq 1 30); do x=$((RANDOM % W)); y=$((RANDOM % H)); printf 'circle %d,%d %d,%d ' "$x" "$y" "$((x + 4))" "$y"; done)" \
  -fill '#ff5a5a' -draw "rectangle 0,700 1920,712" \
  -attenuate 0.28 +noise Gaussian \
  "$OUT/Linuxing-05-crimson.jpg"

# ---------------------------------------------------------------------- 06 frost
# Icy blue with a snowflake lattice.
glow '#060b14' '#10263a' '#2a5a7a' '#9fd8ff' 700 500 620 "$WORK/frost.png"
{
  echo "-fill none -stroke '#bfe6ff' -strokewidth 1"
  for hx in 300 700 1100 1500; do
    for hy in 260 540 820; do
      echo "-draw 'polygon $((hx + 60)),$hy $((hx + 30)),$((hy + 52)) $((hx - 30)),$((hy + 52)) $((hx - 60)),$hy $((hx - 30)),$((hy - 52)) $((hx + 30)),$((hy - 52))'"
    done
  done
  echo "-attenuate 0.28 +noise Gaussian"
  echo "'$OUT/Linuxing-06-frost.jpg'"
} | xargs magick "$WORK/frost.png"

echo "wrote wallpapers to $OUT"
ls -1 "$OUT"
