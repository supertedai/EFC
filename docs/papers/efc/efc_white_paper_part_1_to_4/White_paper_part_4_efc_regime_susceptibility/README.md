# EFC White Paper Part 4: Regime Susceptibility and Cross-Scale Mapping

**Author:** Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)) · Symbiose Research, Sandnes, Norway
**DOI:** [10.6084/m9.figshare.31970907](https://doi.org/10.6084/m9.figshare.31970907)
**License:** CC-BY-4.0 · **Track:** EFC White Paper Series · **Regimes:** L0, L1, L2
**Series:** EFC White Paper (Part 4 of 4)

---

## TL;DR

| Question | Answer |
|---|---|
| What does this paper do? | Proposes regime susceptibility function T(S) connecting galactic and cosmological scales |
| Core concept | Dark matter and dark energy are phases of a single entropic continuum, not substances |
| Susceptibility function | T(S) = S_0(1-S_0) / [S(1-S)] |
| Self-regulation | beta(S) * rho_eff(S) = const (Proposition 1) |
| Effective energy density | rho_eff(S) = S(1-S) — Bernoulli variance form |
| Equation of state | w(a) = -beta(S) * a — dynamical dark energy prediction |
| Amplification ratio | beta_cosm/beta_gal ~ 6.25 — measurable, parameter-free |
| Kill criterion | KC5: w_0 = -1 to within 2% at Euclid precision falsifies this paper |
| Thermodynamic boundaries | S -> 0 (singularity, GR) and S -> 1 (Altular limit, de Sitter) |

## Core Equations

### Energy-flow current divergence (Eq. 1)
```
div(J^mu) < 0  =>  convergent flow  =>  excess gravity (DM regime)
div(J^mu) = 0  =>  equilibrium      =>  matter-dominated epoch
div(J^mu) > 0  =>  divergent flow   =>  accelerated expansion (DE regime)
```

### Effective energy density (Eq. 3)
```
rho_eff(S) = S(1 - S)
```

### Regime susceptibility function (Eq. 6)
```
T(S) = S_0(1 - S_0) / [S(1 - S)]
```

### Self-regulation (Proposition 1, Eq. 8)
```
beta(S) * rho_eff(S) = beta_0 * S_0(1 - S_0) = const
```

### Equation of state (Eq. 5)
```
w(a) = p_eff / rho_eff = -beta(S) * a
```

## Physical Interpretation

- **T(S)** is the inverse of the system's dynamical capacity
- Near thermodynamic boundaries (S -> 0 or S -> 1), T diverges: system is "stiff"
- At midpoint S = 0.5, T is minimised: system is maximally flexible
- This mirrors the susceptibility of a physical system near a critical point
- The "order parameter" is the entropic distance from either boundary: 1/T(S) = S(1-S)

## Key Results

- **rho_eff = S(1-S):** Uniquely motivated Bernoulli form; vanishes at both boundaries, peaks at S = 0.5
- **T(S) self-regulation:** Although T -> infinity at boundaries, beta * rho_eff remains constant throughout
- **w(a) = -beta(S) * a:** Dynamical dark energy with no parameter recycling; w_0 = -beta_cosm determined from two independent calibrations
- **beta_cosm/beta_gal ~ 6.25:** Cross-scale amplification ratio is a measurable, parameter-free prediction
- **Dark matter/energy reinterpretation:** Convergent and divergent phases of a single entropic flow

## Files

| File | Description |
|---|---|
| `index.json` | Machine-readable structured metadata |
| `metadata.json` | Extended metadata with equations and physical interpretation |
| `schema.json` | JSON Schema for susceptibility objects |
| `white-paper-part-4-susceptibility.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `data/entropic_continuum.json` | Energy-flow phases and thermodynamic boundaries |
| `data/susceptibility_properties.json` | T(S) properties and self-regulation proof |
| `src/regime_susceptibility.py` | Implementation of T(S), rho_eff, w(a), and amplification |
| `examples/compute_susceptibility.py` | Demo: T(S) profile, equation of state, amplification ratio |

## Provenance

Fourth and final paper in the canonical EFC White Paper series.
Companion papers: [Part 1](../White_paper_part_1_efc_recovery_limits/),
[Part 2](../White_paper_part_2_efc_field_equations_observables/),
[Part 3](../White_paper_part_3_efc_validation_falsification/).
