"""
Cosmic Shear Likelihood — DES Y3-like for EFC Case B
=====================================================

Cobaya-compatible likelihood that computes shear angular power spectrum
C_ℓ^{γγ}(i,j) from a modified matter power spectrum P_eff(k,z).

Case B specificity: P_eff already contains BOTH growth and lensing
modifications from EFC. The likelihood just computes the observable
(C_ℓ) from the theory (P_eff) and compares to data.

Survey specifications (DES Y3-like, Abbott+ 2022):
    Sky area:    ~4143 deg² (DES Y3 footprint)
    n_eff:       5.59 arcmin⁻² (effective source density)
    sigma_e:     0.26 (intrinsic ellipticity per component)
    4 tomographic bins (z = 0.0–0.36, 0.36–0.63, 0.63–0.87, 0.87–2.0)
    ℓ range:     30–2048 (conservative, avoids baryonic feedback)

For production use, swap the mock data vector with actual DES Y3
two-point data from:
    https://des.ncsa.illinois.edu/releases/y3a2

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-12
"""

import numpy as np
from scipy.interpolate import RectBivariateSpline, interp1d

# =========================================================================
# DES Y3 survey specifications
# =========================================================================

# Tomographic bin edges
ZBIN_EDGES = np.array([0.0, 0.36, 0.63, 0.87, 2.0])
N_ZBINS = len(ZBIN_EDGES) - 1  # 4

# Source redshift distribution n(z) — Smail-type per bin
# n(z) ∝ z^α exp(-(z/z0)^β), fitted to DES Y3 METACALIBRATION
# (Approximation; production should use actual n(z) histograms)
SMAIL_PARAMS = [
    {"alpha": 1.3, "z0": 0.20, "beta": 1.5},  # bin 1
    {"alpha": 1.5, "z0": 0.40, "beta": 1.5},  # bin 2
    {"alpha": 1.5, "z0": 0.55, "beta": 1.5},  # bin 3
    {"alpha": 1.5, "z0": 0.80, "beta": 1.5},  # bin 4
]

SKY_AREA_DEG2 = 4143.0
F_SKY = SKY_AREA_DEG2 / 41253.0  # ~0.1004
N_EFF = 5.59  # arcmin⁻² (total, split across bins)
SIGMA_E = 0.26

# Multipole binning (20 log-spaced bins from ℓ=30 to ℓ=2048)
ELL_MIN = 30
ELL_MAX = 2048
N_ELL = 20


def smail_nz(z, alpha, z0, beta, z_lo, z_hi):
    """Smail-type n(z) confined to [z_lo, z_hi]."""
    mask = (z >= z_lo) & (z < z_hi)
    nz = z ** alpha * np.exp(-(z / z0) ** beta)
    nz *= mask
    return nz


def get_nz_funcs():
    """Return normalized n(z) functions for each tomographic bin."""
    z_fine = np.linspace(0, 3.0, 1000)
    funcs = []
    for i, sp in enumerate(SMAIL_PARAMS):
        nz = smail_nz(z_fine, sp["alpha"], sp["z0"], sp["beta"],
                       ZBIN_EDGES[i], ZBIN_EDGES[i + 1])
        norm = np.trapz(nz, z_fine)
        if norm > 0:
            nz_normed = nz / norm
        else:
            nz_normed = nz
        func = interp1d(z_fine, nz_normed, bounds_error=False, fill_value=0.0)
        funcs.append(func)
    return funcs


# =========================================================================
# Lensing kernel and C_ℓ computation
# =========================================================================

def chi_of_z_flat_lcdm(z, Omega_m=0.3, H0=67.36):
    """Comoving distance χ(z) for flat ΛCDM [Mpc/h]."""
    c_km_s = 299792.458
    z = np.atleast_1d(z)
    result = np.zeros_like(z)
    for i, zi in enumerate(z):
        zz = np.linspace(0, zi, max(int(zi * 200), 50))
        E = np.sqrt(Omega_m * (1 + zz) ** 3 + (1 - Omega_m))
        integrand = 1.0 / E
        result[i] = (c_km_s / H0) * np.trapz(integrand, zz)
    return result


