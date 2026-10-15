#!/usr/bin/env bash
# ============================================================================
#  Linuxing Max · wallpaper generator
#
#  Produces the bundled 1920×1080 wallpapers. Every one is a hacker / developer
#  / Linux / Omarchy terminal scene in the style of the first photo, all in the
#  SAME green palette so the whole system stays one coherent look.
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

# ============================================================================
#  scene <out> — draws the same green terminal panel, reading
#  "colour|y|size|b-or-r|text" lines from stdin
# ============================================================================
scene() {
  local out=$1
  local -a cmd=(
    magick -size ${W}x${H} radial-gradient:'#101613'-'#050706'
    -fill '#0a100c' -stroke '#1c2a21' -strokewidth 1 -draw "roundrectangle 420,190 1500,890 20,20"
    -fill '#060a07' -draw "roundrectangle 420,190 1500,244 20,20"
    -fill '#1c2a21' -draw "circle 446,217 446,211"
    -fill '#2a3d31' -draw "circle 486,217 486,211"
    -fill '#3d2a2e' -draw "circle 526,217 526,211"
    -gravity NorthWest -font "$MONO"
  )
  local color y size w text
  while IFS='|' read -r color y size w text; do
    [[ -z ${color// /} ]] && continue
    cmd+=(-fill "$color" -pointsize "$size")
    [[ $w == b ]] && cmd+=(-font "$MONO_B")
    cmd+=(-annotate "+460+$y" "$text")
    [[ $w == b ]] && cmd+=(-font "$MONO")
  done
  cmd+=(-attenuate 0.3 +noise Gaussian "$out")
  "${cmd[@]}"
}

# ------------------------------------------------------------------ 02 recon
scene "$OUT/Linuxing-02-recon.jpg" <<'LINES'
#3ddc84|300|26|b|linuxing@max:~$ nmap -sV 10.10.10.0/24
#5f7366|348|24||Starting Nmap 7.95 ( https://nmap.org )
#9fb3a6|392|24||Nmap scan report for gateway (10.10.10.1)
#7ce8a8|436|24||22/tcp    open     ssh        OpenSSH 9.8p1
#7ce8a8|480|24||80/tcp    open     http       nginx 1.27.3
#7ce8a8|524|24||443/tcp   open     ssl/https  TLS 1.3
#ff7a93|568|24||3306/tcp  closed   mysql
#f0d9a0|612|24||8080/tcp  filtered http-proxy
#5f7366|660|24||Nmap done: 256 IPs (12 hosts up) scanned in 8.4s
#3ddc84|740|26|b|linuxing@max:~$ _
LINES

# -------------------------------------------------------------- 03 developer
scene "$OUT/Linuxing-03-developer.jpg" <<'LINES'
#3ddc84|300|26|b|linuxing@max:~/linuxing-max$ git log --oneline --graph
#f0d9a0|348|24||* 23cdefd (HEAD -> main) photo-driven schemes
#f0d9a0|392|24||* d3146dd fix: drop unsupported animation leaf
#f0d9a0|436|24||* 66f8b20 starter theme: whole-system schemes
#f0d9a0|480|24||* 5f1a9c2 initial commit
#3ddc84|560|26|b|linuxing@max:~/linuxing-max$ git status
#9fb3a6|608|24||On branch main
#5f7366|652|24||Your branch is up to date with 'origin/main'.
#7ce8a8|696|24||nothing to commit, working tree clean
#3ddc84|770|26|b|linuxing@max:~/linuxing-max$ _
LINES

# ------------------------------------------------------------------ 04 editor
scene "$OUT/Linuxing-04-editor.jpg" <<'LINES'
#3ddc84|300|26|b|linuxing@max:~/linuxing-max$ cat tools/linuxing_generate.py
#5f7366|348|24||#!/usr/bin/env python3
#5f7366|392|24||# Linuxing Max - wallpaper-driven schemes
#82c8ff|448|24||def retint(photo):
#9fb3a6|492|24||    palette = extract(photo)
#82c8ff|536|24||    for surface in system:
#9fb3a6|580|24||        surface.paint(palette.accent)
#82c8ff|624|24||    return palette
#82c8ff|688|24||if __name__ == "__main__":
#9fb3a6|732|24||    retint(sys.argv[1])
#3ddc84|800|26|b|linuxing@max:~/linuxing-max$ _
LINES

# -------------------------------------------------------------------- 05 root
scene "$OUT/Linuxing-05-root.jpg" <<'LINES'
#3ddc84|296|26|b|root@max:/# systemctl status firewall
#9fb3a6|344|24||* firewall.service - Linuxing Max packet filter
#7ce8a8|388|24||     Active: active (running) since Fri 2026-10-15
#9fb3a6|432|24||    Drop: 14,203 packets    Pass: 982,441 packets
#3ddc84|516|26|b|root@max:/# tail -f /var/log/auth.log
#ff7a93|564|24||Failed password for root from 10.0.0.5 port 22 ssh2
#7ce8a8|608|24||Accepted publickey for l1sec from 10.0.0.9 port 22
#5f7366|652|24||pam_unix(sshd:session): session opened for user l1sec
#ff7a93|696|24||Failed password for invalid user admin from 10.0.0.9
#7ce8a8|740|24||sshd: error: maximum authentication attempts exceeded
#3ddc84|808|26|b|root@max:/# _
LINES

# ----------------------------------------------------------------- 06 omarchy
scene "$OUT/Linuxing-06-omarchy.jpg" <<'LINES'
#3ddc84|296|26|b|linuxing@max:~$ sudo pacman -Sy omarchy-theme
#5f7366|344|24||:: Synchronising package databases...
#5f7366|388|24||resolving dependencies, looking for conflicting packages...
#9fb3a6|432|24||Packages (2) linuxing-max-6.0-1  linuxing-max-walls-6.0-1
#5f7366|480|24||Total Download Size:  3.16 MiB
#5f7366|528|24||:: Proceed with installation? [Y/n] Y
#9fb3a6|576|24||linuxing-max-6.0-1       261.2 KiB  1.2MiB/s  00:00
#3ddc84|624|24||:: Running post-transaction hooks...
#7ce8a8|672|24||[ ok ] activating theme linuxing-max
#7ce8a8|712|24||[ ok ] retinting shell, terminal and gtk apps
#5f7366|760|24||==> enjoy Linuxing Max - linuxing@max:~$ _
LINES

echo "wrote wallpapers to $OUT"
ls -1 "$OUT"
