# EFC public-agent V1

This workflow is deliberately review-only. It reads explicit JSON records and
produces a deterministic plan; it does not edit `docs/public`, call GitHub,
push, merge, publish, or delete anything.

## Local use

```sh
python3 scripts/efc_public_agent.py --mode dry-run
python3 scripts/efc_public_agent.py --mode pr
```

`dry-run` writes nothing. `pr` writes only the fixed allowlisted directory
`reports/efc-public-agent/`; the name means PR-oriented artifacts, not automatic
PR creation. A maintainer must review and apply any public-page change.

The agent fails closed when configuration, sources, record identity, operation,
permissions, or target safety is ambiguous. Targets must be existing EFC public
HTML paths in the input, while output is kept outside `docs/public`.

Each source record may include a non-empty `citations` list. If omitted, the
source JSON path is recorded as the citation. This makes every proposal
traceable without treating source text as executable instructions. Opus is an
explicit adapter boundary, selected with `EFC_OPUS_ADAPTER`; V1 accepts only
the default `disabled` value and never makes a network call. `OPUS_API_URL` and
`OPUS_API_KEY` are reserved for a future adapter and are never logged.

Set `EFC_LOG_LEVEL=INFO` for bounded run logging. Logs contain mode, repository,
record count, and plan hash only; errors are written to stderr and no partial
report is created before all validation succeeds.
