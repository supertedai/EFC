"""EFC Water Phase Engine — H2O phase engine (step 1, round 2).

Computes the phase-boundary curves of H2O (vapour, melt, sublimation) and
classifies the phase for a given (T, P) point, from material parameters and
the Clausius-Clapeyron equation — not from table lookup.

Model-agnostic in the CoolPack spirit: all physical constants are inputs
(REQUIRED_PARAMS), so alternative descriptions of the same regime can be
plugged in and compared without swapping the engine.

EFC role: H2O is the demonstrator axis for node/regime/phase/emergence/proxy.
The phases are regimes with their own validity ranges; the boundary curves
are the regime transitions; the triple point is the point where three
regimes meet.

Validity ranges (each regime answers NaN outside its own, measured against IAPWS):
    saturation_pressure :  t_triple <= T <= t_vap_ref
                           (the Watson correlation n=0.33 is calibrated in
                           0-100 C; at 450 K the deviation is -9.7 %, at 625 K
                           -52.5 % — hence no extrapolation towards T_c)
    melting_temperature :  0 <= P <= p_ice_ih_max (208.566 MPa, IAPWS
                           R14-08; higher pressure is other ice phases)
    sublimation_pressure:  t_sublim_min (50 K) <= T <= t_triple
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

# Watson exponent for L_v(T) in the 0-100 C window. Measured against table
# values: n=0.33 gives 2501 kJ/kg at 0 C, 2443 at 25 C, 2385 at 50 C, 2323 at 75 C
# (known values: 2501, 2442, 2383, 2321) — n=0.38 overestimates the low interval.
WATSON_EXPONENT_DEFAULT = 0.33


class WaterPhaseEngine(EFCEngine):
    """Phase-boundary engine for H2O (step 1: boundary curves + classification)."""

    REQUIRED_PARAMS = [
        "t_triple",                  # K
        "p_triple",                  # Pa
        "t_critical",                # K
        "p_critical",                # Pa (used in the classification)
        "latent_vaporization_ref",   # J/kg, at t_vap_ref
        "t_vap_ref",                 # K — also the upper calibration limit
        "p_vap_ref",                 # Pa — physical reference at t_vap_ref
                                     # (boiling point by definition: 101325 Pa)
        "latent_fusion",             # J/kg
        "latent_sublimation",        # J/kg, at ~0 C
        "gas_constant",              # J/(kg*K), R_v for H2O
        "density_ice",               # kg/m3
        "density_water",             # kg/m3
        "p_ice_ih_max",              # Pa — the ice Ih limit (IAPWS R14-08)
        "t_sublim_min",              # K — lower sublimation limit
    ]

    @property
    def name(self) -> str:
        return "water_phase"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def _watson_lv(self, params: dict, t) -> np.ndarray:
        """Latent heat of vaporisation L_v(T) via the Watson correlation.

        L_v(T) = L_ref * ((Tc - T) / (Tc - T_ref)) ** n
        For T > Tc the argument becomes negative and the result NaN — that
        is right: above the critical point there is no latent heat. (The
        engine only uses the correlation inside the calibration window
        anyway.)
        """
        n = float(params.get("watson_exponent", WATSON_EXPONENT_DEFAULT))
        tc = params["t_critical"]
        tref = params["t_vap_ref"]
        lref = params["latent_vaporization_ref"]
        return lref * ((np.asarray(tc) - np.asarray(t)) / (tc - tref)) ** n

    def saturation_pressure(self, params: dict, t: np.ndarray) -> np.ndarray:
        """Vapour pressure P_sat(T) along the liquid-gas boundary.

        Integrated Clausius-Clapeyron with L_v(T):
            P_sat(T) = p_triple * exp( int_{t_triple}^{T} L_v/(R T^2) dT )

        Validity range: t_triple <= T <= t_vap_ref. Outside: NaN
        (the correlation is calibrated in 0-100 C; extrapolation towards T_c
        was measured at -52.5 % deviation at 625 K in independent review).
        """
        t = np.atleast_1d(np.asarray(t, dtype=float))
        t0 = params["t_triple"]
        tmax = params["t_vap_ref"]
        r = params["gas_constant"]
        p0 = params["p_triple"]
        out = np.full(t.shape, np.nan)
        ok = (t >= t0) & (t <= tmax)
        if not np.any(ok):
            return out
        try:
            trapz = np.trapezoid  # numpy >= 2.0
        except AttributeError:
            trapz = np.trapz
        for i in np.flatnonzero(ok):
            ti = float(t[i])
            if abs(ti - t0) < 1e-12:
                out[i] = p0  # the integral is zero — exact by calibration
                continue
            # A dense grid that ends EXACTLY at ti — a grid that stops at
            # the last point below ti underestimates the tail and drove the
            # boiling point from 99.6 kPa to 97.3 kPa (measured).
            tt = np.linspace(t0, ti, 400)
            lv = self._watson_lv(params, tt)
            integrand = lv / (r * tt * tt)
            out[i] = p0 * np.exp(trapz(integrand, tt))
        return out

    def melting_temperature(self, params: dict, p: np.ndarray) -> np.ndarray:
        """Melting temperature T_m(P) along the solid-liquid boundary (ice Ih).

        Clausius-Clapeyron for solid-liquid with constant latent heat and
        volume change:
            T_m(P) = t_triple * exp( dv_melt * (P - p_triple) / L_f )
        where dv_melt = 1/rho_vann - 1/rho_is < 0 (ice floats).

        Validity range: 0 <= P <= p_ice_ih_max (208.566 MPa, IAPWS
        R14-08). Above it there are other ice phases — NaN, not
        extrapolation. Negative pressure is also rejected deterministically.
        """
        p = np.atleast_1d(np.asarray(p, dtype=float))
        dv = 1.0 / params["density_water"] - 1.0 / params["density_ice"]
        lf = params["latent_fusion"]
        out = np.full(p.shape, np.nan)
        ok = (p >= 0.0) & (p <= params["p_ice_ih_max"])
        out[ok] = params["t_triple"] * np.exp(
            dv * (p[ok] - params["p_triple"]) / lf)
        return out

    def sublimation_pressure(self, params: dict, t: np.ndarray) -> np.ndarray:
        """Sublimation pressure P_sub(T) along the solid-gas boundary.

        Clausius-Clapeyron with constant L_s:
            P_sub(T) = p_triple * exp( -(L_s/R) * (1/T - 1/t_triple) )
        Validity range: t_sublim_min (50 K, IAPWS R14-08) <= T <=
        t_triple. Outside: NaN (negative temperature previously gave inf).
        """
        t = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.full(t.shape, np.nan)
        ok = (t >= params["t_sublim_min"]) & (t <= params["t_triple"])
        r = params["gas_constant"]
        ls = params["latent_sublimation"]
        out[ok] = params["p_triple"] * np.exp(
            -(ls / r) * (1.0 / t[ok] - 1.0 / params["t_triple"]))
        return out

    # ------------------------------------------------------------------
    # Classification — «which phase is H2O here?»
    # ------------------------------------------------------------------

    # Relative tolerance for «the point lies on a phase boundary».
    EPS_REL = 1e-6
    EPS_T = 1e-6  # K

    def classify(self, params: dict, t: float, p: float) -> str:
        """Phase for one (T, P) point.

        Return values: solid, liquid, gas, supercritical, coexistence.
        - Supercritical requires T > T_c AND P > P_c (the convention); above
          T_c with P <= P_c there is one gas-like fluid phase.
        - A point on a phase boundary (within EPS_REL/EPS_T) is
          «coexistence» — two phases coexist there, the boundary is not
          an arbitrary side.
        """
        t = float(t)
        p = float(p)
        tc = params["t_critical"]
        pc = params["p_critical"]
        if t > tc:
            # Supercritical requires STRICTLY T > T_c and P > P_c (review round 2).
            return "supercritical" if p > pc else "gas"
        if abs(t - tc) <= self.EPS_T:
            # The critical temperature itself: P == P_c is the critical point
            # (boundary), P < P_c is gas, P > P_c beyond what the engine can judge.
            if abs(p - pc) <= self.EPS_REL * pc:
                return "coexistence"
            return "gas" if p < pc else "unknown"
        if (abs(t - params["t_vap_ref"]) <= self.EPS_T
                and abs(p - params["p_vap_ref"])
                <= self.EPS_REL * params["p_vap_ref"]):
            # The boiling point is a phase boundary — the model's P_sat(373.15)
            # lies 1.7 % below the physical definition, so the
            # reference point must be used here. Stands BEFORE the t_vap_ref
            # branch so that the tolerance is symmetric on both sides
            # of the boiling-point temperature (review round 3).
            return "coexistence"
        if t > params["t_vap_ref"]:
            # Above the calibration window P_sat is monotonically increasing,
            # and the PHYSICAL reference p_vap_ref (boiling point by
            # definition) is a lower bound for the real P_sat(T). p <= p_vap_ref
            # is CERTAINLY gas. Higher p the engine cannot judge honestly —
            # «unknown», not a guessed side.
            return "gas" if p <= params["p_vap_ref"] else "unknown"
        if t < params["t_triple"]:
            p_vap = float(self.sublimation_pressure(
                params, np.array([t]))[0])
        else:
            p_vap = float(self.saturation_pressure(
                params, np.array([t]))[0])
        t_melt = float(self.melting_temperature(params, np.array([p]))[0])
        if (abs(p - p_vap) <= self.EPS_REL * max(p_vap, 1.0)
                or abs(t - t_melt) <= self.EPS_T):
            return "coexistence"
        if t < t_melt:
            return "gas" if p < p_vap else "solid"
        return "gas" if p <= p_vap else "liquid"

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Primary observable: the vapour curve. coordinates = 1-D T array (K).

        The contract: invalid or missing parameters and wrong
        coordinate shapes give a NaN array — never an exception.
        """
        coordinates = np.asarray(coordinates, dtype=float)
        try:
            ok = self.validate_params(params_dict)
        except (TypeError, ValueError):
            # Invalid parameter types (None, string, array) must fail
            # closed as NaN, not as an exception (review round 2).
            ok = False
        if coordinates.ndim != 1 or not ok:
            return np.full(coordinates.shape, np.nan)
        return self.saturation_pressure(params_dict, coordinates)

    # ------------------------------------------------------------------
    # The engine↔schema bridge — the engine's self-description as regime node
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        """Full RegimeNode per schema/regime_node.schema.json.

        The bridge between engine and atlas: any EFCEngine with this method
        is a valid node in the EFC atlas — the coupling graph and the regime
        instances can consume the self-description mechanically. The manifest
        below is a backwards-compatible projection of this.

        Id and validity range are NOT local choices: they must agree with
        the h2o nodes' declared regimes in schema/regime_nodes.jsonld —
        the consistency is tested mechanically (tests/test_engine_manifest_bridge.py).
        The limits are DERIVED from the effective parameters, so that the
        self-description never lies about the engine's actual regimes —
        also with alternative parameters (review 2026-09-16).
        """
        t_vap = params["t_vap_ref"]
        p_ice = params["p_ice_ih_max"]
        t_sub = params["t_sublim_min"]
        n = float(params.get("watson_exponent", WATSON_EXPONENT_DEFAULT))
        validity = (
            "vapour ["
            + str(params["t_triple"]) + ", " + str(t_vap) + "] K; "
            "melt [0, " + str(p_ice / 1e6) + "] MPa (ice Ih); "
            "sublimation [" + str(t_sub) + " K, t_triple] — "
            "for canonical parameters identical to the h2o nodes' validity ranges"
        )
        law_form = ("Clausius-Clapeyron with Watson L_v(T) (n=" + str(n)
                    + ") — numerical integration, no table lookup")
        return {
            "id": "efc.water_phase_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["0 C / 273.15 K — the melting point (at 1 atm) — phase boundary", "100 C / 373.15 K — the boiling point (at 1 atm) — phase boundary"],
            "motor": "water"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "The H2O phase boundaries are the IAPWS standard's institutional consensus; the EFC engine is OUR recomputation of them — an error in it hits only us, and nobody in thermodynamics gains from re-checking it.",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["temperatur", "trykk"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # still stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 2,
                "forelder": "h2o.liquid",
                "tidsskala": "s (motor time)",
                "lengdeskala": "macro (P-T space)"
            },            "regime": {
                "name": "H2O phase-boundary computation",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "phase boundaries P_sat(T), T_m(P), P_sub(T)",
                "measurer": "numerical integration of Clausius-Clapeyron",
                "instrument": "WaterPhaseEngine (efc_inference/engine/water.py)",
                "proxy_chain": [
                    "P_sat(T) via Watson L_v(T)",
                    "T_m(P) via dv_melt = 1/rho_vann - 1/rho_is",
                    "P_sub(T) via constant L_s"
                ],
                "placement": "P-T space — the engine computes one (T,P) point at a time",
                "compression": "boundary curves + phase classification (solid/liquid/gas/supercritical + coexistence/unknown)"
            },
            "episenter": "The P-T landscape — the engine reads the same landscape as the h2o nodes, and declares the same boundaries",
            "buffer": {
                "role": "the validity ranges are the engine's buffer: outside them it answers NaN/unknown instead of extrapolating",
                "note": "the buffer logic in instrument form: the engine damps its own overreach."
            },
            "ontology": {
                "assumes": [
                    "the material parameters (latent heats, densities, critical constants) are correct",
                    "Clausius-Clapeyron applies in the declared regimes"
                ],
                "source": "IAPWS R6-95/R14-08; standard thermodynamics; review-verified against IAPWS (2026-09-16)"
            },
            "observer": {
                "er_del_av_systemet": True,
                "bandwidth": "the engine sees only T and P — no optical, acoustic or chemical channels",
                "awareness": "instrument_window"
            },
            "emergence": {
                "loop": "parameters -> boundary curves -> phase classification -> calibration against the triple point -> parameters",
                "properties": [
                    "phase classification",
                    "declared validity range per curve"
                ]
            },
            "fractal": {
                "pattern": "the same computation law in every point of the P-T landscape — the engine is an instance of the pattern the h2o nodes describe",
                "note": "one engine, one pattern, three limit curves that meet."
            },
            "coupling": {
                "local": "each curve is computed locally in its own regime",
                "global": "the validity ranges of the engine ARE those of the h2o nodes — and the bridge is tested mechanically against regime_nodes.jsonld",
                "empathy_note": "the engine knows which atlas nodes it carries (CARRIES), and the tests verify that it does not declare anything the atlas contradicts."
            },
        }

    # ------------------------------------------------------------------
    # The empathy gate — what the engine serves and is calibrated against
    # ------------------------------------------------------------------

    def manifest(self, params: dict) -> dict:
        """The engine's global coupling surface: which atlas concepts it serves,
        and which physical references it is calibrated against. Consumed by
        the coupling graph/atlas, so that local computations have a declared
        global reach (systemic empathy)."""
        return {
            "name": self.name,
            "couplings": [
                {"axis": "node",
                 "relation": "every (T,P) point is a node in the phase regime"},
                {"axis": "regime",
                 "relation": "solid/liquid/gas/supercritical are regimes "
                             "with their own validity ranges"},
                {"axis": "fase",
                 "relation": "three boundary curves that meet at the triple point"},
                {"axis": "emergens",
                 "relation": "phase properties (density, optics) change at "
                             "the transition — emergent per regime, not "
                             "linearly derived"},
                {"axis": "proxy",
                 "relation": "P_sat, T_m and P_sub are observable proxies "
                             "for the phase — the phase itself is a state"},
            ],
            "calibration": {
                "t_triple": float(params["t_triple"]),
                "p_triple": float(params["p_triple"]),
                "t_critical": float(params["t_critical"]),
            },
        }
