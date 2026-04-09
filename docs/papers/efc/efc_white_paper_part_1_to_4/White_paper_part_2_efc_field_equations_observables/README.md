# EFC White Paper Part 2: Field Equations and Observable Mapping

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)) · Symbiose Research, Sandnes, Norway
**DOI:** [10.6084/m9.figshare.31970898](https://doi.org/10.6084/m9.figshare.31970898)
**License:** CC-BY-4.0 · **Track:** EFC White Paper Series · **Regimes:** L0, L1, L2
**Series:** EFC White Paper (Part 2 of 4)

---

## TL;DR

| Question | Answer |
|---|---|
| What does this paper do? | Derives field equations from entropy-gradient principle and maps to observables |
| Central scalar field | S(a) — dimensionless entropy field, S in [0,1] |
| Coupling formula | mu(a) = 1 + beta * S(a), with beta ~ 0.16 from SPARC |
| EFC kernel | mu_EFC(k,z) = (1 - S_bar(z)) + s_tilde(k,z)/delta_tilde(k,z) |
| Growth rate prediction | f*sigma_8(z=0.7) = 0.430 vs LCDM 0.449 (sealed, 2.0 sigma) |
| S_8 suppression | Delta_sigma_8 proportional to (1 - mu_0) integral g(a;n) d ln a |
| Gravitational slip | eta = Psi/Phi != 1 required (Sigma != mu in L2) |
| Response surface | R(k,S) maps wavenumber and entropy to G_eff/G_N |
| Key signal | alpha_L2 = -1.00 +/- 0.46 (2.20 sigma, Delta_AIC = -2.91) |

## Structural Hierarchy

1. Entropy field S(a) — **fundamental**
2. Coupling formula mu(a) = 1 + beta*S(a) — **derived**
3. Growth equation with mu(a) — **dynamical**
4. f*sigma_8, S_8, Sigma observables — **empirical**
5. R(k,S) response surface — **unifying**

## Observable Mapping (Table 1)

| Observable | Equation | Dataset | Result | Status |
|---|---|---|---|---|
| alpha_L2 (background) | (7) | CMB+BAO | COLLAPSED | Failed |
| alpha_L2 (growth) | (9) | DESI+BOSS | -1.00 +/- 0.46 (2.20 sigma) | Pass |
| f*sigma_8(z=0.7) | (9) | RSD | 0.430 vs 0.449 (2.0 sigma) | Sealed |
| f*sigma_8 LOO | (9) | RSD | 7/7 folds | Pass |
| S_8 (DES Y6) | (11) | DES | 0.3 sigma (pre-reg.) | Pass |
| BAO transfer | (7) | DESI->BOSS | No refit needed | Pass |
| Lensing (KiDS) | (13) | KiDS-1000 | Regime-activated fit improved | Pass |
| mu < 1 sign | (2) | Multi-probe | B > 0 required | Pass |
| Pure mu < 1 excl. | (13) | Structure | Slip required (Sigma != mu) | T3 |
| Solar system (PPN) | (1) | KT1 | GR recovered (< 10^-5) | Pass |
| w(a) = -beta(S)*a | (13) | Euclid | Candidate: w_0 ~ -1 | Planned |

## Files

| File | Description |
|---|---|
| `index.json` | Machine-readable structured metadata |
| `metadata.json` | Extended metadata with equations and validation table |
| `schema.json` | JSON Schema for observable mapping objects |
| `white-paper-part-2-field-equations.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `data/observable_mapping.json` | Table 1: equation-data correspondence |
| `data/planned_tests.json` | Table 2: open observational tests |
| `src/field_equations.py` | Implementation of coupling, growth, and observables |
| `examples/compute_observables.py` | Demo: compute mu, f*sigma_8, S_8 suppression |

## Provenance

Second paper in the canonical EFC White Paper series.
Companion papers: [Part 1](../White_paper_part_1_efc_recovery_limits/),
[Part 3](../White_paper_part_3_efc_validation_falsification/),
[Part 4](../White_paper_part_4_efc_regime_susceptibility/).
