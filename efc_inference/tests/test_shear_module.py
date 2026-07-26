"""Tests for KiDS-1000 weak-lensing shear module."""

import json
import numpy as np
import pytest
from pathlib import Path

from efc_inference.modules.shear_module import (
    ShearModule, _LensingResponseEngine
)


# ── Test data path ────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent.parent / "data" / "lensing"
KIDS_JSON = DATA_DIR / "kids1000_results.json"


def _create_minimal_json(tmpdir: Path) -> Path:
    """Create a minimal KiDS-1000-format JSON for testing."""
    data = {
        "fit_results": {
            "best_fit_parameters": {
                "alpha": {"value": 0.10},
                "k_trans": {"value": 0.1},
                "z_activ": {"value": 0.5},
                "delta_k": {"value": 0.05},
            }
        },
        "likelihood_analysis": {
            "delta_chi2": -50.9,
            "n_data_points": 770,
            "delta_AIC": -44.9,
            "delta_BIC": -31.0,
        },
        "s8_tension_analysis": {
            "standard_comparison": {
                "kids1000": {"s8": 0.759, "error": 0.024},
                "planck": {"s8": 0.834, "error": 0.016},
                "tension_sigma": 2.6,
            },
            "reframed_analysis": {
                "s_wl_reframed": 0.829,
                "comparison_to_planck": {
                    "tension_sigma": 0.3,
                },
            },
        },
        "tomographic_fingerprint": {
            "low_z_bins": {"improvement_factor": 3.2},
            "high_z_bins": {"improvement_factor": 0.4},
        },
        "sigma_values": {
            "2d_grid": {
                "k_values_h_per_Mpc": [0.05, 0.1, 0.2, 0.3],
                "z_values": [0.0, 0.3, 0.5, 1.0],
                "sigma_matrix": [
                    [1.081, 1.049, 1.017, 0.983],
                    [1.100, 1.060, 1.020, 1.000],
                    [1.184, 1.110, 1.036, 1.076],
                    [1.210, 1.126, 1.041, 1.100],
                ],
            }
        },
    }
    path = tmpdir / "kids1000_test.json"
    path.write_text(json.dumps(data))
    return path


class TestLensingResponseEngine:
    """Test the parametric Σ(k,z) fallback engine."""

    def test_unity_at_high_z(self):
        """Σ should approach 1 at z >= z_activ."""
        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        k = np.array([0.3, 0.3, 0.3])
        z = np.array([0.5, 0.7, 1.0])
        sigma = _LensingResponseEngine.compute_sigma(params, k, z)
        np.testing.assert_allclose(sigma, 1.0, atol=0.01)

    def test_above_unity_at_low_z(self):
        """Σ > 1 at z=0, k > k_trans."""
        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        k = np.array([0.3])
        z = np.array([0.0])
        sigma = _LensingResponseEngine.compute_sigma(params, k, z)
        assert sigma[0] > 1.0

    def test_near_unity_at_low_k(self):
        """Σ ≈ 1 at k << k_trans regardless of z."""
        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        k = np.array([0.001, 0.001])
        z = np.array([0.0, 0.3])
        sigma = _LensingResponseEngine.compute_sigma(params, k, z)
        np.testing.assert_allclose(sigma, 1.0, atol=0.02)

    def test_alpha_zero_gives_unity(self):
        """α=0 means no modification: Σ=1 everywhere."""
        params = {"alpha_lens": 0.0, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        k = np.linspace(0.01, 1.0, 20)
        z = np.linspace(0.0, 1.0, 20)
        sigma = _LensingResponseEngine.compute_sigma(params, k, z)
        np.testing.assert_allclose(sigma, 1.0, atol=1e-10)

    def test_monotonic_in_k(self):
        """At fixed z=0, Σ should increase monotonically with k."""
        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        k = np.linspace(0.01, 1.0, 50)
        z = np.zeros(50)
        sigma = _LensingResponseEngine.compute_sigma(params, k, z)
        # Should be monotonically non-decreasing
        assert np.all(np.diff(sigma) >= -1e-10)

    def test_default_params(self):
        """Should work with empty params_dict (uses defaults)."""
        sigma = _LensingResponseEngine.compute_sigma(
            {}, np.array([0.3]), np.array([0.0])
        )
        assert np.isfinite(sigma[0])
        assert sigma[0] > 1.0


class TestShearModule:
    """Test KiDS-1000 shear module."""

    def test_load_data(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        # 4 k × 4 z = 16 grid points
        assert module.n_data == 16
        assert module.coordinates.shape == (16, 2)
        assert len(module.observed) == 16
        assert len(module.errors) == 16

    def test_sigma_values_in_range(self, tmp_path):
        """All Σ values should be in [0.9, 1.3]."""
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        assert np.all(module.observed >= 0.9)
        assert np.all(module.observed <= 1.3)

    def test_errors_positive(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        assert np.all(module.errors > 0)

    def test_predict_finite(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        pred = module.predict(params)
        assert len(pred) == 16
        assert np.all(np.isfinite(pred))

    def test_log_likelihood_finite(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        params = {"alpha_lens": 0.10, "k_trans": 0.1,
                  "z_activ": 0.5, "delta_k": 0.05}
        ll = module.log_likelihood(params)
        assert np.isfinite(ll)

    def test_delta_chi2(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        assert module.get_delta_chi2() == pytest.approx(-50.9)

    def test_s8_reframing(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        s8 = module.get_s8_reframing()
        assert "standard_comparison" in s8
        assert "reframed_analysis" in s8
        assert s8["standard_comparison"]["tension_sigma"] == 2.6
        assert s8["reframed_analysis"]["comparison_to_planck"]["tension_sigma"] == 0.3

    def test_best_fit_params(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        bp = module.get_best_fit_params()
        assert bp["alpha"] == 0.10
        assert bp["k_trans"] == 0.1

    def test_summary(self, tmp_path):
        json_path = _create_minimal_json(tmp_path)
        module = ShearModule()
        module.load_data(data_path=str(json_path))

        s = module.summary()
        assert s["name"] == "shear"
        assert s["n_data"] == 16
        assert s["delta_chi2"] == -50.9
        assert s["s8_tension_before"] == 2.6
        assert s["s8_tension_after"] == 0.3

    def test_file_not_found(self):
        module = ShearModule()
        with pytest.raises(FileNotFoundError):
            module.load_data(data_path="/nonexistent/kids.json")

    def test_not_loaded_raises(self):
        module = ShearModule()
        with pytest.raises(RuntimeError, match="load_data"):
            module.predict({"alpha_lens": 0.1})

    @pytest.mark.skipif(not KIDS_JSON.exists(),
                        reason="KiDS-1000 data not available")
    def test_real_kids_data(self):
        """Load actual KiDS-1000 data if available."""
        module = ShearModule()
        module.load_data(data_path=str(KIDS_JSON))

        assert module.n_data == 16  # 4k × 4z
        assert np.all(module.observed >= 0.9)
        assert np.all(module.observed <= 1.3)
        assert module.get_delta_chi2() == pytest.approx(-50.9)

        # Best-fit params should give reasonable likelihood
        params = module.get_best_fit_params()
        params_dict = {
            "alpha_lens": params.get("alpha", 0.10),
            "k_trans": params.get("k_trans", 0.10),
            "z_activ": params.get("z_activ", 0.50),
            "delta_k": params.get("delta_k", 0.05),
        }
        ll = module.log_likelihood(params_dict)
        assert np.isfinite(ll)
