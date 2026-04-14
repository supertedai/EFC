# ============================================================
# EFC Nested Sampling — Environment Setup (Windows PowerShell)
# ============================================================
# Sets up: cobaya, dynesty, nautilus, Planck data, CAMB on Windows.
#
# PolyChord + MPI do NOT run natively on Windows — if you need them,
# use WSL2 (Windows Subsystem for Linux) and run setup_environment.sh
# from inside WSL instead.
#
# Usage (PowerShell, as user — not Administrator):
#   powershell -ExecutionPolicy Bypass -File .\setup_environment.ps1
#
# Author: Morten Magnusson / Symbiose Research
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "============================================"
Write-Host "EFC Nested Sampling — Environment Setup (Windows)"
Write-Host "============================================"

# ------------------------------------------------------------
# Step 0: Check Python
# ------------------------------------------------------------
Write-Host ""
Write-Host ">>> Step 0: Python check..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ from:"
    Write-Host "  https://www.python.org/downloads/windows/"
    Write-Host "  (Check 'Add Python to PATH' during installation)"
    exit 1
}
$pyVer = & $python.Source --version 2>&1
Write-Host "Found: $pyVer  ($($python.Source))"

# ------------------------------------------------------------
# Step 1: Virtual environment
# ------------------------------------------------------------
$VENV_PATH = Join-Path $HOME "efc_nested_venv"
$PACKAGES_PATH = if ($env:COBAYA_PACKAGES_PATH) {
    $env:COBAYA_PACKAGES_PATH
} else {
    Join-Path $HOME "cobaya_packages"
}

Write-Host ""
Write-Host ">>> Step 1: Virtual environment..."
if (-not (Test-Path $VENV_PATH)) {
    & $python.Source -m venv $VENV_PATH
    Write-Host "Created: $VENV_PATH"
} else {
    Write-Host "Exists:  $VENV_PATH"
}

$venvPython = Join-Path $VENV_PATH "Scripts\python.exe"
$venvPip    = Join-Path $VENV_PATH "Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: venv python missing at $venvPython"
    exit 1
}

# ------------------------------------------------------------
# Step 2: Core packages
# ------------------------------------------------------------
Write-Host ""
Write-Host ">>> Step 2: Core packages..."
& $venvPip install --upgrade pip setuptools wheel
& $venvPip install numpy scipy matplotlib

# ------------------------------------------------------------
# Step 3: Cosmology stack
# ------------------------------------------------------------
# CAMB on Windows needs gfortran from MSYS2 or a prebuilt wheel.
# The pip package ships wheels for recent Python versions on win_amd64.
Write-Host ""
Write-Host ">>> Step 3: Cosmology stack..."
& $venvPip install camb cobaya getdist

# ------------------------------------------------------------
# Step 4: Nested samplers (no MPI on native Windows)
# ------------------------------------------------------------
Write-Host ""
Write-Host ">>> Step 4: Nested samplers..."
& $venvPip install dynesty nautilus-sampler

Write-Host ""
Write-Host "NOTE: PolyChord + MPI are not installed on native Windows."
Write-Host "      Use WSL2 for PolyChord, or stick with dynesty / nautilus."

# ------------------------------------------------------------
# Step 5: Planck + BAO + SNe likelihood data (~2 GB)
# ------------------------------------------------------------
Write-Host ""
Write-Host ">>> Step 5: Likelihood data (~2 GB)..."
$env:COBAYA_PACKAGES_PATH = $PACKAGES_PATH

$cobayaInstall = Join-Path $VENV_PATH "Scripts\cobaya-install.exe"
if (-not (Test-Path $cobayaInstall)) {
    # Fall back to module invocation if the shim isn't present
    & $venvPython -m cobaya install "config\efc_polychord.yaml" --packages-path $PACKAGES_PATH --skip-global 2>&1 | Out-Host
    & $venvPython -m cobaya install "config\efc_polychord_reduced.yaml" --packages-path $PACKAGES_PATH --skip-global 2>&1 | Out-Host
} else {
    & $cobayaInstall "config\efc_polychord.yaml" --packages-path $PACKAGES_PATH --skip-global 2>&1 | Out-Host
    & $cobayaInstall "config\efc_polychord_reduced.yaml" --packages-path $PACKAGES_PATH --skip-global 2>&1 | Out-Host
}

# ------------------------------------------------------------
# Step 6: Verify
# ------------------------------------------------------------
Write-Host ""
Write-Host ">>> Step 6: Verification..."
$verifyScript = @'
import camb; print(f"CAMB {camb.__version__}")
import cobaya; print(f"cobaya {cobaya.__version__}")
import dynesty; print(f"dynesty {dynesty.__version__}")
import getdist; print(f"GetDist {getdist.__version__}")
try:
    import nautilus; print(f"nautilus {nautilus.__version__}")
except ImportError:
    print("nautilus: NOT INSTALLED")
print("PolyChord / MPI: not available on native Windows (use WSL)")
'@
& $venvPython -c $verifyScript

Write-Host ""
Write-Host "============================================"
Write-Host "Setup complete."
Write-Host ""
Write-Host "Activate the environment in new shells with:"
Write-Host "  & '$VENV_PATH\Scripts\Activate.ps1'"
Write-Host "  `$env:COBAYA_PACKAGES_PATH = '$PACKAGES_PATH'"
Write-Host ""
Write-Host "Run samplers:"
Write-Host "  python src\launch_dynesty.py --ncpu 8 --model both"
Write-Host "  python src\launch_nautilus.py --ncpu 8 --model both"
Write-Host ""
Write-Host "For PolyChord (MPI), use WSL2 and setup_environment.sh."
Write-Host "============================================"
