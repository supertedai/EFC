#!/bin/bash
# ============================================================
# EFC Nested Sampling — Environment Setup (Linux + macOS)
# ============================================================
# Sets up: cobaya, PolyChord, dynesty, nautilus, Planck data, CAMB.
#
# Detects Linux vs macOS and uses the right package manager
# (apt / brew) for MPI and gfortran.
#
# Usage:
#   chmod +x setup_environment.sh
#   ./setup_environment.sh
#
# For Windows, use setup_environment.ps1 instead.
#
# Author: Morten Magnusson / Symbiose Research
# ============================================================

set -e

echo "============================================"
echo "EFC Nested Sampling — Environment Setup"
echo "============================================"

OS="$(uname -s)"
case "$OS" in
    Linux*)   PLATFORM="linux" ;;
    Darwin*)  PLATFORM="macos" ;;
    *)        PLATFORM="unknown" ;;
esac
echo "Platform: $PLATFORM ($OS)"

PACKAGES_PATH="${COBAYA_PACKAGES_PATH:-$HOME/cobaya_packages}"
VENV_PATH="$HOME/efc_nested_venv"

# ------------------------------------------------------------
# Step 0: System dependencies (gfortran, MPI, pkg-config)
# ------------------------------------------------------------
echo ""
echo ">>> Step 0: System dependencies..."

if [ "$PLATFORM" = "macos" ]; then
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew not found. Install from https://brew.sh first:"
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    echo "Homebrew found: $(brew --version | head -1)"

    # gfortran ships in gcc on macOS
    brew list gcc &> /dev/null || brew install gcc
    brew list open-mpi &> /dev/null || brew install open-mpi
    brew list pkg-config &> /dev/null || brew install pkg-config
    echo "macOS system deps ready (gcc/gfortran, open-mpi, pkg-config)"

elif [ "$PLATFORM" = "linux" ]; then
    if command -v apt &> /dev/null; then
        # Debian/Ubuntu
        if ! command -v gfortran &> /dev/null || ! command -v mpicc &> /dev/null; then
            echo "Installing system deps via apt (requires sudo)..."
            sudo apt update
            sudo apt install -y gfortran libopenmpi-dev openmpi-bin pkg-config
        fi
    elif command -v dnf &> /dev/null; then
        # Fedora/RHEL
        if ! command -v gfortran &> /dev/null || ! command -v mpicc &> /dev/null; then
            echo "Installing system deps via dnf (requires sudo)..."
            sudo dnf install -y gcc-gfortran openmpi-devel pkgconfig
        fi
    else
        echo "WARNING: Unknown Linux distro. Install manually:"
        echo "  - gfortran, libopenmpi-dev, pkg-config"
    fi
    echo "Linux system deps ready"
else
    echo "WARNING: Unknown platform '$OS'. Skipping system deps."
fi

# ------------------------------------------------------------
# Step 1: Python virtual environment
# ------------------------------------------------------------
echo ""
echo ">>> Step 1: Virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "Created: $VENV_PATH"
else
    echo "Exists: $VENV_PATH"
fi
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"

# ------------------------------------------------------------
# Step 2: Python core packages
# ------------------------------------------------------------
echo ""
echo ">>> Step 2: Core packages..."
pip install --upgrade pip setuptools wheel
pip install numpy scipy matplotlib

# ------------------------------------------------------------
# Step 3: Cosmology stack
# ------------------------------------------------------------
echo ""
echo ">>> Step 3: Cosmology stack..."
pip install camb cobaya getdist

# ------------------------------------------------------------
# Step 4: Nested samplers
# ------------------------------------------------------------
echo ""
echo ">>> Step 4: Nested samplers..."
pip install dynesty nautilus-sampler

if command -v mpicc &> /dev/null; then
    echo "MPI found: $(mpicc --version 2>&1 | head -1)"
    pip install mpi4py pypolychord
    echo "PolyChord installed with MPI support"
else
    echo "WARNING: No MPI compiler on PATH."
    if [ "$PLATFORM" = "macos" ]; then
        echo "  Fix: brew install open-mpi"
    elif [ "$PLATFORM" = "linux" ]; then
        echo "  Fix: sudo apt install libopenmpi-dev openmpi-bin"
    fi
    echo "  (dynesty and nautilus work without MPI.)"
fi

# ------------------------------------------------------------
# Step 5: Planck + BAO + SNe likelihood data (~2 GB)
# ------------------------------------------------------------
echo ""
echo ">>> Step 5: Likelihood data (~2 GB)..."
export COBAYA_PACKAGES_PATH="$PACKAGES_PATH"

cobaya-install config/efc_polychord.yaml --packages-path "$PACKAGES_PATH" --skip-global 2>&1 || true
cobaya-install config/efc_polychord_reduced.yaml --packages-path "$PACKAGES_PATH" --skip-global 2>&1 || true

# ------------------------------------------------------------
# Step 6: Verify
# ------------------------------------------------------------
echo ""
echo ">>> Step 6: Verification..."
python3 -c "
import camb; print(f'CAMB {camb.__version__}')
import cobaya; print(f'cobaya {cobaya.__version__}')
import dynesty; print(f'dynesty {dynesty.__version__}')
import getdist; print(f'GetDist {getdist.__version__}')
try:
    import nautilus; print(f'nautilus {nautilus.__version__}')
except ImportError:
    print('nautilus: NOT INSTALLED')
try:
    import pypolychord; print('PolyChord: OK')
except ImportError:
    print('PolyChord: NOT INSTALLED (use dynesty or nautilus)')
try:
    from mpi4py import MPI; print(f'MPI: {MPI.Get_library_version().strip()}')
except ImportError:
    print('MPI: NOT INSTALLED')
"

echo ""
echo "============================================"
echo "Setup complete."
echo ""
echo "Activate the environment in new shells with:"
echo "  source $VENV_PATH/bin/activate"
echo "  export COBAYA_PACKAGES_PATH=$PACKAGES_PATH"
echo ""
echo "PolyChord (MPI, recommended):"
echo "  mpirun -n 32 python src/launch_polychord.py"
echo ""
echo "dynesty (no MPI, fallback):"
echo "  python src/launch_dynesty.py --ncpu 16 --model both"
echo ""
echo "nautilus (low-RAM, degeneracy-tolerant):"
echo "  python src/launch_nautilus.py --ncpu 8 --model both"
echo ""
echo "Expected wall time: 48-96h (PolyChord), 72-120h (dynesty), 24-48h (nautilus)"
echo "============================================"
