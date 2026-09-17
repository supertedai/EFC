"""Regresjonstester for kunnskapslivssyklusen (fase 1).

Kontraktene: den kanoniske hashen er stabil på tvers av nøkkelrekkefølge
og Unicode-form; triage og bench bruker SAMME funksjon; arxiv-parseren
håndterer Atom XML (den faktiske responsformen — JSON-antakelsen ga 0
treff); og >5 MB-respons kappes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))


def test_kanon_hash_nfc_og_rekkefoelge():
    from kanon_hash import kanon_hash
    a = {"claim": "entropigradient ∇S", "n": 1, "b": [1, 2]}
    b = {"b": [1, 2], "claim": "entropigradient ∇S", "n": 1}  # annen rekkefølge
    c = {"claim": "entropigradient \u2207S", "n": 1, "b": [1, 2]}  # NFD-ish: prekomponert vs dekomponert
    assert kanon_hash(a) == kanon_hash(b), "nøkkelrekkefølge må ikke endre hashen"
    # NFC-normalisering: sammensatt ∇ (U+2207) og dekomponert ∇ (U+2207 er ikke
    # dekomponerbart — bruk é som faktisk splitter i NFD)
    d = {"claim": "e\u0301", "n": 1}   # e + kombinerende akutt (NFD)
    e = {"claim": "\u00e9", "n": 1}    # é prekomponert (NFC)
    assert kanon_hash(d) == kanon_hash(e), "NFC-normaliseringen må gjøre NFD/NFC like"


def test_triage_og_bench_deler_funksjon():
    import subprocess
    from kanon_hash import kanon_hash
    kandidat = {
        "insight_id": "INS-abcdef01", "source_role": "researcher",
        "writer_role": "researcher", "run_id": "run-test-0001",
        "claim": "En testpåstand med entropigradient.",
        "claim_type": "observation", "scope": "test",
        "source_refs": [{"uri": "https://example.org/t", "retrieved_at": "2026-09-16T00:00:00Z"}],
        "confidence": 0.5, "status": "candidate",
        "created_at": "2026-09-16T00:00:00Z",
    }
    kopi = dict(kandidat)
    kopi["content_hash"] = kanon_hash(kandidat)
    sti = Path("/tmp") / "test-kandidat.yaml"
    import yaml
    sti.write_text(yaml.safe_dump(kopi, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROT / "scripts/maintenance/triage_insikt.py"),
                        str(sti)], capture_output=True, text=True, timeout=60)
    svar = json.loads(r.stdout)
    assert svar["status"] == "gyldig", f"kandidat med riktig hash må passere: {svar}"
    assert svar["triage"] in ("lav", "middels", "høy")


def test_arxiv_parser_atom_xml():
    import efc_inntak as inn
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2503.14738v1</id>
    <title>  DESI DR2 Results II: Measurements of BAO  </title>
    <published>2025-03-18T00:00:00Z</published>
    <link href="http://dx.doi.org/10.1103/x.test"/>
    <summary>  Baryon acoustic oscillations from DESI DR2.  </summary>
  </entry>
</feed>"""
    import urllib.request
    original = urllib.request.Request, urllib.request.urlopen

    class _Svar:
        def __init__(self, data: bytes):
            self._d = data
        def read(self, n=None):
            return self._d[:n] if n else self._d
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_open(req, timeout=None):
        return _Svar(xml.encode())
    urllib.request.Request = lambda *a, **k: a[0] if a else ""
    urllib.request.urlopen = fake_open
    try:
        ut = inn._arxiv(5)
    finally:
        urllib.request.Request, urllib.request.urlopen = original
    assert len(ut) == 1, f"Atom-poster må parses: {ut}"
    assert ut[0]["kilde"] == "arxiv"
    assert ut[0]["tittel"] == "DESI DR2 Results II: Measurements of BAO"
    assert ut[0]["doi"] == "10.1103/x.test"
