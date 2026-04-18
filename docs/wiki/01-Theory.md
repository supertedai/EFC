# 01 · Theory

> Axioms, field equations, regimes, formal specification.
> Read this if you want the mathematical backbone of EFC.

[🏠 Home](./Home.md) · [→ Evidence](./02-Evidence.md) · [→ Glossary](./06-Glossary.md)

---

## Start with the canonical reference

The **White Paper Series (Parts 1–4)** is the authoritative four-part theory document:

| Part | Topic | DOI |
|---|---|---|
| 1 | Recovery conditions (EFC ⊃ ΛCDM) | [figshare.31970886](https://doi.org/10.6084/m9.figshare.31970886) |
| 2 | Field equations & observable mapping | [figshare.31970898](https://doi.org/10.6084/m9.figshare.31970898) |
| 3 | Validation ledger & falsification protocol | [figshare.31970904](https://doi.org/10.6084/m9.figshare.31970904) |
| 4 | Regime susceptibility T(S) & dynamical dark energy | [figshare.31970907](https://doi.org/10.6084/m9.figshare.31970907) |

Rendered overview: [`EFC_White_Paper_Series.html`](../public/EFC_White_Paper_Series.html) · Source folder: [`docs/papers/efc/efc_white_paper_part_1_to_4/`](../papers/efc/efc_white_paper_part_1_to_4/)

---

## Core axiom and key equations

```
Axiom: Energy flows along entropy gradients.
```

| Name | Equation | Role |
|---|---|---|
| Effective coupling | μ(a) = 1 + β·S(a) | Background response |
| Response surface | μ(k, S) = 1 + R(k, S) | Perturbation sector |
| Field equation | G_μν = 8πG(T_μν + T^(Ef)_μν) + Λ_eff g_μν | Full theory |
| Screening model | ln(μ) = k·ln(1 + g†/g_bar), k = 0.415, g† = 2.51×10⁻¹⁰ | SPARC fit |
| Gradient flow | dF/dt = −∫\|∇ṡ\|² dV + B | Lyapunov for all regimes |

Empirical best-fit constants (2026):
- β = 0.16 (unified BAO/SN/RSD)
- R(k≈0.13, S≈0.30) ≈ +0.30 (WP3)
- k = 0.415 ± 0.029 (174 SPARC galaxies)
- Cross-scale C = k/a_G = 4.4

---

## Regimes (L0–L3)

EFC organises physical predictions by where you are in the entropy–density landscape:

| Regime | Domain | ΛCDM match |
|---|---|---|
| **L0** | High-density, low-entropy (solar system, inner galaxy) | Exact Einstein gravity |
| **L1** | Galactic outskirts | Screened transition |
| **L2** | Cluster scales, perturbations | Modified μ, Σ, η |
| **L3** | Cosmological background, voids | Full entropic response |

ΛCDM is recovered as the **L0/L1 limit** of EFC (Eq. 6: K(ρ)→∞, T(a)→0, ξ≫1). See [ΛCDM as Special Case of EFC](https://doi.org/10.6084/m9.figshare.31943361).

---

## Regime-Consistent Measurement Principle (RCMP)

Cross-regime measurements must use rulers matched to the regime being measured. Violating RCMP (V1/V2/V3) produces apparent nulls that are **measurement failures, not physics failures** — see [KT3b cross-regime measurement failure](https://doi.org/10.6084/m9.figshare.31963821).

Three valid replacement architectures are proposed in that note.

---

## Formal specification

Machine-readable theory objects live in [`/theory/`](../../theory/):

- [`theory/formal/efc_formal_spec.tex`](../../theory/formal/efc_formal_spec.tex) — LaTeX formal spec
- [`theory/formal/efc_master.tex`](../../theory/formal/efc_master.tex) — master document
- [`theory/formal/index.jsonld`](../../theory/formal/index.jsonld) — JSON-LD model ontology
- [`theory/formal/efc-r-model/`](../../theory/formal/efc-r-model/), `efc-s-model/`, `efc-d-model/`, `efc-c0-model/`, `efc-h-model/` — sub-model definitions
- [`theory/EFC_R_FRAGMENT_TOPOLOGY_MAPPING.md`](../../theory/EFC_R_FRAGMENT_TOPOLOGY_MAPPING.md)

---

## Tier-1 theory papers

The highest-tier theory documents (T1) are pulled from the full 150-paper corpus. See the auto-generated list in [Papers by topic → Theory (T1)](./03-Papers-by-Topic.md#theory).

Quick links to T1 theory anchors:

- [Energy-Flow Cosmology: An Effective Phenomenological Law for Gravitation](https://doi.org/10.6084/m9.figshare.30563738)
- [Regime Structure and Entropic Flow Ontology in Discrete Gravity Models](https://doi.org/10.6084/m9.figshare.31348417)
- [Homo Fluxus v2.0 — Civilization Map through EFC](https://doi.org/10.6084/m9.figshare.31940604)

---

## Next

- **Want to see if it holds up?** → [02 · Evidence](./02-Evidence.md)
- **Want the vocabulary?** → [06 · Glossary](./06-Glossary.md)
- **Want to run the theory end-to-end?** → [04 · Reproduce](./04-Reproduce.md)
