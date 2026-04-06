"""
EFC Cosmic Dipole — Core Implementation

Regime-dependent isotropy: entropy gradient ∇S produces an intrinsic
galaxy number count dipole via direction-dependent G_eff(S).

DOI: 10.6084/m9.figshare.31942731
Author: Morten Magnusson
"""

import numpy as np

# Constants
C_KMS = 299792.458  # Speed of light [km/s]
V_PECULIAR = 370.0  # Peculiar velocity [km/s]
MU_0 = 0.415        # SPARC-calibrated coupling (EFC Screening)


class KinematicDipole:
    """Standard kinematic dipole from peculiar velocity.

    D_kin ≈ 2v/c (aberration + Doppler boosting combined).
    """

    def __init__(self, v_peculiar=V_PECULIAR):
        self.v_peculiar = v_peculiar

    def amplitude(self):
        """Kinematic dipole amplitude D_kin = 2v/c."""
        return 2.0 * self.v_peculiar / C_KMS

    def info(self):
        return {
            "v_peculiar_km_s": self.v_peculiar,
            "D_kinematic": self.amplitude(),
            "mechanism": "Aberration + Doppler boosting",
        }


class EntropyGradient:
    """Large-scale entropy gradient mechanism (Eq. 2).

    ΔG_eff(n̂) ≈ G_N μ₀ f'(S̄) (∇S · n̂) L_grad

    Parameters
    ----------
    grad_S_over_S : float
        Fractional entropy gradient |∇S| L_grad / S̄.
    f_prime : float
        Derivative of enhancement function |f'(S̄)| (~ 1 near transition).
    mu_0 : float
        SPARC-calibrated coupling constant.
    """

    def __init__(self, grad_S_over_S=0.023, f_prime=1.0, mu_0=MU_0):
        self.grad_S_over_S = grad_S_over_S
        self.f_prime = f_prime
        self.mu_0 = mu_0

    def delta_G_eff_fractional(self):
        """Fractional change in G_eff along gradient direction.

        ΔG_eff/G_N = μ₀ |f'| |∇S| L_grad / S̄
        """
        return self.mu_0 * self.f_prime * self.grad_S_over_S

    def required_gradient(self, D_excess, b_eff=1.5):
        """Compute required |∇S| L_grad / S̄ for given excess (Eq. 5).

        Parameters
        ----------
        D_excess : float
            Observed dipole excess (D_obs - D_kin).
        b_eff : float
            Effective tracer bias.

        Returns
        -------
        float
            Required fractional entropy gradient.
        """
        return 2.0 * D_excess / (b_eff * self.mu_0 * self.f_prime)

    def variation_percent(self):
        """Entropy variation as percentage of mean."""
        return self.grad_S_over_S * 100.0

    def cmb_consistency(self):
        """Check consistency with CMB isotropy constraint.

        CMB: δT/T ~ 10⁻⁵ at z ~ 1100
        Growth amplification: ~ 10³
        Expected late-time variation: ~ 10⁻² = 1%
        """
        cmb_anisotropy = 1e-5
        growth_factor = 1e3
        expected_late = cmb_anisotropy * growth_factor
        return {
            "cmb_anisotropy": cmb_anisotropy,
            "growth_factor": growth_factor,
            "expected_late_time_variation": expected_late,
            "required_variation": self.grad_S_over_S,
            "consistent": self.grad_S_over_S <= expected_late * 3,
            "ratio": self.grad_S_over_S / expected_late,
        }


class DipoleAmplitude:
    """EFC-predicted dipole amplitude (Eq. 4).

    D_EFC ≈ (b_eff/2) μ₀ |f'(S̄)| |∇S| L_grad / S̄

    Parameters
    ----------
    b_eff : float
        Effective tracer bias.
    mu_0 : float
        SPARC coupling.
    f_prime : float
        |f'(S̄)|.
    grad_S_over_S : float
        Fractional entropy gradient.
    """

    def __init__(self, b_eff=1.5, mu_0=MU_0, f_prime=1.0, grad_S_over_S=0.023):
        self.b_eff = b_eff
        self.mu_0 = mu_0
        self.f_prime = f_prime
        self.grad_S_over_S = grad_S_over_S

    def D_EFC(self):
        """Compute EFC intrinsic dipole amplitude."""
        return (self.b_eff / 2.0) * self.mu_0 * self.f_prime * self.grad_S_over_S

    def D_total(self, v_peculiar=V_PECULIAR):
        """Total predicted dipole = kinematic + EFC."""
        kin = KinematicDipole(v_peculiar)
        return kin.amplitude() + self.D_EFC()

    def scan_bias(self, b_values):
        """Scan D_EFC across different tracer biases."""
        results = []
        for b in b_values:
            self.b_eff = b
            results.append({"b_eff": b, "D_EFC": round(self.D_EFC(), 5),
                           "D_total": round(self.D_total(), 5)})
        return results


