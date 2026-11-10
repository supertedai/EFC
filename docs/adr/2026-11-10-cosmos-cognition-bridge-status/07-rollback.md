# 07 — Rollback

Nothing in this change is irreversible. It touches no credential, no scheduler, no
external service, and — by mandate — is never merged by the implementer.

## Triggers

Roll back if any of the following is observed:

- the schema rejects the edited node (`additionalProperties: false` violation);
- an existing test outside the added one goes red (regression);
- `doi_coverage_pending.json` **loses** an item, or a `disposition` moves away from
  `changelog_only` for any of the four cited DOIs (a silent backlog drain);
- `efc_bro_synk.py --sjekk` reports a deviation or a format change;
- the reviewer finds that the wording asserts establishment the sources do not support;
- `origin/main` moves in a way that conflicts with these files.

## Procedure

Before push (nothing is published):

```bash
cd /opt/agent-work/EFC/.worktrees/t_1610348d
git checkout -- schema/regime_nodes.jsonld \
    docs/efc-atlas/atlas/data.mjs docs/efc-atlas/INDEKS.md \
    docs/validation-ledger/data/doi_coverage_matrix.json \
    docs/validation-ledger/data/doi_coverage_pending.json \
    docs/validation-ledger/data/doi_coverage_open_findings.json \
    docs/validation-ledger/data/changelog.json docs/public/EFC_Changelog.html
rm tests/test_atlas_bro_status.py
rm -r docs/adr/2026-11-10-cosmos-cognition-bridge-status
git status --porcelain      # must be empty
```

After push, before merge (the PR is the rollback handle):

```bash
git revert <commit>         # on the branch, then push
# or: gh pr close <n> --repo supertedai/EFC
```

`origin/main` is never touched, so no revert on `main` is needed — that is the point of
working in the worktree and stopping at the PR.

## Proof of a clean rollback

`git status --porcelain` empty **and** `git rev-parse HEAD` equal to the recorded baseline
`d527af7423e6cb84faad3223b5c0e97c77e8ec20` (or to the rebased `origin/main` tip, recorded at
push time).

## Owner

Implementer (`researcher`) executes; **Morten** decides whether a rollback is required
after merge-review. The other pre-provisioned worktree and the shared checkout are not
rollback targets — they were never edited.
