"""Tests for the holding->release engines: solar flare, quake, transient (L-026/L-028/L-036).

All three engines encode the same shape: energy/stress/mass charges
slowly in a buffer, and is released abruptly when a threshold is crossed — the
same pattern that was found in the recon of kosmos.sol (GOES flares),
kosmos.jord (USGS quakes) and kosmos.transienter (ALeRCE/ZTF events).
The engines are REGIME ENGINES: they compute the shape's observables
(charging time, released energy/moment, class) from physical parameters
— they do not claim predictive power for single events.

Discipline: the models are idealized (Avallon-style magnetic buffer;
elastic-rebound/Burridge-Knopoff-style fault loading; collapse buffer
with G*M^2/R). It shall stand in the engine's own description, and release shall
be THRESHOLD-DRIVEN — not time-driven. All three also hold the SAME
fail-closed contract for the input: the buffer charges from zero, so negative
or non-finite input is outside the window and gives NaN — never
"holding" and never a release (the L-036/PR #501 shape).

The transient engine (L-036) has LANDED atlas coupling: the node
efc.transient_engine stands in schema/regime_nodes.jsonld with the three
ANALOGOUS_TO relations. The guard that made the postponement machine-visible
was replaced by the bridge test below, which holds the engine's regime_node() and
the atlas node together mechanically.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from efc_inference.engine.solar_flare import SolarFlareEngine
from efc_inference.engine.jordskjelv import JordskjelvEngine
from efc_inference.engine.transient import TransientEngine

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

_ATLAS = Path(__file__).resolve().parents[1] / "schema" / "regime_nodes.jsonld"
_SKJEMA = Path(__file__).resolve().parents[1] / "schema" / "regime_node.schema.json"


# ----------------------------------------------------------------------
# The solar-flare engine
# ----------------------------------------------------------------------

SOLFLARE_PARAMS = {
    "mu_0": 1.25663706212e-6,   # N/A^2 — vacuum permeability
    "b_crit": 0.3,              # T — critical field strength for release
    "oppladningsrate": 1.0e-6,  # T/s — dB/dt in the active region
    "volum": 1.0e21,            # m^3 — active-region volume
}


def test_solarflare_beregner_oppladningstid():
    e = SolarFlareEngine()
    t = e.oppladningstid(SOLFLARE_PARAMS)
    assert np.isclose(t, SOLFLARE_PARAMS["b_crit"] / SOLFLARE_PARAMS["oppladningsrate"])
    assert t > 0


def test_solarflare_utlost_energi_fra_magnetisk_buffer():
    e = SolarFlareEngine()
    energi = e.utlost_energi(SOLFLARE_PARAMS)
    # E = B^2 / (2 mu_0) * volum
    forventet = (SOLFLARE_PARAMS["b_crit"] ** 2
                 / (2 * SOLFLARE_PARAMS["mu_0"])) * SOLFLARE_PARAMS["volum"]
    assert np.isclose(energi, forventet)


def test_solarflare_goes_klasse_monoton():
    """Higher released energy -> at least as high a GOES class (A<B<C<M<X)."""
    e = SolarFlareEngine()
    klasser = [e.goes_klasse(e.utlost_energi(
        {**SOLFLARE_PARAMS, "b_crit": b})) for b in (0.1, 0.2, 0.3, 0.5)]
    assert klasser == sorted(klasser, key="ABCMX".index)
    assert all(k in "ABCMX" for k in klasser)


def test_solarflare_goes_anker_1e22_j_er_m():
    """The calibration anchor: 1e22 J ~ M class (typical M-flare energy).
    Proxey's documentation and code shall agree."""
    e = SolarFlareEngine()
    assert e.goes_klasse(1e22) == "M"
    assert e.goes_klasse(1e23) == "X"
    assert e.goes_klasse(1e21) == "C"
    assert e.goes_klasse(1e20) == "B"


def test_solarflare_holdingsfase_for_terskel():
    """For B < b_crit the buffer is in holding: no release, the energy
    builds up. compute() shall report holding, not release."""
    e = SolarFlareEngine()
    params = dict(SOLFLARE_PARAMS)
    out = e.compute(params, np.array([0.1]))  # B = 0.1 T < 0.3 T
    assert out.shape == (1,)
    # No release: released energy = 0
    assert out[0] == 0.0


