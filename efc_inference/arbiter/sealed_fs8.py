"""The sealed fσ8 arbiter (step 12).

The machine judge against EFC's sealed prediction P2:

    fσ8(z=0.7) = 0.430 (EFC)  vs  0.449 (ΛCDM)

Sealed 2026-04-14 under DOI 10.6084/m9.figshare.32013156
(«Sealed Blind Predictions for Growth-Rate Observables: EFC vs ΛCDM»),
and lying as a message on the bus (subject
kosmos.kosmologi.tilstand.efc-fs8, seq 5817, source efc-sealed-baseline).

Important distinction — SEALED ANCHOR vs ENGINE PREDICTION:
- 0.430 is the BLIND anchor that was sealed 2026-04-14. The verdict is
  always passed against the anchor — the criterion cannot be changed after
  the sealing.
- In addition the arbiter computes an EXPLICIT engine prediction from the
  given parameters (the growth engine). The distance measurement↔engine
  prediction is reported separately, so that the deviation between the engine
  layer and the anchor becomes VISIBLE — never hidden.

The verdict logic is three-valued and every verdict carries the rule that
passed it, with source. The arbiter NEVER passes a verdict on data it does
not have.

Honesty clause: the sealed prediction rests on μ<1 (the B channel in the
perturbation layer, «linear growth with entropy damping»). The engine layer's
growth API (efc_inference.engine.growth) has mu=1 hardcoded as of today —
only the background channel (alpha_cosmo) is included. The arbiter reports
this openly and does not claim that 0.430 is reproduced by machine.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from efc_inference.engine.growth import EFCGrowth

SEALED_DOI = "10.6084/m9.figshare.32013156"
SEALED_DATE = "2026-04-14"
ARBITER_INSTRUMENT = "DESI DR2 full-shape RSD (galaxy-RSD, z~0.7)"
ANCHOR_EFC = 0.430
ANCHOR_LCDM = 0.449
# The instrument requires galaxy-RSD tracers (LRG/ELG); Lyα is a different
# tracer and cannot pass the verdict. The z window is the test's regime: z~0.7.
ALLOWED_TRACERS = ("LRG", "ELG")
Z_MIN, Z_MAX = 0.5, 0.9
# Floating-point rounding makes «exactly 1σ/2σ/3σ» values land a hair's
# breadth on the wrong side of the limit (2.0 becomes 1.999999999999999).
# The «~1σ» formulation is not exact anyway, so the limits use an epsilon.
EPS = 1e-9


class SealedFs8Arbiter:
    """Judges against the sealed fσ8(z=0.7) prediction."""

    def __init__(self, growth: Optional[EFCGrowth] = None):
        self.growth = growth or EFCGrowth()

    # ------------------------------------------------------------------
    # The criterion (sealed) — rendering, source-referenced
    # ------------------------------------------------------------------
    @staticmethod
    def kriterium() -> dict:
        return {
            "anker_efc": ANCHOR_EFC,
            "anker_lcdm": ANCHOR_LCDM,
            "arbiter_instrument": ARBITER_INSTRUMENT,
            "tillatte_tracere": list(ALLOWED_TRACERS),
            "z_vindu": [Z_MIN, Z_MAX],
            "forseglet_dato": SEALED_DATE,
            "forseglet_doi": SEALED_DOI,
            "bekreftelse": ("DESI DR2 full-shape fsigma8(z~0.7) shall lie "
                            "within ~1σ of 0.430"),
            "falsifikasjon_a": ("Measured fσ8(z=0.7) > 0.449 at more than 3σ — "
                                "consistent with ΛCDM at high significance "
                                "(P2 damage-test)"),
            "falsifikasjon_b": ("Falsified if the measurement is consistent "
                                "with 0.449 (ΛCDM) within less than 1σ "
                                "or excludes 0.430 at at least 2σ "
                                "(P1, falsifiable_by)"),
        }

    # ------------------------------------------------------------------
    # The predictions — parameter-derived from the engine, not hardcoded
    # ------------------------------------------------------------------
    def nullmodell(self, params: Optional[dict] = None) -> float:
        """The ΛCDM null model: alpha_cosmo=0."""
        p = dict(params or {})
        p.setdefault("Omega_m", 0.3)
        p.setdefault("H0", 70.0)
        p.setdefault("sigma8", 0.8)
        p["alpha_cosmo"] = 0.0
        return float(self.growth.compute(p, np.array([0.7]))[0])

    def prediksjon_efc(self, params: dict) -> float:
        """The EFC engine prediction from the given parameters."""
        return float(self.growth.compute(params, np.array([0.7]))[0])

    # ------------------------------------------------------------------
    # The verdict
    # ------------------------------------------------------------------
    def vurder(self, measurement: Optional[dict],
               params: Optional[dict] = None) -> dict:
        """Three-valued verdict: PASS / FAIL / VENTER.

        measurement: dict with fsigma8, sigma, z_eff, tracer, kilde — or
        None (the arbiter measurement does not exist yet).
        params: engine parameters for the EXPLICIT engine prediction.
        """
        if measurement is None:
            return {
                "status": "VENTER",
                "årsak": ("The arbiter measurement is missing: DESI DR2 "
                          "full-shape galaxy-RSD fσ8(z~0.7) is not available. "
                          "The published DR2 Lyα full-shape measurement "
                          "(2026-07-30) is a different tracer and cannot "
                          "pass this verdict."),
                "regel": "none — no basis",
                "kilde": "bus subject kosmos.kosmologi.tilstand.efc-fs8 "
                         "(arbiter: no, waiting_on: DESI DR2 full-shape)",
            }

        # --- validation of the measurement ----------------------------
        for field in ("fsigma8", "sigma", "z_eff", "tracer", "kilde"):
            if field not in measurement or measurement[field] is None:
                return {
                    "status": "VENTER",
                    "årsak": f"the measurement is missing the field «{field}» — "
                             "invalid basis, verdict not passed.",
                    "regel": "none — invalid measurement",
                    "kilde": "the arbiter's own validation",
                }
        if not np.isfinite(measurement["sigma"]) or measurement["sigma"] <= 0:
            return {
                "status": "VENTER",
                "årsak": (f"sigma={measurement['sigma']} is not a positive, "
                          "finite number — invalid basis, verdict not "
                          "passed."),
                "regel": "none — invalid measurement",
                "kilde": "the arbiter's own validation",
            }
        if measurement["tracer"].upper() not in ALLOWED_TRACERS:
            return {
                "status": "VENTER",
                "årsak": (f"Tracer {measurement['tracer']} is not galaxy-"
                          f"RSD ({'/'.join(ALLOWED_TRACERS)}). Lyα is a "
                          "different tracer and cannot pass this verdict."),
                "regel": "none — wrong instrument",
                "kilde": ARBITER_INSTRUMENT,
            }
        if not (Z_MIN <= measurement["z_eff"] <= Z_MAX):
            return {
                "status": "VENTER",
                "årsak": (f"z_eff={measurement['z_eff']} lies outside the test's "
                          f"z window [{Z_MIN}, {Z_MAX}] — the measurement "
                          "is not the criterion's measurement."),
                "regel": "none — wrong z window",
                "kilde": "the criterion applies to z~0.7",
            }

        m = measurement["fsigma8"]
        s = measurement["sigma"]
        diff_efc = abs(m - ANCHOR_EFC) / s
        diff_lcdm = abs(m - ANCHOR_LCDM) / s

        # --- explicit engine prediction (separate from the anchor) -----
        engine_prediction = None
        if params is not None:
            engine_prediction = self.prediksjon_efc(params)

        details = {
            "avstand_anker_efc_sigma": round(diff_efc, 2),
            "avstand_anker_lcdm_sigma": round(diff_lcdm, 2),
        }
        if engine_prediction is not None:
            details["motorprediksjon"] = engine_prediction
            details["avstand_motorprediksjon_sigma"] = round(
                abs(m - engine_prediction) / s, 2)

        if diff_efc <= 1.0 + EPS:
            return {
                "status": "PASS",
                "årsak": (f"The measurement {m}±{s} lies {diff_efc:.1f}σ from "
                          f"the anchor 0.430 — within ~1σ "
                          "(the confirmation criterion)."),
                "regel": self.kriterium()["bekreftelse"],
                "kilde": SEALED_DOI,
                **details,
            }

        over_lcdm_3sigma = (m - ANCHOR_LCDM) / s > 3.0 + EPS
        consistent_lcdm_1sigma = diff_lcdm < 1.0 + EPS
        excludes_anchor_2sigma = diff_efc >= 2.0 - EPS

        if over_lcdm_3sigma:
            return {
                "status": "FAIL",
                "årsak": (f"The measurement {m}±{s} lies "
                          f"{(m - ANCHOR_LCDM) / s:.1f}σ ABOVE 0.449 — "
                          "consistent with ΛCDM at high significance "
                          "(P2 damage-test)."),
                "regel": self.kriterium()["falsifikasjon_a"],
                "kilde": f"validation-ledger P2 (DAMAGE); {SEALED_DOI}",
                **details,
            }

        if consistent_lcdm_1sigma or excludes_anchor_2sigma:
            return {
                "status": "FAIL",
                "årsak": (f"The measurement {m}±{s} is consistent with 0.449 "
                          f"within <1σ ({diff_lcdm:.1f}σ) or "
                          f"excludes the anchor 0.430 at ≥2σ "
                          f"({diff_efc:.1f}σ) — falsified after P1."),
                "regel": self.kriterium()["falsifikasjon_b"],
                "kilde": SEALED_DOI,
                **details,
            }

        return {
            "status": "VENTER",
            "årsak": (f"The measurement {m}±{s} does not separate the models "
                      f"at the criterion: {diff_efc:.1f}σ from 0.430, "
                      f"{diff_lcdm:.1f}σ from 0.449 — neither confirmed "
                      "nor falsified."),
            "regel": "none — intermediate",
            "kilde": SEALED_DOI,
            **details,
        }

    # ------------------------------------------------------------------
    # The report — full provenance + the honesty clause
    # ------------------------------------------------------------------
    def rapport(self, measurement: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
        """Full report: criterion, predictions, verdict and honesty."""
        verdict = self.vurder(measurement, params)
        null = self.nullmodell()

        # The μ channel's status in the engine layer — measured, not assumed:
        # EFCVariantC carries μ(a) = 1 + (mu_0−1)·g(a). With the canonical
        # parameters (Ωm=0.3, H0=70, σ8=0.8, α=0) and mu_0=0.5 the engine
        # gives fσ8(z=0.7)=0.4301 — the sealed value is reproducible. That is
        # a consistency check, NOT a proof that mu_0=0.5 was the sealed
        # parameter value: the prediction's own B value is not publicly bound
        # to this engine's mu_0 scale. The verdict is therefore still passed
        # only against the anchor.
        mu_status = self._mu_status()
        return {
            "kriterium": self.kriterium(),
            "nullmodell_fs8_07": null,
            "dom": verdict,
            "mu_kanal_i_injisert_motor": mu_status["i_injisert_motor"],
            "mu_reproduksjon_variantc": mu_status["reproduksjon_variantc"],
            "ærlighet": mu_status["ærlighet"],
        }

    def _mu_status(self) -> dict:
        """Measures the μ channel's actual state.

        Two separate facts:
        1. Does the INJECTED engine (self.growth) have the channel? VariantA/B
           have μ=1 hardcoded — there mu_0 has no effect.
        2. The engine layer's capability: EFCVariantC has the channel, and with
           the canonical parameters + mu_0=0.5 it gives 0.4301 — the sealed
           value is reproducible (a consistency check, NOT proof about the
           sealed parameter value).
        """
        is_injected = bool(getattr(self.growth, "stotter_mu", lambda: False)())
        variant = type(self.growth.cosmology).__name__

        repro = None
        try:
            from efc_inference.core.cosmology_model import EFCVariantC
            g = EFCGrowth(cosmology=EFCVariantC())
            fs8_mu05 = float(g.compute(
                {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
                 "alpha_cosmo": 0.0, "mu_0": 0.5},
                np.array([0.7]))[0])
            fs8_mu1 = float(g.compute(
                {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8,
                 "alpha_cosmo": 0.0, "mu_0": 1.0},
                np.array([0.7]))[0])
            deviation = abs(fs8_mu05 - ANCHOR_EFC)
            repro = {
                "variant": "EFCVariantC",
                "mu_0": 0.5,
                "fs8_mu_0_5": round(fs8_mu05, 4),
                "fs8_mu_1_0": round(fs8_mu1, 4),
                "avvik_fra_anker": round(deviation, 4),
            }
        except Exception as e:  # pragma: no cover
            repro = {"feil": str(e)}

        injected_text = (
            f"The injected engine ({variant}) "
            + ("HAS" if is_injected else "does NOT have")
            + " the μ channel."
        )
        honesty = (
            f"{injected_text} The engine layer's capability: EFCVariantC "
            "carries μ = 1 + (mu_0−1)·g(a), and with canonical parameters "
            f"and mu_0=0.5 it gives fσ8(z=0.7)={repro['fs8_mu_0_5']:.4f} — "
            f"{repro['avvik_fra_anker']:.4f} from the sealed anchor "
            "0.430. The prediction is thus reproducible with the channel; "
            "that does NOT prove which mu_0 was sealed, and the verdict "
            "is still passed only against the anchor. The engine prediction "
            "is reported separately — deviations shall be visible, not hidden."
        ) if repro and "feil" not in repro else (
            f"{injected_text} The VariantC reproduction could not be measured "
            f"({repro.get('feil') if repro else 'unknown'}) — the arbiter "
            "claims nothing it has not measured.")

        return {
            "i_injisert_motor": is_injected,
            "variant": variant,
            "reproduksjon_variantc": repro,
            "ærlighet": honesty,
        }

    # ------------------------------------------------------------------
    # The bus payload (subject kosmos.kosmologi.oppgjoer.efc-fs8-arbiter)
    # ------------------------------------------------------------------
    def payload(self, measurement: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
        """Payload for publication — or for an artefact when the bus is
        read-only for us (the verden-MCP is a consumer only)."""
        return {
            "emne": "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter",
            "kriterium": self.kriterium(),
            "rapport": self.rapport(measurement, params),
            "proveniens": {
                "generert_av": "SealedFs8Arbiter",
                "modul": "efc_inference/arbiter/sealed_fs8.py",
                "growth_motor": type(self.growth).__name__,
                "generert_tid": None,  # filled in by the caller with the actual time
            },
        }
