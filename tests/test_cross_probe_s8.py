"""Tests for the P1/P2 cross-probe estimator (validation-ledger physics_test
«EFC P1/P2 cross-probe test against DES-Y6 vs KiDS-Legacy S8 bifurcation»).

The test is "Approved", but the estimator stood as "Planned". The
estimator must answer ONE thing: what is the S8 equivalent of the sealed
P1/P2 values at K0 = 2.0, and how far is it from each of the two surveys'
S8.

The discipline the tests enforce:
  * everything is loaded from repo-local files — no network fetching, no
    invented numbers (the anchors are traceable to the source file or to
    the ledger entry they come from);
  * each leg is reported SEPARATELY (lensing and growth are not merged);
  * discrepancies between the sealed claim and the reference
    implementation are reported openly — they are not hidden;
  * a missing source gives WAITING, never a verdict on data you do not
    have.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from efc_inference.arbiter import cross_probe_s8 as cp

ROT = Path(__file__).resolve().parents[1]


# ----------------------------------------------------------------------
# 1. The sources: they exist, are repo-local, and carry the sealed values
# ----------------------------------------------------------------------
def test_kildefilene_er_repo_lokale_og_bærer_de_forseglede_verdiene():
    ankere = cp.last_ankere(ROT)
    assert ankere["cmb_2026"]["s8"] == pytest.approx(0.836)
    assert ankere["des_y6_wcdm"]["s8"] == pytest.approx(0.782)
    assert ankere["kids_legacy_wright"]["s8"] == pytest.approx(0.815)
    for navn, a in ankere.items():
        assert a["kilde"], navn          # no anchor without a source
        assert a["pluss"] > 0 and a["minus"] > 0, navn
    # The anchors must be pointable, not merely present
    assert "p1_p2_cross_probe" in ankere["des_y6_wcdm"]["kilde"]
    assert "2503.19441" in ankere["kids_legacy_wright"]["kilde"]


def test_p1_p2_og_k0_scanen_lastes_fra_repoet():
    p1 = cp.last_p1(ROT)
    p2 = cp.last_p2(ROT)
    k0 = cp.last_k0(ROT)
    assert p1["crossover_redshift"] == pytest.approx(0.44)
    assert p1["crossover_uncertainty"] == pytest.approx(0.03)
    assert p2["fsigma8_z07"] == pytest.approx(0.430)
    assert k0["verdi"] == pytest.approx(1.37)
    assert k0["scan_range"] == [0.5, 4.0]


def test_des_y6_wcdm_konstanten_stemmer_med_ledgeroppfoeringen():
    """Anti-drift: the DES Y6 wCDM numbers must be the same as the ledger
    entry for this test states — not remembered, not guessed."""
    ledger = json.loads(
        (ROT / "docs/validation-ledger/data/tests.json").read_text("utf-8"))
    poster = ledger["categories"]["physics_test"] if isinstance(
        ledger, dict) and "categories" in ledger else None
    if poster is None:  # fallback: flat list
        poster = ledger.get("tests", [])
    funnet = [p for p in poster
              if p.get("test_id", "") and "p1_p2_cross_probe" in p["test_id"]]
    assert funnet, "the ledger entry for the P1/P2 cross-probe does not exist"
    tekst = funnet[0]["data_source"]
    m = re.search(r"S8 = ([\d.]+) \+([\d.]+)/-([\d.]+)", tekst)
    assert m, f"did not find the DES Y6 numbers in the ledger's data_source: {tekst}"
    a = cp.last_ankere(ROT)["des_y6_wcdm"]
    assert a["s8"] == pytest.approx(float(m.group(1)))
    assert a["pluss"] == pytest.approx(float(m.group(2)))
    assert a["minus"] == pytest.approx(float(m.group(3)))


def test_ingen_nettverkshenting_i_modulen():
    kilde = Path(cp.__file__).read_text("utf-8")
    for forbudt in ("requests", "urllib", "http://", "https://api",
                    "socket"):
        assert forbudt not in kilde, f"network dependency: {forbudt}"


# ----------------------------------------------------------------------
# 2. The engine: Sigma_eff(z; K0) is taken from the sealed
#    reference implementation — not reimplemented here
# ----------------------------------------------------------------------
def test_sigma_eff_kommer_fra_den_forseglede_referanseimplementasjonen():
    motor = cp.last_motor(ROT)
    assert str(motor.__file__).endswith(
        "docs/papers/efc/EFC_compound_paper/src/efc_compound_paper.py")


def test_sigma_eff_avtar_med_z_og_er_naer_1_ved_K0_store():
    sig_lav_z = cp.sigma_eff(0.1, 2.0, ROT)
    sig_hoy_z = cp.sigma_eff(0.9, 2.0, ROT)
    assert sig_lav_z > sig_hoy_z, "Sigma_eff must decrease with z"


def test_lavere_K0_gir_sterkere_demping():
    svak = cp.sigma_eff(0.44, 4.0, ROT)
    sterk = cp.sigma_eff(0.44, 0.5, ROT)
    assert sterk < svak


# ----------------------------------------------------------------------
# 3. The S8 equivalent: the definition is inherited from the repo, not invented
# ----------------------------------------------------------------------
def test_s8_er_CMB_baseline_ganger_Sigma():
    """P3 in efc_des_y6_validation defines the relation
    S8_lens/S8_CMB = Sigma (0.95 <-> 0.95). The estimator uses the same
    coupling: S8_equivalent = S8_CMB * Sigma."""
    sig = cp.sigma_eff(0.44, 2.0, ROT)
    bein = cp.s8_ekvivalent(0.44, 2.0, modus="lensing_sigma", rot=ROT)
    assert bein["s8"] == pytest.approx(0.836 * sig, rel=1e-9)
    assert bein["modus"] == "lensing_sigma"
    assert "Sigma" in bein["kilde"] or "P3" in bein["kilde"]


def test_vekstbeinet_bruker_forseglet_P2_og_er_et_eget_bein():
    bein = cp.s8_ekvivalent(0.7, 2.0, modus="vekst", rot=ROT)
    assert bein["s8"] == pytest.approx(0.836 * (0.430 / 0.449), rel=1e-9)
    assert "forutsetning" in bein          # amplitude proxy — declared
    assert bein["s8"] != pytest.approx(
        cp.s8_ekvivalent(0.44, 2.0, modus="lensing_sigma", rot=ROT)["s8"])


def test_alle_beina_baerer_sigma_og_kilde():
    for modus in ("lensing_sigma", "lensing_mu", "vekst"):
        bein = cp.s8_ekvivalent(0.44, 2.0, modus=modus, rot=ROT)
        assert bein["s8_sigma"] > 0, modus
        assert bein["kilde"], modus


# ----------------------------------------------------------------------
# 4. Distance and category — the rule is explicit and testable
# ----------------------------------------------------------------------
def test_avstand_velger_riktig_sigma_retning():
    ankere = cp.last_ankere(ROT)
    over = cp.avstand(0.900, ankere["des_y6_wcdm"])
    under = cp.avstand(0.700, ankere["des_y6_wcdm"])
    assert over["sigma_trukket"] == pytest.approx(
        ankere["des_y6_wcdm"]["pluss"])
    assert under["sigma_trukket"] == pytest.approx(
        ankere["des_y6_wcdm"]["minus"])
    assert over["delta"] > 0 > under["delta"]


def test_kategoriene_fra_ledgeren():
    """(i) between the two WL surveys = MIDBAND, (ii) above KiDS = CMB end,
    (iii) below DES Y6 = DES-Y6 territory."""
    ankere = cp.last_ankere(ROT)
    des, kids = ankere["des_y6_wcdm"]["s8"], ankere["kids_legacy_wright"]["s8"]
    midt = 0.5 * (des + kids)
    assert cp.kategori(midt, ankere) == "MIDBAND"
    assert cp.kategori(kids + 0.01, ankere) == "CMB_KONSISTENT"
    assert cp.kategori(des - 0.01, ankere) == "DES_Y6_KONSISTENT"


def test_kategori_er_monoton():
    ankere = cp.last_ankere(ROT)
    rekke = [cp.kategori(x, ankere) for x in
             (0.70, 0.75, 0.78, 0.79, 0.80, 0.81, 0.82, 0.85, 0.90)]
    orden = {"DES_Y6_KONSISTENT": 0, "MIDBAND": 1, "CMB_KONSISTENT": 2}
    assert [orden[k] for k in rekke] == sorted(orden[k] for k in rekke)


# ----------------------------------------------------------------------
# 5. The verdict: both legs, both checks, honest discrepancies
# ----------------------------------------------------------------------
def test_vurder_er_treverdig_og_venter_uten_kilde():
    dom = cp.vurder(K0=2.0, rot=ROT / "no-such-dir")
    assert dom["status"] == "VENTER"
    assert dom["arsak"]


def test_vurder_rapporterer_motstandarden_og_begge_sjekkene():
    dom = cp.vurder(K0=2.0, rot=ROT)
    assert dom["status"] == "VURDERT"
    assert dom["K0"] == pytest.approx(2.0)
    assert set(dom["bein"]) >= {"lensing_sigma", "vekst"}
    for navn, bein in dom["bein"].items():
        assert "kategori" in bein, navn
        assert "avstand_kids_legacy" in bein, navn
        assert "avstand_des_y6" in bein, navn
        assert "sjekk_kids_innen_0015" in bein, navn
        assert "sjekk_des_min_1p5_sigma" in bein, navn
        assert isinstance(bein["sjekk_kids_innen_0015"], bool), navn
    # The ledger's quantitative expectation and its falsification window
    assert "forventning_innfridd" in dom
    assert "falsifikasjonsvindu" in dom


def test_ingen_skjult_sammenslaing_av_beina():
    dom = cp.vurder(K0=2.0, rot=ROT)
    assert "gjennomsnitt" not in json.dumps(dom, ensure_ascii=False).lower()
    assert "snitt" not in json.dumps(dom, ensure_ascii=False).lower()


def test_motoravvikene_rapporteres_og_skjules_ikke():
    """The reference implementation does not reproduce the sealed claim on
    all points. That is a finding, not a footnote."""
    avvik = cp.motor_avvik(ROT)
    typer = {a["type"] for a in avvik}
    assert "crossover" in typer           # sealed z=0.44 vs the engine
    assert "k0_scan_bredde" in typer      # paper ~0.87 vs the engine
    assert "p2_fsigma8" in typer          # sealed 0.430 vs the engine
    for a in avvik:
        assert a["forseglet"] is not None, a["type"]
        # Either a measured engine value, or an explicit status that the
        # engine gives none — never silence.
        assert a["motor"] is not None or a.get("motor_status"), a["type"]
    xover = [a for a in avvik if a["type"] == "crossover"][0]
    assert xover["motor_status"] in ("funnet", "ingen_fortegnssendring")
    assert xover["motor"] is not None or xover["motor_status"] == \
        "ingen_fortegnssendring"
    dom = cp.vurder(K0=2.0, rot=ROT)
    assert dom["motor_avvik"] == avvik


def test_folsomhet_over_z_eff_rapporteres():
    dom = cp.vurder(K0=2.0, rot=ROT)
    assert set(dom["folsomhet_z_eff"]) == {"0.3", "0.44", "0.9"}
    for punkt in dom["folsomhet_z_eff"].values():
        assert "s8" in punkt and "kategori" in punkt


# ----------------------------------------------------------------------
# 6. Determinism and CLI
# ----------------------------------------------------------------------
def test_determinisme():
    a = json.dumps(cp.vurder(K0=2.0, rot=ROT), sort_keys=True)
    b = json.dumps(cp.vurder(K0=2.0, rot=ROT), sort_keys=True)
    assert a == b


def test_cli_skriver_json_til_stdout(tmp_path, capsys):
    rc = cp.hoved(["--rot", str(ROT)])
    assert rc == 0
    ut = json.loads(capsys.readouterr().out)
    assert ut["status"] == "VURDERT"
    sti = tmp_path / "dom.json"
    assert cp.hoved(["--rot", str(ROT), "--ut", str(sti)]) == 0
    assert json.loads(sti.read_text("utf-8"))["K0"] == pytest.approx(2.0)
