# The risk register (the reviewer function, phase 1)

This is the EFC repository's one append-only risk register. The register is
**the source of truth** for risk: a finding that exists only as report prose
counts as open.

The basis for the decision: `/home/morten/hermes-filer/efc-reviewer-avgjorelse.md`
(2026-09-17, fanout `deleg_2465ee23`, five perspectives, converging):
**no new Reviewer profile** — a reviewer FUNCTION owned by the orchestrator
layer, with an external attesting party at medium/high risk and the human as the
professional approver for the irreversible/critical.

## The files

| File | What |
|---|---|
| `risiko-register.jsonl` | The register itself. One line = one entry. **Append-only.** |
| `README.md` | This file: schema, thresholds, gates, usage. |

Append-only is a **git property**, not a file property. CI requires that the
diff on `risiko-register.jsonl` only adds lines
(`validate_risk_register.py --base <ref>`), and that every entry validates
fail-closed. Everything under `governance/risiko/` is owned content like
everything else in the repository (`governance/**` → the component `rotfiler`,
owner `orchestrator`), and the validator checks that itself in addition to
`validate_ownership.py`.

## Field specification (`registerversjon: "1.0"`)

The register is **closed**: a field that is not listed here is an error, not a
piece of information. The field names are the register's own JSON keys and
stand verbatim — they are the schema the validator reads, not prose. Where a
key is a transliteration of a Norwegian word, its plain-English reading stands
in parentheses. The fields marked **closing field** are the only ones that may
be changed on an existing entry — that is the human's gate decision (see
"The gate").

| Field | Type | Requirement |
|---|---|---|
| `risk_id` | str | `RISK-<TYPE>-<4 digits>`, unique, TYPE must match `type` |
| `type` | str | `HAZID` \| `HAZOP` \| `BLAST_RADIUS` \| `GAP` |
| `hazard_or_deviation` | str | The hazard or the deviation, one sentence |
| `source_change_id` | str | `t_<hex>` \| `pr<number>` \| `<base-sha>..<head-sha>` |
| `release_id` | str\|null | null when the entry does not belong to a release |
| `berorte_komponenter` (affected components) | list[str] | ids from `governance/ownership-register.json` — must exist |
| `arsak` (cause) | str | Why this can happen |
| `konsekvens` | str | What is at stake |
| `barrierer` | list[str] | What already stands against it |
| `sannsynlighet` | str | `lav` \| `middels` \| `høy` |
| `alvorlighet` | str | `lav` \| `middels` \| `høy` \| `kritisk` |
| `blast_radius_score` | int | 1–256 (`F × E × P × I`) |
| `klasse` | str | `grønn` \| `gul` \| `rød` — **never laxer than the score** |
| `eier` | str | One of the `owners` in the ownership register |
| `utforer` (executor) | str | Whoever registered the entry |
| `reviewer` | str | **Must differ from `utforer`** (no self-review) |
| `status` | str | `oppdaget` → `lukket` \| `superseded` — **closing field** |
| `tiltak` | list[str] | Actionable measures |
| `kanban_card_id` | str | `t_<hex>` \| `pr<number>` |
| `gate_required` | bool | Required (`true`) for the red class |
| `gate_decision` | str | `venter` \| `godkjent` \| `avslått` \| `ikke_nodvendig` — **closing field** |
| `gate_besluttet_av` | str\|null | Required when the decision is `godkjent`/`avslått`, and must then be `menneske` — **closing field** |
| `evidenslenker` | list[str] | Prefix `repo:` (the path must exist) \| `url:` (http/https) \| `ekstern:` (source outside the tree) |
| `opprettet_tid` | str | ISO-8601 |
| `forfall` | str\|null | `YYYY-MM-DD`, `null` = no agreed deadline |
| `sist_vurdert` | str | `YYYY-MM-DD` — **closing field** |
| `rest_risiko` (residual risk) | str | What still stands open |
| `supersedes` | list[str] | risk_ids this entry replaces — must exist |
| `related_ids` | list[str] | Related risk_ids — must exist |
| `registerversjon` | str | `1.0` (unknown version = error) |

The `ekstern:` prefix is deliberate: the HAZID/HAZOP analysis that seeded the
register sits outside the tree today. A false `repo:` path would have hidden it.

## Class, thresholds and what they demand

`blast_radius.py` computes `BR = F × E × P × I` (each factor 1–4, lowest value 1
so "unknown" never masks risk). The class names below are the literals the
scorer itself emits:

