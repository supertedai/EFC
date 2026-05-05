#!/usr/bin/env python3
"""EFC sealed-prediction immutability guard.

Manages a top-level ``.seal-manifest.json`` that records SHA-256 hashes of
the artefacts that comprise an EFC pre-registration. The intent is research
integrity: once a prediction is sealed (e.g. Euclid DR1 benchmark for
October 2026), any later modification to the underlying file must be either
an explicit re-seal (committed alongside an updated manifest and a roadmap
entry explaining why) or a CI failure.

Operating modes
---------------
``--init``
    Build a manifest from current state. Refuses to overwrite an existing
    manifest unless ``--force`` is also supplied. Use this exactly once at
    the moment you decide which files are sealed.

``--verify``  (default)
    Read the manifest and confirm each listed file's current SHA-256 still
    matches what was recorded. Exit 0 = clean, 2 = mismatch, 3 = manifest
    or sealed file missing.

``--list``
    Show the manifest in human-readable form.

Sealed artefacts (current set)
------------------------------
* ``pipelines/efc/euclid_dr1/data/benchmark.json``
* ``pipelines/efc/euclid_dr1/data/parameter_scan.json``
* ``pipelines/efc/euclid_dr1/data/frozen_prediction_hash.json``

Provenance note
---------------
``frozen_prediction_hash.json`` already records a SHA-256 from 2026-04-12
that does *not* match the current bytes of ``benchmark.json`` under standard
canonicalisations. This manifest is therefore a *forward-looking* guard:
it locks state from manifest-creation onward. Reconciling the historical
2026-04-12 claim with current bytes is a separate research-integrity task
and is *not* in scope for the guard.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ".seal-manifest.json"

# Files whose immutability we guard. Add to this list only via an explicit
# re-seal commit; never trim it without a roadmap entry explaining why a
# prediction is being un-sealed.
SEALED_PATHS = (
    "pipelines/efc/euclid_dr1/data/benchmark.json",
    "pipelines/efc/euclid_dr1/data/parameter_scan.json",
    "pipelines/efc/euclid_dr1/data/frozen_prediction_hash.json",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest() -> dict:
    entries = []
    for rel in SEALED_PATHS:
        p = REPO_ROOT / rel
        if not p.exists():
            raise SystemExit(f"[seal] sealed file missing on init: {rel}")
        entries.append(
            {
                "path": rel,
                "sha256": sha256(p),
                "bytes": p.stat().st_size,
            }
        )
    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": (
            "Forward-looking immutability guard. Any change to a listed file"
            " must be accompanied by an explicit re-seal: update this manifest"
            " in the same commit and add a Validation Ledger v-bump entry"
            " documenting the re-seal. Unannounced changes will fail CI."
        ),
        "entries": entries,
    }


def cmd_init(force: bool) -> int:
    if MANIFEST.exists() and not force:
        print(
            f"[seal] {MANIFEST.relative_to(REPO_ROOT)} already exists;"
            f" use --force to overwrite (requires explicit re-seal commit)"
        )
        return 1
    payload = build_manifest()
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"[seal] wrote {MANIFEST.relative_to(REPO_ROOT)} —"
        f" {len(payload['entries'])} entries"
    )
    for e in payload["entries"]:
        print(f"  {e['path']}: {e['sha256'][:16]}… ({e['bytes']} bytes)")
    return 0


def cmd_verify() -> int:
    if not MANIFEST.exists():
        print(
            f"[seal] manifest missing: {MANIFEST.relative_to(REPO_ROOT)}."
            f" Run --init once to bootstrap."
        )
        return 3
    manifest = json.loads(MANIFEST.read_text())
    failures: list[tuple[str, str, str]] = []
    missing: list[str] = []
    for e in manifest.get("entries", []):
        rel = e["path"]
        expected = e["sha256"]
        p = REPO_ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        actual = sha256(p)
        if actual != expected:
            failures.append((rel, expected, actual))
    if missing:
        print("[seal] FAIL — sealed files missing:")
        for rel in missing:
            print(f"  {rel}")
    if failures:
        print(
            f"[seal] FAIL — {len(failures)} sealed file(s) modified without re-seal:"
        )
        for rel, exp, act in failures:
            print(f"  {rel}")
            print(f"    expected: {exp}")
            print(f"    actual:   {act}")
        print(
            "\nTo re-seal (research-integrity-affecting):"
            "\n  1. Document the change in the Validation Ledger as a v-bump."
            "\n  2. Run: python3 scripts/maintenance/efc_seal_manifest.py --init --force"
            "\n  3. Commit the manifest update alongside the file change."
        )
    if missing or failures:
        return 2
    print(
        f"[seal] OK — {len(manifest['entries'])} sealed file(s) match manifest."
    )
    return 0


def cmd_list() -> int:
    if not MANIFEST.exists():
        print(f"[seal] manifest missing: {MANIFEST.relative_to(REPO_ROOT)}")
        return 3
    manifest = json.loads(MANIFEST.read_text())
    print(f"version:      {manifest.get('version')}")
    print(f"generated_at: {manifest.get('generated_at')}")
    print(f"policy:       {manifest.get('policy')}")
    print(f"entries ({len(manifest.get('entries', []))}):")
    for e in manifest.get("entries", []):
        print(f"  {e['path']}")
        print(f"    sha256: {e['sha256']}")
        print(f"    bytes:  {e['bytes']}")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EFC sealed-prediction guard")
    p.add_argument("--init", action="store_true", help="initialise manifest from current state")
    p.add_argument("--force", action="store_true", help="allow --init to overwrite existing manifest")
    p.add_argument("--verify", action="store_true", help="verify current state against manifest (default)")
    p.add_argument("--list", action="store_true", help="show manifest contents")
    args = p.parse_args(list(argv) if argv is not None else None)

    if args.init:
        return cmd_init(force=args.force)
    if args.list:
        return cmd_list()
    return cmd_verify()


if __name__ == "__main__":
    sys.exit(main())
