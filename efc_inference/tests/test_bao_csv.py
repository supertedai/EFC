"""Tests for BAO module with CSV loading and distance computations."""

import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.bao_module import BAOModule, C_KM_S, DEFAULT_RD
from efc_inference.engine.hubble import EFCHubble


def _create_bao_csv(tmpdir: Path) -> Path:
    """Create a minimal BAO CSV file with all 3 observable types."""
    path = tmpdir / "bao_test.csv"
    lines = [
        "z,observable,value,sigma",
        "0.38,DM_over_rd,10.23,0.17",
        "0.51,DH_over_rd,22.33,0.58",
        "0.70,DV_over_rd,17.86,0.33",
    ]
    path.write_text("\n".join(lines))
    return path


def _create_bao_dh_only(tmpdir: Path) -> Path:
    """Create CSV with only DH measurements."""
    path = tmpdir / "bao_dh.csv"
    lines = [
        "z,observable,value,sigma",
        "0.38,DH_over_rd,25.00,0.76",
        "0.51,DH_over_rd,22.33,0.58",
        "0.61,DH_over_rd,20.75,0.53",
    ]
    path.write_text("\n".join(lines))
    return path


LCDM_PARAMS = {
    "H0": 67.4,
    "Omega_m": 0.315,
    "alpha_cosmo": 0.0,
    "r_d": 147.09,
}


class TestBAOCSV:
    def test_load_csv(self, tmp_path):
        path = _create_bao_csv(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        assert module.n_data == 3
        assert module.name == "bao"
        assert len(module.coordinates) == 3
        assert len(module.observed) == 3
        assert len(module.errors) == 3

    def test_file_not_found(self):
        module = BAOModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/bao.csv")

    def test_predict_all_types(self, tmp_path):
        """Test predictions for DH, DM, and DV observables."""
        path = _create_bao_csv(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        pred = module.predict(LCDM_PARAMS)

        assert len(pred) == 3
        assert all(np.isfinite(pred))
        assert all(pred > 0)

    def test_dh_prediction(self, tmp_path):
        """DH/rd = c / (H(z) * r_d), should be ~20-30 for LCDM."""
        path = _create_bao_dh_only(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        pred = module.predict(LCDM_PARAMS)

        # DH/rd should decrease with z (H(z) increases)
        assert pred[0] > pred[-1]
        # Reasonable LCDM range
        for p in pred:
            assert 10 < p < 40

    def test_log_likelihood(self, tmp_path):
        path = _create_bao_csv(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        ll = module.log_likelihood(LCDM_PARAMS)
        assert np.isfinite(ll)
        assert ll < 0

    def test_residuals(self, tmp_path):
        path = _create_bao_csv(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        resid = module.residuals(LCDM_PARAMS)
        assert len(resid) == 3
        assert all(np.isfinite(resid))

    def test_comoving_distance(self, tmp_path):
        """Comoving distance should increase with z."""
        path = _create_bao_csv(tmp_path)
        module = BAOModule()
        module.load_data(data_path=str(path))

        d1 = module._comoving_distance(LCDM_PARAMS, 0.5)
        d2 = module._comoving_distance(LCDM_PARAMS, 1.0)

        assert d2 > d1 > 0
        # Rough LCDM: D_M(z=1) ~ 3300 Mpc
        assert 2000 < d2 < 5000

    def test_unknown_observable(self, tmp_path):
        path = tmp_path / "bad_obs.csv"
        path.write_text("z,observable,value,sigma\n0.5,UNKNOWN,10.0,1.0\n")
        module = BAOModule()
        module.load_data(data_path=str(path))

        with pytest.raises(ValueError, match="Unknown BAO observable"):
            module.predict(LCDM_PARAMS)

    def test_not_loaded_raises(self):
        module = BAOModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict(LCDM_PARAMS)
