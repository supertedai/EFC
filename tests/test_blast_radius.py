"""Tester for blast-radius-scoreren (t_882cfca, fase 1).

Fixturer per faktor: F, E, P og I testes HVER FOR SEG — en scorer som bare
testes end-to-end kan ikke skille «faktoren virker ikke» fra «faktoren ble
aldri truffet». Grensene (1–3/4–7/8–15/16–31/32+) testes på tallene i
bestillingen, og trigger-overstyringen testes mot en score som ellers ville
vært «liten» — den skal fortsatt bli blokkerende.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
SCRIPT = ROT / "scripts" / "maintenance" / "blast_radius.py"
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

import blast_radius as br  # noqa: E402

GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.org"]

EIERREGISTER = {
    "owners": ["orchestrator", "researcher"],
    "components": [
        {"id": "skript", "owner": "orchestrator", "coverage_glob": ["scripts/**"]},
        {"id": "tester", "owner": "researcher", "coverage_glob": ["tests/**"]},
        {"id": "docs", "owner": "researcher", "coverage_glob": ["docs/**"]},
        {"id": "gater", "owner": "orchestrator", "coverage_glob": [".github/**"]},
    ],
}

GYLDIG_POST = {
    "risk_id": "RISK-BLAST_RADIUS-0001", "type": "BLAST_RADIUS",
    "hazard_or_deviation": "test", "source_change_id": "t_deadbeef",
    "release_id": None, "berorte_komponenter": ["skript"], "arsak": "a",
    "konsekvens": "k", "barrierer": ["b"], "sannsynlighet": "middels",
    "alvorlighet": "høy", "blast_radius_score": 16, "klasse": "rød",
    "eier": "orchestrator", "utforer": "faber", "reviewer": "ekstern",
    "status": "oppdaget", "tiltak": ["t"], "kanban_card_id": "t_deadbeef",
    "gate_required": True, "gate_decision": "venter",
    "evidenslenker": ["repo:scripts/maintenance/blast_radius.py"],
    "opprettet_tid": "2026-09-17T07:30:00+00:00", "forfall": None,
    "sist_vurdert": "2026-09-17", "rest_risiko": "r", "supersedes": [],
    "related_ids": [], "registerversjon": "1.0",
}


def _git_rot(tmp_path: Path, filer: dict[str, str]) -> Path:
    """Minimalt git-repo med base-commit og et eierregister som dekker det."""
    (tmp_path / "governance").mkdir(parents=True, exist_ok=True)
    (tmp_path / "governance" / "ownership-register.json").write_text(
        json.dumps(EIERREGISTER), encoding="utf-8")
    (tmp_path / "governance" / "risiko").mkdir(parents=True, exist_ok=True)
    (tmp_path / "governance" / "risiko" / "risiko-register.jsonl").write_text(
        "", encoding="utf-8")
    for navn, innhold in filer.items():
        p = tmp_path / navn
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(innhold, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(GIT + ["add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(GIT + ["commit", "-qm", "base"], cwd=tmp_path, check=True)
    return tmp_path


def _kall(rot: Path, *args: str) -> subprocess.CompletedProcess:
    miljo = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@e.org"}
    return subprocess.run([sys.executable, str(SCRIPT), "--rot", str(rot), *args],
                          capture_output=True, text=True, env=miljo, timeout=120)


# --- faktor for faktor ----------------------------------------------------

def test_f_faktor_baand():
    assert [br.f_faktor(n) for n in (0, 1, 2, 3, 4, 20, 21)] == [1, 1, 2, 2, 3, 3, 4]


def test_e_faktor_ukjent_eier_og_antall():
    assert br.e_faktor([], True) == 4, "ukjent eier skal aldri gi lav E"
    assert br.e_faktor(["orchestrator"], False) == 1
    assert br.e_faktor(["orchestrator", "researcher"], False) == 2
    assert br.e_faktor(["a", "b", "c"], False) == 3
    assert br.e_faktor(["a", "b", "c", "d"], False) == 4
    assert br.e_faktor(["a", "a"], False) == 1, "duplikater er én eier"


def test_p_faktor_per_baand():
    assert br.p_faktor(["scripts/maintenance/blast_radius.py"]) == 1
    assert br.p_faktor(["schema/global_schema.json"]) == 2
    assert br.p_faktor(["docs/public/EFC_Validation_Ledger.html"]) == 3
    assert br.p_faktor(["api/v1/concepts.json"]) == 4
    assert br.p_faktor(["scripts/x.py", "api/v1/concepts.json"]) == 4, "høyeste treff vinner"
    assert br.p_faktor([]) == 1


def test_i_faktor_per_baand():
    assert br.i_faktor(["tests/test_blast_radius.py"]) == 1
    assert br.i_faktor(["public/graph/statements.yaml"]) == 2
    assert br.i_faktor(["schemas/insight-candidate.schema.json"]) == 3
    for sti in (".github/workflows/efc-risiko.yml", "governance/risiko/risiko-register.jsonl",
                "figshare/doi-map.json", "scripts/maintenance/gate_log.py"):
        assert br.i_faktor([sti]) == 4, sti
    # auth/ er proveniens i dette repoet, ikke credential: mappenavnet alene
    # skal ikke gi I=4 og privilegium-trigger.
    assert br.i_faktor(["auth/orcid.json"]) == 2
    assert "privilegium" not in br.triggere(["auth/orcid.json"], False)
    assert br.i_faktor([]) == 1
    assert br.i_faktor(["governance/x.json", "tests/y.py"]) == 4


def test_score_og_klasse_baand():
    assert br.score(1, 1, 1, 1) == 1
    assert br.score(4, 4, 4, 4) == 256
    for tall, forventet in ((1, "liten"), (3, "liten"), (4, "material"),
                            (7, "material"), (8, "høy"), (15, "høy"),
                            (16, "kritisk"), (31, "kritisk"),
                            (32, "blokkerende"), (256, "blokkerende")):
        assert br.klasse(tall, []) == forventet, tall


def test_trigger_overstyrer_scoren():
    assert br.klasse(4, ["gate-endring"]) == "blokkerende"
    assert br.klasse(1, ["ukjent-grenseflate"]) == "kritisk"
    assert br.klasse(1, ["privilegium"]) == "blokkerende"
    assert br.triggere(["figshare/doi-map.json"], False) == ["produksjon"]
    assert br.triggere(["scripts/x.py"], True) == ["ukjent-grenseflate"]
    assert br.triggere(["tests/x.py"], False) == []


def test_registerklasse_mapping():
    assert [br.registerklasse(k) for k in ("liten", "material", "høy", "kritisk", "blokkerende")] \
        == ["grønn", "gul", "gul", "rød", "rød"]


# --- ende-til-ende mot et ekte (lite) git-repo ----------------------------

def test_cli_maaler_faktorene_og_gir_material(tmp_path):
    rot = _git_rot(tmp_path, {"scripts/a.py": "x\n", "tests/test_a.py": "y\n"})
    (rot / "scripts" / "a.py").write_text("x2\n", encoding="utf-8")
    (rot / "tests" / "test_a.py").write_text("y2\n", encoding="utf-8")
    r = _kall(rot, "--diff", "HEAD", "--json")
    assert r.returncode == 0, r.stderr
    ut = json.loads(r.stdout)
    assert ut["faktorer"] == {"F": 2, "E": 2, "P": 1, "I": 1}
    assert ut["score"] == 4 and ut["klasse"] == "material"
    assert sorted(ut["filer"]) == ["scripts/a.py", "tests/test_a.py"]
    assert ut["gate"]["oppfylt"] is False


def test_cli_utracket_fil_telles_med(tmp_path):
    rot = _git_rot(tmp_path, {"scripts/a.py": "x\n"})
    (rot / "tests").mkdir(exist_ok=True)
    (rot / "tests" / "ny.py").write_text("ny\n", encoding="utf-8")
    ut = json.loads(_kall(rot, "--diff", "HEAD", "--json").stdout)
    assert "tests/ny.py" in ut["filer"], "en kjøring før commit skal se nye filer"


def test_cli_ukjent_eier_gir_E4_og_kritisk(tmp_path):
    rot = _git_rot(tmp_path, {"ukjent/x.py": "x\n"})
    (rot / "ukjent" / "x.py").write_text("x2\n", encoding="utf-8")
    ut = json.loads(_kall(rot, "--diff", "HEAD", "--json").stdout)
    assert ut["ukjent_eier"] is True and ut["faktorer"]["E"] == 4
    assert ut["klasse"] == "kritisk", "ukjent grenseflate er en kritisk trigger"


def test_cli_gate_nekter_uten_og_slipper_med_menneskelig_beslutning(tmp_path):
    rot = _git_rot(tmp_path, {".github/workflows/y.yml": "on: push\n"})
    (rot / ".github" / "workflows" / "y.yml").write_text("on: pull_request\n", encoding="utf-8")
    r = _kall(rot, "--diff", "HEAD", "--json", "--gate", "--change-id", "t_deadbeef")
    ut = json.loads(r.stdout)
    assert ut["klasse"] == "blokkerende" and ut["triggere"] == ["gate-endring"]
    assert r.returncode == 1, "gaten skal nekte uten menneskelig beslutning"

    post = dict(GYLDIG_POST)
    post.update({"gate_decision": "godkjent", "gate_besluttet_av": "menneske"})
    (rot / "governance" / "risiko" / "risiko-register.jsonl").write_text(
        json.dumps(post, ensure_ascii=False) + "\n", encoding="utf-8")
    r2 = _kall(rot, "--diff", "HEAD", "--json", "--gate", "--change-id", "t_deadbeef")
    ut2 = json.loads(r2.stdout)
    assert ut2["gate"]["oppfylt"] is True and ut2["gate"]["risk_id"] == "RISK-BLAST_RADIUS-0001"
    assert r2.returncode == 0


def test_cli_slettet_fil_telles_med(tmp_path):
    """En sletting er den mest irreversible endringen — den skal ikke kunne
    forsvinne ut av målingen fordi den ikke er en «endring» i filtrets øyne."""
    rot = _git_rot(tmp_path, {"docs/public/side.html": "<h1>krav</h1>\n"})
    (rot / "docs" / "public" / "side.html").unlink()
    ut = json.loads(_kall(rot, "--diff", "HEAD", "--json").stdout)
    assert ut["antall_filer"] == 1 and "docs/public/side.html" in ut["filer"]
    assert ut["faktorer"]["P"] == 3, "en slettet offentlig side er fortsatt offentlig flate"


def test_cli_tom_diff_er_liten_men_ukjent_ref_er_verktoyfeil(tmp_path):
    rot = _git_rot(tmp_path, {"scripts/a.py": "x\n"})
    ut = json.loads(_kall(rot, "--diff", "HEAD", "--json").stdout)
    assert ut["antall_filer"] == 0 and ut["klasse"] == "liten"
    r = _kall(rot, "--diff", "finnes-ikke-ref", "--json")
    assert r.returncode == 2, "en måling som ikke kunne gjøres er ikke «ingen risiko»"
    assert json.loads(r.stdout)["feil"][0]["type"] == "tool_error"


def test_eiere_og_komponenter_oversetter_stier_til_ids():
    eiere, ider, ukjent = br.eiere_og_komponenter(["tests/a.py", "scripts/b.py"], EIERREGISTER)
    assert sorted(ider) == ["skript", "tester"] and ukjent is False
    assert sorted(eiere) == ["orchestrator", "researcher"]
    _, _, ukjent2 = br.eiere_og_komponenter(["public/graph/x.yaml"], EIERREGISTER)
    assert ukjent2 is True
