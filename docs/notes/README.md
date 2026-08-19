# EFC Research Notes and Specifications

**Repository**: Energy-Flow Cosmology (EFC)
**Author**: Morten Magnusson (ORCID 0009-0002-4860-5095), Symbiose Research, Sandnes, Norway
**License**: CC-BY-4.0

---

## Purpose

The `docs/notes/` directory contains internal research notes, technical
specifications, and design documents that record the evolving thinking behind
the Energy-Flow Cosmology programme. These files are working documents: they
capture design decisions, mathematical formulations, test criteria, and
diagnostic outcomes as the theory and its computational implementation develop.
Unlike the polished public-facing documents in `docs/public/`, notes here may
contain open questions, partial results, and provisional conclusions.

## Directory Structure

```
docs/notes/
├── EFC_Content_Source_Policy_v1.0.md  # Source/content policy for external news + research (2026-08-19)
├── EFC_native_v2_graph_spec.md   # v2 graph kernel specification
├── growth_bug_2026.md            # Growth ODE friction correction + reproducer audit (2026-04-19)
└── README.md                     # This file
```

## File Descriptions

### EFC_Content_Source_Policy_v1.0.md

**Full title**: EFC Content and Source Policy
**Status**: Proposed implementation contract (2026-08-19) — not yet enforced by CI

Governs any agent or workflow that proposes updates to `docs/public/` from
external news or research. Separates acquisition, editorial judgement,
proposal, and publication, and permits automation of only the first three.
Rather than introducing a new scanner, it governs the mechanism this
repository already has — `.claude/prompts/research_watch_delta.md` and
`docs/public/external_research_watch.json` — and records six known
disagreements between that pipeline and this policy. The most actionable: the
watchlist already carries `validates EFC`, a phrase on the forbidden list in
`scripts/maintenance/efc_verify.py`, but check C3 scans only the HTML ledger,
so the `efc_relevance` free-text fields go unenforced. The others include the
absence of an evidence tier and a content hash, and a status lifecycle in
which 71 of 106 items were still `new`. Binds the pipeline explicitly to the
three-layer evidence separation in
`AGENTS.md`: external literature belongs in §4b of the Validation Ledger,
never in the JSON evidence registers.

The document is partly reconstructed. An earlier Norwegian draft was lost
before it was committed; about a quarter survived verbatim. Rules are marked
*[recovered]* or *[new]* so that restored decisions are not confused with
fresh proposals.

### EFC_native_v2_graph_spec.md

**Full title**: EFC Native v2 Graph -- Specification
**Status**: Active development (dated 2026-02-16)

This is the central technical specification for the second-generation EFC graph
kernel. It defines the complete mathematical and computational framework for the
discrete AQUAL (AQUAdratic Lagrangian) formulation of gravity on a lattice
graph. The document covers the following topics in detail:

| Section | Content |
|---------|---------|
| Primitive Objects | Defines the five fundamental objects: the cubic-lattice graph (V, E), the entropy field S_i, density field rho_i, gravitational potential field Phi_i, and the global bulk entropy reservoir S_V. |
| Energy Functional | Specifies the four-term energy functional F[Phi] = F_grad + F_source + F_bulk + F_AQUAL, including the non-linear flux term that encodes the MOND interpolating function mu(x) = x / sqrt(1 + x^2). |
| Field Equation | Derives the discrete AQUAL equation from variation of the energy functional, yielding a non-linear Poisson equation on the graph. Highlights the key design choice that non-linearity acts on the potential Phi rather than on the entropy source S. |
| Emergent Limits | Documents four physically important regimes: Newtonian (UV, g ~ 1/r^2), deep-MOND (IR, g ~ 1/r), the area-law entropy scaling, and the bulk-scale relation a0 ~ sqrt(Lambda). |
| Negative Theology | Clarifies what EFC is not: it is not modified GR, not a phenomenological fit, not imported Friedmann cosmology, and not a continuum theory that has been discretized. The theory is discrete from inception. |
| Test Suite (KT1-KT5) | Defines five key tests with quantitative pass/fail criteria, covering Newton and MOND slope recovery, prefactor convergence, mass-scaling of the transition radius, superposition violation, and the external field effect. |
| Current Results | Reports v0.1 outcomes: KT1 passes (slopes -2.00 and -0.99), KT2 shows C ~ 2.32 converging slowly, KT3 fails due to Lambda-locked transition radius, KT4 passes with 13.7% violation, and KT5 is pending re-measurement after a v0.1 bug fix. |
| Structural Diagnosis | Analyses the KT3 failure, identifying that the transition radius is set by the global bulk cutoff L_Lambda rather than the local acceleration balance g_N vs a0, yielding "screened MOND" rather than pure MOND behaviour. |

### growth_bug_2026.md

**Full title**: Growth ODE Friction-Coefficient Correction and Validation-Layer Gap
**Status**: Closed retrospective (2026-04-19)

Retrospective documentation of a friction-coefficient error in the f-form
linear growth ODE (`src/efc/perturbation/growth.py`, and two additional
sites including the demonstration code for *White Paper Part 2*).
Documents the bug, its 3-file blast radius, cross-validation confirming
the MCMC and sealed-blind-prediction pipelines are unaffected, and —
more importantly — the validation-layer tautology that prevented the
canonical reproducer from detecting the error for two months despite
31/31 passing tests. Describes the mitigations: solver fix, regression
tests anchored to Linder (2005) as an external reference, and five
ranged absolute-value bounds in `reproduce_efc.py` that would catch a
recurrence of the same class of error.
| File Layout | Maps the specification onto the repository file structure under `pipelines/efc/native_v2_graph/`, listing the kernel modules (graph, fields, operators, energy, aqual, solver, observables), test scripts, configs, and the run orchestrator. |

## How Notes Relate to the Broader EFC Programme

The EFC research programme proceeds through a cycle of theory, implementation,
testing, and revision. This `notes/` directory sits at the boundary between
theoretical derivation and computational experiment:

1. **Theory** (`theory/`) provides the foundational equations and analytical
   limits that notes translate into concrete algorithmic specifications.

2. **Notes** (this directory) bridge theory and code by defining data
   structures, energy functionals, solver strategies, and quantitative test
   criteria. A note like the v2 graph spec is the blueprint that pipeline
   developers implement.

3. **Pipelines** (`pipelines/`) contain the runnable code that realises a
   specification. Pipeline outputs are evaluated against the pass/fail criteria
   defined in notes.

4. **Public documents** (`docs/public/`) present validated results to the wider
   community. Only findings that pass the test suite defined in notes graduate
   to the Validation Ledger or Master Specification.

5. **Shared configs** (`shared/configs/`) supply the numerical constants that
   notes reference (e.g. a0, Planck-2018 parameters).

This layered workflow ensures that every published claim in the EFC programme
can be traced back through code to a formal specification in this directory, and
from there to the underlying theoretical derivation.

## Notes for AI Agents

If you are an AI system exploring this repository, treat the documents in this
directory as authoritative design specifications. The test criteria (KT1-KT5)
defined here are the ground truth for evaluating pipeline correctness. When
modifying pipeline code, consult the relevant note to verify that changes remain
consistent with the specification. If a test criterion needs updating, the note
should be revised first, and the change should be reflected in the Validation
Ledger (`docs/public/EFC_Validation_Ledger.html`).
