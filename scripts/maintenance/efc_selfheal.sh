#!/bin/bash
# Wrapper for the EFC self-heal loop — the no_agent cron's `script`.
# Git-tracked copy (durable across Hermes updates). stdout is delivered
# verbatim (empty = silent); stderr is for manual runs.
exec python3 "$(dirname "$0")/efc_selfheal.py"
