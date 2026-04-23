# EFC Model Comparison Ledger

> **Purpose**: Run EFC against competing models on identical data + identical
> likelihood + identical priors. Anything else is apples-to-oranges.

---

## 1. Comparison protocol

A valid comparison requires:

1. **Same dataset** (same DOI, same data version)
2. **Same likelihood code** (same entry in `likelihood-ledger`)
3. **Same nuisance parameters and priors**
4. **Different theoretical model** (the only varying axis)

Any deviation must be flagged in the comparison entry's `caveats` field.

---

## 2. Reported quantities

Per comparison row:

| Quantity | Required |
|----------|----------|
| `chi2` per model | yes |
| `Δχ²` (model − reference) | yes |
| `AIC`, `BIC` per model | yes |
| `ΔAIC`, `ΔBIC` | yes |
| `ln Z` (Bayesian evidence) per model | when nested sampling available |
| `ln K = ln Z_A − ln Z_B` | when both `ln Z` available |
| `n_params` per model | yes |
| Reference model | declared |

`ΔAIC` and `ln K` interpretation follows Jeffreys' scale — recorded
verbatim in `interpretation` field, never paraphrased.

---

## 3. Model registry (initial)

Stored in `data/models.json`:

| model_id | Description | n_free_params (cosmo) | Status |
|----------|-------------|------------------------|--------|
| `lcdm`           | Standard ΛCDM (reference) | 6 | registered |
| `efc_v3`         | EFC current frozen version | TBD | registered |
| `horndeski_min`  | Minimal Horndeski (αB, αM free) | 8 | placeholder |
| `f_of_r_hu_sawicki` | f(R) Hu-Sawicki | 7 | placeholder |
| `dgp_normal`     | DGP normal branch | 6 | placeholder |
| `wcdm`           | wCDM (constant w) | 7 | placeholder |

Each model entry MUST declare its likelihood-compatible code path
(e.g. MGCAMB module name, or analytic fσ8 implementation).

---

## 4. Comparison entry template

```json
{
  "comparison_id": "fsigma8_2026__efc_vs_lcdm",
  "likelihood_id": "s8_growth_fsigma8_2026",
  "models": [
    {"model_id": "efc_v3",  "chi2": null, "aic": null, "bic": null, "ln_z": null, "n_params": null},
    {"model_id": "lcdm",    "chi2": null, "aic": null, "bic": null, "ln_z": null, "n_params": 6}
  ],
  "reference_model": "lcdm",
  "delta_chi2": null,
  "delta_aic":  null,
  "ln_k":       null,
  "interpretation": "PENDING",
  "caveats": [],
  "status": "declared"
}
```

---

## 5. Falsification interaction

Model comparison results feed `evaluation-ledger/data/evaluation.json["current_state"]["model_preference"]`,
NOT `falsification_status`. (See evaluation-ledger §4.) A comparison
showing `prefers_lcdm` does not falsify EFC; it lowers preference.

---

## 6. Open questions

1. Are external/competing models run inside this repo, or imported via DOI
   from external papers?
2. For Horndeski / f(R), do we use MGCAMB defaults or repo-pinned configs?
3. Should comparisons against scalar-tensor MG include screening regimes
   separately?

---

## Status

**DRAFT — 2026-04-23.** Skeleton awaiting maintainer review.
Last updated: 2026-04-23.
