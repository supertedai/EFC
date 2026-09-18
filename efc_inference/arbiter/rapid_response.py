"""The rapid-response watch (step 14).

The last link in the sealed chain: when DESI DR2 full-shape
galaxy-RSD fσ8(z~0.7) is published, the verdict must be passed
automatically — not wait for a manual run.

The watch is PURE — it processes the last bus message and runs
SealedFs8Arbiter (step 12, with step 13's μ-aware engine prediction).
Fetching from the bus is the caller's responsibility (injectable);
publishing happens only if the caller grants write access — otherwise
the artifact is the deliverable and the gap is declared.

Recognition is CONSERVATIVE: the watch judges only a message that is
documented as DESI DR2 full-shape galaxy-RSD fσ8 — tracer LRG/ELG,
observable fsigma8, survey/source pointing at DR2 full-shape, NOT
marked as baseline (efc-sealed-baseline / arbiter: nei), z_eff in
[0.5, 0.9], with fsigma8 AND sigma. Anything else passes no verdict —
the watch waits rather than judging wrong.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
from typing import Optional

from efc_inference.arbiter.sealed_fs8 import (
    SealedFs8Arbiter,
    TILLATTE_TRACERE,
    Z_MIN,
    Z_MAKS,
)

BASELINE_KILDE = "efc-sealed-baseline"


def _endelig(v) -> bool:
    """Finiteness check that never crashes on invalid types."""
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


class RapidResponseVakt:
    """Processes bus messages and passes the verdict when it can."""

    def __init__(self, arbiter: Optional[SealedFs8Arbiter] = None,
                 artefakt_sti: str = "arbiter-efc-fs8-dom.json"):
        self.arbiter = arbiter or SealedFs8Arbiter()
        self.artefakt_sti = artefakt_sti

    # ------------------------------------------------------------------
    # Recognition (conservative)
    # ------------------------------------------------------------------
    def gjenkjenn(self, melding: dict) -> Optional[dict]:
        """Extracts an arbiter measurement from a bus message — or None.

        Requires the WHOLE documentation: galaxy-RSD tracer (LRG/ELG),
        observable fsigma8, survey/source pointing at DESI DR2
        full-shape, NOT baseline, z_eff in the window, fsigma8 + sigma.
        """
        if not isinstance(melding, dict):
            return None
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return None

        # Not the baseline — it is the arbiter's foundation, not the measurement.
        kilde = str(hoder.get("kilde", "")).lower()
        if hoder.get("arbiter") == "nei" or BASELINE_KILDE in kilde:
            return None

        # The observable must be fsigma8 — the watch judges no others.
        if str(hoder.get("observabel", "")).lower() != "fsigma8":
            return None

        # The survey must be DESI DR2 — not merely contain «dr2»
        # («BOSS DR2» would be a different data set).
        survey = str(hoder.get("survey", "")).lower()
        if not ("desi" in survey and "dr2" in survey):
            return None

        tracer = hoder.get("tracer")
        if tracer is None or str(tracer).upper() not in TILLATTE_TRACERE:
            return None

        for felt in ("fsigma8", "fsigma8_sigma", "z_eff"):
            if felt not in maalt or maalt[felt] is None:
                return None

        try:
            fs8 = float(maalt["fsigma8"])
            sigma = float(maalt["fsigma8_sigma"])
            z_eff = float(maalt["z_eff"])
        except (TypeError, ValueError):
            return None

        if not (_endelig(fs8) and _endelig(sigma) and _endelig(z_eff)):
            return None

        if not (Z_MIN <= z_eff <= Z_MAKS):
            return None

        return {
            "fsigma8": fs8,
            "sigma": sigma,
            "z_eff": z_eff,
            "tracer": str(tracer).upper(),
            "kilde": str(hoder.get("kilde", "unknown")),
        }

    # ------------------------------------------------------------------
    # The verdict
    # ------------------------------------------------------------------
    def sjekk(self, melding: dict,
              params: Optional[dict] = None) -> dict:
        """Runs the watch: recognizes, judges, writes the artifact.

        The artifact carries FULL input provenance: message ID, source,
        the message's sha256 hash, the recognized measurement and the
        parameters — so that the verdict can always be tied back to a
        concrete bus message.
        """
        måling = self.gjenkjenn(melding)
        if måling is None:
            dom = {
                "status": "VENTER",
                "årsak": self._hvorfor_ikke(melding),
                "regel": "none — the message is not the arbiter measurement",
                "kilde": "RapidResponseVakt.gjenkjenn",
            }
        else:
            dom = self.arbiter.vurder(måling, params)

        payload = {
            "emne": "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter",
            "kriterium": self.arbiter.kriterium(),
            "input": self._input_proveniens(melding, måling, params),
            "rapport": {
                "dom": dom,
                "mu_kanal_i_injisert_motor": bool(
                    getattr(self.arbiter.growth, "stotter_mu",
                            lambda: False)()),
                "ærlighet": self.arbiter.rapport().get("ærlighet", ""),
            },
            "proveniens": {
                "generert_av": "RapidResponseVakt",
                "modul": "efc_inference/arbiter/rapid_response.py",
                "arbiter": "SealedFs8Arbiter",
                "generert_tid": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(),
            },
        }
        self._skriv_artefakt(payload)
        return payload

    def _input_proveniens(self, melding: dict,
                          måling: Optional[dict],
                          params: Optional[dict]) -> dict:
        """A verifiable link between the bus message and the verdict."""
        serialisert = json.dumps(melding, sort_keys=True,
                                 ensure_ascii=False)
        meldings_id = None
        hoder = melding.get("hoder") if isinstance(melding, dict) else None
        if isinstance(hoder, dict):
            meldings_id = hoder.get("Nats-Msg-Id") or hoder.get("kilde")
        return {
            "meldings_id": meldings_id,
            "meldings_hash_sha256": hashlib.sha256(
                serialisert.encode("utf-8")).hexdigest(),
            "gjenkjent_maaling": måling,
            "params": params,
        }

    def _hvorfor_ikke(self, melding: dict) -> str:
        """Explains honestly why a message was not judged — without
        crashing on invalid types/shapes."""
        if not isinstance(melding, dict):
            return "The message is not a dict — invalid form."
        hoder = melding.get("hoder")
        maalt = melding.get("maalt")
        if not isinstance(hoder, dict) or not isinstance(maalt, dict):
            return "The message lacks hoder/maalt — invalid form."

        kilde = str(hoder.get("kilde", "")).lower()
        if hoder.get("arbiter") == "nei" or BASELINE_KILDE in kilde:
            return ("The message is the sealed baseline — "
                    "reference values, not the arbiter measurement.")
        if str(hoder.get("observabel", "")).lower() != "fsigma8":
            return (f"The observable is {hoder.get('observabel', 'unknown')} "
                    "— the watch judges only fsigma8.")
        survey = str(hoder.get("survey", "")).lower()
        if not ("desi" in survey and "dr2" in survey):
            return ("The survey is not DESI DR2 full-shape "
                    f"(survey={hoder.get('survey', 'unknown')}, "
                    f"kilde={hoder.get('kilde', 'unknown')}).")

        tracer = str(hoder.get("tracer", "unknown"))
        if tracer.upper() not in TILLATTE_TRACERE:
            return (f"The tracer is {tracer} — not galaxy-RSD "
                    f"({'/'.join(TILLATTE_TRACERE)}).")

        for felt in ("fsigma8", "fsigma8_sigma", "z_eff"):
            if felt not in maalt or maalt[felt] is None:
                return f"The measurement lacks the field «{felt}»."

        z_verdi = maalt["z_eff"]
        if not _endelig(z_verdi):
            return f"z_eff={z_verdi!r} is not a finite number."
        z = float(z_verdi)
        if not (Z_MIN <= z <= Z_MAKS):
            return (f"z_eff={z} lies outside the test's z window "
                    f"[{Z_MIN}, {Z_MAKS}].")
        return "The message was not recognized as an arbiter measurement."

    # ------------------------------------------------------------------
    # The artifact
    # ------------------------------------------------------------------
    def _skriv_artefakt(self, payload: dict) -> None:
        with open(self.artefakt_sti, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
