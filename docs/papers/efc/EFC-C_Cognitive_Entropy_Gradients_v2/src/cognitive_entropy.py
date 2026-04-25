"""
EFC-C v2.1: Cognitive Entropy Gradients -- Core Implementation

Bridge B1** (degree-heterogeneity formulation):
    kappa = C_eff * D_ratio**gamma

where C_eff = 2.0 +/- 0.15 (regime-transformed cosmological, fixed prior to neural analysis),
gamma = 0.55 +/- 0.05 (one empirical fit parameter), and D_ratio = <k_hub>/<k_periph>.

DOI: 10.6084/m9.figshare.32091700 (v2)

Author: Morten Magnusson
"""

import math


class CentrifugalEntropyScore:
    """Centrifugal entropy score kappa = <S_hub> / <S_periph>.

    Captures the directional structure of entropy flow across the connectome.
    """

    def __init__(self, S_hub, S_periph):
        if not S_hub or not S_periph:
            raise ValueError("Both S_hub and S_periph must be non-empty")
        self.S_hub = list(S_hub)
        self.S_periph = list(S_periph)

    @property
    def mean_S_hub(self):
        return sum(self.S_hub) / len(self.S_hub)

    @property
    def mean_S_periph(self):
        return sum(self.S_periph) / len(self.S_periph)

    @property
    def kappa(self):
        return self.mean_S_hub / self.mean_S_periph

    def interpret(self):
        k = self.kappa
        if k > 1.1:
            return "centrifugal"
        elif k < 0.9:
            return "centripetal"
        return "flat"

    def info(self):
        return {
            "kappa": self.kappa,
            "mean_S_hub": self.mean_S_hub,
            "mean_S_periph": self.mean_S_periph,
            "n_hub": len(self.S_hub),
            "n_periph": len(self.S_periph),
            "interpretation": self.interpret(),
        }


class DegreeRatio:
    """Hub-to-periphery degree ratio D_ratio = <k_hub> / <k_periph>.

    Computed from per-parcel weighted degrees with a top 10% / bottom 30% partition
    by default (PDF v2.1 Sec 2.1).
    """

    def __init__(self, degrees, hub_pct=0.10, periph_pct=0.30):
        if not degrees:
            raise ValueError("degrees must be non-empty")
        sorted_deg = sorted(degrees, reverse=True)
        n = len(sorted_deg)
        n_hub = max(1, int(n * hub_pct))
        n_periph = max(1, int(n * periph_pct))
        self.k_hub = sorted_deg[:n_hub]
        self.k_periph = sorted_deg[-n_periph:]
        self.hub_pct = hub_pct
        self.periph_pct = periph_pct

    @property
    def mean_k_hub(self):
        return sum(self.k_hub) / len(self.k_hub)

    @property
    def mean_k_periph(self):
        return sum(self.k_periph) / len(self.k_periph)

    @property
    def D_ratio(self):
        return self.mean_k_hub / self.mean_k_periph


class BridgeB1DoubleStar:
    """Bridge B1**: kappa = C_eff * D_ratio^gamma.

    Degree-heterogeneity formulation (PDF v2.1 Sec 2.2). Replaces the v2.0 Fiedler
    formulation kappa = C / (1 + lambda_2 * tau_c).

    Parameters
    ----------
    C_eff : float
        Regime-transformed cross-domain constant (default 2.0).
        Fixed prior to neural analysis via RCMP L3->L1 from cosmological C = k/a_G.
    C_eff_uncertainty : float
        Uncertainty on C_eff (default 0.15).
    gamma : float
        Power-law exponent (default 0.55). Constrained to [0.5, 0.6].
        One empirical fit parameter, estimated once from HCP reference sample.
    gamma_uncertainty : float
        Uncertainty on gamma (default 0.05).
    """

    def __init__(self, C_eff=2.0, C_eff_uncertainty=0.15,
                 gamma=0.55, gamma_uncertainty=0.05):
        self.C_eff = C_eff
        self.C_eff_uncertainty = C_eff_uncertainty
        self.gamma = gamma
        self.gamma_uncertainty = gamma_uncertainty

    def kappa(self, D_ratio):
        """Predict kappa from hub-to-periphery degree ratio."""
        return self.C_eff * (D_ratio ** self.gamma)

    def kappa_interval(self, D_ratio, D_ratio_uncertainty=0.15):
        """Predict kappa with EBE-bounded 95% interval [1.7, 2.6] at baseline.

        Returns (low, central, high) using first-order Gaussian propagation
        over (C_eff, gamma, D_ratio).
        """
        central = self.kappa(D_ratio)
        # First-order propagation: dk/dC = D^g, dk/dg = C*D^g*ln(D), dk/dD = C*g*D^(g-1)
        D_pow = D_ratio ** self.gamma
        dk_dC = D_pow
        dk_dg = self.C_eff * D_pow * math.log(D_ratio) if D_ratio > 0 else 0.0
        dk_dD = self.C_eff * self.gamma * (D_ratio ** (self.gamma - 1))
        var = (
            (dk_dC * self.C_eff_uncertainty) ** 2
            + (dk_dg * self.gamma_uncertainty) ** 2
            + (dk_dD * D_ratio_uncertainty) ** 2
        )
        sigma = math.sqrt(var)
        # 95% EBE-bounded ~ 2 sigma
        return (central - 2 * sigma, central, central + 2 * sigma)

    def kappa_table(self):
        """Reproduce v2.1 prediction table for typical D_ratio range."""
        cases = [
            {"D_ratio": 0.9},
            {"D_ratio": 1.0},
            {"D_ratio": 1.2},
            {"D_ratio": 1.5},
        ]
        results = []
        for c in cases:
            k = self.kappa(c["D_ratio"])
            results.append({**c, "kappa_pred": round(k, 3)})
        return results


