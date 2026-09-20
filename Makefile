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
# The bridge sync reads the CANONICAL parameters from the test modules (one
# source for test and sync), and those modules import numpy/pytest (see
# PYTHON above).
	$(PYTHON) scripts/maintenance/efc_bro_synk.py --sjekk
# The sealed atlas experiment (ADR-086 §4). It reads its OWN bank snapshot — a
# commit, not a ref (docs/efc-atlas/eksperiment/bank.py) — so it needs full git
# history, and it cannot be fooled by a moved main. Measured 2026-09-19: the
# path was run by no workflow and no target, so 4 failing tests stood unseen.
	$(MAKE) eksperiment

eksperiment:
	$(PYTHON) -m pytest docs/efc-atlas/eksperiment -q

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