def lensing_efficiency(z_lens, chi_lens, nz_func, Omega_m=0.3, H0=67.36):
    """
    Lensing efficiency kernel W(χ) for a tomographic bin.

    W(χ) = (3/2) Ω_m (H0/c)² (1+z) χ ∫_z^∞ n(z') (χ(z')-χ) / χ(z') dz'
    """
    c_km_s = 299792.458
    prefactor = 1.5 * Omega_m * (H0 / c_km_s) ** 2  # (h/Mpc)²

    W = np.zeros_like(z_lens)
    for i, (zl, cl) in enumerate(zip(z_lens, chi_lens)):
        z_src = np.linspace(zl + 1e-4, 3.0, 150)
        nz_src = nz_func(z_src)
        chi_src = chi_of_z_flat_lcdm(z_src, Omega_m, H0)
        integrand = nz_src * (chi_src - cl) / np.maximum(chi_src, 1e-10)
        W[i] = prefactor * (1 + zl) * cl * np.trapz(integrand, z_src)
    return W


def compute_cl_matrix(ell_array, k_array, z_array, Pk_grid,
                      Omega_m=0.3, H0=67.36):
    """
    Compute C_ℓ^{ij} for all tomographic bin pairs via Limber approximation.

    C_ℓ^{ij} = ∫ W_i(χ) W_j(χ) P(k=ℓ/χ, z(χ)) / χ² dχ

    Parameters
    ----------
    ell_array : array (N_ell,)
    k_array : array (Nk,)
    z_array : array (Nz,)
    Pk_grid : array (Nk, Nz) — P(k,z) [can be ΛCDM or EFC-modified]
    Omega_m, H0 : float

    Returns
    -------
    Cl : dict {(i,j): array (N_ell,)} for i <= j
    """
    # Interpolate P(k,z) on log-k grid
    log_k = np.log(k_array)
    log_Pk = np.log(np.clip(Pk_grid, 1e-30, None))
    Pk_interp = RectBivariateSpline(log_k, z_array, log_Pk)

    # Integration grid
    z_int = np.linspace(0.02, 2.5, 300)
    chi_int = chi_of_z_flat_lcdm(z_int, Omega_m, H0)

    # Compute lensing efficiencies for all bins
    nz_funcs = get_nz_funcs()
    W_bins = []
    for nz_func in nz_funcs:
        W = lensing_efficiency(z_int, chi_int, nz_func, Omega_m, H0)
        W_bins.append(W)

    # C_ℓ for each (i,j) pair and each ℓ
    Cl = {}
    n_pairs = N_ZBINS * (N_ZBINS + 1) // 2

    for i in range(N_ZBINS):
        for j in range(i, N_ZBINS):
            cl_ij = np.zeros(len(ell_array))

            for il, ell in enumerate(ell_array):
                # Limber: k = (ℓ + 0.5) / χ
                k_limber = (ell + 0.5) / np.maximum(chi_int, 1.0)

                # Evaluate P(k, z) at Limber points
                P_at_ell = np.zeros_like(z_int)
                for iz in range(len(z_int)):
                    kl = k_limber[iz]
                    if k_array[0] <= kl <= k_array[-1]:
                        P_at_ell[iz] = np.exp(
                            float(Pk_interp(np.log(kl), z_int[iz]))
                        )

                # Integrand: W_i W_j P / χ²
                integrand = W_bins[i] * W_bins[j] * P_at_ell / chi_int ** 2
                cl_ij[il] = np.trapz(integrand, chi_int)

            Cl[(i, j)] = cl_ij

    return Cl


# =========================================================================
# Noise and covariance
# =========================================================================

def shape_noise_cl(ell_array):
    """
    Shape noise power spectrum N_ℓ^{ij} = σ_e² / n_bar_i × δ_{ij}.

    Returns dict {(i,j): array} with noise per bin pair.
    """
    arcmin2_per_sr = (180.0 * 60.0 / np.pi) ** 2
    n_per_bin = (N_EFF / N_ZBINS) * arcmin2_per_sr  # per sr

    N = {}
    for i in range(N_ZBINS):
        for j in range(i, N_ZBINS):
            if i == j:
                N[(i, j)] = np.full(len(ell_array), SIGMA_E ** 2 / n_per_bin)
            else:
                N[(i, j)] = np.zeros(len(ell_array))
    return N


