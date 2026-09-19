"""EFC Tidevann Engine — periodic gravitational coupling (L-039).

The tide is the periodic flow form of gravitational coupling: the moon
lifts and lowers Earth's ocean in an endless charge/drain cycle, and
tidal braking phase-locks the system (the moon always shows the same
side — holding in resonance).

The model is an IDEALIZED equilibrium model: no ocean-basin dynamics,
no coastal resonance amplification (Bay of Fundy etc.), no energy
dissipation history. The tidal height is the open-ocean scale.

The physics:
    Tidal acceleration: a_t ~ 2 G M_obj R / r^3
    Tidal height (open ocean): h ~ a_t * R / g
    The Roche limit (fluid): d = 2.44 R (rho_sentral/rho_objekt)^(1/3)
    Phase locking: rotation period == orbital period
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class TidevannEngine(EFCEngine):
    """Tidal coupling with a charge/drain cycle and phase locking (idealized)."""

    REQUIRED_PARAMS = [
        "G",               # m^3/(kg s^2)
        "M_sentral",       # kg
        "m_objekt",        # kg
        "avstand",         # m — the distance between the bodies
        "radius_sentral",  # m — the radius of the central body
        "rho_sentral",     # kg/m^3 — the density of the central body
        "rho_objekt",      # kg/m^3 — the density of the object
    ]

    @property
    def name(self) -> str:
        return "tidevann"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def tidevannsakselerasjon(self, params: dict) -> float:
        """a_t = 2 G m_obj R / r^3 — the differential gravity
        across the radius of the central body."""
        return float(2 * params["G"] * params["m_objekt"]
                     * params["radius_sentral"]
                     / params["avstand"] ** 3)

    def tidevannshoyde(self, params: dict) -> float:
        """The open-ocean scale: h ~ a_t * R / g with g = G M/R^2."""
        a_t = self.tidevannsakselerasjon(params)
        g = params["G"] * params["M_sentral"] / params["radius_sentral"] ** 2
        return float(a_t * params["radius_sentral"] / g)

    def roche_grense(self, params: dict) -> float:
        """d = 2.44 R (rho_sentral/rho_objekt)^(1/3) — the threshold where
        the tide breaks the cohesion (idealized fluid body)."""
        ratio = params["rho_sentral"] / params["rho_objekt"]
        return float(2.44 * params["radius_sentral"] * ratio ** (1 / 3))

    def er_faselaast(self, params: dict, rotasjonsperiode: float,
                     omlopsperiode: float) -> bool:
        """Phase locking: rotation synchronized with the orbit (1 % tolerance)."""
        return bool(abs(rotasjonsperiode - omlopsperiode)
                    / max(omlopsperiode, 1e-12) < 0.01)

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given distances (m), return the tidal acceleration (m/s^2)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        distances = np.asarray(coordinates, dtype=float)
        out = []
        for r in distances:
            p = {**params_dict, "avstand": float(r)}
            if float(r) <= 0:
                out.append(np.nan)
            else:
                out.append(self.tidevannsakselerasjon(p))
        return np.array(out)

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        h = self.tidevannshoyde(params)
        r_roche = self.roche_grense(params)
        validity = (
            "Tidal regime: periodic charge/drain cycle — the moon lifts "
            "and lowers the central body's ocean every orbit; phase "
            "locking is the holding of tidal braking (rotation "
            "synchronized with orbit). IDEALIZED equilibrium model: no "
            "ocean-basin dynamics, no coastal resonance amplification, "
            "no dissipation history. The Roche limit ("
            + f"{r_roche:.3e}" + " m) is the threshold where the tide "
            "breaks the cohesion."
        )
        law_form = ("a_t = 2 G m_obj R / r^3; h ~ a_t R / g; "
                    "d_roche = 2.44 R (rho_s/rho_o)^(1/3); "
                    "phase locking: P_rot = P_orbit")
        return {
            "id": "efc.tidevann_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the Roche limit ~ 2.44 R — break-up boundary — idealized"],
            "motor": "tidevann"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "The equilibrium tide and the Roche limit are textbook matter carried by oceanography; the charge/discharge reading of the cycle is the framework's, and lands outside what oceanographers would call a tide model.",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["rom", "masse", "tid"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "The tide — periodic gravitational coupling",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "tidal acceleration, tidal height, Roche limit, phase-lock status",
                "measurer": "analytic tidal model",
                "instrument": "TidevannEngine (efc_inference/engine/tidevann.py)",
                "proxy_chain": [
                    "m_obj, r -> a_t (differential gravity)",
                    "a_t -> h (open-ocean proxy)",
                    "periods -> phase-lock status",
                ],
                "placement": "one distance point at a time in the two-body tide",
                "compression": "(r, periods) -> (a_t, h, Roche, locked?)",
            },
            "episenter": "The Roche limit: the point where the periodic coupling becomes too strong and the connection breaks — the tidal regime shift",
            "buffer": {
                "role": "the sea is the buffer: it is raised and lowered in the periodic cycle without breaking — right up to the Roche limit",
                "note": "ANALOGY to the heart's fill-pressure cycle and the orbit's periodic holding — not identity: the tide is forced by an external period, the heart sets its own.",
            },
            "ontology": {
                "assumes": [
                    "equilibrium tide (no basin resonance)",
                    "The Roche limit for a fluid body (the 2.44 factor) with a simplified density ratio",
                ],
                "source": "standard tidal theory (differential gravitation, Roche); the analogy marking is the atlas's own",
            },
            "observer": {
                "bandwidth": "the engine sees only distance and periods — no basin geometry, no dissipation measurement",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "orbit -> lift -> orbit -> lower — the tide's endless loop",
                "properties": ["a_t", "h", "Roche distance", "lock status"],
            },
            "fractal": {
                "pattern": "periodic charge/drain cycle: the tide, the cardiac cycle, the charge cycle (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one body pair, one tidal cycle",
                "global": "the tide couples the moon and Earth — ANALOGOUS_TO homo.hjerte_syklus and efc.orbital_engine",
                "empathy_note": "the sea does not ask why it is lifted — it just follows, twice a day, forever.",
            },
        }
