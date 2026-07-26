"""ai_workflow_framework.py

Reference implementation of the AI-Augmented Scientific Workflow Framework
(Version 1.2) by M. Magnusson.
DOI: 10.6084/m9.figshare.30636863

Implements the four core mechanisms:
  QA  — Question Architecture
  EN  — Entropy Navigation
  RS  — Reflective Scaffolding
  SR  — Strict Separation of Roles

Key formalisms
--------------
* Information-entropy scoring of question / answer landscapes
* KL-divergence-based novelty search for Entropy Navigation
* Reflective Scaffolding verification via causal-graph grounding
* Human Validation Gate with role-separation audit
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Constants drawn from the paper (Section 8 alignment table & framework spec)
# ---------------------------------------------------------------------------
ALIGNMENT_SCORES: Dict[str, float] = {
    "QA": 1.0,       # High
    "EN": 1.0,       # High
    "RS": 0.75,      # Medium-High
    "SR": 1.0,       # High
}

ROLE_LABELS = ("HUMAN", "AI", "SYSTEM")

# Default thresholds used in the implementation
ENTROPY_HIGH_THRESHOLD: float = 0.7   # normalised, above => high-entropy zone
KL_NOVELTY_THRESHOLD: float = 0.5     # KL divergence for novelty detection
RS_GROUNDING_THRESHOLD: float = 0.6   # min causal-grounding score to pass RS
HUMAN_GATE_MIN_SCORE: float = 0.8     # aggregate score to pass validation gate
FAIR_COMPLIANCE_WEIGHTS: Dict[str, float] = {
    "Findable": 0.25, "Accessible": 0.25,
    "Interoperable": 0.25, "Reusable": 0.25,
}

# ---------------------------------------------------------------------------
# QA — Question Architecture
# ---------------------------------------------------------------------------

def qa_formalize(question_text: str,
                 intent_vector: np.ndarray,
                 domain_tags: List[str]) -> Dict:
    """Convert scientific intent into a machine-readable QA object.

    Parameters
    ----------
    question_text : str
        Natural-language scientific question.
    intent_vector : np.ndarray
        Numeric vector encoding scientific intent (unit-normalised).
    domain_tags : list[str]
        Categorical domain labels.

    Returns
    -------
    dict  — machine-readable question object with entropy estimate.
    """
    intent_norm = intent_vector / (np.linalg.norm(intent_vector) + 1e-12)
    # Shannon entropy of the normalised intent distribution (clipped for log)
    p = np.abs(intent_norm) / (np.sum(np.abs(intent_norm)) + 1e-12)
    entropy = -np.sum(p * np.log2(p + 1e-12))
    max_entropy = np.log2(len(p) + 1e-12)
    normalised_entropy = float(entropy / (max_entropy + 1e-12))
    return {
        "question": question_text,
        "intent_vector": intent_norm.tolist(),
        "domain_tags": domain_tags,
        "entropy": normalised_entropy,
        "high_entropy": normalised_entropy > ENTROPY_HIGH_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# EN — Entropy Navigation
# ---------------------------------------------------------------------------

def en_shannon_entropy(p: np.ndarray) -> float:
    """Compute Shannon entropy H(p) = -sum(p_i log2 p_i)."""
    p = np.asarray(p, dtype=np.float64)
    p = p / (p.sum() + 1e-12)
    return float(-np.sum(p * np.log2(p + 1e-12)))


def en_kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL divergence D_KL(p || q) used as novelty / divergence metric."""
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    return float(np.sum(p * np.log2((p + 1e-12) / (q + 1e-12))))


def en_navigate(prior: np.ndarray,
                posterior: np.ndarray,
                threshold: float = KL_NOVELTY_THRESHOLD
                ) -> Dict:
    """Entropy Navigation step: compare prior and posterior landscapes.

    Returns divergence metric and whether the region is novel enough to explore.
    """
    h_prior = en_shannon_entropy(prior)
    h_post = en_shannon_entropy(posterior)
    kl = en_kl_divergence(posterior, prior)
    return {
        "H_prior": h_prior,
        "H_posterior": h_post,
        "KL_divergence": kl,
        "delta_entropy": h_post - h_prior,
        "novel": kl > threshold,
    }


# ---------------------------------------------------------------------------
# RS — Reflective Scaffolding
# ---------------------------------------------------------------------------

