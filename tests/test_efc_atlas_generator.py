"""EFC-atlasets ene invariant: mirror er alltid fersk.

Atlaset har ingen egen sannhet — det genereres fra regime_nodes.jsonld.
En utdatert data.mjs er derfor ikke en kosmetisk drift; det er to
navnerom for samme system, og hele poenget med generatoren er at den
feilen skal vaere UMULIG aa committe.

Measured 2026-09-19 (card t_db4fa279): the invariant was read for two of the
four files the generator WRITES. `SYSTEM.md` and `atlas.html` are produced by
the same run (the generator strips their whitespace after `node build.mjs`),
and no gate compared them with the generator's output — a hand edit in either
passed every check. That is how a mirror drifts away from its producer: the
emitted text is read by tests, but the EMISSION is not.
"""
import pathlib
import subprocess

ROT = pathlib.Path(__file__).resolve().parents[1]

#: Every file the generator writes. Declared here so that a NEW write target in
#: `efc_atlas_generator.py` fails the test below instead of landing unread.
GENERATED = ("docs/efc-atlas/atlas/data.mjs",
             "docs/efc-atlas/INDEKS.md",
             "docs/efc-atlas/SYSTEM.md",
             "docs/efc-atlas/atlas.html")


def _atlas_files() -> dict[str, bytes]:
    """Every file under docs/efc-atlas, by path, with its bytes."""
    rot = ROT / "docs" / "efc-atlas"
    return {str(p.relative_to(ROT)): p.read_bytes()
            for p in sorted(rot.rglob("*")) if p.is_file()}


def test_mirror_er_fersk_etter_regenerering():
    """The generator's output IS the committed mirror — for every file it writes.

    Both halves matter: the set of files it rewrites must be exactly the
    declared set (an undeclared writer is a producer no gate reads), and every
    declared file must come out of the run unchanged (otherwise the committed
    mirror is not what the generator produces).
    """
    for path in GENERATED:
        assert (ROT / path).is_file(), f"{path} is missing — the generator writes it"
    before = _atlas_files()
    r = subprocess.run(
        ["/opt/venvs/t_123ed6d9/bin/python",
         str(ROT / "scripts" / "maintenance" / "efc_atlas_generator.py")],
        capture_output=True, text=True, cwd=ROT, timeout=120)
    assert r.returncode == 0, r.stderr[:400]
    after = _atlas_files()
    rewritten = {path for path in after if before.get(path) != after[path]}
    undeclared = sorted(rewritten - set(GENERATED))
    assert not undeclared, (
        f"the generator writes files that are not declared in GENERATED: "
        f"{undeclared} — declare them, so the run is read")
    for generated in GENERATED:
        r2 = subprocess.run(["git", "diff", "--exit-code", "--", generated],
                            capture_output=True, cwd=ROT, timeout=30)
        assert r2.returncode == 0, (
            f"{generated} is stale — the generator changed it. Run "
            "efc_atlas_generator.py and commit the result.")


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
