"""P1/P2 cross-probe estimator (validation-ledger physics_test
«EFC P1/P2 cross-probe test against DES-Y6 vs KiDS-Legacy S8 bifurcation»).

The test was «Approved» while the estimator stood as «Planned». This module is
the estimator: it computes the S8 equivalent of EFC's sealed P1/P2 values at
a given K0 and measures the distance to DES Y6 and KiDS Legacy — each on its
own, because the 2026 numbers are not the same measurement of the same universe.

SEALED ANCHORS (never changed here — they are read):
  * P1 Sigma_eff(z) crossover at z ~ 0.44 — DOI 10.6084/m9.figshare.32037990
  * P2 f*sigma8(z=0.7) = 0.430            — DOI 10.6084/m9.figshare.32013156
  * the K0 scan (K0 = 1.37 standard, search 0.5-4.0) — DOI 10.6084/m9.figshare.32080059

WHAT THE ESTIMATOR DOES — and does not do:
  * It loads the sealed reference implementation of Sigma_eff(z; K0)
    (docs/papers/efc/EFC_compound_paper/src/efc_compound_paper.py) and
    USES it. The physics is not reimplemented here — two sources for the same
    equation is the drift ADR-002 was written against.
  * It couples Sigma to S8 with the repository's own P3 relation
    (S8_lens/S8_CMB = Sigma, see docs/papers/efc/efc_des_y6_validation) and
    reads S8_CMB from the repository's own data file. No new constants.
  * It passes no verdict on RCMP. It reports each leg on its own —
    lensing (Sigma_eff) and growth (f*sigma8) — and which of the ledger's three
    outcome categories each leg lands in:
        (i)   MIDBAND            — between the two WL surveys
        (ii)  CMB_KONSISTENT     — at the CMB-consistent end
        (iii) DES_Y6_KONSISTENT  — in DES-Y6 territory (weakens the RCMP
                                   argument, cf. the test's falsification window)
  * It does not hide deviations: the reference implementation's default
    parameters do not reproduce all the sealed numbers. Those deviations are
    reported in motor_avvik() and travel with every verdict.
  * A missing source gives VENTER — never a verdict on data one does not have.

Everything is read repo-locally. No network fetching, and nothing is written
back to the repository: the CLI can write the report to a path the caller
itself gives.
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
#  Sources (repo-local paths, relative to the repo root)
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

K0_TEST = 2.0                 # the expectation in the ledger is formulated at K0=2.0
Z_EFF_STANDARD = 0.44         # the sealed comparison redshift (P1)
Z_EFF_FOLSOMHET = (0.30, 0.44, 0.90)   # the P3 window z ~ 0.3-0.9
Z_P2 = 0.7                    # the sealed P2 redshift

LOKALE_MODI = ("lensing_sigma", "lensing_mu", "vekst")

# The ledger's quantitative expectation (quote, see tests.json for the test):
#   «K0=2.0 shall reproduce the S8 equivalent within +/-0.015 of the KiDS
#    Legacy central value and lie >=1.5 sigma from DES-Y6.»
KIDS_TOLERANSE = 0.015
DES_MIN_AVSTAND_SIGMA = 1.5

KATEGORIER = ("MIDBAND", "CMB_KONSISTENT", "DES_Y6_KONSISTENT")


class Kildefeil(Exception):
    """A repo-local source is missing or unreadable — no verdict is passed."""


# ----------------------------------------------------------------------
#  Loading of repo-local sources
# ----------------------------------------------------------------------
def _les_json(rot: Path, relativ: Path) -> dict:
    sti = rot / relativ
    if not sti.exists():
        raise Kildefeil(f"missing source file: {sti}")
    try:
        return json.loads(sti.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Kildefeil(f"unreadable source file {sti}: {exc}") from exc


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
        raise Kildefeil(f"found no test entries in {LEDGER_TESTS}")
    return poster


def last_p1(rot: Optional[Path] = None) -> dict:
    """P1: the sealed Sigma_eff crossover (DOI 32037990).

    The crossover is read from the perturbation-sector package and cross-checked
    against the regime-transition paper. If the two do not agree, no verdict is
    passed — two sealed numbers for the same quantity shall not be merged in
    silence.
    """
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, P1_PROFIL)
    pred = data.get("predictions") or {}
    cross = (pred.get("crossover_redshift") or {}).get("value")
    band = ((data.get("parameters") or {}).get("tolerance_band") or {}).get(
        "value")
    if cross is None or band is None:
        raise Kildefeil(f"the P1 values are missing in {P1_PROFIL}")

    kompound = _les_json(rot, KOMPOUND_DATA).get("P1_lensing_sector") or {}
    kompound_cross = kompound.get("crossover_redshift")
    if kompound_cross is None:
        raise Kildefeil(f"the P1 crossover is missing in {KOMPOUND_DATA}")
    if abs(float(kompound_cross) - float(cross)) > 1e-9:
        raise Kildefeil(
            "the P1 crossover differs between the two sealed sources: "
            f"{cross} ({P1_PROFIL}) vs {kompound_cross} ({KOMPOUND_DATA})")

    return {
        "crossover_redshift": float(cross),
        "crossover_uncertainty": float(kompound.get("crossover_uncertainty", 0.0)),
        "tolerance_band": float(band),
        "kilde": (f"{P1_PROFIL}#predictions.crossover_redshift (DOI {P1_DOI}); "
                  f"cross-checked against "
                  f"{KOMPOUND_DATA}#P1_lensing_sector"),
    }


def last_p2(rot: Optional[Path] = None) -> dict:
    """P2: the sealed f*sigma8(0.7) = 0.430 (DOI 32013156)."""
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, KOMPOUND_DATA)
    p2 = (data.get("P2_growth_sector") or {}).get("fsigma8_z07") or {}
    if "value" not in p2:
        raise Kildefeil(f"the P2 value is missing in {KOMPOUND_DATA}")
    return {
        "fsigma8_z07": float(p2["value"]),
        "uncertainty": float(p2.get("uncertainty", 0.0)),
        "redshift": float(p2.get("redshift", Z_P2)),
        "kilde": (f"{KOMPOUND_DATA}#P2_growth_sector.fsigma8_z07 "
                  f"(DOI {P2_DOI})"),
    }


def last_k0(rot: Optional[Path] = None) -> dict:
    """The K0 scan from the regime-transition paper (DOI 32080059)."""
    rot = Path(rot or ROT_STANDARD)
    data = _les_json(rot, KOMPOUND_DATA)
    k0 = (((data.get("P1_lensing_sector") or {}).get("parameters") or {})
          .get("K0") or {})
    if "value" not in k0:
        raise Kildefeil(f"the K0 scan is missing in {KOMPOUND_DATA}")
    return {
        "verdi": float(k0["value"]),
        "scan_range": [float(x) for x in k0.get("scan_range", [])],
        "delta_z_across_scan": float(k0.get("delta_z_across_scan", float("nan"))),
        "kilde": (f"{KOMPOUND_DATA}#P1_lensing_sector.parameters.K0 "
                  f"(DOI {K0_DOI})"),
    }


def last_motor(rot: Optional[Path] = None):
    """The sealed reference implementation of Sigma_eff(z; K0).

    It is loaded from a file path because it lives in a paper package, not in
    a package. The physics is used as it is — it is not copied here.
    """
    rot = Path(rot or ROT_STANDARD)
    sti = rot / KOMPOUND_MOTOR
    if not sti.exists():
        raise Kildefeil(f"missing the reference implementation: {sti}")
    spec = importlib.util.spec_from_file_location(
        "efc_compound_paper_forseglet", sti)
    if spec is None or spec.loader is None:
        raise Kildefeil(f"cannot load {sti}")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _regex_ledger(rot: Path, moenster: str, beskrivelse: str,
                  test_id_del: Optional[str] = None):
    """Find a number in the ledger's prose — deterministic, not «first hit».

    If test_id_del is given, only entries whose test_id contains it are read.
    The anchor shall be pointable at, not merely present.
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
            f"found no {beskrivelse} in {LEDGER_TESTS}"
            f"{f' (test_id contains {test_id_del!r})' if test_id_del else ''}"
            " — the anchor is not traceable")
    return treff[0]


