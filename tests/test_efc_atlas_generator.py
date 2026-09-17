"""EFC-atlasets ene invariant: data.mjs er alltid fersk.

Atlaset har ingen egen sannhet — det genereres fra regime_nodes.jsonld.
En utdatert data.mjs er derfor ikke en kosmetisk drift; det er to
navnerom for samme system, og hele poenget med generatoren er at den
feilen skal vaere UMULIG aa committe.
"""
import pathlib
import subprocess

ROT = pathlib.Path(__file__).resolve().parents[1]


def test_data_mjs_er_fersk_etter_regenerering():
    r = subprocess.run(
        ["/opt/venvs/t_123ed6d9/bin/python",
         str(ROT / "scripts" / "maintenance" / "efc_atlas_generator.py")],
        capture_output=True, text=True, cwd=ROT, timeout=60)
    assert r.returncode == 0, r.stderr[:400]
    r2 = subprocess.run(["git", "diff", "--exit-code", "--",
                         "docs/efc-atlas/atlas/data.mjs"],
                        capture_output=True, cwd=ROT, timeout=30)
    assert r2.returncode == 0, (
        "data.mjs er utdatert — generatoren endret den. Kjør "
        "efc_atlas_generator.py og commit resultatet.")


def test_atlas_bygger_uten_feil():
    """Generatoren ER byggetrinnet naa — den skriver data.mjs, kjoerer
    build.mjs og stripper whitespace. Ikke kall node direkte: det
    overskriver den strippede outputen."""
    r = subprocess.run(
        ["/opt/venvs/t_123ed6d9/bin/python",
         str(ROT / "scripts" / "maintenance" / "efc_atlas_generator.py")],
        capture_output=True, text=True, cwd=ROT, timeout=120)
    assert r.returncode == 0, r.stderr[-400:]
    assert "built" in r.stdout or "structures" in r.stdout


def test_generert_atlas_har_doctype_og_charset():
    html = (ROT / "docs" / "efc-atlas" / "atlas.html").read_text()
    assert html.startswith("<!doctype html>"), "quirks mode"
    assert '<meta charset="utf-8">' in html[:120], "mojibake arrows"


def test_bygget_output_har_ingen_trailing_whitespace():
    """build.mjs skriver tomme linjer med mellomrom — generatoren
    stripper dem. Denne testen laaser at den COMMITTEDE tilstanden
    er strippet, ikke bare arbeidstreet."""
    for navn in ("SYSTEM.md", "atlas.html"):
        p = ROT / "docs" / "efc-atlas" / navn
        darlige = [i for i, l in enumerate(
            p.read_text().splitlines(), 1) if l.rstrip() != l]
        assert not darlige, f"{navn}: trailing whitespace pa linjene {darlige}"
