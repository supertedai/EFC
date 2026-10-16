"""EFC's atlas has one invariant: the generated atlas is always fresh.

The atlas holds no truth of its own — it is generated from
regime_nodes.jsonld, and the generator writes all four surfaces in ONE run:
data.mjs, INDEKS.md, SYSTEM.md and atlas.html. A stale file is not cosmetic
drift but two namespaces for one system, and the whole point of the generator
is that this error must be IMPOSSIBLE to commit.

MEASURED 2026-09-20 (t_31a7afd9): the freshness claim covered data.mjs and
INDEKS.md only. When `docs/efc-atlas/atlas/template.html` or the generator's
strip step was changed without regenerating, the generator rewrote SYSTEM.md
and atlas.html while pytest said GREEN (exit 0, 23 passed). The published
docs/efc-atlas/atlas.html could therefore lag behind the bank with green CI.
Both arms are now covered by one mechanism: the generator writes all four in
the same run.
"""
import pathlib
import subprocess
import sys

# The interpreter. The generator runs as a subprocess, so it must be the
# one RUNNING this test — that is the one holding the dependencies,
# wherever it happens to live. Measured 2026-09-18: this line hardcoded a
# venv path that exists only on the Hermes host, and in CI
# (ubuntu-latest) both tests died with FileNotFoundError. A test that
# passes only on the host is not a gate.
PYTHON = sys.executable

ROT = pathlib.Path(__file__).resolve().parents[1]


#: Every surface the generator writes in ONE run. Split this list and one arm
#: is freshness-gated while the other is not — that was the measured failure.
GENERATED_SURFACES = (
    "docs/efc-atlas/atlas/data.mjs",
    "docs/efc-atlas/INDEKS.md",
    "docs/efc-atlas/SYSTEM.md",
    "docs/efc-atlas/atlas.html",
)


def test_all_generated_surfaces_are_fresh_after_regeneration():
    """MEASURED 2026-09-20 (t_31a7afd9); the command is the CI job's last step:

        python3 -m pytest tests/test_efc_atlas_generator.py tests/test_atlas_lesbarhet.py -q

    The build arm was not gated: `template.html` changed without regenerating
    -> exit 0 while the generator wrote `M docs/efc-atlas/atlas.html`; the
    generator's strip step changed without regenerating -> exit 0 while it
    wrote `M docs/efc-atlas/SYSTEM.md`, `M docs/efc-atlas/atlas.html`. Only
    the data.mjs arm went red (exit 1).

    The comparison is against HEAD, not against the index: `git diff` alone
    answers "does the working tree match what you staged", so a regenerated
    but staged and uncommitted output would pass. The gate protects what is
    COMMITTED.
    """
    r = subprocess.run(
        [PYTHON,
         str(ROT / "scripts" / "maintenance" / "efc_atlas_generator.py")],
        capture_output=True, text=True, cwd=ROT, timeout=60)
    assert r.returncode == 0, r.stderr[:400]
    for generated in GENERATED_SURFACES:
        r2 = subprocess.run(["git", "diff", "HEAD", "--exit-code", "--",
                             generated],
                            capture_output=True, cwd=ROT, timeout=30)
        assert r2.returncode == 0, (
            f"{generated} er utdatert — generatoren endret den. Kjør "
            "efc_atlas_generator.py og commit resultatet.")


def test_atlas_bygger_uten_feil():
    """Generatoren ER byggetrinnet naa — den skriver data.mjs, kjoerer
    build.mjs og stripper whitespace. Ikke kall node direkte: det
    overskriver den strippede outputen."""
    r = subprocess.run(
        [PYTHON,
         str(ROT / "scripts" / "maintenance" / "efc_atlas_generator.py")],
        capture_output=True, text=True, cwd=ROT, timeout=120)
    assert r.returncode == 0, r.stderr[-400:]
    assert "built" in r.stdout or "structures" in r.stdout


def test_generert_atlas_har_doctype_og_charset():
    html = (ROT / "docs" / "efc-atlas" / "atlas.html").read_text()
    assert html.startswith("<!doctype html>"), "quirks mode"
    assert '<meta charset="utf-8">' in html[:120], "mojibake arrows"


def test_bygget_output_har_ingen_trailing_whitespace():
    """This test locks the COMMITTED state as stripped, not the working tree,
    so the bytes come from HEAD and not from the file.

    MEASURED 2026-09-20 (t_31a7afd9): it read SYSTEM.md/atlas.html AFTER an
    earlier test had run the generator, and so measured what the generator had
    just written. The claim ("the committed state") and the measurement were
    two different things, and in practice the order on the command line made
    the test blind to a stale commit.

    The failure it catches, which the freshness gate cannot: output that is
    REGENERATED and COMMITTED with whitespace. Then HEAD == the generator, but
    the artefact itself is broken.

    MEASURED the same day: build.mjs writes no trailing whitespace today (raw
    `node build.mjs` -> 0 such lines, last byte '\\n'), so the generator's
    strip step is a no-op. It is the freshness gate above that catches build
    drift, not this test.
    """
    for navn in ("SYSTEM.md", "atlas.html"):
        sti = f"docs/efc-atlas/{navn}"
        r = subprocess.run(["git", "show", f"HEAD:{sti}"],
                           capture_output=True, text=True, cwd=ROT, timeout=30)
        assert r.returncode == 0, f"{sti} is not in HEAD: {r.stderr[:200]}"
        darlige = [i for i, l in enumerate(r.stdout.splitlines(), 1)
                   if l.rstrip() != l]
        assert not darlige, f"{navn}: trailing whitespace pa linjene {darlige}"
