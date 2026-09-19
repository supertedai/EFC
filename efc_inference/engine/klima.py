"""EFC Klima Engine — radiation balance and regime switches (L-040).

The climate's 0D energy balance is the EFC form in pure form on Earth:
energy in (the sun), buffer (the ocean's heat capacity), threshold
transitions (the ice-albedo switch with hysteresis towards snowball
Earth).

The model is an IDEALIZED 0D energy-balance model — it is NOT a
climate-model competitor: no circulation, no clouds, no spatial
structure. That stands in the self-description. Climate modelling is a
discipline of its own with its own literature; the engine codes only the
form.

The physics:
    C dT/dt = (S/4)(1 - alpha) - eps sigma T^4
Equilibrium: T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4).
The ice-albedo switch: the albedo grows when T falls below the freezing
point — above a threshold no warm equilibrium exists (snowball Earth,
hysteresis).

DELIBERATELY OMITTED — the AMOC switch (t_9978fc90). The card for the
climate engine (L-040) names TWO regime switches: the ice-albedo
feedback and AMOC. Only ice-albedo is coded here. The AMOC switch is
ASSESSED and DELIBERATELY OMITTED: the 0D energy balance has no
circulation to switch off — AMOC is an overturning cell that requires at
least two boxes (temperature AND salinity) driven by freshwater forcing,
and neither the engine's state space (T) nor its parameter space
(S, alpha, eps, sigma, C) holds it. A Stommel box is a discipline of its
own with its own literature and belongs in an ENGINE OF ITS OWN, not in
the radiation balance. The delimitation also stands in regime_node(); it
has been made machine-visible in tests/test_klima_engine.py, not left as
silence. No AMOC threshold is stated anywhere — because none exists.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class KlimaEngine(EFCEngine):
    """0D energy-balance engine with buffer and regime switch (idealized)."""

    REQUIRED_PARAMS = [
        "solarkonstant",       # W/m^2 — S
        "albedo",              # 1 — alpha
        "emissivitet",         # 1 — eps (greenhouse effect included)
        "stefan_boltzmann",    # W/(m^2 K^4) — sigma
        "hav_varmekapasitet",  # J/(m^2 K) — C (the mixed layer)
    ]

    @property
    def name(self) -> str:
        return "klima"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def likevektstemperatur(self, params: dict) -> float:
        """T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4)."""
        s = params["solarkonstant"]
        incoming = (s / 4.0) * (1.0 - params["albedo"])
        return float((incoming / (params["emissivitet"]
                                  * params["stefan_boltzmann"])) ** 0.25)

    def tidskonstant(self, params: dict) -> float:
        """Tau = C / (4 eps sigma T_eq^3) — the buffer's inertia."""
        t_eq = self.likevektstemperatur(params)
        return float(params["hav_varmekapasitet"]
                     / (4 * params["emissivitet"]
                        * params["stefan_boltzmann"] * t_eq ** 3))

    def albedo_tilbakekobling(self, params: dict, delta_t: float) -> float:
        """The ice-albedo feedback: colder -> more ice -> higher
        albedo. The amplification factor for a temperature perturbation
        (positive feedback > 1)."""
        # Idealized: the albedo rises linearly with a fall below 0 °C
        # with slope coefficient 0.005 K^-1 (order of magnitude from
        # ice extent).
        slope = 0.005
        d_alpha = slope * (-delta_t) if delta_t < 0 else 0.0
        if d_alpha <= 0:
            return 1.0
        # T_eq sensitivity to albedo: dT_eq/d_alpha = -T_eq/(4(1-alpha))
        t_eq = self.likevektstemperatur(params)
        sensitivity = t_eq / (4 * (1 - params["albedo"]))
        amplification = 1.0 / (1.0 - sensitivity * slope)
        return float(amplification)

    def har_varm_likevekt(self, params: dict, tilstand: str = "varm") -> bool:
        """A warm equilibrium exists when T_eq > 273.15 K — with STATE-
        dependent thresholds (hysteresis): from «warm» the system falls
        only when the albedo crosses alpha_fall (where T_eq = 273.15 K);
        from «snowball» it returns only when the albedo crosses
        alpha_retur (< alpha_fall — the snowball Earth's reflectance
        stabilizes it, idealized hysteresis width)."""
        alpha_fall = self._alpha_ved_frysepunkt(params)
        alpha_retur = params.get("alpha_retur", 0.35)
        if tilstand == "snøball":
            return bool(params["albedo"] < alpha_retur)
        return bool(params["albedo"] <= alpha_fall)

    def _alpha_ved_frysepunkt(self, params: dict) -> float:
        """The albedo where T_eq crosses 273.15 K:
        alpha = 1 - 4 eps sigma T^4 / S."""
        t = 273.15
        out_radiation = 4 * params["emissivitet"] * params["stefan_boltzmann"] * t ** 4
        return float(1.0 - out_radiation / params["solarkonstant"])

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given albedo values, return T_eq (K) of the RADIATIVE
        equilibrium — NaN where the equilibrium lies below the freezing
        point (no WARM equilibrium exists there)."""
        alb = np.asarray(coordinates, dtype=float)
        out = []
        for a in alb:
            p = {**params_dict, "albedo": float(a)}
            t_eq = self.likevektstemperatur(p)
            out.append(t_eq if t_eq > 273.15 else np.nan)
        return np.array(out)

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        t_eq = self.likevektstemperatur(params)
        tau_years = self.tidskonstant(params) / (365.25 * 86400)
        validity = (
            "0D energy-balance regime: energy in (sun) -> buffer (ocean, "
            f"tau ~ {tau_years:.0f} year) -> out (emission). The ice-albedo "
            "switch is the regime transition with STATE-DEPENDENT "
            "thresholds (hysteresis): from «warm» the system falls at "
            "alpha_fall, from «snowball» it returns only at alpha_retur "
            "(< alpha_fall — the snowball's reflectance stabilizes it, "
            "idealized width). IDEALIZED 0D model — NOT a "
            "climate-model competitor: no circulation, no clouds, no "
            "spatial structure. The AMOC switch (which the card names "
            "alongside ice-albedo) is CONSIDERED and DELIBERATELY "
            "OMITTED: the 0D energy balance has no circulation to switch "
            "off — AMOC requires two boxes and freshwater forcing, and "
            "belongs in a SEPARATE ENGINE (its own discipline, its own "
            "literature). No AMOC threshold is stated — because none "
            "exists."
        )
        law_form = ("C dT/dt = (S/4)(1-alpha) - eps sigma T^4; "
                    "T_eq = [(S/4)(1-alpha)/(eps sigma)]^(1/4); "
                    "tau = C/(4 eps sigma T_eq^3)")
        return {
            "id": "efc.klima_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["alpha_fall ~ 0.4341 vs alpha_retur = 0.35 — hysteresis thresholds — state-dependent albedos", "radiation equilibrium below the freezing point -> NaN — model boundary"],
            "motor": "klima"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["temperatur", "energi", "tid"],
                "enheter": "motor-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # nonetheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "The radiation balance of the climate and its regime switches",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "equilibrium temperature, time constant, regime switch",
                "measurer": "analytic 0D energy balance",
                "instrument": "KlimaEngine (efc_inference/engine/klima.py)",
                "proxy_chain": [
                    "solar constant + albedo -> incoming radiation",
                    "eps sigma T^4 -> outgoing radiation",
                    "C -> the buffer's inertia",
                ],
                "placement": "the Earth's energy balance — one global point at a time",
                "compression": "radiation perturbations -> (T_eq, tau, switch status)",
            },
            "episenter": "the ice-albedo threshold: where the warm equilibrium disappears — the climate's regime shift",
            "buffer": {
                "role": "the ocean's heat capacity is the buffer: it damps and delays all disturbances — the broad buffer logic at global scale",
                "note": "ANALOGY to the setpoint-holding of the homeostasis buffer — not identity: the climate has no setpoint mechanism, only basins of attraction (like the ecology).",
            },
            "ontology": {
                "assumes": [
                    "the 0D approximation holds (global average)",
                    "the ice-albedo switch is idealized (linear rise below 0 °C)",
                    "The AMOC switch is ASSESSED and DELIBERATELY OMITTED (t_9978fc90): "
                    "the engine has no circulation variable — a "
                    "freshwater-driven overturning cell requires two boxes and "
                    "belongs in a SEPARATE ENGINE, not in the radiation balance",
                ],
                "source": "standard 0D energy-balance model (the Budyko-Sellers tradition); the analogy marking is the atlas's own",
            },
            "observer": {
                "bandwidth": "the engine sees only global averages — no regional dynamics",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "perturbation -> the buffer damps -> new equilibrium -> (or) switch -> new regime — the climate's loop",
                "properties": ["T_eq", "tau", "switch status"],
            },
            "fractal": {
                "pattern": "buffer + threshold switch: climate, homeostasis, ecology (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one global point",
                "global": "the climate is homo.fluxus's outer state carrier — ANALOGOUS_TO homo.okologi and homo.homeostase_buffer",
                "empathy_note": "the climate holds — until the threshold is crossed. Like all buffers.",
            },
        }
