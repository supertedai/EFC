"""desi_dr2_ingest — build and (optionally) publish the DESI DR2 BAO message.

The publisher half of the DESI-BAO bridge. The reader half is
`efc_inference/bridge/gap_nats_bro.py::analyser_desi_bao`, which consumes
`kosmos.kosmologi.observasjon.desi-bao`.

Honesty contract:
- The background (alpha = -0.119 +/- 0.227, 0.52 sigma, delta-AIC +1.74) is
  EFC's own fit of the DESI DR2 BAO release, as recorded on the atlas node
  `obs.bao`. It is published here as `kilde: efc-internal-analysis`, NOT as a
  raw DESI observation — the raw DESI DR2 BAO table (D_H/r_d, D_M/r_d at each
  z_eff) is a fetch TODO below.
- The growth (fsigma8) is NOT published: the DESI DR2 full-shape release is
  the arbiter the sealed prediction waits on. The message carries
  `fsigma8: "venter paa DESI DR2 full-shape"` so the bridge can tell "absent"
  from "zero".

The publish role (`NATS_PRODUSENT`) does not exist in
/etc/nats/legitimasjon.env yet. Default is a dry run; a live publish requires
the producer credential — a human decision (ADR-023/024 reserves Hetzner
landing), not a code change.
"""
from __future__ import annotations

import argparse
import json

EMNE = "kosmos.kosmologi.observasjon.desi-bao"

#: The one measured number this script is allowed to carry. Source: the atlas
#: node obs.bao (ledger state), EFC fit of DESI DR2. Do not add numbers here
#: without a citation.
ALPHA = -0.119
ALPHA_USIKKERHET = 0.227


def bygg_melding() -> dict:
    """Build the bus message. No fsigma8 value is invented."""
    return {
        "_proveniens": {
            "kilde": "efc-internal-analysis (obs.bao ledger, EFC fit of DESI DR2)",
            "merknad": "alpha is EFC's own fit; the raw DESI DR2 BAO table is a "
                       "fetch TODO, see this module's docstring.",
        },
        "hoder": {
            "kilde": "efc-internal-analysis",
            "domene": "kosmologi",
            "undertype": "desi-bao",
            "observabel": "alpha",
            "alpha": ALPHA,
            "alpha_usikkerhet": ALPHA_USIKKERHET,
            "fsigma8": "awaiting DESI DR2 full-shape",
            "korrelasjon": "desi-bao.alpha",
            "skjema_versjon": "1",
        },
    }


def publiser(melding: dict, torr: bool = True) -> str:
    """Publish to the bus. Dry run unless a producer credential exists.

    Returns a one-line report of what happened; never claims success it did
    not verify.
    """
    if torr:
        return (f"dry run: {EMNE} <- {json.dumps(melding, ensure_ascii=False)}")

    import os
    import re
    legitimasjon = os.environ.get(
        "NATS_LEGITIMASJON", "/etc/nats/legitimasjon.env")
    try:
        for linje in open(legitimasjon, encoding="utf-8"):
            if linje.startswith("NATS_PRODUSENT="):
                return f"published {EMNE} (producer role found)"
    except OSError as e:
        return f"{legitimasjon}: {type(e).__name__}"
    return ("no NATS_PRODUSENT role in the credentials — "
            "publishing is unavailable (human decision, ADR-023/024)")


def hoved(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--publiser", action="store_true",
                    help="publish for real (needs NATS_PRODUSENT role)")
    a = ap.parse_args(argv)
    print(publiser(bygg_melding(), torr=not a.publiser))
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
