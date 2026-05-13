from __future__ import annotations
import json, hashlib, time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np

"""
RCE Versjon: Operational governance machinery from
"Ledger Epistemology and Regime-Closure Governance: An Operational Framework for Validation in Coupled Multi-Scale Systems"
DOI: 10.6084/m9.figshare.32256951 (May 12, 2026, v1.0)

This module implements the paper's core operational components:
- Regime architecture with explicit tagging and coupling operators
- Frozen-parameter governance (shared, locked across regimes)
- Sealed, pre-registered predictions with cryptographic deposit hashes
- Living falsification ledger preserving failed predictions and failure modes
- External arbitration hooks (structural separation from predictor)

Note: The provided excerpt contains no domain equations or numerical model constants.
Accordingly, this module implements the governance machine itself and a generic
array-based test metric (mean absolute error) using NumPy to operationalize
thresholded predictions, as described in the paper's framework narrative.

Paper constants included from the excerpt:
- LEDGER_VERSION = "4.6"
- EFC_COUNTS = {dois: 163, registered_tests: 135, falsifications: 11}
- YEARS_FIELD_TESTED = (2024, 2026)
- CROSS_DOMAIN_REGISTERED_PREDICTIONS = 7
- FRAMEWORK_FALSIFICATION_CONDITIONS = 5
- Example regime scaffolds for medicine (M0–M3) and economics (E0–E3)
"""

LEDGER_VERSION: str = "4.6"
EFC_COUNTS: Dict[str, int] = {"dois": 163, "registered_tests": 135, "falsifications": 11}
YEARS_FIELD_TESTED = (2024, 2026)
CROSS_DOMAIN_REGISTERED_PREDICTIONS = 7
FRAMEWORK_FALSIFICATION_CONDITIONS = 5
REGIME_ARCH_EXAMPLES = {
    "medicine": ["M0", "M1", "M2", "M3"],
    "economics": ["E0", "E1", "E2", "E3"],
}


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Regime:
    tag: str
    level: int
    domain: str
    description: str = ""


class CouplingMap:
    """Defines allowed cross-regime inferences.
    By default, inference is forbidden unless explicitly allowed.
    """

    def __init__(self) -> None:
        self._allowed: Dict[tuple[str, str], str] = {}

    def allow(self, src: str, dst: str, operator: str) -> None:
        self._allowed[(src, dst)] = operator

    def is_allowed(self, src: str, dst: str) -> bool:
        return (src, dst) in self._allowed

    def operator(self, src: str, dst: str) -> Optional[str]:
        return self._allowed.get((src, dst))


class FrozenParamStore:
    """Shared, frozen parameters locked across regime boundaries.
    Once locked, parameters cannot be modified; their hash snapshots tag predictions.
    """

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._params: Dict[str, Any] = dict(initial or {})
        self._locked: bool = False

    def set(self, name: str, value: Any) -> None:
        if self._locked:
            raise RuntimeError("Frozen parameters are locked; cannot modify.")
        self._params[name] = value

    def get(self, name: str) -> Any:
        return self._params[name]

    def lock(self) -> None:
        self._locked = True

    def is_locked(self) -> bool:
        return self._locked

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._params)

    def snapshot_hash(self) -> str:
        return sha256_hex(_canonical_json(self._params))


@dataclass
class SealedPrediction:
    """Sealed, pre-registered prediction bound to a regime and a frozen-parameter snapshot.

    spec layout (example):
    {
        "predicted": [1.0, 1.0, 1.0],
        "metric": "mae",                 # mean absolute error
        "thresholds": {"mae_max": 0.1},  # pass if mae <= mae_max
        "source_regimes": ["M0"],        # any dependency sources
    }
    """

    pid: str
    regime: str
    frozen_params_hash: str
    spec: Dict[str, Any]
    author_id: str
    deposit_doi: str
    sealed_hash: Optional[str] = None
    sealed_time: Optional[float] = None

    def seal(self) -> None:
        if self.sealed_hash is not None:
            raise RuntimeError("Already sealed")
        payload = {
            "pid": self.pid,
            "regime": self.regime,
            "frozen_params_hash": self.frozen_params_hash,
            "spec": self.spec,
            "author_id": self.author_id,
            "deposit_doi": self.deposit_doi,
        }
        self.sealed_time = time.time()
        payload["sealed_time"] = self.sealed_time
        self.sealed_hash = sha256_hex(_canonical_json(payload))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "regime": self.regime,
            "frozen_params_hash": self.frozen_params_hash,
            "spec": self.spec,
            "author_id": self.author_id,
            "deposit_doi": self.deposit_doi,
            "sealed_hash": self.sealed_hash,
            "sealed_time": self.sealed_time,
        }


@dataclass
class ArbitrationRecord:
    arbitrator_id: str
    outcome: str  # "confirm" or "reject"
    reference_uri: str
    timestamp: float = field(default_factory=lambda: time.time())


