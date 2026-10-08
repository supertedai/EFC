# Context and baseline

## Canonical source

- Repository: `https://github.com/supertedai/EFC.git`
- Base: `origin/main` / `52ba3222dbd0672ceedb50c5dbec38f11a4b5168`
- Isolated worktree: `/opt/agent-work/EFC/.worktrees/atlas-settlement-state-20261008`
- The claimed worktree now contains changes only in `scripts/atlas_lesing.py`, `tests/test_atlas_oppslag.py`, and this ADR package. No atlas node, prediction, physics engine, generated public surface, or live bus was changed.

## Reproduction

On the baseline, `scripts/atlas_lesing.py:finn()` sets `har_oppgjoer` from mere presence of `node["settlement"]` (line 501); the CLI prints `is settled` whenever that flag is true (lines 2249–2250). Running:

```text
/opt/venvs/t_123ed6d9/bin/python scripts/atlas_lesing.py . --emne efc.growth_engine --alle --ref HEAD
```

prints the `efc.growth_engine` hit with `has prediction · is settled`.

The static `efc.growth_engine`, `obs.fsigma8`, and `obs.bao` records have `settlement.outcome = "waiting for arbiter: DESI DR2 full-shape"`; the growth node lacks `outcome_time` and `settlement_version`, and its `settlement_result` is `null`.

The former completed-example `kosmos.asteroider` has a full-looking static result, but its prediction correlation is `jpl-sentry.29075` while the settlement correlation is `jpl-sentry.2026 RO10`. The schema describes correlation as the stable key shared by prediction and settlement. It will therefore remain a visible `record_only`/unverified record; no atlas data are changed. `verden.vaer` is used as the completed static exemplar because its prediction and settlement correlations match.

## Independent runtime read

The live `VERDEN_PROGNOSE` record for `kosmos.kosmologi.prediksjon.efc-fs8` is sequence 31058, timestamp 2026-09-07T15:00:05Z. Its headers say `arbiter=nei`, `arbiter_venter_paa=DESI DR2 full-shape`, and preserve the sealed criterion. The queried `kosmos.kosmologi.oppgjoer.efc-fs8` subject returned no message. The latest sampled baseline state messages are older survey measurements, not the named arbiter. This supports “pending”, not a test outcome or failure.

The `efc:EFC` concept registered without a regime-node is explicitly an intended namespace-only hit in `references/efc-atlas.md`; it is not part of this change. The `efc.growth_engine` node itself discloses that its current Variant A has no μ channel; that model-variant question is not altered here.