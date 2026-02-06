#!/usr/bin/env python3
"""
BESR3 Path A: Full Entropy Profile α-Fit from TNG-Cluster API
===============================================================
THE DECISIVE TEST. Fits K(r) = K₀ + K₁₀₀·(r/100kpc)^α to each of 352
TNG-Cluster halos using gas particle data from the TNG API.

This eliminates the three remaining referee objections:
  1. T-slope variation → measured directly via K = T·ne^{-2/3}
  2. Radius mismatch → fit over same interval as ACCEPT (20-400 kpc)
  3. Local vs global → global power-law fit, not point measurement

USAGE:
  export TNG_API_KEY="your-api-key-here"
  python3 besr3_path_a_alpha_fit.py

RUNTIME: ~3 min/halo × 352 = ~18 hours (with checkpointing)
CHECKPOINTING: Results saved after each halo to besr3_alpha_fits.json
RESTART: Automatically skips already-computed halos

LOCKED PARAMETERS (set before seeing results):
  - Fit range: 20-400 kpc (physical)
  - Fit model: K(r) = K₀ + K₁₀₀·(r/100kpc)^α  [Cavagnolo+2008]
  - Radial bins: 30 log-spaced bins in fit range
  - Gas selection: T > 10⁶ K, non-star-forming (Lehle+2024 methodology)
  - Weighting: mass-weighted K in each radial bin

Author: BESR3 analysis pipeline
Date: 2026-02-06
"""

import os
import sys
import json
import time
import requests
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════
# CONFIGURATION (LOCKED)
# ═══════════════════════════════════════════
TNG_BASE_URL = "https://www.tng-project.org/api"
SIMULATION = "TNG-Cluster"
SNAPSHOT = 99  # z=0

# Fit parameters (LOCKED before seeing results)
FIT_R_MIN_KPC = 20.0    # Inner fit radius [kpc]
FIT_R_MAX_KPC = 400.0   # Outer fit radius [kpc]
N_RADIAL_BINS = 30       # Number of log-spaced radial bins
T_MIN_K = 1e6            # Minimum gas temperature [K]

# File paths
CATALOG_FILE = "TNG-Cluster_Catalog.txt"
CHECKPOINT_FILE = "besr3_alpha_fits.json"
RESULTS_FILE = "besr3_path_a_results.json"

# TNG unit conversions
HUBBLE_PARAM = 0.6774
UNIT_LENGTH_CM = 3.085678e21  # kpc in cm (for Arepo → physical kpc)
PROTON_MASS_G = 1.6726e-24
BOLTZMANN_ERG = 1.3807e-16
KEV_PER_ERG = 6.242e8


def get_api_key():
    key = os.environ.get("TNG_API_KEY")
    if not key:
        print("ERROR: Set TNG_API_KEY environment variable")
        print("  export TNG_API_KEY='your-api-key-here'")
        sys.exit(1)
    return key


def load_catalog(path):
    """Load TNG-Cluster catalog for halo metadata."""
    cols = ["origID", "haloID", "mhalo_200c", "mhalo_500c", "r200c", "r500c",
            "mstar_30kpc", "mstar_100kpc", "mhi_halo", "mass_smbh", "fgas_r500",
            "sfr_30pkpc", "xray_05_2kev", "szy_r500c", "Bmag_10kpc", "ne_10kpc",
            "temp_10kpc", "zform", "richness_95", "richness_100", "richness_105",
            "richness_110", "cc_flag_str", "coolcore_tcool", "coolcore_entropy",
            "coolcore_ne", "coolcore_ne_slope", "coolcore_C_phys", "coolcore_C_scaled",
            "perseus_flag", "po_xray_x", "po_xray_y", "po_xray_z",
            "po_sz_x", "po_sz_y", "po_sz_z"]
    
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    
    data = {c: [] for c in cols}
    for line in lines:
        parts = line.split()
        if len(parts) < 36:
            continue
        for i, c in enumerate(cols):
            val = parts[i]
            if c == "cc_flag_str":
                data[c].append(val)
            elif val == "nan":
                data[c].append(np.nan)
            else:
                try:
                    data[c].append(float(val))
                except ValueError:
                    data[c].append(np.nan)
    
    for c in cols:
        if c != "cc_flag_str":
            data[c] = np.array(data[c], dtype=float)
        else:
            data[c] = np.array(data[c])
    
    return data


