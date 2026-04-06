"""
EFC-C v2.0: Cognitive Entropy Gradients -- Core Implementation

Centrifugal entropy score kappa and connectome-constrained predictions.

Key equation:
    kappa_healthy = C / (1 + lambda_2(W) * tau_c)

where C = 4.4 +/- 0.6 from SPARC galactic dynamics (no neural fitting).

Author: Morten Magnusson
"""

import math


class CentrifugalEntropyScore:
    """Centrifugal entropy score kappa = <S_hub> / <S_periph>.

    Captures the directional structure of entropy flow across the connectome.

    Parameters
    ----------
    S_hub : list of float
        Entropy values for hub regions (top 10% by weighted degree).
    S_periph : list of float
        Entropy values for peripheral regions (bottom 30% by weighted degree).
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
        """Centrifugal entropy score."""
        return self.mean_S_hub / self.mean_S_periph

    def interpret(self):
        """Interpret the kappa value.

        Returns
        -------
        str : 'centrifugal' (healthy), 'flat', or 'centripetal' (pathological)
        """
        k = self.kappa
        if k > 1.1:
            return "centrifugal"
        elif k < 0.9:
            return "centripetal"
        else:
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


class BridgeB1Star:
    """Bridge B1* equation: kappa = C / (1 + lambda_2 * tau_c).

    Cross-domain prediction from galactic dynamics to neural entropy.
    No parameters are fit to neural data.

    Parameters
    ----------
    C : float
        Cross-domain constant k/a_G = 4.4 +/- 0.6 from SPARC.
    C_uncertainty : float
        Uncertainty on C.
    """

    def __init__(self, C=4.4, C_uncertainty=0.6):
        self.C = C
        self.C_uncertainty = C_uncertainty

    def kappa(self, lambda_2, tau_c):
        """Predict kappa from connectome parameters.

        Parameters
        ----------
        lambda_2 : float
            Fiedler eigenvalue of the normalized graph Laplacian.
        tau_c : float
            Cortical entropy redistribution timescale [seconds].

        Returns
        -------
        float : predicted kappa
        """
        return self.C / (1.0 + lambda_2 * tau_c)

    def kappa_range(self, lambda_2, tau_c):
        """Predict kappa with uncertainty bounds.

        Returns
        -------
        tuple : (kappa_low, kappa_central, kappa_high)
        """
        central = self.kappa(lambda_2, tau_c)
        low = (self.C - self.C_uncertainty) / (1.0 + lambda_2 * tau_c)
        high = (self.C + self.C_uncertainty) / (1.0 + lambda_2 * tau_c)
        return (low, central, high)

    def delta_kappa(self, lambda_2_healthy, lambda_2_disorder, tau_c):
        """Predict disorder-specific kappa shift.

        Delta_kappa = C * [1/(1 + l2_h * tau) - 1/(1 + l2_d * tau)]
        """
        k_h = self.kappa(lambda_2_healthy, tau_c)
        k_d = self.kappa(lambda_2_disorder, tau_c)
        return k_h - k_d

    def kappa_table(self):
        """Reproduce Table from paper (Section 3.1).

        Returns
        -------
        list of dict
        """
        cases = [
            {"lambda_2": 0.3, "tau_c": 2.0},
            {"lambda_2": 0.5, "tau_c": 3.5},
            {"lambda_2": 0.8, "tau_c": 5.0},
        ]
        results = []
        for c in cases:
            k = self.kappa(c["lambda_2"], c["tau_c"])
            results.append({**c, "kappa_pred": round(k, 2)})
        return results


class ConnectomeParameters:
    """Structural connectome parameters for kappa prediction.

    Parameters
    ----------
    lambda_2 : float
        Fiedler eigenvalue of the normalized graph Laplacian.
    n_regions : int
        Number of parcellation regions (e.g. 360 for HCP MMP1.0).
    hub_percentile : float
        Top percentile for hub classification (default 10).
    periph_percentile : float
        Bottom percentile for peripheral classification (default 30).
    """

    def __init__(self, lambda_2=0.5, n_regions=360,
                 hub_percentile=10.0, periph_percentile=30.0):
        self.lambda_2 = lambda_2
        self.n_regions = n_regions
        self.hub_percentile = hub_percentile
        self.periph_percentile = periph_percentile

    @property
    def n_hub(self):
        """Number of hub regions."""
        return max(1, int(self.n_regions * self.hub_percentile / 100.0))

    @property
    def n_periph(self):
        """Number of peripheral regions."""
        return max(1, int(self.n_regions * self.periph_percentile / 100.0))

    def tau_c(self, L_parcel_mm=5.0, D_eff_mm_per_s=3.0):
        """Compute cortical entropy redistribution timescale.

        tau_c = L_parcel^2 / D_eff

        Parameters
        ----------
        L_parcel_mm : float
            Characteristic parcel size [mm].
        D_eff_mm_per_s : float
            Effective diffusion coefficient [mm/s].

        Returns
        -------
        float : tau_c in seconds
        """
        return L_parcel_mm ** 2 / D_eff_mm_per_s

    def info(self):
        return {
            "lambda_2": self.lambda_2,
            "n_regions": self.n_regions,
            "n_hub": self.n_hub,
            "n_periph": self.n_periph,
            "tau_c_s": self.tau_c(),
        }


class DisorderPrediction:
    """Disorder-specific kappa and alpha_AP predictions.

    Extends Bridge B1* to psychiatric populations.
    """

    # Published structural connectome findings
    DISORDERS = {
        "healthy": {
            "lambda_2": 0.5,
            "description": "Baseline connectivity",
            "predicted_kappa_direction": None,
            "alpha_AP_direction": None,
        },
        "schizophrenia": {
            "lambda_2": 0.35,
            "description": "Reduced frontotemporal connectivity",
            "predicted_kappa_direction": "elevated (paradoxical, reduced short-circuiting)",
            "alpha_AP_direction": "elevated (anterior-dominant entropy elevation)",
        },
        "MDD": {
            "lambda_2": 0.40,
            "description": "Reduced global efficiency",
            "predicted_kappa_direction": "elevated (similar to SCZ, different magnitude)",
            "alpha_AP_direction": "reduced (posterior-shifted entropy)",
        },
    }

    def __init__(self, bridge=None):
        self.bridge = bridge or BridgeB1Star()

    def predict(self, disorder, tau_c=3.5):
        """Predict kappa for a given disorder.

        Parameters
        ----------
        disorder : str
            One of 'healthy', 'schizophrenia', 'MDD'.
        tau_c : float
            Cortical redistribution timescale [s].

        Returns
        -------
        dict
        """
        if disorder not in self.DISORDERS:
            raise ValueError(f"Unknown disorder: {disorder}")

        d = self.DISORDERS[disorder]
        kappa = self.bridge.kappa(d["lambda_2"], tau_c)
        healthy_kappa = self.bridge.kappa(self.DISORDERS["healthy"]["lambda_2"], tau_c)

        return {
            "disorder": disorder,
            "lambda_2": d["lambda_2"],
            "kappa_predicted": round(kappa, 3),
            "delta_kappa": round(healthy_kappa - kappa, 3) if disorder != "healthy" else 0.0,
            "description": d["description"],
            "alpha_AP_direction": d["alpha_AP_direction"],
        }

    def discrimination_test(self, tau_c=3.5):
        """Test if alpha_AP can discriminate schizophrenia from MDD.

        Q2a: alpha_AP_scz > alpha_AP_healthy
        Q2b: alpha_AP_mdd < alpha_AP_healthy

        Returns
        -------
        dict with predictions for each disorder
        """
        results = {}
        for disorder in self.DISORDERS:
            results[disorder] = self.predict(disorder, tau_c)
        return results


class CognitiveCoherenceThreshold:
    """Entropy threshold for cognitive coherence (Prediction Q3).

    kappa_crit = C / (1 + lambda_2_max * tau_c_max)

    When kappa < kappa_crit, the centrifugal gradient is lost,
    corresponding to disorders of consciousness.
    """

    def __init__(self, C=4.4, lambda_2_max=1.0, tau_c_max=5.0):
        self.C = C
        self.lambda_2_max = lambda_2_max
        self.tau_c_max = tau_c_max

    @property
    def kappa_crit(self):
        """Critical kappa threshold."""
        return self.C / (1.0 + self.lambda_2_max * self.tau_c_max)

    def evaluate(self, kappa_observed):
        """Evaluate whether observed kappa is below critical threshold.

        Parameters
        ----------
        kappa_observed : float

        Returns
        -------
        dict
        """
        below = kappa_observed < self.kappa_crit
        return {
            "kappa_observed": kappa_observed,
            "kappa_crit": round(self.kappa_crit, 4),
            "below_threshold": below,
            "interpretation": "disrupted_gradient" if below else "maintained_gradient",
        }


class EFCC_Framework:
    """Complete EFC-C v2 prediction framework.

    Combines centrifugal entropy score, Bridge B1*, connectome parameters,
    disorder predictions, and cognitive coherence threshold.
    """

    def __init__(self, C=4.4, C_uncertainty=0.6):
        self.bridge = BridgeB1Star(C, C_uncertainty)
        self.threshold = CognitiveCoherenceThreshold(C)
        self.disorders = DisorderPrediction(self.bridge)

    def predict_healthy(self, lambda_2=0.5, tau_c=3.5):
        """Prediction Q1: healthy resting-state kappa."""
        kappa = self.bridge.kappa(lambda_2, tau_c)
        kappa_range = self.bridge.kappa_range(lambda_2, tau_c)
        return {
            "prediction": "Q1",
            "lambda_2": lambda_2,
            "tau_c": tau_c,
            "kappa_predicted": round(kappa, 3),
            "kappa_range": [round(x, 3) for x in kappa_range],
        }

    def predict_disorders(self, tau_c=3.5):
        """Prediction Q2: disorder-specific shifts."""
        return self.disorders.discrimination_test(tau_c)

    def predict_coherence(self, kappa_observed):
        """Prediction Q3: cognitive coherence threshold."""
        return self.threshold.evaluate(kappa_observed)

    def full_report(self, lambda_2=0.5, tau_c=3.5):
        """Complete prediction report."""
        return {
            "Q1_healthy": self.predict_healthy(lambda_2, tau_c),
            "Q2_disorders": self.predict_disorders(tau_c),
            "Q3_coherence_threshold": self.threshold.kappa_crit,
            "kappa_table": self.bridge.kappa_table(),
        }
