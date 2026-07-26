"""Tests for H(z) cosmic chronometer module."""

import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.hz_module import HzModule
from efc_inference.engine.hubble import EFCHubble


def _create_hz_csv(tmpdir: Path) -> Path:
    """Create a minimal H(z) CSV file."""
    path = tmpdir / "hz_test.csv"
    lines = [
        "z,Hz_km_s_Mpc,sigma",
        "0.07,69.0,19.6",
        "0.20,72.9,29.6",
        "0.35,82.7,8.4",
        "0.48,97.0,62.0",
        "0.90,117.0,23.0",
    ]
    path.write_text("\n".join(lines))
    return path


class TestHzModule:
    def test_load_data(self, tmp_path):
        path = _create_hz_csv(tmp_path)
        module = HzModule()
        module.load_data(data_path=str(path))

        assert module.n_data == 5
        assert module.name == "hz"
        assert len(module.coordinates) == 5
        assert len(module.observed) == 5
        assert len(module.errors) == 5

    def test_file_not_found(self):
        module = HzModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/path.csv")

    def test_no_data_path(self):
        module = HzModule()
        with pytest.raises(ValueError, match="data_path"):
            module.load_data()

    def test_predict(self, tmp_path):
        path = _create_hz_csv(tmp_path)
        module = HzModule()
        module.load_data(data_path=str(path))

        params = {"H0": 67.4, "Omega_m": 0.315, "alpha_cosmo": 0.0}
        pred = module.predict(params)

        assert len(pred) == 5
        assert all(np.isfinite(pred))
        # H(z) should increase with z for LCDM
        assert pred[-1] > pred[0]

    def test_log_likelihood(self, tmp_path):
        path = _create_hz_csv(tmp_path)
        module = HzModule()
        module.load_data(data_path=str(path))

        params = {"H0": 67.4, "Omega_m": 0.315, "alpha_cosmo": 0.0}
        ll = module.log_likelihood(params)

        assert np.isfinite(ll)
        assert ll < 0  # log-likelihood is negative

    def test_residuals(self, tmp_path):
        path = _create_hz_csv(tmp_path)
        module = HzModule()
        module.load_data(data_path=str(path))

        params = {"H0": 67.4, "Omega_m": 0.315, "alpha_cosmo": 0.0}
        resid = module.residuals(params)

        assert len(resid) == 5
        assert all(np.isfinite(resid))

    def test_not_loaded_raises(self):
        module = HzModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict({"H0": 67.4})

    def test_min_error_floor(self, tmp_path):
        path = _create_hz_csv(tmp_path)
        module = HzModule()
        module.load_data(data_path=str(path), min_error=30.0)
        assert all(module.errors >= 30.0)

    def test_negative_z_raises(self, tmp_path):
        path = tmp_path / "bad_hz.csv"
        path.write_text("z,Hz_km_s_Mpc,sigma\n-0.1,70.0,5.0\n")
        module = HzModule()
        with pytest.raises(ValueError, match="non-negative"):
            module.load_data(data_path=str(path))
