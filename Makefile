# EFC — kunnskapslivssyklusen, fase 1
install:
	uv sync --frozen

check:
	python3 scripts/maintenance/statement_graph_check.py
	python3 scripts/maintenance/validate_activity_log.py
	python3 scripts/maintenance/validate_risk_register.py
	python3 scripts/maintenance/verifier_bench.py
# Bro-synken leser de KANONISKE parametrene fra testmodulene (én kilde for
# test og synk), og de modulene importerer numpy/pytest. Kjor denne linja
# med testvenv-en (f.eks. /opt/venvs/t_123ed6d9/bin/python), ikke en bar
# python3 — ellers stopper den paa importen og sier hvilken modul som mangler.
	python3 scripts/maintenance/efc_bro_synk.py --sjekk

inntak-dry:
	python3 scripts/maintenance/efc_inntak.py --dry-run

inntak:
	python3 scripts/maintenance/efc_inntak.py

full-check: check
	python3 scripts/maintenance/validate_repo.py
	python3 scripts/maintenance/validate_links.py --maks-eksterne 15

runde:
	python3 scripts/maintenance/vedlikeholdsrunde.py

blast:
	python3 scripts/maintenance/blast_radius.py --diff origin/main --gate
