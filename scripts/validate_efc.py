"""
validate_efc.py
----------------
Runs a simple validation of the EFC model against mock data
(JWST, DESI, SPARC) and compares with a ΛCDM baseline.
The code is designed to show structure and principle – not accurate observational data.

Usage:
    python3 scripts/validate_efc.py --dataset jwst
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.efc.core.efc_core import EFCModel, EFCParameters

# ----------------------------
# 1. MOCK-DATA GENERATOR
# ----------------------------

def load_dataset(name):
    """Returns a mock dataset based on the chosen type."""
    np.random.seed(42)
    z = np.linspace(0, 5, 50)

    if name == "jwst":
        # Simulates an early-galaxy luminosity–density trend
        observed = np.exp(-z) + np.random.normal(0, 0.05, len(z))
        label = "JWST early galaxies"
    elif name == "desi":
        # BAO-like distance–redshift curve
        observed = np.sin(z) / z + np.random.normal(0, 0.03, len(z))
        label = "DESI BAO"
    elif name == "sparc":
        # Rotation curves – flat against radial distance
        z = np.linspace(0, 30, 50)
        observed = 1 - np.exp(-z/5) + np.random.normal(0, 0.02, len(z))
        label = "SPARC rotation curves"
    else:
        raise ValueError(f"Unknown dataset: {name}")

    return pd.DataFrame({"z": z, "obs": observed, "label": label})

# ----------------------------
# 2. EFC MODEL
# ----------------------------

def efc_prediction(z):
    """
    Simple EFC baseline prediction for observational data.
    Converts redshift z → simplified energy flow.
    """

    # placeholder physics — remove once EFC-D is wired in
    rho = 1e-26 * (1 + z)
    S = 0.5 + 0.1 * z

    from src.efc.potential.efc_potential import compute_energy_flow
    Ef = compute_energy_flow(rho, S)

    return Ef


# ----------------------------
# 3. ΛCDM BENCHMARK
# ----------------------------

def lcdm_prediction(z, H0=70, Ωm=0.3, ΩΛ=0.7):
    """Standard cosmology: H(z) = H0 * sqrt(Ωm*(1+z)^3 + ΩΛ)"""
    return H0 * np.sqrt(Ωm * (1 + z)**3 + ΩΛ) / H0

# ----------------------------
# 4. VALIDATION
# ----------------------------

def validate(dataset_name):
    data = load_dataset(dataset_name)
    z = data["z"].values

    efc_vals = efc_prediction(z)
    lcdm_vals = lcdm_prediction(z)

    # Comparison (r^2)
    corr_efc = np.corrcoef(data["obs"], efc_vals)[0, 1]
    corr_lcdm = np.corrcoef(data["obs"], lcdm_vals)[0, 1]

    print(f"\nDataset: {dataset_name.upper()}")
    print(f"  Corr(EFC, observed)  = {corr_efc:.3f}")
    print(f"  Corr(ΛCDM, observed) = {corr_lcdm:.3f}")

    # Plot the results
    plt.figure(figsize=(6,4))
    plt.plot(z, data["obs"], "k.", label="Observed")
    plt.plot(z, efc_vals, "r-", label="EFC prediction")
    plt.plot(z, lcdm_vals, "b--", label="ΛCDM baseline")
    plt.xlabel("z (redshift or proxy)")
    plt.ylabel("Normalized signal")
    plt.title(f"EFC Validation – {dataset_name.upper()}")
    plt.legend()
    plt.tight_layout()

    outdir = Path("output")
    outdir.mkdir(exist_ok=True)
    plt.savefig(outdir / f"validation_{dataset_name}.png", dpi=200)
    print(f"  → Plot saved to {outdir}/validation_{dataset_name}.png")

# ----------------------------
# 5. MAIN
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="jwst",
                        help="jwst | desi | sparc")
    args = parser.parse_args()
    validate(args.dataset)
