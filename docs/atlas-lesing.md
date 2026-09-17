# Reading the atlas — which copy is authoritative

**Rule: read the atlas from `git:origin/main` in the clone. Never from a
working tree.**

## Why this is written down

The atlas exists in several working copies, and they do not show the same
map. Measured 2026-09-17:

| Copy | Nodes | Problem |
|---|---|---|
| `/opt/agent-work/EFC` (working tree) | 72 | six PRs behind `origin/main` |
| `/home/morten/EFC-review` (`pr-463`) | 82 | a PR branch that was later merged |
| `.worktrees/vedlikehold` | 45 | missing the `perspektiv` field entirely |

A copy that answers reads as a live atlas. On 2026-09-17, the figure
"82 atlas nodes" reported in the *Atlas, NATS and motorer* thread came from
a PR branch, not from `main` — and a guard built on the working tree
reported 72 while `main` had 82.

This is the same failure mode as 2026-09-16 (atlas sync pointing at
components that did not run) and 2026-09-14 (memory available but not
steering): **the artifact exists and responds — so it reads as truth.**

## The rule, concretely

```bash
# Right — the ref, not the checkout
git -C /opt/agent-work/EFC show origin/main:schema/regime_nodes.jsonld

# Wrong — whatever the working tree happens to contain
cat /opt/agent-work/EFC/schema/regime_nodes.jsonld
```

Any tool that reads the atlas must name the ref it read, so a stale copy is
visible in the output rather than in the reader's assumption.
`metrikk/atlasoppgjoer.py` does this: it reports `git:origin/main` as its
source, and a test requires exactly that string — a default of `HEAD` is
killed by mutation 7.

## The other copies

Every other copy of the atlas is a **working copy** and must not be read as
the atlas. They exist for editing, not for answering.

Measured on the authoritative ref 2026-09-17 (`b0d0d17c`): **82 nodes,
19 engines, `perspektiv` set on all 82** (48 paradigm / 23 consensus /
11 academia).
