# EFC Content and Source Policy

**Version**: 1.0
**Status**: proposed implementation contract — not yet enforced by CI
**Date**: 2026-08-19
**Author**: Morten Magnusson (ORCID 0009-0002-4860-5095), Symbiose Research, Sandnes, Norway
**License**: CC-BY-4.0
**Scope**: any agent or workflow that proposes updates to `docs/public/` from
external news or research sources

---

## 0. What this document governs, and what it does not

This policy separates four steps that are easy to collapse into one:
**acquisition**, **editorial judgement**, **proposal**, and **publication**.
An agent may automate the first three. It must not perform the fourth.

It does **not** introduce a new scanning mechanism. This repository already
has one, and this policy governs it rather than competing with it:

| Existing artefact | Role |
|---|---|
| `.claude/prompts/research_watch_delta.md` | the delta-scan procedure |
| `docs/public/external_research_watch.json` | the watchlist — source of truth for "already seen" |
| `docs/public/external_research_watch_mapping.json` | watchlist → ledger mapping |
| `docs/public/EFC_External_Research_Ledger.html` | the published external-research page |

Where this policy and the delta-scan prompt disagree, **this policy wins and
the prompt should be corrected**, so that one rule set governs one pipeline.
Section 4 lists the disagreements known at the time of writing.

### Provenance of this text

An earlier draft of this policy was written in Norwegian and largely lost
before it was committed. Roughly a quarter of it was recovered verbatim from
run logs; the rest existed only as section headings. This document is
therefore **newly authored in English**, and it is not a translation. Rules
marked *[recovered]* are restatements of the surviving original text. Rules
marked *[new]* were written for this version and have no predecessor — they
are proposals, not restored decisions, and should be read with that weight.
The recovered material predates the current repository invariants and did not
account for them; §1.8 and §4 are where that gap is closed.

---

## 1. Non-negotiable rules

1. *[recovered]* Every external factual claim must carry a source record with
   a canonical URL, a `retrieved_at`, and — where the source states it — an
   `occurred_at` or `published_at`. **Time of retrieval is not time of event.**
2. *[recovered]* A search snippet, model recollection, or memory-store entry is
   never on its own sufficient documentation for a news or research claim.
3. *[recovered]* The agent writes only to an isolated working branch or
   produces a dry-run report. Direct push to a published branch is disabled by
   default.
4. *[recovered]* Source URL, DOI, arXiv ID, and content hash are used for
   deduplication; the same story must not be published twice because several
   outlets covered it.
5. *[recovered]* Disagreement, missing metadata, low quality, possible
   retraction, or uncertain relevance must be surfaced as uncertainty and must
   stop automatic publication of that item.
6. *[recovered]* No secrets, API keys, personal access tokens, or private
   memory extracts may reach HTML, logs, commits, or proposals.
7. *[recovered]* The agent preserves existing HTML structure, navigation, and
   manual editorial content. It must never rewrite the whole site to change a
   single entry.
8. *[new]* **The three-layer evidence separation in `AGENTS.md` is binding on
   this pipeline.** Third-party literature discovered by any scan is layer 2:
   it belongs in §4b of `docs/public/EFC_Validation_Ledger.html`, tagged
   `[external — …]`, and **never** in `docs/validation-ledger/data/*.json`.
   Only EFC's own publications, each with an 8-digit Figshare DOI, enter the
   JSON evidence registers. An agent that moves an external item into those
   registers has committed claim inflation, which CI rejects.
9. *[new]* **Language discipline applies to generated prose.** External results
   are `consistent with`, `overlaps with`, or `within EFC prediction band` —
   never `confirms EFC`. This holds for the `efc_relevance` field as much as
   for rendered HTML.

---

## 2. Source hierarchy

### 2.1 EFC's own sources *[recovered]*

For claims about EFC, in this order:

1. EFC's versioned canonical documents and technical specifications in this
   repository, cited with file path and commit or version.
2. EFC's published articles and datasets with a DOI or other stable identifier.
3. EFC's official publication surfaces, when the content can be traced back to
   a versioned original.
4. Internal memory stores and the EFC graph, as **internal traces and
   prioritisation signals only**.

A memory entry or graph node may propose a topic or reuse an already-verified
EFC claim, but it must point back to an external or versioned EFC source
before the claim enters public HTML. The agent records the memory or graph
reference and lookup time in its working log; it does not reproduce private
memory text.

### 2.2 Research *[recovered]*

Use several layers, in this order:

