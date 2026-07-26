"""Tests for fσ8 growth rate module."""

import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.growth_module import GrowthModule
from efc_inference.engine.growth import EFCGrowth


def _create_fs8_csv(tmpdir: Path) -> Path:
    """Create a minimal fσ8 CSV file."""
    path = tmpdir / "fs8_test.csv"
    lines = [
        "z,fs8,sigma",
        "0.02,0.428,0.046",
        "0.38,0.497,0.045",
        "0.61,0.436,0.034",
        "0.85,0.470,0.080",
        "1.40,0.482,0.116",
    ]
    path.write_text("\n".join(lines))
    return path


class TestGrowthModule:
    def test_load_data(self, tmp_path):
        path = _create_fs8_csv(tmp_path)
        module = GrowthModule()
        module.load_data(data_path=str(path))

        assert module.n_data == 5
        assert module.name == "growth"
        assert len(module.coordinates) == 5
        assert len(module.observed) == 5
        assert len(module.errors) == 5

    def test_file_not_found(self):
        module = GrowthModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/path.csv")

    def test_no_data_path(self):
        module = GrowthModule()
        with pytest.raises(ValueError, match="data_path"):
            module.load_data()

    def test_predict(self, tmp_path):
        path = _create_fs8_csv(tmp_path)
        module = GrowthModule()
        module.load_data(data_path=str(path))

        params = {"Omega_m": 0.315, "sigma8": 0.811, "alpha_cosmo": 0.0, "H0": 67.4}
        pred = module.predict(params)

        assert len(pred) == 5
        assert all(np.isfinite(pred))
        # fσ8 values should be in reasonable range [0, 1]
        assert all(pred > 0)
        assert all(pred < 1.5)

    def test_log_likelihood(self, tmp_path):
        path = _create_fs8_csv(tmp_path)
        module = GrowthModule()
        module.load_data(data_path=str(path))

        params = {"Omega_m": 0.315, "sigma8": 0.811, "alpha_cosmo": 0.0, "H0": 67.4}
        ll = module.log_likelihood(params)

        assert np.isfinite(ll)
        # LL can be positive due to normalization constant -0.5*ln(2*pi*sigma^2)
        # Just verify it's finite and not -inf

    def test_residuals(self, tmp_path):
        path = _create_fs8_csv(tmp_path)
        module = GrowthModule()
        module.load_data(data_path=str(path))

        params = {"Omega_m": 0.315, "sigma8": 0.811, "alpha_cosmo": 0.0, "H0": 67.4}
        resid = module.residuals(params)

        assert len(resid) == 5
        assert all(np.isfinite(resid))

    def test_not_loaded_raises(self):
        module = GrowthModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict({"Omega_m": 0.3})

    def test_min_error_floor(self, tmp_path):
        path = _create_fs8_csv(tmp_path)
        module = GrowthModule()
        module.load_data(data_path=str(path), min_error=0.1)
        assert all(module.errors >= 0.1)

    def test_lcdm_fallback_consistency(self, tmp_path):
        """LCDM growth should give fσ8 ~ 0.4-0.5 at z~0."""
        path = tmp_path / "low_z.csv"
        path.write_text("z,fs8,sigma\n0.01,0.45,0.05\n")
        module = GrowthModule()
        module.load_data(data_path=str(path))

        params = {"Omega_m": 0.315, "sigma8": 0.811, "alpha_cosmo": 0.0, "H0": 67.4}
        pred = module.predict(params)

        # At z~0, fσ8 should be close to sigma8
        # f(z=0) ~ Omega_m^0.55 ~ 0.55, so fσ8 ~ 0.55 * 0.811 ~ 0.45
        assert 0.3 < pred[0] < 0.6
