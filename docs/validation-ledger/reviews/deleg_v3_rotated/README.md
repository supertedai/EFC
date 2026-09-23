# v3 rotated-mandate gap-filling review — plan

artifact_type: orchestrator_navigation_metadata (NOT reviewer output)
run_id: deleg_v3_rotated
claim_map_version: 3.1-neutral (claims are neutral; the direction is decided by the reviewer)
parent: deleg_d21ed669 (frozen, hash-bound, NOT touched)
model: gpt-5.6-luna (same-model-family caveat applies)

## Why this round
v2 failed gate 1 because the claims were compound. v3.0 atomised into 16 claims but smuggled the orchestrator's OWN conclusions into the claims ("overlapping, not disjoint", "not independent because", "contradicting", "not a recovery"). A blind reviewer handed a conclusion inside a claim confirms the reasoning, not the truth — an echo chamber. v3.1 neutralises: 15 claims, one predicate each, the direction unknown to the reviewer.

## Neutrality rule
The reviewer DECIDES the direction (supported/contradicted/open), it does not confirm a built-in conclusion. If a claim still appears to carry a conclusion, flag is_compound/leading instead of confirming.

## The honest narrowing (five not-readable items — ROUTED, not SOLVED)
1. Is sqrt(u)=x? -> dimensional derivation of beta/r_* (G2a, G2b)
2. Is C=2.32 derived? -> Watson-integral / Green-function derivation (A2)
3. Which a0 is canonical? -> input/output freeze (A1a, A1b)
4. Is the covariant bridge closable? -> actual reduction S_grid->relativistic (B2, B3, B4)
5. Are the recovery edges real? -> executed likelihood/holdout (L1, L2)

These are WORK, not decisions. v3 documents and routes them — it solves nothing.

## D1 is NOT a claim
Five calibration-free discriminators (E_G, RAR with frozen a0, bullet delta_kappa, f_sigma8/BAO, lensing-slip/siren) are a TEST DESIGN, not a proposition to be "satisfied/open". It is removed from claim_map and lives here as a design artifact.

## Round 1: 8 blind, rotated reviewers (parallel)
1. Dimensional analyst -> G2a, G2b
2. Asymptoticist -> G1a, G1b
3. Regime/phase mapper -> G1c
4. Provenance accountant -> A1a, A1b, A2
5. Measurement-chain theorist -> A3
6. Alternative-paradigm comparator -> L1, L2
7. Covariant bridge analyst -> B1, B2, B3, B4
8. Reproducer/falsifier -> G1a, G1b, A1a, A2 (runs code)

## Round 2: advocate + attacker (after round 1)
The attacker is aimed EXPLICITLY at the orchestrator synthesis (leading claims, a0-bridge independence, "code-structure disguised as physical unification"), not only at the manuscript.

## Round 3: role 9 meta-synthesizer (synthesises 1+2, gate-applicability, overlap/contradiction)

## Definition of done (v3)
v3 is done when:
(a) the 15 claims have reviewer-assigned status + gate_applicability,
(b) the v2-vs-v3 delta is written,
(c) the five not-readable items are routed to named artifact tasks,
(d) the release gate is still REFUSED (fail-closed).

## Confidence numbers are NOT aggregated
confidence is per-reading certainty, not independent probabilities. No multiplication/averaging as if they were independent evidence (AI_REVIEW_NOTICE).

## Barriers (fail-closed)
- Do not touch deleg_d21ed669, verdict.json, claim_gate_matrix.json (tracked), findings_index.json (tracked).
- Do not run findings_index.py --apply.
- Do not promote RECOVERED_BY_LIMIT_OF to empirical recovery.
- Do not call C=2.32 "derived" without an independent analytic chain.
- Do not call Gamma_B a phase without a u->S mapping.
- Do not call box(phi)=Gamma(rho) the same Gamma as dS/drho without a typed identity map.
- Do not use the sqrt form as a positive KC1 win.
- No SPARC/a0 data used for both calibration AND discrimination.
- Human gate remains untouched and fail-closed.
- The orchestrator does NOT author findings/dispositions/verdicts/claim-status — that is reviewer output.
