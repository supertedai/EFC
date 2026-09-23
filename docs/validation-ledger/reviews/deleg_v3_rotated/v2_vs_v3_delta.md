# v2 → v3.1 delta

artifact_type: orchestrator_navigation_metadata (NOT reviewer output)
run_id: deleg_v3_rotated
parent: deleg_d21ed669 (v2, frozen, hash-bound, UNTOUCHED)

## What changed between the rounds

| Axis | v2 | v3.1 |
|---|---|---|
| Claims | 12 (C1–C12), all compound | 15 atomised, one predicate each |
| Gate cells | 120 (12×10) | 150 (15×10) |
| Distribution | 31 satisfied / 35 open / 54 n/a | 45 satisfied / 63 open / 42 n/a |
| Gate 1 (claim identity) | Failed blanket (compound) | 7 satisfied, 8 open (atomised) |
| Model | gpt-5.6-luna (9 roles) | gpt-5.6-luna (8 rotated + role 9 meta) |
| Findings | 55 | 15 claims × status + 6 packages + 5 artifact routes |
| Status | Verdict built by orchestrator (authority breach, later cleaned) | Role 9 = reviewer disposition, mechanical matrix |

**Note:** as a *share*, v3 is more open than v2 (42 % vs 29 % open) — not less. That is honest, not over-green; that is the point.

## What was atomised / reshaped

v3.1 is a *re-scoping*, not a renumbering of v2's C1–C12. The mapping:

- v2 C1/C2/C3 (Γ-forms + "non-linear saturation" + √[ρ]-residual) → v3 G1a/G1b (exact algebra) + G2a/G2b (dimensional normalization, *refined*: the √[ρ]-residual turned out to be the β/r_* hole) + G1c (domain).
- v2 C9 (a₀-discriminator proposed) → v3 A1a/A1b/A2/A3 (the a₀-ladder *expanded* to 6+ values with provenance + C=2.32-prefactor + ancestry assessment).
- **New in v3** (from the generative round, not in v2): B1–B4 (the transport bridge grid→covariant) + L1/L2 (paradigm limits as declarations).

## Key status changes (not just better resolution)

1. **C=2.32 is a numerically converged lattice measurement, not analytic Watson/Green.** (v2 called it a "fit"; v3 specifies: neither a statistical fit nor a derived constant.)
2. **The covariant EFT → μ_BE edge is `contradicted`.** (v2 flagged it only as "declared"; v3 establishes the trend break: the classical correction *increases* with g, μ_BE *decreases*, and μ_BE is postulated.)
3. **The β/r_* hole is a dimensional defect, not just a "residual dimension".** (x²/u = 4π/(3·l_g) = 2.59e35 m⁻¹; √u=x requires l_g = 4π/3 ≈ 4.19 m.)
4. **Two latent unit errors verified** (cosmology.yaml:18 a0_kpc deviation ~974k; efc_integration_test.py:48 Lambda_cosmo factor 1e6) — both without downstream consumers, severity medium.

## Compound claims requiring v3.2 (role 9's recommendation)

G2a, G2b, A1a, B1, B2, B3, L1, L2 — 8 compound in total. They are `is_compound=true` and cannot be closed as wholes. Role 9 recommended explicit sub-claims (G2a.1–3, G2b.1–3, A1a-per-value, B1.1–3, B2.1–4, B3.1–4, L1.1–4, L2.1–4).

## Coverage holes (role 9's assessment)

1. **F-prov-7 (`related_packages` heterogeneous)** — not among the 15 v3.1 claims. Role 9: *must* be added as an atomic v3.2 claim, not absorbed into package prose.
2. **The Γ-aliases are not literal common identifiers** — a v3.2 provenance claim must freeze the source→alias map, normalization, measurand, regime namespace.
3. The two latent unit errors must be repaired before any numerical a₀ bridge is used.
4. The five discriminator designs are not evidence nodes until measurement chains/likelihoods/holdouts are executed.

## The five routed artifact tasks (not closable by reading)

| Artifact | Type |
|---|---|
| β/r_* dimensional derivation | Author/math work |
| C=2.32 Watson/Green derivation | Author/math work |
| Canonical a₀ author-freeze | Author/human gate |
| Covariant reduction S_grid → relativistic action | Author/math work |
| Equal-footing holdout likelihood | Execution artifact |

## Provenance warning (carried forward from round 2)

- Role 9 was *partly seeded*: the prompt carried 12 "established physical judgements" to be preserved. Its confirmation of *these specific points* is seeded corroboration, not a fresh test. This is documented in `role9_provenance_note.json` and must not later be presented as independent validation.
- The round-2 attacker was seeded (5 targets with evidence). Adversarial material, not independent evidence.
- All roles are gpt-5.6-luna. Agreement = reading-consistency, never independent validation.
