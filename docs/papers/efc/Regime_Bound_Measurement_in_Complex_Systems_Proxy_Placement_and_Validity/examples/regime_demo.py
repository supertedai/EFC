#!/usr/bin/env python3
"""
Demo: Regime-Bound Measurement in Complex Systems
Working paper — March 7, 2026

Usage: python regime_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.regime_measurement import (
    CoreConcepts, PredictionRegister, AxiomZeroResults,
    StructuralChain, ValidityProfile,
    EFC_REGIMES, HUBBLE_PLACEMENTS, AI_METRIC_PROXIES,
    NINE_THESES, FIVE_PREDICTIONS, FBREAK,
)

def main():
    print("Regime-Bound Measurement in Complex Systems — Demo")
    print("Working paper, March 7, 2026\n")

    # Core concepts
    concepts = CoreConcepts()
    print(concepts.print_reference_table())
    print()

    # Nine theses
    print("Nine Theses (Section 3)")
    print("=" * 50)
    for i, t in enumerate(NINE_THESES, 1):
        print(f"  T{i}: {t}")
    print()

    # Structural chain
    chain = StructuralChain()
    print(chain.detail())
    print()

    # EFC regimes
    print("EFC Structural Regimes (Table 2)")
    print("=" * 70)
    print(f"{'Regime':<14} {'Tertile':<10} {'Character':<30} {'Expected Response'}")
    print("-" * 70)
    for r in EFC_REGIMES:
        print(f"{r.name:<14} {r.tertile:<10} {r.character[:30]:<30} {r.expected_response}")
    print()

    # Axiom 0
    ax0 = AxiomZeroResults()
    print(ax0.summary())
    print()

    # Hubble tension placement
    print("Hubble Tension Placement Analysis (Table 4)")
    print("=" * 60)
    for p in HUBBLE_PLACEMENTS:
        print(f"  {p.name}: z={p.z}, regime={p.regime}")
        print(f"    Instrument: {p.instrument}")
        print(f"    Interpretive: {p.interpretive}")
    print()

    # AI metrics
    print("AI Metric Proxy Structure (Table 6)")
    print("=" * 70)
    for m in AI_METRIC_PROXIES:
        print(f"  {m.metric}: proxy for {m.target}")
        print(f"    Blind to: {m.blindness}")
    print()

    # Validity profile template
    vp = ValidityProfile()
    print(vp.template())
    print()

    # Prediction register
    register = PredictionRegister()
    print(register.summary())
    print()

    # Framework-breaking outcomes
    print("Framework-Breaking Outcomes (Section 8.4)")
    print("=" * 60)
    for fid, outcome, consequence in FBREAK:
        print(f"  {fid}: {outcome}")
        print(f"    -> {consequence}")

if __name__ == "__main__":
    main()
