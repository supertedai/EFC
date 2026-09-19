"""Tests for the first self-consistent EFC background solver (L-033).

Source — the action paper (docs/papers/efc/EFC_Relativistic_Action_Field_
Equations_Perturbation_Theory_and_Extraction), section 4.1:

    3 M_Pl^2 F(phi_bar) H^2 = rho_bar_m + 1/2 K(rho_bar) phi_dot_bar^2
                              + V(phi_bar) + 3 M_Pl^2 H F_dot
                              + lambda_dot_bar phi_dot_bar            (12)
    phi_bar_ddot + 3 H phi_dot_bar = Gamma(rho_bar)                      (13)

HONESTY — this is the FIRST background, not a Boltzmann code:
    * The solver integrates (12) and (13) together with matter conservation
      and the response field lambda (eq. 10). CMB, PERTURBATIONS and EFCLASS
      are not implemented.
    * V(phi) is unspecified in the paper. We choose V = const (Lambda-like)
      because the LCDM limit (the card's falsifier) needs a Lambda term.
    * K0 is blind in the background's phi dynamics when phi_dot = Gamma = 0 —
      the flow condition (13) is geometric and does not contain K.

MEASURED TOLERANCES (this test file is where they live):
    * LCDM limit:          max relative error ~1e-10  (assert < 1e-8)
    * H(z) consistency:    ~2e-6 at z_max = 2         (assert < 1e-5)
    * constraint residual: ~4e-6 at z_max = 2         (assert < 1e-4)
    The residual is STRUCTURAL (unchanged from rtol 1e-8 to 1e-11) and scales
    as K'(rho) = k0/(omega_crit(1-x)^2) — the paper's own neglect of
    delta K/delta g^mu_nu (section 2.1, "Note on delta K"). It is tested.

TDD: written before efc_inference/engine/efc_background.py existed.
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
    jsonschema is None, reason="jsonschema is not installed")


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

# The paper's own reference choices where they exist: alpha = 0.01 (the
# paper's default), K0 = 1 (the reference code). LCDM limit: alpha = gamma0 = 0
# and phi_dot = lambda_dot = 0 at z=0.
LCDM = {
    "alpha": 0.0,
    "k0": 1.0,
    "omega_crit": 1.0e3,
    "gamma0": 0.0,
    "Omega_m": 0.3,
    "V0": None,          # None -> V0 from the z=0 normalization (flat closure)
    "phi0": 0.0,
    "phi_dot0": 0.0,
    "lam0": 0.0,
    "lam_dot0": 0.0,
}

# Active EFC background: non-minimal coupling AND flow condition active.
EFC = {**LCDM, "alpha": 0.01, "gamma0": 0.05}


def bro_kanoniske() -> dict:
    """Canonical parameters for the engine's ATLAS NODE.

    One source for the test and the bridge sync (scripts/maintenance/
    efc_bro_synk.py). ``H0`` is included because ``compute()`` measures H(z)
    in km/s/Mpc; ``regime_node()`` reads only the dimensionless core, and
    knows the source is this file — not a guess at which module-level dict is
    "the canonical one".
    """
    return {**EFC, "H0": 70.0}


def _lcdm_E(z, Omega_m=0.3, V0=0.7):
    """Flat LCDM (no radiation): E^2 = Omega_m(1+z)^3 + Omega_L."""
    z = np.asarray(z, dtype=float)
    return np.sqrt(Omega_m * (1.0 + z) ** 3 + V0)


def _lcdm_kurve(z, **kw):
    """Varies omega_crit/k0 and returns the residual from the solution."""
    params = {**EFC, "alpha": 0.0, "gamma0": 0.0, "phi_dot0": 0.05,
              "omega_crit": 1.0e3, "k0": 1.0, **kw}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=51,
                                           rtol=1e-11, atol=1e-13)
    return sol.diagnostics["constraint_residual_max"]


# ---------------------------------------------------------------------------
# 1. The action's response functions (eq. 2, 47, 48)
# ---------------------------------------------------------------------------

def test_K_divergerer_ved_rho_crit_eq2():
    """K(rho) = K0/(1 - rho/rho_crit) — diverges at rho >= rho_crit.

    Same boundary behaviour as mu_kz.k_rho (and the reference code
    efc_relativistic.py:26-29): the stiffness is not defined outside.
    """
    assert np.isclose(kinetic_stiffness(1.0, 0.0), 1.0)
    assert np.isclose(kinetic_stiffness(1.0, 0.5), 2.0)
    assert np.isinf(kinetic_stiffness(1.0, 1.0))
    assert np.isinf(kinetic_stiffness(1.0, 1.5))


def test_gamma_og_gamma_prime_eq47_48():
    """Gamma and Gamma' are exactly eq. 47/48 — and identical to the
    mu(k,z) module's functions for the same parameters. The background and
    mu(k,z) must not be able to drift apart in their formulas."""
    from efc_inference.engine.mu_kz import gamma_rho, gamma_prime_rho

    g0, x = 0.7, 0.4
    mu_params = {"gamma0": g0, "rho_crit": 1.0}
    assert np.isclose(gamma_of_rho(g0, x), gamma_rho(mu_params, x))
    assert np.isclose(gamma_prime_of_rho(g0, x),
                      gamma_prime_rho(mu_params, x))


# ---------------------------------------------------------------------------
# 2. The LCDM limit test (the card's falsifier)
# ---------------------------------------------------------------------------

def test_lcdm_grensen_reproduserer_standard_friedmann():
    """alpha = gamma0 = 0, phi_dot = lambda_dot = 0, V = const:
    the solver must reproduce standard flat LCDM within the measured tolerance.

    This IS the falsifier: a background solver that does not take the LCDM
    limit is wrong, however elegant it looks in the other regime. The tolerance
    is reported (sol.lcdm_max_rel_error) — not merely claimed to be small.
    """
    sol = EFCBackgroundSolver(LCDM).solve(z_max=3.0, n_points=301)
    assert sol.status == "ok"
    feil = float(np.max(np.abs(sol.E / _lcdm_E(sol.z) - 1.0)))
    assert feil < 1e-8, f"measured deviation from LCDM: {feil:.3e}"
    assert sol.lcdm_max_rel_error is not None
    assert sol.lcdm_max_rel_error < 1e-8
    # and the solver must not boast: it reports the measured number
    assert np.isclose(sol.lcdm_max_rel_error, feil, rtol=1e-3, atol=1e-12)


def test_lcdm_grensen_er_ikke_definert_naar_phi_dot_er_ikke_null():
    """With phi_dot != 0 the background is NOT LCDM (stiff kinetic energy) —
    then the solver must say 'not defined', not report a number."""
    params = {**LCDM, "phi_dot0": 0.05}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=51)
    assert sol.lcdm_max_rel_error is None


def test_z0_normalisering_H0_og_a0():
    """a(z=0) = 1 and H(z=0) = H0 — the normalization is in the contract."""
    for params in (LCDM, EFC):
        sol = EFCBackgroundSolver(params).solve(z_max=2.0, n_points=101)
        assert np.isclose(sol.a[0], 1.0, rtol=0, atol=1e-12)
        assert np.isclose(sol.E[0], 1.0, rtol=0, atol=1e-10), params
        assert np.isclose(sol.z[0], 0.0)


def test_a_er_noeyaktig_en_over_en_pluss_z():
    """a = 1/(1+z) is an exact invariant, not something the integrator may
    drift. (Error class found during development: a missing E factor in
    d rho_m/dz and da/dz — the residual exposed it, this test prevents
    a repeat.)"""
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=101)
    assert np.allclose(sol.a, 1.0 / (1.0 + sol.z), rtol=1e-9, atol=1e-12)


def test_k0_er_blind_i_bakgrunnen_naar_phi_dot_og_gamma_er_null():
    """Structural honesty: K0 does NOT enter the phi dynamics.

    The flow condition (13) is geometric — K(rho) appears only in the
    energy density (12) and in the lambda equation (10), both multiplied
    by phi_dot. With phi_dot = Gamma = 0 the background is therefore
    identical for K0 = 1 and K0 = 1e6. That is a property of the paper's
    equations, not of the code — and it must be measured, not assumed.
    """
    a = EFCBackgroundSolver({**LCDM, "k0": 1.0}).solve(z_max=2.0, n_points=51)
    b = EFCBackgroundSolver({**LCDM, "k0": 1.0e6}).solve(z_max=2.0, n_points=51)
    assert np.allclose(a.E, b.E, rtol=0, atol=1e-12)


# ---------------------------------------------------------------------------
# 3. Internal consistency: solver H(z) vs modified Friedmann directly (12)
# ---------------------------------------------------------------------------

def test_h_z_stemmer_med_modified_friedmann_direkte():
    """The card's requirement 3: H(z) from the integrated solution must agree
    with H(z) from eq. (12) evaluated DIRECTLY on the solution's state.

    The integration drives E through the acceleration equation (eq. 7, the
    (i,j) part); (12) is used only as an initial condition. That the residual
    stays small along the whole solution is therefore a real consistency
    measurement — not a tautology. Measured for the reference parameters:
    order of magnitude 1e-6.
    """
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=201)
    assert sol.status == "ok"
    assert sol.h_consistency_max_rel < 1e-5, sol.h_consistency_max_rel


def test_constraint_residualen_rapporteres_med_definisjon():
    """(12) must hold along the solution — the residual is measured, named and
    defined in plain language."""
    sol = EFCBackgroundSolver(EFC).solve(z_max=2.0, n_points=201)
    d = sol.diagnostics
    assert "constraint_residual_max" in d
    assert d["constraint_residual_max"] < 1e-4, d["constraint_residual_max"]
    assert d["constraint_residual_definition"]
    assert d["h_consistency_definition"]
    assert "K'" in d["constraint_residual_cause"]


def test_constraint_residualen_er_strukturell_ikke_numerisk():
    """The residual must be a property of the EQUATIONS, not of the
    integrator: a tighter rtol must not remove it.

    The baseline (alpha = 0, phi_dot = 0) sits at integration level (~1e-11).
    With the EFC terms active it is ~1e-6 — five orders of magnitude up.
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
    """The measured CAUSE: the residual scales as K'(rho).

    The paper says so itself (section 2.1, "Note on delta K"): since K depends
    on rho, which depends on the metric, delta K/delta g^mu_nu contributes
    extra terms that are NEGLECTED. The residual is precisely measured to
    follow K' = k0/(omega_crit (1-x)^2): proportional to 1/omega_crit, to k0
    and to phi_dot^2 — and zero when phi_dot = 0.
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
# 4. The rho_crit domain: K diverges — the solver must stop honestly
# ---------------------------------------------------------------------------

def test_rho_crit_domenet_stopper_aerlig():
    """rho_crit = 0.45 * 3 M_Pl^2 H0^2 with Omega_m = 0.3: rho_bar reaches
    rho_crit at (1+z)^3 = 1.5, that is z = 0.1447.

    The solver must stop there and say so — not return numbers it has no
    coverage for. Everything after the crossing must be NaN.
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
    # rho at the last valid GRID POINT — not exactly rho_crit, because the
    # crossing falls between two grid points (dz = 0.01 -> ~2 % in rho here).
    assert sol.diagnostics["rho_crit_rho"] == pytest.approx(0.45, rel=0.02)


