"""EFC Oekonomi Engine — Minsky's financial regimes (L-041).

Minsky's financial instability hypothesis is the holding->release form
in finance: stability breeds confidence, confidence breeds debt, and the
debt drives the system through three regimes — hedge (income covers debt
and interest), speculative (income covers the interest, the debt must be
rolled) and Ponzi (income covers neither — assets must be
sold). Crisis is the release: the stable years ARE the holding that
built the buffer.

The model is an IDEALISED regime classification with a linear
leverage drift in stable periods (the Minsky moment:
«stability is destabilising»). It is NOT an economic
model competitor — economics is a discipline of its own with its own
literature; the engine only codes the form.

The regimes (leverage ratio = debt / annual income):
    hedge:      income covers interest + repayment
    spekulativ: income covers the interest, the debt is rolled
    ponzi:      income covers neither
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

REGIME_CODES = {"hedge": 0, "spekulativ": 1, "ponzi": 2}


class OekonomiEngine(EFCEngine):
    """Minsky's financial regimes with leverage thresholds (idealised)."""

    REQUIRED_PARAMS = [
        "rente",              # 1/year — the interest rate
        "inntektsavkastning",  # 1/year — the return on the income
        "gjeldsgrad_hedge",    # threshold: hedge -> spekulativ
        "gjeldsgrad_ponzi",    # threshold: spekulativ -> ponzi
    ]

    @property
    def name(self) -> str:
        return "oekonomi"

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def regime(self, params: dict, gjeldsgrad: float) -> str:
        """Classifies the financial regime from the leverage ratio."""
        if gjeldsgrad < params["gjeldsgrad_hedge"]:
            return "hedge"
        if gjeldsgrad < params["gjeldsgrad_ponzi"]:
            return "spekulativ"
        return "ponzi"

    def gjeldsgrad_drift(self, params: dict, gjeldsgrad: float,
                         stabile_aar: float) -> float:
        """The Minsky moment: in stable periods the debt grows faster
        than the income — the leverage ratio drifts upward with (interest -
        income return + confidence term). Idealised linear drift."""
        # Idealised: the debt grows with the interest rate, the income with
        # the return; under stability the credit conditions loosen and
        # the drift is amplified (the confidence term, fixed idealised 0.06/year
        # — larger than the interest-minus-return gap so that
        # the Minsky moment is positive, as the hypothesis requires).
        confidence_term = 0.06
        drift_rate = (params["rente"] - params["inntektsavkastning"]
                      + confidence_term)
        if drift_rate <= 0:
            # The model assumes positive drift; without it the
            # Minsky moment is undefined — an honest NaN, not silent
            # clipping to standstill.
            return float("nan")
        return float(gjeldsgrad * (1.0 + drift_rate * stabile_aar))

    # ------------------------------------------------------------------
    # The EFCEngine contract
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given leverage ratios, return regime codes (0=hedge,
        1=spekulativ, 2=ponzi)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        gg = np.asarray(coordinates, dtype=float)
        return np.array([REGIME_CODES[self.regime(params_dict, float(g))]
                         for g in gg])

    # ------------------------------------------------------------------
    # Self-description
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        validity = (
            "Minsky's financial regimes: stability breeds confidence -> debt "
            "grows -> hedge -> speculative -> ponzi -> crisis. The "
            "stable years ARE the holding that builds the buffer for "
            "the trigger (the Minsky moment: stability is "
            "destabilising — here as measurable leverage drift). "
            "DELIMITATION: Minsky is ONE tradition among several in "
            "economics; the model does NOT predict the timing or occurrence "
            "of crises — only the qualitative form of the regime. "
            "IDEALISED regime classification with linear drift — "
            "NOT an economic model competitor: no sectors, "
            "no central bank, no policy, no heterogeneous "
            "actors."
        )
        law_form = ("hedge: income covers interest + repayment; "
                    "speculative: income covers the interest, the debt is rolled; "
                    "ponzi: income covers neither — assets "
                    "are sold. Leverage drift: gg(t+1) = gg(t) * "
                    "(1 + (r - g + confidence) * dt)")
        return {
            "id": "efc.oekonomi_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["drift_rate <= 0 -> NaN (not silent clipping) — honesty boundary", "the hedge/speculative/ponzi boundaries — the Minsky typology — one tradition among several"],
            "motor": "oekonomi"},
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
            # the engine cannot know where in the staircase its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": "homo.fluxus",
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "regime": {
                "name": "Minsky's financial regimes — stability as holding",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "financial regime (hedge/speculative/ponzi), leverage drift",
                "measurer": "threshold classification + linear drift",
                "instrument": "OekonomiEngine (efc_inference/engine/oekonomi.py)",
                "proxy_chain": [
                    "leverage ratio -> regime (two thresholds)",
                    "stable years -> leverage drift (the Minsky moment)",
                ],
                "placement": "one leverage point at a time in the idealised regime",
                "compression": "(leverage ratio, stability duration) -> (regime, drift)",
            },
            "episenter": "the Ponzi threshold: the point where the system can no longer roll — finance's regime shift from holding to release",
            "buffer": {
                "role": "the stable years are the buffer: trust builds up and the debt accumulates — until the buffer is full and the crisis is triggered",
                "note": "ANALOGY to the homeostasis buffer's saturation (homo.homeostase_buffer) — not identity: the financial system has no setpoint mechanism, only thresholds.",
            },
            "ontology": {
                "assumes": [
                    "Minsky's three regimes describe the qualitative states of finance",
                    "the leverage drift is linear and the confidence term constant (idealization)",
                ],
                "source": "Hyman Minsky, Financial Instability Hypothesis (the 1970s-80s); the analogy labelling is the atlas's own",
            },
            "observer": {
                "bandwidth": "the engine sees only debt ratio and interest rates — no sector balances, no currency dynamics",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "stability -> confidence -> debt -> speculation -> ponzi -> crisis -> new stability — the Minsky cycle",
                "properties": ["regime", "leverage ratio", "drift"],
            },
            "fractal": {
                "pattern": "stability that builds its own release: finance, fault, the sun's flares (analogy)",
                "note": "one pattern, three domains — the buffer is charged by the stable itself.",
            },
            "coupling": {
                "local": "one system, one leverage ratio",
                "global": "the economy is the collective scale of homo.fluxus — ANALOGOUS_TO homo.homeostase_buffer",
                "empathy_note": "the market does not know that the stability is temporary — it just keeps building.",
            },
        }
