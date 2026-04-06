#!/usr/bin/env python3
"""Demo for EFC CMB Thermodynamic Gradient package.

Demonstrates the thermodynamic-gradient interpretation of the CMB,
including anisotropy modes, grid properties, and temperature fluctuations.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cmb_gradient import CMBGradient, CMBAnisotropy


def main() -> None:
    cmb = CMBGradient()

    # Full summary
    print(cmb.summary())

    # Compute a temperature fluctuation from an entropy perturbation
    delta_S = 5e-30  # W/m^3/K
    dt_over_t = cmb.temperature_fluctuation(delta_S)
    print(f"\nTemperature fluctuation dT/T for dS={delta_S:.1e}: {dt_over_t:.4e}")

    # Add a custom high-l mode
    cmb.anisotropies.append(CMBAnisotropy(
        multipole_l=1000, amplitude_uK=50.0, entropy_gradient=5e-30
    ))
    print(f"Updated RMS anisotropy: {cmb.total_rms_anisotropy():.2f} uK")
    print(f"Grid energy density: {cmb.grid.energy_density:.3e} J/m^3")
    print("\nDone.")


if __name__ == "__main__":
    main()