def test_solarflare_regime_node_selvbeskrivelse():
    e = SolarFlareEngine()
    node = e.regime_node(SOLFLARE_PARAMS)
    assert node["id"] == "efc.solar_flare_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "released" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()


def test_solarflare_fail_closed_paa_ugyldig_feltstyrke():
    """Invalid field strength is outside the window — never "holding" and never
    an exception.

    Measured for this contract (origin/main = afdc620f):
    compute([-1, nan, inf, -inf]) -> [0.0, 0.0, inf, 0.0] — the engine
    answered "the buffer holds" for NaN and -inf, and released an infinite
    energy for +inf.
    """
    e = SolarFlareEngine()
    ugyldig = np.array([-1.0, -SOLFLARE_PARAMS["b_crit"], np.nan,
                        np.inf, -np.inf])
    ut = e.compute(SOLFLARE_PARAMS, ugyldig)
    assert np.all(np.isnan(ut)), ut


def test_solarflare_hjelperen_har_samme_fail_closed_kontrakt():
    """magnetisk_energi() is the same CLASS of helper as the transient engine's
    bindingsenergi(): B^2 made the energy POSITIVE also for negative B, so
    a directly calling party got a number where compute() gives NaN.
    The contract shall have ONE source, not one per call.
    """
    e = SolarFlareEngine()
    ugyldig = np.array([-1.0, np.nan, np.inf, -np.inf])
    energi = e.magnetisk_energi(SOLFLARE_PARAMS, ugyldig)
    assert np.all(np.isnan(energi)), energi
    # Valid input is UNCHANGED: E = B^2/(2 mu_0) * V at the threshold.
    assert np.isclose(e.magnetisk_energi(SOLFLARE_PARAMS, np.array([0.3]))[0],
                      e.utlost_energi(SOLFLARE_PARAMS))
    # ...and the NaN set of the helper and of compute() is the SAME.
    miks = np.array([-1.0, np.nan, np.inf, -np.inf, 0.0, 0.1, 0.3, 0.9])
    assert np.array_equal(np.isnan(e.magnetisk_energi(SOLFLARE_PARAMS, miks)),
                          np.isnan(e.compute(SOLFLARE_PARAMS, miks)))


def test_solarflare_validity_deklarerer_ugyldig_inngang():
    """The window is the engine's own claim. If the contract does not stand there, it
    is silent — the same error class that "NaN -> holding" was measured as."""
    v = SolarFlareEngine().regime_node(SOLFLARE_PARAMS)["regime"]["validity"]
    assert "outside the window" in v
    assert "NaN" in v
    assert "negativ" in v


# ----------------------------------------------------------------------
# The earthquake engine
# ----------------------------------------------------------------------

JORDSKJELV_PARAMS = {
    "skjaermodul": 3.0e10,       # Pa — shear modulus (the Earth's crust)
    "lade_rate": 1.0e4,          # Pa/year — stress accumulation
    "terskel": 3.0e6,            # Pa — stress drop at release
    "areal": 1.0e8,              # m^2 — rupture area
}


def test_jordskjelv_gjentakelsestid():
    e = JordskjelvEngine()
    t = e.gjentakelsestid(JORDSKJELV_PARAMS)
    assert np.isclose(t, JORDSKJELV_PARAMS["terskel"] / JORDSKJELV_PARAMS["lade_rate"])
    assert t > 0


def test_jordskjelv_moment_og_magnitude():
    e = JordskjelvEngine()
    m0 = e.seismisk_moment(JORDSKJELV_PARAMS)
    # M0 = mu * A * D with D = terskel / mu
    forventet = (JORDSKJELV_PARAMS["skjaermodul"] * JORDSKJELV_PARAMS["areal"]
                 * (JORDSKJELV_PARAMS["terskel"] / JORDSKJELV_PARAMS["skjaermodul"]))
    assert np.isclose(m0, forventet)
    # Mw = (2/3)(log10 M0 - 9.1)
    mw = e.magnitude(JORDSKJELV_PARAMS)
    assert np.isclose(mw, (2 / 3) * (np.log10(m0) - 9.1))


def test_jordskjelv_holdingsfase_for_akkumulering():
    e = JordskjelvEngine()
    # Stress below threshold: holding — the moment builds up, release is 0
    out = e.compute(JORDSKJELV_PARAMS, np.array([1.0e6]))  # 1 MPa < 3 MPa
    assert out.shape == (1,)
    assert out[0] == 0.0


