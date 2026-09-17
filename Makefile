# EFC — kunnskapslivssyklusen, fase 1
install:
	uv sync --frozen

check:
	python3 scripts/maintenance/statement_graph_check.py
	python3 scripts/maintenance/validate_activity_log.py
	python3 scripts/maintenance/verifier_bench.py

inntak-dry:
	python3 scripts/maintenance/efc_inntak.py --dry-run

inntak:
	python3 scripts/maintenance/efc_inntak.py

full-check: check
	python3 scripts/maintenance/validate_repo.py
	python3 scripts/maintenance/validate_links.py --maks-eksterne 15

runde:
	python3 scripts/maintenance/vedlikeholdsrunde.py
