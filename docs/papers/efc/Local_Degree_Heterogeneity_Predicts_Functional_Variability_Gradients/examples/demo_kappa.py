#!/usr/bin/env python3
"""Demonstration: Centrifugal Entropy Score (kappa) Analysis.

Shows the hub-to-periphery functional variability gradient, the
dissociation between degree ratio and Fiedler eigenvalue, threshold
sensitivity, and clinical biomarker predictions.

DOI: 10.6084/m9.figshare.31940370
"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from connectome_kappa import (
    CentrifugalEntropyScore,
    ConnectomeAnalysis,
    ThresholdSensitivity,
    BiomarkerPredictions,
    compute_kappa,
    compute_fc_cv,
    compute_structural_log_degree,
    compute_degree_ratio,
)


def demo_kappa_definition():
    """Explain and compute kappa on a simple example."""
    print("=" * 70)
    print("CENTRIFUGAL ENTROPY SCORE: kappa = <S_hub> / <S_periph>")
    print("=" * 70)
    print()
    print("Definition:")
    print("  Hub regions:    top 10% of nodes by weighted structural degree")
    print("  Peripheral:     bottom 30% of nodes by weighted structural degree")
    print("  kappa > 1  =>   hubs have higher functional variability")
    print()

    # Synthetic 100-node connectome
    random.seed(42)
    n = 100
    # Power-law-like degree distribution
    degrees = sorted([random.paretovariate(1.5) for _ in range(n)], reverse=True)
    # Entropy proxy: log-degree + noise
    entropy = [compute_structural_log_degree(d) + random.gauss(0, 0.1) for d in degrees]

    scorer = CentrifugalEntropyScore()
    kappa = scorer.compute(entropy, degrees)
    interpretation = scorer.interpret(kappa)

    print(f"Synthetic 100-node connectome:")
    print(f"  kappa = {kappa:.3f}")
    print(f"  {interpretation}")
    print(f"  Degree ratio = {compute_degree_ratio(degrees):.2f}")
    print()


def demo_paper_results():
    """Reproduce key results from the paper (Tables 3-5)."""
    print("=" * 70)
    print("PAPER RESULTS (Tables 3-5)")
    print("=" * 70)
    print()

    # Table 3: Group-average kappa across atlases
    atlases = [
        ("Desikan-68", 68, 0.954, 1.267),
        ("Schaefer-100", 100, 1.143, 1.165),
        ("Schaefer-200", 200, 1.198, 1.182),
        ("Schaefer-300", 300, 1.250, 1.180),
        ("Glasser-360", 360, 1.099, 1.202),
        ("Schaefer-400", 400, 1.097, 1.184),
    ]

    print("Table 3: Centrifugal entropy score across parcellation atlases")
    print(f"{'Atlas':<16s} {'N':>5s} {'kappa(FC-CV)':>14s} {'kappa(struct)':>14s}")
    print("-" * 52)
    for name, n, k_fc, k_str in atlases:
        print(f"{name:<16s} {n:5d} {k_fc:14.3f} {k_str:14.3f}")

    # Compute CV
    k_struct = [a[3] for a in atlases]
    mean_s = sum(k_struct) / len(k_struct)
    std_s = math.sqrt(sum((k - mean_s)**2 for k in k_struct) / (len(k_struct) - 1))
    print(f"\nStructural kappa CV = {std_s/mean_s:.1%} (scale-invariant)")
    print()

    # Table 4: Feature correlations
    print("Table 4: Feature correlations with kappa (n=6 atlases)")
    features = [
        ("Peripheral mean degree", 0.86, 0.028),
        ("Degree ratio", -0.83, 0.042),
        ("Clustering coefficient", -0.78, 0.067),
        ("Modularity Q", 0.73, 0.100),
        ("Hub mean degree", -0.75, 0.088),
        ("Fiedler eigenvalue", -0.63, 0.178),
        ("Betweenness ratio", -0.56, 0.249),
        ("Participation ratio", 0.47, 0.344),
    ]
    print(f"{'Feature':<28s} {'r':>8s} {'p':>8s} {'Sig?':>6s}")
    print("-" * 54)
    for name, r, p in features:
        sig = "  *" if p < 0.05 else ""
        print(f"{name:<28s} {r:+8.2f} {p:8.3f} {sig:>6s}")
    print()

    # Table 5: Individual-subject results
    print("Table 5: Individual-subject analysis (n=8, 219 regions)")
    print(f"  kappa = 2.20 +/- 0.15")
    print(f"  r(kappa, 1/D_ratio) = -0.97, p < 0.001, r^2 = 0.94")
    print(f"  r(kappa, 1/lambda2) = +0.16, p = 0.70")
    print()
    print("  => Degree ratio explains 94% of inter-subject variance")
    print("  => Fiedler eigenvalue has NO predictive power")
    print()


def demo_dissociation():
    """Highlight the local vs global dissociation."""
    print("=" * 70)
    print("KEY DISSOCIATION: Local (degree) vs Global (Fiedler)")
    print("=" * 70)
    print()
    print("  LOCAL predictor  (degree ratio):     r = -0.97, p < 0.001")
    print("  GLOBAL predictor (Fiedler lambda2):  r = +0.16, p = 0.70")
    print()
    print("  Implication: Functional variability gradients are shaped by")
    print("  local degree contrast, NOT global spectral properties.")
    print()
    print("  This challenges the prominence of algebraic connectivity")
    print("  (lambda2) in network neuroscience models of brain function.")
    print()


def demo_threshold_sensitivity():
    """Demonstrate threshold sensitivity on synthetic data."""
    print("=" * 70)
    print("THRESHOLD SENSITIVITY (30 combinations)")
    print("=" * 70)
    print()

    # Synthetic data with clear hub-periphery gradient
    random.seed(42)
    n = 200
    degrees = sorted([random.paretovariate(1.5) for _ in range(n)], reverse=True)
    entropy = [compute_structural_log_degree(d) + random.gauss(0, 0.05) for d in degrees]

    sensitivity = ThresholdSensitivity()
    result = sensitivity.run(entropy, degrees)

    print(f"  Combinations tested: {result['n_combinations']}")
    print(f"  All kappa > 1: {result['all_above_unity']}")
    print(f"  kappa range: [{result['kappa_range'][0]:.3f}, {result['kappa_range'][1]:.3f}]")
    print(f"  kappa mean: {result['kappa_mean']:.3f}")
    print(f"  kappa CV: {result['kappa_cv']:.1%}")
    print()
    print("  Paper result (Schaefer-200): structural CV = 1.7%, FC-CV = 3.2%")
    print("  All 30 combinations yield kappa > 1 in both proxies.")
    print()


def demo_biomarker_predictions():
    """Show clinical predictions."""
    print("=" * 70)
    print("BIOMARKER PREDICTIONS")
    print("=" * 70)
    print()

    for pred in BiomarkerPredictions.predictions():
        print(f"  {pred['domain']}:")
        print(f"    Prediction: {pred['prediction']}")
        print(f"    Mechanism:  {pred['mechanism']}")
        print(f"    Test with:  {pred['testable_with']}")
        print()


def demo_entropy_proxies():
    """Show the two entropy proxies."""
    print("=" * 70)
    print("ENTROPY PROXIES")
    print("=" * 70)
    print()
    print("  Primary: FC-CV = std(FC_i) / mean(|FC_i|)")
    print("    Captures functional connection diversity")
    print("    Available for group-average (Dataset 1)")
    print()
    print("  Secondary: S = log(1 + degree)")
    print("    Purely structural proxy")
    print("    Available for both datasets")
    print()

    # Example computation
    fc_row = [0.3, -0.1, 0.5, 0.2, -0.4, 0.6, -0.2, 0.1]
    cv = compute_fc_cv(fc_row)
    print(f"  Example FC row: {fc_row}")
    print(f"  FC-CV = {cv:.4f}")
    print()

    degrees = [5, 20, 50, 100, 200]
    print(f"  {'Degree':>8s}  {'log(1+deg)':>12s}")
    print("  " + "-" * 22)
    for d in degrees:
        print(f"  {d:8d}  {compute_structural_log_degree(d):12.4f}")
    print()


if __name__ == "__main__":
    demo_kappa_definition()
    demo_paper_results()
    demo_dissociation()
    demo_threshold_sensitivity()
    demo_entropy_proxies()
    demo_biomarker_predictions()
    print("All demonstrations complete.")