def last_ankere(rot: Optional[Path] = None) -> dict:
    """The three S8 anchors, each with source and asymmetric errors.

    The anchors are PARSED from the repository's own files where they exist
    there; where the number stands only in prose (the ledger entry) it is read
    out of that same prose — so that a change in the ledger cannot remain
    unseen here.
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

    # DES Y6 in wCDM: the number stands in the ledger entry for THIS test.
    m, test_id = _regex_ledger(
        rot, r"S8\s*=\s*([\d.]+)\s*\+([\d.]+)/-([\d.]+)", "DES Y6 (wCDM)",
        test_id_del="p1_p2_cross_probe")
    ankere["des_y6_wcdm"] = {
        "navn": "DES Y6 3x2pt (wCDM)",
        "s8": float(m.group(1)), "pluss": float(m.group(2)),
        "minus": float(m.group(3)),
        "kilde": (f"{LEDGER_TESTS} ({test_id}; arXiv:2601.14559, wCDM)"),
    }

    # KiDS Legacy (Wright et al. 2025): the number stands in the ledger's S8 entry.
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

    # The bifurcation variant: KiDS-Legacy + DES Y3 jointly.
    m, test_id = _regex_ledger(
        rot, r"2503\.19442[^.]*?S8\s*=\s*([\d.]+)", "KiDS Legacy+DES Y3")
    ankere["kids_legacy_joint"] = {
        "navn": "KiDS-Legacy + DES Y3 (joint)",
        "s8": float(m.group(1)), "pluss": 0.012, "minus": 0.012,
        "usikkerhet_merknad": ("the ledger states the uncertainty as ~0.012 "
                               "(approximate), not an exact symmetric pair"),
        "kilde": f"{LEDGER_TESTS} ({test_id}; arXiv:2503.19442)",
    }
    return ankere


# ----------------------------------------------------------------------
#  The engine: Sigma_eff(z; K0)
# ----------------------------------------------------------------------
def sigma_eff(z: float, K0: float, rot: Optional[Path] = None) -> float:
    """Sigma_eff(z; K0) from the sealed reference implementation."""
    motor = last_motor(rot)
    verdi = motor.sigma_eff(np.array([float(z)]), K0=float(K0))[0]
    return float(verdi)


def mu_lensing(z: float, K0: float, rot: Optional[Path] = None) -> float:
    """mu(z; K0) — lensing without slip (the eta=1 branch, cf. A3/P3)."""
    motor = last_motor(rot)
    verdi = motor.mu_lensing(np.array([float(z)]), K0=float(K0))[0]
    return float(verdi)


def crossover_z(K0: float, rot: Optional[Path] = None) -> Optional[float]:
    """The crossover the engine finds for this K0, in [0.01, 2.0]. None = none."""
    motor = last_motor(rot)
    z_grid = np.linspace(0.01, 2.0, 2000)
    verdi = motor.find_crossover_z(z_grid, motor.sigma_eff(z_grid, K0=float(K0)))
    return None if not np.isfinite(verdi) else float(verdi)


def motor_avvik(rot: Optional[Path] = None) -> list[dict]:
    """Deviations between the sealed numbers and the reference implementation.

    This is a finding, not a footnote: the default parameters in the reference
    implementation do not reproduce the sealed P1 crossover or the sealed P2
    amplitude. The estimator uses the engine as it is and says what it does not
    reproduce.
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
        "kilde": (f"sealed P1 (DOI {P1_DOI}, z=0.44+/-0.03) vs "
                  f"find_crossover_z at K0={k0['verdi']} in z in [0.01, 2.0]"),
        "merknad": ("the engine finds no sign change in Sigma_eff-1 at the "
                    "standard parameters; the sealed value lies outside "
                    "what it gives"),
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
                  "delta_z_across_scan vs scan_K0(K0 in "
                  f"[{k0['scan_range'][0]}, {k0['scan_range'][1]}], 50 points); "
                  f"{int(gyldige.size)} of {K0s.size} K0 values give a crossover"),
    })

    try:
        fs8 = float(motor.fsigma8_prediction(z=p2["redshift"]))
        fs8_motor: Any = fs8
    except Exception as exc:  # noqa: BLE001 — the deviation shall be reported
        fs8_motor = f"ERROR: {type(exc).__name__}: {exc}"
    avvik.append({
        "type": "p2_fsigma8",
        "forseglet": p2["fsigma8_z07"],
        "motor": fs8_motor,
        "enhet": "f*sigma8",
        "kilde": (f"sealed P2 (DOI {P2_DOI}) vs fsigma8_prediction("
                  f"z={p2['redshift']}) in the reference implementation"),
        "merknad": ("the sealed amplitude is reproduced instead by "
                    "efc_inference/engine/growth.py with EFCVariantC(mu_0=0.5) "
                    "(scripts/repro/sealed_fs8_repro.py) — a different code "
                    "path than the reference implementation"),
    })

    try:
        kons = motor.check_mu_consistency(0.44)
        mu_motor: Any = float(kons["relative_diff_pct"])
    except Exception as exc:  # noqa: BLE001
        mu_motor = f"ERROR: {type(exc).__name__}"
    avvik.append({
        "type": "mu_konsistens_p1_p2",
        "forseglet": 11.0,
        "motor": mu_motor,
        "enhet": "percent",
        "kilde": ("P1/P2 mu consistency at z=0.44: the paper states ~11 % "
                  "(EFC_compound_paper, cross_sector_consistency) vs "
                  "check_mu_consistency(0.44) in the reference implementation"),
    })
    return avvik


