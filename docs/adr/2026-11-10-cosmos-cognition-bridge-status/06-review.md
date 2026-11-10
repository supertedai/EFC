# 06 — Independent review

**Status: REVIEWED. One external panel round on the patch, findings dispositioned; one
confirmation round on the delta.**

## Reviewer route and provenance (measured)

| Field | Value |
|---|---|
| Route | `openai` (direct API — the only route that can echo which model answered) |
| Model requested | `gpt-5.6-luna` |
| Model echoed by the API | `gpt-5.6-luna` |
| `model_verified` | **true** |
| Script | `/opt/hermes-skills/autonomous-ai-agents/claude-opus-second-opinion/scripts/claude_opus_api.py` |
| Prompt | neutral dossier, 24 131 chars: acceptance criterion, verbatim source quotes P1–P5, exact `git show` of the patch, the post-patch provenance/revision, the measured register side effects, 7 neutral questions. It contained no verdict and no leading wording. |
| Verdict | **PASS**, confidence **0.93** |

This is a **different model from the implementer** (the implementer ran as
`deepseek-flash`), reached over a separate channel with the model id echoed by the API — so
it is a genuine external review, not a same-family second look. The reviewer had no tools and
no write access.

Independence note: the dossier *did* include the acceptance criterion from the card, because
a reviewer must know what was asked. That is Morten's requirement, not the implementer's
conclusion; the reviewer was asked explicitly to judge whether each claim in the patch is
supported by the sources.

## Findings and disposition

| # | Sev. | Reviewer's point | Verdict | What was done |
|---|---|---|---|---|
| 1 | note | All substantive claims are supported by P1–P5 | accept (agreement) | no action |
| 2 | should-fix | "Counter-evidence, earlier" is imprecise: P1/P4 qualify *derivation and empirical establishment*, not the *existence* of proposals | **accept** | reworded to "Earlier qualifications against the bridge being derived or empirically confirmed" |
| 3 | note | "Two … exist" implies exactly two; "at least two … have been published" is more precise | **partial accept** | changed to "**At least two** formal/model-based proposals exist" — removes the exhaustiveness implication. "Published" was not adopted: the bank's job is to record that proposals exist, not to certify the publication channel |
| 4 | note | The patch asserts no empirical or causal establishment | accept (agreement) | no action; the negative-claim pin is in the test |
| 5 | note | Recording the 32091700 conflict as unresolved is correct; DataCite does not settle which local label is right | accept (agreement) | no action |
| 6 | should-fix | Omitted a P2 limit: "The bridge does not close the cosmology-RLHF loop directly" — a reader could infer a complete closed bridge | **accept** | added to the revision entry, and **pinned by the test** |
| 7 | should-fix | Omitted a P1 limit: "EFC-C has not yet been fit to a neural dataset" | **accept** | added to the revision entry, and **pinned by the test** |
| 8 | should-fix | The commit message contained a malformed DOI, `10.32091700` | **accept — real defect** | corrected to `10.6084/m9.figshare.32091700`; the commit was rewritten before it was ever pushed |
| 9 | should-fix | Citing P4 by repository path instead of DOI can look like metric gaming unless the policy is documented; adding the DOI in a non-provenance field would be more transparent | **partial accept** | *Documentation*: accept — the policy is written down in `01-context.md` (coverage register) and `02-options.md` §F. *Adding the DOI*: **reject on measured behaviour** — the register matches `10\.6084/m9\.figshare\.\d{8}` anywhere in the bank file, so there is **no** "non-provenance field" that would not flip the flag; adding the string is exactly what would clear the backlog item without a decision |
| 10 | note | Hard-coded 126/86 totals are snapshot assertions, not proof that *this* patch added nothing | accept (note, no change) | that is the assertion's stated purpose (the card forbids inventing a node or an edge); the count is pinned in `test_atlas_proveniens.py` against the same baseline |
| 11 | note | The entry gives future readers most safeguards; the missing ones are #6 and #7 | accept (agreement) | addressed by #6/#7 |

## Confirmation round on the delta

A second panel call was made with the **delta only** (the reworded sentence, the two added
limits, the corrected DOI) and the question "do these changes introduce any new defect or
misstatement, and is each of your should-fix findings now satisfied?" — not a re-ask of the
original question, and not an iteration toward agreement. Result recorded below.

_Round 2 result:_ filled in §"Round 2" below.

## Round 2

_Pending at the time this file was first written; appended after the call._

## What this review does NOT establish

- It does not establish that the atlas is scientifically correct, only that this patch's
  wording is calibrated against the sources it cites.
- It is one external model. It agrees with the implementer on the main claim, which is
  expected when both read the same evidence — the value is in the four should-fix findings it
  produced, three of which changed the artifact.
- Landing is still Morten's word.
