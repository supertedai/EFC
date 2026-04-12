#!/bin/bash
# ============================================================
# EFC Nested Sampling — Environment Setup
# ============================================================
# Sets up: cobaya, PolyChord, dynesty, Planck data, CAMB.
#
# Usage:
#   chmod +x setup_environment.sh
#   ./setup_environment.sh
#
# Author: Morten Magnusson / Symbiose Research
# Date:   2026-04-12
# ============================================================

set -e

echo "============================================"
echo "EFC Nested Sampling — Environment Setup"
echo "============================================"

PACKAGES_PATH="${COBAYA_PACKAGES_PATH:-$HOME/cobaya_packages}"
VENV_PATH="$HOME/efc_nested_venv"

# Step 1: Virtual environment
echo ""
echo ">>> Step 1: Virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "Created: $VENV_PATH"
else
    echo "Exists: $VENV_PATH"
fi
source "$VENV_PATH/bin/activate"

# Step 2: Core packages
echo ""
echo ">>> Step 2: Core packages..."
pip install --upgrade pip setuptools wheel
pip install numpy scipy matplotlib

# Step 3: Cosmology stack
echo ""
echo ">>> Step 3: Cosmology stack..."
pip install camb cobaya getdist

# Step 4: Nested samplers
echo ""
echo ">>> Step 4: Nested samplers..."
pip install dynesty

if command -v mpicc &> /dev/null; then
    echo "MPI found: $(mpicc --version 2>&1 | head -1)"
    pip install mpi4py pypolychord
    echo "PolyChord installed with MPI support"
else
    echo "WARNING: No MPI compiler. PolyChord needs:"
    echo "  sudo apt install libopenmpi-dev openmpi-bin"
    echo "dynesty works without MPI."
fi

# Step 5: Planck + BAO + SNe likelihood data
echo ""
echo ">>> Step 5: Likelihood data (~2 GB)..."
export COBAYA_PACKAGES_PATH="$PACKAGES_PATH"

# Use the full MGCAMB config to install all likelihoods
cobaya-install config/efc_polychord.yaml --packages-path "$PACKAGES_PATH" --skip-global 2>&1 || true

# Also install reduced-run likelihoods
cobaya-install config/efc_polychord_reduced.yaml --packages-path "$PACKAGES_PATH" --skip-global 2>&1 || true

# Step 6: Verify
echo ""
echo ">>> Step 6: Verification..."
python3 -c "
import camb; print(f'CAMB {camb.__version__}')
import cobaya; print(f'cobaya {cobaya.__version__}')
import dynesty; print(f'dynesty {dynesty.__version__}')
import getdist; print(f'GetDist {getdist.__version__}')
try:
    import pypolychord; print('PolyChord: OK')
except ImportError:
    print('PolyChord: NOT INSTALLED (use dynesty)')
try:
    from mpi4py import MPI; print(f'MPI: {MPI.Get_library_version().strip()}')
except ImportError:
    print('MPI: NOT INSTALLED')
"

echo ""
echo "============================================"
echo "Setup complete."
echo ""
echo "PolyChord (MPI, recommended):"
echo "  source $VENV_PATH/bin/activate"
echo "  export COBAYA_PACKAGES_PATH=$PACKAGES_PATH"
echo "  mpirun -n 32 python src/launch_polychord.py"
echo ""
echo "dynesty (no MPI, fallback):"
echo "  source $VENV_PATH/bin/activate"
echo "  export COBAYA_PACKAGES_PATH=$PACKAGES_PATH"
echo "  python src/launch_dynesty.py --ncpu 16 --model both"
echo ""
echo "Expected: 48-96h (PolyChord), 72-120h (dynesty)"
echo "============================================"