# ----------------------------------------------------------------------
#  The S8 equivalent and the distance to each survey
# ----------------------------------------------------------------------
def s8_ekvivalent(z_eff: float, K0: float, modus: str = "lensing_sigma",
                  rot: Optional[Path] = None) -> dict:
    """The S8 equivalent of the sealed P1/P2 value at K0.

    The lensing legs couple Sigma to S8 with the repository's own P3 relation
    (S8_lens/S8_CMB = Sigma). The growth leg couples the sealed P2 amplitude
    to S8 via the ratio to the LCDM anchor — an amplitude proxy, declared.
    """
    rot = Path(rot or ROT_STANDARD)
    if modus not in LOKALE_MODI:
        raise ValueError(f"unknown modus: {modus}")
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
            "kilde": (f"sealed P2 f*sigma8(z={p2['redshift']})="
                      f"{ANKER_EFC} (DOI {P2_DOI}) against LCDM {ANKER_LCDM} "
                      "(sealed_fs8) x S8_CMB from "
                      f"{DE_Y6_DATA}#cmb_2026"),
            "forutsetning": ("amplitude proxy: sigma8 is damped as f*sigma8 — "
                             "f and sigma8 are not damped identically in EFC, "
                             "so the leg is an approximation, not an equation"),
        }

    if modus == "lensing_mu":
        sigma_kobling = mu_lensing(z_eff, K0, rot)
        kobling_navn = "mu (the eta=1 branch)"
        kilde = (f"the P3/A3 relation S8_lens/S8_CMB = mu (eta=1, see "
                 f"{DE_Y6_DATA}) x mu(z={float(z_eff):.2f}; K0={float(K0)}) "
                 f"from {KOMPOUND_MOTOR}")
    else:
        sigma_kobling = sigma_eff(z_eff, K0, rot)
        kobling_navn = "Sigma_eff"
        kilde = (f"the P3 relation S8_lens/S8_CMB = Sigma (see {DE_Y6_DATA}) x "
                 f"Sigma_eff(z={float(z_eff):.2f}; K0={float(K0)}) from "
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
        "forutsetning": ("1D compression: one number per survey, not the full "
                         f"Sigma(k,z). The uncertainty on Sigma is the paper's "
                         f"own +/-{p1['tolerance_band'] * 100:.0f} %-envelope "
                         "(efc_perturbation_sector#tolerance_band)"),
    }


