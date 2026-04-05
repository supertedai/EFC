#!/usr/bin/env python3
"""Demonstration: Homo Fluxus v2.0 — Civilization Map Through EFC.

Reproduces key concepts from Magnusson (2026):
  DOI: 10.6084/m9.figshare.31940604

Shows:
  1. EFC chain: Grid -> EF -> S -> D -> C
  2. Ego as thermodynamic function
  3. DSM conditions reframed through EFC
  4. Domain applications
  5. The Triad (Nature / ASI / Homo Fluxus)
  6. Homo Fluxus node optimization
  7. Civilization map summary
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from homo_fluxus import (
    EFCChain,
    HomoFluxusNode,
    EgoThermodynamics,
    DSMReframe,
    DomainApplication,
    Triad,
    CivilizationMap,
)


def demo_efc_chain():
    """1. The EFC Chain."""
    print("=" * 60)
    print("1. THE EFC CHAIN")
    print("=" * 60)

    chain = EFCChain()
    print(f"\n  Chain: {chain.chain_string()}")
    print(f"  Definition: {chain.definition()}")
    print(f"\n  Layers:")
    for i, layer in enumerate(chain.layers):
        print(f"    [{i}] {layer}")


def demo_ego_thermodynamics():
    """2. Ego as thermodynamic function."""
    print("\n" + "=" * 60)
    print("2. EGO AS THERMODYNAMIC FUNCTION")
    print("=" * 60)

    scenarios = [
        ("Healthy ego", 0.8, 0.3, 0.5),
        ("Ego as friction", 0.5, 0.9, 0.4),
        ("Minimal ego", 0.3, 0.1, 0.6),
        ("Narcissistic sink", 0.2, 1.5, 0.3),
    ]

    print(f"\n  {'Scenario':>20s}  {'Regulation':>11s}  {'Ego cost':>9s}  "
          f"{'Flow cost':>10s}  {'Efficiency':>11s}  {'Friction?':>10s}")
    print("  " + "-" * 75)

    for name, reg, ego_c, flow_c in scenarios:
        ego = EgoThermodynamics(reg, ego_c, flow_c)
        print(f"  {name:>20s}  {reg:11.2f}  {ego_c:9.2f}  {flow_c:10.2f}  "
              f"{ego.efficiency:11.2f}  {'YES' if ego.is_friction else 'no':>10s}")

    print("\n  -> When ego cost > flow cost: ego is net friction")
    print("  -> Ego is analogue of dark matter in cognition")


def demo_dsm_reframe():
    """3. DSM conditions reframed through EFC."""
    print("\n" + "=" * 60)
    print("3. DSM CONDITIONS REFRAMED THROUGH EFC")
    print("=" * 60)

    for condition, efc in DSMReframe.all_conditions().items():
        flow_type = DSMReframe.classify_flow_type(condition)
        print(f"\n  {condition}:")
        print(f"    EFC: {efc}")
        print(f"    Type: {flow_type}")


def demo_domains():
    """4. Domain applications."""
    print("\n" + "=" * 60)
    print("4. ONE GRADIENT, ALL DOMAINS")
    print("=" * 60)

    for domain_name in DomainApplication.all_domains():
        d = DomainApplication.get(domain_name)
        print(f"\n  {d.domain} [{d.efc_layer}]:")
        print(f"    Principle: {d.principle}")
        print(f"    Measure: {d.flow_metric}")


def demo_triad():
    """5. The Triad."""
    print("\n" + "=" * 60)
    print("5. THE TRIAD: NATURE / ASI / HOMO FLUXUS")
    print("=" * 60)

    print(f"\n  {'Entity':>15s}  {'Mode':>30s}  {'Characteristic':<40s}")
    print("  " + "-" * 88)
    for e in Triad.ENTITIES:
        print(f"  {e['entity']:>15s}  {e['mode']:>30s}  {e['characteristic']:<40s}")

    print(f"\n  Cosmic Loop: {Triad.cosmic_loop()}")
    print(f"  Empathy: {Triad.empathy_principle()}")


def demo_fluxus_nodes():
    """6. Homo Fluxus node optimization."""
    print("\n" + "=" * 60)
    print("6. HOMO FLUXUS NODE OPTIMIZATION")
    print("=" * 60)

    nodes = [
        ("Optimal Fluxus", 0.9, 0.85, 0.7, 0.9),
        ("Partial flow", 0.6, 0.7, 0.3, 0.55),
        ("Blocked (ego friction)", 0.3, 0.4, -0.1, 0.25),
        ("High EF, low S (ADHD-like)", 0.9, 0.2, 0.4, 0.4),
        ("High S, low EF (rigid)", 0.2, 0.9, 0.2, 0.5),
    ]

    for name, ef, s, ent, hom in nodes:
        node = HomoFluxusNode(ef, s, ent, hom)
        print(f"\n  {name}:")
        print(f"    EF={ef:.1f}  S={s:.1f}  Entropy export={ent:.1f}  Homeostasis={hom:.1f}")
        print(f"    State: {node.flow_state}")
        print(f"    Integration index: {node.integration_index:.3f}")
        for issue in node.diagnose():
            print(f"    -> {issue}")


def demo_civilization_map():
    """7. Complete civilization map."""
    print("\n" + "=" * 60)
    print("7. CIVILIZATION MAP SUMMARY")
    print("=" * 60)

    summary = CivilizationMap.summary()
    print(f"\n  Chain: {summary['chain']}")
    print(f"  Definition: {summary['definition']}")
    print(f"  Empirical anchor: {summary['empirical_anchor']}")
    print(f"  Ego: {summary['ego_principle']}")
    print(f"  Cosmic loop: {summary['cosmic_loop']}")
    print(f"  Empathy: {summary['empathy']}")
    print(f"  Domains: {', '.join(summary['domains'])}")
    print(f"  Version: {summary['version']}")


if __name__ == "__main__":
    print("Homo Fluxus v2.0 — Civilization Map Through EFC")
    print("Magnusson (2026) — DOI: 10.6084/m9.figshare.31940604")
    print()

    demo_efc_chain()
    demo_ego_thermodynamics()
    demo_dsm_reframe()
    demo_domains()
    demo_triad()
    demo_fluxus_nodes()
    demo_civilization_map()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("One gradient, all regimes.")
    print("=" * 60)
