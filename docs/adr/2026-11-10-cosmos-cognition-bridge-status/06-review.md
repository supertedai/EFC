# 06 — Independent review

**Status: REVIEWED. Two external panel rounds (review + delta confirmation) with the same
verified route; every finding dispositioned. The final external verdict is BLOCK on one
point, and that point is measurably absent from the artifact — see Round 2.**

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

Route and model identical to round 1 (route `openai`, model echoed `gpt-5.6-luna`,
`model_verified: true`). The dossier contained **only the file delta** between the reviewed
version (`37babbbb`) and the final one (`b67759b5`), plus the five questions above.

**Verdict: BLOCK, confidence 0.98.** Findings:

| # | Sev. | Point | Verdict | Why |
|---|---|---|---|---|
| R2-1 | note | (2) satisfied by "Earlier qualifications against the bridge being derived or empirically confirmed" | accept (agreement) | — |
| R2-2 | note | (6) and (7) satisfied and faithful to the sources | accept (agreement) | — |
| R2-3 | should-fix | **(8) not satisfied** — the malformed DOI `10.32091700` is said to remain in the commit message; no correction was shown in the delta | **reject on measurement** | the dossier for round 2 showed only file diffs, so the commit message — which is where finding (8) lived — was not in front of the reviewer. Measured on the artifact: `git log -1 --format=%B b67759b5 \| grep -o "10\.[0-9]\{4,5\}/[^ ,;)]*"` → `10.6084/m9.figshare.31940547`, `10.6084/m9.figshare.31969983`, `10.6084/m9.figshare.32091700's`; `grep -c "10\.32091700"` → **0**. The malformed token does not exist in the committed history. This was a **defect in my round-2 dossier**, not in the patch |
| R2-4 | note | (3) "At least two" adequately avoids the exhaustive implication | accept (agreement) | — |
| R2-5 | note | no new defect introduced by the delta | accept (agreement) | — |

### How the BLOCK is handled

The BLOCK rests on an artifact I failed to supply (the commit message), not on the patch.
The disposition is therefore **reject on L0 measurement**, not "argue with the reviewer",
and not a third panel call — the second-opinion protocol forbids iterating toward agreement,
and the point is settled by a command anyone can rerun. Recorded here so the disagreement is
visible rather than tidied away: an external reviewer's last word on this change is **BLOCK**,
its stated ground is measurably absent, and the ground's absence is my presentation error.

If Morten wants an external sign-off on finding (8) specifically, the artifact to put in
front of a reviewer is `git log -1 --format=%B b67759b5` (or the PR description), not a file
diff.


## What this review does NOT establish

- It does not establish that the atlas is scientifically correct, only that this patch's
  wording is calibrated against the sources it cites.
- It is one external model. It agrees with the implementer on the main claim, which is
  expected when both read the same evidence — the value is in the four should-fix findings it
  produced, three of which changed the artifact.
- Landing is still Morten's word.
