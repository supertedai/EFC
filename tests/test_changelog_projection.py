"""Regresjonstester for changelog-projeksjonen (t_26dd0ef5).

Kontraktene som testes:
  * change_id er sha256 av hendelsens eget innhold — stabil, unik, etterregnbar;
  * projeksjonen er DETERMINISTISK: samme logg gir bit-identisk
    changelog.json og HTML-region, og metatypen projection_built holdes
    utenfor inputen så rebygging konvergerer;
  * kjeden registerpost → changelog.json → EFC_Changelog.html bærer samme
    change_id, og brudd fanges hardt: manglende change_id, manuell redigering
    av den genererte regionen, ukjent id på en flate, omskrevet logg;
  * en testendring i scripts/ gir en projeksjonslinje med change_id på alle
    tre flatene (akseptkriteriet), målt i et EKTE git-repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
MAINT = ROT / "scripts" / "maintenance"
sys.path.insert(0, str(MAINT))

GEN = MAINT / "efc_auto_changelog.py"
SJEKK = MAINT / "efc_changelog_check.py"

from efc_change_id import (  # noqa: E402
    HTML_SLUTT,
    HTML_START,
    PROJ_NOKKEL,
    avvik,
    beregn_change_id,
    change_id_for,
    html_region,
    input_hash,
    json_projeksjon,
    json_tekst,
    les_logg,
    projeksjonsinput,
    region_fra_html,
    sett_inn_region,
)

SIDE_HODE = (
    "<!doctype html>\n<html><body>\n"
    # Navbaren bærer den røde «du er her»-markeringen slik efc_navbar_sync.py
    # rendrer den. Generatoren skal IKKE røre navbaren (målt: den gamle
    # _nav_helper.ensure_nav fjernet markeringen og ga navbar_drift).
    '<div style="background:#f8f9fa;">\n'
    '  <a href="EFC_Elevator_Pitch.html">Pitch</a>\n'
    '  <a href="EFC_Changelog.html" style="color:#c22;">Changelog</a>\n'
    "</div>\n"
    "<h2>2026</h2>\n\n<ul>\n"
    "  <li><strong>2026-09-07</strong> &mdash; eldre linje.</li>\n"
    "</ul>\n</body></html>\n"
)


def _hendelse(event_id="EVT-2026-000001", occurred="2026-09-16T21:09:34+00:00",
              sti="scripts/maintenance/efc_change_id.py", why="test",
              med_change_id=True, action="file_changed"):
    hendelse = {
        "event_id": event_id,
        "occurred_at": occurred,
        "action": action,
        "role": "researcher",
        "kanban_card": "t_26dd0ef5",
        "files": [sti],
        "why": why,
        "result": "success",
        "reversible": True,
    }
    if med_change_id:
        hendelse["change_id"] = beregn_change_id(hendelse)
    return hendelse


def _skriv_logg(sti: Path, hendelser: list[dict]) -> None:
    sti.write_text("".join(json.dumps(h, ensure_ascii=False) + "\n"
                           for h in hendelser), encoding="utf-8")


def _bygg_kjede(tmp: Path, hendelser: list[dict]) -> tuple[Path, Path, Path]:
    """Skriv logg + de to flatene fra samme projeksjon (konsistent kjede)."""
    (tmp / "logs").mkdir(parents=True, exist_ok=True)
    (tmp / "docs" / "validation-ledger" / "data").mkdir(parents=True, exist_ok=True)
    (tmp / "docs" / "public").mkdir(parents=True, exist_ok=True)
    logg = tmp / "logs" / "activity.jsonl"
    _skriv_logg(logg, hendelser)
    oppføringer, _ = projeksjonsinput(hendelser)
    json_sti = tmp / "docs" / "validation-ledger" / "data" / "changelog.json"
    json_sti.write_text(json_tekst(json_projeksjon({"name": "Recent Changes"},
                                                    oppføringer)),
                        encoding="utf-8")
    html_sti = tmp / "docs" / "public" / "EFC_Changelog.html"
    html_sti.write_text(sett_inn_region(SIDE_HODE, html_region(oppføringer),
                                        "2026"), encoding="utf-8")
    return logg, json_sti, html_sti


def _meta(inn_hash: str, event_id="EVT-2026-000099") -> dict:
    hendelse = {
        "event_id": event_id,
        "occurred_at": "2026-09-17T06:00:00+00:00",
        "action": "projection_built",
        "role": "auto",
        "kanban_card": "auto-projeksjon",
        "files": ["docs/validation-ledger/data/changelog.json"],
        "why": f"changelog-projeksjon bygget: generator=efc_auto_changelog.py "
               f"version=2.0 input_hash={inn_hash}",
        "result": "success",
        "reversible": True,
        "generator": "efc_auto_changelog.py",
        "generator_version": "2.0",
        "input_hash": inn_hash,
    }
    hendelse["change_id"] = beregn_change_id(hendelse)
    return hendelse


# ---------------------------------------------------------------- change_id
def test_change_id_er_innholdsavhengig_og_ignorerer_eget_felt():
    a = _hendelse(med_change_id=False)
    b = dict(a, change_id="CHG-000000000000")
    assert beregn_change_id(a) == beregn_change_id(b), \
        "change_id må regnes uten change_id-feltet selv"
    assert change_id_for(a) == beregn_change_id(a), \
        "uten lagret id avledes den fra innholdet"
    assert change_id_for(b) == "CHG-000000000000", \
        "en lagret id er autoritativ — og sjekken krever at den er sann"
    endret = dict(a, why="noe annet")
    assert beregn_change_id(a) != beregn_change_id(endret), \
        "en endret logglinje må gi en ny id"
    assert beregn_change_id(a).startswith("CHG-")


def test_legacy_linje_uten_change_id_faar_avledet_id():
    hendelse = _hendelse(med_change_id=False)
    assert change_id_for(hendelse) == beregn_change_id(hendelse)
    oppføringer, statistikk = projeksjonsinput([hendelse])
    assert statistikk["legacy_uten_change_id"] == 1
    assert oppføringer[0]["change_id"] == beregn_change_id(hendelse)


def test_endret_logglinje_oppdages_som_avvik(tmp_path):
    logg, json_sti, html_sti = _bygg_kjede(
        tmp_path, [_hendelse(), _meta("x")])
    # omskriv linja i ettertid (samme id, annet innhold)
    linjer = logg.read_text(encoding="utf-8").splitlines()
    linjer[0] = linjer[0].replace('"why": "test"', '"why": "pønsket"')
    logg.write_text("\n".join(linjer) + "\n", encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "change_id_avviker_fra_innhold" in typer


# --------------------------------------------------------- determinisme
def test_projeksjonen_er_deterministisk_og_nyeste_foerst():
    eldre = _hendelse(event_id="EVT-2026-000001",
                      occurred="2026-09-16T10:00:00+00:00", sti="a/x.py")
    nyere = _hendelse(event_id="EVT-2026-000002",
                      occurred="2026-09-17T10:00:00+00:00", sti="b/y.py")
    oppføringer, _ = projeksjonsinput([eldre, nyere])
    assert [o["files"][0] for o in oppføringer] == ["b/y.py", "a/x.py"]
    assert input_hash(oppføringer) == input_hash(projeksjonsinput([eldre, nyere])[0])
    assert html_region(oppføringer) == html_region(
        projeksjonsinput([eldre, nyere])[0])


def test_metahendelsen_holdes_utenfor_inputen():
    endringer = [_hendelse(), _hendelse(event_id="EVT-2026-000002",
                                        sti="b/y.py")]
    oppfør, _ = projeksjonsinput(endringer)
    uten_meta = input_hash(oppfør)
    oppfør_med, statistikk = projeksjonsinput(endringer + [_meta(uten_meta)])
    assert input_hash(oppfør_med) == uten_meta, \
        "projeksjonens egen provenienshendelse må ikke endre inputen"
    assert statistikk["meta_hendelser"] == 1
    assert len(oppfør_med) == 2


def test_regionen_settes_inn_idempotent_og_bevarer_historikken():
    oppføringer, _ = projeksjonsinput([_hendelse()])
    region = html_region(oppføringer)
    html = sett_inn_region(SIDE_HODE, region, "2026")
    assert HTML_START in html and HTML_SLUTT in html
    assert html.index(HTML_START) < html.index("eldre linje")
    assert sett_inn_region(html, region, "2026") == html, \
        "reinnsetting av samme region må være en no-op"
    assert region_fra_html(html) == region
    # en NY region skal ERSTATTE den gamle, ikke legges ved siden av
    ny_region = html_region(projeksjonsinput([_hendelse(why="oppdatert")])[0])
    byttet = sett_inn_region(html, ny_region, "2026")
    assert region_fra_html(byttet) == ny_region
    assert byttet.count(HTML_START) == 1, "regionen skal finnes nøyaktig én gang"
    assert "eldre linje" in byttet, "historikken utenfor regionen skal stå"


def test_html_escaper_innhold_fra_loggen():
    farlig = _hendelse(why='<script>alert("x")</script> & <b>uthevet</b>')
    oppføringer, _ = projeksjonsinput([farlig])
    region = html_region(oppføringer)
    assert "<script>" not in region
    assert "&lt;script&gt;" in region
    assert "&amp;" in region


# ----------------------------------------------------------------- sjekken
def test_avvik_er_tom_naar_kjeden_er_konsistent(tmp_path):
    hendelser = [_hendelse(), _hendelse(event_id="EVT-2026-000002",
                                        sti="docs/public/x.html")]
    oppfør, _ = projeksjonsinput(hendelser)
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, hendelser + [_meta(
        input_hash(oppfør))])
    resultat = avvik(logg, json_sti, html_sti)
    assert resultat["feil"] == [], resultat["feil"]
    assert resultat["info"]["endringer"] == 2


def test_sjekken_feiler_paa_changelog_uten_change_id(tmp_path):
    """Akseptkriteriet: CI feiler på changelog uten change_id."""
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    data = json.loads(json_sti.read_text(encoding="utf-8"))
    del data[PROJ_NOKKEL]["entries"][0]["change_id"]
    json_sti.write_text(json_tekst(data), encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "json_post_uten_change_id" in typer
    assert "json_projeksjon_avviker" in typer


def test_sjekken_feiler_paa_html_linje_uten_change_id(tmp_path):
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    html = html_sti.read_text(encoding="utf-8").replace(' data-change-id="', ' data-x="')
    html_sti.write_text(html, encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "html_linje_uten_change_id" in typer


def test_sjekken_feiler_paa_manuell_redigering_av_regionen(tmp_path):
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    html = html_sti.read_text(encoding="utf-8").replace(
        "&mdash; test &mdash;", "&mdash; håndredigert &mdash;")
    html_sti.write_text(html, encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "html_region_avviker" in typer


def test_sjekken_feiler_paa_change_id_som_bare_finnes_paa_en_flate(tmp_path):
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    data = json.loads(json_sti.read_text(encoding="utf-8"))
    data[PROJ_NOKKEL]["entries"][0]["change_id"] = "CHG-deadbeefcafe"
    json_sti.write_text(json_tekst(data), encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "ukjent_change_id_i_json" in typer
    assert "mangler_json_post" in typer


def test_sjekken_feiler_paa_ukjent_change_id_i_html(tmp_path):
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    html = html_sti.read_text(encoding="utf-8").replace(
        HTML_SLUTT,
        '  <li data-change-id="CHG-deadbeefcafe">fabrikkert</li>\n' + HTML_SLUTT, 1)
    html_sti.write_text(html, encoding="utf-8")
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "ukjent_change_id_i_html" in typer


def test_sjekken_feiler_paa_change_id_utenfor_projeksjonen(tmp_path):
    """Historikken er grandfathered, men en fabrikkert korrelasjonsnøkkel er ikke."""
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, [_hendelse(), _meta("x")])
    html = html_sti.read_text(encoding="utf-8").replace(
        "</ul>", '  <li data-change-id="CHG-deadbeefcafe">utenfor regionen</li>\n</ul>', 1)
    html_sti.write_text(html, encoding="utf-8")
    resultat = avvik(logg, json_sti, html_sti)
    typer = {f["type"] for f in resultat["feil"]}
    assert "change_id_utenfor_projeksjonen" in typer
    assert resultat["info"]["historiske_linjer_utenfor_regionen"] >= 2


def test_sjekken_feiler_naar_projeksjonen_ikke_er_logget(tmp_path):
    hendelser = [_hendelse()]
    oppfør, _ = projeksjonsinput(hendelser)
    logg, json_sti, html_sti = _bygg_kjede(tmp_path, hendelser + [_meta("feil-hash")])
    typer = {f["type"] for f in avvik(logg, json_sti, html_sti)["feil"]}
    assert "projeksjon_ikke_logget" in typer
    assert input_hash(oppfør) != "feil-hash"


# ---------------------------------------------------- ekte git: ende-til-ende
def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.org",
         "-c", "commit.gpgsign=false", *args],
        cwd=str(repo), capture_output=True, text=True, timeout=60)


def _mal_repo(tmp_path: Path) -> Path:
    """Et minimalt, ekte EFC-lignende repo med de tre skriptene på plass."""
    repo = tmp_path / "repo"
    (repo / "scripts" / "maintenance").mkdir(parents=True)
    (repo / "docs" / "validation-ledger" / "data").mkdir(parents=True)
    (repo / "docs" / "public").mkdir(parents=True)
    (repo / "logs").mkdir()
    for navn in ("efc_change_id.py", "efc_auto_changelog.py",
                 "efc_changelog_check.py",
                 "validate_activity_log.py"):
        (repo / "scripts" / "maintenance" / navn).write_text(
            (MAINT / navn).read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "docs" / "public" / "EFC_Changelog.html").write_text(
        SIDE_HODE, encoding="utf-8")
    (repo / "docs" / "validation-ledger" / "data" / "changelog.json").write_text(
        json.dumps({"name": "Recent Changes", "version": "3.0", "changes": []},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (repo / "logs" / "activity.jsonl").write_text("", encoding="utf-8")
    assert _git(repo, "init", "-b", "main").returncode == 0
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-m", "base").returncode == 0
    return repo


def _kjor(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=str(repo),
                          capture_output=True, text=True, timeout=120)


def test_testendring_i_scripts_gir_change_id_paa_alle_tre_flatene(tmp_path):
    """Akseptkriteriet, målt ende-til-ende i et ekte git-repo."""
    repo = _mal_repo(tmp_path)
    skript = repo / "scripts" / "maintenance" / "proeve.py"
    skript.write_text("# testendring i scripts/\n", encoding="utf-8")
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-m",
                "test: proveendring i scripts\n\nAktør: faber\n"
                "Oppgave: t_26dd0ef5").returncode == 0

    res = _kjor(repo, "scripts/maintenance/efc_auto_changelog.py",
                "--base", "HEAD~1", "--head", "HEAD", "--json")
    assert res.returncode == 0, res.stderr
    rapport = json.loads(res.stdout)
    registrert = rapport["registrering"]["registrert"]
    assert [h["files"][0] for h in registrert] == ["scripts/maintenance/proeve.py"]
    cid = registrert[0]["change_id"]
    assert registrert[0]["role"] == "faber", "Aktør-traileren skal bli rollen"
    assert registrert[0]["kanban_card"] == "t_26dd0ef5"

    # flate 1: registerposten
    logg_tekst = (repo / "logs" / "activity.jsonl").read_text(encoding="utf-8")
    assert cid in logg_tekst
    # flate 2: changelog.json
    data = json.loads((repo / "docs" / "validation-ledger" / "data"
                       / "changelog.json").read_text(encoding="utf-8"))
    assert cid in [e["change_id"] for e in data[PROJ_NOKKEL]["entries"]]
    # flate 3: EFC_Changelog.html
    html = (repo / "docs" / "public" / "EFC_Changelog.html").read_text(
        encoding="utf-8")
    assert f'data-change-id="{cid}"' in html
    assert "eldre linje" in html, "historikken skal stå urørt"
    assert 'color:#c22;' in html, \
        "generatoren skal ikke røre navbarens «du er her»-markering"

    # kjeden er konsistent, og sjekken sier det
    res = _kjor(repo, "scripts/maintenance/efc_changelog_check.py", "--json",
                "--base", "HEAD~1")
    assert res.returncode == 0, res.stdout + res.stderr
    assert json.loads(res.stdout)["feil"] == []

    # rebygging er en no-op (deterministisk)
    før = {p: (repo / p).read_text(encoding="utf-8") for p in (
        "logs/activity.jsonl",
        "docs/validation-ledger/data/changelog.json",
        "docs/public/EFC_Changelog.html")}
    assert _kjor(repo, "scripts/maintenance/efc_auto_changelog.py",
                 "--base", "HEAD~1", "--head", "HEAD").returncode == 0
    etter = {p: (repo / p).read_text(encoding="utf-8") for p in før}
    assert før == etter, "to bygg på samme input må gi bit-identisk output"


def test_torrmodus_skriver_ingenting(tmp_path):
    repo = _mal_repo(tmp_path)
    (repo / "scripts" / "maintenance" / "proeve2.py").write_text("x\n",
                                                                encoding="utf-8")
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-m", "test: torr").returncode == 0
    før = (repo / "logs" / "activity.jsonl").read_text(encoding="utf-8")
    res = _kjor(repo, "scripts/maintenance/efc_auto_changelog.py",
                "--base", "HEAD~1", "--head", "HEAD", "--torr", "--json")
    assert res.returncode == 0
    assert json.loads(res.stdout)["registrering"]["registrert"], \
        "tørrkjøringen skal likevel rapportere hva som ville bli skrevet"
    assert (repo / "logs" / "activity.jsonl").read_text(encoding="utf-8") == før


def test_sjekken_feiler_paa_omskrevet_aktivitetslogg(tmp_path):
    repo = _mal_repo(tmp_path)
    logg = repo / "logs" / "activity.jsonl"
    logg.write_text(json.dumps(_hendelse(), ensure_ascii=False) + "\n",
                    encoding="utf-8")
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-m", "logg: forste").returncode == 0
    linje = logg.read_text(encoding="utf-8")
    logg.write_text(linje.replace("researcher", "legacy"), encoding="utf-8")
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-m", "logg: omskrevet linje").returncode == 0
    res = _kjor(repo, "scripts/maintenance/efc_changelog_check.py", "--json",
                "--base", "HEAD~1")
    assert res.returncode == 1
    typer = {f["type"] for f in json.loads(res.stdout)["feil"]}
    assert "aktivitetslogg_omskrevet" in typer


def test_validate_activity_log_godtar_projeksjonsmeta(tmp_path):
    repo = _mal_repo(tmp_path)
    logg = repo / "logs" / "activity.jsonl"
    _skriv_logg(logg, [_hendelse(), _meta("abc")])
    res = _kjor(repo, "scripts/maintenance/validate_activity_log.py", "--json")
    assert res.returncode == 0, res.stdout
    assert json.loads(res.stdout)["feil"] == []
