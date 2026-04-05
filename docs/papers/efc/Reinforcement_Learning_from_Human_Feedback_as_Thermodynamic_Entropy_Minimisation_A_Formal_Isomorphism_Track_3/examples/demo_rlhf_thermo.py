#!/usr/bin/env python3
"""Demonstration: RLHF as Thermodynamic Entropy Minimisation.

Reproduces key results from Magnusson (2026):
  DOI: 10.6084/m9.figshare.31940535

Shows:
  1. Optimal policy = Boltzmann distribution (Eq. 3)
  2. J = -F identity verification (Eq. 4)
  3. Temperature sweep (phase behaviour)
  4. Grokking as phase transition (P2)
  5. Jailbreaking as Kramers escape (Eq. 9)
  6. Alignment-capability bound (P3)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rlhf_thermodynamics import (
    BoltzmannPolicy,
    FreeEnergyObjective,
    GrokkingPhaseTransition,
    JailbreakKramersEscape,
    AlignmentCapabilityBound,
    OptimalTemperatureScaling,
    RLHFIsomorphism,
)


def demo_boltzmann_policy():
    """1. Optimal RLHF policy is a Boltzmann distribution."""
    print("=" * 60)
    print("1. OPTIMAL POLICY = BOLTZMANN DISTRIBUTION (Eq. 3)")
    print("=" * 60)

    rewards = [2.0, 1.0, 0.5, -1.0]
    actions = ["helpful", "neutral", "verbose", "harmful"]

    for T in [0.5, 1.0, 3.0]:
        policy = BoltzmannPolicy(beta_kl=T, rewards=rewards)
        pi = policy.optimal_policy()
        print(f"\n  T = {T} (beta_KL = {T}):")
        for a, r, p in zip(actions, rewards, pi):
            print(f"    {a:>10s}: R={r:+.1f}  pi*={p:.4f}")
        print(f"    Entropy H = {policy.entropy():.4f}")
        print(f"    <R>       = {policy.expected_reward():.4f}")

    print("\n  -> Low T: concentrates on high-reward (aligned) action")
    print("  -> High T: explores more (higher entropy)")


def demo_free_energy_identity():
    """2. RLHF objective J = -F (algebraically exact)."""
    print("\n" + "=" * 60)
    print("2. J = -F IDENTITY VERIFICATION (Eq. 4)")
    print("=" * 60)

    rewards = [2.0, 1.0, 0.5, -1.0]
    fe = FreeEnergyObjective(beta_kl=1.0, rewards=rewards)
    v = fe.verify_identity()

    print(f"\n  Helmholtz free energy F = {v['F']:.6f}")
    print(f"  RLHF objective J = -F  = {fe.rlhf_objective():.6f}")
    print(f"  Internal energy E      = {v['E_internal']:.6f}")
    print(f"  T * S                  = {v['TS']:.6f}")
    print(f"  F = E - TS check       = {v['F_check']:.6f}")
    print(f"  Residual |F-(E-TS)|    = {v['residual']:.2e}")
    print(f"  Identity holds: {v['identity_holds']}")


def demo_temperature_sweep():
    """3. Temperature sweep showing phase behaviour."""
    print("\n" + "=" * 60)
    print("3. TEMPERATURE SWEEP (Phase Behaviour)")
    print("=" * 60)

    rewards = [3.0, 1.0, 0.0, -2.0]
    results = RLHFIsomorphism.temperature_sweep(
        rewards, temperatures=[0.1, 0.5, 1.0, 2.0, 5.0, 20.0]
    )

    print(f"\n  {'T':>6s}  {'H(pi)':>8s}  {'<R>':>8s}  {'F':>8s}  {'max(pi)':>8s}")
    print("  " + "-" * 44)
    for r in results:
        max_p = max(r["policy"])
        print(f"  {r['temperature']:6.1f}  {r['entropy']:8.4f}  "
              f"{r['expected_reward']:8.4f}  {r['F']:8.4f}  {max_p:8.4f}")

    print("\n  -> T->0: deterministic (H->0, max pi->1)")
    print("  -> T->inf: uniform (H->ln(n), max pi->1/n)")


def demo_grokking():
    """4. Grokking as first-order phase transition (P2)."""
    print("\n" + "=" * 60)
    print("4. GROKKING AS PHASE TRANSITION (Prediction P2)")
    print("=" * 60)

    scenarios = [
        ("Small modulus (p=5)", 3.0, 0.5, 0.1),
        ("Medium modulus (p=23)", 4.5, 1.0, 0.2),
        ("Large modulus (p=97)", 6.0, 1.5, 0.3),
    ]

    print(f"\n  {'Scenario':>25s}  {'H_mem':>6s}  {'H_gen':>6s}  {'T_eff':>6s}  "
          f"{'DeltaS':>7s}  {'L':>7s}  {'t_grok':>7s}")
    print("  " + "-" * 72)

    for name, h_mem, h_gen, t_eff in scenarios:
        g = GrokkingPhaseTransition(h_mem, h_gen, t_eff)
        print(f"  {name:>25s}  {h_mem:6.2f}  {h_gen:6.2f}  {t_eff:6.2f}  "
              f"{g.entropy_gap:7.2f}  {g.latent_heat:7.2f}  "
              f"{g.predicted_latent_period():7.1f}")

    print("\n  -> Larger entropy gap = longer latent period")
    print("  -> Higher T_eff = faster transition (less stalling)")
    print(f"  -> First-order: {all(GrokkingPhaseTransition(h, g, t).is_first_order() for _, h, g, t in scenarios)}")


def demo_jailbreak():
    """5. Jailbreaking as Kramers escape (Eq. 9)."""
    print("\n" + "=" * 60)
    print("5. JAILBREAKING AS KRAMERS ESCAPE (Eq. 9)")
    print("=" * 60)

    t_eff = 1.0
    print(f"\n  T_eff = {t_eff}")
    print(f"\n  {'Delta_F':>8s}  {'P(jail)':>12s}  {'Fold vs 1.0':>12s}")
    print("  " + "-" * 36)

    for df in [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]:
        jb = JailbreakKramersEscape(delta_f=df, t_eff=t_eff)
        fold = jb.fold_improvement(df - 0.5) if df > 0.5 else 1.0
        print(f"  {df:8.1f}  {jb.escape_probability():12.6f}  {fold:12.1f}x")

    # Show barrier needed for target
    jb = JailbreakKramersEscape(delta_f=1.0, t_eff=t_eff)
    target = 1e-6
    needed = jb.barrier_for_target_probability(target)
    print(f"\n  Barrier for P < {target}: Delta_F > {needed:.2f}")
    print("  -> Exponential suppression: modest barrier increase = huge safety gain")


def demo_alignment_capability():
    """6. Alignment-capability bound (P3)."""
    print("\n" + "=" * 60)
    print("6. ALIGNMENT-CAPABILITY BOUND (Prediction P3)")
    print("=" * 60)

    print(f"\n  A * C <= 1 - exp(-(F0-F*)/T)")
    print(f"\n  {'T':>6s}  {'F0-F*':>6s}  {'Bound':>8s}  {'A=0.9,C=0.9':>14s}")
    print("  " + "-" * 40)

    for T in [0.5, 1.0, 2.0, 5.0]:
        for gap in [2.0]:
            acb = AlignmentCapabilityBound(f0=gap, f_star=0.0, temperature=T)
            bound = acb.upper_bound()
            feasible = acb.is_feasible(0.9, 0.9)
            print(f"  {T:6.1f}  {gap:6.1f}  {bound:8.4f}  "
                  f"{'FEASIBLE' if feasible else 'VIOLATED':>14s}")

    print("\n  -> Lower T tightens the bound (more alignment = less capability)")
    print("  -> Larger free-energy gap relaxes the bound")


def demo_mapping_table():
    """Print complete isomorphism mapping."""
    print("\n" + "=" * 60)
    print("COMPLETE ISOMORPHISM TABLE")
    print("=" * 60)
    print(f"\n  {'RLHF Concept':>25s}  <->  {'Statistical Mechanics':<35s}")
    print("  " + "-" * 65)
    for rlhf, sm in RLHFIsomorphism.MAPPING.items():
        label = rlhf.replace("_", " ").title()
        print(f"  {label:>25s}  <->  {sm:<35s}")


if __name__ == "__main__":
    print("RLHF as Thermodynamic Entropy Minimisation")
    print("Magnusson (2026) — DOI: 10.6084/m9.figshare.31940535")
    print()

    demo_boltzmann_policy()
    demo_free_energy_identity()
    demo_temperature_sweep()
    demo_grokking()
    demo_jailbreak()
    demo_alignment_capability()
    demo_mapping_table()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("Key result: RLHF ≡ Free Energy Minimisation (exact)")
    print("=" * 60)