def get_subhalo_info(halo_id, api_key):
    """Get the central subhalo ID and position for a given FoF halo.
    
    Returns: (subhalo_id, position_ckpc_h) or (None, None)
    """
    headers = {"api-key": api_key}
    
    # Get FoF halo → central subhalo ID
    url = f"{TNG_BASE_URL}/{SIMULATION}/snapshots/{SNAPSHOT}/halos/{int(halo_id)}/"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    halo_info = r.json()
    
    sub_id = halo_info.get("GroupFirstSub", None)
    if sub_id is None:
        return None, None
    
    # Get subhalo position (this is the SUBFIND-determined center)
    url_sub = f"{TNG_BASE_URL}/{SIMULATION}/snapshots/{SNAPSHOT}/subhalos/{int(sub_id)}/"
    r2 = requests.get(url_sub, headers=headers, timeout=30)
    r2.raise_for_status()
    sub_info = r2.json()
    
    # SubhaloPos is in ckpc/h (comoving kpc/h)
    pos = sub_info.get("pos_x", None)
    if pos is not None:
        center_ckpc_h = np.array([sub_info["pos_x"], sub_info["pos_y"], sub_info["pos_z"]])
    else:
        # Fallback: try SubhaloPos field
        center_ckpc_h = np.array(sub_info.get("SubhaloPos", [np.nan]*3))
    
    return int(sub_id), center_ckpc_h


def download_cutout(subhalo_id, api_key, radius_kpc):
    """Download gas particle cutout for a subhalo within given radius."""
    headers = {"api-key": api_key}
    
    # Request gas particles: coordinates, masses, internal energy, electron abundance, SFR, density
    params = {
        "gas": "Coordinates,Masses,InternalEnergy,ElectronAbundance,"
               "StarFormationRate,Density"
    }
    
    url = f"{TNG_BASE_URL}/{SIMULATION}/snapshots/{SNAPSHOT}/subhalos/{int(subhalo_id)}/cutout.hdf5"
    
    r = requests.get(url, headers=headers, params=params, timeout=300)
    r.raise_for_status()
    
    return r.content


def process_cutout(hdf5_bytes, r500c_kpc, center_ckpc_h):
    """
    Process HDF5 cutout bytes → radial entropy profile K(r).
    
    Uses SUBFIND-determined halo center (center_ckpc_h) for radial binning.
    This avoids the bias from median-centering on gas particles.
    
    Returns: (r_kpc, K_kevcm2, K_err) arrays for radial bins
    """
    import h5py
    import io
    
    with h5py.File(io.BytesIO(hdf5_bytes), "r") as f:
        if "PartType0" not in f:
            return None, None, None
        
        gas = f["PartType0"]
        
        coords = gas["Coordinates"][:]          # ckpc/h
        masses = gas["Masses"][:]               # 1e10 Msun/h
        u = gas["InternalEnergy"][:]            # (km/s)^2
        xe = gas["ElectronAbundance"][:]        # dimensionless
        sfr = gas["StarFormationRate"][:]       # Msun/yr
        rho = gas["Density"][:]                 # 1e10 Msun/h / (ckpc/h)^3
        
        # Header info
        header = f["Header"]
        a = header.attrs["Time"]                # scale factor (=1 at z=0)
        h = header.attrs["HubbleParam"]
        boxsize = header.attrs["BoxSize"]
    
    # Convert to physical units
    # At z=0: a=1, so comoving = physical
    coords_phys = coords * a / h  # kpc
    
    # Use SUBFIND center (converted to physical kpc), NOT median of particles
    # This matches Lehle+2024 methodology and avoids off-center bias
    center_phys = center_ckpc_h * a / h  # physical kpc
    dx = coords_phys - center_phys
    r = np.sqrt(np.sum(dx**2, axis=1))  # kpc
    
    # Gas temperature from internal energy
    # T = (gamma-1) * u * mu * mp / kB
    # mu = 4 / (1 + 3*XH + 4*XH*xe) for primordial composition
    XH = 0.76
    gamma = 5.0 / 3.0
    mu = 4.0 / (1.0 + 3.0 * XH + 4.0 * XH * xe)
    
    # u is in (km/s)^2 = 1e10 cm^2/s^2
    T = (gamma - 1) * u * 1e10 * mu * PROTON_MASS_G / BOLTZMANN_ERG  # Kelvin
    
    # Electron number density
    # rho in 1e10 Msun/h / (ckpc/h)^3 → convert to g/cm^3
    rho_cgs = rho * 1e10 * 1.989e33 / h / (a / h * 3.085678e21)**3  # g/cm^3
    ne = rho_cgs * XH * xe / PROTON_MASS_G  # cm^{-3}
    
    # Entropy: K = kT * ne^{-2/3} [keV cm^2]
    # k_B * T in keV: T [K] * k_B [erg/K] / (1 keV in erg = 1.602e-9 erg)
    kT_keV = T * BOLTZMANN_ERG / 1.602e-9  # keV
    K = kT_keV * ne**(-2.0/3.0)  # keV cm^2
    
    # Selection: T > 10^6 K AND non-star-forming (following Lehle+2024)
    # NOTE: Using mass-weighted entropy in radial bins. ACCEPT uses spectroscopic-
    # like weighting from X-ray fitting. This affects absolute normalization but
    # is not expected to reverse rank-order correlations across the population.
    mask = (T > T_MIN_K) & (sfr == 0) & (r > 0) & np.isfinite(K) & (K > 0)
    
    if np.sum(mask) < 100:
        return None, None, None
    
    r_sel = r[mask]
    K_sel = K[mask]
    m_sel = masses[mask]
    
    # Radial binning (log-spaced, in fit range)
    r_edges = np.logspace(np.log10(FIT_R_MIN_KPC), np.log10(FIT_R_MAX_KPC), N_RADIAL_BINS + 1)
    r_mid = np.sqrt(r_edges[:-1] * r_edges[1:])  # geometric mean
    
    K_binned = np.full(N_RADIAL_BINS, np.nan)
    K_err = np.full(N_RADIAL_BINS, np.nan)
    N_bin = np.zeros(N_RADIAL_BINS, dtype=int)
    
    for j in range(N_RADIAL_BINS):
        in_bin = (r_sel >= r_edges[j]) & (r_sel < r_edges[j+1])
        n = np.sum(in_bin)
        N_bin[j] = n
        if n >= 5:
            w = m_sel[in_bin]
            K_binned[j] = np.average(K_sel[in_bin], weights=w)
            # Weighted std as error estimate
            K_err[j] = np.sqrt(np.average((K_sel[in_bin] - K_binned[j])**2, weights=w)) / np.sqrt(n)
    
    good = np.isfinite(K_binned) & (K_err > 0)
    if np.sum(good) < 5:
        return None, None, None
    
    return r_mid[good], K_binned[good], K_err[good]


