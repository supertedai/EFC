#!/usr/bin/env python3
"""Demo for EFC Bridging Scales / FEP package.

Demonstrates the bridge between the Free Energy Principle and
Energy-Flow Cosmology using Markov blankets and resonance parameters.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.bridging_scales import MarkovBlanket, BridgingFramework, ResonanceParameter


def main() -> None:
    fw = BridgingFramework(alpha=0.5)

    # Create Markov blankets as energy-flow interfaces
    cell = MarkovBlanket(
        name="Biological cell",
        internal_energy=1e-12,
        boundary_flux=1e-6,
        gradient_magnitude=1e-3,
    )
    neuron = MarkovBlanket(
        name="Neural ensemble",
        internal_energy=1e-9,
        boundary_flux=0.0,  # steady state
        gradient_magnitude=1e-1,
    )
    fw.add_blanket(cell)
    fw.add_blanket(neuron)

    # Add resonance parameters
    fw.add_resonance(ResonanceParameter(xi=1.5, system_label="cell membrane"))
    fw.add_resonance(ResonanceParameter(xi=0.8, system_label="decaying vortex"))

    # Compute bridging quantities
    phi_b = fw.blanket_integrated_scalar(cell, area=1e-10)
    df_dt = fw.variational_free_energy_rate(phi_b)
    t_eff = fw.effective_temperature(energy=1e-12, entropy=1e-14)

    print(fw.summary())
    print()
    print(f"Blanket-integrated scalar Phi_B (cell): {phi_b:.3e}")
    print(f"Variational free energy rate dF/dt:     {df_dt:.3e}")
    print(f"Effective temperature T_eff:             {t_eff:.1f} K")
    print(f"Neuron steady state: {neuron.is_steady_state}")
    print("\nDone.")


if __name__ == "__main__":
    main()
