# Rollback and recovery

## Repository
No production effects arise from the branch. Revert the task commit or close the PR if tests/review fail. Do not force-push protected branches. Verify branch/PR and clean worktree after rollback.

## Bank configuration (only after owner approval)
The script must create a unique full-config backup before any write. On failed readback, stop before directives/pages; restore only affected config fields from that exact backup using the supported config API, then GET the full config and compare it with the backup. Record the backup path and evidence in this file and on the task. Never guess values.

## Historical memories
No historical memories change in this scope. Do not attempt rollback by reprocessing: that endpoint deletes old memory units before extraction. Any future migration needs its own ADR, snapshot/clone, deterministic mapping, per-record before/after readback, and tested restoration plan.

**Actual rollback handle/result:** pending; no mutation has occurred.
