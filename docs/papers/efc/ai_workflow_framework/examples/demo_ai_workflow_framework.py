#!/usr/bin/env python3
"""demo_ai_workflow_framework.py

Demonstrates the AI-Augmented Scientific Workflow Framework (v1.2).
Runs the full Human → AI → System → Validation pipeline and
optionally produces a diagnostic plot.
"""
import numpy as np
import json

from ai_workflow_framework import (
    shannon_entropy, kl_divergence, is_high_entropy,
    qa_score, formalise_question, rs_verify, sr_gate,
    run_pipeline, ALIGNMENT, novelty_signal,
    ENTROPY_HIGH_THRESHOLD, KL_NOVELTY_THRESHOLD,
    RS_PASS_THRESHOLD, SR_GATE_THRESHOLD,
)

# ── 1. Define a scientific question ──────────────────────────────────
question = formalise_question(
    intent="Does entropy-guided exploration improve hypothesis novelty?",
    dims={"testability": 0.85, "specificity": 0.70,
          "novelty": 0.92, "entropy_exposure": 0.65},
)
print("=== Question Architecture (QA) ===")
print(json.dumps(question, indent=2))

# ── 2. Simulate an information landscape ─────────────────────────────
np.random.seed(42)
n_topics = 16
landscape = np.random.dirichlet(np.ones(n_topics) * 0.3)   # high entropy
prior     = np.ones(n_topics) / n_topics                    # uniform prior

H = shannon_entropy(landscape)
kl, novel = novelty_signal(landscape, prior)
print(f"\n=== Entropy Navigation (EN) ===")
print(f"  Shannon entropy  : {H:.4f} bits")
print(f"  High-entropy?    : {is_high_entropy(landscape)}")
print(f"  KL(landscape||prior): {kl:.4f} nats  → novel={novel}")

# ── 3. Reflective Scaffolding ────────────────────────────────────────
rs_score, rs_pass = rs_verify(causal_grounding=0.88,
                               schema_compliance=0.92,
                               state_consistency=0.80)
print(f"\n=== Reflective Scaffolding (RS) ===")
print(f"  RS score : {rs_score}   passed : {rs_pass}")

# ── 4. Human Validation Gate (SR) ────────────────────────────────────
sr_score, gate = sr_gate(rs_score, provenance_complete=True)
print(f"\n=== Strict Separation / Gate (SR) ===")
print(f"  SR score : {sr_score}   gate passed : {gate}")

# ── 5. Full pipeline ─────────────────────────────────────────────────
result = run_pipeline(
    question_dims={"testability": 0.85, "specificity": 0.70,
                   "novelty": 0.92, "entropy_exposure": 0.65},
    landscape_p=landscape,
    prior_q=prior,
    rs_inputs={"causal_grounding": 0.88,
               "schema_compliance": 0.92,
               "state_consistency": 0.80},
    provenance_complete=True,
)
print("\n=== Full Pipeline Result ===")
print(json.dumps(result, indent=2, default=str))

# ── 6. Alignment summary ─────────────────────────────────────────────
print("\n=== Mechanism Alignment (Table §8) ===")
for mech, score in ALIGNMENT.items():
    label = {1.0: "High", 0.75: "Medium-High"}.get(score, str(score))
    print(f"  {mech}: {label} ({score})")

# ── 7. Optional plot ─────────────────────────────────────────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # (a) Entropy across varying landscape concentrations
    alphas = np.linspace(0.05, 5.0, 80)
    entropies = [shannon_entropy(np.random.dirichlet(np.ones(n_topics) * a))
                 for a in alphas]
    axes[0].plot(alphas, entropies, 'b-')
    axes[0].axhline(ENTROPY_HIGH_THRESHOLD * np.log2(n_topics),
                    ls='--', color='r', label='high-entropy threshold')
    axes[0].set(xlabel='Dirichlet α', ylabel='H (bits)',
                title='EN — Entropy vs concentration')
    axes[0].legend(fontsize=8)

    # (b) QA score sensitivity to testability
    test_vals = np.linspace(0, 1, 50)
    scores = [qa_score(t, 0.7, 0.9, 0.6) for t in test_vals]
    axes[1].plot(test_vals, scores, 'g-')
    axes[1].set(xlabel='Testability', ylabel='QA score',
                title='QA — Score vs Testability')

    # (c) SR gate composite vs RS score
    rs_range = np.linspace(0, 1, 50)
    composites = [0.6 * r + 0.4 * 1.0 for r in rs_range]  # prov=True
    axes[2].plot(rs_range, composites, 'm-')
    axes[2].axhline(SR_GATE_THRESHOLD, ls='--', color='r',
                    label=f'gate threshold ({SR_GATE_THRESHOLD})')
    axes[2].set(xlabel='RS score', ylabel='SR composite',
                title='SR — Gate Composite vs RS score')
    axes[2].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig('ai_workflow_framework_demo.png', dpi=150)
    print("\nPlot saved to ai_workflow_framework_demo.png")
    plt.show()
except ImportError:
    print("\nmatplotlib not available — skipping plot.")
