#!/usr/bin/env python3
"""
Demo: Regime-Locked Measurement
March 2026

Usage: python regime_locked_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.regime_locked import (
    Regime, RegimeAppropriateness, BlindSetTaxonomy,
    MetaRegimeProtocol, CrossDomainDemos, CDVCAssessment,
    S0S1Conjecture, FALSIFICATION,
)

def main():
    print("Regime-Locked Measurement — Demo")
    print("March 2026\n")

    # Formal definitions
    print("Formal Framework")
    print("=" * 50)
    print("Regime: R = (I, V, B, G)")
    print("Regime-locked: m in V(R_i) and m not in V(R_j)")
    print("Alpha-score: alpha(phi, R) = |phi ∩ V(R)| / |phi| in [0,1]")
    print("CDVC: sigma in ∩ V(R_k), N >= 3")
    print()

    # Blind-set taxonomy
    taxonomy = BlindSetTaxonomy()
    print(taxonomy.print_table())
    print()

    # Six domains
    demos = CrossDomainDemos()
    print(demos.summary())
    print()

    # CDVC
    cdvc = CDVCAssessment()
    print(f"CDVC: N = {cdvc.n_domains} domains (threshold: {cdvc.threshold})")
    print(f"CDVC satisfied: {cdvc.is_cdvc()}")
    for c in cdvc.conditions():
        print(f"  - {c}")
    print(f"Alternative: {cdvc.alternative()}")
    print()

    # Alpha examples
    alpha = RegimeAppropriateness()
    print("Alpha-Score Examples")
    print("=" * 50)
    examples = {"Full coverage": (1.0, 1.0), "Partial (AI alignment est.)": (0.6, 1.0),
                "Half blind": (0.5, 1.0), "Fully blind": (0.0, 1.0)}
    for name, (phi_v, phi_t) in examples.items():
        print(f"  {name}: alpha = {alpha.alpha(phi_v, phi_t):.2f}")
    print()

    # Protocol
    protocol = MetaRegimeProtocol()
    print(protocol.summary())
    print()
    print(protocol.worked_example_ai())
    print()

    # S0/S1
    conj = S0S1Conjecture()
    print(f"S0/S1 Conjecture: {conj.status}")
    print(f"  S0: {conj.ai_s0}")
    print(f"  S1: {conj.ai_s1}")
    print(f"  Connection: {conj.connection}")
    print()

    # Falsification
    print("Falsification Criteria")
    print("=" * 50)
    for level, criteria in FALSIFICATION.items():
        print(f"  {level.upper()}:")
        for c in criteria:
            print(f"    - {c}")

if __name__ == "__main__":
    main()