def test_jordskjelv_utlosning_over_terskel():
    e = JordskjelvEngine()
    out = e.compute(JORDSKJELV_PARAMS, np.array([3.2e6]))  # above threshold
    assert out.shape == (1,)
    assert out[0] > 0.0  # the moment is released


def test_jordskjelv_regime_node_selvbeskrivelse():
    e = JordskjelvEngine()
    node = e.regime_node(JORDSKJELV_PARAMS)
    assert node["id"] == "efc.jordskjelv_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "released" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()


def test_jordskjelv_fail_closed_paa_ugyldig_spenning():
    """Invalid stress is outside the window — never "holding" and never
    an exception.

    Measured for this contract (origin/main = afdc620f):
    compute([-1, nan, inf, -inf]) -> [0.0, 0.0, 3e14, 0.0] — the engine
    answered "the buffer holds" for NaN and -inf, and released the whole moment
    for +inf. Valid points shall be UNCHANGED.
    """
    e = JordskjelvEngine()
    ugyldig = np.array([-1.0, -JORDSKJELV_PARAMS["terskel"], np.nan,
                        np.inf, -np.inf])
    ut = e.compute(JORDSKJELV_PARAMS, ugyldig)
    assert np.all(np.isnan(ut)), ut
    assert e.compute(JORDSKJELV_PARAMS, np.array([1.0e6]))[0] == 0.0
    assert e.compute(JORDSKJELV_PARAMS, np.array([3.2e6]))[0] > 0.0


def test_jordskjelv_validity_deklarerer_ugyldig_inngang():
    """The window is the engine's own claim — the contract shall stand there."""
    v = JordskjelvEngine().regime_node(
        JORDSKJELV_PARAMS)["regime"]["validity"]
    assert "outside the window" in v
    assert "NaN" in v
    assert "negativ" in v


# ----------------------------------------------------------------------
# The transient engine (stellar death)
# ----------------------------------------------------------------------

TRANS_PARAMS = {
    "G": 6.67430e-11,           # m^3 kg^-1 s^-2 — the gravitational constant
    "terskelmasse": 2.785e30,   # kg — the stability limit (Chandrasekhar-style, MODEL PARAMETER)
    "radius": 1.0e4,            # m — core radius at collapse
    "vekstrate": 6.3e19,        # kg/s — mass accretion (the charging)
    "stigningstid_dager": 20.0,  # days — fast rise in the light curve
    "haletid_dager": 40.0,      # days — exponential tail
    "stigningseksponent": 2.0,  # shape parameter for the rise
}


def test_transient_bindingsenergi_skalerer_med_masse_kvadrert():
    """E_bind = G*M^2/R — and it scales as M^2 (4x mass -> 4x energy)."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    forventet = (TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"])
    assert np.isclose(e.bindingsenergi(TRANS_PARAMS, np.array([m]))[0], forventet)
    dobbel = e.bindingsenergi(TRANS_PARAMS, np.array([2 * m]))[0]
    assert np.isclose(dobbel / forventet, 4.0)


def test_transient_utlost_energi_ved_terskelen():
    """Released energy AT the threshold = G*terskelmasse^2/R."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    forventet = TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"]
    assert np.isclose(e.utlost_energi(TRANS_PARAMS), forventet)
    assert e.utlost_energi(TRANS_PARAMS) > 0


def test_transient_holdetid_fra_vekstrate():
    """The hold time = terskelmasse / vekstrate (seconds), positive and finite."""
    e = TransientEngine()
    t = e.holdetid(TRANS_PARAMS)
    assert np.isclose(t, TRANS_PARAMS["terskelmasse"] / TRANS_PARAMS["vekstrate"])
    assert t > 0


def test_transient_holdingsfase_under_terskel():
    """Below the stability limit the core holds: no release (0)."""
    e = TransientEngine()
    out = e.compute(TRANS_PARAMS, np.array([0.5 * TRANS_PARAMS["terskelmasse"]]))
    assert out.shape == (1,)
    assert out[0] == 0.0


