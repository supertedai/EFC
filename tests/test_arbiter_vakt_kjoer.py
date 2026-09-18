"""Tests for the settlement publication in the arbiter watch runner (L-016).

When an ACTUAL verdict is reached (PASS/FAIL), the outcome must be
published on the bus as a settled prediction
(kosmos.kosmologi.oppgjoer.efc-fs8-arbiter). VENTER diagnoses are NEVER
published — a non-verdict is not a settlement.
The transport is injected; no test touches the bus.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "maintenance"))

import arbiter_vakt_kjoer as kjoerer  # noqa: E402
from efc_inference.arbiter.rapid_response import RapidResponseVakt  # noqa: E402


def _dr2_melding(fs8=0.430, sigma=0.030):
    return {
        "hoder": {"tracer": "LRG", "survey": "DESI DR2",
                  "observabel": "fsigma8",
                  "kilde": "desi-dr2-full-shape",
                  "Nats-Msg-Id": "dr2-full-shape.lrg.0.7.test"},
        "maalt": {"fsigma8": fs8, "fsigma8_sigma": sigma, "z_eff": 0.7},
    }


def test_pass_publiseres_som_oppgjoer(tmp_path):
    publiserte = []
    r = kjoerer.kjoer(_dr2_melding(fs8=0.430, sigma=0.030),
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=lambda emne, payload:
                      publiserte.append((emne, payload)) or "ok")
    assert r["dom"]["status"] == "PASS"
    assert r["publiseringsstatus"] == "ok"
    assert len(publiserte) == 1
    emne, payload = publiserte[0]
    assert emne == "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
    assert json.loads(payload)["rapport"]["dom"]["status"] == "PASS"


def test_fail_publiseres_som_oppgjoer(tmp_path):
    publiserte = []
    r = kjoerer.kjoer(_dr2_melding(fs8=0.510, sigma=0.020),
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=lambda emne, payload:
                      publiserte.append((emne, payload)) or "ok")
    assert r["dom"]["status"] == "FAIL"
    assert len(publiserte) == 1


def test_venter_publiseres_aldri(tmp_path):
    """The baseline message yields VENTER — no settlement publication."""
    baseline = {
        "hoder": {"tracer": "QSO", "survey": "DESI DR1",
                  "observabel": "fsigma8", "kilde": "efc-sealed-baseline",
                  "arbiter": "nei"},
        "maalt": {"fsigma8": 0.318, "fsigma8_sigma": 0.076,
                  "z_eff": 1.491},
    }
    publiserte = []
    r = kjoerer.kjoer(baseline,
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=lambda emne, payload:
                      publiserte.append((emne, payload)) or "ok")
    assert r["dom"]["status"] == "VENTER"
    assert publiserte == []
    assert "no verdict" in r["publiseringsstatus"]


def test_artefakt_skrives_uansett(tmp_path):
    r = kjoerer.kjoer(_dr2_melding(fs8=0.440, sigma=0.030),
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=lambda emne, payload: "test")
    artefakt = json.loads((tmp_path / "dom.json").read_text())
    assert artefakt["rapport"]["dom"]["status"] == r["dom"]["status"]


def test_transport_med_krasj_stopper_ikke_artefakten(tmp_path):
    """A transport that RAISES must not stop the run —
    the verdict is reached, the artifact is written, the error is reported."""
    def krasjende_transport(emne, payload):
        raise RuntimeError("the network went down")

    r = kjoerer.kjoer(_dr2_melding(fs8=0.430, sigma=0.030),
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=krasjende_transport)
    assert r["dom"]["status"] == "PASS"
    assert "publish error" in r["publiseringsstatus"]
    artefakt = json.loads((tmp_path / "dom.json").read_text())
    assert artefakt["rapport"]["dom"]["status"] == "PASS"


def test_transport_feilstatus_stopper_ikke_artefakten(tmp_path):
    """A transport that returns an error status (rather than raising) —
    the artifact is still written, the status is reported honestly."""
    r = kjoerer.kjoer(_dr2_melding(fs8=0.430, sigma=0.030),
                      artefakt_sti=str(tmp_path / "dom.json"),
                      publiser=lambda emne, payload: "network error: timeout")
    assert r["dom"]["status"] == "PASS"
    assert r["publiseringsstatus"] == "network error: timeout"
    assert (tmp_path / "dom.json").exists()


def test_ugyldig_nats_produsent_gir_status_uten_krasj(monkeypatch):
    """An invalid NATS_PRODUSENT shape (non-numeric port, missing parts)
    must give a status string — never a ValueError."""
    for url in ("nats://u:p@host:not-a-port",
                "nats://u:p@host",
                "not-a-url"):
        monkeypatch.setenv("NATS_PRODUSENT", url)
        status = kjoerer.publiser_best_effort(
            "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter", "{}")
        assert isinstance(status, str) and status != "ok", url