def rs_grounding_score(causal_adjacency: np.ndarray,
                       claim_nodes: List[int]) -> float:
    """Compute a causal-grounding score for a set of claim nodes.

    Uses the fraction of claim nodes that are reachable from at least one
    root (node with in-degree 0) in the causal DAG encoded by
    *causal_adjacency*.
    """
    A = np.asarray(causal_adjacency, dtype=np.float64)
    n = A.shape[0]
    # Reachability via matrix power series (boolean)
    reach = np.eye(n, dtype=bool)
    power = A.astype(bool)
    for _ in range(n):
        reach = reach | power
        power = power @ A.astype(bool)
    in_deg = A.sum(axis=0)
    roots = np.where(in_deg == 0)[0]
    if len(roots) == 0 or len(claim_nodes) == 0:
        return 0.0
    grounded = 0
    for c in claim_nodes:
        if any(reach[r, c] for r in roots):
            grounded += 1
    return grounded / len(claim_nodes)


def rs_verify(causal_adjacency: np.ndarray,
              claim_nodes: List[int],
              threshold: float = RS_GROUNDING_THRESHOLD) -> Dict:
    """Reflective Scaffolding verification gate."""
    score = rs_grounding_score(causal_adjacency, claim_nodes)
    return {
        "grounding_score": score,
        "threshold": threshold,
        "pass": score >= threshold,
    }


# ---------------------------------------------------------------------------
# SR — Strict Separation / Human Validation Gate
# ---------------------------------------------------------------------------

def sr_role_audit(contributions: Dict[str, str]) -> Dict:
    """Audit a set of contributions against allowed roles."""
    human_tasks = {"conceptual_direction", "theoretical_framing",
                   "question_architecture", "interpretation",
                   "final_validation"}
    ai_tasks = {"formal_drafting", "symbolic_structuring",
                "documentation_support", "reflective_scaffolding",
                "uncertainty_exploration"}
    system_tasks = {"version_control", "schema_validation",
                    "build_pipelines", "metadata",
                    "machine_readable_structure"}
    violations: List[str] = []
    for task, role in contributions.items():
        if role == "HUMAN" and task not in human_tasks:
            violations.append(f"HUMAN assigned non-human task '{task}'")
        elif role == "AI" and task not in ai_tasks:
            violations.append(f"AI assigned non-AI task '{task}'")
        elif role == "SYSTEM" and task not in system_tasks:
            violations.append(f"SYSTEM assigned non-system task '{task}'")
    return {"violations": violations, "compliant": len(violations) == 0}


def human_validation_gate(qa_obj: Dict,
                          en_obj: Dict,
                          rs_obj: Dict,
                          sr_obj: Dict,
                          weights: Optional[Dict[str, float]] = None
                          ) -> Dict:
    """Aggregate gate: all four mechanisms must pass."""
    if weights is None:
        weights = {k: v for k, v in ALIGNMENT_SCORES.items()}
    scores = {
        "QA": 1.0 - qa_obj.get("entropy", 1.0),  # lower raw entropy => clearer intent
        "EN": 1.0 if en_obj.get("novel", False) else 0.4,
        "RS": rs_obj.get("grounding_score", 0.0),
        "SR": 1.0 if sr_obj.get("compliant", False) else 0.0,
    }
    weighted = sum(scores[k] * weights[k] for k in scores) / (sum(weights.values()) + 1e-12)
    return {
        "component_scores": scores,
        "weights": weights,
        "aggregate": float(weighted),
        "pass": weighted >= HUMAN_GATE_MIN_SCORE,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Self-test: AI Workflow Framework ===")

    # QA test
    iv = np.array([0.5, 0.3, 0.1, 0.1])
    qa = qa_formalize("What drives cosmic expansion?", iv, ["cosmology"])
    print(f"QA object entropy: {qa['entropy']:.4f}  high_entropy={qa['high_entropy']}")
    assert 0.0 <= qa["entropy"] <= 1.0

    # EN test
    prior = np.array([0.25, 0.25, 0.25, 0.25])
    posterior = np.array([0.6, 0.2, 0.1, 0.1])
    en = en_navigate(prior, posterior)
    print(f"EN  KL={en['KL_divergence']:.4f}  novel={en['novel']}")

    # RS test
    adj = np.array([[0,1,0],[0,0,1],[0,0,0]], dtype=float)
    rs = rs_verify(adj, [2])
    print(f"RS  grounding={rs['grounding_score']:.2f}  pass={rs['pass']}")

    # SR test
    contribs = {"conceptual_direction": "HUMAN",
                "formal_drafting": "AI",
                "schema_validation": "SYSTEM"}
    sr = sr_role_audit(contribs)
    print(f"SR  compliant={sr['compliant']}")

    # Gate test
    gate = human_validation_gate(qa, en, rs, sr)
    print(f"GATE aggregate={gate['aggregate']:.4f}  pass={gate['pass']}")
    print("Self-test complete.")