def test_rho_over_rho_crit_i_loesningen_er_aldri_over_en():
    """No point in the returned solution may have rho >= rho_crit."""
    params = {**LCDM, "omega_crit": 0.45, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=2.0, n_points=201)
    x = (sol.rho_m / params["omega_crit"])[np.isfinite(sol.E)]
    assert x.size > 0
    assert np.max(x) <= 1.0 + 1e-9


def test_ugyldig_starttilstand_gir_ingen_tall():
    """Omega_m > omega_crit already at z=0: no coverage, no numbers."""
    params = {**LCDM, "omega_crit": 0.25, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=21)
    assert sol.status == "invalid_state"
    assert not np.any(np.isfinite(sol.E))


# ---------------------------------------------------------------------------
# 5. Self-description: regime_node() — honest validity ranges
# ---------------------------------------------------------------------------

def test_regime_node_er_en_gyldig_regime_node():
    """Self-description must validate against the RegimeNode schema."""
    node = EFCBackgroundEngine().regime_node(EFC)
    assert node["id"] == "efc.efc_background_engine"
    if jsonschema is not None:
        s = json.loads((_REPO / "schema" / "regime_node.schema.json")
                       .read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(
            {"$schema": s["$schema"], "$defs": s["$defs"],
             "$ref": "#/$defs/RegimeNode"}).validate(node)


def test_regime_node_deklarerer_at_bakgrunnen_er_foerste_og_boltzmann_aapen():
    """The honesty requirement: the node must say what it is NOT. A background
    without Boltzmann/CMB that does not say so is read as a full solution."""
    node = EFCBackgroundEngine().regime_node(EFC)
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "foerste" in tekst or "første" in tekst
    assert "boltzmann" in tekst
    assert "aapen" in tekst or "åpen" in tekst
    # the V choice must be in plain language (the paper gives no V(phi))
    assert "v = const" in tekst or "v=const" in tekst
    # and the regime must declare validity + law form
    assert node["regime"]["validity"]
    assert "3 M_Pl" in node["regime"]["law_form"]


def test_regime_node_beskriver_de_effektive_parametrene():
    """The self-description must come from the EFFECTIVE parameters, not from
    canonical numbers — the same requirement the engine bridge put on the
    water engine."""
    alt = {**EFC, "alpha": 0.02, "gamma0": 0.11, "Omega_m": 0.27}
    node = EFCBackgroundEngine().regime_node(alt)
    tekst = node["regime"]["validity"]
    assert "0.02" in tekst
    assert "0.11" in tekst
    assert "0.27" in tekst
    assert "0.3}" not in tekst and "Omega_m=0.3," not in tekst


def test_honesty_feltet_faar_ikke_lov_aa_skryte():
    """The solution carries its own caveats — machine-readable."""
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
# 6. The conventions are explicit and measured
# ---------------------------------------------------------------------------

def test_sign_konvensjonen_er_eksplisitt():
    """The paper's eq. (12) has +3 M_Pl^2 H F_dot; the direct variation of the
    action (eq. 1) in the same signature gives -3 M_Pl^2 H F_dot. Both must be
    selectable EXPLICITLY — no silent convention change."""
    assert NONMINIMAL_SIGN_PAPER == 1.0
    assert NONMINIMAL_SIGN_STANDARD == -1.0
    a = EFCBackgroundSolver(EFC,
                            nonminimal_sign=NONMINIMAL_SIGN_PAPER
                            ).solve(z_max=1.0, n_points=51)
    b = EFCBackgroundSolver(EFC,
                            nonminimal_sign=NONMINIMAL_SIGN_STANDARD
                            ).solve(z_max=1.0, n_points=51)
    # The sign is not cosmetic: with alpha != 0 the two conventions give
    # measurably different H(z).
    assert not np.allclose(a.E, b.E, rtol=1e-9)
    assert a.honesty["nonminimal_sign"] != b.honesty["nonminimal_sign"]


def test_den_maalte_dommen_over_sign_konvensjonen():
    """Which sign closes its own background equation best? It is MEASURED.

    The residual of (12) along the solution is the measurable verdict.
    Measured for the reference parameters (alpha=0.01, gamma0=0.05, z_max=1):
    the paper's printed sign gives ~2.5e-7, the direct variation ~4.7e-7.
    The paper's sign is therefore the default — not because it is printed in
    the paper, but because it measures as the one that closes best.
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
    """The paper's eq. (12) has only lambda_dot phi_dot; the full eq. (6) also
    has the lambda terms. The paper's own note (2.1) says the forms differ by
    boundary terms — which one closes best is measured, not assumed."""
    from efc_inference.engine.efc_background import LAMBDA_STRESS_FORMS

    assert set(LAMBDA_STRESS_FORMS) == {"paper_eq12", "full_eq6"}
    ut = {}
    for form in LAMBDA_STRESS_FORMS:
        sol = EFCBackgroundSolver(EFC, lambda_stress=form).solve(
            z_max=1.0, n_points=51, rtol=1e-11, atol=1e-13)
        ut[form] = sol.diagnostics["constraint_residual_max"]
        assert np.isfinite(ut[form]) and ut[form] < 1e-5, ut
    # Measured: full eq. (6) gives a smaller residual than the paper form.
    assert ut["full_eq6"] < ut["paper_eq12"], ut


def test_ukjent_konvensjon_avvises():
    """No silent fallback on convention choices."""
    with pytest.raises(ValueError):
        EFCBackgroundSolver(EFC, nonminimal_sign=0.5)
    with pytest.raises(ValueError):
        EFCBackgroundSolver(EFC, lambda_stress="something-else")


def test_engine_compute_gir_H_i_km_s_Mpc_og_nan_utenfor_domenet():
    """The engine surface: H(z) = H0 * E(z). H0 is a unit conversion out."""
    e = EFCBackgroundEngine()
    params = {**LCDM, "H0": 70.0}
    z = np.array([0.0, 0.5, 1.0])
    H = e.compute(params, z)
    assert H.shape == z.shape
    assert np.all(np.isfinite(H))
    assert np.isclose(H[0], 70.0, rtol=1e-9)
    # and it must agree with the solver E(z)
    sol = EFCBackgroundSolver(LCDM).solve(z_max=1.0, n_points=2001)
    assert np.allclose(H, 70.0 * np.interp(z, sol.z, sol.E), rtol=1e-6)

    # outside rho_crit: no coverage -> NaN, not extrapolation
    params2 = {**LCDM, "H0": 70.0, "omega_crit": 0.45}
    H2 = e.compute(params2, np.array([0.05, 1.5]))
    assert np.isfinite(H2[0])
    assert np.isnan(H2[1])


def test_engine_avviser_manglende_parametre():
    """validate_params must catch missing keys before it raises."""
    e = EFCBackgroundEngine()
    assert not e.validate_params({**LCDM, "H0": 70.0, "alpha": np.nan})
    H = e.compute({**LCDM, "H0": 70.0, "alpha": np.nan}, np.array([0.1]))
    assert np.isnan(H[0])


# ---------------------------------------------------------------------------
# 7. The background feeds the mu(k,z) module (the card's purpose)
# ---------------------------------------------------------------------------

def test_bakgrunnen_mater_mu_kz_modulen():
    """L-033's purpose: the background inputs (phi_bar, phi_dot_bar, rho_bar,
    lambda_dot_bar) must come FROM the solution — not out of thin air.
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
    """After rho_crit there is no background — then the inputs must be NaN,
    not extrapolated."""
    params = {**LCDM, "omega_crit": 0.45, "Omega_m": 0.3}
    sol = EFCBackgroundSolver(params).solve(z_max=1.0, n_points=101)
    innganger = sol.mu_kz_inputs(z=1.0)
    assert all(np.isnan(v) for v in innganger.values())