class LayerAPredictions:
    """Layer A: topological predictions invariant under C_eff."""

    def __init__(self, gamma_central=0.55, gamma_falsification_window=(0.3, 0.8)):
        self.gamma_central = gamma_central
        self.gamma_falsification_window = gamma_falsification_window

    def test_A1(self, fitted_gamma, r_loglog, n=30):
        """Test A1: structural-entropic coupling slope gamma."""
        gmin, gmax = self.gamma_falsification_window
        passes = (gmin <= fitted_gamma <= gmax) and (r_loglog >= 0.50) and (n >= 30)
        return {
            "id": "A1",
            "fitted_gamma": fitted_gamma,
            "r_loglog": r_loglog,
            "n": n,
            "in_falsification_window": gmin <= fitted_gamma <= gmax,
            "passes": passes,
        }

    def test_A2_A3(self, alpha_AP_groups, auc, n_per_group=15):
        """Test A2/A3: alpha_AP discriminates schizophrenia from MDD."""
        passes = (auc >= 0.60) and (n_per_group >= 15)
        return {
            "id": "A2/A3",
            "alpha_AP_groups": alpha_AP_groups,
            "AUC": auc,
            "n_per_group": n_per_group,
            "passes": passes,
        }


class LayerBPredictions:
    """Layer B: absolute-scale predictions conditional on Bridge validity."""

    def __init__(self, kappa_interval=(1.7, 2.6), kappa_crit=1.9, D_ratio_crit=0.9):
        self.kappa_interval = kappa_interval
        self.kappa_crit = kappa_crit
        self.D_ratio_crit = D_ratio_crit

    def test_B1(self, group_mean_kappa, n=20):
        """Test B1: group-mean kappa within EBE-bounded interval."""
        lo, hi = self.kappa_interval
        in_interval = lo <= group_mean_kappa <= hi
        passes = in_interval and (n >= 20)
        return {
            "id": "B1",
            "group_mean_kappa": group_mean_kappa,
            "interval": [lo, hi],
            "in_interval": in_interval,
            "n": n,
            "passes": passes,
        }

    def test_B2(self, kappa_obs, D_ratio_obs):
        """Test B2: critical threshold at degree hierarchy collapse."""
        # Falsified if kappa > 2.0 with maintained D_ratio > 1.15
        falsified = (kappa_obs > 2.0) and (D_ratio_obs > 1.15)
        return {
            "id": "B2",
            "kappa_obs": kappa_obs,
            "D_ratio_obs": D_ratio_obs,
            "kappa_crit": self.kappa_crit,
            "D_ratio_crit": self.D_ratio_crit,
            "falsified": falsified,
            "passes": not falsified,
        }


class EFCC_v21_Framework:
    """Complete EFC-C v2.1 prediction framework (Bridge B1**)."""

    def __init__(self, C_eff=2.0, C_eff_uncertainty=0.15,
                 gamma=0.55, gamma_uncertainty=0.05):
        self.bridge = BridgeB1DoubleStar(
            C_eff=C_eff,
            C_eff_uncertainty=C_eff_uncertainty,
            gamma=gamma,
            gamma_uncertainty=gamma_uncertainty,
        )
        self.layer_a = LayerAPredictions(gamma_central=gamma)
        self.layer_b = LayerBPredictions()

    def predict_healthy(self, D_ratio=1.2, D_ratio_uncertainty=0.15):
        """Layer B prediction B1: healthy resting-state kappa."""
        kappa = self.bridge.kappa(D_ratio)
        lo, mid, hi = self.bridge.kappa_interval(D_ratio, D_ratio_uncertainty)
        return {
            "prediction": "B1",
            "D_ratio": D_ratio,
            "kappa_predicted": round(kappa, 3),
            "kappa_interval_95": [round(lo, 3), round(hi, 3)],
            "kappa_interval_EBE_bounded": [1.7, 2.6],
        }

    def full_report(self, D_ratio=1.2):
        """Complete v2.1 prediction report."""
        return {
            "version": "2.1",
            "doi": "10.6084/m9.figshare.32091700",
            "B1_healthy": self.predict_healthy(D_ratio),
            "kappa_table": self.bridge.kappa_table(),
            "C_eff": self.bridge.C_eff,
            "gamma": self.bridge.gamma,
            "layer_A_predictions": ["A1", "A2", "A3"],
            "layer_B_predictions": ["B1", "B2"],
        }