- DOI and bibliographic metadata from Crossref or the publisher's official
  page. The Crossref REST API supports lookup and filtering of work
  metadata.[^1]
- OpenAlex as a secondary catalogue for discovery, relations, and search;
  verify title, authors, date, and DOI against the DOI or publisher page
  before publication.[^2]
- arXiv for preprints. An arXiv result must be explicitly marked `preprint`
  and must not be described as peer-reviewed.[^3]
- Peer-reviewed full text or abstract from the publisher or repository, when
  the agent actually has access to it.
- Institutional press releases only as secondary explanation, never as the
  sole evidence for a scientific effect.

Absence of a DOI does not automatically invalidate a work, but it lowers the
quality score and requires clearer labelling. Claims of causality, health
effect, breakthrough, or that a method is established require at least one
primary source and one independent confirmation, or human approval.

### 2.3 News *[recovered, completed]*

Permitted entry points are RSS/Atom feeds, official press releases,
established editorial publications, and primary sources (authority,
institution, project, or company announcement). A news item must have:

- at least one named source that has been read, not merely surfaced by search;
- a separate primary source when the item contains figures, claims about
  research, or attributions of causality. *[new — the recovered text is cut
  off at this point; the remainder of §2.3 below is authored]*
- an identifiable publication date; an item whose date cannot be established
  is held, not published.

News is the weakest tier in this policy. For a physics repository it exists to
provide context around a result, never to establish one. A news item may
accompany a research item; it may not stand in for it.

---

## 3. Domain scope *[recovered in spirit, enumerated from existing practice]*

The delta-scan prompt already enumerates the search domains in use. They are
restated here so the scope lives in the policy rather than only in a prompt:

DESI (DR2 full-shape/RSD, DR3 pre-release); Euclid (Q1, DR1,
science-verification); DES Y6, KiDS Legacy, HSC Y3 cosmic shear; ACT DR7,
SPT-3G, Simons Observatory CMB and lensing; SPARC and BIG-SPARC rotation
curves and modified-gravity fits; JWST Bullet Cluster and other cluster
lensing; entropic, emergent, and informational gravity preprints; and any work
citing an EFC DOI.

Adding or removing a domain is a policy change and goes through review.

---

## 4. Known disagreements with the current pipeline *[new]*

These are gaps between this policy and the pipeline as it stands. Items 1–2
concern `research_watch_delta.md`; items 3–6 concern
`docs/public/external_research_watch.json` and the checks in
`scripts/maintenance/efc_verify.py`. Each is a defect in the pipeline, not an
exception to the policy.

1. **The prompt instructs the agent to commit and push.** Rule 1.3 says the
   agent writes to an isolated branch or a dry-run report. Pushing to an
   active development branch is close to, but not the same as, that. The
   prompt should state the branch is never a published branch, and that no
   merge is performed by the agent.
2. **The prompt is written in Norwegian and ends with "Svar på norsk".** The
   repository's working language for published artefacts is English. Norwegian
   output cannot be pasted into `docs/public/` without translation, which is an
   unrecorded editorial step.
3. **The watchlist has no evidence tier.** `source_type` distinguishes
   `paper | dataset | survey-release | preprint | framework-seminal`, which is
   a *kind*, not a *quality*. §2.2's hierarchy is currently unrepresentable in
   the data.
4. **The watchlist has no content hash**, so rule 1.4's hash-based
   deduplication is not implementable against it today; deduplication is
   `key`-only.
5. **The status lifecycle has no drain.** Of 106 items at version 1.8,
   71 are `status: new`. A status that is never advanced records that
   something was seen, not that it was assessed. §6 proposes the missing
   transitions.
6. **The watchlist already breaches §1.9, and nothing catches it.**
   `arXiv:2503.14738` says `supports EFC L2→L3 regime transition`, and
   `arXiv:2602.10065` says `2.6σ CMB tension validates EFC logged DES Y6 P3
   PASS`. `validates EFC` is on the `FORBIDDEN_PHRASES` list in
   `scripts/maintenance/efc_verify.py`, but check C3 scans only the HTML
   ledger, so `efc_relevance` strings are unenforced. This is the most
   actionable defect in this list: the rule exists, the phrase is already
   banned, and only the scope of the check is missing. Extending C3 to cover
   `external_research_watch.json` would close it — and whoever does so must
   reword these two strings in the same change, or the extended check fails on
   its first run.

   **This concerns wording, not the strength of either result.** Neither entry
   is being called weak; §1.9 is a language rule, and it binds hardest exactly
   where the evidence is strongest, because a weak result never tempts anyone
   to write `validates`. The stronger the finding, the more it is worth stating
   in a form a hostile reader cannot discount on a threshold argument — and
   where a prediction was pre-registered, citing the prior EFC DOI in the same
   sentence carries more weight than any verb could.

