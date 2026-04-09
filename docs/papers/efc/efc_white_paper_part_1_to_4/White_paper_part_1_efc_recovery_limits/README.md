# EFC White Paper Part 1: Recovery Conditions and the LCDM Limit

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)) · Symbiose Research, Sandnes, Norway
**DOI:** [10.6084/m9.figshare.31970886](https://doi.org/10.6084/m9.figshare.31970886)
**License:** CC-BY-4.0 · **Track:** EFC White Paper Series · **Regimes:** L0, L1, L2
**Series:** EFC White Paper (Part 1 of 4)

---

## TL;DR

| Question | Answer |
|---|---|
| What is established? | EFC contains LCDM as a limiting case in the perturbation sector |
| How many recovery conditions? | Three independent sufficient conditions |
| Condition I | Parameter limit: alpha_L2 -> 0 implies mu = Sigma = 1 |
| Condition II | Low-entropy regime: S < S_c ~ 0.1 implies GR recovered |
| Condition III | Density saturation: rho >> rho_crit implies Theta(rho) -> 0, G_eff -> G_N |
| Mutual consistency | All three yield the same limit without cross-terms (Proposition 1) |
| What remains open? | Full background H(z) recovery — stated as explicit open problem |
| Level classification | Level 2 established (perturbation sector); Level 3 open |

## Core Equations

### Regime-transition function (Eq. 2)
```
Theta(z) = (1/2)[1 + tanh((z_L1L2 - z) / Delta_z)]
```

### Modified gravitational parameters (Eqs. 3-4)
```
mu(k,z) = G_eff(k,z) / G_N = 1 - B * g(a; n)
Sigma(k,z) = G_lens(k,z) / G_N = mu_lens(k,z)
```

### EFC kernel (Eq. 5)
```
mu_EFC(k,z) = (1 - S_bar(z)) + s_tilde(k,z) / delta_tilde(k,z)
```

### Triangulated recovery (Proposition 1, Eq. 10)
```
[alpha_L2 -> 0] OR [S < S_c] OR [rho >> rho_crit]
    ==> mu(k,z) -> 1,  Sigma(k,z) -> 1
```

## Key Results

- **Theorem 1 (Parameter recovery):** alpha_L2 = 0 recovers standard Friedmann equation; G_eff = G_N at every scale
- **Theorem 2 (Entropy recovery):** S < S_c ~ 0.1 implies all EFC corrections vanish; L0/L1 regime is GR
- **Theorem 3 (Density recovery):** Theta(rho) screening suppresses EFC in high-density environments (Solar System, stellar interiors)
- **Corollary 1:** EFC contains LCDM as a limiting case in the perturbation sector (EFC superset_pert LCDM)
- **Observational constraint:** alpha_L2 = -1.00 +/- 0.46 at 2.20 sigma with Delta_AIC = -2.91

## Kill Conditions

If any of the following hold, this paper's claims are falsified:
- EFC corrections persist when alpha_L2 = 0 (violates Theorem 1)
- mu or Sigma deviate from 1 in L0/L1 regime where S < S_c (violates Theorem 2)
- Solar System PPN constraints violated — EFC correction > 10^-5 (violates Theorem 3)
- Cross-terms between the three recovery channels produce residual corrections (violates Proposition 1)

## Files

| File | Description |
|---|---|
| `index.json` | Machine-readable structured metadata |
| `metadata.json` | Extended metadata with theorems and tables |
| `schema.json` | JSON Schema for recovery condition objects |
| `white-paper-part-1-recovery-limits.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `data/recovery_conditions.json` | Table 1: Recovery conditions status summary |
| `data/level_classification.json` | Table 2: EFC superset LCDM level classification |
| `src/recovery_limits.py` | Implementation of recovery conditions and EFC kernel |
| `examples/check_recovery.py` | Demo: verify recovery limits numerically |

## Provenance

This is the first paper in the canonical EFC White Paper series.
Companion papers: [Part 2](../White_paper_part_2_efc_field_equations_observables/),
[Part 3](../White_paper_part_3_efc_validation_falsification/),
[Part 4](../White_paper_part_4_efc_regime_susceptibility/).
