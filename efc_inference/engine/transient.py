"""EFC Transient Engine — stellar death's holding->release engine (L-036).

Encodes the form found in the recon of kosmos.transienter (the ALeRCE/ZTF
event kind): the compact core is a buffer that HOLDS as long as the
gravitational binding carries it, and that RELEASES when the mass crosses
the stability limit — collapse, transient (supernova/GRB), remnant.

The model is IDEALISED (collapse buffer): the binding energy E = G*M^2/R
is built with the core mass, and at the stability limit the binding energy
is released at the LOCAL mass. It does NOT claim predictive power for
single events — it computes the form's observables: hold time, released
energy and the lightcurve's shape (rapid rise, exponential tail).

The fourth instance of the form already built for the Sun's flares
(SolarFlareEngine), the Earth's quakes (JordskjelvEngine) and the neuron
(homo.aksjonspotensial).

THE ATLAS LINK IS LANDED: the node efc.transient_engine stands in
schema/regime_nodes.jsonld with the three ANALOGOUS_TO endpoints
(homo.aksjonspotensial, efc.solar_flare_engine, efc.jordskjelv_engine) —
the same pattern as sun/earth/neuron. The guard that waited on the
collision order has been replaced by the bridge test
tests/test_holding_release_motorer.py::test_transient_atlas_node_bro_test,
which holds the atlas node's regime (validity + law_form) IDENTICAL to
regime_node() here — mechanically, not prose-alike.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class TransientEngine(EFCEngine):
    """Holding->release engine for the collapse buffer in a compact core (idealised)."""

    REQUIRED_PARAMS = [
        "G",                  # m^3 kg^-1 s^-2 — the gravitational constant (input)
        "terskelmasse",       # kg — the stability limit (Chandrasekhar-style model parameter)
        "radius",             # m — core radius at which the binding energy is computed
        "vekstrate",          # kg/s — mass growth (the charging)
        "stigningstid_dager",  # days — rapid rise in the lightcurve
        "haletid_dager",      # days — exponential tail
        "stigningseksponent",  # — shape parameter for the rise (alpha)
    ]

    @property
    def name(self) -> str:
        return "transient"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def _valid_mass(self, mass: np.ndarray) -> np.ndarray:
        """The engine's fail-closed contract for mass — ONE source.

        Valid mass is FINITE and NON-NEGATIVE. Anything else is outside
        the window: it yields NaN, never a guess. The predicate is
        separated out because both compute() and bindingsenergi() must
        keep the same contract — two copies drift apart (PR #435).
        """
        return np.isfinite(mass) & (mass >= 0.0)

    def bindingsenergi(self, params: dict, mass: np.ndarray) -> np.ndarray:
        """The gravitational binding E = G * M^2 / R (J) — the buffer's energy.

        Invalid input (negative or non-finite mass) is outside the window
        and yields NaN — never a guess. The squaring would otherwise have
        made the energy POSITIVE for negative mass, so a direct caller got
        a number where compute() yields NaN.
        """
        m = np.asarray(mass, dtype=float)
        out = np.full(m.shape, np.nan)
        valid = self._valid_mass(m)
        out[valid] = params["G"] * m[valid] ** 2 / params["radius"]
        return out

    def holdetid(self, params: dict) -> float:
        """Time from M=0 to the stability limit at constant growth rate (s)."""
        return float(params["terskelmasse"] / params["vekstrate"])

    def utlost_energi(self, params: dict) -> float:
        """The energy released AT the stability limit (J).

        This is the energy at the threshold — not a single event's
        measured energy. compute() uses the LOCAL mass (see the docstring
        there).
        """
        return float(self.bindingsenergi(
            params, np.array([params["terskelmasse"]]))[0])

    def lettkurve(self, params: dict, times_dager: np.ndarray) -> np.ndarray:
        """Normalised lightcurve shape (maximum 1.0 at stigningstid_dager).

        The shape is PARAMETERISED, not derived: a rapid rise
        (t/t_stig)^alpha up to the knee, then an exponential tail
        exp(-(t-t_stig)/t_hale). The knee is SET by stigningstid_dager —
        it is not detected from a series, and the shape claims no regime
        change beyond the parameterised maximum value.

        Times in DAYS (the parameters are named _dager); negative or
        non-finite times are outside the window and yield NaN.
        """
        t = np.asarray(times_dager, dtype=float)
        t_stig = float(params["stigningstid_dager"])
        t_hale = float(params["haletid_dager"])
        alpha = float(params["stigningseksponent"])
        out = np.full(t.shape, np.nan)
        valid = np.isfinite(t) & (t >= 0.0)
        rise_mask = valid & (t < t_stig)
        tail_mask = valid & (t >= t_stig)
        out[rise_mask] = (t[rise_mask] / t_stig) ** alpha
        out[tail_mask] = np.exp(-(t[tail_mask] - t_stig) / t_hale)
        return out

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Given core mass (kg), return released energy (J).

        Holding: mass < terskelmasse -> the core is held up, release = 0.
        Release: mass >= terskelmasse -> the binding energy at the LOCAL
        mass is released (idealised: the whole buffer is let go). The
        convention is the same as SolarFlareEngine.compute(): the energy
        follows the local point, not the declared threshold value.

        Invalid input (negative or non-finite mass) is outside the window
        and yields NaN — never a guess.
        """
        mass = np.asarray(coordinates, dtype=float)
        out = np.full(mass.shape, np.nan)
        valid = self._valid_mass(mass)
        out[valid] = 0.0
        critical = valid & (mass >= params_dict["terskelmasse"])
        out[critical] = self.bindingsenergi(params_dict, mass[critical])
        return out

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        terskelmasse = params["terskelmasse"]
        radius = params["radius"]
        vekstrate = params["vekstrate"]
        t_hold = self.holdetid(params)
        e_ut = self.utlost_energi(params)
        t_stig = params["stigningstid_dager"]
        t_hale = params["haletid_dager"]
        alpha = params["stigningseksponent"]
        validity = (
            "holding: mass < " + str(terskelmasse) + " kg — the core is "
            "held up, no release; release: mass >= " + str(terskelmasse)
            + " kg — the binding energy at the LOCAL mass is released "
            "(the energy at the threshold is " + str(e_ut) + " J). IDEALISED "
            "regime model (collapse buffer): the whole binding energy "
            "G*M^2/R is released at the stability limit, with radius "
            + str(radius) + " m and growth rate " + str(vekstrate) + " kg/s "
            "(hold time " + str(t_hold) + " s). Real supernovae distribute "
            "the energy among neutrinos, kinetic energy and radiation, and "
            "only a fraction becomes light. The stability limit is a "
            "MODEL PARAMETER (Chandrasekhar style): the real limit "
            "depends on composition, rotation and the surroundings. "
            "The lightcurve is a PARAMETERISED form — a rise over "
            + str(t_stig) + " days with exponent " + str(alpha)
            + ", then an exponential tail with timescale " + str(t_hale)
            + " days; the knee is SET by the form, not detected from a "
            "series. Does NOT predict individual events."
        )
        law_form = (
            "E_bind = G*M^2/R; hold time = threshold mass / growth rate; "
            "trigger at mass = threshold mass; light curve: (t/t_stig)^alpha "
            "up to the knee, exp(-(t-t_stig)/t_hale) after"
        )
        return {
            "id": "efc.transient_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["E_bind = G*M^2/R — the collapse buffer — threshold-governed holding->release"],
            "motor": "transient"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["masse", "rom", "tid", "energi"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # still stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Stellar death's holding->release (collapse buffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "hold time, released energy, the lightcurve's form",
                "measurer": "analytic collapse-buffer model (G*M^2/R) + parameterised lightcurve",
                "instrument": "TransientEngine (efc_inference/engine/transient.py)",
                "proxy_chain": [
                    "core mass -> binding energy (E = G*M^2/R)",
                    "binding energy -> released energy at the stability limit",
                    "released energy + rise/tail time -> the lightcurve's normalised shape",
                ],
                "placement": "the collapse buffer in the compact core — the engine computes one mass point at a time",
                "compression": "mass + stability limit + growth rate + lightcurve times -> (t_hold, E_ut, form)",
            },
            "episenter": "the stability limit: the point where the core releases what it has held — the analogy to the neuron's V_th, the Sun's b_crit and the rejection threshold is the form's own",
            "buffer": {
                "role": "the core is the buffer: the mass is built up and held up until the stability limit is crossed",
                "note": "ANALOGY to homo.aksjonspotensial, the Sun's magnetic buffer and the fault's stress build-up — holding->release, four domains, not identity.",
            },
            "ontology": {
                "assumes": [
                    "the binding energy scales as G*M^2/R",
                    "release happens when the mass crosses a stability limit (idealisation: the limit is a model parameter, and a real collapse also depends on rotation and composition)",
                    "the lightcurve's form is parameterised, not derived from a radiation transport model",
                ],
                "source": "the collapse-buffer picture (supernova/GRB as release of gravitational binding); Chandrasekhar-style mass limit as model parameter; the light curve's rise/tail as a shape choice; the idealizations are the engine's own",
            },
            "observer": {
                "bandwidth": "the engine sees only core mass and a mass growth — no rotation, no metallicity, no progenitor structure; the light curve sees the normalised shape, not the spectrum or a luminosity scale",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "mass is built -> the stability limit is crossed -> collapse -> transient -> the remnant is left — stellar death's cycle",
                "properties": ["t_hold", "E_ut", "lightcurve shape"],
            },
            "fractal": {
                "pattern": "holding->release: stellar death's transient, the Sun's flares, the neuron's spike, the fault's quakes — the same form, four domains (analogy)",
                "note": "one pattern, four domains.",
            },
            "coupling": {
                "local": "one core, one buffer",
                "global": "kosmos.transienter is an EVENT KIND — ALeRCE/ZTF readings of many transient classes' transitions; this engine encodes the COLLAPSE branch (stellar death: supernova/GRB), not the event stream as a whole. THE FRAMEWORK'S PLACEMENT: ANALOGOUS_TO homo.aksjonspotensial, efc.solar_flare_engine and efc.jordskjelv_engine — the form's fourth domain, not identity.",
                "empathy_note": "the star holds and holds — until it can hold no more. Like all buffers.",
            },
        }
