"""ai_workflow_framework.py

Reference implementation of the AI-Augmented Scientific Workflow Framework
(Version 1.2) by M. Magnusson.
DOI: 10.6084/m9.figshare.30636863

Implements the four core mechanisms:
  QA  – Question Architecture
  EN  – Entropy Navigation
  RS  – Reflective Scaffolding
  SR  – Strict Separation of Roles

All quantities are modelled with information-theoretic primitives so that
the framework can be exercised numerically.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Constants drawn from the paper
# ---------------------------------------------------------------------------
ALIGNMENT_SCORES: Dict[str, float] = {
    "QA": 1.0,       # High
    "EN": 1.0,       # High
    "RS": 0.75,      # Medium-High
    "SR": 1.0,       # High
}

ROLE_LABELS = ("HUMAN", "AI", "SYSTEM")

# Risk weights (equal priors – paper lists four risks)
RISK_NAMES = ["hallucination", "algorithmic_bias",
              "over_reliance", "incomplete_causal_grounding"]
DEFAULT_RISK_PRIOR = 0.25  # uniform over 4 risks


# ---------------------------------------------------------------------------
# QA – Question Architecture
# ---------------------------------------------------------------------------
def question_entropy(prob_vec: np.ndarray) -> float:
    """Shannon entropy H(Q) of a discrete question probability vector.

    H(Q) = -sum p_i log2(p_i)

    Parameters
    ----------
    prob_vec : array-like, shape (n,)
        Probability distribution over n candidate question branches.

    Returns
    -------
    float  –  entropy in bits
    """
    p = np.asarray(prob_vec, dtype=np.float64)
    p = p[p > 0]
    return -float(np.sum(p * np.log2(p)))


def qa_score(intent_vec: np.ndarray, formalized_vec: np.ndarray) -> float:
    """Cosine similarity between scientific-intent vector and its
    machine-readable formalisation.  QA converts intent → formal object;
    this metric measures fidelity of that conversion.

    Returns
    -------
    float in [-1, 1]
    """
    a = np.asarray(intent_vec, dtype=np.float64)
    b = np.asarray(formalized_vec, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


# ---------------------------------------------------------------------------
# EN – Entropy Navigation
# ---------------------------------------------------------------------------
def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL divergence D_KL(P || Q) used as divergence metric for
    entropy-based exploration.

    D_KL = sum p_i log2(p_i / q_i)
    """
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    mask = (p > 0) & (q > 0)
    return float(np.sum(p[mask] * np.log2(p[mask] / q[mask])))


def entropy_navigation_signal(landscape: np.ndarray,
                              threshold: float = 0.5) -> np.ndarray:
    """Identify high-entropy regions in an information landscape.

    For each row (candidate direction) compute Shannon entropy;
    return boolean mask where entropy exceeds *threshold* × H_max.

    Parameters
    ----------
    landscape : ndarray, shape (n_directions, n_features)
        Each row is a normalised probability profile.
    threshold : float
        Fraction of maximum possible entropy above which a
        direction is flagged as high-entropy (novel/uncertain).

    Returns
    -------
    mask : ndarray of bool, shape (n_directions,)
    """
    n_feat = landscape.shape[1]
    h_max = np.log2(n_feat)
    entropies = np.array([question_entropy(row) for row in landscape])
    return entropies >= threshold * h_max


# ---------------------------------------------------------------------------
# RS – Reflective Scaffolding
# ---------------------------------------------------------------------------
def rs_verification(ai_output: np.ndarray,
                    causal_model: np.ndarray,
                    tolerance: float = 0.10) -> Tuple[bool, float]:
    """Verify AI reflection against an external causal/formal model.

    Computes normalised L2 deviation.  If deviation < tolerance the
    output is *grounded*.

    Returns
    -------
    (grounded: bool, deviation: float)
    """
    a = np.asarray(ai_output, dtype=np.float64)
    c = np.asarray(causal_model, dtype=np.float64)
    norm = np.linalg.norm(c)
    if norm == 0:
        return (False, float('inf'))
    dev = float(np.linalg.norm(a - c) / norm)
    return (dev < tolerance, dev)


# ---------------------------------------------------------------------------
# SR – Strict Separation / Human Validation Gate
# ---------------------------------------------------------------------------
def human_validation_gate(rs_pass: bool,
                          qa_fidelity: float,
                          risk_scores: Optional[Dict[str, float]] = None,
                          qa_threshold: float = 0.70,
                          risk_threshold: float = 0.50) -> Tuple[bool, Dict]:
    """Final human validation gate.  Aggregates QA fidelity, RS
    grounding and residual risk.

    Parameters
    ----------
    rs_pass       : bool   – did reflective scaffolding pass?
    qa_fidelity   : float  – QA cosine score  [0,1]
    risk_scores   : dict   – per-risk probability estimates
    qa_threshold  : float  – minimum acceptable QA fidelity
    risk_threshold: float  – maximum acceptable aggregate risk

    Returns
    -------
    (approved: bool, report: dict)
    """
    if risk_scores is None:
        risk_scores = {r: DEFAULT_RISK_PRIOR for r in RISK_NAMES}
    agg_risk = float(np.mean(list(risk_scores.values())))
    approved = rs_pass and (qa_fidelity >= qa_threshold) and (agg_risk < risk_threshold)
    report = {
        "rs_grounded": rs_pass,
        "qa_fidelity": round(qa_fidelity, 4),
        "aggregate_risk": round(agg_risk, 4),
        "approved": approved,
    }
    return approved, report


def workflow_loop(intent: np.ndarray,
                  formalized: np.ndarray,
                  ai_output: np.ndarray,
                  causal_model: np.ndarray,
                  landscape: np.ndarray,
                  risk_scores: Optional[Dict[str, float]] = None
                  ) -> Dict:
    """Execute one full HUMAN → AI → SYSTEM → HUMAN loop."""
    qa = qa_score(intent, formalized)
    rs_ok, rs_dev = rs_verification(ai_output, causal_model)
    en_mask = entropy_navigation_signal(landscape)
    approved, report = human_validation_gate(rs_ok, qa, risk_scores)
    report["en_high_entropy_count"] = int(en_mask.sum())
    report["rs_deviation"] = round(rs_dev, 4)
    return report


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    rng = np.random.default_rng(42)
    # QA test
    intent = rng.random(8)
    formal = intent + rng.normal(0, 0.05, 8)
    print("QA fidelity:", round(qa_score(intent, formal), 4))

    # EN test
    landscape = rng.dirichlet(np.ones(6), size=10)
    mask = entropy_navigation_signal(landscape)
    print("EN high-entropy directions:", mask.sum(), "/", len(mask))

    # RS test
    causal = rng.random(5)
    ai_out = causal * 1.05
    grounded, dev = rs_verification(ai_out, causal)
    print(f"RS grounded={grounded}, deviation={dev:.4f}")

    # Full loop
    report = workflow_loop(intent, formal, ai_out, causal, landscape)
    print("Full loop report:", report)
