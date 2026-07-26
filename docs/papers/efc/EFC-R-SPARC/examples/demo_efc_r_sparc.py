"""demo_efc_r_sparc.py

Demonstration of the EFC-R framework applied to two synthetic
galaxy archetypes:
  1. LSB (low surface brightness) dwarf  -- flow-dominated regime
  2. Barred spiral                       -- latent-significant regime

Reproduces the qualitative findings of Magnusson (2026).
"""

import numpy as np

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from efc_r_sparc import (
    effective_energy_field,
    rotation_velocity,
    efc_r_decomposition,
    latent_field_proxy,
    classify_regime,
    reduced_chi2,
)

# ----- helpers -----
def mock_observed(V_true, noise_frac=0.05, seed=42):
    rng = np.random.default_rng(seed)
    err = noise_frac * V_true.mean() * np.ones_like(V_true)
    return V_true + rng.normal(0, err), err


# === Galaxy 1: LSB dwarf (flow-dominated) ===
print("===== Galaxy 1: LSB Dwarf =====")
r1 = np.linspace(0.1, 15.0, 150) * 1e3  # pc
rho1 = 5e-3 * np.exp(-r1 / 6e3)
S1 = 0.25 * np.ones_like(r1)  # low, uniform entropy

E_f1 = effective_energy_field(rho1, S1)
V_efc1 = rotation_velocity(r1, E_f1)

# "observed" = pure EFC + small noise (EFC should work well)
V_obs1, V_err1 = mock_observed(V_efc1, noise_frac=0.03)

Lp1 = latent_field_proxy(V_obs1, V_efc1)
reg1 = classify_regime(Lp1)
chi2_1 = reduced_chi2(V_obs1, V_efc1, V_err1)
print(f"  Latent proxy  = {Lp1:.4f}")
print(f"  Regime        = {reg1}")
print(f"  Reduced chi^2 = {chi2_1:.2f}")

# === Galaxy 2: Barred spiral (latent-significant) ===
print("\n===== Galaxy 2: Barred Spiral =====")
r2 = np.linspace(0.1, 25.0, 200) * 1e3
rho2 = 2e-2 * np.exp(-r2 / 4e3)
# Bar introduces entropy gradient + extra mass-like feature
S2 = 0.3 + 0.35 * np.exp(-((r2 - 5e3) ** 2) / (2e3**2))
S2 = np.clip(S2, 0, 1)

E_f2 = effective_energy_field(rho2, S2)
V_efc2 = rotation_velocity(r2, E_f2)

# "observed" has significant bar-driven excess EFC cannot capture
bar_bump = 25.0 * np.exp(-((r2 - 5e3) ** 2) / (1.5e3**2))
V_true2 = np.sqrt(V_efc2**2 + bar_bump**2)
V_obs2, V_err2 = mock_observed(V_true2, noise_frac=0.04)

Lp2 = latent_field_proxy(V_obs2, V_efc2)
reg2 = classify_regime(Lp2)
chi2_2 = reduced_chi2(V_obs2, V_efc2, V_err2)
print(f"  Latent proxy  = {Lp2:.4f}")
print(f"  Regime        = {reg2}")
print(f"  Reduced chi^2 = {chi2_2:.2f}")

# === EFC-R correction for Galaxy 2 ===
print("\n--- Applying EFC-R correction (latent_fraction=0.12) ---")
_, _, E_tot2 = efc_r_decomposition(rho2, S2, latent_fraction=0.12)
V_efcr2 = rotation_velocity(r2, E_tot2)
Lp2r = latent_field_proxy(V_obs2, V_efcr2)
chi2_2r = reduced_chi2(V_obs2, V_efcr2, V_err2)
print(f"  Latent proxy (EFC-R) = {Lp2r:.4f}")
print(f"  Reduced chi^2       = {chi2_2r:.2f}")

# === Summary table ===
print("\n===== Summary =====")
print(f"{'Galaxy':<20} {'L_proxy':>8} {'Regime':<20} {'chi2_red':>8}")
print(f"{'LSB Dwarf':<20} {Lp1:>8.4f} {reg1:<20} {chi2_1:>8.2f}")
print(f"{'Barred Spiral':<20} {Lp2:>8.4f} {reg2:<20} {chi2_2:>8.2f}")
print(f"{'Barred (EFC-R)':<20} {Lp2r:>8.4f} {classify_regime(Lp2r):<20} {chi2_2r:>8.2f}")

# === Optional plot ===
if HAS_MPL:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.set_title("LSB Dwarf (flow-dominated)")
    ax.errorbar(r1 / 1e3, V_obs1, yerr=V_err1, fmt=".", alpha=0.4, label="Observed")
    ax.plot(r1 / 1e3, V_efc1, "r-", lw=2, label="EFC")
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel(r"$V_{\rm rot}$ [km/s]")
    ax.legend()

    ax = axes[1]
    ax.set_title("Barred Spiral (latent-significant)")
    ax.errorbar(r2 / 1e3, V_obs2, yerr=V_err2, fmt=".", alpha=0.4, label="Observed")
    ax.plot(r2 / 1e3, V_efc2, "r-", lw=2, label="EFC")
    ax.plot(r2 / 1e3, V_efcr2, "b--", lw=2, label="EFC-R")
    ax.set_xlabel("r [kpc]")
    ax.legend()

    plt.tight_layout()
    plt.savefig("efc_r_sparc_demo.png", dpi=150)
    print("\nPlot saved to efc_r_sparc_demo.png")
    plt.show()
