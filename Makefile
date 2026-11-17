# EFC — kunnskapslivssyklusen, fase 1
#
# PYTHON: which interpreter runs the checks. The default is `python3`, which
# is right in CI (where the dependencies are installed into it). On a
# workstation `python3` is often a bare system interpreter WITHOUT
# pytest/numpy, and then the bridge sync stops on the import of the test
# modules that own the canonical parameters. Measured 2026-09-18
# (t_2bc25575): the line below carried a comment saying "run with the test
# venv" while the line itself called `python3` — so `make check` could not be
# run as written. Override instead of guessing a path:
#
#   make check PYTHON=/opt/venvs/<id>/bin/python
PYTHON ?= python3

install:
	uv sync --frozen --extra verify

check:
	$(PYTHON) scripts/maintenance/statement_graph_check.py
	$(PYTHON) scripts/maintenance/validate_activity_log.py
	$(PYTHON) scripts/maintenance/validate_risk_register.py
	$(PYTHON) scripts/maintenance/verifier_bench.py
# The language rule, in DEFAULT mode: the whole tree against the committed
# record. CI can only run the change-relative mode (--referanse), because a PR
# must not be blamed for its base branch -- so this line is the only runner the
# ratchet has. Measured 2026-09-19 (t_aad5f41e): without it the record was
# written once and never compared, and the tree grew 1 212 hits past it.
	$(PYTHON) scripts/maintenance/efc_spraakvakt.py
# The bridge sync reads the CANONICAL parameters from the test modules (one
# source for test and sync), and those modules import numpy/pytest (see
# PYTHON above).
	$(PYTHON) scripts/maintenance/efc_bro_synk.py --sjekk

inntak-dry:
	$(PYTHON) scripts/maintenance/efc_inntak.py --dry-run

inntak:
	$(PYTHON) scripts/maintenance/efc_inntak.py

# The measurement, and everything DERIVED from it, as ONE step: the snapshot
# and both axes of schema/atlas_dekning.json (domains and sources) come from
# one reading of the bus. The check afterwards reads the WORKING TREE and
# exits non-zero when the source axis still deviates — a position the
# measurement cannot take (a new shared source without a reason, say) must
# trip here rather than be discovered by CI later. Needs the bus key on the
# door that runs it, and it is a READ of the bus: nothing is published.
#   make maal            # measure, derive, verify
#   make maal PYTHON=python3
maal:
	$(PYTHON) scripts/atlas_volum.py --maal
	$(PYTHON) scripts/atlas_kilder.py --sjekk --ref .

full-check: check
	$(PYTHON) scripts/maintenance/validate_repo.py
	$(PYTHON) scripts/maintenance/validate_links.py --maks-eksterne 15

runde:
	$(PYTHON) scripts/maintenance/vedlikeholdsrunde.py

blast:
	$(PYTHON) scripts/maintenance/blast_radius.py --diff origin/main --gate

# Cross-node change picture (REPORTING, not a gate). exit 2 = drift found
# (work to do, not an error); exit 3 = telemetry unavailable. Reads git
# clones, kanban, arbeidsminne, figshare/ORCID — the stores full-check cannot
# see (full-check only scans this working tree). Deliberately NOT in
# full-check: drift here is often cross-door (another door's working memory)
# and not this repo's to fix; it belongs in the report, not the gate.
node-check:
	$(PYTHON) scripts/maintenance/efc_node_triangulate.py

# Autonomous self-validating loop (OBSERVE -> DECIDE -> ACT). Runs the picture,
# auto-fixes ONLY own-clone lag (ff-only, verified, fail-closed), escalates the
# rest. --strict makes it a gate (exit 2 = drift, exit 3 = unknown); without it
# the script exits 0 and reports drift in stdout (for the no_agent cron, where
# a non-zero exit would read as "script failed").
self-heal:
	$(PYTHON) scripts/maintenance/efc_selfheal.py --strict

# PR-triage: classify open PRs; auto-act is ONLY the reversible CLOSE of
# DEAD (stale point-in-time drafts) + SUPERSEDED (already merged elsewhere).
# Everything else escalates (no auto-merge, per second opinion 0.94).
# --torr reports (default); --utfoer performs the closes.
pr-triage:
	$(PYTHON) scripts/maintenance/efc_pr_triage.py
