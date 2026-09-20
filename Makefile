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
	uv sync --frozen

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

full-check: check
	$(PYTHON) scripts/maintenance/validate_repo.py
	$(PYTHON) scripts/maintenance/validate_links.py --maks-eksterne 15

runde:
	$(PYTHON) scripts/maintenance/vedlikeholdsrunde.py

blast:
	$(PYTHON) scripts/maintenance/blast_radius.py --diff origin/main --gate
