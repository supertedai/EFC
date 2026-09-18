"""Ekte CLI-tester for atlasets retain-inngang — koeen, terskelen og sloyfa.

Tre lag, tre sporsmaal (kort t_3fdc14b7):

  1. KOEEN.    Kommer fragmentet inn i keen med kilde og tidspunkt?
               (PR #529 — testene under er de samme.)
  2. TERSKELEN. Er svaret node-verdig EKSPLISITT, og sier det nei med en
               grunn naar svaret er nei? En terskel som ikke kan leses, er
               en paaminnelse — ikke en terskel.
  3. SLOYFA.   Kan den som la inn fragmentet BEKREFTE at det kom inn — mot
               atlaset, ikke mot keen? Koeen er arbeidsminnet; atlaset er
               sannheten. Uten dette leddet er inntaket et notat.
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
    # CLI-en bruker repoets data/inntak; testens repo er derfor en kopi av
    # bare inntaksomraadet via miljøvariabelen i den offentlige funksjonen.
    return subprocess.run(
        [PYTHON, str(CLI), str(REPO), "--ref", "HEAD", "--innta", tekst,
         "--kilde", kilde, "--inntak-fil", str(data / "atlas_fragmenter.jsonl")],
        cwd=REPO, capture_output=True, text=True, check=False,
    )


def les_linjene(sti: Path) -> list[dict]:
    return [json.loads(linje) for linje in sti.read_text(encoding="utf-8").splitlines()]


def test_innta_skriver_ekte_plassering_med_kilde_og_tidspunkt(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    resultat = kjør_inntak(tmp_path, "vulkansk aske i stratosfaeren", "samtale")

    assert resultat.returncode == 0, resultat.stderr
    assert "written to" in resultat.stdout
    record = les_linjene(fil)[0]
    assert record["tekst"] == "vulkansk aske i stratosfaeren"
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
    første = kjør_inntak(tmp_path, "vulkansk aske i stratosfaeren", "samtale")
    andre = kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    assert første.returncode == andre.returncode == 0
    linjer = les_linjene(fil)
    assert len(linjer) == 2
    assert [x["tekst"] for x in linjer] == [
        "vulkansk aske i stratosfaeren", "kwisatz haderach"
    ]


# ---------------------------------------------------------------------------
# TERSKELEN — ikke alt er node-verdig, og svaret skal vaere eksplisitt
# ---------------------------------------------------------------------------

def _statusser_i_plasser() -> set[str]:
    """Statusene `plasser()` faktisk kan svare, lest fra kilden.

    Testen skal felle en NY status som ingen har tatt stilling til — ikke
    bare de fire vi husket da vi skrev den. Derfor leses svarene ut av
    funksjonen selv.
    """
    src = (REPO / "scripts" / "atlas_lesing.py").read_text(encoding="utf-8")
    kropp = src.split("def plasser(")[1].split("\ndef ")[0]
    return (set(re.findall(r'status = "([a-z_]+)"', kropp))
            | set(re.findall(r'"status": "([a-z_]+)"', kropp)))


def test_terskelen_dekker_hver_status_plasseringen_kan_svare() -> None:
    statusser = _statusser_i_plasser()
    assert statusser, "fant ingen statusser i plasser() — testen maaler ingenting"
    udekket = statusser - set(NODE_TERSKEL)
    assert not udekket, (
        f"plasser() kan svare {sorted(udekket)}, som ingen terskel tar "
        f"stilling til — da blir dommen en utelatelse")


def test_terskelen_svarer_nei_med_grunn_og_ukjent_status_avvises() -> None:
    for status, (dom, grunn) in NODE_TERSKEL.items():
        assert isinstance(dom, bool), f"{status}: dommen er ikke et ja/nei"
        assert grunn.strip(), f"{status}: nei uten grunn er en utelatelse"

    ukjent = node_verdig({"status": "noe-nytt"})
    assert ukjent["node_verdig"] is False
    assert "noe-nytt" in ukjent["grunn"], "den ukjente statusen nevnes ikke"


def test_innta_skriver_terskelen_med_fragmentet(tmp_path: Path) -> None:
    """To ekte fragmenter: ett atlaset eier et domene for, ett det ikke vet om."""
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    kjør_inntak(tmp_path, "energi", "samtale")
    kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    eid, lost = les_linjene(fil)
    assert eid["terskel"] == "hjem_funnet" and eid["node_verdig"] is True
    assert lost["terskel"] == "uten_hjem" and lost["node_verdig"] is False
    assert lost["terskel_grunn"], "nei-et staar uten grunn i koeen"


def test_terskelutskriften_sier_nei_med_grunn(tmp_path: Path) -> None:
    r = kjør_inntak(tmp_path, "kwisatz haderach", "test")
    assert "NOT node-worthy" in r.stdout
    assert "uten_hjem" in r.stdout
    assert "no domain owner" in r.stdout


def test_plasser_ser_alle_domenene_ikke_bare_de_seks_forste() -> None:
    """MAALT 2026-09-18: 39 distinkte `buss_domene` i banken, men plasser()
    leste kandidatlisten fra `akser()`, som kapper eksempelverdiene til seks.
    Bare de seks forste ALFABETISK kunne dermed gi `hjem_funnet` — «energi»
    svarte «ingen anelse» mens `verden.energi` sto i banken. En
    visningsgrense skal ikke avgjore hva atlaset vet."""
    atlas = L.les_atlas(REPO, ref="HEAD")
    domener = sorted({n["buss_domene"] for n in atlas["noder"]
                      if n.get("buss_domene")})
    assert len(domener) > 6, "forutsetning: banken har flere enn seks domener"

    p = L.plasser(atlas, "energi")
    assert p["status"] == "hjem_funnet", (
        "et domene som staar i banken ble ikke funnet — kandidatlisten er "
        "fortsatt kappet")
    assert p["domene_visshet"] == "vet"
    assert any(f["domene"] == "verden.energi" for f in p["forslag"])


# ---------------------------------------------------------------------------
# DEN LUKKEDE SLOYFA — kom fragmentet inn, og er det synlig i atlaset?
# ---------------------------------------------------------------------------

def test_bekreft_sier_ikke_inne_for_et_fragment_atlaset_ikke_baerer() -> None:
    sv = L.bekreft_fra_ref(REPO, "kwisatz haderach", ref="HEAD")
    assert sv["dom"] == "ikke_inne"
    assert sv["kom_inn"] is False
    assert sv["atlas"]["ref"] == "HEAD"
    assert len(sv["atlas"]["commit"]) == 40, "atlaset navngir ikke commiten"


def test_bekreft_sier_inne_og_navngir_noden_med_kode_og_kilde() -> None:
    """Et ekte fragment atlaset baerer: vannets trippelpunkt."""
    sv = L.bekreft_fra_ref(REPO, "trippelpunktet for vann", ref="HEAD")
    assert sv["dom"] == "inne" and sv["kom_inn"] is True
    node = sv["noder"][0]
    assert node["synlig"], "noden er ikke synlig, men dommen sier «inne»"
    assert node["kode"], "generatoren ville nekket aa bygge noden (ingen kode)"
    assert node["plassering"], "noden staar ikke i PLASSERING"
    assert node["synlighet"] == "offentlig"
    assert node["ontology_source"], "en node inn uten ontology.source"


def test_andelsterskelen_er_grunnen_til_at_vulkansk_aske_ikke_er_inne() -> None:
    """MAALT: «vulkansk aske i stratosfaeren» treffer `kosmos.jord.vulkan` paa
    ETT ord — vulkannoden baerer VHP-statuslisten, ikke asken. Med «minst ett
    ord» som regel ville svaret vaert «inne», og da hadde en binding bekreftet
    et fragment. Testen feller den mutanten."""
    sv = L.bekreft_fra_ref(REPO, "vulkansk aske i stratosfaeren", ref="HEAD")
    assert sv["dom"] == "ikke_inne"
    naermest = sv["naermest"]
    assert naermest, "en naer-bom skal navngis, ikke skjules"
    assert "kosmos.jord.vulkan" in naermest["noder"]
    assert naermest["andel"] <= sv["andel_krav"]


def test_uten_baseline_paastaas_ikke_at_treffet_er_nytt() -> None:
    """Uten inntakets commit finnes ingen «for» — og da sier svaret ingenting
    om nyhet i stedet for aa gjette."""
    sv = L.bekreft_fra_ref(REPO, "trippelpunktet for vann", ref="HEAD")
    assert sv["for"] is None
    assert all(d["ny_siden_inntaket"] is None for d in sv["noder"])


def test_for_etter_skiller_en_ny_node_fra_en_som_laa_der() -> None:
    """Ren funksjon: samme fragment, to banker — én med og én uten ordene."""
    def bank(noder):
        return {"kilde": "git:test", "ref": "test", "commit": "0" * 40,
                "noder": noder}

    gammel = bank([{"id": "a.b", "regime": {"name": "noe annet"},
                    "synlighet": "offentlig", "ontology": {"source": "s"}}])
    ny = bank([{"id": "a.b", "regime": {"name": "trippelpunktet for vann"},
                "synlighet": "offentlig", "ontology": {"source": "s"}}])
    gen = {"KODER": {"a.b": "AB"}, "PLASSERING": {"a.b": ("struktur", 5)}}

    uten = bekreft(gammel, "trippelpunktet for vann", gen)
    assert uten["dom"] == "ikke_inne"

    med = bekreft(ny, "trippelpunktet for vann", gen, atlas_for=gammel)
    assert med["dom"] == "inne"
    assert med["noder"][0]["ny_siden_inntaket"] is True
    assert med["for"]["noder_som_bar_ordene"] == []

    laa_der = bekreft(ny, "trippelpunktet for vann", gen, atlas_for=ny)
    assert laa_der["noder"][0]["ny_siden_inntaket"] is False


def _repo(med_generator: bool = True) -> Path:
    """Et minimalt git-repo med bank og (valgfritt) generatortabeller."""
    import tempfile

    r = Path(tempfile.mkdtemp())
    (r / "schema").mkdir()
    (r / "schema" / "regime_nodes.jsonld").write_text(json.dumps({"nodes": [
        {"id": "a.b", "regime": {"name": "trippelpunktet for vann"},
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
    """DEN AVGJØRENDE TESTEN — endrer verden, ikke teksten.

    Generatorens tabeller (KODER, PLASSERING) er det som gjor en node SYNLIG.
    Leses de fra arbeidsstreet, svarer bekreftelsen fra en annen tid enn
    banken den sjekker mot: et fragment kunne sta som «synlig» fordi
    arbeidsstreet var lengre framme. Testen forgifter begge filene i
    arbeidsstreet og krever at svaret er BIT-FOR-BIT identisk.
    """
    r = _repo()
    forst = L.bekreft_fra_ref(r, "trippelpunktet for vann", ref="HEAD")
    assert forst["dom"] == "inne" and forst["noder"][0]["kode"] == "AB"

    bank = r / "schema" / "regime_nodes.jsonld"
    gen = r / "scripts" / "maintenance" / "efc_atlas_generator.py"
    bank_opp, gen_opp = bank.read_bytes(), gen.read_bytes()
    try:
        bank.write_text(json.dumps({"nodes": [
            {"id": "a.b", "regime": {"name": "noe helt annet"},
             "synlighet": "intern", "ontology": {}}]}), encoding="utf-8")
        gen.write_text("KODER = {}\nPLASSERING = {}\n", encoding="utf-8")
        andre = L.bekreft_fra_ref(r, "trippelpunktet for vann", ref="HEAD")
    finally:
        bank.write_bytes(bank_opp)
        gen.write_bytes(gen_opp)

    assert forst == andre, "svaret endret seg da arbeidsstreet endret seg"
    assert "noe helt annet" not in json.dumps(andre)


def test_uten_generatortabeller_paastaas_ikke_synlighet() -> None:
    """Kan tabellene ikke leses, sier svaret DET — det gjetter ikke «synlig»."""
    r = _repo(med_generator=False)
    sv = L.bekreft_fra_ref(r, "trippelpunktet for vann", ref="HEAD")
    assert sv["dom"] == "i_banken_ikke_synlig"
    assert sv["kom_inn"] is False
    assert "KODER" in sv["grunn"]


def test_ulesbar_koelinje_kaster_i_stedet_for_aa_bli_stille_hoppet_over(
        tmp_path: Path) -> None:
    fil = tmp_path / "atlas_fragmenter.jsonl"
    fil.write_text('{"tekst": "a"}\n{ikke json}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        L.les_inntak(fil)


def test_cli_bekrefter_hele_koeen(tmp_path: Path) -> None:
    """Ett kall: keen lest tilbake og hvert fragment bekreftet mot refen."""
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    kjør_inntak(tmp_path, "trippelpunktet for vann", "samtale")
    kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    r = subprocess.run(
        [PYTHON, str(CLI), str(REPO), "--ref", "HEAD", "--inntak-status",
         "--inntak-fil", str(fil)],
        cwd=REPO, capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
    assert "INNE —" in r.stdout and "IKKE_INNE" in r.stdout
    assert "1 inne av 2" in r.stdout
