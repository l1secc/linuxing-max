#!/usr/bin/env bash
# ============================================================================
#  Linuxing Max · one-command install
#
#  Pulls the theme through Omarchy's own installer, then runs its bootstrap so
#  the scheme switcher lands on your PATH. Run it without cloning first:
#
#    bash <(curl -fsSL https://raw.githubusercontent.com/l1secc/linuxing-max/main/tools/bootstrap.sh)
#
#  Set LINUXING_REPO to use a fork, LINUXING_NO_BOOTSTRAP=1 to skip the
#  bootstrap.
# ============================================================================
set -euo pipefail

REPO="${LINUXING_REPO:-https://github.com/l1secc/linuxing-max.git}"
THEME_DIR="$HOME/.config/omarchy/themes/linuxing-max"

# `omarchy theme install` removes any existing theme dir before cloning, so
# refuse to run from inside a checkout (that checkout is the thing it deletes).
# This script lives in tools/, so the checkout root is one level up.
self="${BASH_SOURCE[0]:-}"
if [[ -f $self ]]; then
  self_root="$(cd -- "$(dirname -- "$self")/.." && pwd)"
  if [[ $self_root == "$THEME_DIR" ]]; then
    echo "This is a local checkout. Run ./tools/install.sh instead; it will not re-clone." >&2
    exit 1
  fi
fi

echo "Installing Linuxing Max from $REPO …"
omarchy theme install "$REPO"

if [[ ${LINUXING_NO_BOOTSTRAP:-0} != 1 && -x "$THEME_DIR/tools/install.sh" ]]; then
  "$THEME_DIR/tools/install.sh"
fi

echo
echo "Done. Open the desktop theme with:  omarchy theme set 'Linuxing Max'"
echo "Switch whole-system colour schemes with:  linuxing-scheme"
