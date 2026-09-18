"""EFC Orbital Engine — Kepler and orbital regimes (L-037).

Orbital mechanics as EFC forms: a bound orbit is HOLDING (negative
specific energy — the object is held in a regime), unbound flight is
RELEASE (the binding breaks), resonance is period locking (phase
holding), and the Hill sphere is the potential buffer that holds a moon
against its central body.

The model is IDEALISED two-body mechanics (Kepler + vis-viva + Hill).
It is NOT an N-body simulator and does not predict perturbations —
that is stated in the self-description. The formulas are the most
testable in the whole engine layer: predictions for known objects with
known numbers.

EFC role: the orbital regimes are the periodic flow form — ANALOGY to
the heart's fill-pressure cycle (periodic holding->release) and the
charging process, not identity: the orbital mechanics is conservative
and reversible, the heart is dissipative.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class OrbitalEngine(EFCEngine):
    """Two-body orbital mechanics with EFC regime classification (idealised)."""

    REQUIRED_PARAMS = [
        "G",          # m^3/(kg s^2) — the gravitational constant
        "M_sentral",  # kg — the central body's mass
        "a",          # m — the semi-major axis
        "e",          # 1 — the eccentricity
        "m_objekt",   # kg — the object's mass
    ]

    @property
    def name(self) -> str:
        return "orbital"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def _m_tot(self, params: dict) -> float:
        return params["M_sentral"] + params["m_objekt"]

    def periode(self, params: dict) -> float:
        """Kepler's third law: T = 2π sqrt(a^3 / (G M_tot))."""
        return float(2 * np.pi
                     * np.sqrt(params["a"] ** 3
                               / (params["G"] * self._m_tot(params))))

    def hastighet(self, params: dict, r: float) -> float:
        """Vis-viva: v = sqrt(GM(2/r - 1/a))."""
        return float(np.sqrt(params["G"] * self._m_tot(params)
                             * (2.0 / r - 1.0 / params["a"])))

    def spesifikk_energi(self, params: dict, r: float) -> float:
        """eps = v^2/2 - GM/r = -GM/(2a) (constant along the orbit)."""
        return float(-params["G"] * self._m_tot(params)
                     / (2.0 * params["a"]))

    def hill_sfaere(self, params: dict) -> float:
        """r_H = a (m/(3M))^(1/3) — the APPROXIMATE influence/
        stability boundary against the central body (not a guarantee
        that the binding breaks — crossing the boundary makes the orbit
        unstable, not necessarily unbound)."""
        return float(params["a"] * (params["m_objekt"]
                                    / (3 * params["M_sentral"])) ** (1 / 3))

    def resonans_forhold(self, periode_1: float, periode_2: float) -> float:
        """The ratio between two periods (a 3:2 resonance gives 1.5)."""
        return float(periode_1 / periode_2)

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given (a, e) pairs (N x 2), return the specific energy (J/kg).

        a > 0: elliptical orbit — negative eps = bound = HOLDING.
        a < 0: hyperbolic orbit — positive eps = unbound = RELEASE
        (the hyperbolic convention is a negative semi-major axis; eps =
        -GM/(2a) then gives a positive value automatically).
        a == 0 or invalid parameters: NaN.
        """
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        coords = np.asarray(coordinates, dtype=float)
        if coords.ndim == 1:
            coords = coords.reshape(1, -1)
        m_tot = params_dict["M_sentral"] + params_dict["m_objekt"]
        out = []
        for row in coords:
            a = float(row[0])
            if a == 0:
                out.append(np.nan)
            else:
                out.append(-params_dict["G"] * m_tot / (2.0 * a))
        return np.array(out)

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        r_h = self.hill_sfaere(params)
        validity = (
            "Two-body Kepler regime: bound orbit (eps < 0) is HOLDING — "
            "the object is held in the regime; unbound flight (eps >= 0) is "
            "RELEASE — the binding is broken (hyperbolic orbits: negative "
            "a gives eps > 0). IDEALISED: no perturbations, no "
            "N-body, no atmospheric drag. The Hill sphere ("
            + f"{r_h:.3e}" + " m) is the APPROXIMATE influence/"
            "stability boundary against the central body — crossing it makes "
            "the orbit unstable, not necessarily unbound. Predicts "
            "single orbits, NOT N-body dynamics."
        )
        law_form = ("Kepler: T = 2π sqrt(a^3/(GM)); vis-viva: "
                    "v^2 = GM(2/r - 1/a); eps = -GM/(2a); "
                    "r_H = a (m/(3M))^(1/3)")
        return {
            "id": "efc.orbital_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["epsilon = -GM/(2a): a<0 (hyperbolic) gives release — energy boundary", "the Hill sphere — approximate stability boundary — boundary"],
            "motor": "orbital"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "masse", "tid", "hastighet"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the staircase its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Orbital regimes — Kepler and binding thresholds",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "period, velocity, specific energy, Hill sphere",
                "measurer": "analytical two-body mechanics",
                "instrument": "OrbitalEngine (efc_inference/engine/orbital.py)",
                "proxy_chain": [
                    "a, e -> T (Kepler)",
                    "a, r -> v (vis-viva)",
                    "eps = -GM/(2a) -> holding/release",
                ],
                "placement": "one (a, e) point at a time in the two-body regime",
                "compression": "orbital elements -> (T, v, eps, r_H)",
            },
            "episenter": "the binding threshold eps = 0: the point where an orbit goes from held to released — capture and escape meet there",
            "buffer": {
                "role": "the Hill sphere is the orbit's APPROXIMATE stability buffer: inside it the central body's grip dominates; outside it the orbit becomes unstable (without the binding necessarily breaking)",
                "note": "ANALOGY to the heart's fill-pressure cycle (periodic holding->release) — not identity: the orbital mechanics is conservative and reversible, the heart is dissipative.",
            },
            "ontology": {
                "assumes": [
                    "tolegeme-approksimasjonen gjelder (sentral masse dominerer)",
                    "banene er Kepler-ellipser (ingen perturbasjoner)",
                ],
                "source": "Keplers lover, vis-viva, Hill-sfæren (standard himmelmekanikk); analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "the engine sees only (a, e) — no resonance map, no perturbation history",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "orbit -> period -> phase -> next revolution — the orbit's endless loop",
                "properties": ["T", "v", "eps", "r_H"],
            },
            "fractal": {
                "pattern": "periodic flow with a binding threshold: orbit, cardiac cycle, charge cycle (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one object, one orbit",
                "global": "the orbits are the regimes of the planetary system and the satellites — ANALOGOUS_TO homo.hjerte_syklus",
                "empathy_note": "the orbit does not ask — it just goes, held by nothing other than the energy.",
            },
        }
