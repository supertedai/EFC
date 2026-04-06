#!/usr/bin/env python3
"""Demonstration: EFC -- Is Consciousness Linked to Entropy?

Shows:
  1. Information state and cognitive temperature
  2. Entropy-consciousness link evaluation
  3. Phi threshold scanning
  4. Multi-system comparison

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consciousness_entropy import (
    InformationState,
    EntropyConsciousnessLink,
    ConsciousnessEntropyModel,
)


def demo_information_state():
    """1. Information state and cognitive temperature."""
    print("=" * 60)
    print("1. INFORMATION STATE AND COGNITIVE TEMPERATURE")
    print("   T_cog = S_rate / I_cap")
    print("=" * 60)

    scenarios = [
        ("Low entropy, high cap", 0.1, 1000.0, 0.8),
        ("Moderate", 1.0, 100.0, 0.6),
        ("High entropy, low cap", 10.0, 10.0, 0.3),
        ("Balanced", 5.0, 500.0, 1.2),
    ]

    for name, s_rate, i_cap, phi in scenarios:
        info = InformationState(entropy_rate=s_rate,
                                information_capacity=i_cap,
                                integration_level=phi)
        print(f"\n  {name}:")
        print(f"    S_rate = {s_rate}  I_cap = {i_cap}  Phi = {phi}")
        print(f"    T_cog = {info.cognitive_temperature():.6f}")
        print(f"    Above threshold: {info.is_above_threshold()}")


def demo_entropy_consciousness_link():
    """2. Entropy-consciousness link evaluation."""
    print("\n" + "=" * 60)
    print("2. ENTROPY-CONSCIOUSNESS LINK")
    print("   E = Phi * max(A, 0)")
    print("=" * 60)

    cases = [
        ("Strong internal grad", 5.0, 1.0, 0.8),
        ("Balanced gradients", 2.0, 2.0, 0.7),
        ("External dominated", 1.0, 5.0, 0.9),
        ("High Phi, weak grad", 1.1, 1.0, 1.5),
        ("Low Phi, strong grad", 10.0, 1.0, 0.2),
    ]

    print(f"\n  {'Case':>25s}  {'Asym':>6}  {'E-score':>8}  {'Candidate':>9}")
    print("  " + "-" * 55)

    for name, gi, ge, phi in cases:
        link = EntropyConsciousnessLink(
            internal_entropy_gradient=gi,
            external_entropy_gradient=ge,
            phi=phi,
        )
        print(f"  {name:>25s}  {link.gradient_asymmetry():6.3f}  "
              f"{link.emergence_score():8.4f}  "
              f"{str(link.is_conscious_candidate()):>9s}")


def demo_threshold_scan():
    """3. Phi threshold scanning."""
    print("\n" + "=" * 60)
    print("3. PHI THRESHOLD SCANNING")
    print("=" * 60)

    model = ConsciousnessEntropyModel(phi_threshold=0.5)

    phi_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 2.0]
    results = model.scan_threshold(phi_values, internal_grad=3.0, external_grad=1.0)

    print(f"\n  Internal grad = 3.0, External grad = 1.0, Phi_min = 0.5")
    print(f"\n  {'Phi':>6}  {'E-score':>8}  {'Candidate':>9}")
    print("  " + "-" * 28)
    for r in results:
        print(f"  {r['phi']:6.2f}  {r['emergence_score']:8.4f}  "
              f"{str(r['candidate']):>9s}")


def demo_multi_system():
    """4. Multi-system comparison."""
    print("\n" + "=" * 60)
    print("4. MULTI-SYSTEM COMPARISON")
    print("=" * 60)

    model = ConsciousnessEntropyModel(phi_threshold=0.5)

    systems = [
        ("Human brain", 5.0, 1.0, 1.2),
        ("Simple organism", 2.0, 1.5, 0.3),
        ("Thermostat", 0.5, 2.0, 0.01),
        ("Neural network (AI)", 3.0, 0.5, 0.6),
        ("Rock", 0.01, 0.01, 0.0),
    ]

    for name, gi, ge, phi in systems:
        model.add_system(gi, ge, phi)

    results = model.evaluate_all()
    print(f"\n  {model.summary()}\n")

    for name_phi, r in zip(systems, results):
        name = name_phi[0]
        print(f"  {name:<20s}  Phi={r['phi']:.2f}  A={r['asymmetry']:.3f}  "
              f"E={r['emergence_score']:.4f}  candidate={r['conscious_candidate']}")


if __name__ == "__main__":
    print("EFC: Is Consciousness Linked to Entropy?")
    print("Magnusson (2026)")
    print()

    demo_information_state()
    demo_entropy_consciousness_link()
    demo_threshold_scan()
    demo_multi_system()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
