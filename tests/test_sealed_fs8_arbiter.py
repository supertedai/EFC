"""Tests for the sealed fσ8 arbiter (step 12).

The arbiter is the machine judge against the sealed EFC prediction P2:
fσ8(z=0.7) = 0.430 (EFC) vs 0.449 (ΛCDM), sealed 2026-04-14,
DOI 10.6084/m9.figshare.32013156.

The verdict logic is three-valued — PASS / FAIL / VENTER — and every
verdict must carry the rule that decided it, with its source.
"""
from __future__ import annotations

import numpy as np

from efc_inference.arbiter.sealed_fs8 import SealedFs8Arbiter


def _arbiter() -> SealedFs8Arbiter:
    return SealedFs8Arbiter()


def _m(fs8, sigma, tracer="LRG", z_eff=0.7,
       kilde="DESI DR2 full-shape (synthetic test)"):
    return {"fsigma8": fs8, "sigma": sigma, "z_eff": z_eff,
            "tracer": tracer, "kilde": kilde}


# ----------------------------------------------------------------------
# Calibration and parameter derivation
# ----------------------------------------------------------------------
def test_nullmodellen_gir_lcdm_innen_toleranse():
    """The ΛCDM null model (alpha_cosmo=0) must give fσ8(z=0.7) close to the
    sealed ΛCDM value 0.449. Without it the verdicts are unanchored."""
    null = _arbiter().nullmodell()
    assert abs(null - 0.449) < 0.02, (
        f"the null model gave {null}, expected close to 0.449")


def test_prediksjon_er_parameter_avledet():
    """The prediction must come from the engine with the given parameters —
    not be hard-coded to 0.430."""
    arb = _arbiter()
    pred = arb.prediksjon_efc({"Omega_m": 0.3, "H0": 70.0,
                               "sigma8": 0.8, "alpha_cosmo": 0.1})
    assert isinstance(pred, float)
    assert np.isfinite(pred)
    pred2 = arb.prediksjon_efc({"Omega_m": 0.3, "H0": 70.0,
                                "sigma8": 0.8, "alpha_cosmo": 0.2})
    assert pred != pred2


def test_vurder_rapporterer_motorprediksjon_separat():
    """When parameters are given, the verdict must carry the engine prediction
    EXPLICITLY — and it must be the engine's value, not the anchor."""
    params = {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
              "alpha_cosmo": 0.1}
    arb = _arbiter()
    verdict = arb.vurder(_m(0.440, 0.03), params=params)
    assert verdict["motorprediksjon"] == arb.prediksjon_efc(params)
    assert "avstand_motorprediksjon_sigma" in verdict


# ----------------------------------------------------------------------
# VENTER without a measurement / invalid measurements
# ----------------------------------------------------------------------
def test_uten_maaling_venter_arbiteren():
    verdict = _arbiter().vurder(None)
    assert verdict["status"] == "VENTER"
    assert "DR2" in verdict["årsak"] and "full-shape" in verdict["årsak"]


def test_manglende_felt_venter():
    for field in ("fsigma8", "sigma", "z_eff", "tracer", "kilde"):
        m = _m(0.440, 0.03)
        m[field] = None
        verdict = _arbiter().vurder(m)
        assert verdict["status"] == "VENTER", field
        assert "ugyldig" in verdict["årsak"]


def test_ugyldig_sigma_venter():
    for sigma in (0.0, -0.02, float("nan"), float("inf")):
        verdict = _arbiter().vurder(_m(0.440, sigma))
        assert verdict["status"] == "VENTER", sigma


def test_feil_tracer_venter():
    """Lyα is a different tracer than galaxy RSD — the verdict must not be passed."""
    verdict = _arbiter().vurder(_m(0.440, 0.03, tracer="LyA"))
    assert verdict["status"] == "VENTER"
    assert "tracer" in verdict["årsak"]


def test_feil_z_vindu_venter():
    for z in (0.3, 1.2):
        verdict = _arbiter().vurder(_m(0.440, 0.03, z_eff=z))
        assert verdict["status"] == "VENTER", z


# ----------------------------------------------------------------------
# Confirmation (within ~1σ of 0.430)
# ----------------------------------------------------------------------
def test_innen_1sigma_av_anker_gir_pass():
    verdict = _arbiter().vurder(_m(0.440, 0.03))   # 0.33σ
    assert verdict["status"] == "PASS"
    assert verdict["regel"] and verdict["kilde"]


def test_akkurat_1sigma_gir_pass():
    """The boundary is ≤1σ (inclusive) — "~1σ"."""
    verdict = _arbiter().vurder(_m(0.430 + 0.02, 0.02))  # exactly 1.0σ
    assert verdict["status"] == "PASS"


