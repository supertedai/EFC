"""Tester for repro-settet (L-003).

Settet skal la en ekstern person reprodusere den forseglede
prediksjonen uten nettverk og uten datafiler — og det skal deklarere
kilden og toleransen ærlig.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPRO = Path("scripts/repro/sealed_fs8_repro.py")
README = Path("scripts/repro/README.md")


def test_repro_skriptet_finnes_og_leser_leser_ingen_eksterne_filer():
    innhold = REPRO.read_text(encoding="utf-8")
    assert "EFCVariantC" in innhold
    assert "0.430" in innhold
    # Skriptet skal ikke lese datafiler eller nettverk
    assert "requests" not in innhold and "urlopen" not in innhold
    assert "open(" not in innhold


def test_repro_skriptet_kjorer_og_reproduserer():
    resultat = subprocess.run(
        [sys.executable, str(REPRO)],
        capture_output=True, text=True, timeout=120)
    assert resultat.returncode == 0, resultat.stderr
    assert "0.4301" in resultat.stdout
    assert "OK" in resultat.stdout


def test_repro_skriptet_rapporterer_kilden():
    resultat = subprocess.run(
        [sys.executable, str(REPRO)],
        capture_output=True, text=True, timeout=120)
    assert "10.6084/m9.figshare.32013156" in resultat.stdout


def test_readme_har_instruksjoner_og_aerlighet():
    tekst = README.read_text(encoding="utf-8")
    assert "git clone" in tekst
    assert "sealed_fs8_repro.py" in tekst
    assert "Does not show" in tekst  # ærlighetsseksjonen


def test_repro_skriptet_feiler_kontrollert_ved_gal_mu0():
    """Skriptet skal returnere != 0 dersom den beregnede verdien er
    utenfor toleransen — ingen stille falsk suksess. Faktisk test:
    injiser en feil beregner via main(compute_fn=...) og sjekk retur."""
    import sys as _sys
    _sys.path.insert(0, str(REPRO.parent.parent.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sealed_fs8_repro", str(REPRO))
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    ret = mod.main(compute_fn=lambda: 0.5000)  # 16 % unna — utenfor
    assert ret == 2
