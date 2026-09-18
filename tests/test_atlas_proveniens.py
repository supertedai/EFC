"""Proveniens er obligatorisk for hver node i EFC-atlaset."""
import json
import re
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"
KLAUSUL = "DOI etablerer identitet og persistens, ikke sannhet"
DOI = re.compile(r"^10\.\d{4,9}/\S+$")


def test_alle_atlasnoder_har_proveniens_og_doi_telles(capsys):
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    noder = atlas["nodes"]
    assert len(noder) == 116
    doi_noder = 0
    for node in noder:
        prov = node["ontology"]["proveniens"]
        assert prov["kilder"], node["id"]
        assert KLAUSUL in prov["begrensning"], node["id"]
        assert isinstance(prov["fullstendig"], bool), node["id"]
        for kilde in prov["kilder"]:
            assert kilde["type"] in {"doi", "url", "stroem", "laerebok", "artikkel", "intern"}
            assert kilde["ref"]
            assert kilde["hentet"]
        if any(k["type"] == "doi" and DOI.match(k["ref"]) for k in prov["kilder"]):
            doi_noder += 1
    print(f"Proveniens: {len(noder)} noder; DOI-koblede: {doi_noder}")
    assert doi_noder > 10
