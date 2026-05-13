#!/usr/bin/env python3
"""demo_rce_synthesis.py

Demonstrates the Regime-Closure Epistemology (RCE) framework from
Magnusson 2026 (DOI: 10.6084/m9.figshare.32256939).

Runs:
  1. RCE validity audit for a 4-regime cosmological model (L0-L3)
  2. Dark-X diagnostic: shows how a ledger gap arises and dissolves
  3. Cross-domain validation scoring for 7 pre-registered predictions
  4. Regime energy partition plot over redshift
"""
import numpy as np

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from rce_synthesis import (
    rce_validity, RCE_CONDITIONS, ashby_variety, variety_closure_check,
    conant_ashby_R, modelling_closure_check, frozen_param_fraction,
    frozen_governance_check, coupling_operator, dark_x_diagnostic,
    cross_domain_validation_score, regime_energy_partition,
    REGIME_LABELS_COSMOLOGY, REGIME_LABELS_MEDICINE, REGIME_LABELS_ECONOMICS,
)

print("=" * 65)
print("  RCE Demonstration — Magnusson 2026")
print("=" * 65)

# ------------------------------------------------------------------
# 1. RCE validity audit
# ------------------------------------------------------------------
print("\n[1] RCE Validity Audit (EFC L0-L3, N=4 regimes)")
conditions = {
    "regime_locality": True,
    "variety_closure_ashby": True,
    "modelling_closure_conant_ashby": True,
    "frozen_parameter_governance": True,
    "external_arbitration_beer": True,
}
valid = rce_validity(conditions, n_subsystems=4)
for c, v in conditions.items():
    print(f"  {c:42s} : {'PASS' if v else 'FAIL'}")
print(f"  => Overall RCE valid: {valid}")

print("\n  Ashby variety check:")
v_sys = ashby_variety(2**20)  # ~1M micro-states
v_reg = ashby_variety(2**22)  # regulator covers more
print(f"    V_system   = {v_sys:.1f} bits")
print(f"    V_regulator= {v_reg:.1f} bits  =>  closure: {variety_closure_check(v_reg, v_sys)}")

print("\n  Conant-Ashby modelling closure:")
R = conant_ashby_R(mutual_info=4.7, system_entropy=5.0)
print(f"    R = {R:.3f}  =>  closure (eps=0.05): {modelling_closure_check(R, 0.05)}")

print("\n  Frozen-parameter governance:")
frac = frozen_param_fraction(n_frozen=7, n_total=9)
print(f"    Frozen fraction = {frac:.2f}  =>  governance: {frozen_governance_check(frac)}")

# ------------------------------------------------------------------
# 2. Dark-X diagnostic
# ------------------------------------------------------------------
print("\n[2] Dark-X Diagnostic")
print("  Single-regime model (LCDM-like):")
delta, is_dark = dark_x_diagnostic(
    observed=100.0,
    regime_contributions=[5.0],   # baryonic only
    delta_crit=0.05,
)
print(f"    Ledger gap delta = {delta:.2%}  =>  dark-X symptom: {is_dark}")
print(f"    (The 95% gap is filled by 'dark matter' + 'dark energy')")

print("\n  Multi-regime model (EFC L0-L3):")
delta2, is_dark2 = dark_x_diagnostic(
    observed=100.0,
    regime_contributions=[5.0, 22.0, 45.0, 26.0],  # L0..L3
    delta_crit=0.05,
)
print(f"    Ledger gap delta = {delta2:.2%}  =>  dark-X symptom: {is_dark2}")
print(f"    Regime coupling closes the ledger mechanically.")

# ------------------------------------------------------------------
# 3. Cross-domain validation (7 pre-registered predictions)
# ------------------------------------------------------------------
print("\n[3] Cross-Domain Validation Score (7 predictions)")
pred_labels = [
    "Cosmo: H0 tension",
    "Cosmo: S8 tension",
    "Cosmo: BAO feature",
    "Med: M0-M1 cortisol",
    "Med: M2-M3 HRV",
    "Econ: E1-E2 spread",
    "Metro: SI-kg drift",
]
predictions  = np.array([67.4, 0.77, 148.6, 12.5,  42.0, 1.85, 1.0000])
observations = np.array([67.8, 0.78, 149.3, 12.1,  40.5, 1.90, 1.0001])
thresholds   = np.array([0.02, 0.05, 0.02,  0.10,  0.10, 0.05, 0.001 ])

score, residuals = cross_domain_validation_score(predictions, observations, thresholds)
for i, lab in enumerate(pred_labels):
    status = "PASS" if residuals[i] < thresholds[i] else "FAIL"
    print(f"  {lab:28s}  pred={predictions[i]:8.4f}  obs={observations[i]:8.4f}"
          f"  |res|={residuals[i]:.4f}  thr={thresholds[i]:.3f}  {status}")
print(f"  => CDVS = {score:.2%} ({int(score*len(predictions))}/{len(predictions)} passed)")

# ------------------------------------------------------------------
# 4. Regime energy partition over redshift
# ------------------------------------------------------------------
print("\n[4] Regime Energy Partition (EFC L0-L3)")
E0 = 1.0
weights = np.array([0.05, 0.22, 0.45, 0.28])  # fractional energy by regime
gamma   = np.array([4.0,  3.0,  1.0,  0.0 ])  # scaling exponents
z = np.linspace(0, 5, 200)
E_regimes = regime_energy_partition(E0, weights, z, gamma)

for k, lab in enumerate(REGIME_LABELS_COSMOLOGY):
    print(f"  {lab}: w={weights[k]:.2f}, gamma={gamma[k]:.1f}, "
          f"E(z=0)={E_regimes[k,0]:.3f}, E(z=3)={E_regimes[k,100]:.3f}")

if HAS_MPL:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: energy partition
    ax = axes[0]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for k, lab in enumerate(REGIME_LABELS_COSMOLOGY):
        ax.plot(z, E_regimes[k], label=f"{lab} (w={weights[k]:.2f}, γ={gamma[k]:.0f})",
                color=colors[k], lw=2)
    ax.set_xlabel("Redshift z")
    ax.set_ylabel("E_k(z) / E₀")
    ax.set_title("Regime Energy Partition (L0–L3)")
    ax.legend(fontsize=9)
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)

    # Right: dark-X gap vs. number of regimes included
    ax2 = axes[1]
    contribs_full = [5.0, 22.0, 45.0, 26.0]
    n_reg = range(1, 5)
    deltas = []
    for n in n_reg:
        d, _ = dark_x_diagnostic(100.0, contribs_full[:n], delta_crit=0.05)
        deltas.append(d * 100)
    ax2.bar([f"L0–L{n-1}" for n in n_reg], deltas, color=colors[:4], edgecolor="k")
    ax2.axhline(5.0, color="red", ls="--", lw=1.5, label="δ_crit = 5%")
    ax2.set_ylabel("Ledger gap δ (%)")
    ax2.set_title("Dark-X Diagnostic vs. Regimes Included")
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("rce_demo_output.png", dpi=150)
    print("\n  Plot saved to rce_demo_output.png")
    plt.show()
else:
    print("  (matplotlib not available — skipping plot)")

print("\nDone.")
