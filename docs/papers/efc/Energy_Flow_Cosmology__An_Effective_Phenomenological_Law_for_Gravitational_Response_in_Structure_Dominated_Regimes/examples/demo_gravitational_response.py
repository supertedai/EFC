#!/usr/bin/env python3
"""Demo: Effective Phenomenological Law for Gravitational Response.

Shows the evolution of mu(a) = 1 + beta*S(a) across cosmic history
and the regime classification.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.gravitational_response import (
    EntropyField,
    EffectiveGravitationalCoupling,
    RegimeClassifier,
)


def main():
    print("=" * 65)
    print("EFC -- Effective Gravitational Coupling mu(a): Demo")
    print("=" * 65)

    # Standard EFC parameters
    S_field = EntropyField(S_inf=1.0, a_t=0.55, sigma=0.10)
    coupling = EffectiveGravitationalCoupling(beta=0.16, entropy_field=S_field)
    classifier = RegimeClassifier(coupling)

    print(f"\nEntropy field: {S_field}")
    print(f"Coupling:      {coupling}")
    print(f"Transition z:  {S_field.transition_redshift():.2f}")

    # Evolution table
    redshifts = [1100, 10, 3, 1.5, 1.0, 0.82, 0.5, 0.3, 0.0]
    print(f"\n{'z':>8}  {'a':>8}  {'S(a)':>8}  {'mu(a)':>8}  {'enh%':>6}  {'regime':>6}")
    print("-" * 52)
    for z in redshifts:
        a = 1.0 / (1.0 + z)
        S = S_field.S(a)
        mu = coupling.mu(a)
        enh = coupling.enhancement_percent(a)
        regime = classifier.classify(a)
        print(f"{z:8.2f}  {a:8.4f}  {S:8.4f}  {mu:8.4f}  {enh:5.1f}%  {regime:>6}")

    # Key checks
    print("\n--- Verification ---")

    # GR recovery at early times
    mu_early = coupling.mu(0.001)
    assert coupling.is_gr_limit(0.001), f"Early universe must be GR limit, got mu={mu_early}"
    print(f"GR recovery (a=0.001):  mu = {mu_early:.8f}  [OK]")

    # Full enhancement at late times
    mu_late = coupling.mu(1.0)
    assert mu_late > 1.1, f"Late universe must have mu > 1.1, got {mu_late}"
    print(f"Full enhancement (a=1): mu = {mu_late:.4f}  [OK]")

    # Transition at a_t
    S_mid = S_field.S(S_field.a_t)
    assert abs(S_mid - 0.5) < 0.01, f"S(a_t) should be ~0.5, got {S_mid}"
    print(f"Transition (a_t=0.55):  S  = {S_mid:.4f}  [OK]")

    # Regime classification
    assert classifier.classify_z(1100) == "L0"
    assert classifier.classify_z(0.0) == "L3"
    print(f"Regime z=1100: {classifier.classify_z(1100)}  [OK]")
    print(f"Regime z=0:    {classifier.classify_z(0.0)}  [OK]")

    # Monotonicity of S
    S_vals = [S_field.S(a / 100.0) for a in range(1, 101)]
    for i in range(1, len(S_vals)):
        assert S_vals[i] >= S_vals[i - 1] - 1e-12, "S(a) must be monotonically increasing"
    print("S(a) monotonicity: verified  [OK]")

    print("\nAll checks passed.")
    print("=" * 65)


if __name__ == "__main__":
    main()
