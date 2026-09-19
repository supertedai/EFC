"""EFC Romvaer Engine — the Kp buffer of the magnetosphere (L-038).

The Kp index (0-9) is the discharge level of the magnetosphere: the solar
wind charges the buffer (southward Bz is the charging current — magnetic
reconnection opens the gate), and the buffer discharges in geomagnetic
storms over a few days.

This is a CORRELATION MODEL (solar wind -> Kp), not physics from the
ground up — geomagnetic storm physics is a field of its own. The real
solar wind-Kp coupling is considerably more complex than the linear form
here (see e.g. the Newell coupling and other flux couplings); the linear
charging form is an IDEALISED simplification, calibrated so that
Bz=-12/v=600 gives Kp~5. The EFC contribution is the chain of the form:
the sun's flares (SolarFlareEngine) charge Earth's buffer (this engine) —
two domains, one chain (the same source, SWPC).

Idealised charging/discharging model:
    charging:   Kp_up ~ coefficient * (-Bz/10) * (v/100) for southward Bz
    discharging: Kp(t+1) = Kp(t) - discharge rate per 3 h tick
The storm levels (the NOAA scale): Kp 5 = G1, 6 = G2, 7 = G3, 8 = G4,
9 = G5.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class RomvaerEngine(EFCEngine):
    """Kp buffer engine for the magnetosphere (correlation model, idealized)."""

    REQUIRED_PARAMS = [
        "lade_koeffisient",  # Kp per (nT/10 * 100 km/s) — calibration proxy
        "utladningsrate",    # Kp per 3 h tick — the discharge of the buffer
        "storm_terskel",     # Kp — the G1 storm threshold (5)
    ]

    @property
    def name(self) -> str:
        return "romvaer"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def forventet_kp(self, params: dict, bz: float,
                     hastighet: float) -> float:
        """The charging current: southward Bz (negative) charges;
        northward shields. Kp ~ coefficient * (-Bz/10) * (v/100) for
        Bz < 0."""
        if bz >= 0:
            charging_current = 0.0
        else:
            charging_current = (params["lade_koeffisient"]
                                * (-bz / 10.0) * (hastighet / 100.0))
        # Cap at 9 — the maximum of the scale
        return float(min(9.0, charging_current))

    def utlad(self, kp: float, params: dict, tikk: int = 1) -> float:
        """The buffer discharges: Kp falls with the discharge rate per tick."""
        return float(max(0.0, kp - params["utladningsrate"] * tikk))

    def storm_niva(self, params: dict, kp: float) -> str:
        """The NOAA G scale: Kp 5=G1, 6=G2, 7=G3, 8=G4, 9=G5."""
        if kp < params["storm_terskel"]:
            return "ingen"
        levels = {5: "G1", 6: "G2", 7: "G3", 8: "G4", 9: "G5"}
        return levels.get(int(np.floor(kp)), "G5")

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given (Bz, speed) pairs (N x 2), return the expected Kp."""
        coords = np.asarray(coordinates, dtype=float)
        if coords.ndim == 1:
            coords = coords.reshape(1, -1)
        return np.array([
            self.forventet_kp(params_dict, float(row[0]), float(row[1]))
            for row in coords
        ])

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        validity = (
            "Kp buffer regime: the solar wind charges the magnetosphere "
            "(southward Bz = charging current), the buffer discharges in "
            "storms over a few days. CORRELATION MODEL (solar wind -> Kp) "
            "— NOT physics from the ground up; the real coupling is more "
            "complex (the Newell coupling et al.) and the linear charging "
            "form is an IDEALISED simplification. The NOAA G scale (Kp "
            "5=G1 ... 9=G5). The EFC contribution is the chain of the "
            "form: the sun's flares charge Earth's buffer."
        )
        law_form = ("charging: Kp ~ coefficient * (-Bz_south/10) * (v/100) "
                    "for Bz < 0; discharging: Kp(t+1) = Kp(t) - rate per "
                    "3 h tick; G levels at Kp 5-9")
        return {
            "id": "efc.romvaer_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["the NOAA G scale: 5=G1 ... 9=G5 — warning scale", "Bz=-12/v=600 -> Kp 5.04 — linear correlation — Newell caveat: the real coupling is more complex"],
            "motor": "romvaer"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["magnetfelt", "tid", "hastighet"],
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
                "name": "The magnetosphere's Kp buffer",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "expected Kp, storm level, discharge trajectory",
                "measurer": "correlation model solar wind -> Kp",
                "instrument": "RomvaerEngine (efc_inference/engine/romvaer.py)",
                "proxy_chain": [
                    "Bz, v -> charging current (correlation proxy)",
                    "Kp -> G level (the NOAA scale)",
                ],
                "placement": "the magnetosphere's buffer — one (Bz, v) point at a time",
                "compression": "solar wind state -> (Kp, G level)",
            },
            "episenter": "the storm threshold Kp=5: the point where the buffer goes from holding to release — the magnetosphere's regime shift",
            "buffer": {
                "role": "the magnetosphere is the buffer: it holds the charge from the solar wind until the storm is released",
                "note": "ANALOGY to the sun's magnetic buffer (SolarFlareEngine) — not identity: the Earth's buffer discharges gradually, the sun's is released abruptly.",
            },
            "ontology": {
                "assumes": [
                    "the correlation Bz/v -> Kp is stable in the idealised form",
                    "the G scale (NOAA) is the correct storm classification",
                ],
                "source": "space weather correlations (established practice); the NOAA G scale; the analogy labelling is the atlas's own",
            },
            "observer": {
                "bandwidth": "the engine sees only (Bz, v) — no magnetopause dynamics, no ring current",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "solar wind charges -> threshold -> storm discharges -> quiet — the magnetosphere's loop",
                "properties": ["Kp", "G level", "discharge trajectory"],
            },
            "fractal": {
                "pattern": "charge/discharge buffer with threshold: the magnetosphere, the sun's flares, the battery (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one solar wind state, one Kp",
                "global": "the sun's releases charge Earth's buffer — COUPLED_TO efc.solar_flare_engine via the SWPC chain",
                "empathy_note": "the Earth holds the Sun's wrath in its magnetic embrace — until it lets go.",
            },
        }
