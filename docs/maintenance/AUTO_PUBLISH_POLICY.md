# EFC automatic publication policy

**Status:** active policy draft — applies to scheduled EFC maintenance only
**Owner:** Morten/Joakim decision authority; cron agents implement gates
**Kanban control:** `t_79d0e6e3`

## Purpose

Allow automatic publication of low-risk, provenance-backed maintenance while preventing claim inflation, accidental overwrites, and publication of unverified science.

Automatic publication means a verified maintenance change may be committed and delivered through the configured repository/publication path. It does not mean that an agent may promote a hypothesis to confirmation or bypass repository governance.

## Publication tiers

### Tier A — automatic publication allowed

Only deterministic, reversible changes are eligible:

- DOI/ORCID/Figshare identity correction verified by at least two source checks;
- generated counts, indexes, changelog entries, navigation blocks, or link repairs;
- explicit role/provenance labels for already-existing artifacts;
- correction of a known parser/status mapping without changing scientific meaning;
- bounded wording that lowers or clarifies epistemic status.

Required gates:

1. isolated worktree or cleanly attributable diff;
2. no unrelated dirty files included;
3. source → schema → validator/generator → output path is known;
4. `efc_cross_validate.py` has 0 errors;
5. `efc_verify.py`, ledger schema, narrative/page/root/navbar checks pass;
6. JSON and HTML parse successfully and local-link check has 0 broken links;
7. `git diff --check` passes;
8. rollback commit/diff is recorded;
9. exact target read-back after publication succeeds;
10. changelog/provenance entry is generated where required.

### Tier B — automatic publication allowed after adjudication

A public status or external-evidence update may be published automatically only when the adjudicator packet contains:

- canonical source, DOI/URL, retrieval date, and source type;
- observable, dataset, method, uncertainty, competing explanation and falsifier;
- global-local/systemic-empathy map: local anchor, affected systems, scale/regime transfer, local/global significance, feedback/externalities, next test;
- explicit status: `relevant_dataset_only`, `external_constraint`, `partial_support`, `consistent_with`, `refutation/weakening`, or `unknown`;
- no `confirmed`/`proves EFC`/`confirms EFC` language unless separately human-approved;
- matched baseline, nuisance model, covariance and holdout status where relevant;
- no unresolved contradiction between ledger, public HTML and source packet.

Tier B may update public status pages and the ledger, but may not silently change parameters, historical results, model equations or branch definitions.

### Tier C — human approval required

Never auto-publish:

- a new physical equation, model parameter, transition or regime;
- a new `parameters.json` without an entailed source/schema/generator path;
- an upgrade to `confirmed`, `validated`, `proven`, or equivalent;
- a new falsification or removal of a falsification;
- a merge of ledger roles or schema versions;
- publication from a dirty or unattributable worktree;
- a change whose rollback or target read-back cannot be verified.

## Dirty-state and delivery rules

- Never publish directly from `/root/efc-current` when the working tree is dirty.
- Before any remote publication, verify the Hermes publishing key surface (`mcp__efc_publisering__efc_noekler`) without exposing values. `GITHUB_TOKEN: satt` is necessary evidence that the publisher can try, not proof that the token is valid; verify write access by the actual Hermes publishing mechanism.
- Docker/container shell visibility must never override a positive Hermes publisher auth result.
- Missing auth at the actual Hermes publisher boundary is `CAPABILITY_BLOCKED`; missing auth only in a container shell is `not_visible_from_container`.
- Build a clean release candidate from `origin/main` (for example `/root/efc-release`) and copy/apply only the verified allowlisted diff.
- Run all gates in the release candidate, commit the candidate, and record the commit hash before any publication attempt.
- A gateway/bot-chat delivery failure is not a repository publication failure. Preserve the report locally, retry only through the scheduler, and report the delivery blocker separately.
- Never restart or kill a gateway while an active CLI/session owner is present. Escalate the restart as a human-gated runtime action.
- Never start a second run of a job already marked running; consume its result instead.

Every automatic publication attempt must report:

```text
policy_tier: A | B | C
changed_files:
source_provenance:
gates:
rollback:
publication_target:
readback:
unpublished_claims:
blockers:
```

If any required gate fails, the agent must not publish. It must report `BLOCK` with the exact failed gate and preserve the working diff for review.
