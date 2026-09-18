"""Låser navbar-kontrakten på skriveveiene til de offentlige sidene (t_41d80135).

Navbaren har én eier: ``efc_navbar_sync.py``. Den rendrer den kanoniske
blokken for GJELDENDE side — med den røde «du er her»-markeringen
(``color:#c22``). ``_nav_helper.ensure_nav()`` bar tidligere sin egen kopi av
navbaren UTEN markeringen, så enhver skriver som kalte den gjorde en kanonisk
side om til ``navbar_drift``: målt 2026-09-17 kom ``EFC_Changelog.html`` ut av
skriveveien uten ``color:#c22;`` og ``efc_navbar_sync.py --check`` svarte rc=2.
Driften var usynlig for side-innholdssjekkene fordi de ikke ser navbaren.

Det som låses her:
  1. ``ensure_nav`` uten sidens navn rører ikke navbaren i det hele tatt.
  2. ``ensure_nav`` med sidens navn gjenoppretter nøyaktig den kanoniske
     blokken for den siden, og er idempotent.
  3. En skriving fra hver av de to skriverne (``efc_ai_brain.write_page`` og
     ``efc_ledger_autofill.skriv_side``) til en driftet side etterlater den
     EKTE gaten grønn: ``efc_navbar_sync.main(["--check"]) == 0``.
  4. ``efc_ledger_autofill.main`` skriver begge sidene gjennom ``skriv_side``,
     så veien om det kanoniske navnet ikke kan omgås.

Skrivingene går til en sandkasse-kopi av ``docs/public``; verken repoet eller
de ekte sidene berøres.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
PUBLIC = ROOT / "docs" / "public"
sys.path.insert(0, str(MAINT))

import _nav_helper  # noqa: E402
import efc_ai_brain as brain  # noqa: E402
import efc_ledger_autofill as autofill  # noqa: E402
import efc_navbar_sync as sync  # noqa: E402

SIDEN = "EFC_Changelog.html"


def _legacy_nav() -> str:
    """Navbaren slik den gamle `_nav_helper`-kopien skrev den (uten markering)."""
    linjer = [sync.NAV_OPEN]
    for i, (href, label) in enumerate(sync.NAV_ENTRIES):
        style = ("font-weight:600;" if i == len(sync.NAV_ENTRIES) - 1
                 else "margin-right:1.5rem; font-weight:600;")
        linjer.append(f'  <a href="{href}" style="{style}">{label}</a>')
    linjer.append("</div>")
    return "\n".join(linjer)


def _driftet(tekst: str, side: str) -> str:
    """Bytt ut den kanoniske navbaren med den gamle, markeringsløse varianten."""
    kanonisk = sync.render_nav(side)
    assert kanonisk in tekst, f"{side}: fant ingen kanonisk navbar å drifte fra"
    return tekst.replace(kanonisk, _legacy_nav(), 1)


def _sandkasse(tmp_path: Path) -> Path:
    """Kopi av docs/public med alle sidene gaten sjekker."""
    pub = tmp_path / "docs" / "public"
    pub.mkdir(parents=True, exist_ok=True)
    for side in sync.ALL_PAGES:
        (pub / side).write_text((PUBLIC / side).read_text(encoding="utf-8"),
                                encoding="utf-8")
    return pub


def test_ensure_nav_uten_side_rorer_ikke_navbaren():
    """Uten sidens navn kan en skriver ikke vite hvilken markering som gjelder."""
    tekst = (PUBLIC / SIDEN).read_text(encoding="utf-8")
    etter = _nav_helper.ensure_nav(tekst)
    assert etter == tekst
    assert sync.render_nav(SIDEN) in etter


def test_ensure_nav_med_side_reparerer_drift_og_er_idempotent():
    tekst = (PUBLIC / SIDEN).read_text(encoding="utf-8")
    driftet = _driftet(tekst, SIDEN)
    assert sync.render_nav(SIDEN) not in driftet, "fixturen er ikke ekte drift"

    reparert = _nav_helper.ensure_nav(driftet, SIDEN)
    assert sync.render_nav(SIDEN) in reparert
    assert "color:#c22;" in reparert, "markeringen for gjeldende side mangler"
    assert reparert == tekst, "reparasjonen ga ikke den kanoniske siden tilbake"
    assert _nav_helper.ensure_nav(reparert, SIDEN) == reparert

    # Full sti er også en gyldig sidereferanse.
    assert _nav_helper.ensure_nav(driftet, str(PUBLIC / SIDEN)) == tekst


def test_nav_helper_har_ingen_egen_navbar():
    """Rotårsaken: modulen skal ikke lenger bære sin egen navbar-kopi."""
    kilde = (MAINT / "_nav_helper.py").read_text(encoding="utf-8")
    assert "CANONICAL_NAV_HTML" not in kilde
    assert 'href="EFC_Elevator_Pitch.html"' not in kilde


def test_ai_brain_skriving_holder_navbaren_kanonisk(tmp_path, monkeypatch):
    pub = _sandkasse(tmp_path)
    sti = pub / SIDEN
    sti.write_text(_driftet(sti.read_text(encoding="utf-8"), SIDEN), encoding="utf-8")

    monkeypatch.setattr(sync, "PUBLIC_ROOT", pub)
    monkeypatch.setattr(brain, "PUBLIC_PAGES", {"changelog": str(sti)})

    assert sync.main(["--check"]) == 2, "gaten skal stå rødt på fixturen før skriving"

    brain.write_page("changelog", brain.read_page("changelog") + "\n<li>nytt</li>\n")

    assert "<li>nytt</li>" in sti.read_text(encoding="utf-8")
    assert sync.main(["--check"]) == 0
    assert "color:#c22;" in sti.read_text(encoding="utf-8")


def test_ledger_autofill_skriving_holder_navbaren_kanonisk(tmp_path, monkeypatch):
    pub = _sandkasse(tmp_path)
    sider = ("EFC_Validation_Ledger.html", "EFC_Changelog.html")
    for side in sider:
        sti = pub / side
        sti.write_text(_driftet(sti.read_text(encoding="utf-8"), side), encoding="utf-8")

    monkeypatch.setattr(sync, "PUBLIC_ROOT", pub)
    monkeypatch.setattr(autofill, "LEDGER", str(pub / sider[0]))
    monkeypatch.setattr(autofill, "CHANGELOG", str(pub / sider[1]))

    assert sync.main(["--check"]) == 2, "gaten skal stå rødt på fixturen før skriving"

    for sti in (autofill.LEDGER, autofill.CHANGELOG):
        tekst = Path(sti).read_text(encoding="utf-8")
        autofill.skriv_side(sti, tekst + "\n<li>autofyll</li>\n")
        assert "<li>autofyll</li>" in Path(sti).read_text(encoding="utf-8")

    assert sync.main(["--check"]) == 0
    for side in sider:
        assert "color:#c22;" in (pub / side).read_text(encoding="utf-8")


def test_autofill_main_skriver_begge_sidene_gjennom_skriv_side():
    """main() skal ikke ha sin egen skrivevei forbi det kanoniske navnet."""
    tre = ast.parse((MAINT / "efc_ledger_autofill.py").read_text(encoding="utf-8"))
    main = next(n for n in ast.walk(tre)
                if isinstance(n, ast.FunctionDef) and n.name == "main")
    kall = [n for n in ast.walk(main) if isinstance(n, ast.Call)]

    skrevne = {k.args[0].id for k in kall
               if isinstance(k.func, ast.Name) and k.func.id == "skriv_side"
               and k.args and isinstance(k.args[0], ast.Name)}
    assert skrevne == {"LEDGER", "CHANGELOG"}

    egne_skrivinger = [
        k for k in kall
        if isinstance(k.func, ast.Name) and k.func.id == "open"
        and len(k.args) > 1
        and isinstance(k.args[1], ast.Constant) and k.args[1].value == "w"
    ]
    assert egne_skrivinger == [], "main() skriver en offentlig side utenom skriv_side()"
