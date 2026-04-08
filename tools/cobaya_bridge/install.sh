#!/usr/bin/env bash
# Self-contained install of the EFC bridge cobaya stack.
# Creates a local Python venv, installs cobaya + CAMB (+ optional MGCAMB),
# and runs cobaya-install for all Planck 2018 likelihoods that the current
# network environment can reach.
#
# Reusable: re-running skips what is already installed.
#
# Layout created under this directory (tools/cobaya_bridge/):
#     .venv/              local Python virtualenv
#     packages/           cobaya PACKAGES_DIR (Planck data + clik binaries)
#     chains/             cobaya run outputs
#     logs/               install logs
#
# Usage:
#     cd tools/cobaya_bridge
#     ./install.sh              # full install
#     ./install.sh --with-mgcamb # also try MGCAMB (warning: Python wrapper is
#                                 # known to be broken in the sfu-cosmo pip build)
#     ./install.sh --reduced     # only low-ell + lensing.native (no ESA download)

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

VENV="$HERE/.venv"
PACKAGES="$HERE/packages"
LOGS="$HERE/logs"
mkdir -p "$PACKAGES" "$LOGS" "$HERE/chains"

WITH_MGCAMB=0
REDUCED=0
for arg in "$@"; do
    case "$arg" in
        --with-mgcamb) WITH_MGCAMB=1 ;;
        --reduced)     REDUCED=1     ;;
        *) echo "unknown argument: $arg" >&2; exit 1 ;;
    esac
done

echo "[install] venv: $VENV"
if [[ ! -d "$VENV" ]]; then
    python3 -m venv "$VENV" || {
        echo "[install] python3-venv not installed. Falling back to system python."
        # If venv is unavailable we install into the system Python (best effort).
        VENV=""
    }
fi
if [[ -n "$VENV" ]]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
fi

echo "[install] upgrading pip / setuptools / wheel"
pip install --quiet --upgrade --ignore-installed wheel || true
pip install --quiet --upgrade pip setuptools 2>/dev/null || true

echo "[install] installing numpy / scipy / pyyaml"
pip install --quiet --ignore-installed numpy scipy pyyaml

echo "[install] installing cobaya + vanilla CAMB"
pip install --quiet cobaya camb

if [[ "$WITH_MGCAMB" == "1" ]]; then
    echo "[install] attempting MGCAMB (requires gfortran)"
    if ! command -v gfortran >/dev/null 2>&1; then
        echo "[install] gfortran not found — skip MGCAMB"
    else
        pip install --quiet "git+https://github.com/sfu-cosmo/MGCAMB.git" \
            2> "$LOGS/mgcamb_install.err" || echo "[install] MGCAMB build failed — check $LOGS/mgcamb_install.err"
    fi
    echo "[install] WARNING: the sfu-cosmo MGCAMB pip build has a broken Python"
    echo "[install]          wrapper in the Mu-Sigma code path; values set via"
    echo "[install]          CAMBparams.mu0 / .sigma0 / set_mgparams do not"
    echo "[install]          reach the Fortran backend. Only use this install"
    echo "[install]          if you can fix that binding (patch set_mgparams or"
    echo "[install]          switch to a custom theory wrapper)."
fi

echo "[install] installing Planck likelihoods into $PACKAGES"
YAML_FULL="$HERE/efc_bridge.yaml"
YAML_REDUCED="$HERE/efc_bridge_reduced.yaml"

if [[ "$REDUCED" == "1" ]]; then
    echo "[install] reduced mode: lowl + lensing.native only (no ESA download)"
    cobaya-install cobaya.likelihoods.planck_2018_lowl.TT \
                   cobaya.likelihoods.planck_2018_lowl.EE \
                   cobaya.likelihoods.planck_2018_lensing.native \
                   -p "$PACKAGES" --no-progress-bars \
                   2>&1 | tee "$LOGS/cobaya_install_reduced.log"
else
    echo "[install] full mode: lowl + plik_lite TTTEEE + lensing.clik + DESI BAO + Pantheon+"
    echo "[install]   (requires ESA pla.esac.esa.int to be reachable for Planck)"
    cobaya-install "$YAML_FULL" \
                   cobaya.likelihoods.bao.desi_2024_bao_all \
                   cobaya.likelihoods.sn.pantheonplus \
                   -p "$PACKAGES" --no-progress-bars \
                   2>&1 | tee "$LOGS/cobaya_install_full.log" || {
        echo "[install] full install failed (likely ESA network block on Planck high-ell)."
        echo "[install] retrying without plik_lite (BAO + Pantheon+ + reduced Planck)"
        cobaya-install cobaya.likelihoods.planck_2018_lowl.TT \
                       cobaya.likelihoods.planck_2018_lowl.EE \
                       cobaya.likelihoods.planck_2018_lensing.native \
                       cobaya.likelihoods.bao.desi_2024_bao_all \
                       cobaya.likelihoods.sn.pantheonplus \
                       -p "$PACKAGES" --no-progress-bars \
                       2>&1 | tee "$LOGS/cobaya_install_reduced.log"
    }
fi

echo
echo "[install] done."
echo "[install] to activate the environment later:"
if [[ -n "${VENV:-}" ]]; then
    echo "    source $VENV/bin/activate"
fi
echo "[install] to run:"
echo "    ./run.sh minimize           # reduced (in-sandbox)"
echo "    ./run.sh minimize --full    # requires plik_lite installed"
echo "    ./run.sh gr                 # GR reference, reduced data"
echo "    ./run.sh mcmc --K0m2        # full posterior over (K0, m^2) + BAO + Pantheon+"
