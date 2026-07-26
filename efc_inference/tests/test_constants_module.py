"""Tests for varying constants module."""

import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.constants_module import ConstantsModule


def _create_constants_csv(tmpdir: Path) -> Path:
    """Create a minimal constants CSV file."""
    path = tmpdir / "constants_test.csv"
    lines = [
        "z,quantity,delta_over,sigma",
        "0.89,mu,0.0,1.0e-06",
        "1.15,alpha_em,0.0,1.2e-06",
        "1.58,mu,0.0,5.0e-07",
        "2.34,alpha_em,0.0,2.0e-06",
    ]
    path.write_text("\n".join(lines))
    return path


class TestConstantsModule:
    def test_load_data(self, tmp_path):
        path = _create_constants_csv(tmp_path)
        module = ConstantsModule()
        module.load_data(data_path=str(path))

        assert module.n_data == 4
        assert module.name == "constants"
        assert len(module.quantities) == 4
        assert "mu" in module.quantities
        assert "alpha_em" in module.quantities

    def test_filter_by_quantity(self, tmp_path):
        path = _create_constants_csv(tmp_path)
        module = ConstantsModule()
        module.load_data(data_path=str(path), quantity="mu")

        assert module.n_data == 2
        assert all(q == "mu" for q in module.quantities)

    def test_predict_returns_zeros(self, tmp_path):
        """Null hypothesis: predictions are always zero."""
        path = _create_constants_csv(tmp_path)
        module = ConstantsModule()
        module.load_data(data_path=str(path))

        pred = module.predict({})
        assert len(pred) == 4
        assert np.allclose(pred, 0.0)

    def test_log_likelihood(self, tmp_path):
        path = _create_constants_csv(tmp_path)
        module = ConstantsModule()
        module.load_data(data_path=str(path))

        ll = module.log_likelihood({})
        assert np.isfinite(ll)
        # With observed=0 and pred=0, likelihood should be high
        assert ll > -10.0

    def test_file_not_found(self):
        module = ConstantsModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/path.csv")

    def test_no_data_path(self):
        module = ConstantsModule()
        with pytest.raises(ValueError, match="data_path"):
            module.load_data()

    def test_available_quantities(self, tmp_path):
        path = _create_constants_csv(tmp_path)
        qtys = ConstantsModule.available_quantities(str(path))
        assert "mu" in qtys
        assert "alpha_em" in qtys