def test_transient_utlosning_bruker_den_lokale_massen():
    """The convention shall be explicit and tested: compute() uses the
    LOCAL mass (the energy scales with M^2), while utlost_energi(params)
    is the energy AT the threshold — the same convention as solar_flare.compute().
    An implementation that returns the declared threshold energy for a
    mass ABOVE the threshold shall fail here."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    ved_terskel = e.compute(TRANS_PARAMS, np.array([m]))[0]
    assert np.isclose(ved_terskel, e.utlost_energi(TRANS_PARAMS))
    over = e.compute(TRANS_PARAMS, np.array([1.5 * m]))[0]
    assert np.isclose(over, e.bindingsenergi(TRANS_PARAMS, np.array([1.5 * m]))[0])
    assert over > ved_terskel
    assert not np.isclose(over, ved_terskel)


def test_transient_lettkurve_peak_ved_stigningstiden():
    """The shape: (t/t_stig)^alpha during the rise time, exp(-(t-t_stig)/t_hale)
    after — continuous with a maximum of 1.0 at t = stigningstid_dager."""
    e = TransientEngine()
    t_stig = TRANS_PARAMS["stigningstid_dager"]
    t_hale = TRANS_PARAMS["haletid_dager"]
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig]))[0], 1.0)
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([0.0]))[0], 0.0)
    # the rise is fast and monotonic: alpha = 2 -> (t/t_stig)^2
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig / 2]))[0], 0.25)
    # the tail is exponential with t_hale as the time scale
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig + t_hale]))[0],
                      np.exp(-1.0))
    # monotonic rise before the knee, monotonic tail after (two points each way)
    stig = e.lettkurve(TRANS_PARAMS, np.array([0.2, 0.5, 0.9]) * t_stig)
    hale = e.lettkurve(TRANS_PARAMS, np.array([1.0, 2.0, 5.0]) * t_stig)
    assert list(stig) == sorted(stig)
    assert list(hale) == sorted(hale, reverse=True)


def test_transient_lettkurve_enhet_er_dager_ikke_sekunder():
    """Unit-sensitive logic: the shape takes DAYS (the parameter is named _dager).
    The fixture is built so that a wrong unit goes to the OPPOSITE conclusion:
    100 days = t_stig + 2*t_hale shall give exp(-2) ~ 0.135, while an
    implementation that reads the parameter as seconds gives exp(-1.7e5) ~ 0.
    """
    e = TransientEngine()
    t_stig = TRANS_PARAMS["stigningstid_dager"]
    t_hale = TRANS_PARAMS["haletid_dager"]
    v = e.lettkurve(TRANS_PARAMS, np.array([t_stig + 2 * t_hale]))[0]
    assert v > 0.1
    assert np.isclose(v, np.exp(-2.0))
    # ...and far out on the tail it shall still be > 0, but < 1e-6
    langt = e.lettkurve(TRANS_PARAMS, np.array([t_stig + 20 * t_hale]))[0]
    assert 0.0 < langt < 1e-6


def test_transient_fail_closed_paa_ugyldig_inngang():
    """Invalid input gives NaN — never a guess and never an exception."""
    e = TransientEngine()
    ut = e.compute(TRANS_PARAMS, np.array([-1.0, np.nan, TRANS_PARAMS["terskelmasse"]]))
    assert np.isnan(ut[0]) and np.isnan(ut[1]) and ut[2] > 0
    lk = e.lettkurve(TRANS_PARAMS, np.array([-1.0, np.nan, np.inf]))
    assert np.all(np.isnan(lk))
    assert e.validate_params(TRANS_PARAMS) is True
    ufullstendig = dict(TRANS_PARAMS)
    del ufullstendig["radius"]
    assert e.validate_params(ufullstendig) is False


def test_transient_bindingsenergi_holder_samme_fail_closed_kontrakt():
    """The helper shall not turn the squaring into a valid answer.

    compute() masks negative and non-finite mass to NaN, but
    bindingsenergi() computed E = G*M^2/R directly — and M^2 made the energy
    POSITIVE for negative mass. Someone calling the helper directly (or
    the utlost_energi path) therefore got an answer where the engine otherwise gives NaN.
    Flagged by the copilot review on PR #435; the contract shall have ONE source.
    """
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    ugyldig = np.array([-1.0, -m, np.nan, np.inf, -np.inf])
    ut = e.bindingsenergi(TRANS_PARAMS, ugyldig)
    assert np.all(np.isnan(ut)), ut
    # Valid mass is unchanged: E = G*M^2/R.
    assert np.isclose(e.bindingsenergi(TRANS_PARAMS, np.array([m]))[0],
                      TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"])
    # ...and utlost_energi() is UNAFFECTED — it is called with the declared
    # threshold mass, which is positive.
    assert np.isclose(e.utlost_energi(TRANS_PARAMS),
                      TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"])
    assert e.utlost_energi(TRANS_PARAMS) > 0


def test_transient_massekontrakten_har_een_kilde():
    """The NaN set of the helper and of compute() shall be the SAME.

    Otherwise the contract exists in two versions, and one can drift from the
    other without any test saying so.
    """
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    miks = np.array([-1.0, -m, np.nan, np.inf, -np.inf, 0.0, 0.5 * m, m, 2.0 * m])
    assert np.array_equal(np.isnan(e.bindingsenergi(TRANS_PARAMS, miks)),
                          np.isnan(e.compute(TRANS_PARAMS, miks)))


def test_transient_regime_node_selvbeskrivelse():
    e = TransientEngine()
    node = e.regime_node(TRANS_PARAMS)
    assert node["id"] == "efc.transient_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "released" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()
    tekst = json.dumps(node, ensure_ascii=False)
    assert "IDEALISED" in tekst
    # De tre andre holding->release-endepunktene skal vaere navngitt.
    for endepunkt in ("homo.aksjonspotensial", "efc.solar_flare_engine",
                      "efc.jordskjelv_engine"):
        assert endepunkt in tekst, endepunkt
    assert "ANALOGOUS_TO" in tekst
    # Scoping: the engine encodes the collapse branch, not the event stream.
    assert "kosmos.transienter" in tekst
    assert "event stream" in tekst.lower()


def test_transient_regime_node_er_gyldig_etter_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    skjema = json.loads(_SKJEMA.read_text(encoding="utf-8"))
    node = TransientEngine().regime_node(TRANS_PARAMS)
    feil = sorted(jsonschema.Draft202012Validator(
        skjema["$defs"]["RegimeNode"]).iter_errors(node), key=lambda e: list(e.path))
    if feil:
        raise AssertionError("; ".join(f"{list(e.path)}: {e.message}" for e in feil[:3]))


def test_transient_validity_deriveres_fra_parametrene():
    """The self-description shall carry the EFFECTIVE parameters — not
    hardcoded canonical numbers (the review family from victron/vann)."""
    e = TransientEngine()
    node = e.regime_node(TRANS_PARAMS)
    tekst = node["regime"]["validity"] + " " + node["regime"]["law_form"]
    alt = {
        "G": TRANS_PARAMS["G"],
        "terskelmasse": 4.0e30,
        "radius": 3.0e4,
        "vekstrate": 1.0e20,
        "stigningstid_dager": 33.0,
        "haletid_dager": 77.0,
        "stigningseksponent": 2.5,
    }
    alt_tekst = e.regime_node(alt)["regime"]["validity"]
    assert str(alt["terskelmasse"]) in alt_tekst
    assert str(alt["radius"]) in alt_tekst
    assert str(alt["vekstrate"]) in alt_tekst or str(
        alt["terskelmasse"] / alt["vekstrate"]) in alt_tekst
    for kanonisk in ("2.785e+30", "10000.0", "6.3e+19", "20.0", "40.0"):
        assert kanonisk not in alt_tekst, kanonisk
    # ...and the canonical numbers SHALL stand in the canonical text.
    for kanonisk in ("2.785e+30", "10000.0", "20.0", "40.0"):
        assert kanonisk in tekst, kanonisk


def test_transient_atlas_node_bro_test():
    """The atlas node has been inserted (epistemics v2, PR #444 r1) — the guard has
    been replaced by the bridge test: the engine's regime_node() shall agree mechanically
    with the atlas node, and the ANALOGOUS_TO relations shall be present.
    """
    atlas = json.loads(_ATLAS.read_text(encoding="utf-8"))
    noder = {n["id"]: n for n in atlas["nodes"]}
    assert "efc.transient_engine" in noder
    motornode = TransientEngine().regime_node(TRANS_PARAMS)
    atlasnode = noder["efc.transient_engine"]
    for felt in ("id", "regime", "phase", "perspektiv"):
        assert motornode[felt] == atlasnode[felt], felt
    # The card's requirement, explicitly: validity and law_form are FIELD-identical
    # with regime_node() (mechanically), not prose-like.
    assert atlasnode["regime"]["validity"] == motornode["regime"]["validity"]
    assert atlasnode["regime"]["law_form"] == motornode["regime"]["law_form"]
    # The stipulations shall mirror the engine (review requirement: no empty mask)
    assert atlasnode["stipulasjoner"]["motor"] == "transient"
    assert atlasnode["stipulasjoner"]["terskler"]
    # The ANALOGOUS_TO relations
    objekter = {r["object"] for r in atlas.get("relations", [])
                if r.get("subject") == "efc.transient_engine"
                and r.get("predicate") == "ANALOGOUS_TO"}
    assert objekter == {"homo.aksjonspotensial",
                        "efc.solar_flare_engine",
                        "efc.jordskjelv_engine"}


# ----------------------------------------------------------------------
# Shared discipline
# ----------------------------------------------------------------------


def test_alle_tre_motorene_er_idealisert_merket():
    """The engines shall THEMSELVES say that they are idealized regime models —
    not prediction tools for single events."""
    for e, params in ((SolarFlareEngine(), SOLFLARE_PARAMS),
                      (JordskjelvEngine(), JORDSKJELV_PARAMS),
                      (TransientEngine(), TRANS_PARAMS)):
        node = e.regime_node(params)
        assert "idealis" in json.dumps(node).lower() or \
               "ideal" in json.dumps(node).lower()


def test_alle_tre_motorene_er_terskelstyrte_ikke_tidsstyrte():
    """The same shape in three domains: below the threshold NOTHING happens, above
    the threshold the buffer is released. Time alone releases nothing."""
    solar = SolarFlareEngine()
    assert solar.compute(SOLFLARE_PARAMS, np.array([0.29]))[0] == 0.0
    assert solar.compute(SOLFLARE_PARAMS, np.array([0.31]))[0] > 0.0

    jord = JordskjelvEngine()
    assert jord.compute(JORDSKJELV_PARAMS, np.array([2.9e6]))[0] == 0.0
    assert jord.compute(JORDSKJELV_PARAMS, np.array([3.1e6]))[0] > 0.0

    trans = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    assert trans.compute(TRANS_PARAMS, np.array([0.99 * m]))[0] == 0.0
    assert trans.compute(TRANS_PARAMS, np.array([1.01 * m]))[0] > 0.0


def test_alle_tre_motorene_deler_fail_closed_kontrakten():
    """The same shape ALSO for invalid input: the three buffers charge from
    zero, so negative or non-finite input is outside the window in
    all three. Measured for the contract: sol and jord answered 0.0 ("holding")
    for NaN, while transient answered NaN — one shape, two answers. Now the answer is
    NaN in all three, with the same predicate.
    """
    ugyldig = np.array([-1.0, np.nan, np.inf, -np.inf])
    for e, params in ((SolarFlareEngine(), SOLFLARE_PARAMS),
                      (JordskjelvEngine(), JORDSKJELV_PARAMS),
                      (TransientEngine(), TRANS_PARAMS)):
        ut = e.compute(params, ugyldig)
        assert np.all(np.isnan(ut)), (e.name, ut)


def test_sol_og_jord_atlasnodene_folger_motorenes_validity():
    """The fields the engine OWNS — regime.validity and regime.law_form — shall
    be FIELD-identical also for the solar and earthquake node.

    The bridge test for the transient node already exists; these two are not in
    BROER in efc_bro_synk.py, so without this test the text could drift
    from the engine in silence (the drift class efc_bro_synk.py was written
    for: the engine was tightened, the atlas was not regenerated).
    """
    atlas = json.loads(_ATLAS.read_text(encoding="utf-8"))
    noder = {n["id"]: n for n in atlas["nodes"]}
    for e, params, nid in (
            (SolarFlareEngine(), SOLFLARE_PARAMS, "efc.solar_flare_engine"),
            (JordskjelvEngine(), JORDSKJELV_PARAMS, "efc.jordskjelv_engine")):
        assert nid in noder, nid
        motor = e.regime_node(params)["regime"]
        assert noder[nid]["regime"]["validity"] == motor["validity"], nid
        assert noder[nid]["regime"]["law_form"] == motor["law_form"], nid