---

## 5. Relevance and quality assessment *[new]*

Two separate axes. Collapsing them is how a loud irrelevant paper outranks a
quiet decisive one.

**Relevance** — does this touch EFC at all?

| Level | Meaning |
|---|---|
| `decisive` | bears directly on a kill criterion or a sealed prediction |
| `constraining` | narrows a parameter, regime, or gap already tracked |
| `contextual` | same subject area, no direct consequence |
| `none` | drop; do not log |

**Evidence quality** — how much weight can the claim carry?

| Level | Meaning |
|---|---|
| `peer-reviewed` | published, DOI, peer review verified |
| `preprint` | arXiv or equivalent; explicitly not peer-reviewed |
| `data-release` | survey or collaboration release with documentation |
| `secondary` | press release, news, commentary |

Keyword matching may propose a candidate. It must not decide either axis.
An item scoring `decisive` on relevance and `secondary` on quality is a
research task, not a publishable claim.

---

## 6. Deduplication and lifecycle *[new]*

Deduplicate on `key`, in this precedence: DOI → arXiv ID → canonical URL →
content hash of title plus abstract. The existing watchlist uses `key` alone;
the remaining fallbacks matter when the same result appears as preprint and
then as journal article under a different identifier. Those two are the **same
item** and must be merged, with the DOI becoming the key and the arXiv ID
retained as an alias.

The file's own `schema` block already declares five statuses:
`new | logged | actioned | superseded | framework-logged`. Three are in use
(`new` 71, `framework-logged` 34, `logged` 1). The gap is not vocabulary but
the absence of a transition between being seen and being dealt with.

Proposed lifecycle, extending the declared vocabulary rather than replacing
it:

```
new → assessed → { actioned | held | rejected | superseded }
```

- `assessed` — **new status**; relevance and quality assigned by a human or a
  reviewed run
- `logged` — existing; retained as a synonym for `assessed` where already set
- `actioned` — existing; the stated `ledger_action` has been carried out
- `superseded` — existing; replaced by a later item, which is named
- `held` — **new status**; real but blocked, with the reason recorded
- `rejected` — **new status**; assessed and found not relevant, kept so it is
  not rediscovered

`framework-seminal` items carry `framework-logged` and are historical rather
than newly discovered. This lifecycle does not apply to them; see §13 for
whether they belong under this policy at all.

`rejected` and `superseded` items are never deleted. Deleting them re-opens
them to rediscovery on the next scan.

---

## 7. Time semantics *[recovered, mapped to existing fields]*

Three distinct times, of which the watchlist currently models two:

| Concept | Watchlist field | Meaning |
|---|---|---|
| retrieval | `date_seen` | when the agent first logged it |
| publication | `date_published` | when the source published it |
| occurrence | *absent* | when the described event happened |

`date_seen` is provenance, not evidence. It must never be rendered as the date
of a result. Where a data release describes an observation campaign, the
occurrence time differs from both and should be stated in prose rather than
silently conflated with `date_published`.

---

## 8. Uncertainty and conflict *[new]*

An item is held, not published, when any of the following holds: sources
disagree on a material figure; required metadata is missing; the work is
retracted, or flagged as under correction; relevance cannot be established
without domain judgement; or the only available source is `secondary`.

Where two sources conflict and both are credible, the conflict itself is the
finding. Record both with their identifiers. Do not average them, and do not
silently pick the one that better fits EFC — that is the failure mode this
rule exists to prevent.

---

## 9. Fail-closed publication loop *[recovered, specified]*

```
scan → dedupe → assess → propose (dry-run artefact)
     → human review → manual integration in a reviewed pull request
```

Properties this loop must have:

- Default mode is dry-run. Publication mode is **absent**, not merely disabled.
- The agent never edits `docs/public/` HTML directly. It emits a proposal; a
  human integrates it.
- Any error from a source — network, parse, or schema — marks the run
  incomplete. An incomplete run is not a publishable run.
- A run that produces nothing is a successful run. Absence of findings is
  reported as absence, never as a positive result.
- The workflow holds read-only repository permissions. Write permission is
  not granted as a shortcut around review.

---

## 10. Provenance and manifest *[new]*