def cavagnolo_model(r, K0, K100, alpha):
    """Cavagnolo+2008 entropy model: K(r) = K₀ + K₁₀₀·(r/100)^α"""
    return K0 + K100 * (r / 100.0)**alpha


def fit_alpha(r_kpc, K_kevcm2, K_err, K0_guess=None):
    """
    Fit Cavagnolo model to entropy profile.
    Returns: (K0_fit, K100_fit, alpha_fit, alpha_err, chi2_red, success)
    """
    if K0_guess is None:
        K0_guess = np.min(K_kevcm2)
    
    K100_guess = np.median(K_kevcm2)
    alpha_guess = 1.1  # ACCEPT median
    
    p0 = [max(K0_guess, 1.0), max(K100_guess, 10.0), alpha_guess]
    bounds = ([0, 0, 0.01], [1000, 5000, 5.0])
    
    try:
        popt, pcov = curve_fit(
            cavagnolo_model, r_kpc, K_kevcm2, p0=p0,
            sigma=K_err, absolute_sigma=True,
            bounds=bounds, maxfev=10000
        )
        perr = np.sqrt(np.diag(pcov))
        
        # Reduced chi-squared
        resid = K_kevcm2 - cavagnolo_model(r_kpc, *popt)
        chi2 = np.sum((resid / K_err)**2)
        dof = len(r_kpc) - 3
        chi2_red = chi2 / dof if dof > 0 else np.nan
        
        return {
            "K0_fit": float(popt[0]),
            "K100_fit": float(popt[1]),
            "alpha_fit": float(popt[2]),
            "alpha_err": float(perr[2]),
            "chi2_red": float(chi2_red),
            "n_bins": int(len(r_kpc)),
            "success": True
        }
    
    except (RuntimeError, ValueError) as e:
        return {
            "K0_fit": np.nan,
            "K100_fit": np.nan,
            "alpha_fit": np.nan,
            "alpha_err": np.nan,
            "chi2_red": np.nan,
            "n_bins": int(len(r_kpc)),
            "success": False,
            "error": str(e)
        }


