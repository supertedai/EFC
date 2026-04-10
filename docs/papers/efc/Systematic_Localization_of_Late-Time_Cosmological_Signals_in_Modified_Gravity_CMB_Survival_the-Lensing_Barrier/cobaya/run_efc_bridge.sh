#!/usr/bin/env bash
# Run the EFC bridge test with full Planck plik_lite + lowl + lensing.clik
# and free cosmology + free (mu0, Sigma0).
#
# Reproduces the Δchi² = -0.45 best-fit from the Localization paper
# (DOI: 10.6084/m9.figshare.31368433, Phase 2 "minimize_free_cosmo")
# and pins down the sweet spot referenced in Kill-Test v5.
#
# Prerequisites:
#   * cobaya    >= 3.5
#   * MGCAMB    v1.5.2  (installed in place of vanilla CAMB)
#   * Planck 2018 high-ell plik_lite TTTEEE data
#   * Planck 2018 lowl TT + EE data
#   * Planck 2018 lensing clik data
#   * ~16 GB RAM for --minimize, ~32 GB for full MCMC
#
# Usage:
#   ./run_efc_bridge.sh install          # install likelihoods into PACKAGES_DIR
#   ./run_efc_bridge.sh minimize         # best-fit (reproduces Δchi² ≈ -0.45)
#   ./run_efc_bridge.sh mcmc             # full MCMC posterior
#   ./run_efc_bridge.sh gr               # GR reference run (mu0=Sigma0=1 fixed)

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
YAML="$HERE/efc_bridge.yaml"
PACKAGES_DIR="${COBAYA_PACKAGES:-$HOME/cobaya_packages}"

cmd="${1:-minimize}"

case "$cmd" in
  install)
    cobaya-install "$YAML" -p "$PACKAGES_DIR"
    ;;
  minimize)
    cobaya-run "$YAML" --minimize -p "$PACKAGES_DIR" -f
    ;;
  mcmc)
    cobaya-run "$YAML" -p "$PACKAGES_DIR"
    ;;
  gr)
    # Run the same likelihoods with mu0 and Sigma0 pinned to 1 to establish
    # the GR reference chi2 used in the Δchi² computation.
    TMP_YAML="$HERE/.efc_bridge_gr.yaml"
    python3 - <<PY
import re, sys
with open("$YAML") as fh:
    txt = fh.read()
# Replace the mu0 and Sigma0 blocks with fixed values.
def fix_block(src, name, val):
    pat = re.compile(rf'(  {name}:\n(?:    .+\n)+)', re.M)
    return pat.sub(f'  {name}:\n    value: {val}\n    latex: \\\\{name[0]}_0\n', src)
txt = fix_block(txt, 'mu0', 1.0)
txt = fix_block(txt, 'Sigma0', 1.0)
# Distinct output folder for the GR run
txt = txt.replace("output: chains/efc_bridge", "output: chains/efc_bridge_gr")
with open("$TMP_YAML", "w") as fh:
    fh.write(txt)
PY
    cobaya-run "$TMP_YAML" --minimize -p "$PACKAGES_DIR" -f
    ;;
  *)
    echo "usage: $0 {install|minimize|mcmc|gr}" >&2
    exit 1
    ;;
esac
