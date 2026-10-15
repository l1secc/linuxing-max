#!/usr/bin/env bash
# ============================================================================
#  Linuxing Max · wallpaper generator
#
#  Produces the bundled 1920×1080 wallpapers. All of them are dark and
#  near-monochrome so they sit quietly behind the glass UI and read well under
#  every one of the four colour schemes (green / blue / white / red).
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

# --- 01 · terminal -----------------------------------------------------------
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

# --- 02 · circuit -------------------------------------------------------------
# Faint circuit traces and pads on black.
{
  echo "-size ${W}x${H} xc:'#070809'"
  echo "-fill none -stroke '#18232e' -strokewidth 2"
  for i in $(seq 1 24); do
    x1=$(( RANDOM % W )); y1=$(( RANDOM % H )); x2=$(( x1 + (RANDOM % 240 - 120) )); y2=$(( y1 + (RANDOM % 240 - 120) ))
    echo "-draw 'line $x1,$y1 $x2,$y2'"
  done
  echo "-fill '#1c2c3a' -stroke none"
  for i in $(seq 1 40); do
    x=$(( RANDOM % W )); y=$(( RANDOM % H ))
    echo "-draw 'circle $x,$y $((x+5)),$y'"
  done
  echo "-attenuate 0.3 +noise Gaussian"
  echo "'$OUT/Linuxing-02-circuit.jpg'"
} | xargs magick

# --- 03 · network -------------------------------------------------------------
# A sparse node graph in dim teal.
{
  echo "-size ${W}x${H} xc:'#07090a'"
  echo "-fill none -stroke '#14303a' -strokewidth 1.5"
  for i in $(seq 1 40); do
    x1=$(( RANDOM % W )); y1=$(( RANDOM % H )); x2=$(( RANDOM % W )); y2=$(( RANDOM % H ))
    echo "-draw 'line $x1,$y1 $x2,$y2'"
  done
  echo "-fill '#1e4a58' -stroke none"
  for i in $(seq 1 70); do
    x=$(( RANDOM % W )); y=$(( RANDOM % H ))
    echo "-draw 'circle $x,$y $((x+3)),$y'"
  done
  echo "-attenuate 0.3 +noise Gaussian"
  echo "'$OUT/Linuxing-03-network.jpg'"
} | xargs magick

# --- 04 · matrix --------------------------------------------------------------
# Faint green glyph rain, far dimmer than the Hollywood cliché.
magick -size ${W}x${H} xc:'#050705' \
  -font "$MONO" -pointsize 22 -fill '#0d2f1d' \
  -annotate +0+0 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -font "$MONO" -pointsize 22 -fill '#0d2f1d' \
  -annotate +120+40 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +320+80 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +560+20 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +820+120 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +1120+60 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +1420+140 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -annotate +1680+90 "$(head -c 600 /dev/urandom | tr -dc '01' | head -c 500)" \
  -blur 0x1 -attenuate 0.3 +noise Gaussian \
  "$OUT/Linuxing-04-matrix.jpg"

# --- 05 · grid -----------------------------------------------------------------
# A quiet blueprint grid with a soft corner glow.
magick -size ${W}x${H} xc:'#08090b' \
  -fill none -stroke '#131a22' -strokewidth 1 \
  -draw "$(for x in $(seq 0 96 1920); do printf 'line %d,0 %d,1080 ' "$x" "$x"; done)" \
  -draw "$(for y in $(seq 0 96 1080); do printf 'line 0,%d 1920,%d ' "$y" "$y"; done)" \
  -fill '#0e1822' -stroke none -draw "circle 0,0 900,0" \
  -attenuate 0.3 +noise Gaussian \
  "$OUT/Linuxing-05-grid.jpg"

# --- 06 · glitch -----------------------------------------------------------------
# A few horizontal RGB-shifted bars over black.
magick -size ${W}x${H} xc:'#060606' \
  -fill '#101a12' -draw "rectangle 0,220 1920,246" \
  -fill '#120f16' -draw "rectangle 0,240 1920,252" \
  -fill '#0f1418' -draw "rectangle 0,680 1920,704" \
  -fill '#161014' -draw "rectangle 0,696 1920,708" \
  -fill '#0c1512' -draw "rectangle 0,540 1920,560" \
  -attenuate 0.4 +noise Gaussian \
  "$OUT/Linuxing-06-glitch.jpg"

# --- 07 · radar -----------------------------------------------------------------
# Concentric rings — a SOC / security scanner sweep.
magick -size ${W}x${H} radial-gradient:'#0b1115'-'#050606' \
  -fill none -stroke '#14232e' -strokewidth 1.5 \
  -draw "circle 960,540 960,140" \
  -draw "circle 960,540 960,340" \
  -draw "circle 960,540 960,640" \
  -draw "circle 960,540 960,940" \
  -stroke '#14232e' -draw "line 960,540 960,140" \
  -stroke '#1c3342' -draw "line 960,540 1460,40" \
  -fill '#1c4a3a' -stroke none -draw "circle 1180,380 1180,375" \
  -attenuate 0.3 +noise Gaussian \
  "$OUT/Linuxing-07-radar.jpg"

# --- 08 · hex -----------------------------------------------------------------
# A faint hexagon lattice.
{
  echo "-size ${W}x${H} xc:'#070808'"
  echo "-fill none -stroke '#131b22' -strokewidth 1"
  for row in $(seq 0 8); do
    y=$(( row * 140 - 60 ))
    for col in $(seq 0 12); do
      x=$(( col * 170 - (row % 2) * 85 ))
      echo "-draw 'polygon $x,$y $((x+85)),$((y-49)) $((x+170)),$y $((x+170)),$((y+98)) $((x+85)),$((y+147)) $x,$((y+98))'"
    done
  done
  echo "-attenuate 0.3 +noise Gaussian"
  echo "'$OUT/Linuxing-08-hex.jpg'"
} | xargs magick

echo "wrote wallpapers to $OUT"
ls -1 "$OUT"
