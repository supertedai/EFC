#!/bin/bash
# ============================================================
# EFC Nested Sampling — One-Line Bootstrap
# ============================================================
# Single-command setup for a fresh Mac or Linux machine.
# Clones the repo (or reuses an existing clone), checks out the
# right branch, installs everything.
#
# Usage (from anywhere):
#   curl -fsSL https://raw.githubusercontent.com/supertedai/EFC/claude/update-neo4j-modules-LWO6Y/pipelines/efc/nested_sampling/bootstrap.sh | bash
#
# Or if you've already downloaded it:
#   bash bootstrap.sh
#
# Env vars (optional):
#   EFC_DIR    = where to clone (default: $HOME/EFC)
#   EFC_BRANCH = which branch (default: claude/update-neo4j-modules-LWO6Y)
# ============================================================

set -e

EFC_DIR="${EFC_DIR:-$HOME/EFC}"
EFC_BRANCH="${EFC_BRANCH:-claude/update-neo4j-modules-LWO6Y}"
REPO_URL="https://github.com/supertedai/EFC.git"

echo "============================================"
echo "EFC Nested Sampling — Bootstrap"
echo "============================================"
echo "Target directory: $EFC_DIR"
echo "Branch:           $EFC_BRANCH"
echo ""

# ------------------------------------------------------------
# Step 1: Check git
# ------------------------------------------------------------
if ! command -v git &> /dev/null; then
    echo "ERROR: git not found. Install it first:"
    case "$(uname -s)" in
        Darwin*) echo "  xcode-select --install" ;;
        Linux*)  echo "  sudo apt install git   # or: sudo dnf install git" ;;
    esac
    exit 1
fi

# ------------------------------------------------------------
# Step 2: Clone or reuse
# ------------------------------------------------------------
if [ -d "$EFC_DIR/.git" ]; then
    echo ">>> Reusing existing clone at $EFC_DIR"
    cd "$EFC_DIR"
    git fetch origin "$EFC_BRANCH"
    git checkout "$EFC_BRANCH"
    git pull origin "$EFC_BRANCH"
elif [ -e "$EFC_DIR" ]; then
    echo "ERROR: $EFC_DIR exists but is not a git repo."
    echo "Set EFC_DIR to a different path, or remove $EFC_DIR first."
    exit 1
else
    echo ">>> Cloning $REPO_URL into $EFC_DIR"
    git clone --branch "$EFC_BRANCH" "$REPO_URL" "$EFC_DIR"
    cd "$EFC_DIR"
fi

# ------------------------------------------------------------
# Step 3: Run cross-platform setup
# ------------------------------------------------------------
cd "$EFC_DIR/pipelines/efc/nested_sampling"
echo ""
echo ">>> Running setup.py (detects OS, installs cosmology stack)..."
echo ""

# Pick the first python3 on PATH
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
    echo "ERROR: python3 not found on PATH."
    exit 1
fi

"$PY" setup.py

echo ""
echo "============================================"
echo "Bootstrap complete."
echo ""
echo "Activate the environment:"
echo "  source ~/efc_nested_venv/bin/activate"
echo "  export COBAYA_PACKAGES_PATH=~/cobaya_packages"
echo ""
echo "Run smoke test (30 seconds, no Planck data needed):"
echo "  cd $EFC_DIR/pipelines/efc/nested_sampling"
echo "  python tests/test_nautilus_smoke.py"
echo ""
echo "Run full nautilus sampler (24-48h):"
echo "  python src/launch_nautilus.py --ncpu 8 --model both --reduced"
echo "============================================"
