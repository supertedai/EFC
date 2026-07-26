"""Tests for SPARC module."""

import numpy as np
import pytest
import tempfile
from pathlib import Path

from efc_inference.modules.sparc_module import SPARCModule
from efc_inference.engine.rotation import EFCRotation


def _create_test_data(tmpdir: Path, galaxy: str = "TestGalaxy") -> Path:
    """Create a minimal SPARC-format data file."""
    path = tmpdir / "test_sparc.dat"
    lines = [
        "# Test SPARC data",
        "galaxy_name distance radius Vobs eV Vgas Vdisk Vbul SBdisk SBbul",
    ]
    # 10 data points for TestGalaxy
    for i in range(1, 11):
        r = float(i) * 2.0  # kpc
        v = 150.0 + 10.0 * np.sin(i)  # km/s
        ev = 5.0 + i * 0.5
        lines.append(f"{galaxy} 10.0 {r:.1f} {v:.1f} {ev:.1f} "
                     f"50.0 100.0 0.0 20.0 0.0")

    path.write_text("\n".join(lines))
    return path


class TestSPARCModule:
    def test_load_multi_galaxy(self, tmp_path):
        data_path = _create_test_data(tmp_path, galaxy="NGC1234")
        module = SPARCModule()
        module.load_data(data_path=str(data_path), galaxy="NGC1234")

        assert module.n_data == 10
        assert module.galaxy_name == "NGC1234"
        assert len(module.coordinates) == 10
        assert len(module.observed) == 10
        assert len(module.errors) == 10

    def test_galaxy_not_found(self, tmp_path):
        data_path = _create_test_data(tmp_path, galaxy="NGC1234")
        module = SPARCModule()

        with pytest.raises(ValueError, match="not found"):
            module.load_data(data_path=str(data_path), galaxy="NGC9999")

    def test_file_not_found(self):
        module = SPARCModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/path.dat", galaxy="X")

    def test_predict(self, tmp_path):
        data_path = _create_test_data(tmp_path, galaxy="TestGal")
        module = SPARCModule()
        module.load_data(data_path=str(data_path), galaxy="TestGal")

        params = {
            "entropy_scale": 1e-24,
            "length_scale": 8.0,
            "flow_constant": 1.0,
            "velocity_scale": 200.0,
        }

        pred = module.predict(params)
        assert len(pred) == 10
        assert all(np.isfinite(pred))

    def test_log_likelihood(self, tmp_path):
        data_path = _create_test_data(tmp_path, galaxy="TestGal")
        module = SPARCModule()
        module.load_data(data_path=str(data_path), galaxy="TestGal")

        params = {
            "entropy_scale": 1e-24,
            "length_scale": 8.0,
            "flow_constant": 1.0,
            "velocity_scale": 200.0,
        }

        ll = module.log_likelihood(params)
        assert np.isfinite(ll)

    def test_residuals(self, tmp_path):
        data_path = _create_test_data(tmp_path, galaxy="TestGal")
        module = SPARCModule()
        module.load_data(data_path=str(data_path), galaxy="TestGal")

        params = {
            "entropy_scale": 1e-24,
            "length_scale": 8.0,
            "flow_constant": 1.0,
            "velocity_scale": 200.0,
        }

        resid = module.residuals(params)
        assert len(resid) == 10
        assert all(np.isfinite(resid))

    def test_min_error_floor(self, tmp_path):
        """Errors below min_error should be floored."""
        data_path = _create_test_data(tmp_path, galaxy="TestGal")
        module = SPARCModule()
        module.load_data(data_path=str(data_path), galaxy="TestGal",
                         min_error=10.0)
        assert all(module.errors >= 10.0)

    def test_available_galaxies(self, tmp_path):
        # Create file with two galaxies
        path = tmp_path / "multi.dat"
        lines = [
            "galaxy_name distance radius Vobs eV Vgas Vdisk Vbul SBdisk SBbul",
            "GalA 10.0 1.0 100.0 5.0 50.0 80.0 0.0 20.0 0.0",
            "GalB 15.0 2.0 120.0 6.0 60.0 90.0 0.0 25.0 0.0",
        ]
        path.write_text("\n".join(lines))

        module = SPARCModule()
        galaxies = module.available_galaxies(str(path))
        assert "GalA" in galaxies
        assert "GalB" in galaxies

    def test_not_loaded_raises(self):
        module = SPARCModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict({"entropy_scale": 1.0})