| Score | Class | Requirement |
|---|---|---|
| 1–3 | `liten` | may land automatically |
| 4–7 | `material` | independent reviewer + rollback plan + readback |
| 8–15 | `høy` | 2 independent controls (or reviewer + verifier), ADR |
| 16–31 | `kritisk` | owner sign-off + canary + **human gate** |
| 32+ | `blokkerende` | freeze/quarantine — only the human can decide |

A **critical trigger overrides the number**: `privilegium`, `produksjon`
(`figshare/**`, `docs/public/**`), `destruktiv` (migration/deletion) and
`gate-endring` (`.github/**`, `governance/**`, `*gate*.py`, the scheduler
scripts) each force the blocking class, while `ukjent-grenseflate` (a file with
no owner) forces the critical class on its own. A trigger beats the score in
both directions of that table — never the other way round.

The register's `klasse` is `grønn|gul|rød`, mapped like this: `liten` → `grønn`,
`material`/`høy` → `gul`, `kritisk`/`blokkerende` → `rød`. The validator enforces
that the class is **never laxer than the score**: 4+ cannot be `grønn`, 16+
cannot be `gul`. Stricter is allowed — a qualitative assessment may lift an
entry.

## The gate

`gate_required: true` + `gate_decision: "venter"` means: **the change cannot be
closed before the human has decided it.** A closed entry with a gate demand
requires `godkjent`/`avslått`, and both of those require
`gate_besluttet_av: "menneske"`. Nothing automatic — neither CI, the maintenance
round nor a profile — can write a human decision. `blast_radius.py --gate`
refuses (exit 1) to let a critical/blocking change through without such a
decision in the register.

**How the human writes the decision.** The register is append-only, but the
decision is NOT a new line — it is a change of the **closing fields** on the
entry that is waiting: `status` (`oppdaget` → `lukket`/`superseded`),
`gate_decision` (`venter` → `godkjent`/`avslått`), `gate_besluttet_av`
(`null` → `menneske`) and `sist_vurdert` (the date of the decision). That is the
ONE exception `append_only()` allows: everything else on the entry is immutable
finding data, and a diff that touches another field — or deletes the entry, or
merely moves it (reordering) — still counts as `not_append_only` and stops CI.

**The decision is per entry, not per change-id.** A change-id may carry several
open gate entries (the seed has two for `t_f882cfca`). `--gate` does not let a
change through merely because one of them is approved: `slaa_opp_gate` demands
that EVERY gate entry for the change-id is decided, that none stands at `venter`
and none is `avslått`, and that at least one is `godkjent` by the human. One
approved entry therefore does not cover the other one that is still waiting.

## How it is used

```bash
# scores a diff (report; --gate refuses critical/blocking without a decision)
python3 scripts/maintenance/blast_radius.py --diff origin/main
python3 scripts/maintenance/blast_radius.py --diff origin/main --gate

# validates the register fail-closed, and demands append-only against a ref
python3 scripts/maintenance/validate_risk_register.py --json
python3 scripts/maintenance/validate_risk_register.py --json --base origin/main

# the weekly round runs both and opens one idempotent card per finding class
python3 scripts/maintenance/vedlikeholdsrunde.py --dry-run

# the status words in the activity log
python3 scripts/maintenance/validate_activity_log.py --json
```

CI: `.github/workflows/efc-risiko.yml` (PR + push to main). The scorer runs
there as a **report** — the gate is the human's merge on protected main, not a
green CI job. The register validator runs fail-closed.

## The status words (the activity log)

`logs/activity.jsonl` may carry `statusord`: a list drawn from
`{maskinelt kontrollert, eksternt verifisert, faglig godkjent}`. The words are
**mutually independent** — none of them implies the other two, and the guard
never adds or demands a word that the entry does not carry. The one demand:
`faglig godkjent` may stand only on an entry with `role: "menneske"`, because
professional approval cannot be delegated to a label.

## Seed (2026-09-17)

Two entries are seeded from the existing analyses
(HAZID: 29 hazards, HAZOP: 70 failure states), each with its analysis's
**top 3** named in `tiltak`:

- `RISK-HAZID-0001` — privilege concentration, severity critical, score 64,
  red, the gate is waiting for the human.
- `RISK-BLAST_RADIUS-0001` — the card's own gate change, measured by the scorer
  (`F=3 × E=2 × P=1 × I=4 = 24`, trigger `gate-endring` → `blokkerende`).

## What the register is not

The honesty list from the design stands: a register is not a guarantee of truth.
An entry is traceability, not proof that the risk is handled; `superseded` means
replaced, not gone; and "no registered deviations" means "none registered" — not
"none".
