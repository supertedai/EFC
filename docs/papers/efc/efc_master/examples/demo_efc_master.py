"""demo_efc_master.py – Demonstration of the EFC Master Specification.

Runs the key calculations from the dynamical and structural sectors and
optionally produces diagnostic plots (matplotlib required for plots).
"""

import numpy as np
import sys

from efc_master import (
    energy_flow_field, energy_flow_magnitude,
    effective_potential, expansion_rate,
    rotation_velocity, potential_gradient_numerical,
    effective_light_speed, x_of_S, structural_regime,
    S0, S1, S_MID, C0, A_EDGE, A_PHI, BETA,
)


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Entropy-dependent effective light speed
    # ------------------------------------------------------------------
    S = np.linspace(S0, S1, 200)
    c_S = effective_light_speed(S)
    print("── Effective light speed c(S) ──")
    print(f"  c(S0={S0:.1f})   = {c_S[0]:.6e} m/s")
    print(f"  c(Smid={S_MID:.1f}) = {effective_light_speed(np.array([S_MID]))[0]:.6e} m/s  (minimum)")
    print(f"  c(S1={S1:.1f})   = {c_S[-1]:.6e} m/s")
    print()

    # ------------------------------------------------------------------
    # 2. Toy galactic profile: Ef(r) and S(r)
    # ------------------------------------------------------------------
    r = np.linspace(0.5, 30.0, 300)          # kpc-like radial grid
    S_profile = S_MID + 0.4 * np.exp(-r / 6.0)  # entropy peaks at centre
    Ef_profile = 1.2 * np.exp(-r / 10.0)         # energy flow decays outward

    Phi = effective_potential(Ef_profile, S_profile)
    dPhi_dr = potential_gradient_numerical(r, Phi)
    v_rot = rotation_velocity(r, dPhi_dr)
    H_profile = expansion_rate(Ef_profile, S_profile)

    print("── Rotation curve (sample points) ──")
    for ri in [1, 5, 10, 20]:
        idx = np.argmin(np.abs(r - ri))
        print(f"  r={r[idx]:5.1f}  v={v_rot[idx]:.4f}  H={H_profile[idx]:.4f}  Φ={Phi[idx]:.4f}")
    print()

    # ------------------------------------------------------------------
    # 3. Structural regimes
    # ------------------------------------------------------------------
    regimes = structural_regime(S_profile)
    labels = {0: 'focusing', 1: 'transition', 2: 'defocusing'}
    print("── Structural regimes along profile ──")
    for ri in [1, 5, 15, 25]:
        idx = np.argmin(np.abs(r - ri))
        print(f"  r={r[idx]:5.1f}  S={S_profile[idx]:.3f}  regime={labels[regimes[idx]]}")
    print()

    # ------------------------------------------------------------------
    # 4. Optional plots
    # ------------------------------------------------------------------
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(11, 8))
        fig.suptitle("EFC Master Specification – Demonstration", fontsize=14)

        # (a) c(S)
        ax = axes[0, 0]
        ax.plot(S, c_S / 1e8, lw=2)
        ax.set_xlabel("Entropy S")
        ax.set_ylabel(r"$c(S)\;[\times10^8\;\mathrm{m/s}]$")
        ax.set_title("Effective light speed")
        ax.axvline(S_MID, ls='--', color='grey', label=r'$S_{\rm mid}$')
        ax.legend()

        # (b) Rotation curve
        ax = axes[0, 1]
        ax.plot(r, v_rot, lw=2, color='tab:red')
        ax.set_xlabel("r [arb.]")
        ax.set_ylabel("v(r)")
        ax.set_title("Rotation curve from Φ gradient")

        # (c) Expansion rate
        ax = axes[1, 0]
        ax.plot(r, H_profile, lw=2, color='tab:green')
        ax.set_xlabel("r [arb.]")
        ax.set_ylabel("H(Ef, S)")
        ax.set_title("Expansion rate profile")

        # (d) Potential
        ax = axes[1, 1]
        ax.plot(r, Phi, lw=2, color='tab:purple')
        ax.set_xlabel("r [arb.]")
        ax.set_ylabel(r"$\Phi(E_f,\,S)$")
        ax.set_title("Effective potential")

        plt.tight_layout()
        plt.savefig("efc_demo_output.png", dpi=150)
        print("Plot saved to efc_demo_output.png")
        plt.show()
    except ImportError:
        print("matplotlib not available – skipping plots.")


if __name__ == "__main__":
    main()
