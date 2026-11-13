# Implementation plan

1. Keep Kanban claim/lease and isolated worktree; baseline is `origin/main` at the merged #653 commit.
2. Add focused unittest cases first and run RED: new-only and legacy-only SDK methods; unknown-client refusal; HTTP 200/204 followed by GET/readback; 4xx refusal; mismatched readback stops before directive/page writes.
3. Implement the minimal method resolver and 2xx/readback behavior.
4. Add mission-extension merging with idempotence test; preserve original bank text and explicit replacement behavior.
5. Update spec and README with measured client/server versions, axis distinctions, compatibility behavior, and destructive reprocessing caveat.
6. Run focused tests, relevant EFC suite with canonical venv if present, syntax/JSON checks, repo gates, diff/security scan.
7. Request independent review/second opinion; resolve findings in a fresh round. Do not self-approve.
8. Commit with `Aktør: faber` and `Oppgave: t_c9dbf0a2`; push only `wt/efc-hindsight-followup`, open/read back PR and exact-head checks.
9. Stop before merge or live bank writes pending explicit human gate. If authorized after merge: create fresh config backup, apply only mission additions, read back exact missions/config, verify dry-run idempotence; do not mutate history.
10. Close ADR/task only with observed PR and bank outcomes; keep history migration as a separately scoped item.
