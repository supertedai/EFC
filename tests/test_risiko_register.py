"""Tests for the risk-register validator (t_882cfca, phase 1).

Every rule is tested with ONE mutation at a time against a valid entry, so the
reported error KIND can be read: a validator that is only tested on a valid entry
is a validator that has not been tried. Finally the real register in the tree is
validated, and append-only is tried against a real (small) git repo.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_risk_register as vr  # noqa: E402
from _gitmiljo import rent_gitmiljo  # noqa: E402

EIERREGISTER = {
    "owners": ["orchestrator", "researcher", "faber", "menneske"],
    "components": [
        {"id": "rotfiler", "owner": "orchestrator", "coverage_glob": ["governance/**"]},
        {"id": "vedlikeholdsskript", "owner": "orchestrator", "coverage_glob": ["scripts/**"]},
        {"id": "offentlige-sider", "owner": "researcher", "coverage_glob": ["docs/public/**"]},
    ],
}

GYLDIG = {
    "risk_id": "RISK-BLAST_RADIUS-0001", "type": "BLAST_RADIUS",
    "hazard_or_deviation": "gate-endring", "source_change_id": "t_f882cfca",
    "release_id": None, "berorte_komponenter": ["rotfiler"],
    "arsak": "årsak", "konsekvens": "konsekvens", "barrierer": ["barriere"],
    "sannsynlighet": "middels", "alvorlighet": "høy", "blast_radius_score": 24,
    "klasse": "rød", "eier": "orchestrator", "utforer": "faber",
    "reviewer": "ekstern-attestant", "status": "oppdaget", "tiltak": ["tiltak"],
    "kanban_card_id": "t_f882cfca", "gate_required": True,
    "gate_decision": "venter", "evidenslenker":
        ["repo:scripts/maintenance/validate_risk_register.py"],
    "opprettet_tid": "2026-09-17T07:30:00+00:00", "forfall": None,
    "sist_vurdert": "2026-09-17", "rest_risiko": "rest", "supersedes": [],
    "related_ids": [], "registerversjon": "1.0",
}


def _feil(**endringer: object) -> set[str]:
    post = copy.deepcopy(GYLDIG)
    post.update(endringer)
    return {f["type"] for f in vr.valider_post(post, 1, EIERREGISTER, {GYLDIG["risk_id"]})}


def test_gyldig_post_er_ren():
    assert vr.valider_post(copy.deepcopy(GYLDIG), 1, EIERREGISTER,
                           {GYLDIG["risk_id"]}) == []


def test_skjema_er_lukket():
    post = copy.deepcopy(GYLDIG)
    del post["arsak"]
    assert "missing_field" in {f["type"] for f in vr.valider_post(post, 1, EIERREGISTER, set())}
    assert "unknown_field" in _feil(ekstra_felt="hmm")
    assert "bad_type" in _feil(blast_radius_score="24")
    assert "bad_type" in _feil(barrierer="barriere")
    assert "bad_type" in _feil(gate_required="ja")


def test_enumer_og_versjon_er_lukket():
    assert "bad_enum" in _feil(klasse="oransje")
    assert "bad_enum" in _feil(type="HVA_SOM_HELST")
    assert "bad_enum" in _feil(status="ferdig")
    assert "bad_enum" in _feil(gate_decision="kanskje")
    assert "unknown_registerversjon" in _feil(registerversjon="9.9")
    assert "bad_risk_id" in _feil(risk_id="RISK-1")
    assert "risk_id_type_mismatch" in _feil(risk_id="RISK-HAZID-0001")
    assert "bad_kanban_card_id" in _feil(kanban_card_id="kort-1")
    assert "bad_source_change_id" in _feil(source_change_id="litt lost")


def test_klassen_kan_aldri_vaere_laxere_enn_scoren():
    assert "klasse_laxere_enn_score" in _feil(blast_radius_score=16, klasse="gul")
    assert "klasse_laxere_enn_score" in _feil(blast_radius_score=16, klasse="grønn")
    assert "klasse_laxere_enn_score" in _feil(blast_radius_score=4, klasse="grønn")
    assert _feil(blast_radius_score=3, klasse="grønn") == set(), "3 er lovlig grønn"
    assert _feil(blast_radius_score=3, klasse="rød") == set(), "strengere er lov"
    assert "score_out_of_range" in _feil(blast_radius_score=0)
    assert "score_out_of_range" in _feil(blast_radius_score=257)


def test_gaten_kan_ikke_lukkes_av_automatikk():
    assert "rod_uten_gate" in _feil(klasse="rød", gate_required=False)
    assert "gate_krevd_men_ikke_nodvendig" in _feil(gate_decision="ikke_nodvendig")
    assert "gate_ikke_krevd_men_besluttet" in _feil(gate_required=False, gate_decision="venter")
    assert "lukket_uten_gatebeslutning" in _feil(status="lukket")
    assert "gate_besluttet_av_ikke_menneske" in _feil(
        gate_decision="godkjent", gate_besluttet_av="faber")
    assert _feil(gate_decision="godkjent", gate_besluttet_av="menneske") == set()
    assert _feil(status="lukket", gate_decision="avslått", gate_besluttet_av="menneske") == set()


def test_ingen_selv_review_og_kjente_eiere():
    assert "selv_review" in _feil(reviewer="faber")
    assert _feil(reviewer="ekstern-attestant") == set()
    assert "ukjent_eier" in _feil(eier="hvemsomhelst")
    assert "ukjent_komponent" in _feil(berorte_komponenter=["finnes-ikke"])


def test_evidenslenker_ma_resolvere():
    assert "evidens_uten_prefiks" in _feil(evidenslenker=["scripts/maintenance/blast_radius.py"])
    assert "evidens_sti_finnes_ikke" in _feil(evidenslenker=["repo:scripts/finnes-ikke.py"])
    assert "evidens_url_ugyldig" in _feil(evidenslenker=["url:ftp://x/y"])
    assert "evidens_ekstern_tom" in _feil(evidenslenker=["ekstern:   "])
    assert _feil(evidenslenker=["ekstern:/utenfor/treet.md#1", "url:https://example.org/x"]) == set()


def test_tid_dato_og_referanser():
    assert "ugyldig_tid" in _feil(opprettet_tid="i går")
    assert "ugyldig_dato" in _feil(forfall="2026-13-45")
    assert _feil(forfall=None) == set(), "null = ingen avtalt frist"
    assert "ukjent_referanse" in _feil(related_ids=["RISK-GAP-9999"])
    assert "selvreferanse" in _feil(related_ids=[GYLDIG["risk_id"]])


def test_fil_validering_duplikat_og_ukjent_innhold(tmp_path):
    register = tmp_path / "risiko-register.jsonl"
    linje = json.dumps(GYLDIG, ensure_ascii=False)
    register.write_text(linje + "\n" + linje + "\n", encoding="utf-8")
    feil = vr.valider_innhold(register, EIERREGISTER, tmp_path)
    assert "duplicate_risk_id" in {f["type"] for f in feil}

    register.write_text("{not json}\n", encoding="utf-8")
    assert "invalid_json" in {f["type"] for f in vr.valider_innhold(register, EIERREGISTER, tmp_path)}

    assert "missing_file" in {f["type"] for f in
                              vr.valider_innhold(tmp_path / "nei.jsonl", EIERREGISTER, tmp_path)}


def test_registerets_egne_filer_ma_ha_eier(tmp_path):
    (tmp_path / "governance" / "risiko").mkdir(parents=True)
    (tmp_path / "governance" / "risiko" / "risiko-register.jsonl").write_text(
        json.dumps(GYLDIG, ensure_ascii=False) + "\n", encoding="utf-8")
    uten = {"owners": ["orchestrator"], "components": [
        {"id": "annet", "owner": "orchestrator", "coverage_glob": ["annet/**"]}]}
    feil = vr.valider_innhold(tmp_path / "governance" / "risiko" / "risiko-register.jsonl",
                              uten, tmp_path)
    assert any(f["type"] == "unowned_file" and
               f["file"] == "governance/risiko/risiko-register.jsonl" for f in feil), feil
    covering = {"owners": ["orchestrator"], "components": [
        {"id": "rotfiler", "owner": "orchestrator", "coverage_glob": ["governance/**"]}]}
    assert vr.valider_innhold(tmp_path / "governance" / "risiko" / "risiko-register.jsonl",
                              covering, tmp_path) == []


def _git(*args: str, cwd: Path, miljo: dict[str, str]) -> subprocess.CompletedProcess:
    """One git call with the test's own environment — see `_gitmiljo.py`."""
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@e.org", *args],
                          cwd=cwd, env=miljo, capture_output=True, text=True, check=True)


