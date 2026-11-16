# Rollback

The layer is **read-only with respect to existing claims and gates**. It computes confidence and escalation; it never mutates a claim, never merges, never publishes, and never removes an existing human gate.

Rollback is therefore simple and complete: delete `scripts/maintenance/efc_triangulate.py`, the `data/triangulation/` records, and any wiring added to the figshare-presence workflow. Nothing else is touched, so no other component regresses.

If the layer were ever wired to *auto-accept* a claim that later proves wrong, the recovery is: the underlying claim already carries its source list (auditability rule), so the wrong auto-accept can be traced to its sources and reversed by removing the offending source from the record — a data edit, not a code revert.
