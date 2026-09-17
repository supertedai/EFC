#!/usr/bin/env python3
"""kanon_hash.py — DEN ene kanoniske hash-funksjonen for EFC-artefakter.

Låsen (design §0, ærlighetsregel 2): generator og verifier MÅ dele denne
formen. Spesifikasjonen:
- inndata: Python-objekt (dict/list/str/int/float/bool/None) lastet fra
  YAML/JSON, UTEN content_hash-feltet
- serialisering: json.dumps(obj, sort_keys=True, ensure_ascii=False,
  separators=(",", ":")) — kompakte separatorer, ingen mellomrom-drift
- Unicode: teksten normaliseres til NFC FØR hashing (macOS NFD-dritt skal
  ikke gi hash-kollisjoner på tvers av maskiner)
- tall: JSON-tall som de er (ingen trailing-zeros-normalisering — Python
  og JavaScript leser dem likt via json)
- resultat: "sha256:" + hexdigest

Endringer her er en schema-ENDring: bump versjonen og kjør verifier-bench
før deploy.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata

VERSJON = "1"


def kanon_hash(obj) -> str:
    """sha256 over den kanoniske serialiseringen av obj (uten content_hash)."""
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
        print("bruk: kanon_hash.py <fil.yaml|fil.json>", file=sys.stderr)
        raise SystemExit(2)
    tekst = open(sti, encoding="utf-8").read()
    obj = yaml.safe_load(tekst) if sti.endswith((".yaml", ".yml")) else json.loads(tekst)
    if isinstance(obj, dict):
        obj.pop("content_hash", None)
    print(kanon_hash(obj))
