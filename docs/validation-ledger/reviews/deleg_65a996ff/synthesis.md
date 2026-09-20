# Review synthesis — Γ(ρ) form split (bifurcation) and KC1 status

**Delegation:** `deleg_65a996ff` · **Dispatched:** 2026-09-20 · **Model:** gpt-5.6-luna

## Status of this review (read first)

- **Independence caveat:** all six reviewers are the *same model family*. Their agreement is intra-family reading consistency, **not independent validation**. No external or physical validation is claimed.
- **Normalization:** reviewer outputs were written partly in a Scandinavian language; this archive normalizes them to English. Structured fields (`finding_type`, `doi`, `status`, `conflict_class`, `falsified_by`) are preserved; narrative prose is summarized, not reproduced verbatim.
- **Archive shape:** six reviewer deliveries are normalized into six structured per-role files (`role_0.json` … `role_5.json`, one entry per role, each with its typed findings, verdict and conflict classes), plus one aggregated `roles.json` (verdict + conflict classes per role) and this `synthesis.md` (consensus, dissents, limitations). The per-role files carry the full typed-findings evidence; `roles.json` is a compact index over them.
- **Raw record:** the verbatim fanout transcript lives outside the repo at `~/.hermes/profiles/researcher/cache/delegation/live/deleg_65a996ff/task-*.log`. This archive is the normalized, authoritative layer.

## Question under review

The published corpus carries three competing Γ(ρ) realisations for one intended target quantity, plus two Bose–Einstein exponents, plus a kill criterion (KC1) whose empirical status is unclear.

## Consensus findings (all six reviewers)

1. **Three Γ forms, one target.** A = ρ/(ρ+ρcrit), B = ρ^(3/2)/(ρ+ρcrit), C/B+ = √(ρ/ρcrit)/(1+√(ρ/ρcrit)). They are three candidate definitions of the *same* intended quantity Γ(ρ), not three independent observables.
2. **Shape bifurcation, not trifurcation.** A and C share a saturating rational shape (argument r vs √r); B alone is a non-saturating power (grows as √ρ at high density).
3. **B is non-saturating, and the source records it.** 31942821's own requirement row R2 reads "Partial — not saturation". This is the source's own label, not a coined "P1 violation".
4. **B's prefactor is an unresolved normalization convention.** Displayed as ρ^(3/2)/(ρ+ρcrit) but implemented on dimensionless r = ρ/ρcrit; the source does not reconcile the two. Not a demonstrated unit error.
5. **KC1's wording admits two readings; neither is privileged.** 31941465's `kill_criteria[0]` is a pre-registered kill condition (IF linear wins and √ is excluded at ≥5σ, THEN the √g theorem is falsified) — the *threshold* reading, consistent with PDF §2.4 Table 1 (C3 linear eliminated, C5 √ survives). But the wording is present-tense indicative ("data demonstrate … significantly exclude √g at ≥5σ"), which also admits a *result* reading asserting an executed exclusion that the metadata contradicts (`delta_chi2=null`, `significance_sigma=null`, "no new fit performed"). Which reading is intended is author-gated.
6. **BE exponent split.** exp(√(g/a₀)) is derived in 31878334, 31878760, 31941465 (E ∝ √g); exp(g/a₀) appears in 31942821 metadata and 31941543. Unreconciled.
7. **Supersession is declared, not established.** 31942821's code header declares 31942800 an "upgrade to Scenario B+", but 31942821 is not retired (its key_result says Scenario B, its description says A). This is a declared companion/upgrade relation, not an established scientific supersession.
8. **Public surface mirrors the mixed state.** Validation Ledger and Changelog publish B, B+ and A in the same section without selecting one.
9. **Conflict class = provenance/metadata.** No reviewer found an established physical falsification; the conflict is provenance, representation and version drift.

## Corrections applied to reviewer claims (post-fanout)

- Reviewer 1 (mathematical) labeled B "requires_prefactor_units". The agent qualified this to **normalization_convention_unresolved**: the code consumes a dimensionless r, so Γ₀ can carry [Γ]. The stronger label would have repeated the KC1 overclaim pattern.
- **Post-review source reconciliation (KC1):** the fanout (and the agent's first synthesis) read `kill_criteria` under the *result* reading and flagged an epistemic overclaim. The wording admits a second reading — a *falsification threshold*: "IF robust data prefer the linear form and exclude √ at ≥5σ, THEN the √g theorem is falsified" — under which PDF §2.4 Table 1 (C3 linear eliminated, C5 √ survives, SPARC best fit by √(g/a₀)) makes the package self-consistent. Both readings are supported by the text ("data demonstrate … exclude" is present-tense indicative, so the result reading is not a misreading); neither is privileged. Which is intended is author-gated. The residual, narrower finding is a **PDF-to-metadata provenance gap**: the PDF asserts a >5σ SPARC χ² with no inline citation, while `datasets_used` says "no new fit performed" and `delta_chi2`/`significance_sigma` are null. The original reviewer deliveries are preserved as historical record and reconciled here, not rewritten.
- The verbatim fanout contains Scandinavian prose; normalized here per the repo-wide language gate (`docs/validation-ledger/**` is guarded).

## Open items (gated on author word)

- B's final claim status: `declared_derived` + internal conflict, versus superseded by B+.
- KC1 wording resolution (threshold vs result reading) + PDF↔metadata provenance gap (the PDF asserts >5σ SPARC χ²; metadata says no new fit; execution provenance author-gated) — not an "overclaim downgrade".
- The two discriminating tests (SPARC retrodiction with a₀ locked; dL^GW ≠ dL^EM) — preregistration.
- Publishing the Γ bifurcation + KC1 as one named finding.

## Conclusion

A, B and C are three declared forms of one target with one shape bifurcation and one internal unresolved conflict. KC1's wording admits both a falsification-threshold and a result reading; the open items are that wording resolution (author-gated) and a PDF-to-metadata provenance gap, not an established physical falsification. This is a provenance/representation issue, not an established physical falsification. No claim here is "measured" or "verified" — the audit reads source text and arithmetic only.
