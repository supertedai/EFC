#!/usr/bin/env python3
"""demo_ai_workflow_framework.py

Demonstrates the AI-Augmented Scientific Workflow Framework
(Magnusson, Version 1.2) end-to-end:
  HUMAN intent  →  QA  →  EN  →  RS  →  SR  →  Validation Gate

Optionally produces a summary plot (saved as workflow_dashboard.png).
"""
import numpy as np
import json

from ai_workflow_framework import (
    qa_formalize, en_navigate, en_shannon_entropy,
    rs_verify, sr_role_audit, human_validation_gate,
    ALIGNMENT_SCORES, ENTROPY_HIGH_THRESHOLD,
    KL_NOVELTY_THRESHOLD, RS_GROUNDING_THRESHOLD,
    HUMAN_GATE_MIN_SCORE,
)

# ------------------------------------------------------------------
# 1. HUMAN stage — define scientific intent
# ------------------------------------------------------------------
question = "Does dark-energy density evolve with cosmic time?"
intent = np.array([0.45, 0.30, 0.15, 0.05, 0.05])  # 5-dim intent embedding
domains = ["cosmology", "dark_energy", "observational"]

qa = qa_formalize(question, intent, domains)
print("[QA] Formalised question object:")
print(json.dumps(qa, indent=2))

# ------------------------------------------------------------------
# 2. AI stage — Entropy Navigation (EN)
# ------------------------------------------------------------------
prior = np.ones(5) / 5                           # uniform prior
posterior = np.array([0.50, 0.25, 0.12, 0.08, 0.05])  # after AI scan
en = en_navigate(prior, posterior, threshold=KL_NOVELTY_THRESHOLD)
print("\n[EN] Entropy Navigation result:")
print(json.dumps(en, indent=2))

# ------------------------------------------------------------------
# 3. AI stage — Reflective Scaffolding (RS)
# ------------------------------------------------------------------
# Small causal DAG: 0->1, 0->2, 1->3, 2->3, 3->4
adj = np.array([
    [0,1,1,0,0],
    [0,0,0,1,0],
    [0,0,0,1,0],
    [0,0,0,0,1],
    [0,0,0,0,0],
], dtype=float)
claim_nodes = [3, 4]  # claims to verify
rs = rs_verify(adj, claim_nodes, threshold=RS_GROUNDING_THRESHOLD)
print("\n[RS] Reflective Scaffolding verification:")
print(json.dumps(rs, indent=2))

# ------------------------------------------------------------------
# 4. SYSTEM stage — Strict Separation audit (SR)
# ------------------------------------------------------------------
contributions = {
    "conceptual_direction": "HUMAN",
    "question_architecture": "HUMAN",
    "interpretation": "HUMAN",
    "final_validation": "HUMAN",
    "formal_drafting": "AI",
    "reflective_scaffolding": "AI",
    "uncertainty_exploration": "AI",
    "schema_validation": "SYSTEM",
    "version_control": "SYSTEM",
    "metadata": "SYSTEM",
}
sr = sr_role_audit(contributions)
print("\n[SR] Role-separation audit:")
print(json.dumps(sr, indent=2))

# ------------------------------------------------------------------
# 5. HUMAN VALIDATION GATE
# ------------------------------------------------------------------
gate = human_validation_gate(qa, en, rs, sr)
print("\n[GATE] Human Validation Gate:")
print(json.dumps(gate, indent=2))
if gate["pass"]:
    print("\n>>> GATE PASSED — workflow output accepted.")
else:
    print("\n>>> GATE FAILED — requires human review / iteration.")

# ------------------------------------------------------------------
# 6. Optional plot
# ------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("AI Workflow Framework — Dashboard", fontsize=14)

    # (a) Intent distribution
    ax = axes[0, 0]
    ax.bar(range(len(intent)), intent / intent.sum(), color="steelblue")
    ax.set_title(f"QA Intent  (H_norm={qa['entropy']:.3f})")
    ax.set_xlabel("Dimension")
    ax.set_ylabel("Weight")

    # (b) Prior vs posterior
    ax = axes[0, 1]
    x = np.arange(len(prior))
    w = 0.35
    ax.bar(x - w/2, prior, w, label="Prior", color="gray")
    ax.bar(x + w/2, posterior / posterior.sum(), w, label="Posterior", color="coral")
    ax.set_title(f"EN  KL={en['KL_divergence']:.3f}")
    ax.legend()

    # (c) Alignment scores
    ax = axes[1, 0]
    mechs = list(ALIGNMENT_SCORES.keys())
    vals = [ALIGNMENT_SCORES[m] for m in mechs]
    colors = ["#4CAF50" if v >= 1.0 else "#FFC107" for v in vals]
    ax.barh(mechs, vals, color=colors)
    ax.set_xlim(0, 1.15)
    ax.set_title("Mechanism Alignment (paper Table)")

    # (d) Gate component scores
    ax = axes[1, 1]
    comp = gate["component_scores"]
    labels = list(comp.keys())
    scores = [comp[k] for k in labels]
    bar_colors = ["#4CAF50" if s >= 0.8 else "#F44336" for s in scores]
    ax.bar(labels, scores, color=bar_colors)
    ax.axhline(HUMAN_GATE_MIN_SCORE, ls="--", color="k", label="gate threshold")
    ax.set_ylim(0, 1.15)
    ax.set_title(f"Gate aggregate={gate['aggregate']:.3f}")
    ax.legend()

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("workflow_dashboard.png", dpi=150)
    print("\nPlot saved to workflow_dashboard.png")
except ImportError:
    print("\nmatplotlib not available — skipping plot.")
