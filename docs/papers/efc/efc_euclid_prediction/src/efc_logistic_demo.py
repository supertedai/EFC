"""
EFC Logistic Entropy Field — Reference Implementation

Implements the EFC logistic gravity model used for Euclid DR1
pre-registration predictions. This is the same model patched into
hi_class as the 'efc_logistic' gravity_model.

Benchmark: B0=0.02, M0=0.06, a_t=0.3, Delta=0.3
SHA-256: dbc737979d8a773f56c620759ddded38139157fd9a2dbb321a8ffdb6e68135d2
"""

import numpy as np


class EFCLogistic:
    """EFC logistic entropy field with Horndeski alpha mapping.

    Parameters
    ----------
    B0 : float
        Braiding amplitude (alpha_B = B0 * dS/dlna)
    M0 : float
        Planck mass running amplitude (alpha_M = M0 * S(a))
    a_t : float
        Entropy transition scale factor
    Delta : float
        Transition sharpness in ln(a) space
    alpha_K : float
        Kineticity (constant, for ghost stability)
    """

    def __init__(self, B0=0.02, M0=0.06, a_t=0.3, Delta=0.3, alpha_K=1.0):
        self.B0 = B0
        self.M0 = M0
        self.a_t = a_t
        self.Delta = Delta
        self.alpha_K = alpha_K

    def S(self, a):
        """Logistic entropy field S(a) = 1/(1+exp(-(ln a - ln a_t)/Delta))"""
        a = np.asarray(a, dtype=float)
        x = (np.log(a) - np.log(self.a_t)) / self.Delta
        return np.where(x > 20, 1.0, np.where(x < -20, 0.0,
                        1.0 / (1.0 + np.exp(-x))))

    def dS_dlna(self, a):
        """dS/d(ln a) — peaks at a = a_t"""
        s = self.S(a)
        return s * (1 - s) / self.Delta

    def alpha_M(self, a):
        """Planck mass running: alpha_M = M0 * S(a)"""
        return self.M0 * self.S(a)

    def alpha_B(self, a):
        """Braiding: alpha_B = B0 * dS/dlna"""
        return self.B0 * self.dS_dlna(a)

    def M2(self, a):
        """Planck mass squared M*2(a), computed analytically.

        ln(M*2) = M0 * Delta * log(1 + exp((ln a - ln a_t)/Delta))
        """
        a = np.asarray(a, dtype=float)
        x = (np.log(a) - np.log(self.a_t)) / self.Delta
        log1p_exp = np.where(x > 20, x, np.where(x < -20, 0.0,
                             np.log(1 + np.exp(x))))
        return np.exp(self.M0 * self.Delta * log1p_exp)

    def stability_check(self):
        """Check stability conditions across all epochs."""
        a_arr = np.linspace(0.01, 1.0, 1000)
        aB = self.alpha_B(a_arr)
        D = self.alpha_K + 1.5 * aB**2
        return {
            "D_min": float(D.min()),
            "D_positive": bool(np.all(D > 0)),
            "M0_B0_ratio": self.M0 / self.B0 if self.B0 > 0 else float('inf'),
            "ratio_ge_3": (self.M0 / self.B0 >= 3) if self.B0 > 0 else True,
        }


# Benchmark values
BENCHMARK = {
    "B0": 0.02,
    "M0": 0.06,
    "a_t": 0.3,
    "Delta": 0.3,
    "alpha_K": 1.0,
    "alpha_T": 0.0,
    "predictions": {
        "dsigma8_pct": 1.207,
        "dPk_kc_z05_pct": 2.091,
        "dClpp_ell66_pct": -6.012,
        "dEG_ell66_pct": -3.981,
        "dClTT_ell30_pct": 1.875,
    },
    "sha256": "dbc737979d8a773f56c620759ddded38139157fd9a2dbb321a8ffdb6e68135d2",
}


if __name__ == "__main__":
    model = EFCLogistic(**{k: BENCHMARK[k] for k in ["B0", "M0", "a_t", "Delta", "alpha_K"]})

    print("EFC Logistic Entropy Field — Benchmark")
    print("=" * 50)
    for a, z in [(0.1, 9.0), (0.3, 2.3), (0.5, 1.0), (1.0, 0.0)]:
        print(f"  a={a:.1f} (z={z:.1f}): S={model.S(a):.4f}, "
              f"alpha_M={model.alpha_M(a):.4f}, alpha_B={model.alpha_B(a):.4f}, "
              f"M*2={model.M2(a):.4f}")

    stab = model.stability_check()
    print(f"\nStability: D_min={stab['D_min']:.4f}, D>0={stab['D_positive']}, "
          f"M0/B0={stab['M0_B0_ratio']:.1f}>=3: {stab['ratio_ge_3']}")
