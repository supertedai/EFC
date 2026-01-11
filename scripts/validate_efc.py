"""
validate_efc.py
----------------
Kjører en enkel validering av EFC-modellen mot mock-data
(JWST, DESI, SPARC) og sammenligner med et ΛCDM-baseline.
Koden er designet for å vise struktur og prinsipp – ikke nøyaktige observasjonsdata.

Bruk:
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
    """Returnerer et mock-datasett basert på valgt type."""
    np.random.seed(42)
    z = np.linspace(0, 5, 50)

    if name == "jwst":
        # Simulerer early-galaxy luminosity–density trend
        observed = np.exp(-z) + np.random.normal(0, 0.05, len(z))
        label = "JWST early galaxies"
    elif name == "desi":
        # BAO-lignende avstand–redshift-kurve
        observed = np.sin(z) / z + np.random.normal(0, 0.03, len(z))
        label = "DESI BAO"
    elif name == "sparc":
        # Rotasjonskurver – flat mot radial distanse
        z = np.linspace(0, 30, 50)
        observed = 1 - np.exp(-z/5) + np.random.normal(0, 0.02, len(z))
        label = "SPARC rotation curves"
    else:
        raise ValueError(f"Ukjent datasett: {name}")

    return pd.DataFrame({"z": z, "obs": observed, "label": label})

# ----------------------------
# 2. EFC-MODELL
# ----------------------------

def efc_prediction(z):
    """
    Enkel EFC-baseline-prediksjon for observasjonsdata.
    Konverterer rødforskyvning z → simplifisert energiflyt.
    """

    # placeholder fysikk — fjernes når du legger inn EFC-D
    rho = 1e-26 * (1 + z)
    S = 0.5 + 0.1 * z

    from src.efc.potential.efc_potential import compute_energy_flow
    Ef = compute_energy_flow(rho, S)

    return Ef


# ----------------------------
# 3. ΛCDM-BENCHMARK
# ----------------------------

def lcdm_prediction(z, H0=70, Ωm=0.3, ΩΛ=0.7):
    """Standard kosmologi: H(z) = H0 * sqrt(Ωm*(1+z)^3 + ΩΛ)"""
    return H0 * np.sqrt(Ωm * (1 + z)**3 + ΩΛ) / H0

# ----------------------------
# 4. VALIDERING
# ----------------------------

def validate(dataset_name):
    data = load_dataset(dataset_name)
    z = data["z"].values

    efc_vals = efc_prediction(z)
    lcdm_vals = lcdm_prediction(z)

    # Sammenligning (r^2)
    corr_efc = np.corrcoef(data["obs"], efc_vals)[0, 1]
    corr_lcdm = np.corrcoef(data["obs"], lcdm_vals)[0, 1]

    print(f"\nDataset: {dataset_name.upper()}")
    print(f"  Corr(EFC, observed)  = {corr_efc:.3f}")
    print(f"  Corr(ΛCDM, observed) = {corr_lcdm:.3f}")

    # Plot resultater
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
    print(f"  → Plot lagret i {outdir}/validation_{dataset_name}.png")

# ----------------------------
# 5. MAIN
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="jwst",
                        help="jwst | desi | sparc")
    args = parser.parse_args()
    validate(args.dataset)
