# Rollback and recovery

## Repository rollback

This branch has no production effect. If the implementation fails numerical tests or review, stop and preserve the raw measurements. Revert only this task's commits on `wt/t_bfded048` or close the PR; do not force-push protected branches or modify `main`. Verify the task worktree and exact branch afterward. The pre-change baseline is origin/main e2e5a6c7.

## Numerical-result rollback

Do not delete prior KT2 outputs or relabel them. Store new runs under a unique run directory with commit/config metadata. If a run has wrong units, source mass or window, mark it invalid in its metadata and rerun; do not overwrite the earlier artifact.

## Runtime/data

No production service, bank, external data source, or live physical system is modified. There is no runtime rollback action.

**Current rollback handle/result:** the implementation commit on `wt/t_bfded048` is local to the isolated source branch and has no runtime effect. If review rejects it, revert that exact branch commit after readback; no rollback or production change has occurred.
