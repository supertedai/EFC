import json
import numpy as np
from rce_versjon import (
    Regime, CouplingMap, FrozenParamStore, SealedPrediction,
    evaluate, Ledger, ArbitrationRecord,
    LEDGER_VERSION, EFC_COUNTS, REGIME_ARCH_EXAMPLES,
)


def main() -> None:
    print("Demo: RCE Versjon governance flow (DOI: 10.6084/m9.figshare.32256951)")
    print(f"Ledger version: {LEDGER_VERSION}; EFC counts: {EFC_COUNTS}")
    print(f"Example regimes (medicine): {REGIME_ARCH_EXAMPLES['medicine']}")

    # 1) Define regimes and an allowed coupling
    m0 = Regime(tag="M0", level=0, domain="medicine", description="Molecular")
    m1 = Regime(tag="M1", level=1, domain="medicine", description="Cell/Tissue")
    couplings = CouplingMap()
    couplings.allow(m0.tag, m1.tag, operator="upscale_binding")

    # 2) Create frozen parameters and lock them
    fp = FrozenParamStore({"kappa": 2.0, "beta": 0.4})
    fp.lock()

    # 3) Pre-register and seal a prediction
    predicted = [1.0, 1.0, 1.0]
    spec = {
        "predicted": predicted,
        "metric": "mae",
        "thresholds": {"mae_max": 0.1},
        "source_regimes": [m0.tag],
    }
    pred = SealedPrediction(
        pid="P-MED-DEMO-001",
        regime=m1.tag,
        frozen_params_hash=fp.snapshot_hash(),
        spec=spec,
        author_id="demo.author",
        deposit_doi="10.6084/m9.figshare.32256951",
    )
    pred.seal()

    # 4) Evaluate against observed data
    observed = np.array([1.0, 1.3, 0.7])
    result = evaluate(pred, observed, fp, couplings)

    # 5) Record in ledger with external arbitration note
    ledger = Ledger()
    ledger.register_prediction(pred)
    arb = ArbitrationRecord(arbitrator_id="independent.arbiter", outcome="confirm", reference_uri="https://arbiter.example/case/123")
    ledger.record_outcome(pred.pid, observed, result, failure_mode=(None if result.get("status")=="passed" else "mae_above_threshold"), arbitration=arb)

    print("Result:", result)
    print("Ledger summary:", ledger.summary())
    print("Ledger JSON snippet:")
    print(json.dumps(json.loads(ledger.to_json()), indent=2)[:600] + "...\n")

    # Optional plot if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        x = np.arange(len(predicted))
        plt.plot(x, predicted, "-o", label="predicted")
        plt.plot(x, observed, "-s", label="observed")
        plt.title("Prediction vs Observation (metric=MAE)")
        plt.xlabel("index"); plt.ylabel("value"); plt.legend(); plt.tight_layout()
        plt.show()
    except Exception as e:
        print("Plot skipped:", e)


if __name__ == "__main__":
    main()
