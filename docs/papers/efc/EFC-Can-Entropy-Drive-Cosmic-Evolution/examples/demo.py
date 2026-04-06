#!/usr/bin/env python3
"""Demo for EFC Can Entropy Drive Cosmic Evolution package.

Shows cosmic epochs, entropy gradients, and structure formation
driven by entropy flow.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cosmic_evolution import EntropicEvolution, EntropyGradient


def main() -> None:
    evo = EntropicEvolution()

    print(evo.summary())

    # Inspect specific gradient
    print("\nEntropy flux estimates:")
    for g in evo.gradients:
        print(f"  {g.label}: flux = {g.entropy_flux:.2e} J/(K m^2 s)")

    # Show epoch times in Gyr
    print("\nEpoch timeline:")
    for e in evo.epochs:
        print(f"  {e.name}: {e.time_gyr:.4f} Gyr")

    print(f"\nTotal entropy growth factor: {evo.total_entropy_growth():.2e}")
    print("\nDone.")


if __name__ == "__main__":
    main()
