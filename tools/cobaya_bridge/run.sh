#!/usr/bin/env bash
# Wrapper to run the EFC bridge test against whatever Planck likelihoods
# have been installed by install.sh. Delegates to cobaya-run with the
# local venv and packages path.
#
# Usage:
#     ./run.sh minimize            # default: reduced yaml (in-sandbox)
#     ./run.sh minimize --full     # full yaml (needs plik_lite)
#     ./run.sh gr                  # GR reference minimize (reduced)
#     ./run.sh mcmc                # full MCMC (not recommended under 16 GB)

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

VENV="$HERE/.venv"
PACKAGES="$HERE/packages"

if [[ -d "$VENV" ]]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
fi

cmd="${1:-minimize}"
shift || true

YAML="$HERE/efc_bridge_reduced.yaml"
for a in "$@"; do
    if [[ "$a" == "--full" ]]; then
        YAML="$HERE/efc_bridge.yaml"
    fi
done

case "$cmd" in
    minimize)
        cobaya-run "$YAML" --minimize -f -p "$PACKAGES"
        ;;
    gr)
        TMP="$HERE/.efc_bridge_gr_tmp.yaml"
        python3 - <<PY
import re
with open("$YAML") as fh: t = fh.read()
t = re.sub(r'  Alens:\n(    .+\n)+', '  Alens:\n    value: 1.0\n    latex: A_\\\\mathrm{L}\n', t)
t = t.replace("output: chains/efc_bridge_reduced", "output: chains/efc_bridge_gr")
with open("$TMP", "w") as fh: fh.write(t)
PY
        cobaya-run "$TMP" --minimize -f -p "$PACKAGES"
        ;;
    mcmc)
        cobaya-run "$YAML" -p "$PACKAGES"
        ;;
    *)
        echo "usage: $0 {minimize|gr|mcmc} [--full]" >&2
        exit 1
        ;;
esac
