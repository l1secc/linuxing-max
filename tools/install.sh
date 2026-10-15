#!/usr/bin/env bash
# ============================================================================
#  Linuxing Max · bootstrap
#
#  Omarchy deliberately never runs code from an installed theme:
#  `omarchy theme install <url>` clones the repo, keeps every colour/config
#  file, drops the handful of files that would run code, and applies the theme.
#  So this script is the one-time, idempotent setup that puts the scheme
#  switcher (`linuxing-scheme`) on your PATH, installs the soft look
#  (rounded corners, blur, translucency, animations) and drops in a theme-set
#  hook so `omarchy theme update` / re-applying the theme keeps all of it
#  current.
#
#  Usage:
#    install.sh              install switcher, look and hook
#    install.sh --no-hook    install switcher and look only
#    install.sh --uninstall  remove everything this installed
# ============================================================================
set -euo pipefail

# This script lives in tools/, so the theme root is one level up from here —
# the same directory Omarchy cloned the repo into.
THEME_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
THEME_NAME="$(basename -- "$THEME_DIR")"
HOOK_DIR="$HOME/.config/omarchy/hooks/theme-set.d"
HOOK_FILE="$HOOK_DIR/$THEME_NAME.hook"

WITH_HOOK=1
for arg in "$@"; do
  case "$arg" in
    --no-hook) WITH_HOOK=0 ;;
    --uninstall) ;;
    -h | --help) sed -n '3,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [[ ${1:-} == "--uninstall" ]]; then
  rm -f "$HOOK_FILE"
  "$THEME_DIR/tools/linuxing-bootstrap" --uninstall
  echo "Removed $HOOK_FILE"
  exit 0
fi

# 1. Scheme switcher + soft look.
"$THEME_DIR/tools/linuxing-bootstrap"

# 2. A theme-set hook keeps all of it fresh whenever the theme is re-applied
#    (this is the user-owned hook mechanism Omarchy provides; a theme repo is
#    not allowed to install it by itself).
if (( WITH_HOOK )); then
  mkdir -p "$HOOK_DIR"
  cat >"$HOOK_FILE" <<'HOOK'
#!/usr/bin/env bash
# Keep the Linuxing Max switcher and soft look installed after the theme is
# (re)applied or updated.
[[ ${1:-} == linuxing-max ]] || exit 0
theme_dir="$HOME/.config/omarchy/themes/linuxing-max"
[[ -x $theme_dir/tools/linuxing-bootstrap ]] || exit 0
"$theme_dir/tools/linuxing-bootstrap" --quiet >/dev/null 2>&1 || true
HOOK
  chmod 755 "$HOOK_FILE"
  echo "✓ installed hook $HOOK_FILE"
fi

# 3. PATH check.
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "! note: $BIN_DIR is not on your PATH — add it to call 'linuxing-scheme' directly." >&2 ;;
esac

echo "Try:  linuxing-scheme  |  linuxing-scheme recon  |  linuxing-scheme list"
