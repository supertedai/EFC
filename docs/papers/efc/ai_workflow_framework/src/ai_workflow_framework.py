"""ai_workflow_framework.py

Reference implementation of the AI-Augmented Scientific Workflow Framework
(Version 1.2) by M. Magnusson, DOI: 10.6084/m9.figshare.30636863

Implements the four core mechanisms:
  QA  — Question Architecture
  EN  — Entropy Navigation
  RS  — Reflective Scaffolding
  SR  — Strict Separation of Roles

Key quantities modelled
  * Shannon entropy of an information landscape
  * KL-divergence for novelty / surprise detection
  * Question-object formalisation and scoring
  * Reflective scaffolding verification score
  * Human-validation gate (SR pass/fail)
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple, Optional

# ── alignment scores from Table (Section 8) ──────────────────────────
ALIGNMENT: Dict[str, float] = {
    "QA": 1.0,      # High
    "EN": 1.0,      # High
    "RS": 0.75,     # Medium-High
    "SR": 1.0,      # High
}

# ── default thresholds ────────────────────────────────────────────────
ENTROPY_HIGH_THRESHOLD: float = 0.7   # above => high-entropy region
RS_PASS_THRESHOLD: float = 0.6        # reflective scaffolding minimum
SR_GATE_THRESHOLD: float = 0.8        # human-validation gate minimum
KL_NOVELTY_THRESHOLD: float = 0.5     # KL above => novel signal


# ───────────────────── Entropy Navigation (EN) ────────────────────────
def shannon_entropy(p: np.ndarray) -> float:
    """Compute Shannon entropy H = -sum(p_i log2 p_i) in bits."""
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    if p.size == 0:
        return 0.0
    p = p / p.sum()
    return -float(np.sum(p * np.log2(p)))


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL divergence D_KL(P || Q) = sum(p_i log(p_i / q_i)), nats."""
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    mask = (p > 0) & (q > 0)
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def is_high_entropy(p: np.ndarray, threshold: float = ENTROPY_HIGH_THRESHOLD) -> bool:
    """Return True when normalised entropy exceeds *threshold*."""
    h = shannon_entropy(p)
    h_max = np.log2(len(p)) if len(p) > 1 else 1.0
    return (h / h_max) >= threshold


def novelty_signal(p: np.ndarray, q: np.ndarray,
                   threshold: float = KL_NOVELTY_THRESHOLD) -> Tuple[float, bool]:
    """Return (kl_value, is_novel) for a candidate distribution *p* vs prior *q*."""
    kl = kl_divergence(p, q)
    return kl, kl >= threshold


# ──────────────────── Question Architecture (QA) ──────────────────────
def qa_score(testability: float, specificity: float,
             novelty: float, entropy_exposure: float) -> float:
    """Score a scientific question object.

    Each dimension in [0, 1].  Weighted combination reflecting
    framework priorities (structured intent, entropy navigation).
    """
    weights = np.array([0.30, 0.25, 0.25, 0.20])
    vals = np.array([testability, specificity, novelty, entropy_exposure])
    return float(np.dot(weights, np.clip(vals, 0.0, 1.0)))


def formalise_question(intent: str, dims: Dict[str, float]) -> Dict:
    """Convert scientific intent into a machine-readable question object."""
    score = qa_score(
        dims.get("testability", 0.0),
        dims.get("specificity", 0.0),
        dims.get("novelty", 0.0),
        dims.get("entropy_exposure", 0.0),
    )
    return {"intent": intent, "dimensions": dims, "qa_score": round(score, 4)}


# ─────────────── Reflective Scaffolding (RS) ──────────────────────────
def rs_verify(causal_grounding: float, schema_compliance: float,
              state_consistency: float,
              threshold: float = RS_PASS_THRESHOLD) -> Tuple[float, bool]:
    """Reflective-scaffolding verification.

    Returns (score, passed).  Each input in [0, 1].
    """
    w = np.array([0.40, 0.35, 0.25])
    v = np.clip(np.array([causal_grounding, schema_compliance,
                          state_consistency]), 0.0, 1.0)
    score = float(np.dot(w, v))
    return round(score, 4), score >= threshold


# ──────────────── Strict Separation / Human Gate (SR) ─────────────────
def sr_gate(rs_score: float, provenance_complete: bool,
            human_override: Optional[bool] = None,
            threshold: float = SR_GATE_THRESHOLD) -> Tuple[float, bool]:
    """Human-validation gate.

    *human_override* lets the human governor accept/reject regardless.
    """
    prov = 1.0 if provenance_complete else 0.0
    composite = 0.6 * rs_score + 0.4 * prov
    if human_override is not None:
        return round(composite, 4), human_override
    return round(composite, 4), composite >= threshold


# ─────────────── Full Workflow Pipeline ───────────────────────────────
def run_pipeline(question_dims: Dict[str, float],
                 landscape_p: np.ndarray,
                 prior_q: np.ndarray,
                 rs_inputs: Dict[str, float],
                 provenance_complete: bool = True,
                 human_override: Optional[bool] = None) -> Dict:
    """Execute the full Human → AI → System → Validation loop."""
    q_obj = formalise_question("auto", question_dims)
    h_val = shannon_entropy(landscape_p)
    high_e = is_high_entropy(landscape_p)
    kl_val, novel = novelty_signal(landscape_p, prior_q)
    rs_sc, rs_ok = rs_verify(**rs_inputs)
    sr_sc, sr_ok = sr_gate(rs_sc, provenance_complete, human_override)
    return {
        "qa": q_obj,
        "entropy": {"H_bits": round(h_val, 4), "high_entropy": high_e},
        "novelty": {"KL_nats": round(kl_val, 4), "novel": novel},
        "rs": {"score": rs_sc, "passed": rs_ok},
        "sr": {"score": sr_sc, "gate_passed": sr_ok},
        "overall_accepted": sr_ok,
    }


# ─────────────── Self-test ────────────────────────────────────────────
if __name__ == "__main__":
    # uniform distribution → max entropy
    u = np.ones(8) / 8
    assert abs(shannon_entropy(u) - 3.0) < 1e-9
    # peaked distribution → low entropy
    pk = np.array([0.97, 0.01, 0.01, 0.01])
    assert shannon_entropy(pk) < 0.5
    # QA score bounds
    assert 0.0 <= qa_score(1, 1, 1, 1) <= 1.0
    # RS verify
    sc, ok = rs_verify(0.9, 0.9, 0.9)
    assert ok
    # SR gate
    _, gated = sr_gate(sc, True)
    assert gated
    # pipeline smoke
    res = run_pipeline(
        {"testability": 0.8, "specificity": 0.7, "novelty": 0.9, "entropy_exposure": 0.6},
        u, pk, {"causal_grounding": 0.85, "schema_compliance": 0.9, "state_consistency": 0.8})
    assert res["overall_accepted"]
    print("All self-tests passed.")