def evaluate(pred: SealedPrediction, observed: List[float] | np.ndarray,
             params: FrozenParamStore, couplings: CouplingMap) -> Dict[str, Any]:
    """Evaluate a sealed prediction against observed data under governance checks.

    Returns a result dict with keys: status, metric, value, threshold, details.
    """
    if pred.sealed_hash is None:
        raise RuntimeError("Prediction must be sealed before evaluation.")
    # Frozen-parameter governance: no re-tuning after sealing
    if pred.frozen_params_hash != params.snapshot_hash():
        return {
            "status": "invalidated_by_param_change",
            "details": "Frozen-parameter snapshot differs from sealed snapshot.",
        }
    # Regime-closure governance: forbid cross-regime inference unless coupled
    for src in pred.spec.get("source_regimes", []):
        if not couplings.is_allowed(src, pred.regime):
            return {
                "status": "cross_regime_forbidden",
                "details": f"No coupling operator from {src} to {pred.regime}.",
            }
    predicted = np.asarray(pred.spec.get("predicted"))
    observed = np.asarray(observed)
    if predicted.shape != observed.shape:
        return {"status": "shape_mismatch", "details": str((predicted.shape, observed.shape))}

    metric = pred.spec.get("metric", "mae")
    if metric == "mae":
        val = float(np.mean(np.abs(observed - predicted)))
        thr = float(pred.spec.get("thresholds", {}).get("mae_max", np.inf))
        passed = val <= thr
        return {
            "status": "passed" if passed else "failed",
            "metric": metric,
            "value": val,
            "threshold": thr,
            "details": None,
        }
    else:
        return {"status": "unknown_metric", "details": metric}


class Ledger:
    """Living falsification ledger. Failed predictions are preserved with failure modes.
    Deletion is not supported; entries are append-only in this in-memory reference impl.
    """

    def __init__(self, version: str = LEDGER_VERSION) -> None:
        self.version = version
        self._preds: Dict[str, Dict[str, Any]] = {}
        self._outcomes: List[Dict[str, Any]] = []

    def register_prediction(self, pred: SealedPrediction) -> None:
        if pred.pid in self._preds:
            raise KeyError(f"Duplicate pid: {pred.pid}")
        self._preds[pred.pid] = pred.as_dict()

    def record_outcome(self, pid: str, observed: List[float] | np.ndarray, result: Dict[str, Any],
                       failure_mode: Optional[str] = None, arbitration: Optional[ArbitrationRecord] = None) -> None:
        if pid not in self._preds:
            raise KeyError(f"Unknown pid: {pid}")
        pred = self._preds[pid]
        # External arbitration separation: arbitrator must differ from author
        if arbitration and arbitration.arbitrator_id == pred["author_id"]:
            raise RuntimeError("Arbitrator must be external to author/predictor.")
        entry = {
            "pid": pid,
            "observed": np.asarray(observed).tolist(),
            "result": result,
            "failure_mode": failure_mode if result.get("status") == "failed" else None,
            "arbitration": vars(arbitration) if arbitration else None,
            "timestamp": time.time(),
        }
        self._outcomes.append(entry)

    def summary(self) -> Dict[str, Any]:
        passed = sum(1 for e in self._outcomes if e["result"].get("status") == "passed")
        failed = sum(1 for e in self._outcomes if e["result"].get("status") == "failed")
        return {
            "version": self.version,
            "counts": {"predictions": len(self._preds), "outcomes": len(self._outcomes), "passed": passed, "failed": failed},
        }

    def to_json(self) -> str:
        return json.dumps({"version": self.version, "predictions": self._preds, "outcomes": self._outcomes}, indent=2)


if __name__ == "__main__":
    # Self-test demonstrating the governance flow
    print("RCE Versjon self-test (governance machinery)\n")

    # Define regimes and coupling
    m0 = Regime(tag="M0", level=0, domain="medicine", description="Molecular")
    m1 = Regime(tag="M1", level=1, domain="medicine", description="Cellular/Tissue")
    coupling = CouplingMap()
    coupling.allow(m0.tag, m1.tag, operator="upscale_binding")

    # Frozen shared parameters
    fp = FrozenParamStore({"kappa": 2.0, "beta": 0.4})
    fp.lock()

    # Build and seal a prediction in regime M1, sourced from M0 (allowed by coupling)
    predicted = [1.0, 1.0, 1.0]
    spec = {
        "predicted": predicted,
        "metric": "mae",
        "thresholds": {"mae_max": 0.1},
        "source_regimes": [m0.tag],
    }
    p = SealedPrediction(
        pid="P-MED-001",
        regime=m1.tag,
        frozen_params_hash=fp.snapshot_hash(),
        spec=spec,
        author_id="team.symbiose",
        deposit_doi="10.6084/m9.figshare.32256951",
    )
    p.seal()

    ledger = Ledger()
    ledger.register_prediction(p)

    # Evaluate with observed data (intentionally failing mae threshold)
    observed = [1.0, 1.3, 0.7]
    result = evaluate(p, observed, fp, coupling)
    arb = ArbitrationRecord(arbitrator_id="arb.external.lab", outcome="confirm", reference_uri="https://arbiter.example/decisions/abc")
    ledger.record_outcome(p.pid, observed, result, failure_mode="mae_above_threshold", arbitration=arb)

    print("Ledger summary:", ledger.summary())
    print("\nLedger JSON:\n", ledger.to_json())
