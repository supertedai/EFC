# 02 · Evidence

> The empirical case for (and constraints on) EFC.
> Validation Ledger, kill-tests, sealed predictions, falsification criteria.

[🏠 Home](./Home.md) · [← Theory](./01-Theory.md) · [→ Papers by topic](./03-Papers-by-Topic.md)

---

## The single source of truth

All validated results live in the **Validation Ledger**:

- **Rendered:** [`EFC_Validation_Ledger.html`](../public/EFC_Validation_Ledger.html) (v3.20 public / v4.8 internal)
- **Machine-readable:** [`docs/validation-ledger/data/evidence-register.json`](../validation-ledger/data/evidence-register.json) and [`data/ledger.json`](../validation-ledger/data/ledger.json)

> **Evidence-layer discipline** (enforced by `efc_verify.py`, CI will reject violations):
> 1. EFC publications (own Figshare DOI) → evidence-register + ledger
> 2. Third-party arXiv publications → only in `§4b`, tagged `[external — …]`
> 3. EFC working notes confronting externals → own DOI + own VAL report ID

---

## Current verdict

**Stage: Non-rejectable model.** Across **103+ independent tests**, EFC has not been ruled out. It does not yet outperform ΛCDM — margins are too small to call a winner — but survives every test.

Global verdict: **OPEN**.

---

## Kill-tests and falsification

Five pre-registered kill criteria define what would falsify EFC:

- See `§5` of [`EFC_Validation_Ledger.html`](../public/EFC_Validation_Ledger.html)
- Complete protocol: [White Paper Part 3](https://doi.org/10.6084/m9.figshare.31970904)

Most recent kill-test results:

| Test | DOI | Outcome |
|---|---|---|
| Complete Kill-Test v6 (six-probe L0→L3) | [31964847](https://doi.org/10.6084/m9.figshare.31964847) | All 4 cobaya runs: Δχ² ≤ 0 |
| Kill-Test v6 Universality on SPARC 175 | [31986762](https://doi.org/10.6084/m9.figshare.31986762) | EFC win rate 60.2% |
| KT3b Cross-Regime Measurement Failure | [31963821](https://doi.org/10.6084/m9.figshare.31963821) | Null diagnosed as RCMP violation |
| Bullet Cluster Confrontation | [31963668](https://doi.org/10.6084/m9.figshare.31963668) | PIEMD A_sig baseline null |

Full list: [Papers by topic → Empirical tests](./03-Papers-by-Topic.md#empirical_test).

---

## Sealed predictions (pre-registered)

**Discipline:** every prediction must cite the **prior** EFC DOI where it was first stated, in the same sentence, to prevent post-diction.

Headline sealed predictions:

| Target survey | Prediction | DOI | Resolves |
|---|---|---|---|
| Euclid DR1 (Oct 2026) | Boltzmann-calibrated σ₈/P(k)/lensing/E_G band | [31990053](https://doi.org/10.6084/m9.figshare.31990053) | Oct 2026 |
| Growth rate fσ₈ | Sealed blind predictions | [32013156](https://doi.org/10.6084/m9.figshare.32013156) | ongoing |
| SO × Euclid E_G | Cross-correlation band | [32023788](https://doi.org/10.6084/m9.figshare.32023788) | 2027+ |
| Deep-void ISW sign-flip | Density-dependent coupling | [31942677](https://doi.org/10.6084/m9.figshare.31942677) | Stage-IV |

Full list: [Papers by topic → Sealed predictions](./03-Papers-by-Topic.md#sealed_prediction).

Roadmap: [`EFC_Stage-IV_Data_Roadmap.html`](../public/EFC_Stage-IV_Data_Roadmap.html).

---

## Channel-by-channel snapshot

| Channel | Sample | Result |
|---|---|---|
| Galaxy rotation curves | SPARC 175 | k = 0.415 ± 0.029; win rate 60.2% (AIC) |
| Background expansion | DESI DR2 | α = −0.14 ± 0.21 (0.65σ from null) |
| Cosmic shear | KiDS-1000 | Improved fit, regime-activated lensing response |
| BAO transfer | BOSS DR12 | Δχ² = −7.77, k_eff = 0 |
| Growth rate | fσ₈ multi-epoch | Null consistent, B = 0 within 1σ |
| Cluster lensing | Bullet | PIEMD A_sig baseline null; δκ test pending |
| Survey scaling | DES Y6 P3 | 0.944 ± 0.018 (vs 0.95 ± 0.03 pred) |

---

## Gap analysis and open questions

- [`EFC_Gap_Analysis.html`](../public/EFC_Gap_Analysis.html) — what's still missing, by section
- [`EFC_Predictions.html`](../public/EFC_Predictions.html) — live list of active predictions
- [`EFC_Changelog.html`](../public/EFC_Changelog.html) — version history

---

## Language discipline (for citers)

External observations are **`consistent with`** / **`overlaps with`** / **`within EFC prediction band`** — never **`confirms EFC`**. Violating this is treated as claim inflation.

---

## Next

- **Need the raw papers?** → [03 · Papers by topic](./03-Papers-by-Topic.md)
- **Want to rerun the tests?** → [04 · Reproduce](./04-Reproduce.md)