class DipoleExcess:
    """Comparison of observed dipole excess with EFC prediction.

    Observations from NVSS, CatWISE2020, WISE-SuperCOSMOS.
    """

    OBSERVATIONS = [
        {"survey": "NVSS", "D_obs": 0.012, "error": 0.003, "tracer": "radio sources"},
        {"survey": "CatWISE2020", "D_obs": 0.0095, "error": 0.002, "tracer": "quasars"},
        {"survey": "WISE-SuperCOSMOS", "D_obs": 0.008, "error": 0.002, "tracer": "galaxies"},
    ]

    def __init__(self):
        self.kin = KinematicDipole()

    def excess(self):
        """Compute excess for each observation."""
        D_kin = self.kin.amplitude()
        results = []
        for obs in self.OBSERVATIONS:
            excess = obs["D_obs"] - D_kin
            ratio = obs["D_obs"] / D_kin
            results.append({
                "survey": obs["survey"],
                "D_obs": obs["D_obs"],
                "D_kin": round(D_kin, 5),
                "D_excess": round(excess, 5),
                "ratio_obs_kin": round(ratio, 2),
                "tracer": obs["tracer"],
            })
        return results

    def mean_excess(self):
        """Mean excess across surveys."""
        excesses = [e["D_excess"] for e in self.excess()]
        return round(np.mean(excesses), 5)


class RegimeDependentIsotropy:
    """Isotropy as regime condition in EFC.

    L0 (CMB): S → S_max, isotropy holds (δT/T ~ 10⁻⁵)
    L1 (background): S(z) homogeneous in Friedmann eq
    L2 (structure): S(x) varies spatially, isotropy broken locally
    """

    REGIMES = [
        {"regime": "L0", "epoch": "CMB (z~1100)", "isotropy": "exact to 10⁻⁵",
         "S_state": "S → S_max (thermal equilibrium)"},
        {"regime": "L1", "epoch": "Cosmological background", "isotropy": "assumed spatially homogeneous",
         "S_state": "S(z) evolves with redshift"},
        {"regime": "L2", "epoch": "Structure-dominated", "isotropy": "broken locally",
         "S_state": "S(x) varies spatially"},
    ]

    def regime_table(self):
        """Return regime isotropy classification."""
        return self.REGIMES

    def key_insight(self):
        return {
            "insight": "L1→L2 transition need not be spatially uniform",
            "consequence": "S(x,z) can inherit a large-scale gradient",
            "mechanism": "∇S → ΔG_eff → directional structure growth → intrinsic dipole",
        }


class Predictions:
    """Predictions P1-P4 and open gaps G1-G4."""

    def p1_redshift_dependence(self):
        return {
            "id": "P1", "description": "Redshift dependence",
            "prediction": "EFC dipole excess grows with decreasing z",
            "contrast": "Kinematic dipole is redshift-independent",
            "test": "Tomographic redshift bins in galaxy count dipole",
        }

    def p2_sigma8_anisotropy(self):
        return {
            "id": "P2", "description": "Correlation with S₈ anisotropy",
            "prediction": "fσ₈ shows directional dependence at ~2% level",
            "test": "Directional fσ₈ from DESI/Euclid",
        }

    def p3_alignment(self):
        return {
            "id": "P3", "description": "Alignment with structure asymmetry",
            "prediction": "EFC dipole aligned with bulk flow and CMB dipole, but amplitude exceeds kinematic",
            "status": "Consistent with observations",
        }

    def p4_scale_dependence(self):
        return {
            "id": "P4", "description": "Scale dependence",
            "prediction": "Excess more pronounced for tracers sampling large volumes",
            "mechanism": "R(k) ∝ k⁻⁴ amplifies at super-cluster scales (k < 0.01 Mpc⁻¹)",
        }

    def open_gaps(self):
        return [
            {"id": "G1", "description": "Origin of ∇S|LSS", "status": "open",
             "candidate": "~10% local supercluster density asymmetry amplified by non-linear μ(S)"},
            {"id": "G2", "description": "Quantitative f(S) profile at super-Hubble scales", "status": "open"},
            {"id": "G3", "description": "Separation from kinematic contribution", "status": "open",
             "method": "Multi-tracer, multi-redshift analysis"},
            {"id": "G4", "description": "CMB isotropy consistency (explicit verification)", "status": "open",
             "plausibility": "Growth factor ~10³ amplifies 10⁻⁵ to ~1%"},
        ]

    def summary(self):
        return {
            "predictions": {"P1": self.p1_redshift_dependence(), "P2": self.p2_sigma8_anisotropy(),
                           "P3": self.p3_alignment(), "P4": self.p4_scale_dependence()},
            "gaps": self.open_gaps(),
            "status": "Working note — logical consistency established, not detection claim",
        }
