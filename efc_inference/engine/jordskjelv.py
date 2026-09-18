"""EFC Jordskjelv Engine — the Earth's holding->release engine (L-028).

Codes the form that was found in the reconnaissance of kosmos.jord
(the USGS catalogue): the fault is a buffer that is CHARGED slowly (the
plates move) and RELEASED suddenly when the stress exceeds the friction
threshold — elastic rebound.

The model is IDEALIZED (Burridge-Knopoff-style charging): the stress
accumulates at a charge rate, and is released at the threshold with a
stress drop. The observables are recurrence time, seismic moment and
moment magnitude (the Gutenberg-Richter framework). It does NOT CLAIM
predictive power for single earthquakes — it computes the observables of
the form.

Moment magnitude: Mw = (2/3)(log10 M0 - 9.1), M0 = mu * A * D with the
slip D = stress drop / mu (Kanamori).
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class JordskjelvEngine(EFCEngine):
    """Holding->release engine for the fault's stress buffer (idealized)."""

    REQUIRED_PARAMS = [
        "skjaermodul",   # Pa — mu, the shear modulus of the crust
        "lade_rate",     # Pa/year — stress accumulation
        "terskel",       # Pa — the stress drop at release
        "areal",         # m^2 — rupture area
    ]

    @property
    def name(self) -> str:
        return "jordskjelv"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def _gyldig_spenning(self, spenning: np.ndarray) -> np.ndarray:
        """The engine's fail-closed contract for stress — ONE source.

        Valid stress is FINITE and NON-NEGATIVE: the buffer charges from
        stress = 0 and upwards, so negative stress is outside the
        model's state space. Split out because the contract must have
        one place, not one per call. Same form as
        TransientEngine._gyldig_masse() (L-036).
        """
        return np.isfinite(spenning) & (spenning >= 0.0)

    def gjentakelsestid(self, params: dict) -> float:
        """Time between releases at a constant charge rate (idealized)."""
        return float(params["terskel"] / params["lade_rate"])

    def seismisk_moment(self, params: dict) -> float:
        """M0 = mu * A * D, with the slip D = threshold / mu (Kanamori)."""
        d = params["terskel"] / params["skjaermodul"]
        return float(params["skjaermodul"] * params["areal"] * d)

    def magnitude(self, params: dict) -> float:
        """Moment magnitude Mw = (2/3)(log10 M0 - 9.1)."""
        m0 = self.seismisk_moment(params)
        if m0 <= 0:
            return float("nan")
        return float((2 / 3) * (np.log10(m0) - 9.1))

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Given stress (Pa), return the released moment (N*m).

        Holding: stress < threshold -> the buffer holds, release = 0.
        Release: stress >= threshold -> the moment is released
        (idealized: M0 is computed with the DECLARED stress drop, not
        the local one).

        Invalid input (negative or non-finite stress) is outside the
        window and gives NaN — never a guess. Previously NaN, -1 and
        -inf were reported as «holding» (0.0) and +inf as a release.
        """
        spenning = np.asarray(coordinates, dtype=float)
        ut = np.full(spenning.shape, np.nan)
        gyldig = self._gyldig_spenning(spenning)
        ut[gyldig] = 0.0
        kritisk = gyldig & (spenning >= params_dict["terskel"])
        ut[kritisk] = self.seismisk_moment(params_dict)
        return ut

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        terskel = params["terskel"]
        t_rep = self.gjentakelsestid(params)
        mw = self.magnitude(params)
        validity = (
            "holding: stress < " + str(terskel) + " Pa — the fault "
            "charges, no release; release: stress >= " + str(terskel)
            + " Pa — the buffer is released. IDEALIZED regime model "
            "(Burridge-Knopoff-style charging): the release happens at "
            "a fixed threshold and the whole stress drop is released. "
            "Invalid input (negative or non-finite stress) is outside "
            "the window and gives NaN — never a guess: the buffer "
            "charges from stress = 0. Does NOT predict single "
            "earthquakes."
        )
        law_form = ("gjentakelsestid = terskel / lade_rate; "
                    "M0 = mu * A * (terskel/mu); "
                    "Mw = (2/3)(log10 M0 - 9.1)")
        return {
            "id": "efc.jordskjelv_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the elastic-rebound assumption — idealized model — model boundary, not predictor"],
            "motor": "jordskjelv"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["energi", "rom", "tid"],
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
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "The Earth's holding->release (fault buffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "recurrence time, seismic moment, moment magnitude",
                "measurer": "analytic elastic-rebound model",
                "instrument": "JordskjelvEngine (efc_inference/engine/jordskjelv.py)",
                "proxy_chain": [
                    "charge rate -> recurrence time",
                    "stress drop -> slip -> M0 -> Mw (Kanamori)",
                ],
                "placement": "the fault's stress buffer — the engine computes one stress point at a time",
                "compression": "charge rate + threshold + area -> (t_rep, M0, Mw)",
            },
            "episenter": "the threshold: the point where the fault releases what it has held — the analogy to the neuron's V_th and the sun's b_crit is the form's own",
            "buffer": {
                "role": "the fault is the buffer: the stress charges and is held until the threshold is crossed",
                "note": "ANALOGY to homo.aksjonspotensial and the Sun's magnetic buffer — holding->release, three domains, not identity.",
            },
            "ontology": {
                "assumes": [
                    "elastic rebound applies: the stress accumulates elastically and is released abruptly",
                    "triggering occurs at a fixed threshold (idealization: real friction is velocity- and state-dependent)",
                ],
                "source": "elastic rebound (Reid), Burridge-Knopoff-tradisjonen, Kanamoris Mw; idealiseringene er motorens egne",
            },
            "observer": {
                "bandwidth": "the engine sees only voltage and charge rate — no friction law, no pore pressure",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "plate drift -> stress builds -> threshold -> release -> stress builds again — the earthquake cycle",
                "properties": ["t_rep", "M0", "Mw"],
            },
            "fractal": {
                "pattern": "holding->release: the fault's earthquake, the sun's flares, the neuron's spike — the same form, three domains (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one fault, one buffer",
                "global": "quake is kosmos.jord's regime shift — ANALOGOUS_TO homo.aksjonspotensial and efc.solar_flare_engine",
                "empathy_note": "the Earth holds and holds — until it slips. Like all buffers.",
            },
        }