Every run emits an append-only manifest recording: run identifier, commit SHA,
start and end time in UTC, each source URL with its HTTP status, counts of
items found, deduplicated, assessed, and proposed, every error encountered,
and the policy version under which the run executed.

Manifests are never rewritten. A corrected run is a new manifest that
references the one it supersedes. Deleting a manifest to hide a failed or
rejected source is a policy violation.

---

## 11. Metadata schema *[recovered intent, expressed in the existing format]*

Extending the current watchlist item rather than replacing it. Fields marked
**new** do not exist in version 1.8 of the file.

```json
{
  "key": "arXiv:2503.14738",
  "title": "DESI DR2 Results II: BAO Measurements and Cosmological Constraints",
  "source_type": "paper",
  "url": "https://arxiv.org/abs/2503.14738",
  "date_seen": "2026-04-17",
  "date_published": "2025-03-19",
  "efc_relevance": "2.3σ ΛCDM tension, 3.1σ preference for w0wa; supports EFC L2→L3 regime transition and WP4 T(S).",
  "ledger_action": "Add L2 row to Validation Ledger; update gap theory-background-hz-modification to 'decision-ready'.",
  "status": "new",

  "aliases": ["DOI:10.1088/1475-7516/2025/xx/xxx"],
  "relevance": "constraining",
  "evidence_quality": "preprint",
  "content_hash": "sha256:…",
  "retrieved_by": "research-watch-delta",
  "policy_version": "1.0",
  "uncertainty": null
}
```

`aliases`, `relevance`, `evidence_quality`, `content_hash`, `retrieved_by`,
`policy_version`, and `uncertainty` are **new**. Adding them is backward
compatible: existing consumers ignore unknown keys, and the nine existing
fields keep their meaning. A tenth, `framework_category`, appears on the 34
`framework-seminal` items and is unchanged by this policy.

**The `efc_relevance` value above is reproduced verbatim from the live file,
including the word `supports`.** By §1.9 it should read `consistent with`. It
is quoted unaltered rather than silently corrected, because a policy document
that conforms its own evidence to its own rule is doing the thing §8 forbids.
See §4.6.

---

## 12. Acceptance criteria *[recovered intent, made testable]*

A single update is acceptable when all of the following can be demonstrated:

1. Re-running the scan with unchanged inputs produces no new items
   (idempotence on `key`).
2. Every proposed item has a resolvable canonical URL and a `date_published`.
3. No proposed item's `key` or alias already exists in the watchlist.
4. `docs/public/` is byte-identical before and after a dry-run.
5. A source that returns an error appears in the manifest and does not appear
   as a proposal.
6. No credential, token, or private memory text appears in any output.
7. No external item has been written to
   `docs/validation-ledger/data/evidence-register.json` or
   `docs/validation-ledger/data/ledger.json`. These two files are named
   because they are what `AGENTS.md` names and what `efc_verify.py` checks;
   the wider `data/*.json` glob also covers generated dumps such as
   `atlas.json` and `tests.json`, which would make the criterion untestable.
8. No generated prose contains `confirms EFC` or equivalent.

Criteria 7 and 8 are the ones specific to this repository. They are also the
ones an agent is most likely to breach while believing it is being helpful.

---

## 13. Open questions

These require a decision by the repository owner and are not settled here:

- Should the delta scan remain a human-pasted prompt, or become a scheduled
  workflow? This policy is written to hold in either case.
- Who assigns `relevance` and `evidence_quality` — a reviewed agent run, or a
  human? §5 forbids keyword matching from deciding, but does not say who does.
- Should `framework-seminal` items, which are historical rather than new
  findings, be governed by this policy at all, or split into their own
  register?

---

## References

[^1]: Crossref REST API — work metadata lookup and filtering.
    <https://api.crossref.org/> · <https://www.crossref.org/documentation/retrieve-metadata/rest-api/>
[^2]: OpenAlex API — catalogue for discovery, relations, and search.
    <https://docs.openalex.org/>
[^3]: arXiv API — Atom-based interface for preprint metadata.
    <https://info.arxiv.org/help/api/index.html>
[^4]: NIST AI Risk Management Framework, Generative AI Profile (NIST AI 600-1)
    — provenance, source citation, and human oversight.
    <https://doi.org/10.6028/NIST.AI.600-1>

> The recovered draft cited these four sources by footnote marker, but its
> reference list was in the lost portion. The URLs above were supplied when
> this version was written; they are not recovered text, and each should be
> checked with a `retrieved_at` when this policy is first enforced — which is
> precisely what rule 1.1 demands of everything else.
