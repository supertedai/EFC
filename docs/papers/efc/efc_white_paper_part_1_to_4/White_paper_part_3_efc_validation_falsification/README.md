# EFC White Paper Part 3: Data, Validation Ledger, and Falsification Protocol

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)) · Symbiose Research, Sandnes, Norway
**DOI:** [10.6084/m9.figshare.31970904](https://doi.org/10.6084/m9.figshare.31970904)
**License:** CC-BY-4.0 · **Track:** EFC White Paper Series · **Regimes:** L0, L1, L2
**Series:** EFC White Paper (Part 3 of 4)

---

## TL;DR

| Question | Answer |
|---|---|
| What is this paper? | Complete validation record + falsification protocol for Stage-IV surveys |
| Registered tests | 102 total |
| Passed | 66 |
| Failed | 17 |
| Falsified (with successor) | 5 |
| Sealed predictions | 2 (cryptographic hashes, pre-data) |
| Kill criteria | 5 sharp conditions under which EFC must be abandoned |
| Confirmation thresholds | 4 levels from 2.20 sigma hint to 5 sigma detection |

## Sealed Blind Predictions

### Prediction 1 (Freeze v1, 2026-02-18)
- alpha_L2 = -0.689
- f*sigma_8(z=2.042) crossover
- D_H/r_d(z=1.0): EFC = 16.527 vs LCDM = 17.466 (3.1 sigma deviation)
- D_H/r_d(z=0.7): EFC = 19.797 vs LCDM = 20.719 (2.3 sigma)
- f*sigma_8(z=0.7): EFC = 0.430 vs LCDM = 0.449 (2.0 sigma)
- Hash: `7a850cfa58477701...`

### Prediction 2 (Freeze v2, 2026-02-21)
- alpha_L2 = -0.702
- Hash: `dbccda150abca0e7...`

## Kill Criteria (Stage-IV)

1. **Growth suppression absent:** |alpha_L2| < 0.1 at 3 sigma => EFC falsified (growth sector)
2. **Wrong f*sigma_8 trajectory:** |z_cross_obs - 2.042| > 3 sigma => crossover prediction falsified
3. **S_8 converges to LCDM:** S_8 = S_{8,LCDM} +/- 0.005 at Stage-IV precision => S_8 channel falsified
4. **No gravitational slip:** |eta - 1| < 0.01 at Euclid precision => slip prediction falsified
5. **No dynamical dark energy:** |w_0 + 1| < 0.02 at Euclid precision => dynamical DE prediction falsified

## Confirmation Roadmap

| Level | Threshold | Channel | Survey | Timeline |
|---|---|---|---|---|
| Hint (current) | 2.20 sigma | f*sigma_8 LOO | DESI+BOSS | 2026 |
| Suggestive | 3 sigma joint | f*sigma_8 + S_8 | +DES+KiDS | 2027 |
| Evidence | 3.5 sigma | mu-Sigma + f*sigma_8 | +Euclid Y1 | 2028 |
| Detection | 5 sigma | All channels locked | Euclid+Rubin | 2030+ |

## Files

| File | Description |
|---|---|
| `index.json` | Machine-readable structured metadata |
| `metadata.json` | Extended metadata with ledger summary and kill criteria |
| `schema.json` | JSON Schema for validation test objects |
| `white-paper-part-3-validation.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `data/validation_ledger.json` | Full 102-test validation record |
| `data/kill_criteria.json` | 5 kill criteria with thresholds |
| `data/confirmation_roadmap.json` | 4-level confirmation roadmap |
| `src/validation_checker.py` | Implementation of status classification and kill checks |
| `examples/ledger_summary.py` | Demo: print ledger statistics and kill-test status |

## Provenance

Third paper in the canonical EFC White Paper series.
Companion papers: [Part 1](../White_paper_part_1_efc_recovery_limits/),
[Part 2](../White_paper_part_2_efc_field_equations_observables/),
[Part 4](../White_paper_part_4_efc_regime_susceptibility/).
