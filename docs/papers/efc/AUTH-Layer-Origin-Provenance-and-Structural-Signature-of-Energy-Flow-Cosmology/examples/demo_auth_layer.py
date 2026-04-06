#!/usr/bin/env python3
"""
Demo: AUTH Layer -- Provenance and Structural Signature of EFC

Demonstrates provenance chain creation, structural signature analysis,
insight stabilisation, and identity verification.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auth_layer import (
    AUTHLayer,
    LayerType,
    TransitionState,
)


def main():
    print("=" * 60)
    print("AUTH LAYER DEMO")
    print("Origin, Provenance, and Structural Signature of EFC")
    print("=" * 60)

    auth = AUTHLayer()

    # --- Demo 1: Provenance chain creation and verification ---
    print("\n1. PROVENANCE CHAIN CREATION")
    print("-" * 40)

    chain = auth.create_chain("entropy_flow_equation")
    chain.add_record(LayerType.THEORY, "Initial formulation of entropy flow")
    chain.add_record(LayerType.METHODOLOGY, "Numerical implementation in CLASS")
    chain.add_record(LayerType.COGNITION, "Cross-validated with BAO data")
    chain.add_record(LayerType.AUTH, "Provenance chain sealed")

    summary = chain.summary()
    print(f"  Origin:        {summary['origin']}")
    print(f"  Chain length:  {summary['chain_length']}")
    print(f"  Layers:        {summary['layers_covered']}")
    print(f"  Chain valid:   {summary['chain_valid']}")

    assert summary["chain_length"] == 4
    assert summary["chain_valid"] is True
    assert len(summary["layers_covered"]) == 4
    print("  [PASS] Provenance chain verified")

    # --- Demo 2: Structural signature analysis ---
    print("\n2. STRUCTURAL SIGNATURE ANALYSIS")
    print("-" * 40)

    sig = auth.structural_signature()
    print(f"  Theory anchors:      {len(sig.theory_anchors)}")
    print(f"  Methodology anchors: {len(sig.methodology_anchors)}")
    print(f"  Cognition anchors:   {len(sig.cognition_anchors)}")
    print(f"  Total depth:         {sig.signature_depth()}")
    print(f"  Cross-links:         {len(sig.cross_links)}")
    print(f"  Cross-link density:  {sig.cross_link_density():.3f}")
    print(f"  Consistent:          {sig.is_structurally_consistent()}")

    assert sig.signature_depth() == 12
    assert sig.is_structurally_consistent() is True
    assert sig.cross_link_density() > 0
    print("  [PASS] Structural signature is consistent")

    # --- Demo 3: Insight stabilisation (s0/s1 transitions) ---
    print("\n3. INSIGHT STABILISATION (s0/s1)")
    print("-" * 40)

    transition = auth.create_transition("gate_function_sign_lemma")
    print(f"  Concept: {transition.concept}")
    print(f"  Initial state: {transition.state.value}")

    assert transition.state == TransitionState.S0_LATENT

    transition.activate()
    print(f"  After activate: {transition.state.value}")
    assert transition.state == TransitionState.S1_ACTIVE

    transition.confirm(LayerType.THEORY)
    transition.confirm(LayerType.METHODOLOGY)
    print(f"  After 2 confirmations: {transition.state.value} "
          f"(count={transition.stabilisation_count})")
    assert not transition.is_stabilised()

    transition.confirm(LayerType.COGNITION)
    print(f"  After 3 confirmations: {transition.state.value}")
    assert transition.is_stabilised()
    print("  [PASS] Insight correctly stabilised after 3-layer confirmation")

    # --- Demo 4: Chain integrity tamper detection ---
    print("\n4. CHAIN INTEGRITY / TAMPER DETECTION")
    print("-" * 40)

    chain2 = auth.create_chain("regime_transition")
    chain2.add_record(LayerType.THEORY, "Landau equation formulation")
    chain2.add_record(LayerType.METHODOLOGY, "RK4 numerical integration")

    assert chain2.verify_chain() is True
    print("  Valid chain: OK")

    # Tamper with a record
    original_hash = chain2.records[0].hash
    chain2.records[0].hash = "tampered_hash"
    assert chain2.verify_chain() is False
    print("  Tampered chain detected: OK")

    chain2.records[0].hash = original_hash
    assert chain2.verify_chain() is True
    print("  Restored chain: OK")
    print("  [PASS] Tamper detection working correctly")

    # --- Demo 5: Full identity check ---
    print("\n5. FULL IDENTITY CHECK")
    print("-" * 40)

    identity = auth.identity_check()
    print(f"  Framework:    {identity['provenance']['framework']}")
    print(f"  Author:       {identity['provenance']['author']}")
    print(f"  DOI:          {identity['provenance']['doi']}")
    print(f"  Sig. depth:   {identity['signature_depth']}")
    print(f"  Consistent:   {identity['structurally_consistent']}")
    print(f"  Chains valid: {identity['chains_valid']}")
    print(f"  Stabilised:   {identity['stabilised_insights']}/{identity['total_insights']}")

    assert identity["structurally_consistent"] is True
    assert identity["chains_valid"] is True
    assert identity["stabilised_insights"] == 1
    print("  [PASS] Identity check passed")

    # --- Demo 6: Summary output ---
    print("\n6. AUTH LAYER SUMMARY")
    print("-" * 40)
    print(auth.summary())

    print("\n" + "=" * 60)
    print("ALL DEMOS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
