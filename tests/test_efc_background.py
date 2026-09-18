"""Tester for den foerste selvkonsistente EFC-bakgrunnsloeseren (L-033).

Kilde — aksjonspapiret (docs/papers/efc/EFC_Relativistic_Action_Field_
Equations_Perturbation_Theory_and_Extraction), seksjon 4.1:

    3 M_Pl^2 F(phi_bar) H^2 = rho_bar_m + 1/2 K(rho_bar) phi_dot_bar^2
                              + V(phi_bar) + 3 M_Pl^2 H F_dot
                              + lambda_dot_bar phi_dot_bar            (12)
    phi_bar_ddot + 3 H phi_dot_bar = Gamma(rho_bar)                      (13)

AERLIGHET — dette er den FOERSTE bakgrunnen, ikke en Boltzmann-kode:
    * Loeseren integrerer (12) og (13) sammen med materie-bevaring og
      responsfeltet lambda (eq. 10). CMB, perturbaSJONER og EFCLASS er
      ikke implementert.
    * V(phi) er uspesifisert i papiret. Vi velger V = const (Lambda-lik)
      fordi LCDM-grensen (kortets falsifikator) krever et Lambda-ledd.
    * K0 er blind i bakgrunnens phi-dynamikk naar phi_dot = Gamma = 0 —
      flyt-betingelsen (13) er geometrisk og inneholder ikke K.

MAALTE TOLERANSER (denne testfilen er der de staar):
    * LCDM-grensen:        maks relativ feil ~1e-10  (assert < 1e-8)
    * H(z)-konsistens:     ~2e-6 ved z_max = 2       (assert < 1e-5)
    * constraint-residual: ~4e-6 ved z_max = 2       (assert < 1e-4)
    Residualen er STRUKTURELL (uendret fra rtol 1e-8 til 1e-11) og skalerer
    som K'(rho) = k0/(omega_crit(1-x)^2) — papirets egen neglisjering av
    delta K/delta g^mu_nu (seksjon 2.1, "Note on delta K"). Det testes.

TDD: skrevet foer efc_inference/engine/efc_background.py fantes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from efc_inference.engine.efc_background import (  # noqa: E402
    NONMINIMAL_SIGN_PAPER,
    NONMINIMAL_SIGN_STANDARD,
    EFCBackgroundEngine,
    EFCBackgroundSolver,
    gamma_of_rho,
    gamma_prime_of_rho,
    kinetic_stiffness,
)

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema ikke installert")


# ---------------------------------------------------------------------------
# Parametre
# ---------------------------------------------------------------------------

# Papirets egne referansevalg der de finnes: alpha = 0.01 (papirets default),
# K0 = 1 (referansekoden). LCDM-grensen: alpha = gamma0 = 0 og
# phi_dot = lambda_dot = 0 ved z=0.
LCDM = {
    "alpha": 0.0,
    "k0": 1.0,
    "omega_crit": 1.0e3,
    "gamma0": 0.0,
    "Omega_m": 0.3,
    "V0": None,          # None -> V0 settes av z=0-normaliseringen (flat lukning)
    "phi0": 0.0,
    "phi_dot0": 0.0,
    "lam0": 0.0,
    "lam_dot0": 0.0,
}

# Aktiv EFC-bakgrunn: ikke-minimal kobling OG flyt-betingelse virker.
EFC = {**LCDM, "alpha": 0.01, "gamma0": 0.05}


def bro_kanoniske() -> dict:
    """Kanoniske parametre for motorens ATLAS-NODE.

    Én kilde for testen og bro-synken (scripts/maintenance/efc_bro_synk.py).
    ``H0`` er med fordi ``compute()`` maaler H(z) i km/s/Mpc; ``regime_node()``
    leser bare den dimensjonsloese kjernen, og vet at kilden er denne fila —
    ikke et gjett paa hvilket modulnivaa-dict som er «det kanoniske».
    """
    return {**EFC, "H0": 70.0}


def _lcdm_E(z, Omega_m=0.3, V0=0.7):
    """Standard flat LCDM (uten straling): E^2 = Omega_m(1+z)^3 + Omega_L."""
    z = np.asarray(z, dtype=float)
    return np.sqrt(Omega_m * (1.0 + z) ** 3 + V0)


def _lcdm_kurve(z, **kw):
    """Varierer omega_crit/k0 og returnerer residualen fra loesningen."""
    params = {**EFC, "alpha": 0.0, "gamma0": 0.0, "phi_dot0": 0.05,
              "omega_crit": 1.0e3, "k0": 1.0, **kw}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=51,
                                           rtol=1e-11, atol=1e-13)
    return sol.diagnostics["constraint_residual_max"]


# ---------------------------------------------------------------------------
# 1. Aksjonens responsfunksjoner (eq. 2, 47, 48)
# ---------------------------------------------------------------------------

def test_K_divergerer_ved_rho_crit_eq2():
    """K(rho) = K0/(1 - rho/rho_crit) — divergerer ved rho >= rho_crit.

    Samme grenseoppfoersel som mu_kz.k_rho (og referansekoden
    efc_relativistic.py:26-29): stivheten er ikke definert utenfor.
    """
    assert np.isclose(kinetic_stiffness(1.0, 0.0), 1.0)
    assert np.isclose(kinetic_stiffness(1.0, 0.5), 2.0)
    assert np.isinf(kinetic_stiffness(1.0, 1.0))
    assert np.isinf(kinetic_stiffness(1.0, 1.5))


def test_gamma_og_gamma_prime_eq47_48():
    """Gamma og Gamma' er noeyaktig eq. 47/48 — og identiske med
    mu(k,z)-modulens funksjoner for samme parametre. Bakgrunnen og
    mu(k,z) maa ikke kunne gli fra hverandre i formlene sine."""
    from efc_inference.engine.mu_kz import gamma_rho, gamma_prime_rho

    g0, x = 0.7, 0.4
    mu_params = {"gamma0": g0, "rho_crit": 1.0}
    assert np.isclose(gamma_of_rho(g0, x), gamma_rho(mu_params, x))
    assert np.isclose(gamma_prime_of_rho(g0, x),
                      gamma_prime_rho(mu_params, x))


# ---------------------------------------------------------------------------
# 2. LCDM-grensetesten (kortets falsifikator)
# ---------------------------------------------------------------------------

def test_lcdm_grensen_reproduserer_standard_friedmann():
    """alpha = gamma0 = 0, phi_dot = lambda_dot = 0, V = const:
    loeseren skal reprodusere standard flat LCDM innenfor maalt toleranse.

    Dette ER falsifikatoren: en bakgrunnsloeser som ikke tar LCDM-grensen
    er feil, uansett hvor pen den er i det andre regimet. Toleransen
    rapporteres (sol.lcdm_max_rel_error) — ikke bare pastass at den er liten.
    """
    sol = EFCBackgroundSolver(LCDM).solve(z_max=3.0, n_points=301)
    assert sol.status == "ok"
    feil = float(np.max(np.abs(sol.E / _lcdm_E(sol.z) - 1.0)))
    assert feil < 1e-8, f"malt avvik fra LCDM: {feil:.3e}"
    assert sol.lcdm_max_rel_error is not None
    assert sol.lcdm_max_rel_error < 1e-8
    # og loeseren skal ikke skryte: den rapporterer det maalte tallet
    assert np.isclose(sol.lcdm_max_rel_error, feil, rtol=1e-3, atol=1e-12)


def test_lcdm_grensen_er_ikke_definert_naar_phi_dot_er_ikke_null():
    """Med phi_dot != 0 er bakgrunnen IKKE LCDM (stiv kinetisk energi) —
    da skal loeseren si 'ikke definert', ikke rapportere et tall."""
    params = {**LCDM, "phi_dot0": 0.05}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=51)
    assert sol.lcdm_max_rel_error is None


def test_z0_normalisering_H0_og_a0():
    """a(z=0) = 1 og H(z=0) = H0 — normaliseringen er en del av kontrakten."""
    for params in (LCDM, EFC):
        sol = EFCBackgroundSolver(params).solve(z_max=2.0, n_points=101)
        assert np.isclose(sol.a[0], 1.0, rtol=0, atol=1e-12)
        assert np.isclose(sol.E[0], 1.0, rtol=0, atol=1e-10), params
        assert np.isclose(sol.z[0], 0.0)


def test_a_er_noeyaktig_en_over_en_pluss_z():
    """a = 1/(1+z) er en eksakt invariant, ikke noe integratoren skal drive.
    (Feil klasse som ble funnet i utviklingen: en manglende E-faktor i
    d rho_m/dz og da/dz — residualen avsloerte den, denne testen hindrer
    gjentakelse.)"""
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=101)
    assert np.allclose(sol.a, 1.0 / (1.0 + sol.z), rtol=1e-9, atol=1e-12)


def test_k0_er_blind_i_bakgrunnen_naar_phi_dot_og_gamma_er_null():
    """Strukturell aerlighet: K0 gaar IKKE inn i phi-dynamikken.

    Flyt-betingelsen (13) er geometrisk — K(rho) staar bare i
    energitettheten (12) og i lambda-ligningen (10), begge multiplisert
    med phi_dot. Med phi_dot = Gamma = 0 er bakgrunnen derfor identisk
    for K0 = 1 og K0 = 1e6. Det er en egenskap ved papirets ligninger,
    ikke ved koden — og den skal vaere maalt, ikke antatt.
    """
    a = EFCBackgroundSolver({**LCDM, "k0": 1.0}).solve(z_max=2.0, n_points=51)
    b = EFCBackgroundSolver({**LCDM, "k0": 1.0e6}).solve(z_max=2.0, n_points=51)
    assert np.allclose(a.E, b.E, rtol=0, atol=1e-12)


# ---------------------------------------------------------------------------
# 3. Indre konsistens: loeserens H(z) mot modified Friedmann direkte (12)
# ---------------------------------------------------------------------------

def test_h_z_stemmer_med_modified_friedmann_direkte():
    """Kortets krav 3: H(z) fra den integrerte loesningen skal stemme med
    H(z) fra eq. (12) evaluert DIREKTE paa loesningens tilstand.

    Integrasjonen driver E via akselerasjonsligningen (eq. 7, (i,j)-delen);
    (12) brukes bare som startbetingelse. At residualen holder seg liten
    langs hele loesningen er derfor en ekte konsistensmaaling — ikke en
    tautologi. Maalt for referanseparametrene: storrelsesorden 1e-6.
    """
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=201)
    assert sol.status == "ok"
    assert sol.h_consistency_max_rel < 1e-5, sol.h_consistency_max_rel


def test_constraint_residualen_rapporteres_med_definisjon():
    """(12) skal holdes langs loesningen — residualen er maalt, navngitt og
    definert i klartekst."""
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=201)
    d = sol.diagnostics
    assert "constraint_residual_max" in d
    assert d["constraint_residual_max"] < 1e-4, d["constraint_residual_max"]
    assert d["constraint_residual_definition"]
    assert d["h_consistency_definition"]
    assert "K'" in d["constraint_residual_cause"]


def test_constraint_residualen_er_strukturell_ikke_numerisk():
    """Residualen skal vaere en egenskap ved LIGNINGENE, ikke ved
    integratoren: strammere rtol skal ikke fjerne den.

    Baseline (alpha = 0, phi_dot = 0) er paa integrasjonsniva (~1e-11).
    Med EFC-leddene i sving er den ~1e-6 — fem storrelsesordener opp.
    """
    stram = EFCBackgroundSolver(EFC).solve(z_max=1.0, n_points=51,
                                          rtol=1e-11, atol=1e-13)
    grov = EFCBackgroundSolver(EFC).solve(z_max=1.0, n_points=51,
                                         rtol=1e-8, atol=1e-11)
    r_stram = stram.diagnostics["constraint_residual_max"]
    r_grov = grov.diagnostics["constraint_residual_max"]
    assert 0.5 < r_stram / r_grov < 2.0, (r_stram, r_grov)
    basis = EFCBackgroundSolver(LCDM).solve(z_max=1.0, n_points=51,
                                           rtol=1e-11, atol=1e-13)
    assert basis.diagnostics["constraint_residual_max"] < 1e-9
    assert r_stram > 1e3 * basis.diagnostics["constraint_residual_max"]


def test_constraint_residualen_skalerer_som_K_prime():
    """Den malte AARSAKEN: residualen skalerer som K'(rho).

    Papiret sier selv (seksjon 2.1, "Note on delta K"): siden K avhenger av
    rho, som avhenger av metrikken, gir delta K/delta g^mu_nu tilleggsledd
    som NEGLISJERES. Residualen er nettopp maalt til aa foelge
    K' = k0/(omega_crit (1-x)^2): proporsjonal med 1/omega_crit, med k0 og
    med phi_dot^2 — og null naar phi_dot = 0.
    """
    r_3 = _lcdm_kurve(None, omega_crit=1.0e3)
    r_4 = _lcdm_kurve(None, omega_crit=1.0e4)
    assert np.isclose(r_4 / r_3, 0.1, rtol=0.05), (r_3, r_4)
    r_k1 = _lcdm_kurve(None, k0=1.0)
    r_k10 = _lcdm_kurve(None, k0=10.0)
    assert np.isclose(r_k10 / r_k1, 10.0, rtol=0.05), (r_k1, r_k10)
    r_u = _lcdm_kurve(None, phi_dot0=0.05)
    r_2u = _lcdm_kurve(None, phi_dot0=0.10)
    assert np.isclose(r_2u / r_u, 4.0, rtol=0.05), (r_u, r_2u)
    assert _lcdm_kurve(None, phi_dot0=0.0) < 1e-9


# ---------------------------------------------------------------------------
# 4. rho_crit-domenet: K divergerer — loeseren skal stoppe aerlig
# ---------------------------------------------------------------------------

def test_rho_crit_domenet_stopper_aerlig():
    """rho_crit = 0.45 * 3 M_Pl^2 H0^2 med Omega_m = 0.3: rho_bar naar
    rho_crit ved (1+z)^3 = 1.5, altsaa z = 0.1447.

    Loeseren skal stoppe der og si det — ikke returnere tall den ikke har
    dekning for. Alt etter krysset skal vaere NaN.
    """
    params = {**LCDM, "omega_crit": 0.45, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=2.0, n_points=201)
    assert sol.status == "rho_crit_reached"
    z_krit = (1.5) ** (1.0 / 3.0) - 1.0
    assert sol.z_rho_crit is not None
    assert abs(sol.z_rho_crit - z_krit) < 0.01, (sol.z_rho_crit, z_krit)
    gyldig = sol.z < sol.z_rho_crit
    assert np.all(np.isfinite(sol.E[gyldig]))
    assert not np.any(np.isfinite(sol.E[~gyldig]))
    assert sol.diagnostics["rho_crit_reached"] is True
    # rho ved siste gyldige GRIDPUNKT — ikke noeyaktig rho_crit, fordi
    # krysset faller mellom to gridpunkter (dz = 0.01 -> ~2 % i rho her).
    assert sol.diagnostics["rho_crit_rho"] == pytest.approx(0.45, rel=0.02)


def test_rho_over_rho_crit_i_loesningen_er_aldri_over_en():
    """Ingen punkt i den returnerte loesningen skal ha rho >= rho_crit."""
    params = {**LCDM, "omega_crit": 0.45, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=2.0, n_points=201)
    x = (sol.rho_m / params["omega_crit"])[np.isfinite(sol.E)]
    assert x.size > 0
    assert np.max(x) <= 1.0 + 1e-9


def test_ugyldig_starttilstand_gir_ingen_tall():
    """Omega_m > omega_crit allerede ved z=0: ingen dekning, ingen tall."""
    params = {**LCDM, "omega_crit": 0.25, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=21)
    assert sol.status == "invalid_state"
    assert not np.any(np.isfinite(sol.E))


# ---------------------------------------------------------------------------
# 5. Selvbeskrivelse: regime_node() — aerlige gyldighetsomraader
# ---------------------------------------------------------------------------

def test_regime_node_er_en_gyldig_regime_node():
    """Motorens selvbeskrivelse skal validere mot RegimeNode-skjemaet."""
    node = EFCBackgroundEngine().regime_node(EFC)
    assert node["id"] == "efc.efc_background_engine"
    if jsonschema is not None:
        s = json.loads((_REPO / "schema" / "regime_node.schema.json")
                       .read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(
            {"$schema": s["$schema"], "$defs": s["$defs"],
             "$ref": "#/$defs/RegimeNode"}).validate(node)


def test_regime_node_deklarerer_at_bakgrunnen_er_foerste_og_boltzmann_aapen():
    """AErlighetskravet: noden skal si hva den IKKE er. En bakgrunn uten
    Boltzmann/CMB som ikke sier det, blir lest som en full loesning."""
    node = EFCBackgroundEngine().regime_node(EFC)
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "foerste" in tekst or "første" in tekst
    assert "boltzmann" in tekst
    assert "aapen" in tekst or "åpen" in tekst
    # V-valget skal staa i klartekst (papiret spesifiserer ikke V(phi))
    assert "v = const" in tekst or "v=const" in tekst
    # og regimet skal deklarere gyldighet + lovform
    assert node["regime"]["validity"]
    assert "3 M_Pl" in node["regime"]["law_form"]


def test_regime_node_beskriver_de_effektive_parametrene():
    """Selvbeskrivelsen skal komme fra de EFFEKTIVE parametrene, ikke fra
    kanoniske tall — samme krav som motor-broen stilte til water-motoren."""
    alt = {**EFC, "alpha": 0.02, "gamma0": 0.11, "Omega_m": 0.27}
    node = EFCBackgroundEngine().regime_node(alt)
    tekst = node["regime"]["validity"]
    assert "0.02" in tekst
    assert "0.11" in tekst
    assert "0.27" in tekst
    assert "0.3}" not in tekst and "Omega_m=0.3," not in tekst


def test_honesty_feltet_faar_ikke_lov_aa_skryte():
    """Loevningen baerer sine egne forbehold — maskinlesbart."""
    sol = EFCBackgroundSolver(EFC, nonminimal_sign=NONMINIMAL_SIGN_PAPER
                              ).solve(z_max=1.0, n_points=51)
    h = sol.honesty
    assert h["boltzmann_cmb"].startswith("open")
    assert "V" in h["V_choice_note"]
    assert h["nonminimal_sign"] == NONMINIMAL_SIGN_PAPER
    assert h["lambda_stress"]
    assert any("perturbasjon" in n.lower() or "perturbation" in n.lower()
               for n in h["not_valid_for"])


# ---------------------------------------------------------------------------
# 6. Konvensjonene er eksplisitte og maalte
# ---------------------------------------------------------------------------

def test_sign_konvensjonen_er_eksplisitt():
    """Papirets eq. (12) har +3 M_Pl^2 H F_dot; den direkte variasjonen av
    aksjonen (eq. 1) i samme signatur gir -3 M_Pl^2 H F_dot. Begge maa
    kunne velges EKSPLISITT — ingen stille konvensjonsendring."""
    assert NONMINIMAL_SIGN_PAPER == 1.0
    assert NONMINIMAL_SIGN_STANDARD == -1.0
    a = EFCBackgroundSolver(EFC,
                            nonminimal_sign=NONMINIMAL_SIGN_PAPER
                            ).solve(z_max=1.0, n_points=51)
    b = EFCBackgroundSolver(EFC,
                            nonminimal_sign=NONMINIMAL_SIGN_STANDARD
                            ).solve(z_max=1.0, n_points=51)
    # Tegnet er ikke kosmetisk: med alpha != 0 gir de to konvensjonene
    # maalbart ulik H(z).
    assert not np.allclose(a.E, b.E, rtol=1e-9)
    assert a.honesty["nonminimal_sign"] != b.honesty["nonminimal_sign"]


def test_den_maalte_dommen_over_sign_konvensjonen():
    """Hvilken sign holder sin egen bakgrunnsligning best? Det MAALES.

    Residualen til (12) langs loesningen er den maalbare dommen. Maalt for
    referanseparametrene (alpha=0.01, gamma0=0.05, z_max=1):
    papirets trykte fortegn gir ~2.5e-7, den direkte variasjonen ~4.7e-7.
    Papirets fortegn er derfor default — ikke fordi det staar i papiret,
    men fordi det maales som det som lukker best.
    """
    res = {}
    for navn, sign in (("papir", NONMINIMAL_SIGN_PAPER),
                       ("standard", NONMINIMAL_SIGN_STANDARD)):
        sol = EFCBackgroundSolver(EFC, nonminimal_sign=sign).solve(
            z_max=1.0, n_points=51, rtol=1e-11, atol=1e-13)
        res[navn] = sol.diagnostics["constraint_residual_max"]
        assert np.isfinite(res[navn]) and res[navn] < 1e-5, res
    assert res["papir"] < res["standard"], res


def test_lambda_stress_formene_er_eksplisitte_og_maalte():
    """Papirets eq. (12) har bare lambda_dot phi_dot; full eq. (6) har ogsaa
    lambda-leddene. Papirets eget notat (2.1) sier formene skiller seg med
    randledd — hvilken som lukker best er maalt, ikke antatt."""
    from efc_inference.engine.efc_background import LAMBDA_STRESS_FORMS

    assert set(LAMBDA_STRESS_FORMS) == {"paper_eq12", "full_eq6"}
    ut = {}
    for form in LAMBDA_STRESS_FORMS:
        sol = EFCBackgroundSolver(EFC, lambda_stress=form).solve(
            z_max=1.0, n_points=51, rtol=1e-11, atol=1e-13)
        ut[form] = sol.diagnostics["constraint_residual_max"]
        assert np.isfinite(ut[form]) and ut[form] < 1e-5, ut
    # Maalt: full eq. (6) gir mindre residual enn papirets trykte form.
    assert ut["full_eq6"] < ut["paper_eq12"], ut


def test_ukjent_konvensjon_avvises():
    """Ingen stille fallback paa konvensjonsvalg."""
    with pytest.raises(ValueError):
        EFCBackgroundSolver(EFC, nonminimal_sign=0.5)
    with pytest.raises(ValueError):
        EFCBackgroundSolver(EFC, lambda_stress="noe-annet")


def test_engine_compute_gir_H_i_km_s_Mpc_og_nan_utenfor_domenet():
    """Motorflaten: H(z) = H0 * E(z). H0 er bare enhetsomregning ut."""
    e = EFCBackgroundEngine()
    params = {**LCDM, "H0": 70.0}
    z = np.array([0.0, 0.5, 1.0])
    H = e.compute(params, z)
    assert H.shape == z.shape
    assert np.all(np.isfinite(H))
    assert np.isclose(H[0], 70.0, rtol=1e-9)
    # og den skal stemme med loeserens E(z)
    sol = EFCBackgroundSolver(LCDM).solve(z_max=1.0, n_points=2001)
    assert np.allclose(H, 70.0 * np.interp(z, sol.z, sol.E), rtol=1e-6)

    # utenfor rho_crit: ingen dekning -> NaN, ikke ekstrapolasjon
    params2 = {**LCDM, "H0": 70.0, "omega_crit": 0.45}
    H2 = e.compute(params2, np.array([0.05, 1.5]))
    assert np.isfinite(H2[0])
    assert np.isnan(H2[1])


def test_engine_avviser_manglende_parametre():
    """validate_params skal fange manglende noekler for den kaster."""
    e = EFCBackgroundEngine()
    assert not e.validate_params({**LCDM, "H0": 70.0, "alpha": np.nan})
    H = e.compute({**LCDM, "H0": 70.0, "alpha": np.nan}, np.array([0.1]))
    assert np.isnan(H[0])


# ---------------------------------------------------------------------------
# 7. Bakgrunnen mater mu(k,z)-modulen (kortets formaal)
# ---------------------------------------------------------------------------

def test_bakgrunnen_mater_mu_kz_modulen():
    """L-033s formaal: bakgrunns-inngangene (phi_bar, phi_dot_bar, rho_bar,
    lambda_dot_bar) skal komme FRA loesningen — ikke fra luften.
    """
    from efc_inference.engine.mu_kz import MuKZEngine

    sol = EFCBackgroundSolver(EFC).solve(z_max=1.5, n_points=101)
    innganger = sol.mu_kz_inputs(z=0.5)
    assert set(innganger) >= {"phi_bar", "phi_dot_bar", "rho_bar",
                              "lambda_dot_bar"}
    for v in innganger.values():
        assert np.isfinite(v)
    params = {"alpha": EFC["alpha"], "K0": EFC["k0"],
              "rho_crit": EFC["omega_crit"], "gamma0": EFC["gamma0"],
              "M_Pl": 1.0, **innganger}
    mu = MuKZEngine().mu_at(params, a=1.0 / 1.5, k=0.1)
    assert np.isfinite(mu) and mu > 0


def test_mu_kz_inngangene_utenfor_domenet_er_nan():
    """Etter rho_crit finnes ingen bakgrunn — da skal inngangene vaere NaN,
    ikke ekstrapolerte."""
    params = {**LCDM, "omega_crit": 0.45, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=101)
    innganger = sol.mu_kz_inputs(z=1.0)
    assert all(np.isnan(v) for v in innganger.values())
