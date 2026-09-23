# Run manifest — `deleg_d21ed669` (EFC Model Family Reconciliation, v2 adversarial review)

**This file is ORCHESTRATOR navigation metadata, not reviewer output.**
It contains no disposition, no claim_status, and no verdict. Those are
reviewer-authored artifacts (`verdict.json`, `claim_gate_matrix.json`,
`role_*.json`) and remain authoritative over this index. Do not read this
file as a synthesis of the reviewers' findings.

## Identity

| Field | Value |
|---|---|
| Run ID | `deleg_d21ed669` |
| Slug / manuscript | `EFC_Model_Family_Reconciliation` |
| Snapshot | `snapshot.tex` (frozen; byte-identical to live `.tex`) |
| Snapshot SHA-256 | `d21ed6699cf0ed438ae3c687553889e676d7dc92e45acab43d459e9281575f15` |
| Method revision | `v2` |
| Reviewers | 9 roles / 3 rounds (round 1: 8 blind roles; round 2: advocate + attacker; round 3: meta-reviewer) |
| Reviewer model | `gpt-5.6-luna` (same-model family — see caveat) |

## Artifact inventory

| File | Author | Content |
|---|---|---|
| `plan.json` | orchestrator | run plan / gate contract |
| `snapshot.tex` | orchestrator (freeze) | frozen manuscript text |
| `claim_map.json` | orchestrator | C1–C12 claim set |
| `role_*.json` ×8 | round-1 reviewers | 51 typed findings |
| `round2_advocate.md` / `round2_attacker.md` | round-2 reviewers | adversarial rebuttals |
| `verdict.json` | meta-reviewer | 55 findings (51 + 4 meta), 12 claim_verdicts |
| `claim_gate_matrix.json` | orchestrator (from reviewer dispositions) | 12×10 gate matrix |
| `meta_review.json` | meta-reviewer (role 9) | 51 dispositions, 12 claim_status, 4 meta findings, `gate_applicability` adjudication |
| `synthesis.md` | meta-reviewer (role 9) | **authoritative reviewer-authored synthesis** (global verdict, deepest finding, per-claim status, 6 author-gated items) |

`meta_review.json` and `synthesis.md` are the meta-reviewer's own words and are
**verbatim / authoritative**. This README duplicates none of their reasoning.

## Machine state (verified)

- **Findings:** 55 (51 round-1 + 4 meta-reviewer). All 12 claims `proposed`; nothing promoted.
- **Gate matrix:** 31 `satisfied` / 35 `open` / 54 `not_applicable` (120 cells = 12×10).
- **Hash binding:** `claim_gate_matrix.json → verdict_sha256` **matches** `sha256(verdict.json)`.
- **Schema check:** OK (all schema/instance pairs valid and closed).
- **Test suite:** 53/53 passed.
- **Fail-closed refusals (expected, by design):**
  - `runner check` → `REFUSED: claim 'C1' has an open gate (1)` (exit 1)
  - `release` → `REFUSED: human_gate.json missing (a human must dispose; agents cannot)` (exit 1)

## Why it stops here (author-gated, not agent-fixable)

1. **Γ cross-object identity/normalization** — `dS/dρ`, the per-mode rate, the
   `□φ = Γ(ρ)` source, and the grid-action Γ are not linked by a shared
   normalization/sign/unit/identity map (deeper than Γ_B's residual dimension).
2. **KC1 execution provenance** — the `≥5σ` SPARC language has null likelihood
   fields and "no new fit performed"; wording is a conditional falsifier, but
   execution/attribution is unproven.
3. **a₀ freeze** — provisional MOND/SPARC input `1.2e-10` (not EFC-derived);
   preregistration INVALID until exactly one value is author-frozen.
4. **B → B+ status** — declared companion relation, `supersession_status =
   not_established`; a discriminator test is the only thing that can select.
5. **Siren specificity** — `d_L^GW ≠ d_L^EM` is a class-level propagation
   observable; needs frozen `F(φ₀)/F(φ(z))` + a symmetric comparator (GR
   systematics + ≥1 rival friction model) to become EFC-specific.
6. **Figshare/version** — whether the corrected KC1 wording requires a public
   version bump is a publication decision, not an agent action.

## Caveat (epistemic, permanent)

All reviewers are the same model family (`gpt-5.6-luna`). Their agreement is
**reading consistency**, never independent validation. An executed empirical
test outranks consensus.

## Known coverage gap (not silently patched)

`related_packages` wording is corrected to "heterogeneous" in
`snapshot.tex:101`, but the leading "not cross-linked directly" remains
overbroad (F-prov-7: 31941465 and 31878760 carry direct `related_packages`
links). This proposition is **not** in C1–C12; adding it to `verdict.json`
requires a versioned claim-map revision and a new reviewer round.

## Handoff

This directory is **untracked** by design. Committing it — together with
`human_gate.json` (per `human_gate.schema.json`) and a regenerated
`findings_index.json` (`--apply`) — is the human-gated completion step, not
an agent action. Merge, DOI, Figshare, and publication are human word.