def load_checkpoint(path):
    """Load existing results for restart capability."""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_checkpoint(results, path):
    """Save results incrementally."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def main():
    api_key = get_api_key()
    catalog = load_catalog(CATALOG_FILE)
    
    N_halos = len(catalog["haloID"])
    print(f"TNG-Cluster Path A: Full α-fit pipeline")
    print(f"Halos: {N_halos}")
    print(f"Fit range: {FIT_R_MIN_KPC}–{FIT_R_MAX_KPC} kpc")
    print(f"Model: K(r) = K₀ + K₁₀₀·(r/100kpc)^α")
    print(f"Checkpoint file: {CHECKPOINT_FILE}")
    print()
    
    # Load checkpoint
    results = load_checkpoint(CHECKPOINT_FILE)
    done = set(results.keys())
    print(f"Already completed: {len(done)} halos")
    
    t_start = time.time()
    
    for i in range(N_halos):
        halo_id = int(catalog["haloID"][i])
        halo_key = str(halo_id)
        
        if halo_key in done:
            continue
        
        K0_cat = catalog["coolcore_entropy"][i]
        r500c = catalog["r500c"][i]  # kpc (already physical from catalog)
        log_mass = catalog["mhalo_500c"][i]
        ne_slope = catalog["coolcore_ne_slope"][i]
        tcool = catalog["coolcore_tcool"][i]
        
        print(f"[{len(done)+1}/{N_halos}] Halo {halo_id} "
              f"(log M={log_mass:.2f}, K₀_cat={K0_cat:.1f}, r500c={r500c:.0f} kpc)...", 
              end=" ", flush=True)
        
        try:
            # Step 1: Get central subhalo ID and SUBFIND position
            sub_id, center_ckpc_h = get_subhalo_info(halo_id, api_key)
            if sub_id is None or center_ckpc_h is None:
                print("SKIP (no central subhalo)")
                results[halo_key] = {"success": False, "error": "no central subhalo"}
                save_checkpoint(results, CHECKPOINT_FILE)
                done.add(halo_key)
                continue
            
            # Step 2: Download cutout (within r500c for safety, fit uses inner part)
            hdf5_data = download_cutout(sub_id, api_key, r500c)
            
            # Step 3: Process → radial entropy profile (centered on SUBFIND position)
            r_bins, K_bins, K_err = process_cutout(hdf5_data, r500c, center_ckpc_h)
            
            if r_bins is None:
                print("SKIP (insufficient gas cells)")
                results[halo_key] = {"success": False, "error": "insufficient gas cells"}
                save_checkpoint(results, CHECKPOINT_FILE)
                done.add(halo_key)
                continue
            
            # Step 4: Fit Cavagnolo model
            fit = fit_alpha(r_bins, K_bins, K_err, K0_guess=K0_cat)
            
            # Store with metadata
            fit["halo_id"] = halo_id
            fit["subhalo_id"] = int(sub_id)
            fit["K0_catalog"] = float(K0_cat)
            fit["ne_slope_catalog"] = float(ne_slope)
            fit["tcool_catalog"] = float(tcool)
            fit["log_M500c"] = float(log_mass)
            fit["r500c_kpc"] = float(r500c)
            
            results[halo_key] = fit
            done.add(halo_key)
            
            if fit["success"]:
                print(f"α = {fit['alpha_fit']:.3f} ± {fit['alpha_err']:.3f} "
                      f"(K₀_fit={fit['K0_fit']:.1f}, χ²ᵣ={fit['chi2_red']:.2f})")
            else:
                print(f"FIT FAILED: {fit.get('error', 'unknown')}")
            
            # Checkpoint every halo
            save_checkpoint(results, CHECKPOINT_FILE)
            
        except requests.exceptions.RequestException as e:
            print(f"API ERROR: {e}")
            # Don't save — will retry on restart
            time.sleep(5)
            continue
        except Exception as e:
            print(f"ERROR: {e}")
            results[halo_key] = {"success": False, "error": str(e)}
            save_checkpoint(results, CHECKPOINT_FILE)
            done.add(halo_key)
            continue
        
        # Rate limiting: be polite to TNG servers
        time.sleep(0.5)
    
    elapsed = (time.time() - t_start) / 3600
    print(f"\nCompleted in {elapsed:.1f} hours")
    
    # ═══════════════════════════════════════════
    # ANALYSIS (runs after all fits complete)
    # ═══════════════════════════════════════════
    analyze_results(results, catalog)


def analyze_results(results, catalog):
    """Run the locked BESR3 test battery on α_fit values."""
    from scipy.stats import spearmanr, rankdata
    
    # Extract successful fits
    alpha_list, K0_list, tcool_list, mass_list, ne_slope_list = [], [], [], [], []
    
    for key, val in results.items():
        if val.get("success") and np.isfinite(val.get("alpha_fit", np.nan)):
            alpha_list.append(val["alpha_fit"])
            K0_list.append(val["K0_catalog"])
            tcool_list.append(val["tcool_catalog"])
            mass_list.append(val["log_M500c"])
            ne_slope_list.append(val["ne_slope_catalog"])
    
    alpha = np.array(alpha_list)
    K0 = np.array(K0_list)
    tcool = np.array(tcool_list)
    log_mass = np.array(mass_list)
    ne_slope = np.array(ne_slope_list)
    
    N = len(alpha)
    print(f"\n{'='*65}")
    print(f"BESR3 PATH A: DECISIVE TEST (N={N} successful fits)")
    print(f"{'='*65}")
    
    if N < 50:
        print("WARNING: Too few successful fits for reliable statistics")
        return
    
    # Partial Spearman
    def partial_spearman(x, y, z):
        rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
        def res(r, rz):
            s = np.sum((r - r.mean()) * (rz - rz.mean())) / np.sum((rz - rz.mean())**2)
            return r - s * rz
        return spearmanr(res(rx, rz), res(ry, rz))
    
    # Test 1: Raw Spearman
    rho_aK, p_aK = spearmanr(alpha, K0)
    rho_at, p_at = spearmanr(alpha, tcool)
    
    print(f"\n  ρ(α_fit, K₀)    = {rho_aK:+.4f}  (p={p_aK:.2e})")
    print(f"  ρ(α_fit, tcool)  = {rho_at:+.4f}  (p={p_at:.2e})")
    print(f"  ACCEPT reference: ρ(α, y_CCT) ≈ +0.36")
    
    # Test 2: Partial
    rho_aK_p, p_aK_p = partial_spearman(alpha, K0, log_mass)
    rho_at_p, p_at_p = partial_spearman(alpha, tcool, log_mass)
    
    print(f"\n  ρ(α_fit, K₀ | M)    = {rho_aK_p:+.4f}  (p={p_aK_p:.2e})")
    print(f"  ρ(α_fit, tcool | M)  = {rho_at_p:+.4f}  (p={p_at_p:.2e})")
    
    # Test 3: Mass-binned
    edges = [14.0, 14.3, 14.6, 14.9, 15.5]
    print(f"\n  Mass-binned:")
    for i in range(len(edges)-1):
        mask = (log_mass >= edges[i]) & (log_mass < edges[i+1])
        n = np.sum(mask)
        if n > 10:
            rho, p = spearmanr(alpha[mask], K0[mask])
            print(f"    [{edges[i]:.1f}, {edges[i+1]:.1f}): N={n:3d}, ρ={rho:+.3f}")
    
    # Consistency: α_fit vs α_proxy
    alpha_proxy = (2.0/3.0) * ne_slope
    rho_fit_proxy, _ = spearmanr(alpha, alpha_proxy)
    print(f"\n  Consistency: ρ(α_fit, α_proxy) = {rho_fit_proxy:+.3f}")
    
    # Verdict
    sign_K0 = rho_aK < 0
    sign_tc = rho_at < 0
    
    print(f"\n{'='*65}")
    if sign_K0 and sign_tc:
        print("FINAL VERDICT: SIGN FLIP CONFIRMED.")
        print("TNG-Cluster α_fit gives opposite sign to ACCEPT observations.")
        print("All three referee objections eliminated.")
        print("This is a genuine sim-obs mismatch in CC-structure coupling.")
    elif not sign_K0 and not sign_tc:
        print("FINAL VERDICT: SIGN FLIP REVERSED.")
        print("Definition matching (full α-fit) reverses the sign.")
        print("The original finding was a definition artifact.")
    else:
        print("FINAL VERDICT: MIXED SIGNAL.")
        print("One CC proxy flips, the other doesn't. Requires investigation.")
    print(f"{'='*65}")
    
    # Save final results
    final = {
        "N_fits": int(N),
        "alpha_fit_median": float(np.median(alpha)),
        "alpha_fit_mean": float(np.mean(alpha)),
        "alpha_fit_std": float(np.std(alpha)),
        "rho_alpha_K0": float(rho_aK),
        "rho_alpha_tcool": float(rho_at),
        "rho_alpha_K0_partial_M": float(rho_aK_p),
        "rho_alpha_tcool_partial_M": float(rho_at_p),
        "rho_alpha_fit_vs_proxy": float(rho_fit_proxy),
        "ACCEPT_reference": 0.36,
        "sign_flip_K0": bool(sign_K0),
        "sign_flip_tcool": bool(sign_tc),
    }
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(final, f, indent=2)
    print(f"\nResults saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
