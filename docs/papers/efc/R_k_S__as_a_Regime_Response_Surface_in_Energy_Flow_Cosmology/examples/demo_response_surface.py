#!/usr/bin/env python3
"""Demo: R(k,S) Regime Response Surface.

Shows how the response surface maps gravitational deviation from GR
as a function of scale and structural maturity, and how the S8
tension is interpreted as a regime transition.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.regime_response_surface import (
    RegimeResponseSurface,
    StructuralMaturity,
    ResponseCoordinate,
)


def main():
    print("=" * 65)
    print("EFC -- R(k,S) Regime Response Surface: Demo")
    print("=" * 65)

    surface = RegimeResponseSurface(R_max=0.30, k_pivot=0.13, S_pivot=0.30)
    maturity = StructuralMaturity(z_mid=0.8)

    print(f"\nSurface:  {surface}")
    print(f"Maturity: {maturity}")

    # Response surface at fixed k = k_pivot
    print(f"\n--- R(k=0.13, S) across structural maturity ---")
    print(f"{'S':>6}  {'R(k,S)':>8}  {'mu':>8}")
    print("-" * 26)
    for S_val in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
        R = surface.R(0.13, S_val)
        mu = surface.mu(0.13, S_val)
        print(f"{S_val:6.2f}  {R:8.4f}  {mu:8.4f}")

    # Response surface at fixed S = 0.30 across k
    print(f"\n--- R(k, S=0.30) across wavenumber ---")
    print(f"{'k':>6}  {'R(k,S)':>8}  {'mu':>8}")
    print("-" * 26)
    for k_val in [0.01, 0.05, 0.10, 0.13, 0.15, 0.20, 0.30]:
        R = surface.R(k_val, 0.30)
        mu = surface.mu(k_val, 0.30)
        print(f"{k_val:6.2f}  {R:8.4f}  {mu:8.4f}")

    # S8 prediction
    print(f"\n--- S8 Tension Interpretation ---")
    S8_cmb = 0.83
    S8_pred = surface.s8_prediction(S8_cmb=S8_cmb, S=0.30)
    print(f"S8 (CMB):       {S8_cmb:.2f}")
    print(f"S8 (predicted): {S8_pred:.3f}")
    print(f"Offset:         {S8_cmb - S8_pred:.3f}")

    # Structural maturity across redshift
    print(f"\n--- Structural Maturity S(z) ---")
    print(f"{'z':>6}  {'S(z)':>6}  {'linear?':>8}  {'nonlinear?':>10}")
    print("-" * 34)
    for z in [5.0, 2.0, 1.0, 0.8, 0.5, 0.3, 0.0]:
        S = maturity.S(z)
        lin = maturity.is_linear(z)
        nonlin = maturity.is_nonlinear(z)
        print(f"{z:6.1f}  {S:6.3f}  {str(lin):>8}  {str(nonlin):>10}")

    # Falsification check
    print(f"\n--- Falsification Check ---")
    coords = [
        ResponseCoordinate(k=0.10, S=0.3, R=0.10),
        ResponseCoordinate(k=0.13, S=0.5, R=0.15),
        ResponseCoordinate(k=0.13, S=0.7, R=0.20),
    ]
    result = surface.falsification_check(coords)
    print(f"Tomographic consistency: {result['tomographic_consistency']}")
    print(f"Trend sign positive:    {result['trend_sign_positive']}")

    # Verification
    print("\n--- Verification ---")
    assert surface.R(0.13, 0.0) == 0.0, "R must be 0 when S=0 (GR limit)"
    assert surface.R(0.13, 0.3) > 0, "R must be positive at k_pivot, S=0.3"
    assert surface.mu(0.13, 0.0) == 1.0, "mu must be 1 when S=0"
    assert surface.mu(0.13, 0.5) > 1.0, "mu must exceed 1 for S>0"
    assert S8_pred < S8_cmb, "Late-universe S8 must be lower than CMB S8"
    assert maturity.is_linear(10.0), "z=10 must be linear regime"
    assert maturity.is_nonlinear(0.0), "z=0 must be non-linear regime"
    assert result["tomographic_consistency"], "Test coords must be consistent"

    coord = surface.coordinate(0.13, 0.3)
    assert isinstance(coord, ResponseCoordinate)
    assert not coord.is_gr(), "Should not be GR at S=0.3"

    print("All checks passed.")
    print("=" * 65)


if __name__ == "__main__":
    main()
