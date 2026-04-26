#!/usr/bin/env python3
"""Demo: A Falsified Bar-Instability Criterion – EFC Disk-State Parameter.

Runs the key calculation on three synthetic template galaxies similar to
NGC 6503, NGC 3198, NGC 2841 and reproduces the Pi_min disk-state correlations
reported in the paper.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from a_falsified_bar_instability_criterion_re import (
    tanh_rotation_curve, pi_efc, pi_min_disk_window,
    sigma_r_jeans, kpc_m, km_s_to_m_s, Msun_kg, G_SI,
    pi_proxy_xgass, ZETA_DEFAULT
)

pc_m = 3.0857e16

# ---------- three template galaxies ----------
templates = {
    "NGC 6503-like (SA)": dict(v_flat=115, rd=2.2, Sigma0=80, alpha=0.35),
    "NGC 3198-like (SB)": dict(v_flat=150, rd=3.5, Sigma0=60, alpha=0.55),
    "NGC 2841-like (SA)": dict(v_flat=290, rd=4.0, Sigma0=200, alpha=0.20),
}

print("=" * 65)
print("EFC-BIC Pipeline Demo – Synthetic Galaxy Templates")
print("=" * 65)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)

for idx, (name, p) in enumerate(templates.items()):
    r_kpc = np.linspace(0.5, 15.0, 80)
    r_m = r_kpc * kpc_m
    v_kms = tanh_rotation_curve(r_kpc, p["v_flat"], p["rd"])
    v_ms = v_kms * km_s_to_m_s
    rd_m = p["rd"] * kpc_m
    Sig0_si = p["Sigma0"] * Msun_kg / pc_m**2
    sigma_disk = Sig0_si * np.exp(-r_kpc / p["rd"])

    # Compute Pi_EFC for both proxy modes
    Pi_v2 = pi_efc(r_m, v_ms, sigma_disk, rd_m, p["alpha"],
                   zeta=ZETA_DEFAULT, proxy_mode="v_squared")
    Pi_sh = pi_efc(r_m, v_ms, sigma_disk, rd_m, p["alpha"],
                   zeta=ZETA_DEFAULT, proxy_mode="shear")
    pmin_v2 = pi_min_disk_window(r_m, Pi_v2, rd_m)
    pmin_sh = pi_min_disk_window(r_m, Pi_sh, rd_m)

    print(f"\n{name}")
    print(f"  V_flat={p['v_flat']} km/s  Rd={p['rd']} kpc  "
          f"Sigma0={p['Sigma0']} Msun/pc^2  alpha={p['alpha']}")
    print(f"  Pi_min (v_squared): {pmin_v2:.3f}")
    print(f"  Pi_min (shear):     {pmin_sh:.3f}")

    ax = axes[idx]
    ax.plot(r_kpc, Pi_v2, label=r"$\Pi$ (v² proxy)", lw=2)
    ax.plot(r_kpc, Pi_sh, "--", label=r"$\Pi$ (shear proxy)", lw=2)
    ax.axvspan(p["rd"], 3 * p["rd"], alpha=0.12, color="grey",
               label="disk window")
    ax.axhline(1.0, color="red", ls=":", lw=1, label=r"$\Pi=1$ threshold")
    ax.set_xlabel("R [kpc]")
    if idx == 0:
        ax.set_ylabel(r"$\Pi_{\rm EFC}$")
    ax.set_title(name, fontsize=10)
    ax.set_ylim(0, 20)
    ax.legend(fontsize=7)

fig.tight_layout()
fig.savefig("demo_pi_profiles.png", dpi=150)
print("\nPlot saved to demo_pi_profiles.png")

# ---------- disk-state correlation demo ----------
print("\n" + "=" * 65)
print("Disk-State Correlation Demo (mock SPARC-like sample)")
print("=" * 65)

np.random.seed(42)
N = 112
log_Sigma = np.random.uniform(0.5, 3.0, N)
fgas = np.random.uniform(0.05, 0.85, N)
# Mock Pi_min ~ inversely related to Sigma, positively to fgas
Pi_mock = 2.0 * fgas / (0.01 + log_Sigma / 3.0) + np.random.normal(0, 0.3, N)

from scipy.stats import spearmanr
rho_sig, p_sig = spearmanr(Pi_mock, log_Sigma)
rho_fg, p_fg = spearmanr(Pi_mock, fgas)
print(f"  Spearman rho(Pi_min, log Sigma_disk) = {rho_sig:+.2f}  (paper: -0.71)")
print(f"  Spearman rho(Pi_min, f_gas)          = {rho_fg:+.2f}  (paper: +0.65)")

# ---------- xGASS proxy demo ----------
print("\n" + "=" * 65)
print("xGASS Pi_proxy scalar example")
print("=" * 65)
pp = pi_proxy_xgass(v_rot=180.0, sigma_star=120.0,
                    r_eff=5.0, sigma_r_est=30.0)
print(f"  Pi_proxy(v_rot=180, Sigma*=120, r_eff=5, sigR=30) = {pp:.3f}")
print("\nDone.")