def avstand(s8: float, anker: dict) -> dict:
    """The distance to one anchor, with the correct one-sided sigma sign."""
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
    """The ledger's three outcome categories, as a monotone rule in S8.

    (i)   MIDBAND            — between DES Y6 and KiDS Legacy
    (ii)  CMB_KONSISTENT     — at or above KiDS (the CMB-consistent end)
    (iii) DES_Y6_KONSISTENT  — below DES Y6 (the test's falsification window)
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
    """Three-valued verdict: VURDERT when the sources exist, otherwise VENTER.

    Each leg is reported on its own. The legs are not merged — they answer to
    different couplings between the sealed values and S8, and a summary would
    hide exactly the disagreement that has been found.
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
            "arsak": f"repo-local source is missing or unreadable: {exc}",
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
            "1D compression: one S8 number per survey, not the full "
            "Sigma(k,z) form.",
            "The Sigma -> S8 coupling is the repository's own P3 relation; it "
            "is not tested against tomography here.",
            "The growth leg is an amplitude proxy (sigma8 is damped as f*sigma8).",
            "z_eff is set to the sealed comparison redshift 0.44 for BOTH "
            "surveys — equal for both, so the comparison is not tuned against "
            "one of them. The sensitivity over z is reported.",
            "No verdict on RCMP is passed here. The estimator reports where "
            "the legs land; the interpretation is the human's and the "
            "reviewer's.",
        ],
    }


# ----------------------------------------------------------------------
#  CLI
# ----------------------------------------------------------------------
def hoved(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="P1/P2 cross-probe-estimator (DES-Y6 vs KiDS-Legacy S8)")
    p.add_argument("--rot", default=str(ROT_STANDARD),
                   help="repo root (default: two levels up from this file)")
    p.add_argument("--K0", type=float, default=K0_TEST)
    p.add_argument("--z-eff", type=float, default=None)
    p.add_argument("--ut", default=None, help="write JSON to file (otherwise stdout)")
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
