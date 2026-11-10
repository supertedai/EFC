# 04 — Plan (ordered; dependencies in brackets)

Every step runs inside `/opt/agent-work/EFC/.worktrees/t_1610348d` on branch
`wt/t_1610348d`, based on `origin/main @ d527af74`. The shared checkout and the other
pre-provisioned worktree are never edited.

1. **Baseline** [done] — record HEAD/merge-base/status; run the required suite and the
   bridge/schema gates; record results (`01-context.md`).
2. **ADR package** [done before any source edit] — `00`–`08`.
3. **RED** — write `tests/test_atlas_bro_status.py` and run it alone. It must fail, and it
   must fail on the *content* assertions (not on a crash/import error). Record the exact
   failure.
4. **GREEN** — edit `schema/regime_nodes.jsonld` with a script that (a) loads the bank,
   (b) appends the two provenance entries and one revision entry, (c) writes back with the
   file's declared format (`json.dumps(indent=2, ensure_ascii=False)` + trailing newline,
   verified byte-identical round-trip before the edit), so the diff is exactly the intended
   lines.
5. **Validate immediately** — `json.load`, then validate the instance against
   `schema/regime_node.schema.json` with `jsonschema`; confirm the round-trip format is
   still exact (`efc_bro_synk.py --sjekk` is the format guard).
6. **Re-run the test** — must pass.
7. **Regenerate derived artifacts** — `efc_atlas_generator.py`, then
   `doi_coverage_register.py`; inspect `git diff` against the predictions in
   `03-decision.md` §4. Stop and report on any deviation.
8. **Changelog projection** — run `changelog_projeksjon.py` (twice, to prove idempotence),
   inspect the produced row, and commit both `changelog.json` and `EFC_Changelog.html` if
   the projection demands a row.
9. **Gates** — required suite; `efc_bro_synk --sjekk`; `efc_schema_check.py`;
   `validate_repo.py`; `validate_ownership.py`; `statement_graph_check.py`;
   `efc_page_consistency.py`; `efc_narrative_consistency.py`; `efc_navbar_sync.py --check`;
   `efc_spraakvakt.py`; atlas generator determinism (run twice, compare sha256).
10. **Commit** — one descriptive English subject; the diff reviewed line by line.
11. **Independent review** — a distinct reviewer session receives the ADR package, the
    diff, the acceptance criteria and the known risks; findings dispositioned in
    `06-review.md`. The implementer does not approve its own change.
12. **Rebase + re-gate** — rebase onto current `origin/main`, rerun step 9, then push the
    branch and open a PR against `supertedai/EFC`. Read back head/base/state/checks and
    copy the exact values into `08-closeout.md` and the card.
13. **Closeout** — `08-closeout.md` with observed results, deviations, residual unknowns
    and rollback handle; card updated; no merge, no publish.

## Rollback handles (see `07-rollback.md`)

- Before push: `git checkout -- <paths>` / `git reset --hard d527af74`.
- After push: revert commit(s) on the branch, or close the PR; nothing is merged, so
  `origin/main` is never in a changed state.
