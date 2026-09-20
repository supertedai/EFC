"""Real CLI tests for the atlas retain entrance — the queue, the threshold, the loop.

Three layers, three questions (card t_3fdc14b7):

  1. THE QUEUE.     Does the fragment enter the queue with source and time?
                    (PR #529 — the tests below are the same.)
  2. THE THRESHOLD. Is the verdict node-worthy EXPLICITLY, and does it say no
                    with a reason when the answer is no? A threshold that cannot
                    be read is a reminder — not a threshold.
  3. THE LOOP.      Can the one who entered the fragment CONFIRM that it got in —
                    against the atlas, not against the queue? The queue is the
                    working memory; the atlas is the truth. Without this link the
                    intake is a note.

The fragments are English, like the atlas they are placed in (t_648190ca).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CLI = REPO / "scripts" / "atlas_lesing.py"

sys.path.insert(0, str(REPO / "scripts"))
import atlas_lesing as L  # noqa: E402

from atlas_lesing import NODE_TERSKEL, bekreft, node_verdig  # noqa: E402


def kjør_inntak(tmp_path: Path, tekst: str, kilde: str) -> subprocess.CompletedProcess[str]:
    """Run the real CLI against an isolated intake area."""
    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    # The CLI uses the repo's data/inntak; the test's repo is therefore a copy of
    # only the intake area, via the environment variable in the public function.
    return subprocess.run(
        [PYTHON, str(CLI), str(REPO), "--ref", "HEAD", "--innta", tekst,
         "--kilde", kilde, "--inntak-fil", str(data / "atlas_fragmenter.jsonl")],
        cwd=REPO, capture_output=True, text=True, check=False,
    )


def les_linjene(sti: Path) -> list[dict]:
    return [json.loads(linje) for linje in sti.read_text(encoding="utf-8").splitlines()]


def test_innta_skriver_ekte_plassering_med_kilde_og_tidspunkt(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    resultat = kjør_inntak(tmp_path, "volcanic ash in the stratosphere", "samtale")

    assert resultat.returncode == 0, resultat.stderr
    assert "written to" in resultat.stdout
    record = les_linjene(fil)[0]
    assert record["tekst"] == "volcanic ash in the stratosphere"
    assert record["kilde"] == "samtale"
    assert record["tidspunkt"]
    assert record["plasseringsstatus"] == "uten_hjem"
    assert record["forslag"][0]["noder"] == ["kosmos.jord.vulkan"]


def test_innta_ukjent_fragment_blir_arlig_uten_hjem(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    resultat = kjør_inntak(tmp_path, "kwisatz haderach", "test")

    assert resultat.returncode == 0, resultat.stderr
    record = les_linjene(fil)[0]
    assert record["plasseringsstatus"] == "uten_hjem"
    assert record["domene_visshet"] == "ingen_anelse"
    assert record["kilde"] == "test"


def test_innta_er_append_only_for_to_fragmenter(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    første = kjør_inntak(tmp_path, "volcanic ash in the stratosphere", "samtale")
    andre = kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    assert første.returncode == andre.returncode == 0
    linjer = les_linjene(fil)
    assert len(linjer) == 2
    assert [x["tekst"] for x in linjer] == [
        "volcanic ash in the stratosphere", "kwisatz haderach"
    ]


# ---------------------------------------------------------------------------
# THE THRESHOLD — not everything is node-worthy, and the answer shall be explicit
# ---------------------------------------------------------------------------

def _statusser_i_plasser() -> set[str]:
    """The statuses `plasser()` can actually answer, read from the source.

    The test shall fell a NEW status nobody has taken a position on — not just
    the four we remembered when we wrote it. The answers are therefore read out
    of the function itself.
    """
    src = (REPO / "scripts" / "atlas_lesing.py").read_text(encoding="utf-8")
    kropp = src.split("def plasser(")[1].split("\ndef ")[0]
    return (set(re.findall(r'status = "([a-z_]+)"', kropp))
            | set(re.findall(r'"status": "([a-z_]+)"', kropp)))


def test_terskelen_dekker_hver_status_plasseringen_kan_svare() -> None:
    statusser = _statusser_i_plasser()
    assert statusser, "found no statuses in plasser() — the test measures nothing"
    udekket = statusser - set(NODE_TERSKEL)
    assert not udekket, (
        f"plasser() can answer {sorted(udekket)}, which no threshold takes a "
        f"position on — then the verdict becomes an omission")


def test_terskelen_svarer_nei_med_grunn_og_ukjent_status_avvises() -> None:
    for status, (dom, grunn) in NODE_TERSKEL.items():
        assert isinstance(dom, bool), f"{status}: the verdict is not a yes/no"
        assert grunn.strip(), f"{status}: a no without a reason is an omission"

    ukjent = node_verdig({"status": "noe-nytt"})
    assert ukjent["node_verdig"] is False
    assert "noe-nytt" in ukjent["grunn"], "the unknown status is not named"


def test_innta_skriver_terskelen_med_fragmentet(tmp_path: Path) -> None:
    """Two real fragments: one the atlas owns a domain for, one it does not know."""
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    kjør_inntak(tmp_path, "energi", "samtale")
    kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    eid, lost = les_linjene(fil)
    assert eid["terskel"] == "hjem_funnet" and eid["node_verdig"] is True
    assert lost["terskel"] == "uten_hjem" and lost["node_verdig"] is False
    assert lost["terskel_grunn"], "the no stands without a reason in the queue"


def test_terskelutskriften_sier_nei_med_grunn(tmp_path: Path) -> None:
    r = kjør_inntak(tmp_path, "kwisatz haderach", "test")
    assert "NOT node-worthy" in r.stdout
    assert "uten_hjem" in r.stdout
    assert "no domain owner" in r.stdout


def test_plasser_ser_alle_domenene_ikke_bare_de_seks_forste() -> None:
    """MEASURED 2026-09-18: 39 distinct `buss_domene` in the bank, but plasser()
    read the candidate list from `akser()`, which truncates the sample values to
    six. Only the first six ALPHABETICALLY could thereby give `hjem_funnet` —
    «energi» answered «ingen anelse» while `verden.energi` stood in the bank. A
    display limit shall not decide what the atlas knows."""
    atlas = L.les_atlas(REPO, ref="HEAD")
    domener = sorted({n["buss_domene"] for n in atlas["noder"]
                      if n.get("buss_domene")})
    assert len(domener) > 6, "premise: the bank has more than six domains"

    p = L.plasser(atlas, "energi")
    assert p["status"] == "hjem_funnet", (
        "a domain that stands in the bank was not found — the candidate list is "
        "still truncated")
    assert p["domene_visshet"] == "vet"
    assert any(f["domene"] == "verden.energi" for f in p["forslag"])


# ---------------------------------------------------------------------------
# THE CLOSED LOOP — did the fragment get in, and is it visible in the atlas?
# ---------------------------------------------------------------------------

def test_bekreft_sier_ikke_inne_for_et_fragment_atlaset_ikke_baerer() -> None:
    sv = L.bekreft_fra_ref(REPO, "kwisatz haderach", ref="HEAD")
    assert sv["dom"] == "ikke_inne"
    assert sv["kom_inn"] is False
    assert sv["atlas"]["ref"] == "HEAD"
    assert len(sv["atlas"]["commit"]) == 40, "the atlas does not name the commit"


def test_bekreft_sier_inne_og_navngir_noden_med_kode_og_kilde() -> None:
    """A real fragment the atlas carries: the triple point of water."""
    sv = L.bekreft_fra_ref(REPO, "the triple point of water", ref="HEAD")
    assert sv["dom"] == "inne" and sv["kom_inn"] is True
    node = sv["noder"][0]
    assert node["synlig"], "the node is not visible, but the verdict says «in»"
    assert node["kode"], "the generator would refuse to build the node (no code)"
    assert node["plassering"], "the node does not stand in PLASSERING"
    assert node["synlighet"] == "offentlig"
    assert node["ontology_source"], "a node in without ontology.source"


def test_andelsterskelen_er_grunnen_til_at_vulkansk_aske_ikke_er_inne() -> None:
    """MEASURED: «volcanic ash in the stratosphere» hits `kosmos.jord.vulkan` on
    ONE word — the volcano node carries the VHP status list, not the ash. With
    «at least one word» as the rule the answer would have been «in», and then a
    confirmation had confirmed a fragment. The test fells that mutant."""
    sv = L.bekreft_fra_ref(REPO, "volcanic ash in the stratosphere", ref="HEAD")
    assert sv["dom"] == "ikke_inne"
    naermest = sv["naermest"]
    assert naermest, "a near miss shall be named, not hidden"
    assert "kosmos.jord.vulkan" in naermest["noder"]
    assert naermest["andel"] <= sv["andel_krav"]


def test_uten_baseline_paastaas_ikke_at_treffet_er_nytt() -> None:
    """Without the intake's commit there is no «before» — and then the answer
    says nothing about novelty instead of guessing."""
    sv = L.bekreft_fra_ref(REPO, "the triple point of water", ref="HEAD")
    assert sv["for"] is None
    assert all(d["ny_siden_inntaket"] is None for d in sv["noder"])


def test_for_etter_skiller_en_ny_node_fra_en_som_laa_der() -> None:
    """Pure function: the same fragment, two banks — one with and one without the words."""
    def bank(noder):
        return {"kilde": "git:test", "ref": "test", "commit": "0" * 40,
                "noder": noder}

    gammel = bank([{"id": "a.b", "regime": {"name": "something else"},
                    "synlighet": "offentlig", "ontology": {"source": "s"}}])
    ny = bank([{"id": "a.b", "regime": {"name": "the triple point of water"},
                "synlighet": "offentlig", "ontology": {"source": "s"}}])
    gen = {"KODER": {"a.b": "AB"}, "PLASSERING": {"a.b": ("struktur", 5)}}

    uten = bekreft(gammel, "the triple point of water", gen)
    assert uten["dom"] == "ikke_inne"

    present = bekreft(ny, "the triple point of water", gen, atlas_for=gammel)
    assert present["dom"] == "inne"
    assert present["noder"][0]["ny_siden_inntaket"] is True
    assert present["for"]["noder_som_bar_ordene"] == []

    laa_der = bekreft(ny, "the triple point of water", gen, atlas_for=ny)
    assert laa_der["noder"][0]["ny_siden_inntaket"] is False


def _repo(med_generator: bool = True) -> Path:
    """A minimal git repo with a bank and (optionally) the generator tables."""
    import tempfile

    r = Path(tempfile.mkdtemp())
    (r / "schema").mkdir()
    (r / "schema" / "regime_nodes.jsonld").write_text(json.dumps({"nodes": [
        {"id": "a.b", "regime": {"name": "the triple point of water"},
         "synlighet": "offentlig", "ontology": {"source": "maalt"}}]}),
        encoding="utf-8")
    if med_generator:
        (r / "scripts" / "maintenance").mkdir(parents=True)
        (r / "scripts" / "maintenance" / "efc_atlas_generator.py").write_text(
            "KODER = {'a.b': 'AB'}\nPLASSERING = {'a.b': ('struktur', 5)}\n",
            encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"],
                ["-c", "user.name=t", "-c", "user.email=t@t",
                 "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", str(r), *cmd],
                       capture_output=True, text=True)
    return r


def test_bank_og_generatortabeller_leses_fra_refen_ikke_arbeidsstreet() -> None:
    """THE DECISIVE TEST — it changes the world, not the text.

    The generator's tables (KODER, PLASSERING) are what make a node VISIBLE.
    Read from the working tree, the confirmation answers from a different time
    than the bank it checks against: a fragment could stand as «visible» because
    the working tree was further ahead. The test poisons both files in the
    working tree and requires the answer to be BIT-FOR-BIT identical.
    """
    r = _repo()
    forst = L.bekreft_fra_ref(r, "the triple point of water", ref="HEAD")
    assert forst["dom"] == "inne" and forst["noder"][0]["kode"] == "AB"

    bank = r / "schema" / "regime_nodes.jsonld"
    gen = r / "scripts" / "maintenance" / "efc_atlas_generator.py"
    bank_opp, gen_opp = bank.read_bytes(), gen.read_bytes()
    try:
        bank.write_text(json.dumps({"nodes": [
            {"id": "a.b", "regime": {"name": "something entirely different"},
             "synlighet": "intern", "ontology": {}}]}), encoding="utf-8")
        gen.write_text("KODER = {}\nPLASSERING = {}\n", encoding="utf-8")
        andre = L.bekreft_fra_ref(r, "the triple point of water", ref="HEAD")
    finally:
        bank.write_bytes(bank_opp)
        gen.write_bytes(gen_opp)

    assert forst == andre, "the answer changed when the working tree changed"
    assert "something entirely different" not in json.dumps(andre)


def test_uten_generatortabeller_paastaas_ikke_synlighet() -> None:
    """If the tables cannot be read, the answer says SO — it does not guess «visible»."""
    r = _repo(med_generator=False)
    sv = L.bekreft_fra_ref(r, "the triple point of water", ref="HEAD")
    assert sv["dom"] == "i_banken_ikke_synlig"
    assert sv["kom_inn"] is False
    assert "KODER" in sv["grunn"]


def test_ulesbar_koelinje_kaster_i_stedet_for_aa_bli_stille_hoppet_over(
        tmp_path: Path) -> None:
    fil = tmp_path / "atlas_fragmenter.jsonl"
    fil.write_text('{"tekst": "a"}\n{not json}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        L.les_inntak(fil)


def test_cli_bekrefter_hele_koeen(tmp_path: Path) -> None:
    """One call: the queue read back and every fragment confirmed against the ref."""
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    kjør_inntak(tmp_path, "the triple point of water", "samtale")
    kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    r = subprocess.run(
        [PYTHON, str(CLI), str(REPO), "--ref", "HEAD", "--inntak-status",
         "--inntak-fil", str(fil)],
        cwd=REPO, capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
    assert "INNE —" in r.stdout and "IKKE_INNE" in r.stdout
    assert "1 inne av 2" in r.stdout
