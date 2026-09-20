"""Tests for the repro kit (L-003).

The kit must let an external person reproduce the sealed prediction
without network and without data files — and it must declare the
source and the tolerance honestly.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPRO = Path("scripts/repro/sealed_fs8_repro.py")
README = Path("scripts/repro/README.md")


def test_repro_skriptet_finnes_og_leser_leser_ingen_eksterne_filer():
    content = REPRO.read_text(encoding="utf-8")
    assert "EFCVariantC" in content
    assert "0.430" in content
    # The script must not read data files or the network
    assert "requests" not in content and "urlopen" not in content
    assert "open(" not in content


def test_repro_skriptet_kjorer_og_reproduserer():
    result = subprocess.run(
        [sys.executable, str(REPRO)],
        capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert "0.4301" in result.stdout
    assert "OK" in result.stdout


def test_repro_skriptet_rapporterer_kilden():
    result = subprocess.run(
        [sys.executable, str(REPRO)],
        capture_output=True, text=True, timeout=120)
    assert "10.6084/m9.figshare.32013156" in result.stdout


def test_readme_har_instruksjoner_og_aerlighet():
    tekst = README.read_text(encoding="utf-8")
    assert "git clone" in tekst
    assert "sealed_fs8_repro.py" in tekst
    assert "Does not show" in tekst  # ærlighetsseksjonen


def test_repro_skriptet_feiler_kontrollert_ved_gal_mu0():
    """The script must return != 0 if the computed value is outside
    the tolerance — no silent false success. The actual test: inject
    a wrong calculator via main(compute_fn=...) and check the return."""
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
