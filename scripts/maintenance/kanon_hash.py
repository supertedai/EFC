#!/usr/bin/env python3
"""kanon_hash.py — THE one canonical hash function for EFC artefacts.

The lock (design §0, honesty rule 2): generator and verifier MUST share
this shape. The specification:
- input: Python object (dict/list/str/int/float/bool/None) loaded from
  YAML/JSON, WITHOUT the content_hash field
- serialisation: json.dumps(obj, sort_keys=True, ensure_ascii=False,
  separators=(",", ":")) — compact separators, no whitespace drift
- Unicode: the text is normalised to NFC BEFORE hashing (macOS NFD junk
  must not give hash collisions across machines)
- numbers: JSON numbers as they are (no trailing-zeros normalisation —
  Python and JavaScript read them alike through json)
- result: "sha256:" + hexdigest

Changes here are a schema CHANGE: bump the version and run verifier-bench
before deploy. No existing artefacts carry hashes from any older shape —
the pipeline is new, so v1 applies from day one and no migration is
needed. The first artefact that carries a v1 hash locks the shape for
everyone.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata

VERSJON = "1"


def kanon_hash(obj) -> str:
    """sha256 over the canonical serialisation of obj (without content_hash)."""
    normalisert = _nfc(obj)
    serialisert = json.dumps(normalisert, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"))
    return "sha256:" + hashlib.sha256(serialisert.encode("utf-8")).hexdigest()


def _nfc(obj):
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [_nfc(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): _nfc(v) for k, v in obj.items()}
    return obj


if __name__ == "__main__":
    import sys
    import yaml
    sti = sys.argv[1] if len(sys.argv) > 1 else None
    if not sti:
        print("usage: kanon_hash.py <file.yaml|file.json>", file=sys.stderr)
        raise SystemExit(2)
    tekst = open(sti, encoding="utf-8").read()
    obj = yaml.safe_load(tekst) if sti.endswith((".yaml", ".yml")) else json.loads(tekst)
    if isinstance(obj, dict):
        obj.pop("content_hash", None)
    print(kanon_hash(obj))
