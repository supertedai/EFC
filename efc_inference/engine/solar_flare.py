"""EFC Solar Flare Engine — the Sun's holding->release engine (L-026).

Encodes the form found in the recon of kosmos.sol (GOES X-ray flux,
DONKI eruption catalogue): the Sun's magnetic field is a buffer that
CHARGES slowly (footpoint motions twist the field) and is TRIGGERED
suddenly when the field exceeds a critical strength — flare/CME.

The model is IDEALISED (Avallon-style energy buffer): magnetic energy
B^2/(2 mu_0) * V is built up with a charging rate dB/dt, and the whole
buffer is released when B reaches b_crit. It does NOT claim predictive
power for single events — it computes the form's observables: charging
time, released energy and the expected GOES class.

The GOES classification follows the canonical scale (peak X-ray flux in
the 1-8 Angstrom band): A < 1e-7, B < 1e-6, C < 1e-5, M < 1e-4,
X >= 1e-4 W/m^2. The engine maps released energy to class via a simple
energy-to-flux proxy — marked as proxy, not identity.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

# GOES classes in ascending order (canonical scale)
GOES_CLASSES = "ABCMX"


class SolarFlareEngine(EFCEngine):
    """Holding->release engine for the Sun's magnetic buffer (idealised)."""

    REQUIRED_PARAMS = [
        "mu_0",            # N/A^2 — vacuum permeability
        "b_crit",          # T — critical field strength for release
        "oppladningsrate", # T/s — dB/dt in the active region
        "volum",           # m^3 — active region volume
    ]

    @property
    def name(self) -> str:
        return "solar_flare"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def _valid_field(self, b: np.ndarray) -> np.ndarray:
        """The engine's fail-closed contract for field strength — ONE source.

        Valid field strength is FINITE and NON-NEGATIVE: the buffer charges
        from B = 0 and upwards, so negative B is outside the model's state
        space. Separated out because both compute() and magnetisk_energi()
        must keep the SAME contract — two copies drift apart. The same form
        as TransientEngine._valid_mass() (L-036), and for the same reason:
        the square makes the input positive.
        """
        return np.isfinite(b) & (b >= 0.0)

    def magnetisk_energi(self, params: dict, b: np.ndarray) -> np.ndarray:
        """Magnetic buffer energy E = B^2 / (2 mu_0) * V.

        Invalid input (negative or non-finite B) is outside the window
        and yields NaN — never a guess. Without the mask, B^2 would have
        made the energy POSITIVE also for negative B, so a direct caller
        got a number where compute() answers «outside the window».
        """
        b = np.asarray(b, dtype=float)
        out = np.full(b.shape, np.nan)
        valid = self._valid_field(b)
        out[valid] = (b[valid] ** 2 / (2 * params["mu_0"])) * params["volum"]
        return out

    def oppladningstid(self, params: dict) -> float:
        """Time from B=0 to the threshold at constant charging rate."""
        return float(params["b_crit"] / params["oppladningsrate"])

    def utlost_energi(self, params: dict) -> float:
        """The energy released when the buffer reaches the threshold."""
        return float(self.magnetisk_energi(params, np.array([params["b_crit"]]))[0])

    def goes_klasse(self, energy: float) -> str:
        """Maps released energy to expected GOES class (proxy).

        Proxy chain: energy -> peak flux (1-8 A) -> class.
        Calibration anchor: 1e22 J ~ M class. Bins per decade:
            A < 1e20, B < 1e21, C < 1e22, M < 1e23, X >= 1e23 J.
        (1e22 J is the typical released energy for M class flares.)
        Idealised: real flares release only a FRACTION of the buffer.
        """
        energy_per_class = {
            "A": 1e20,   # A: energy < 1e20 J
            "B": 1e21,
            "C": 1e22,
            "M": 1e23,   # M: 1e22 <= energy < 1e23 (the anchor 1e22 -> M)
            "X": float("inf"),
        }
        cls = "X"
        for k in GOES_CLASSES:
            if energy < energy_per_class[k]:
                cls = k
                break
        return cls

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Given field strengths B (T), return released energy (J).

        Holding: B < b_crit -> the buffer holds, release = 0.
        Release: B >= b_crit -> the buffer is released (idealised: entirely).

        Invalid input (negative or non-finite B) is outside the window
        and yields NaN — never a guess. Previously NaN and -inf were
        reported as «holding» (0.0) and +inf as a release.
        """
        b = np.asarray(coordinates, dtype=float)
        out = np.full(b.shape, np.nan)
        valid = self._valid_field(b)
        out[valid] = 0.0
        critical = valid & (b >= params_dict["b_crit"])
        out[critical] = self.magnetisk_energi(params_dict, b[critical])
        return out

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        b_crit = params["b_crit"]
        rate = params["oppladningsrate"]
        t_opp = self.oppladningstid(params)
        e_ut = self.utlost_energi(params)
        validity = (
            "holding: B < " + str(b_crit) + " T — the buffer charges, no "
            "release; release: B >= " + str(b_crit) + " T — the buffer "
            "is released. IDEALIZED regime model (Avallon-style buffer): "
            "the whole buffer is released at the threshold; real flares "
            "release a fraction. Invalid input (negative or non-finite B) "
            "is outside the window and yields NaN — never a guess: the "
            "buffer is charged from B = 0, and B^2 would otherwise have "
            "made the energy positive also for negative B. Does NOT "
            "predict single events."
        )
        law_form = ("E = B^2/(2 mu_0) * V; charging time = b_crit / "
                    "(dB/dt); trigger at B = b_crit")
        return {
            "id": "efc.solar_flare_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["GOES bins: 1e20->B, 1e21->C, 1e22->M, 1e23->X J — class boundaries — proxy chain, not a physical law"],
            "motor": "solar_flare"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "The GOES scale and the storm watch are carried by NOAA/SWPC, who would lose from a wrong warning; our buffer model is idealized and has no carrier in solar physics — only we have something to defend.",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["energi", "tid"],
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
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "The Sun's holding->release (magnetic buffer)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "charging time, released energy, GOES class",
                "measurer": "analytic buffer model + GOES class proxy",
                "instrument": "SolarFlareEngine (efc_inference/engine/solar_flare.py)",
                "proxy_chain": [
                    "B -> magnetic energy (E = B^2/(2 mu_0) * V)",
                    "energy -> GOES class (calibration proxy: 1e22 J ~ M)",
                ],
                "placement": "the magnetic buffer of the active region — the engine computes one field-strength point at a time",
                "compression": "field strength + charging rate -> (t_opp, E_ut, class)",
            },
            "episenter": "the threshold b_crit: the point where the buffer releases what it has held — the analogy to the neuron's V_th and the fault's threshold is the form's own",
            "buffer": {
                "role": "the magnetic field is the buffer: the energy is charged and held until the threshold is crossed",
                "note": "ANALOGY to homo.aksjonspotensial and the earthquake's fault — holding->release, three domains, not identity.",
            },
            "ontology": {
                "assumes": [
                    "the magnetic energy density B^2/(2 mu_0) applies",
                    "release happens at a critical field strength (idealisation: real release also depends on topology)",
                ],
                "source": "the energy-buffer picture of solar physics (Avallon style); the GOES class scale (1-8 A); the idealizations are the engine's own",
            },
            "observer": {
                "bandwidth": "the engine sees only field strength and charging rate — no magnetic topology, no plasma dynamics",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "footpoint motions -> the field twists -> threshold -> release -> the field is rebuilt — the flare cycle",
                "properties": ["t_opp", "E_ut", "GOES class"],
            },
            "fractal": {
                "pattern": "holding->release: the Sun's flares, the neuron's spike, the fault's quakes — the same form, three domains (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one active region, one buffer",
                "global": "flares are the regime shift of kosmos.sol — ANALOGOUS_TO homo.aksjonspotensial and efc.jordskjelv_engine",
                "empathy_note": "the sun holds and holds — until it lets go. Like all buffers.",
            },
        }


class SolarFlareEngineBrakdel(SolarFlareEngine):
    """Variant that releases a fraction of the buffer (more realistic)."""

    @property
    def name(self) -> str:
        return "solar_flare_brakdel"
