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
├── EFC_native_v2_graph_spec.md   # v2 graph kernel specification
└── README.md                     # This file
```

## File Descriptions

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
