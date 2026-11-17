#!/bin/bash
# Wrapper for the EFC self-heal loop — the no_agent cron's `script`.
# This file is the RESTORATION TEMPLATE: copy it to
# ~/.hermes/profiles/researcher/scripts/efc_selfheal.sh after a profile wipe.
# It resolves the .py by ABSOLUTE repo path (the cron runs it from the profile
# scripts/ dir, where the .py is NOT adjacent). stdout is delivered verbatim
# (empty = silent); stderr is for manual runs.
exec python3 /home/morten/EFC/scripts/maintenance/efc_selfheal.py "$@"