def gaussian_covariance(ell_array, Cl_theory, N_ell):
    """
    Gaussian covariance for C_ℓ:

        Cov(C_ℓ^{ij}, C_ℓ^{kl}) = [(C_ℓ^{ik}+N^{ik})(C_ℓ^{jl}+N^{jl})
                                    + (C_ℓ^{il}+N^{il})(C_ℓ^{jk}+N^{jk})]
                                    / [(2ℓ+1) f_sky Δℓ]

    For diagonal approximation: Var(C_ℓ^{ij}) = 2(C_ℓ^{ij} + N^{ij})² / (2ℓ+1)f_sky Δℓ.
    """
    # Log-spaced ℓ bins → Δℓ ≈ 0.3ℓ
    delta_ell = 0.3 * ell_array

    Var = {}
    for (i, j), cl in Cl_theory.items():
        n = N_ell.get((i, j), np.zeros_like(ell_array))
        n_modes = F_SKY * (2 * ell_array + 1) * delta_ell
        Var[(i, j)] = 2.0 * (cl + n) ** 2 / n_modes

    return Var


# =========================================================================
# Likelihood class (Cobaya-compatible)
# =========================================================================

class CosmicShearLikelihood:
    """
    Gaussian cosmic shear likelihood for EFC Case B testing.

    Computes C_ℓ^{γγ} from modified P(k,z), compares to fiducial data.

    For production: replace fiducial with actual DES Y3 data vector
    and full covariance matrix (not diagonal).
    """

    def __init__(self, fiducial="LCDM"):
        self.ell_array = np.logspace(
            np.log10(ELL_MIN), np.log10(ELL_MAX), N_ELL)
        self.fiducial_model = fiducial
        self._data_vector = None
        self._inv_var = None

    def generate_fiducial(self, k_array, z_array, Pk_LCDM, Omega_m=0.3, H0=67.36):
        """Generate fiducial data vector from ΛCDM P(k,z)."""
        Cl_fid = compute_cl_matrix(
            self.ell_array, k_array, z_array, Pk_LCDM, Omega_m, H0)
        N_ell = shape_noise_cl(self.ell_array)
        Var = gaussian_covariance(self.ell_array, Cl_fid, N_ell)

        # Flatten to data vector
        self._pairs = sorted(Cl_fid.keys())
        self._data_vector = np.concatenate([Cl_fid[p] for p in self._pairs])
        self._inv_var = np.concatenate(
            [1.0 / Var[p] for p in self._pairs])
        self._N_ell = N_ell

        return Cl_fid

    def loglike(self, Cl_theory):
        """
        Gaussian log-likelihood:
            -2 ln L = Σ (C_data - C_theory)² / Var
        """
        theory_vec = np.concatenate([Cl_theory[p] for p in self._pairs])
        delta = self._data_vector - theory_vec
        chi2 = np.sum(delta ** 2 * self._inv_var)
        return -0.5 * chi2

    @property
    def n_data(self):
        return len(self._data_vector) if self._data_vector is not None else 0


# =========================================================================
# Self-test
# =========================================================================

if __name__ == "__main__":
    print("Cosmic Shear Likelihood — DES Y3-like")
    print("=" * 50)

    # Generate a simple P(k,z) for testing
    k = np.logspace(-3, 1, 100)
    z = np.linspace(0, 2.5, 50)
    # Approximate P(k) ∝ k^ns × T²(k) with simple transfer function
    Pk = np.outer(k ** (-2.5) * np.exp(-(k / 0.2) ** 2) * 1e4,
                  (1.0 / (1.0 + z)) ** 2)

    print(f"P(k,z) grid: {Pk.shape}")
    print(f"Tomographic bins: {N_ZBINS}")
    print(f"ℓ range: {ELL_MIN}–{ELL_MAX}, {N_ELL} bins")
    print(f"f_sky: {F_SKY:.4f}")

    ell = np.logspace(np.log10(ELL_MIN), np.log10(ELL_MAX), N_ELL)

    # Compute C_ℓ
    Cl = compute_cl_matrix(ell, k, z, Pk)
    print(f"\nC_ℓ pairs computed: {len(Cl)}")
    for (i, j), cl in sorted(Cl.items()):
        print(f"  ({i},{j}): C_ℓ range [{cl.min():.2e}, {cl.max():.2e}]")

    # Likelihood test
    like = CosmicShearLikelihood()
    like.generate_fiducial(k, z, Pk)
    logL = like.loglike(Cl)
    print(f"\nlog L(fiducial) = {logL:.2f} (should be ~0)")
    print(f"Data vector length: {like.n_data}")
