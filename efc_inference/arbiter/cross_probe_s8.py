"""P1/P2 cross-probe-estimatoren (validation-ledger physics_test
«EFC P1/P2 cross-probe test against DES-Y6 vs KiDS-Legacy S8 bifurcation»).

Testen var «Approved» mens estimatoren sto som «Planned». Denne modulen er
estimatoren: den regner S8-ekvivalenten av EFCs forseglede P1/P2-verdier ved
en gitt K0 og måler avstanden til DES Y6 og KiDS Legacy — hver for seg,
fordi 2026-tallene ikke er samme måling av samme univers.

FORSEGLEDE ANKERE (endres aldri her — de leses):
  * P1 Sigma_eff(z)-crossover ved z ~ 0.44 — DOI 10.6084/m9.figshare.32037990
  * P2 f*sigma8(z=0.7) = 0.430            — DOI 10.6084/m9.figshare.32013156
  * K0-skanen (K0 = 1.37 standard, sok 0.5-4.0) — DOI 10.6084/m9.figshare.32080059

HVA ESTIMATOREN GJOR — og ikke gjor:
  * Den laster den forseglede referanseimplementasjonen av Sigma_eff(z; K0)
    (docs/papers/efc/EFC_compound_paper/src/efc_compound_paper.py) og
    BRUKER den. Fysikken reimplementeres ikke her — to kilder til samme
    ligning er den drift ADR-002 ble skrevet mot.
  * Den kobler Sigma til S8 med repoets egen P3-relasjon
    (S8_lens/S8_CMB = Sigma, se docs/papers/efc/efc_des_y6_validation) og
    leser S8_CMB fra repoets egen datafil. Ingen nye konstanter.
  * Den feller ingen dom om RCMP. Den rapporterer hvert bein for seg —
    linsing (Sigma_eff) og vekst (f*sigma8) — og hvilken av ledgerens tre
    utfallskategorier hvert bein lander i:
        (i)   MIDBAND            — mellom de to WL-surveyene
        (ii)  CMB_KONSISTENT     — paa den CMB-konsistente enden
        (iii) DES_Y6_KONSISTENT  — i DES-Y6-territoriet (svekker RCMP-
                                   argumentet, jf. testens falsifikasjonsvindu)
  * Den skjuler ikke avvik: referanseimplementasjonens standardparametre
    reproduserer ikke alle de forseglede tallene. De avvikene rapporteres i
    motor_avvik() og følger med i hver dom.
  * Manglende kilde gir VENTER — aldri en dom paa data man ikke har.

Alt leses repo-lokalt. Ingen nettverkshenting. Ingen datafiler skrives.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np

from efc_inference.arbiter.sealed_fs8 import ANKER_EFC, ANKER_LCDM

# ----------------------------------------------------------------------
#  Kilder (repo-lokale stier, relativt til repo-roten)
# ----------------------------------------------------------------------
ROT_STANDARD = Path(__file__).resolve().parents[2]

P1_PROFIL = Path("docs/papers/efc/efc_perturbation_sector/data/parameters.json")
DE_Y6_DATA = Path("docs/papers/efc/efc_des_y6_validation/data/des_y6_data.json")
KOMPOUND_DATA = Path("docs/papers/efc/EFC_compound_paper/data/parameters.json")
KOMPOUND_MOTOR = Path(
    "docs/papers/efc/EFC_compound_paper/src/efc_compound_paper.py")
LEDGER_TESTS = Path("docs/validation-ledger/data/tests.json")

P1_DOI = "10.6084/m9.figshare.32037990"
P2_DOI = "10.6084/m9.figshare.32013156"
K0_DOI = "10.6084/m9.figshare.32080059"

K0_TEST = 2.0                 # forventningen i ledgeren er formulert ved K0=2.0
Z_EFF_STANDARD = 0.44         # den forseglede sammenligningsredskiften (P1)
Z_EFF_FOLSOMHET = (0.30, 0.44, 0.90)   # P3-vinduet z ~ 0.3-0.9
Z_P2 = 0.7                    # den forseglede P2-redskiften

LOKALE_MODI = ("lensing_sigma", "lensing_mu", "vekst")

# Ledgerens kvantitative forventning (sitat, se tests.json for testen):
#   «K0=2.0 skal reprodusere S8-ekvivalent innen +/-0.015 av KiDS Legacy-
#    sentralverdi og ligge >=1.5 sigma fra DES-Y6.»
KIDS_TOLERANSE = 0.015
DES_MIN_AVSTAND_SIGMA = 1.5

KATEGORIER = ("MIDBAND", "CMB_KONSISTENT", "DES_Y6_KONSISTENT")


class Kildefeil(Exception):
    """En repo-lokal kilde mangler eller er uleselig — ingen dom felles."""


# ----------------------------------------------------------------------
#  Lasting av repo-lokale kilder
# ----------------------------------------------------------------------
def _les_json(rot: Path, relativ: Path) -> dict:
    sti = rot / relativ
    if not sti.exists():
        raise Kildefeil(f"mangler kildefil: {sti}")
    try:
        return json.loads(sti.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Kildefeil(f"uleselig kildefil {sti}: {exc}") from exc


def _ledger_poster(rot: Path) -> list[dict]:
    data = _les_json(rot, LEDGER_TESTS)
    kategorier = data.get("categories") or {}
    poster: list[dict] = []
    for verdi in kategorier.values():
        if isinstance(verdi, list):
            poster.extend(p for p in verdi if isinstance(p, dict))
    if not poster and isinstance(data.get("tests"), list):
        poster = [p for p in data["tests"] if isinstance(p, dict)]
    if not poster:
        raise Kildefeil(f"fant ingen testoppfoeringer i {LEDGER_TESTS}")
    return poster


def last_p1(rot: Optional[Path] = None) -> dict:
    """P1: den forseglede Sigma_eff-crossoveren (DOI 32037990).

    Crossoveren leses fra perturbationssektor-pakken og krysses mot
    regimetransisjons-artikkelen. Er de to ikke enige, felles ingen dom —
    to forseglede tall for samme storrelse skal ikke slaaes sammen i stillhet.
    """
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, P1_PROFIL)
    pred = data.get("predictions") or {}
    cross = (pred.get("crossover_redshift") or {}).get("value")
    band = ((data.get("parameters") or {}).get("tolerance_band") or {}).get(
        "value")
    if cross is None or band is None:
        raise Kildefeil(f"P1-verdiene mangler i {P1_PROFIL}")

    kompound = _les_json(rot, KOMPOUND_DATA).get("P1_lensing_sector") or {}
    kompound_cross = kompound.get("crossover_redshift")
    if kompound_cross is None:
        raise Kildefeil(f"P1-crossoveren mangler i {KOMPOUND_DATA}")
    if abs(float(kompound_cross) - float(cross)) > 1e-9:
        raise Kildefeil(
            "P1-crossoveren er ulik i de to forseglede kildene: "
            f"{cross} ({P1_PROFIL}) vs {kompound_cross} ({KOMPOUND_DATA})")

    return {
        "crossover_redshift": float(cross),
        "crossover_uncertainty": float(kompound.get("crossover_uncertainty", 0.0)),
        "tolerance_band": float(band),
        "kilde": (f"{P1_PROFIL}#predictions.crossover_redshift (DOI {P1_DOI}); "
                  f"krysset mot {KOMPOUND_DATA}#P1_lensing_sector"),
    }


def last_p2(rot: Optional[Path] = None) -> dict:
    """P2: den forseglede f*sigma8(0.7) = 0.430 (DOI 32013156)."""
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, KOMPOUND_DATA)
    p2 = (data.get("P2_growth_sector") or {}).get("fsigma8_z07") or {}
    if "value" not in p2:
        raise Kildefeil(f"P2-verdien mangler i {KOMPOUND_DATA}")
    return {
        "fsigma8_z07": float(p2["value"]),
        "uncertainty": float(p2.get("uncertainty", 0.0)),
        "redshift": float(p2.get("redshift", Z_P2)),
        "kilde": (f"{KOMPOUND_DATA}#P2_growth_sector.fsigma8_z07 "
                  f"(DOI {P2_DOI})"),
    }


def last_k0(rot: Optional[Path] = None) -> dict:
    """K0-skanen fra regimetransisjons-artikkelen (DOI 32080059)."""
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, KOMPOUND_DATA)
    k0 = (((data.get("P1_lensing_sector") or {}).get("parameters") or {})
          .get("K0") or {})
    if "value" not in k0:
        raise Kildefeil(f"K0-skanen mangler i {KOMPOUND_DATA}")
    return {
        "verdi": float(k0["value"]),
        "scan_range": [float(x) for x in k0.get("scan_range", [])],
        "delta_z_across_scan": float(k0.get("delta_z_across_scan", float("nan"))),
        "kilde": (f"{KOMPOUND_DATA}#P1_lensing_sector.parameters.K0 "
                  f"(DOI {K0_DOI})"),
    }


def last_motor(rot: Optional[Path] = None):
    """Den forseglede referanseimplementasjonen av Sigma_eff(z; K0).

    Lastes fra filsti fordi den ligger i en papirpakke, ikke i en pakke.
    Fysikken brukes som den er — den kopieres ikke hit.
    """
    rot = Path(rot or ROT_STANDARD)
    sti = rot / KOMPOUND_MOTOR
    if not sti.exists():
        raise Kildefeil(f"mangler referanseimplementasjonen: {sti}")
    spec = importlib.util.spec_from_file_location(
        "efc_compound_paper_forseglet", sti)
    if spec is None or spec.loader is None:
        raise Kildefeil(f"kan ikke laste {sti}")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _regex_ledger(rot: Path, moenster: str, beskrivelse: str,
                  test_id_del: Optional[str] = None):
    """Finn et tall i ledgerens prosa — deterministisk, ikke «forste treff».

    Er test_id_del gitt, leses bare oppfoeringer hvis test_id inneholder den.
    Ankeret skal kunne pekes paa, ikke bare finnes.
    """
    rx = re.compile(moenster)
    treff = []
    for post in _ledger_poster(rot):
        test_id = str(post.get("test_id") or "")
        if test_id_del and test_id_del not in test_id:
            continue
        tekst = " ".join(str(post.get(felt) or "") for felt in
                         ("data_source", "notes", "prediction", "name"))
        m = rx.search(tekst)
        if m:
            treff.append((m, test_id or None))
    if not treff:
        raise Kildefeil(
            f"fant ikke {beskrivelse} i {LEDGER_TESTS}"
            f"{f' (test_id inneholder {test_id_del!r})' if test_id_del else ''}"
            " — ankeret er ikke sporbart")
    return treff[0]


def last_ankere(rot: Optional[Path] = None) -> dict:
    """De tre S8-ankerne, hver med kilde og usymmetriske feil.

    Ankerne PARSEs fra repoets egne filer der de finnes der; der tallet bare
    staar i prosa (ledgeroppfoeringen) leses det ut av den samme prosaen —
    slik at en endring i ledgeren ikke kan bli stående usett her.
    """
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, DE_Y6_DATA)
    cmb = data["cmb_2026"]["S8"]
    des_lcdm = data["des_y6"]["S8"]
    ankere: dict[str, dict] = {
        "cmb_2026": {
            "navn": "Combined CMB 2026 (Planck+ACT DR6+SPT-3G)",
            "s8": float(cmb["value"]),
            "pluss": float(cmb["uncertainty_plus"]),
            "minus": float(cmb["uncertainty_minus"]),
            "kilde": (f"{DE_Y6_DATA}#cmb_2026 (Qu et al. 2026, PRD 114)"),
        },
        "des_y6_lcdm": {
            "navn": "DES Y6 3x2pt (LCDM)",
            "s8": float(des_lcdm["value"]),
            "pluss": float(des_lcdm["uncertainty"]),
            "minus": float(des_lcdm["uncertainty"]),
            "kilde": f"{DE_Y6_DATA}#des_y6 (arXiv:2601.14559)",
        },
    }

    # DES Y6 i wCDM: tallet staar i ledgeroppfoeringen for DENNE testen.
    m, test_id = _regex_ledger(
        rot, r"S8\s*=\s*([\d.]+)\s*\+([\d.]+)/-([\d.]+)", "DES Y6 (wCDM)",
        test_id_del="p1_p2_cross_probe")
    ankere["des_y6_wcdm"] = {
        "navn": "DES Y6 3x2pt (wCDM)",
        "s8": float(m.group(1)), "pluss": float(m.group(2)),
        "minus": float(m.group(3)),
        "kilde": (f"{LEDGER_TESTS} ({test_id}; arXiv:2601.14559, wCDM)"),
    }

    # KiDS Legacy (Wright et al. 2025): tallet staar i ledgerens S8-oppfoering.
    m, test_id = _regex_ledger(
        rot, r"2503\.19441\)?:\s*S8\s*=\s*([\d.]+)\s*\(\+([\d.]+)\s*/"
             r"[\-\u2212]([\d.]+)\)", "KiDS Legacy (Wright et al. 2025)")
    ankere["kids_legacy_wright"] = {
        "navn": "KiDS Legacy (Wright et al. 2025)",
        "s8": float(m.group(1)), "pluss": float(m.group(2)),
        "minus": float(m.group(3)),
        "kilde": (f"{LEDGER_TESTS} ({test_id}; arXiv:2503.19441, "
                  "cosmic shear)"),
    }

    # Bifurkasjons-varianten: KiDS-Legacy + DES Y3 samlet.
    m, test_id = _regex_ledger(
        rot, r"2503\.19442[^.]*?S8\s*=\s*([\d.]+)", "KiDS Legacy+DES Y3")
    ankere["kids_legacy_joint"] = {
        "navn": "KiDS-Legacy + DES Y3 (joint)",
        "s8": float(m.group(1)), "pluss": 0.012, "minus": 0.012,
        "usikkerhet_merknad": ("ledgeren oppgir usikkerheten som ~0.012 "
                               "(tilnaermet), ikke et eksakt symmetrisk par"),
        "kilde": f"{LEDGER_TESTS} ({test_id}; arXiv:2503.19442)",
    }
    return ankere


# ----------------------------------------------------------------------
#  Motoren: Sigma_eff(z; K0)
# ----------------------------------------------------------------------
def sigma_eff(z: float, K0: float, rot: Optional[Path] = None) -> float:
    """Sigma_eff(z; K0) fra den forseglede referanseimplementasjonen."""
    motor = last_motor(rot)
    verdi = motor.sigma_eff(np.array([float(z)]), K0=float(K0))[0]
    return float(verdi)


def mu_lensing(z: float, K0: float, rot: Optional[Path] = None) -> float:
    """mu(z; K0) — linsing uten slip (eta=1-grenen, jf. A3/P3)."""
    motor = last_motor(rot)
    verdi = motor.mu_lensing(np.array([float(z)]), K0=float(K0))[0]
    return float(verdi)


def crossover_z(K0: float, rot: Optional[Path] = None) -> Optional[float]:
    """Crossoveren motoren finner for denne K0, i [0.01, 2.0]. None = ingen."""
    motor = last_motor(rot)
    z_grid = np.linspace(0.01, 2.0, 2000)
    verdi = motor.find_crossover_z(z_grid, motor.sigma_eff(z_grid, K0=float(K0)))
    return None if not np.isfinite(verdi) else float(verdi)


def motor_avvik(rot: Optional[Path] = None) -> list[dict]:
    """Avvik mellom de forseglede tallene og referanseimplementasjonen.

    Dette er et funn, ikke en fotnote: standardparametrene i
    referanseimplementasjonen reproduserer ikke den forseglede P1-crossoveren
    eller den forseglede P2-amplituden. Estimatoren bruker motoren som den er
    og sier hva den ikke reproduserer.
    """
    rot = Path(rot or ROT_STANDARD)
    motor = last_motor(rot)
    k0 = last_k0(rot)
    p2 = last_p2(rot)
    avvik: list[dict] = []

    zc = crossover_z(k0["verdi"], rot)
    avvik.append({
        "type": "crossover",
        "forseglet": 0.44,
        "motor": zc,
        "motor_status": ("funnet" if zc is not None
                         else "ingen_fortegnssendring"),
        "enhet": "z",
        "kilde": (f"forseglet P1 (DOI {P1_DOI}, z=0.44+/-0.03) vs "
                  f"find_crossover_z ved K0={k0['verdi']} i z i [0.01, 2.0]"),
        "merknad": ("motoren finner ingen fortegnsendring i Sigma_eff-1 ved "
                    "standardparametrene; den forseglede verdien ligger "
                    "utenfor det den gir"),
    })

    K0s = np.linspace(k0["scan_range"][0], k0["scan_range"][1], 50)
    zc_skan = motor.scan_K0(K0s)
    gyldige = zc_skan[np.isfinite(zc_skan)]
    bredde = (float(np.max(gyldige) - np.min(gyldige))
              if gyldige.size else None)
    avvik.append({
        "type": "k0_scan_bredde",
        "forseglet": k0["delta_z_across_scan"],
        "motor": bredde,
        "enhet": "delta_z",
        "kilde": (f"{KOMPOUND_DATA}#P1_lensing_sector.parameters.K0."
                  "delta_z_across_scan vs scan_K0(K0 i "
                  f"[{k0['scan_range'][0]}, {k0['scan_range'][1]}], 50 punkter); "
                  f"{int(gyldige.size)} av {K0s.size} K0-verdier gir crossover"),
    })

    try:
        fs8 = float(motor.fsigma8_prediction(z=p2["redshift"]))
        fs8_motor: Any = fs8
    except Exception as exc:  # noqa: BLE001 — avviket skal rapporteres
        fs8_motor = f"FEIL: {type(exc).__name__}: {exc}"
    avvik.append({
        "type": "p2_fsigma8",
        "forseglet": p2["fsigma8_z07"],
        "motor": fs8_motor,
        "enhet": "f*sigma8",
        "kilde": (f"forseglet P2 (DOI {P2_DOI}) vs fsigma8_prediction("
                  f"z={p2['redshift']}) i referanseimplementasjonen"),
        "merknad": ("den forseglede amplituden reproduseres i stedet av "
                    "efc_inference/engine/growth.py med EFCVariantC(mu_0=0.5) "
                    "(scripts/repro/sealed_fs8_repro.py) — en annen kodevei "
                    "enn referanseimplementasjonen"),
    })

    try:
        kons = motor.check_mu_consistency(0.44)
        mu_motor: Any = float(kons["relative_diff_pct"])
    except Exception as exc:  # noqa: BLE001
        mu_motor = f"FEIL: {type(exc).__name__}"
    avvik.append({
        "type": "mu_konsistens_p1_p2",
        "forseglet": 11.0,
        "motor": mu_motor,
        "enhet": "prosent",
        "kilde": ("P1/P2 mu-konsistens ved z=0.44: artikkelen oppgir ~11 % "
                  "(EFC_compound_paper, cross_sector_consistency) vs "
                  "check_mu_consistency(0.44) i referanseimplementasjonen"),
    })
    return avvik


# ----------------------------------------------------------------------
#  S8-ekvivalenten og avstanden til hver survey
# ----------------------------------------------------------------------
def s8_ekvivalent(z_eff: float, K0: float, modus: str = "lensing_sigma",
                  rot: Optional[Path] = None) -> dict:
    """S8-ekvivalenten av den forseglede P1/P2-verdien ved K0.

    Linsingsbeina kobler Sigma til S8 med repoets egen P3-relasjon
    (S8_lens/S8_CMB = Sigma). Vekstbeinet kobler den forseglede P2-amplituden
    til S8 via forholdet til LCDM-ankeret — en amplitudeproxy, deklarert.
    """
    rot = Path(rot or ROT_STANDARD)
    if modus not in LOKALE_MODI:
        raise ValueError(f"ukjent modus: {modus}")
    ankere = last_ankere(rot)
    cmb = ankere["cmb_2026"]
    p1 = last_p1(rot)

    if modus == "vekst":
        p2 = last_p2(rot)
        forhold = ANKER_EFC / ANKER_LCDM
        s8 = cmb["s8"] * forhold
        rel_p2 = (p2["uncertainty"] / p2["fsigma8_z07"]) if p2["uncertainty"] else 0.0
        rel_cmb = cmb["pluss"] / cmb["s8"]
        sigma = s8 * math.sqrt(rel_p2 ** 2 + rel_cmb ** 2)
        return {
            "modus": modus,
            "z_eff": float(p2["redshift"]),
            "K0": float(K0),
            "s8": s8,
            "s8_sigma": sigma,
            "forhold_til_lcdm": forhold,
            "kilde": (f"forseglet P2 f*sigma8(z={p2['redshift']})="
                      f"{ANKER_EFC} (DOI {P2_DOI}) mot LCDM {ANKER_LCDM} "
                      "(sealed_fs8) x S8_CMB fra "
                      f"{DE_Y6_DATA}#cmb_2026"),
            "forutsetning": ("amplitudeproxy: sigma8 dempes som f*sigma8 — "
                             "f og sigma8 dempes ikke identisk i EFC, saa "
                             "beinet er en tilnaerming, ikke en likning"),
        }

    if modus == "lensing_mu":
        sigma_kobling = mu_lensing(z_eff, K0, rot)
        kobling_navn = "mu (eta=1-grenen)"
        kilde = (f"P3/A3-relasjonen S8_lens/S8_CMB = mu (eta=1, se "
                 f"{DE_Y6_DATA}) x mu(z={float(z_eff):.2f}; K0={float(K0)}) "
                 f"fra {KOMPOUND_MOTOR}")
    else:
        sigma_kobling = sigma_eff(z_eff, K0, rot)
        kobling_navn = "Sigma_eff"
        kilde = (f"P3-relasjonen S8_lens/S8_CMB = Sigma (se {DE_Y6_DATA}) x "
                 f"Sigma_eff(z={float(z_eff):.2f}; K0={float(K0)}) fra "
                 f"{KOMPOUND_MOTOR}")

    s8 = cmb["s8"] * sigma_kobling
    sigma = math.sqrt((cmb["pluss"] * sigma_kobling) ** 2
                      + (cmb["s8"] * p1["tolerance_band"]) ** 2)
    return {
        "modus": modus,
        "z_eff": float(z_eff),
        "K0": float(K0),
        "kobling": kobling_navn,
        "kobling_verdi": sigma_kobling,
        "s8": s8,
        "s8_sigma": sigma,
        "kilde": kilde,
        "forutsetning": ("1D-kompresjon: ett tall per survey, ikke full "
                         f"Sigma(k,z). Usikkerheten paa Sigma er papirets "
                         f"egen +/-{p1['tolerance_band'] * 100:.0f} %-envelope "
                         "(efc_perturbation_sector#tolerance_band)"),
    }


def avstand(s8: float, anker: dict) -> dict:
    """Avstanden til ett anker, med riktig en-sidig sigma fortegnet."""
    delta = float(s8) - anker["s8"]
    sigma = anker["pluss"] if delta >= 0 else anker["minus"]
    return {
        "anker": anker["navn"],
        "s8_anker": anker["s8"],
        "delta": delta,
        "sigma_trukket": sigma,
        "avstand_sigma": abs(delta) / sigma if sigma else float("inf"),
        "kilde": anker["kilde"],
    }


def kategori(s8: float, ankere: dict) -> str:
    """Ledgerens tre utfallskategorier, som monoton regel i S8.

    (i)   MIDBAND            — mellom DES Y6 og KiDS Legacy
    (ii)  CMB_KONSISTENT     — paa eller over KiDS (den CMB-konsistente enden)
    (iii) DES_Y6_KONSISTENT  — under DES Y6 (testens falsifikasjonsvindu)
    """
    des = ankere["des_y6_wcdm"]["s8"]
    kids = ankere["kids_legacy_wright"]["s8"]
    if s8 > kids:
        return "CMB_KONSISTENT"
    if s8 >= des:
        return "MIDBAND"
    return "DES_Y6_KONSISTENT"


def _vurder_bein(z_eff: float, K0: float, modus: str, ankere: dict,
                 rot: Path) -> dict:
    bein = s8_ekvivalent(z_eff, K0, modus=modus, rot=rot)
    kids = ankere["kids_legacy_wright"]
    des = ankere["des_y6_wcdm"]
    av_kids = avstand(bein["s8"], kids)
    av_des = avstand(bein["s8"], des)
    bein["avstand_kids_legacy"] = av_kids
    bein["avstand_des_y6"] = av_des
    bein["kategori"] = kategori(bein["s8"], ankere)
    bein["sjekk_kids_innen_0015"] = abs(bein["s8"] - kids["s8"]) <= KIDS_TOLERANSE
    bein["sjekk_des_min_1p5_sigma"] = av_des["avstand_sigma"] >= DES_MIN_AVSTAND_SIGMA
    bein["margin_kids_toleranse"] = KIDS_TOLERANSE - abs(bein["s8"] - kids["s8"])
    return bein


def vurder(K0: float = K0_TEST, z_eff: Optional[float] = None,
           rot: Optional[Path] = None) -> dict:
    """Dom-treverdig: VURDERT naar kildene finnes, ellers VENTER.

    Hvert bein rapporteres for seg. Beina slaas ikke sammen — de svarer paa
    ulike koblinger mellom de forseglede verdiene og S8, og et sammendrag
    ville skjult nettopp uenigheten som er funnet.
    """
    rot = Path(rot or ROT_STANDARD)
    z = Z_EFF_STANDARD if z_eff is None else float(z_eff)
    try:
        ankere = last_ankere(rot)
        p1 = last_p1(rot)
        p2 = last_p2(rot)
        k0 = last_k0(rot)
        avvik = motor_avvik(rot)
    except Kildefeil as exc:
        return {
            "status": "VENTER",
            "arsak": f"repo-lokal kilde mangler eller er uleselig: {exc}",
            "K0": float(K0),
            "z_eff": z,
        }

    bein = {}
    for modus in ("lensing_sigma", "lensing_mu", "vekst"):
        bein[modus] = _vurder_bein(z, K0, modus, ankere, rot)

    folsomhet = {}
    for zz in Z_EFF_FOLSOMHET:
        b = _vurder_bein(zz, K0, "lensing_sigma", ankere, rot)
        folsomhet[f"{zz:g}"] = {
            "s8": b["s8"],
            "s8_sigma": b["s8_sigma"],
            "kategori": b["kategori"],
            "avstand_des_y6_sigma": b["avstand_des_y6"]["avstand_sigma"],
            "avstand_kids_legacy_sigma": b["avstand_kids_legacy"]["avstand_sigma"],
            "sjekk_kids_innen_0015": b["sjekk_kids_innen_0015"],
        }

    innfridd = [n for n, b in bein.items()
                if b["sjekk_kids_innen_0015"] and b["sjekk_des_min_1p5_sigma"]]
    i_vindu = [n for n, b in bein.items()
               if b["kategori"] == "DES_Y6_KONSISTENT"]

    return {
        "status": "VURDERT",
        "test_id": ("conv_efc_p1_p2_cross_probe_test_against_des_y6_vs_"
                    "kids_legacy_s8_"),
        "K0": float(K0),
        "z_eff": z,
        "forseglet": {
            "P1_crossover_z": p1["crossover_redshift"],
            "P2_fsigma8_z07": p2["fsigma8_z07"],
            "K0_standard": k0["verdi"],
            "K0_scan_range": k0["scan_range"],
        },
        "ankere": ankere,
        "bein": bein,
        "folsomhet_z_eff": folsomhet,
        "motor_avvik": avvik,
        "forventning_innfridd": bool(innfridd),
        "forventning_innfridd_av": innfridd,
        "falsifikasjonsvindu": bool(i_vindu),
        "falsifikasjonsvindu_bein": i_vindu,
        "forbehold": [
            "1D-kompresjon: ett S8-tall per survey, ikke full Sigma(k,z)-form.",
            "Koblingen Sigma -> S8 er repoets egen P3-relasjon; den er ikke "
            "testet mot tomografi her.",
            "Vekstbeinet er en amplitudeproxy (sigma8 dempes som f*sigma8).",
            "z_eff er satt til den forseglede sammenligningsredskiften 0.44 "
            "for BEGGE surveys — likt for begge, saa sammenligningen ikke "
            "tunese mot ett av dem. Folsomheten over z rapporteres.",
            "Ingen dom om RCMP felles her. Estimatoren rapporterer hvor "
            "beina lander; tolkningen er menneskets og reviewerens.",
        ],
    }


# ----------------------------------------------------------------------
#  CLI
# ----------------------------------------------------------------------
def hoved(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="P1/P2 cross-probe-estimator (DES-Y6 vs KiDS-Legacy S8)")
    p.add_argument("--rot", default=str(ROT_STANDARD),
                   help="repo-rot (standard: to nivaaer opp fra denne fila)")
    p.add_argument("--K0", type=float, default=K0_TEST)
    p.add_argument("--z-eff", type=float, default=None)
    p.add_argument("--ut", default=None, help="skriv JSON til fil (ellers stdout)")
    a = p.parse_args(argv)

    dom = vurder(K0=a.K0, z_eff=a.z_eff, rot=Path(a.rot))
    tekst = json.dumps(dom, ensure_ascii=False, indent=2, sort_keys=True)
    if a.ut:
        Path(a.ut).write_text(tekst + "\n", encoding="utf-8")
    else:
        print(tekst)
    return 0 if dom["status"] == "VURDERT" else 3


if __name__ == "__main__":
    sys.exit(hoved())
