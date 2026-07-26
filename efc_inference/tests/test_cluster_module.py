"""Tests for TNG-Cluster entropy-structure correlation module."""

import json
import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.cluster_module import ClusterModule


# ── Test data path ────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent.parent / "data" / "clusters"
TNG_JSON = DATA_DIR / "tng_cluster_results.json"


def _create_minimal_json(tmpdir: Path) -> Path:
    """Create a minimal TNG-cluster-format JSON for testing."""
    data = {
        "dataset": "TNG-Cluster + ACCEPT comparison",
        "tng_cluster": {
            "n_halos": 352,
            "redshift": 0,
            "mass_range": {
                "log_M500c_min": 14.0,
                "log_M500c_max": 15.3,
            },
            "cool_core_population": {
                "SCC": {"count": 28, "fraction": 0.08},
                "WCC": {"count": 206, "fraction": 0.59},
                "NCC": {"count": 118, "fraction": 0.34},
            },
        },
        "accept": {
            "n_clusters": 239,
            "correlation_alpha_yCCT": {"rho": 0.36},
        },
        "primary_correlations": {
            "ne_slope_vs_K0": {
                "rho": -0.872,
                "p_value": 7.96e-111,
                "N": 352,
            },
        },
        "mass_controlled": {
            "partial_ne_slope_K0_given_M": {
                "rho": -0.880,
                "p_value": 2e-115,
                "N": 352,
            },
        },
        "mass_binned_analysis": {
            "bins": [
                {"mass_bin": "[14.0, 14.3)", "N": 41, "rho": -0.790, "p_value": 9e-10},
                {"mass_bin": "[14.3, 14.6)", "N": 118, "rho": -0.860, "p_value": 1e-35},
                {"mass_bin": "[14.6, 14.9)", "N": 121, "rho": -0.901, "p_value": 5e-45},
                {"mass_bin": "[14.9, 15.5)", "N": 71, "rho": -0.897, "p_value": 4e-26},
            ],
        },
        "ks_test": {
            "D_statistic": 1.000,
            "p_value": 2.4e-30,
        },
        "sign_flip_summary": {
            "tng_cluster_rho": -0.872,
            "accept_rho": 0.36,
            "sign_reversal": True,
            "magnitude_difference": 1.23,
        },
    }
    path = tmpdir / "tng_test.json"
    path.write_text(json.dumps(data))
    return path


class TestClusterModule:
    """Test TNG-Cluster entropy-structure correlation module."""

    def test_load_data(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        # 4 mass bins
        assert module.n_data == 4
        assert len(module.coordinates) == 4
        assert len(module.observed) == 4
        assert len(module.errors) == 4

    def test_correlations_negative(self, tmp_path):
        """All mass-binned correlations should be negative (TNG result)."""
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        assert np.all(module.observed < 0)

    def test_n_halos(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        assert module.get_n_halos() == 352

    def test_sign_flip_evidence(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        sf = module.get_sign_flip_evidence()
        assert sf["tng_cluster_rho"] == pytest.approx(-0.872)
        assert sf["accept_rho"] == pytest.approx(0.36)
        assert sf["sign_reversal"] is True

    def test_global_correlation(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        gc = module.get_global_correlation()
        assert gc["rho"] == pytest.approx(-0.872)
        assert gc["N"] == 352

    def test_ks_test(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        ks = module.get_ks_test()
        assert ks["D_statistic"] == pytest.approx(1.000)

    def test_cool_core_population(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        cc = module.get_cool_core_population()
        assert cc["SCC"]["count"] == 28
        assert cc["WCC"]["count"] == 206
        assert cc["NCC"]["count"] == 118

    def test_predict_self_consistent(self, tmp_path):
        """Predict should return observed (self-consistent placeholder)."""
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        pred = module.predict({})
        np.testing.assert_array_almost_equal(pred, module.observed)

    def test_log_likelihood_self_consistent(self, tmp_path):
        """Self-consistent prediction should give χ²=0 → max likelihood."""
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        ll = module.log_likelihood({})
        assert np.isfinite(ll)
        # Self-consistent → zero residuals → ll = -0.5 * sum(log(2π σ²))
        # This is the normalization constant, should be finite and negative or small positive
        # The key test: χ² contribution is 0, only normalization remains
        expected_norm = -0.5 * np.sum(np.log(2 * np.pi * module.errors**2))
        assert ll == pytest.approx(expected_norm, rel=1e-6)

    def test_mass_controlled(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        mc = module.get_mass_controlled_correlation()
        assert "partial_ne_slope_K0_given_M" in mc

    def test_summary(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ClusterModule()
        module.load_data(data_path=str(json_path))

        s = module.summary()
        assert s["name"] == "cluster"
        assert s["n_halos"] == 352
        assert s["tng_rho"] == pytest.approx(-0.872)
        assert s["accept_rho"] == pytest.approx(0.36)
        assert s["sign_reversal"] is True
        assert s["ks_D"] == pytest.approx(1.0)

    def test_file_not_found(self):
        module = ClusterModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/tng.json")

    def test_not_loaded_raises(self):
        module = ClusterModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict({})

    @pytest.mark.skipif(not TNG_JSON.exists(),
                        reason="TNG cluster data not available")
    def test_real_tng_data(self):
        """Load actual TNG cluster data if available."""
        module = ClusterModule()
        module.load_data(data_path=str(TNG_JSON))

        assert module.n_data == 4  # 4 mass bins
        assert module.get_n_halos() == 352
        assert np.all(module.observed < 0)

        sf = module.get_sign_flip_evidence()
        assert sf["sign_reversal"] is True

        ll = module.log_likelihood({})
        assert np.isfinite(ll)
