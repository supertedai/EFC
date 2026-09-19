"""EnerFlytEngine — society as energy flow (L-052).

Morten's principle (f): the whole of society is an energy-flow diagram on
every axis. The SIR engine models the fraction flux of epidemiology; this
one models the ENERGY flux:

    dS/dt = P - C - L

where P = production, C = consumption, L = loss, S = the buffer (the store).

The regimes are the three states of the buffer threshold:
    abundance : P > C + L — the buffer fills
    balance   : P ~ C + L — the buffer stands still
    scarcity  : C + L > P — the buffer empties; below the threshold is
               the release regime (rationing/redistribution)

HONESTY CLAUSES (review discipline from the economy/society engines):
- This is ONE axis of society. Money, attention and trust are
  other currencies with explicit NON-conservation — they are not in
  this model, and that is said explicitly.
- The engine does NOT predict when crises arrive — it says when
  the buffer crosses the threshold in the model. Society's actual crises
  have actors, politics and norms that are not in the flow equation.
- Production and consumption are idealized scalars — real societies
  have sectors, networks and power that distribute the fluxes.

Fraction invariant: the regime is invariant under per-capita scaling —
the same flow per person gives the same regime (the scale is a choice,
not a physics change).
"""
from __future__ import annotations

import numpy as np

from efc_inference.engine.base_engine import EFCEngine


class EnerFlytEngine(EFCEngine):
    """Society's energy flow — buffer balance with three regimes."""

    REQUIRED_PARAMS = [
        "produksjon",  # P — energy/time
        "forbruk",     # C — energy/time
        "buffer",      # S0 — the initial holding
    ]

    @property
    def name(self) -> str:
        return "enerflyt"

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given (production, consumption) pairs, return dS/dt per point."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        ut = []
        for rad in koord:
            p = {**params_dict, "produksjon": float(rad[0]),
                 "forbruk": float(rad[1])}
            ut.append(self.vurder(p)["dS_dt"])
        return np.array(ut)

    def vurder(self, params: dict) -> dict:
        """Returns the flow assessment for the given parameters.

        A buffer below the threshold with negative drift gives
        buffer_etter = NaN (not silent clamping — the pattern from
        OekonomiEngine).
        """
        p = float(params["produksjon"])
        c = float(params["forbruk"])
        tap = float(params.get("tap", 0.0))
        s = float(params["buffer"])
        terskel = float(params.get("terskel", 0.0))

        drift = p - c - tap
        if drift == 0.0:
            regime = "balance"
        elif drift > 0.0:
            regime = "abundance"
        else:
            regime = "scarcity"

        buffer_etter = s + drift
        if s == 0.0 and drift < 0.0:
            buffer_etter = float("nan")

        return {
            "regime": regime,
            "dS_dt": drift,
            "buffer_etter": buffer_etter,
            "under_terskel": buffer_etter < terskel,
        }

    def regime_node(self, params: dict) -> dict:
        u = self.vurder(params)
        return {
            "id": "efc.enerflyt_engine",
            "synlighet": self.SYNLIGHET,
            "regime": {
                "name": u["regime"],
                "validity": ("abundance: P > C + L — the buffer fills; "
                             "balance: P ~ C + L; scarcity: C + L > P — "
                             "the buffer empties and the release regime "
                             "is rationing/redistribution. Does NOT "
                             "predict when the crisis arrives — only "
                             "where the buffer crosses the threshold in "
                             "the model."),
            },
            "phase": u["regime"],
            "measure": {
                "target": "the buffer S and the drift dS/dt = P - C - L",
                "measurer": "energy statistics — production, consumption, "
                            "stores (national accounts)",
                "instrument": "statistics agencies and grid operators",
                "proxy_chain": ["registered production -> consumption -> "
                                "buffer estimate — all are accounting "
                                "proxies, not direct measurements"],
                "placement": "society's own accounts",
                "compression": "the whole of society is compressed into "
                               "three numbers per unit of time",
            },
            "episenter": ("the energy-accounting frame: scarcity is a "
                          "reading in the P-C-L frame, not a property "
                          "of society in itself"),
            "buffer": {
                "role": "S is society's energy buffer — the holding that "
                        "absorbs the imbalance between production and "
                        "consumption",
                "note": "the same buffer logic as the battery and "
                        "homeostasis — at societal scale",
            },
            "ontology": {
                "assumes": [
                    "energy is ONE axis of society — money, "
                    "attention and trust are other currencies with "
                    "explicit NON-conservation and are not in the model",
                    "production and consumption are idealized scalars — "
                    "real societies have sectors, networks and power",
                    "dS/dt = P - C - L is an idealised "
                    "flow equation, not a social law",
                ],
                "source": "the conservation of the energy budget; EFC "
                          "buffer logic (analogy to battery and "
                          "homeostasis — not identity)",
            },
            "observer": {
                "bandwidth": "society's own accounting — only what is "
                             "registered and reported; the black "
                             "economy and unregistered fluxes are "
                             "invisible to this instrument",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "production -> buffer -> consumption -> "
                        "production incentives — the loop keeps "
                        "society's energy system going",
                "properties": ["abundance", "balance", "scarcity"],
            },
            "fractal": {
                "pattern": "cell -> body -> household -> society: the "
                           "same buffer balance at every scale",
                "note": "homeostasis is the biological version of the "
                        "same flow logic",
            },
            "coupling": {
                "local": "every household balances locally",
                "global": "society's energy buffer is the collective — "
                          "scarcity couples everyone",
                "empathy_note": "the scarcity does not strike equally — "
                                "the model has no distribution, and "
                                "that is a deliberate gap",
            },
            "perspektiv": "paradigme",
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, "
                                    "not by the field",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["energi", "tid", "fraksjon"],
                "enheter": "energy/time, per-capita fractions",
                "status": "proxy",
                "alternativer": ["money, attention, trust — "
                                 "non-conserved currencies outside "
                                 "the model"],
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the ladder its node belongs. The field must
            # nonetheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 1,
                "forelder": "homo.fluxus",
                "tidsskala": "motor time",
                "lengdeskala": "domain"
            },            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": [("the threshold is the buffer boundary WE "
                              "set — scarcity is our definition, not "
                              "nature's line")],
                "motor": "enerflyt",
            },
            "analogi": {
                "avbildning": ("buffer -> battery storage/homeostasis, "
                               "scarcity -> discharge/fever, "
                               "production -> charging/intake"),
                "bryter_der": ("society is not an organism: "
                               "no central regulator, the distribution "
                               "is political, and the actors have "
                               "intentions — the flow equation has "
                               "none of them"),
            },
        }
