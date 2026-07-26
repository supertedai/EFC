"""demo_ai_workflow_framework.py

Demonstrates the AI-Augmented Scientific Workflow Framework.
Runs a full HUMAN → AI → SYSTEM → HUMAN validation cycle,
prints diagnostics and optionally produces a summary plot.
"""
import numpy as np
import json

from ai_workflow_framework import (
    question_entropy, qa_score, kl_divergence,
    entropy_navigation_signal, rs_verification,
    human_validation_gate, workflow_loop,
    ALIGNMENT_SCORES, RISK_NAMES, DEFAULT_RISK_PRIOR,
)


def main() -> None:
    rng = np.random.default_rng(2025)

    # --- 1. Question Architecture (QA) ------------------------------------
    n_branches = 8
    uniform = np.ones(n_branches) / n_branches
    focused = np.array([0.6, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01])
    print("=== Question Architecture (QA) ===")
    print(f"  Uniform question entropy : {question_entropy(uniform):.4f} bits")
    print(f"  Focused question entropy : {question_entropy(focused):.4f} bits")

    intent_vec = rng.random(10)
    formal_vec = intent_vec + rng.normal(0, 0.02, 10)
    fidelity = qa_score(intent_vec, formal_vec)
    print(f"  QA fidelity (cosine)     : {fidelity:.4f}")

    # --- 2. Entropy Navigation (EN) ---------------------------------------
    n_directions, n_features = 20, 6
    landscape = rng.dirichlet(np.ones(n_features), size=n_directions)
    mask = entropy_navigation_signal(landscape, threshold=0.5)
    print("\n=== Entropy Navigation (EN) ===")
    print(f"  Directions explored      : {n_directions}")
    print(f"  High-entropy (novel)     : {mask.sum()}")
    print(f"  Low-entropy (familiar)   : {(~mask).sum()}")

    prior = np.ones(n_features) / n_features
    posterior = focused[:n_features] / focused[:n_features].sum()
    print(f"  KL(posterior || prior)    : {kl_divergence(posterior, prior):.4f} bits")

    # --- 3. Reflective Scaffolding (RS) -----------------------------------
    causal_model = rng.random(12)
    ai_good = causal_model * (1 + rng.normal(0, 0.03, 12))
    ai_bad = causal_model * (1 + rng.normal(0, 0.30, 12))
    ok1, d1 = rs_verification(ai_good, causal_model, tolerance=0.10)
    ok2, d2 = rs_verification(ai_bad, causal_model, tolerance=0.10)
    print("\n=== Reflective Scaffolding (RS) ===")
    print(f"  Good AI output : grounded={ok1}, dev={d1:.4f}")
    print(f"  Bad  AI output : grounded={ok2}, dev={d2:.4f}")

    # --- 4. Strict Separation / Validation Gate (SR) ----------------------
    risk_low = {r: 0.10 for r in RISK_NAMES}
    risk_high = {r: 0.60 for r in RISK_NAMES}
    app1, rep1 = human_validation_gate(True, 0.95, risk_low)
    app2, rep2 = human_validation_gate(False, 0.50, risk_high)
    print("\n=== Human Validation Gate (SR) ===")
    print(f"  Scenario A (low risk)  : approved={app1}  {rep1}")
    print(f"  Scenario B (high risk) : approved={app2}  {rep2}")

    # --- 5. Full workflow loop --------------------------------------------
    report = workflow_loop(intent_vec, formal_vec, ai_good,
                           causal_model, landscape, risk_low)
    print("\n=== Full Workflow Loop ===")
    print(json.dumps(report, indent=2))

    # --- 6. Alignment summary ---------------------------------------------
    print("\n=== Mechanism Alignment Scores (from paper Table §8) ===")
    for mech, score in ALIGNMENT_SCORES.items():
        bar = "█" * int(score * 20)
        print(f"  {mech} : {score:.2f}  {bar}")

    # --- 7. Optional plot --------------------------------------------------
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(14, 4))

        # (a) Question entropy comparison
        labels = ["Uniform", "Focused"]
        vals = [question_entropy(uniform), question_entropy(focused)]
        axes[0].bar(labels, vals, color=["steelblue", "coral"])
        axes[0].set_ylabel("Entropy (bits)")
        axes[0].set_title("QA: Question Entropy")

        # (b) Entropy landscape
        ent_vals = np.array([question_entropy(row) for row in landscape])
        colors = ["coral" if m else "steelblue" for m in mask]
        axes[1].bar(range(n_directions), ent_vals, color=colors)
        axes[1].axhline(0.5 * np.log2(n_features), ls="--", color="grey",
                        label="threshold")
        axes[1].set_xlabel("Direction")
        axes[1].set_ylabel("Entropy (bits)")
        axes[1].set_title("EN: Landscape Entropy")
        axes[1].legend()

        # (c) Alignment scores
        mechs = list(ALIGNMENT_SCORES.keys())
        scores = list(ALIGNMENT_SCORES.values())
        axes[2].barh(mechs, scores, color="teal")
        axes[2].set_xlim(0, 1.1)
        axes[2].set_xlabel("Alignment")
        axes[2].set_title("Mechanism Alignment (§8)")

        plt.tight_layout()
        plt.savefig("workflow_framework_demo.png", dpi=150)
        print("\nPlot saved to workflow_framework_demo.png")
        plt.show()
    except ImportError:
        print("\nmatplotlib not available – skipping plot.")


if __name__ == "__main__":
    main()