def _git_repo(tmp_path: Path) -> tuple[str, dict[str, str]]:
    """A fresh, small git repo with the register in the first commit.

    Returns (base sha, environment). The home directory lives in `tmp_path`,
    and GIT_DIR/GIT_* are scrubbed away: the outcome shall come from this
    fixture, not from what other tests or the machine happened to set.
    """
    miljo = rent_gitmiljo(tmp_path / "hjem")
    _git("init", "-q", cwd=tmp_path, miljo=miljo)
    _git("add", "-A", cwd=tmp_path, miljo=miljo)
    _git("commit", "-qm", "base", cwd=tmp_path, miljo=miljo)
    return _git("rev-parse", "HEAD", cwd=tmp_path, miljo=miljo).stdout.strip(), miljo


def test_append_only_er_en_git_egenskap(tmp_path):
    register = tmp_path / "governance" / "risiko" / "risiko-register.jsonl"
    register.parent.mkdir(parents=True)
    register.write_text(json.dumps(GYLDIG, ensure_ascii=False) + "\n", encoding="utf-8")
    base, miljo = _git_repo(tmp_path)

    assert vr.append_only(base, tmp_path) == []
    register.write_text(register.read_text(encoding="utf-8") +
                        json.dumps({**GYLDIG, "risk_id": "RISK-GAP-0002", "type": "GAP",
                                    "related_ids": ["RISK-BLAST_RADIUS-0001"]},
                                   ensure_ascii=False) + "\n", encoding="utf-8")
    assert vr.append_only(base, tmp_path) == [], "a new line is allowed"

    _git("commit", "-qam", "add", cwd=tmp_path, miljo=miljo)
    register.write_text(json.dumps({**GYLDIG, "rest_risiko": "changed"}, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    feil = vr.append_only(base, tmp_path)
    assert [f["type"] for f in feil] == ["not_append_only"], feil
    assert vr.append_only("finnes-ikke", tmp_path)[0]["type"] == "tool_error"


def test_append_only_tillater_gatebeslutning_men_ikke_annet(tmp_path):
    """The human decision path is the ONE exception to append-only.

    F1: flipping the closing fields (status, gate_decision, gate_besluttet_av,
    sist_vurdert) on a post is allowed — that is the human's gate decision.
    Everything else (changing another field, deletion) is still forbidden.
    """
    register = tmp_path / "governance" / "risiko" / "risiko-register.jsonl"
    register.parent.mkdir(parents=True)
    register.write_text(json.dumps(GYLDIG, ensure_ascii=False) + "\n", encoding="utf-8")
    base, _ = _git_repo(tmp_path)

    # (a) beslutningen: flip av lukkefeltene på posten — lovlig.
    besluttet = {**GYLDIG, "status": "lukket", "gate_decision": "godkjent",
                 "gate_besluttet_av": "menneske", "sist_vurdert": "2026-09-18"}
    register.write_text(json.dumps(besluttet, ensure_ascii=False) + "\n", encoding="utf-8")
    assert vr.append_only(base, tmp_path) == [], "the gate decision is the one exception"

    # (b) another field (rest_risiko) changed without a decision — still forbidden.
    register.write_text(json.dumps({**GYLDIG, "rest_risiko": "rewritten"},
                                   ensure_ascii=False) + "\n", encoding="utf-8")
    assert [f["type"] for f in vr.append_only(base, tmp_path)] == ["not_append_only"]

    # (c) a post deleted — still forbidden.
    register.write_text("", encoding="utf-8")
    assert [f["type"] for f in vr.append_only(base, tmp_path)] == ["not_append_only"]


def test_gaten_kan_ikke_blindes_av_lokal_git_konfigurasjon(tmp_path, monkeypatch):
    """The register's append-only gate must not be blindable from outside.

    A git configuration outside the process can swap out the diff itself:
    `diff.external` (or GIT_EXTERNAL_DIFF) runs an arbitrary command instead of
    git, a textconv driver can empty the content, and a diff driver with
    `binary = true` lets git answer «Binary files differ» without any removed
    lines. Then the gate sees no removed lines — and a real line break on the
    register would have passed with exit 0. Measured 2026-09-18: all three
    channels did exactly that.

    The canaries are deliberate: they prove FIRST that the poisoning works on a
    raw `git diff`. Without them the test could go green because the channel was
    stengt et annet sted enn i gaten.
    """
    register = tmp_path / "governance" / "risiko" / "risiko-register.jsonl"
    register.parent.mkdir(parents=True)
    register.write_text(json.dumps(GYLDIG, ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / ".gitattributes").write_text("*.jsonl diff=jsonl\n", encoding="utf-8")
    base, miljo = _git_repo(tmp_path)

    # The violation: rest_risiko (outside the closing fields) is rewritten — nothing is added.
    register.write_text(json.dumps({**GYLDIG, "rest_risiko": "rewritten"},
                                   ensure_ascii=False) + "\n", encoding="utf-8")

    # --- Channel 1: diff.external (GIT_EXTERNAL_DIFF) + textconv. ---
    forgiftet = tmp_path / "forgiftet-gitconfig"
    forgiftet.write_text("[diff]\n\texternal = /bin/true\n"
                         "[diff \"jsonl\"]\n\ttextconv = /bin/true\n", encoding="utf-8")
    kanar = {**miljo, "GIT_CONFIG_GLOBAL": str(forgiftet),
             "GIT_EXTERNAL_DIFF": "/bin/true"}
    raa = subprocess.run(["git", "diff", "-U0", base, "--",
                          "governance/risiko/risiko-register.jsonl"],
                         cwd=tmp_path, env=kanar, capture_output=True, text=True, check=True)
    assert not [ln for ln in raa.stdout.splitlines()
                if ln.startswith("-") and not ln.startswith("---")], \
        "the canary is not blind — then this probe measures nothing"

    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(forgiftet))
    monkeypatch.setenv("GIT_EXTERNAL_DIFF", "/bin/true")
    feil = vr.append_only(base, tmp_path)
    assert [f["type"] for f in feil] == ["not_append_only"], feil

    # --- Channel 2: a diff driver with binary = true. ---
    # `.gitattributes` in the tree points `*.jsonl` at the driver `jsonl`;
    # with `binary = true` git answers "Binary files differ" instead
    # to show removed lines. --no-ext-diff and --no-textconv do not close
    # this — only --text does (measured: git 2.53.0).
    binaer = tmp_path / "binaer-gitconfig"
    binaer.write_text("[diff \"jsonl\"]\n\tbinary = true\n", encoding="utf-8")
    binaer_kanar = {k: v for k, v in miljo.items() if k != "GIT_EXTERNAL_DIFF"}
    binaer_kanar["GIT_CONFIG_GLOBAL"] = str(binaer)
    raa2 = subprocess.run(["git", "diff", "-U0", "--no-ext-diff", "--no-textconv",
                           base, "--", "governance/risiko/risiko-register.jsonl"],
                          cwd=tmp_path, env=binaer_kanar, capture_output=True,
                          text=True, check=True)
    assert not [ln for ln in raa2.stdout.splitlines()
                if ln.startswith("-") and not ln.startswith("---")], \
        "the binary canary is not blind — then this probe measures nothing"

    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(binaer))
    monkeypatch.delenv("GIT_EXTERNAL_DIFF", raising=False)
    feil = vr.append_only(base, tmp_path)
    assert [f["type"] for f in feil] == ["not_append_only"], feil


def test_det_ekte_registeret_validerer():
    """Readback of the register in the tree — not only of a fixture."""
    register = ROT / "governance" / "risiko" / "risiko-register.jsonl"
    eierregister = json.loads((ROT / "governance" / "ownership-register.json").read_text(
        encoding="utf-8"))
    feil = vr.valider_innhold(register, eierregister, ROT)
    assert feil == [], feil
    linjer = [json.loads(x) for x in register.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(linjer) == 2
    assert {p["type"] for p in linjer} == {"HAZID", "BLAST_RADIUS"}
    for p in linjer:
        assert p["gate_required"] is True and p["gate_decision"] == "venter", \
            "an open red post shall wait for the human, not for the automation"
