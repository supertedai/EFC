# EFC Adversarial Review Protocol (v2 — paradigm-neutral)

**Status:** authoritative. This file lives in git and is the source of truth for
how a claim may be promoted. Hermes profiles, skills, cron and memory are thin
callers and mirrors — never the gate. If a Hermes update removes a skill, this
protocol and the CI gate that enforces it are untouched.

## Why this exists

A claim promoted on the strength of consensus can be wrong for a reason no
individual reviewer saw. The remedy is not more reviewers but a structure that
makes a single source-verified fact outrank any number of agreeing opinions,
and that marks every finding with *where its claim comes from* so that a
borrowed paradigm can never masquerade as raw evidence.

## The two rules that bind

1. **Consensus is not evidence.** A promoted claim (`declared_derived`,
   `declared_companion_upgrade`) must carry at least one `accepted` `supports`
   finding on a grounding evidence layer. Opinion layers alone (`PARADIGM`,
   `PREVIOUS_AGENT`, `HINDSIGHT`, `AUTHOR`, `HYPOTHESIS`) can never promote a
   claim. `RAW_SIGNAL`, `TARGET`, `NORMATIVE`, `DERIVED` and `EXTERNAL` ground
   directly; `INSTRUMENT` and `PROXY` are paradigm-laden (the measurer/
   instrument/proxy are borrowed from a paradigm), so they ground ONLY when
   the finding also carries an `atlas_field` pointing at the measurement chain
   (gate 7 — the bias-audit). Enforced mechanically in `efc_review_gate.py`.

2. **No agent promotes its own claim.** Agents write `proposed_status`.
   Only the human gate writes `status`. There is no code path from an agent to
   a binding status.

## Paradigm neutrality (mandatory)

ΛCDM, MOND, GR and EFC are treated as explicitly labelled model/paradigm
layers — none is a hidden null hypothesis or a universal answer key. When EFC
borrows a ΛCDM/GR-derived measure, measurer, instrument or coordinate choice,
the measurement chain must show *where* the borrowing enters and which bias it
can introduce. "Established physics" is not an unlabelled adjudicator.

## Evidence layers (closed vocabulary)

`RAW_SIGNAL · INSTRUMENT · PROXY · TARGET · NORMATIVE · DERIVED · PARADIGM ·
PREVIOUS_AGENT · HINDSIGHT · AUTHOR · EXTERNAL · HYPOTHESIS`

A Hindsight retrieval without a primary source is `HINDSIGHT`, never
`NORMATIVE`, and requires fresh source verification before it can support
anything.

## The nine reviewers (blind round, then adversarial round)

Each role answers one question; each has a bias-shield. Run 1–8 in parallel
without each other's findings (anchoring kills independence); then a fresh
Advocate and Attacker each get one rebuttal; then the meta-reviewer (9)
synthesises. See `review_roles.json` for the machine-readable mandates.

## The ten gates

1. Claim identity · 2. Provenance · 3. Formal validity · 4. Model-relative
validity · 5. Paradigm declaration · 6. Measurement chain · 7. Proxy & bias
audit · 8. Regime/phase/domain · 9. Discrimination & falsification ·
10. Reproduction + synthesis + **human gate**.

GR/ΛCDM is thus not a universal answer key — it is one model family judged
against the same raw signal and the same explicitly declared measurement chain.

## Release gate (fail-closed)

DOI reservation and publication are refused unless, for the claim in question:
- a frozen `verdict.json` is structurally closed (all findings disposed, valid
  `method_revision`), checked by `efc_review_gate.py` (pure stdlib, runs
  anywhere Hermes does not);
- `method_revision` is ≥ v2 (numeric compare, not equality — future v3 must not break it);
- all findings have a closed disposition;
- `human_gate.status` is exactly `approved`, written by a human, bound to the
  verdict by `verdict_id` + `method_revision` + `verdict_sha256`;
- `snapshot_sha256` matches the reviewed source AND the live manuscript is
  byte-identical to that snapshot (source edited after review = refusal);
- every promoted claim is both human-approved and grounded in an `accepted`
  finding on a grounding evidence layer (rejected findings never ground);
- `--confirmed-by morten` is present for any irreversible step.

Two separate enforcement layers, both authoritative:
1. `scripts/maintenance/efc_review_gate.py release <claim>` — the fail-closed
   release gate. Pure Python stdlib in git, runnable without Hermes; a non-zero
   exit is a hard refusal.
2. CI schema validation (`efc-schema.yml` / the review-gate workflow) — the
   frozen `verdict.json` and `human_gate.json` are validated against
   `verdict.schema.json` and `human_gate.schema.json` with `jsonschema`. The
   stdlib gate does structural checks so it runs anywhere; the CI step is the
   schema authority. Neither layer is optional.

## Method revisions

- **v1** = pre-paradigm-neutrality pilot (Run #001). Frozen history, never a
  release gate, never rewritten. β_F→α reconciliation is recorded in a dated
  addendum, never by mutating the frozen reviewer words.
- **v2** = this protocol.

## Atlas coupling

Findings reference the atlas's *actual* fields (`measure`, `maale_paradigme`,
`epistemikk`, `stipulasjoner`, `observer`, `regime`, `phase`, `emergence`,
`coupling`, `fractal`) as `atlas_field` values. `metaspeil`, `vektor` and
`rotasjon` are prose, not schema fields; rotation-curve concerns map through
`measure.proxy_chain`.
