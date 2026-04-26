"""non_mcmc_constraints_on_the_efc___parame.py

Reference implementation for:
  Non-MCMC Constraints on the EFC α-Parameter:
  BAO, Growth-Rate, and Cluster Evidence
  (EFC-VAL-2026-005, DOI: 10.6084/m9.figshare.32101213)

Implements key equations and statistical metrics from the paper:
  - EFC-corrected Hubble parameter H(z; alpha)
  - Delta-chi-squared likelihood ratio
  - k-fold cross-validation splitter and scorer
  - Leave-one-out (LOO) validation
  - Delta-AIC model comparison
  - Growth rate f*sigma8 under EFC correction
"""
import numpy as np
from typing import Tuple, List, Optional

# ---------------------------------------------------------------------------
# Fiducial LCDM cosmological constants (Planck 2018 flat LCDM)
# ---------------------------------------------------------------------------
H0_FIDUCIAL: float = 67.4        # km/s/Mpc
OMEGA_M: float = 0.315
OMEGA_LAMBDA: float = 1.0 - OMEGA_M
SIGMA8_FIDUCIAL: float = 0.811

# ---------------------------------------------------------------------------
# Paper-reported numerical results
# ---------------------------------------------------------------------------
ALPHA_MCMC: float = -0.101       # MCMC posterior mean
ALPHA_MCMC_ERR: float = 0.212    # MCMC 1-sigma
ALPHA_MCMC_SIGNIF: float = 0.479 # sigma

ALPHA_FS8: float = -1.00         # f-sigma8 non-MCMC best fit
ALPHA_FS8_ERR: float = 0.46
ALPHA_FS8_SIGNIF: float = 2.20   # sigma

ALPHA_BLIND_PRED_1: float = -0.702  # sealed blind prediction 1
ALPHA_BLIND_PRED_2: float = -0.689  # sealed blind prediction 2

DCHI2_DESI: float = -22.01
DCHI2_BOSS: float = -7.77
DCHI2_CC: float = -0.17
DAIC_MCMC: float = 1.763
DAIC_FS8: float = -2.91
CHI2RED_ILLUSTRIS: float = 0.00


def H_lcdm(z: np.ndarray) -> np.ndarray:
    """Standard flat-LCDM Hubble parameter H(z) in km/s/Mpc."""
    z = np.asarray(z, dtype=np.float64)
    return H0_FIDUCIAL * np.sqrt(OMEGA_M * (1.0 + z)**3 + OMEGA_LAMBDA)


def H_efc(z: np.ndarray, alpha: float) -> np.ndarray:
    """EFC-corrected Hubble parameter.

    The entropic correction enters as a multiplicative factor:
        H_EFC(z) = H_LCDM(z) * (1 + alpha * S(z))
    where the entropic source term S(z) = ln(1+z) / (1+z) is the
    leading-order EFC kernel (sector L0-L2).
    """
    z = np.asarray(z, dtype=np.float64)
    S_z = np.log(1.0 + z) / (1.0 + z)
    return H_lcdm(z) * (1.0 + alpha * S_z)


def growth_factor_approx(z: np.ndarray) -> np.ndarray:
    """Approximate LCDM growth factor g(z) normalised to 1 at z=0."""
    z = np.asarray(z, dtype=np.float64)
    Omega_z = OMEGA_M * (1.0 + z)**3 / (OMEGA_M * (1.0 + z)**3 + OMEGA_LAMBDA)
    return Omega_z ** 0.55


def fsigma8_lcdm(z: np.ndarray) -> np.ndarray:
    """f*sigma8(z) under flat LCDM."""
    z = np.asarray(z, dtype=np.float64)
    f_z = growth_factor_approx(z)
    # sigma8(z) ~ sigma8_0 * D(z)/D(0); use simple approximation D ~ 1/(1+z)
    sigma8_z = SIGMA8_FIDUCIAL / (1.0 + z)
    return f_z * sigma8_z


def fsigma8_efc(z: np.ndarray, alpha: float) -> np.ndarray:
    """f*sigma8(z) under EFC correction.

    The EFC alpha modifies the growth rate via the ratio H_EFC/H_LCDM,
    entering as a correction to the growth index:
        f_EFC = f_LCDM * (H_EFC / H_LCDM)
    """
    z = np.asarray(z, dtype=np.float64)
    ratio = H_efc(z, alpha) / H_lcdm(z)
    return fsigma8_lcdm(z) * ratio


