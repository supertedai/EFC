"""EFC Samfunn Engine — SIR epidemiology as a flow model (L-042).

The SIR model is the flow model in pure form: susceptible (S) -> infected
(I) -> recovered (R), with R0 = beta/gamma as the threshold — R0 > 1 is
OUTBREAK (release: the reservoir of susceptibles is emptied), R0 < 1 is
DAMPED (holding: the infection finds no susceptibles), and R0 = 1 is the
THRESHOLD itself (the regime shift).

The model is an IDEALIZED homogeneous SIR: no age structure, no network
topology, no behavior, no vaccination strategies. It is NOT an
epidemiological model competitor — epidemiology is a field of its own with
its own literature; the engine codes only the form.

The physics (homogeneous SIR):
    dS/dt = -beta S I / N
    dI/dt =  beta S I / N - gamma I
    dR/dt =  gamma I
    R0 = beta / gamma
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class SamfunnEngine(EFCEngine):
    """Homogeneous SIR flow model with an R0 threshold (idealized)."""

    REQUIRED_PARAMS = [
        "beta",   # 1/day — infection rate
        "gamma",  # 1/day — recovery rate
        "N",      # population size
    ]

    @property
    def name(self) -> str:
        return "samfunn"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def r0(self, params: dict) -> float:
        """R0 = beta / gamma — the basic reproduction number."""
        if params["gamma"] == 0:
            return float("inf")
        return float(params["beta"] / params["gamma"])

    def utbrudds_status(self, params: dict) -> str:
        """Regime classification at the threshold R0 = 1."""
        r0 = self.r0(params)
        if r0 > 1:
            return "utbrudd"
        if r0 < 1:
            return "dempet"
        return "terskel"

    def sir_bane(self, params: dict, t: np.ndarray,
                 s0: float = 0.999, i0: float = 0.001):
        """The SIR trajectory as FRACTIONS of N (s + i + r = 1 at all
        times; the population counts are S = N*s, I = N*i, R = N*r).

        Integrated with Euler on a fine grid — sufficient for the
        qualitative trajectory of the form (this is a form model, not a
        precision integrator; the docstring's honesty says so)."""
        s, i = s0, i0
        s_track, i_track, r_track = [s], [i], [1 - s - i]
        dt = float(np.mean(np.diff(np.asarray(t, dtype=float))))
        for _ in range(len(np.atleast_1d(t)) - 1):
            ds = -params["beta"] * s * i
            di = params["beta"] * s * i - params["gamma"] * i
            s = max(0.0, s + ds * dt)
            i = max(0.0, i + di * dt)
            r = 1.0 - s - i
            s_track.append(s)
            i_track.append(i)
            r_track.append(r)
        return (np.array(s_track), np.array(i_track), np.array(r_track))

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given (beta, gamma) pairs (N x 2), return R0 per point."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        coords = np.asarray(coordinates, dtype=float)
        if coords.ndim == 1:
            coords = coords.reshape(1, -1)
        out = []
        for row in coords:
            p = {**params_dict, "beta": float(row[0]),
                 "gamma": float(row[1])}
            out.append(self.r0(p))
        return np.array(out)

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        r0 = self.r0(params)
        validity = (
            "SIR flow regime: susceptible -> infected -> recovered with "
            f"R0 = {r0:.2f} — the threshold R0 = 1 is the regime shift: "
            "above it is the outbreak (release, the reservoir empties), "
            "below it the infection is damped (holding). IDEALIZED "
            "homogeneous SIR: no age structure, no network, no behavior, "
            "no vaccination — NOT an epidemiological model competitor. "
            "The trajectory is integrated with Euler on a fine grid — a "
            "form model, not a precision integrator."
        )
        law_form = ("dS/dt = -beta S I/N; dI/dt = beta S I/N - gamma I; "
                    "dR/dt = gamma I; R0 = beta/gamma")
        return {
            "id": "efc.samfunn_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["R0 = 1 — the threshold between three regimes — regime breaker"],
            "motor": "samfunn"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, not by the field; the narrative is our own, and it is a strength to know it",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["tid", "fraksjon"],
                "enheter": "engine-specific (SI)",
                "status": "avledet",
                "alternativer": ["coordinate-free formulations"]
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": "homo.fluxus",
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "SIR epidemiology — flow with threshold",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "R0, outbreak status, the epidemic trajectory",
                "measurer": "homogeneous SIR integration",
                "instrument": "SamfunnEngine (efc_inference/engine/samfunn.py)",
                "proxy_chain": [
                    "beta, gamma -> R0",
                    "R0 -> outbreak status (threshold 1)",
                    "the SIR trajectory -> the shape of the curve",
                ],
                "placement": "one (beta, gamma) point at a time in the homogeneous regime",
                "compression": "(beta, gamma) -> (R0, status, trajectory)",
            },
            "episenter": "the threshold R0 = 1: the point where an infection dies out or takes off — the epidemic's regime shift",
            "buffer": {
                "role": "the reservoir of susceptibles is the buffer: the outbreak drains it, and when it is empty, the epidemic dies out on its own",
                "note": "ANALOGY to immunology's threshold-governed defence (homo.immunologi) — not identity: SIR is population flow, the immune response is bodily defence.",
            },
            "ontology": {
                "assumes": [
                    "homogeneous mixture (all meet all alike)",
                    "constant beta and gamma in the window",
                ],
                "source": "Kermack-McKendrick SIR (1927); the analogy marking is the atlas's own",
            },
            "observer": {
                "bandwidth": "the engine sees only the aggregates S, I, R — no individuals, no network",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "infection -> outbreak -> the reservoir empties -> herd immunity -> the infection dies — the epidemic's loop",
                "properties": ["R0", "peak", "final size"],
            },
            "fractal": {
                "pattern": "flow through a limited reservoir with a threshold: epidemic, discharge, collapse (analogy)",
                "note": "one pattern, three domains.",
            },
            "coupling": {
                "local": "one society, one epidemic",
                "global": "the health domain is the collective scale of homo.fluxus — ANALOGOUS_TO homo.immunologi",
                "empathy_note": "the epidemic does not know it is a flow — it just runs until the reservoir is empty.",
            },
        }
