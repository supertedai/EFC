#!/usr/bin/env python3
"""
Phase 4 — E_G observable test.

Morten's directive: "Flytt analysen fra 'hvordan vokser δ' → 'hvordan relaterer Φ og Ψ seg til δ'"

Prediction step (no MCMC). Compute E_G(z) for each cosmology model and compare
to literature measurements. If growth-only EFC modifications produce detectable
E_G deviations from LCDM, we have a new observable direction. If not, growth
sector is truly exhausted and we must include lensing Σ-modification.

Definition (Zhang et al. 2007, Reyes et al. 2010):
    E_G(k, z) = [∇²(Φ + Ψ) / (a² · ρ_m · δ_m)] · (d ln D / d ln a)⁻¹

Quasi-static approximation:
    E_G(z) = Σ(z) · Ω_{m,0} / f(z)

where:
    Σ(z) = (Φ + Ψ) / (Φ + Ψ)_GR    — lensing coupling
    f(z) = d ln D / d ln a           — growth rate

In pure LCDM: Σ = 1, so E_G(z) = Ω_{m,0} / f(z).

For growth-only EFC modifications (VariantJ, VariantK):
    Σ = 1 still (we did NOT modify lensing potentials)
    f(z) modified via growth ODE
    ⇒ E_G shifts via f alone

If E_G predictions for VariantJ/K are NOT distinguishable from LCDM at current
measurement precision, confirms: fσ8 + E_G in growth-only-mode gives same null
as fσ8 alone.

If they ARE distinguishable: new observable direction worth MCMC.

Output:
    outputs/grav_bridge/phase4_e_g_<timestamp>.json
    outputs/grav_bridge/phase4_e_g_plot_<timestamp>.png
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

from efc_grav_bridge import (  # noqa: E402
    FlatLCDM, EFCVariantJ, EFCVariantK,
)

OUT_DIR = REPO_ROOT / "outputs"


# ─── E_G literature measurements ───────────────────────────────
# z, E_G, sigma, source
E_G_LITERATURE = [
    (0.267, 0.43, 0.13, "Amon+2018 (KiDS+GAMA+2dFLenS)"),
    (0.32,  0.39, 0.06, "Reyes+2010 (SDSS)"),
    (0.42,  0.45, 0.06, "Singh+2019 (SDSS DR12)"),
    (0.57,  0.30, 0.07, "Blake+2016 (RCSLenS × BOSS CMASS)"),
    (0.60,  0.48, 0.12, "de la Torre+2017 (VIPERS × CFHTLenS)"),
]

# LCDM prediction reference (γ ≈ 0.545 approximation)
GAMMA_LCDM = 0.545


# ─── compute f(z) from growth ODE (stand-alone, to avoid fs8 normalization) ─

def compute_f_and_D(cosmology, params, z_arr, a_ini=1e-3,
                    rtol=1e-9, atol=1e-11):
    """Solve growth ODE and extract f(z) = d ln D / d ln a and D(z)/D(0).

    Uses cosmology.e_squared, de_squared_da, growth_source, friction_extra.
    Identical ODE structure to EFCGrowth._compute but returns (f, D_ratio).
    """
    a_data = 1.0 / (1.0 + np.asarray(z_arr, dtype=float))

    def ode(a, y):
        D, Dp = y
        a_arr = np.array([a])
        E2 = cosmology.e_squared(a_arr, params).item()
        if E2 <= 0:
            return [0.0, 0.0]
        E_a = np.sqrt(E2)
        dE2_da = cosmology.de_squared_da(a_arr, params).item()
        dE_da = dE2_da / (2.0 * E_a)
        friction_base = 3.0 / a + dE_da / E_a
        friction_extra = cosmology.friction_extra(a_arr, params).item()
        friction = friction_base + friction_extra
        source = cosmology.growth_source(a_arr, params).item()
        return [Dp, -friction * Dp + source * D]

    y0 = [a_ini, 1.0]
    sol = solve_ivp(ode, (a_ini, 1.0), y0, method="RK45",
                    rtol=rtol, atol=atol, dense_output=True)
    if not sol.success:
        raise RuntimeError(f"growth ODE failed: {sol.message}")

    D_at_1 = float(sol.sol(1.0)[0])
    f_vals = np.zeros_like(a_data)
    D_ratio = np.zeros_like(a_data)
    for i, a in enumerate(a_data):
        D_i, Dp_i = sol.sol(a)
        D_i = float(D_i); Dp_i = float(Dp_i)
        if D_i <= 0:
            f_vals[i] = np.nan
            D_ratio[i] = np.nan
        else:
            f_vals[i] = a * Dp_i / D_i
            D_ratio[i] = D_i / D_at_1
    return f_vals, D_ratio


def compute_E_G(cosmology, params, z_arr, Sigma_fn=None):
    """E_G(z) = Σ(z) · Ω_{m,0} / f(z).

    For growth-only variants (VariantJ, VariantK): Σ=1.
    For potential future slip-variants: Sigma_fn can return Σ(z).
    """
    f_z, _ = compute_f_and_D(cosmology, params, z_arr)
    Om0 = float(params["Omega_m"])
    if Sigma_fn is None:
        Sigma = np.ones_like(z_arr)
    else:
        Sigma = Sigma_fn(z_arr)
    return Sigma * Om0 / f_z


def E_G_lcdm_approx(z_arr, Om0=0.3):
    """Standard LCDM approximation via γ ≈ 0.545.

    f(z) ≈ Ω_m(z)^γ,  Ω_m(z) = Ω_{m,0} · (1+z)³ / E²(z)
    """
    E2 = Om0 * (1.0 + z_arr) ** 3 + (1.0 - Om0)
    Om_z = Om0 * (1.0 + z_arr) ** 3 / E2
    f_z = Om_z ** GAMMA_LCDM
    return Om0 / f_z


def chi2(E_G_pred, E_G_obs, sigma_obs):
    residuals = np.asarray(E_G_obs) - np.asarray(E_G_pred)
    return float(np.sum((residuals / np.asarray(sigma_obs)) ** 2))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print(" Phase 4 — E_G observable test (prediction vs literature, no MCMC)")
    print("=" * 80)

    z_data = np.array([row[0] for row in E_G_LITERATURE])
    E_G_obs = np.array([row[1] for row in E_G_LITERATURE])
    sigma_obs = np.array([row[2] for row in E_G_LITERATURE])
    sources = [row[3] for row in E_G_LITERATURE]

    print(f"\nE_G literature compilation ({len(E_G_LITERATURE)} points):")
    for z, eg, s, src in E_G_LITERATURE:
        print(f"  z={z:.3f}  E_G = {eg:.3f} ± {s:.3f}  {src}")

    # ── Models to compare ──────────────────────────────────
    Om_central = 0.30  # close to BAO posterior (0.299) and Planck

    models = [
        ("LCDM (γ-approx)",      None,                  None),
        ("LCDM (growth ODE)",    FlatLCDM(),            {"Omega_m": Om_central}),
        ("VariantJ β=-0.02",     EFCVariantJ(),         {"Omega_m": Om_central, "beta": -0.02}),
        ("VariantJ β=+0.22",     EFCVariantJ(),         {"Omega_m": Om_central, "beta": +0.22}),
        ("VariantJ β=+1.0 (extreme)", EFCVariantJ(),    {"Omega_m": Om_central, "beta": +1.0}),
        ("VariantK β=-0.18",     EFCVariantK(),         {"Omega_m": Om_central, "beta": -0.18}),
        ("VariantK β=+2.0 (extreme)", EFCVariantK(),    {"Omega_m": Om_central, "beta": +2.0}),
    ]

    print(f"\nModel predictions (Ω_m,0 = {Om_central}):\n")
    header = f"  {'Model':<32} {'χ²':>7} " + " ".join([f"z={z:.2f}" for z in z_data])
    print(header)
    print("  " + "-" * (len(header) - 2))

    results = []
    z_grid = np.linspace(0.01, 0.8, 100)  # for smooth model curves
    for name, model, params in models:
        if model is None:
            # Analytical LCDM approximation
            E_G_at_data = E_G_lcdm_approx(z_data, Om0=Om_central)
            E_G_curve = E_G_lcdm_approx(z_grid, Om0=Om_central)
        else:
            E_G_at_data = compute_E_G(model, params, z_data)
            E_G_curve = compute_E_G(model, params, z_grid)
        c2 = chi2(E_G_at_data, E_G_obs, sigma_obs)
        values_str = " ".join([f"{v:6.4f}" for v in E_G_at_data])
        print(f"  {name:<32} {c2:>7.2f} {values_str}")
        results.append({
            "name": name,
            "params": {k: float(v) for k, v in (params or {"Omega_m": Om_central}).items()},
            "chi2": c2,
            "E_G_at_data_z": [float(v) for v in E_G_at_data],
            "E_G_curve_z": z_grid.tolist(),
            "E_G_curve": [float(v) for v in E_G_curve],
        })

    # Reference: χ² for a horizontal line at mean
    E_G_mean = float(np.average(E_G_obs, weights=1.0 / sigma_obs ** 2))
    c2_const = chi2(np.full_like(E_G_obs, E_G_mean), E_G_obs, sigma_obs)
    print(f"\n  [{'Constant':<32} {c2_const:>7.2f}   mean = {E_G_mean:.3f}]")

    # ── Interpretation ─────────────────────────────────────
    chi2_lcdm_approx = results[0]["chi2"]
    chi2_lcdm_ode = results[1]["chi2"]
    chi2_j_best = results[2]["chi2"]    # Step 2 median
    chi2_j_unlocked = results[3]["chi2"]
    chi2_j_extreme = results[4]["chi2"]
    chi2_k_best = results[5]["chi2"]    # Step 3 median
    chi2_k_extreme = results[6]["chi2"]

    # Δχ² relative to LCDM ODE
    delta_j_best = chi2_j_best - chi2_lcdm_ode
    delta_j_extreme = chi2_j_extreme - chi2_lcdm_ode
    delta_k_best = chi2_k_best - chi2_lcdm_ode
    delta_k_extreme = chi2_k_extreme - chi2_lcdm_ode

    print("\n" + "=" * 80)
    print(" INTERPRETATION")
    print("=" * 80)
    print(f"\nΔχ² vs LCDM-ODE baseline ({chi2_lcdm_ode:.2f}):")
    print(f"  VariantJ β=-0.02 (Step2 post):   {delta_j_best:+.3f}")
    print(f"  VariantJ β=+0.22 (unlocked):     {delta_j_extreme:+.3f}")
    print(f"  VariantK β=-0.18 (Step3 post):   {delta_k_best:+.3f}")
    print(f"  VariantK β=+2.0  (extreme):      {delta_k_extreme:+.3f}")

    # Sensitivity check: how much does E_G shift for extreme beta?
    eg_lcdm_at_data = np.array(results[1]["E_G_at_data_z"])
    eg_j_extreme_at_data = np.array(results[4]["E_G_at_data_z"])
    eg_k_extreme_at_data = np.array(results[6]["E_G_at_data_z"])
    max_shift_j = float(np.max(np.abs(eg_j_extreme_at_data - eg_lcdm_at_data) / sigma_obs))
    max_shift_k = float(np.max(np.abs(eg_k_extreme_at_data - eg_lcdm_at_data) / sigma_obs))

    print(f"\nMax E_G shift (in units of measurement σ) for extreme β:")
    print(f"  VariantJ β=+1.0:  {max_shift_j:.2f}σ at any z in dataset")
    print(f"  VariantK β=+2.0:  {max_shift_k:.2f}σ at any z in dataset")

    if max_shift_j < 0.5 and max_shift_k < 0.5:
        verdict = "BLIND — growth-only EFC modifications produce <0.5σ E_G shifts across all tested β. E_G is NOT a new observable direction for these variants."
    elif max_shift_j < 2.0 and max_shift_k < 2.0:
        verdict = "WEAK — growth-only modifications shift E_G <2σ at extreme β. E_G may add information in joint fits, but not decisive alone."
    else:
        verdict = f"SENSITIVE — extreme β gives ≥2σ E_G shifts. E_G is a new informative direction for this variant."

    print(f"\n>>> VERDICT: {verdict}")

    # ── Plot ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 7))

    # Data
    ax.errorbar(z_data, E_G_obs, yerr=sigma_obs, fmt="o", color="black",
                capsize=4, markersize=8, label="E_G data (literature)", zorder=10)
    for (z, eg, s, src) in E_G_LITERATURE:
        ax.annotate(src.split()[0], (z, eg), xytext=(5, 5), textcoords="offset points",
                    fontsize=7, color="gray")

    # Models
    colors = ["#777777", "#1f77b4", "#d62728", "#ff7f0e", "#b30000",
              "#9467bd", "#4b0082"]
    linestyles = ["-", "-", "--", "--", ":", "--", ":"]
    for r, c, ls in zip(results, colors, linestyles):
        ax.plot(r["E_G_curve_z"], r["E_G_curve"], color=c, ls=ls,
                lw=1.8, label=f"{r['name']}  (χ²={r['chi2']:.2f})")

    ax.axhline(E_G_mean, color="gray", ls=":", alpha=0.4,
               label=f"inverse-variance mean = {E_G_mean:.3f}")

    ax.set_xlim(0, 0.8)
    ax.set_ylim(0.1, 0.7)
    ax.set_xlabel("z"); ax.set_ylabel("E_G(z)")
    ax.set_title("Phase 4 — E_G prediction vs literature (growth-only EFC variants)")
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)

    plot_path = OUT_DIR / f"phase4_e_g_plot_{ts}.png"
    fig.savefig(plot_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"\nPlot saved: {plot_path}")

    # ── Save summary ──────────────────────────────────────
    summary = {
        "phase": "4_E_G_observable_prediction",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": "Test if growth-only EFC modifications produce detectable E_G signal vs LCDM",
        "Omega_m_central": Om_central,
        "literature_data": [
            {"z": z, "E_G": eg, "sigma": s, "source": src}
            for z, eg, s, src in E_G_LITERATURE
        ],
        "inverse_variance_weighted_mean": round(E_G_mean, 4),
        "models": [
            {
                "name": r["name"],
                "params": r["params"],
                "chi2_vs_literature": round(r["chi2"], 3),
                "E_G_at_data_z": [round(v, 4) for v in r["E_G_at_data_z"]],
            }
            for r in results
        ],
        "chi2_constant_mean_reference": round(c2_const, 3),
        "max_shift_J_extreme_sigma_units": round(max_shift_j, 3),
        "max_shift_K_extreme_sigma_units": round(max_shift_k, 3),
        "verdict": verdict,
    }

    summary_path = OUT_DIR / f"phase4_e_g_{ts}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary: {summary_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