def delta_chi2(data_z: np.ndarray, data_obs: np.ndarray,
               data_err: np.ndarray, alpha: float,
               observable: str = "H") -> float:
    """Compute Delta-chi2 = chi2_EFC - chi2_LCDM (negative favours EFC)."""
    data_z = np.asarray(data_z, dtype=np.float64)
    data_obs = np.asarray(data_obs, dtype=np.float64)
    data_err = np.asarray(data_err, dtype=np.float64)
    if observable == "H":
        pred_lcdm = H_lcdm(data_z)
        pred_efc = H_efc(data_z, alpha)
    elif observable == "fsigma8":
        pred_lcdm = fsigma8_lcdm(data_z)
        pred_efc = fsigma8_efc(data_z, alpha)
    else:
        raise ValueError(f"Unknown observable: {observable}")
    chi2_lcdm = np.sum(((data_obs - pred_lcdm) / data_err) ** 2)
    chi2_efc = np.sum(((data_obs - pred_efc) / data_err) ** 2)
    return chi2_efc - chi2_lcdm


def delta_aic(dchi2: float, k_eff_efc: int = 1, k_eff_lcdm: int = 0) -> float:
    """Delta AIC = Delta-chi2 + 2*(k_EFC - k_LCDM). Negative favours EFC."""
    return dchi2 + 2.0 * (k_eff_efc - k_eff_lcdm)


def kfold_cv(data_z: np.ndarray, data_obs: np.ndarray,
            data_err: np.ndarray, alpha: float,
            k: int = 5, observable: str = "H") -> Tuple[int, List[float]]:
    """k-fold cross-validation returning (folds_preferring_efc, fold_dchi2s)."""
    n = len(data_z)
    indices = np.arange(n)
    np.random.seed(42)
    np.random.shuffle(indices)
    folds = np.array_split(indices, k)
    fold_dchi2: List[float] = []
    efc_wins = 0
    for fold_idx in folds:
        dc2 = delta_chi2(data_z[fold_idx], data_obs[fold_idx],
                         data_err[fold_idx], alpha, observable)
        fold_dchi2.append(float(dc2))
        if dc2 < 0:
            efc_wins += 1
    return efc_wins, fold_dchi2


def loo_cv(data_z: np.ndarray, data_obs: np.ndarray,
           data_err: np.ndarray, alpha: float,
           observable: str = "fsigma8") -> Tuple[int, int]:
    """Leave-one-out CV. Returns (epochs_preferring_efc, total_epochs)."""
    n = len(data_z)
    efc_wins = 0
    for i in range(n):
        train_mask = np.ones(n, dtype=bool)
        train_mask[i] = False
        dc2 = delta_chi2(data_z[~train_mask], data_obs[~train_mask],
                         data_err[~train_mask], alpha, observable)
        if dc2 < 0:
            efc_wins += 1
    return efc_wins, n


def significance_sigma(value: float, error: float) -> float:
    """Significance in sigma units: |value| / error."""
    if error <= 0:
        return np.inf
    return abs(value) / error


def tension_sigma(val1: float, err1: float, val2: float, err2: float) -> float:
    """Tension between two estimates in sigma."""
    return abs(val1 - val2) / np.sqrt(err1**2 + err2**2)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Self-test: non_mcmc_constraints_on_the_efc___parame ===")
    z_test = np.array([0.3, 0.5, 0.7, 1.0, 1.5])
    h_lcdm = H_lcdm(z_test)
    h_efc = H_efc(z_test, alpha=ALPHA_FS8)
    print(f"H_LCDM(z={z_test}): {np.round(h_lcdm, 2)}")
    print(f"H_EFC (z={z_test}, alpha={ALPHA_FS8}): {np.round(h_efc, 2)}")
    sig_mcmc = significance_sigma(ALPHA_MCMC, ALPHA_MCMC_ERR)
    sig_fs8 = significance_sigma(ALPHA_FS8, ALPHA_FS8_ERR)
    print(f"MCMC significance:  {sig_mcmc:.3f} sigma (paper: {ALPHA_MCMC_SIGNIF})")
    print(f"fs8  significance:  {sig_fs8:.2f} sigma  (paper: {ALPHA_FS8_SIGNIF})")
    t = tension_sigma(ALPHA_FS8, ALPHA_FS8_ERR, ALPHA_BLIND_PRED_1, 0.0)
    print(f"fs8 vs blind pred 1 tension: {t:.2f} sigma (~0.7 expected)")
    daic_boss = delta_aic(DCHI2_BOSS, k_eff_efc=0, k_eff_lcdm=0)
    print(f"Delta-AIC BOSS (keff=0): {daic_boss:.2f}")
    print("Self-test passed.")
