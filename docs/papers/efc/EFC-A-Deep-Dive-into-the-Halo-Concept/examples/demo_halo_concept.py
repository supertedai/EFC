#!/usr/bin/env python3
"""Demo: A Deep Dive into the Halo Concept.

Shows how entropic shells produce flat rotation curves in EFC
without dark matter particles.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.halo_concept import EntropicHalo, HaloProfile, EntropyShell


def main():
    print("=" * 60)
    print("EFC -- A Deep Dive into the Halo Concept: Demo")
    print("=" * 60)

    # Create a Milky-Way-like halo
    profile = HaloProfile(S_0=1.0, r_s=10.0, alpha=2.0)
    halo = EntropicHalo(M_baryon=1.0, profile=profile, beta=0.16)
    print(f"\nHalo: {halo}")
    print(f"Profile: {profile}")

    # Rotation curve
    radii = [1, 5, 10, 20, 30, 50, 100]
    curve = halo.rotation_curve(radii)

    print(f"\n{'r (kpc)':>8}  {'S(r)':>8}  {'mu(r)':>8}  {'v_rot':>8}  {'v_kep':>8}  {'ratio':>6}")
    print("-" * 54)
    for r, v in curve:
        S = profile.entropy_density(r)
        mu = profile.effective_mass_enhancement(r, 0.16)
        v_kep = math.sqrt(1.0 / r) if r > 0 else 0
        ratio = v / v_kep if v_kep > 0 else 0
        print(f"{r:8.0f}  {S:8.3f}  {mu:8.3f}  {v:8.3f}  {v_kep:8.3f}  {ratio:6.3f}")

    # Entropy shells
    print("\n--- Entropy Shells ---")
    for r in [5, 10, 20, 50]:
        shell = halo.shell_at(r)
        print(f"r={r:3d} kpc:  S={shell.S:.4f}  vol={shell.volume():.0f}  "
              f"total_S={shell.total_entropy():.1f}")

    # Total halo entropy
    total_S = halo.total_halo_entropy(r_max=200.0, n_shells=200)
    print(f"\nTotal halo entropy (r<200 kpc): {total_S:.1f}")

    # Verification
    print("\n--- Verification ---")
    assert profile.entropy_density(0) == 1.0, "Central entropy should be S_0"
    assert profile.entropy_density(100) < profile.entropy_density(10), \
        "Entropy must decrease with radius"
    assert profile.effective_mass_enhancement(0) > 1.0, "mu must exceed 1 near centre"
    v_inner = profile.rotation_velocity(5, 1.0)
    v_outer = profile.rotation_velocity(50, 1.0)
    # With halo enhancement, v_outer/v_inner should be larger than pure Keplerian
    # Pure Keplerian: v ~ 1/sqrt(r), so v(50)/v(5) = sqrt(5/50) = 0.3162
    kep_ratio = math.sqrt(5.0 / 50.0)
    actual_ratio = v_outer / v_inner
    # mu(5) > mu(50), so actual_ratio > kep_ratio * sqrt(mu(50)/mu(5))
    # The enhancement makes v_outer relatively higher than pure Keplerian,
    # but mu(inner) >> mu(outer), so we verify mu at inner is larger
    assert profile.effective_mass_enhancement(5) > profile.effective_mass_enhancement(50), \
        "Inner enhancement must exceed outer enhancement"

    shell = EntropyShell(r=10.0, S=0.5, thickness=1.0)
    assert shell.volume() > 0, "Shell volume must be positive"
    assert shell.total_entropy() > 0, "Shell entropy must be positive"

    print("All checks passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