def test_over_1sigma_av_anker_gir_ikke_pass_alene():
    """1.25σ from the anchor is not confirmation — the verdict must come from
    another rule or become VENTER."""
    verdict = _arbiter().vurder(_m(0.455, 0.02))  # 1.25σ from 0.430
    # 0.455 is 0.3σ from 0.449 → FAIL via P1 (consistent with ΛCDM),
    # not PASS.
    assert verdict["status"] != "PASS"


# ----------------------------------------------------------------------
# Falsification A (P2: >0.449 at >3σ)
# ----------------------------------------------------------------------
def test_over_3sigma_over_lcdm_gir_fail():
    verdict = _arbiter().vurder(_m(0.449 + 4 * 0.02, 0.02))  # 4.0σ over
    assert verdict["status"] == "FAIL"
    assert "P2" in verdict["regel"] or "damage" in verdict["regel"]


def test_akkurat_3sigma_over_lcdm_gir_ikke_p2_fail():
    """Exactly 3.0σ above 0.449 is NOT ">3σ" — but 3.95σ from the anchor
    triggers the P1 exclusion (≥2σ), so the verdict is still FAIL — just
    with another rule."""
    verdict = _arbiter().vurder(_m(0.449 + 3 * 0.02, 0.02))
    assert verdict["status"] == "FAIL"
    assert "P2" not in verdict["regel"]


# ----------------------------------------------------------------------
# Falsification B (P1)
# ----------------------------------------------------------------------
def test_konsistent_med_lcdm_innen_1sigma_gir_fail():
    verdict = _arbiter().vurder(_m(0.455, 0.02))  # 0.3σ from 0.449
    assert verdict["status"] == "FAIL"


def test_ekskluderer_anker_over_2sigma_gir_fail():
    verdict = _arbiter().vurder(_m(0.430 + 2 * 0.02, 0.02))  # 2.0σ over
    assert verdict["status"] == "FAIL"


def test_ekskluderer_anker_under_2sigma_gir_fail():
    """Exclusion is two-sided: a measurement BELOW 0.430 at ≥2σ
    excludes the anchor as much as one above."""
    verdict = _arbiter().vurder(_m(0.430 - 2 * 0.02, 0.02))  # 2.0σ under
    assert verdict["status"] == "FAIL"


def test_under_2sigma_fra_begge_ankre_venter():
    """1.75σ from 0.430 and 1.25σ from 0.449 (with m>0.449: not >3σ) —
    neither confirmed, excluded nor ΛCDM-consistent → VENTER."""
    verdict = _arbiter().vurder(_m(0.500, 0.04))
    assert verdict["status"] == "VENTER"


# ----------------------------------------------------------------------
# The report and the payload
# ----------------------------------------------------------------------
def test_rapporten_maaler_mu_kanalen_arlig():
    """Step 13 wired in the μ channel (EFCVariantC, mu_0). The report
    must MEASURE the actual state — both the injected engine and the
    engine layer's capability. The reproduction must be documented with
    numbers, and the text must distinguish reproducibility from proof
    about a sealed parameter value."""
    report = _arbiter().rapport()
    # The default engine is EFCVariantA — it does NOT have the channel...
    assert report["mu_kanal_i_injisert_motor"] is False
    # ...but the engine layer's capability (VariantC) is measured and documented.
    rep = report["mu_reproduksjon_variantc"]
    assert rep["variant"] == "EFCVariantC"
    assert abs(rep["fs8_mu_0_5"] - 0.430) < 0.005
    assert "reproduserbar" in report["ærlighet"]
    assert "IKKE" in report["ærlighet"]  # does not prove sealed mu_0
    assert "har IKKE" in report["ærlighet"]  # injected variant reported


def test_rapporten_med_variantc_sier_den_injiserte_har_kanalen():
    """With EFCVariantC injected the status must say so — variant-aware,
    not hard-coded."""
    from efc_inference.core.cosmology_model import EFCVariantC
    from efc_inference.engine.growth import EFCGrowth
    arb = SealedFs8Arbiter(growth=EFCGrowth(cosmology=EFCVariantC()))
    report = arb.rapport()
    assert report["mu_kanal_i_injisert_motor"] is True
    assert "HAR" in report["ærlighet"]


def test_payload_har_kriterium_og_proveniens():
    p = _arbiter().payload()
    assert p["emne"] == "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
    assert p["kriterium"]["anker_efc"] == 0.430
    assert p["kriterium"]["forseglet_doi"] == "10.6084/m9.figshare.32013156"
    assert p["proveniens"]["generert_av"] == "SealedFs8Arbiter"
