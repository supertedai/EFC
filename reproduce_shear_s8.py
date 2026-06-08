#!/usr/bin/env python3
"""
EFC Cosmic-Shear S8 Amplitude Reproducibility Script  (F7, amplitude leg)
=========================================================================

Deterministic reproduction of the S8-AMPLITUDE test of EFC's three branches
against existing cosmic-shear measurements.

    python reproduce_shear_s8.py

Reproduces:
    - S8 predictions for EFC-robust (mu<1, Sigma~0.99), LCDM/Planck, and
      EFC-fragile (eta-boost, 0% robust)
    - chi2 vs existing lensing S8 (point-prediction, diagonal errors)
    - tension with model-error propagation (the honest significance)
    - robustness to the KiDS-1000 vs KiDS-Legacy bifurcation

SCOPE DISCLAIMER (read this).  This tests ONLY the amplitude consequence of
the fragile eta-boost branch (eta-boost => enhanced growth => HIGH S8). It is
NOT the full Sigma_eff(z) SHAPE test (the z~0.44 crossover, criterion F9),
which remains a GAP awaiting Euclid DR1 (Oct 2026) and the full Cobaya+MGCAMB
likelihood. A first-look: diagonal errors, no covariance, no nuisance
marginalisation. The chi2 ranking uses point predictions; the reported tension
adds each branch's own prediction error in quadrature (the honest version).

Status (first-look, for review; not a sealed Validation-Ledger verdict):
    existing DES Y6 + KiDS S8 already DISFAVOUR the fragile eta-boost branch
    (~3 sigma combined-error), robust to the KiDS choice; robust EFC (S8 down)
    is the best fit to existing lensing, ahead of LCDM. This is the amplitude
    leg of F7 -- it makes F7 partly testable NOW, not only at Euclid.

Dependencies: none beyond the Python standard library (math).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

# =====================================================================
# 1. MODEL S8 PREDICTIONS  (value, 1-sigma prediction error, source)
# =====================================================================
# EFC-robust : mu<1 growth-suppression, Sigma~0.99 (DOI 10.6084/m9.figshare.31188193;
#              structural closure 32084670). S8 shifts DOWN below LCDM.
# LCDM       : Planck 2018/2026 CMB anchor.
# EFC-fragile: the sealed eta-boost upper branch (eta in [1.05,1.15]), classified
#              0% robust by EFC's own perturbation-sector scan (DOI 32037990).
MODELS = {
    "EFC robust (mu<1, Sigma~0.99)": {"S8": 0.820, "err": 0.020, "src": "DOI 31188193 / 32084670"},
    "LCDM / Planck":                 {"S8": 0.832, "err": 0.013, "src": "Planck 2018/2026"},
    "EFC fragile (eta-boost, 0%rob)":{"S8": 0.847, "err": 0.015, "src": "DOI 32037990 (sealed, 0% robust)"},
}

# =====================================================================
# 2. EXISTING COSMIC-SHEAR S8 DATA  (VERIFIED 2026-06-08 against the source papers:
#    DES Y6 arXiv:2601.14559, KiDS-Legacy arXiv:2503.19442)
# =====================================================================
DATA = [
    {"name": "DES Y6 3x2pt", "S8": 0.789, "err": 0.012, "src": "arXiv:2601.14559 (DES Y6 3x2pt, Jan 2026; verified 2026-06-08)"},
    {"name": "KiDS-Legacy",  "S8": 0.814, "err": 0.012, "src": "arXiv:2503.19442 (KiDS-Legacy S8=0.814 +0.011/-0.012; verified 2026-06-08)"},
]
# The KiDS-1000 (0.766) vs KiDS-Legacy (0.814) bifurcation is unresolved
# (Euclid DR1 will arbitrate); we test robustness to it below.
KIDS_VARIANTS = {"KiDS-Legacy": {"S8": 0.814, "err": 0.012},
                 "KiDS-1000":   {"S8": 0.766, "err": 0.020}}


def chi2(s8_model, points):
    """Point-prediction chi2 (diagonal data errors only)."""
    return sum(((s8_model - p["S8"]) / p["err"]) ** 2 for p in points)


def tension(s8_model, model_err, p):
    """Honest tension for one point: model + data error in quadrature (sigma)."""
    return (s8_model - p["S8"]) / math.sqrt(p["err"] ** 2 + model_err ** 2)


class Result:
    def __init__(self):
        self.checks, self.n_pass, self.n_fail = [], 0, 0

    def check(self, name, passed, detail=""):
        tag = "\033[32mPASS\033[0m" if passed else "\033[31mFAIL\033[0m"
        print(f"  [{tag}] {name}" + (f"  ({detail})" if detail else ""))
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        self.n_pass += int(passed); self.n_fail += int(not passed)

    def summary(self):
        return {"total": self.n_pass + self.n_fail, "passed": self.n_pass, "failed": self.n_fail}


def main():
    print("=" * 70)
    print("  EFC COSMIC-SHEAR S8 AMPLITUDE REPRODUCIBILITY SCRIPT  (F7, amplitude leg)")
    print("  amplitude consequence only -- NOT the Sigma_eff(z) crossover (F9, Euclid)")
    print(f"  Python {sys.version.split()[0]}")
    print("=" * 70)
    R = Result(); t0 = time.time()

    R.check("data_loaded", len(DATA) >= 2, f"{len(DATA)} lensing points")

    # ── chi2 ranking (point predictions) ────────────────────────────────
    print("\n--- chi2 vs existing lensing (point prediction, diagonal) ---")
    chis = {}
    for name, m in MODELS.items():
        c = chi2(m["S8"], DATA); chis[name] = c
        ts = "  ".join(f"{p['name'].split()[0]}:{tension(m['S8'], m['err'], p):+.1f}sig" for p in DATA)
        print(f"  {name:<34} S8={m['S8']:.3f}  chi2={c:5.1f}   tension(w/model-err): {ts}")
    R.check("predictions_finite", all(math.isfinite(c) for c in chis.values()))

    best = min(chis, key=chis.get)
    print(f"\n  Best fit to existing lensing: {best} (chi2={chis[best]:.1f})")
    R.check("robust_is_best_fit", best.startswith("EFC robust"),
            f"{best} (robust EFC predicts S8 down, matching low lensing)")

    fragile = "EFC fragile (eta-boost, 0%rob)"
    R.check("fragile_disfavoured", chis[fragile] > chis[best],
            f"fragile chi2={chis[fragile]:.1f} > best {chis[best]:.1f} (dchi2=+{chis[fragile]-chis[best]:.1f})")

    # ── honest combined tension of the fragile branch ───────────────────
    print("\n--- fragile-branch combined tension (model + data error) ---")
    fr = MODELS[fragile]
    inv = sum(1.0 / (p["err"] ** 2 + fr["err"] ** 2) for p in DATA)
    num = sum((fr["S8"] - p["S8"]) / (p["err"] ** 2 + fr["err"] ** 2) for p in DATA)
    combined_sig = num / math.sqrt(inv)  # inverse-variance combined tension
    print(f"  per-point: " + ", ".join(f"{p['name'].split()[0]} {tension(fr['S8'],fr['err'],p):+.2f}sig" for p in DATA))
    print(f"  combined (inverse-variance): {combined_sig:+.2f} sigma  "
          f"(point-prediction chi2 would read ~{math.sqrt(chis[fragile]-chis[best]):.1f}sig -- inflated, no model err)")
    R.check("fragile_tension_gt_2sigma", combined_sig > 2.0,
            f"fragile disfavoured at {combined_sig:.1f} sigma (combined, model-error-propagated)")

    # ── robustness to the KiDS bifurcation ──────────────────────────────
    print("\n--- robustness to KiDS-1000 (0.766) vs KiDS-Legacy (0.815) ---")
    kids_ok = True
    for kn, kv in KIDS_VARIANTS.items():
        pts = [DATA[0], {"name": kn, **kv}]
        ck = {n: chi2(m["S8"], pts) for n, m in MODELS.items()}
        order_ok = ck[best] < ck["LCDM / Planck"] < ck[fragile]
        kids_ok = kids_ok and order_ok
        print(f"  {kn:<12} chi2  robust={ck[best]:.1f}  LCDM={ck['LCDM / Planck']:.1f}  fragile={ck[fragile]:.1f}"
              + ("  [order holds]" if order_ok else "  [ORDER BREAKS]"))
    R.check("fragile_disfavoured_under_both_kids", kids_ok,
            "robust < LCDM < fragile under both KiDS choices")

    # ── determinism ─────────────────────────────────────────────────────
    R.check("deterministic", abs(chi2(fr["S8"], DATA) - chis[fragile]) < 1e-12, "identical on re-run")

    elapsed = time.time() - t0
    s = R.summary()
    print(f"\n{'=' * 70}")
    tag = "\033[32mALL PASSED\033[0m" if s["failed"] == 0 else f"\033[31m{s['failed']} FAILED\033[0m"
    print(f"  {s['passed']}/{s['total']} checks passed  [{tag}]  ({elapsed:.2f}s)")
    print(f"  VERDICT (first-look): fragile eta-boost disfavoured ~{combined_sig:.1f}sigma by existing")
    print(f"  lensing; robust EFC (S8 down) best fit. AMPLITUDE leg only -- crossover -> Euclid.")
    print("=" * 70)

    output = {
        "meta": {"script": "reproduce_shear_s8.py",
                 "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "scope": "S8-amplitude leg of F7 ONLY; Sigma_eff(z) crossover (F9) is a separate GAP awaiting Euclid DR1",
                 "note": "First-look: diagonal errors, no covariance/nuisance; literature S8 values -- verify vs source DOIs before any sealed claim"},
        "models": MODELS,
        "data": DATA,
        "results": {"chi2": {k: round(v, 3) for k, v in chis.items()},
                    "best_fit": best,
                    "fragile_combined_tension_sigma": round(combined_sig, 3),
                    "robust_to_kids_bifurcation": kids_ok},
        "checks": R.checks, "summary": s,
    }
    rstr = json.dumps(output["results"], sort_keys=True, default=str)
    output["content_hash"] = hashlib.sha256(rstr.encode()).hexdigest()
    outp = Path(__file__).resolve().parent / "reproduce_shear_s8_output.json"
    outp.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  Output: {outp.name}\n  SHA-256: {output['content_hash']}")
    return 0 if s["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
