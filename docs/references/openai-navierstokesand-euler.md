# External mathematical reference: OpenAI Navier–Stokes and Euler Lean repository

**Reference class:** external mathematical/formalization source; not EFC evidence.
**Reference status:** source snapshot pinned; local Lean build not verified; paper-to-Lean semantic correspondence challenged; EFC mapping proposed only.

## Canonical source and snapshot

- Upstream repository: <https://github.com/openai/NavierStokesAndEuler>
- Pinned commit: [`f9e8bc5b38b6e212696e8a30e3e91517af887bbd`](https://github.com/openai/NavierStokesAndEuler/commit/f9e8bc5b38b6e212696e8a30e3e91517af887bbd)
- Commit date: 2026-09-10
- Snapshot read: 2026-11-22
- License: Apache-2.0
- Lean toolchain declared by the repository: `leanprover/lean4:v4.34.0-rc2`; Mathlib and Comparator are pinned in `lakefile.toml`.
- Reproducible checkout: `git clone https://github.com/openai/NavierStokesAndEuler.git && cd NavierStokesAndEuler && git checkout f9e8bc5b38b6e212696e8a30e3e91517af887bbd`.

The `main` HEAD measured on 2026-11-22 resolves to this same commit. The pinned upstream tree is the reference; later `main` revisions must be recorded as separate snapshots rather than silently substituted.

## What the Navier–Stokes result states

The repository and linked OpenAI manuscript concern **forced** incompressible 3D Navier–Stokes. For each positive viscosity they state breakdown alternatives (C) and (D): a smooth initial condition together with a smooth external force satisfying the stated conditions, on all of `R^3` or on the periodic torus. This is not the same statement as blow-up for the unforced Navier–Stokes problem. The repository separately formalizes an **unforced Euler** result; do not conflate that with its Navier–Stokes result.

Primary manuscript: <https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf>
OpenAI announcement: <https://openai.com/index/navier-stokes-solution/>

## What the Lean status does—and does not—establish

At the pinned commit, `formalization.yaml` reports `sorry_count: 0` for the listed main Navier–Stokes and Euler declarations, and lists only `propext`, `Classical.choice`, and `Quot.sound` as their axioms. This is the repository's own status declaration. Its `review.status` is `self-assessed`; the metadata is not an independent mathematical review.

The repository README gives `lake exe cache get` and `lake build` as the build procedure. It also documents separate Comparator challenges for comparing theorem statements. The challenge files intentionally contain `sorry` placeholders; these are not the same as the listed main theorem proofs having zero `sorry`.

The KCL/Cambridge preprint, *Navier–Stokes lost in translation* (<https://arxiv.org/abs/2610.08144>), reports that some Lean declarations do not faithfully match stronger or differently formulated claims/proofs in OpenAI's human-readable manuscript, including a derivative-order discrepancy in Lemma 8.6. The authors explicitly do **not** establish that OpenAI's natural-language proof is false; the finding means that Lean-checking the formal artifact alone does not establish that the paper and Lean development prove the same claims.

**Local execution on 2026-11-22:** the repository was downloaded and pinned at the commit above. A local `lake build` attempt did not run: `lake` is not installed/on `PATH` (exit 127). No local Lean kernel build or Comparator run is therefore claimed here.

## EFC relationship and bounded use

The EFC regime-transition package (DOI <https://doi.org/10.6084/m9.figshare.31941543>) already contains a data-field analogy between laminar/turbulent Navier–Stokes regimes and an EFC regime transition: [`regime_transition_data.json`](../papers/efc/Consistency_of_Scale_Dependent_Gravitational_Response_in_EFC_Numerical_Regime_Transition_Test/data/regime_transition_data.json). The corresponding EFC implementation computes cosmological response quantities; it is not a Navier–Stokes solver. At EFC `origin/main` commit `9c88ed20`, topic queries for `Navier-Stokes`, `fluid dynamics`, `turbulence`, and `Reynolds` returned no atlas hits. That is a search result, not proof that no related concept exists under another label.

Appropriate use: a pinned mathematical reference and possible external test domain for EFC's regime-description methods. Before making a physical bridge, define an explicit map from EFC variables to fluid observables and equations, state forcing/boundary conditions and the applicable regime, and derive a differential, falsifiable prediction against the standard Navier–Stokes baseline. A resemblance between energy flow, dissipation, or regime language is not a derivation, an EFC prediction, or evidence for EFC. No such coupling or fluid-data test is established by this reference entry.

## Evidence labels

- **Source present:** upstream Git repository at the exact commit above; local checkout retained separately from the EFC Git tree.
- **Formalization status:** repository-reported zero `sorry` for named main declarations; local build not run because the required `lake` executable is absent.
- **Semantic correspondence:** challenged by the cited KCL/Cambridge preprint; unresolved here.
- **EFC relation:** documented analogy and proposed use only; no EFC implementation, derived coupling, or empirical test.
