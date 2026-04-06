#!/usr/bin/env python3
"""
H0 and S8 Tensions Resolution Demo

Demonstrates how entropy-dependent gravity resolves both the
Hubble tension and S8 tension simultaneously.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from h0_s8_tensions import (
    EffectiveGravity,
    HubbleTension,
    S8Tension,
    TensionResolver,
)


def main():
    print("=" * 60)
    print("EFC H0 and S8 Tensions Resolution Demo")
    print("=" * 60)
    print()

    # Effective gravity
    gravity = EffectiveGravity(g_n=1.0, beta=-0.02)
    print("Effective Gravity G_eff(S) = G_N * (1 + beta * S):")
    for s in [0.0, 2.0, 4.0, 6.0, 8.0]:
        print(f"  S={s:5.1f}: G_eff = {gravity.g_eff(s):.4f}, "
              f"suppression = {gravity.suppression_factor(s):.4f}")
    print()

    # Hubble tension
    hubble = HubbleTension(h0_local=73.0, h0_cmb=67.4)
    print(f"Hubble Tension: {hubble.tension_sigma():.1f} sigma")
    print(f"  H0_local = {hubble.h0_local} km/s/Mpc")
    print(f"  H0_CMB   = {hubble.h0_cmb} km/s/Mpc")
    h0_corr = hubble.corrected_h0(gravity, s_local=5.0)
    chi2 = hubble.chi2_improvement(gravity, s_local=5.0)
    print(f"  H0_corrected(S=5) = {h0_corr:.2f} km/s/Mpc")
    print(f"  chi2 improvement  = {chi2:.2f}")
    print()

    # S8 tension
    s8 = S8Tension(s8_lcdm=0.832, s8_observed=0.766)
    print(f"S8 Tension: {s8.tension_sigma():.1f} sigma")
    s8_corr = s8.corrected_s8(gravity, s_growth=4.0)
    resid = s8.residual_tension(gravity, s_growth=4.0)
    print(f"  S8_corrected(S=4) = {s8_corr:.4f}")
    print(f"  Residual tension  = {resid:.1f} sigma")
    print()

    # Full resolver
    resolver = TensionResolver(beta=-0.02)
    print(resolver.summary())
    print()

    result = resolver.resolve(s_local=5.0, s_growth=4.0)
    print("Resolution Results:")
    for key, val in result.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.4f}")
        else:
            print(f"  {key}: {val}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
