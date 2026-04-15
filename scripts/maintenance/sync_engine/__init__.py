"""
EFC Sync Engine

Event-driven, fixpoint-converging repo synchronisation.

Three registries drive the engine:

  * handlers/    — one per change type (T1_NEW_PAPER, T13_DRIFT_FIX, …)
  * invariants/  — one per cross-check (version consistency, DOI integrity, …)
  * derived/     — regenerators that rebuild consumer files from canonical sources

The orchestrator (efc_full_sync.py) wires them together:

    classify_diff → propagate via handlers → regenerate derived → verify
                                                       ↑              ↓
                                                       └── loop until fixpoint

See docs/architecture/sync_engine.md (TBD) for the full algorithm spec.
"""
from __future__ import annotations

__version__ = "1.0.0"
