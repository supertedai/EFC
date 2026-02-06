#!/usr/bin/env python3
"""
BESR3: Extract entropy power-law index (alpha_sim) from TNG-Cluster
=====================================================================
Fits K(r) = K0 + K100 * (r/100 kpc)^alpha to radial entropy profiles
of all 352 primary zoom halos at z=0 (snapshot 99).

Based on Cavagnolo et al. (2009) / ACCEPT methodology.
Entropy: K = kB*T * ne^(-2/3)

Usage:
    export TNG_API_KEY="your-api-key-here"
    python besr3_extract_alpha.py [--start 0] [--end 352] [--output results/]

Output:
    - besr3_alpha_results.csv  (per-halo results)
    - besr3_profiles/          (per-halo radial profiles as .npz)
    - besr3_summary.json       (aggregate statistics)

Requirements:
    pip install numpy scipy h5py requests

Author: Morten Magnusson / EFC Project
Protocol: BESR-3 v1.0 (preregistered)
"""

import os
import sys
import json
import time
import logging
import argparse
import warnings
from pathlib import Path
from io import BytesIO

import numpy as np
from scipy.optimize import curve_fit
import h5py
import requests

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- Configuration -----------------------------------------------------------
API_KEY = os.environ.get("TNG_API_KEY", "")
BASE_URL = "http://www.tng-project.org/api/TNG-Cluster"
SNAPSHOT = 99  # z=0
N_RADIAL_BINS = 25
R_MIN_KPC = 10.0       # inner radial cut
R_FIT_MIN_KPC = 10.0   # fit range inner
R_FIT_MAX_FRAC = 1.0   # fit out to 1.0 * R500
HUBBLE_h = 0.6774      # TNG cosmology
UNIT_MASS_MSUN = 1e10 / HUBBLE_h
UNIT_LENGTH_KPC = 1e3 / HUBBLE_h  # ckpc/h -> kpc at z=0
XH = 0.76              # hydrogen mass fraction
KB_KEV = 8.617333e-8   # keV/K
MP_G = 1.6726e-24      # proton mass in grams
CM_PER_KPC = 3.0857e21

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("BESR3")


# --- .env loading ------------------------------------------------------------
def load_env():
    """Load API key from .env file if not in environment."""
    global API_KEY
    if API_KEY:
        return
    for env_path in [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("TNG_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return


# --- API helpers -------------------------------------------------------------
def api_get(url, params=None):
    """GET with API key and retry logic."""
    headers = {"api-key": API_KEY}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=300)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            wait = 2 ** attempt * 5
            log.warning(f"API error (attempt {attempt+1}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"API failed after 5 attempts: {url}")


def api_get_json(url, params=None):
    """GET JSON response."""
    return api_get(url, params).json()


def api_get_hdf5(url, params=None):
    """GET HDF5 binary and return h5py File object (in-memory)."""
    r = api_get(url, params)
    return h5py.File(BytesIO(r.content), "r")


# --- Data loading ------------------------------------------------------------
def get_primary_halos():
    """
    Get list of primary zoom target halos at snapshot 99.
    Returns list of dicts with halo_id, subhalo_id, M500c, R500c, etc.
    """
    log.info("Loading group catalog to identify primary zoom targets...")

    url = f"{BASE_URL}/snapshots/{SNAPSHOT}/halos/"
    params = {
        "limit": 500,
        "GroupPrimaryZoomTarget": 1,
    }

    halos = []
    offset = 0

    while True:
        params["offset"] = offset
        data = api_get_json(url, params)
        results = data.get("results", [])

        if not results:
            break

        for h in results:
            halo_id = h["id"]
            halo_url = f"{BASE_URL}/snapshots/{SNAPSHOT}/halos/{halo_id}/"
            halo_data = api_get_json(halo_url)

            m500 = halo_data.get("Group_M_Crit500", 0) * UNIT_MASS_MSUN
            r500 = halo_data.get("Group_R_Crit500", 0) * UNIT_LENGTH_KPC
            central_sub = halo_data.get("GroupFirstSub", -1)
            orig_id = halo_data.get("GroupOrigHaloID", -1)

            if m500 > 0 and r500 > 0 and central_sub >= 0:
                halos.append({
                    "halo_id": halo_id,
                    "subhalo_id": central_sub,
                    "M500c": m500,
                    "R500c_kpc": r500,
                    "OrigHaloID": orig_id,
                })

        offset += len(results)
        if offset >= data.get("count", 0):
            break

        log.info(f"  Loaded {offset}/{data.get('count', '?')} halos...")

    log.info(f"Found {len(halos)} primary zoom targets")
    return halos


def get_primary_halos_fast():
    """
    Faster method: iterate through halos and check GroupPrimaryZoomTarget.
    TNG-Cluster has exactly 352 primary targets.
    """
    log.info("Loading primary zoom targets (fast method)...")

    halos = []
    halo_id = 0
    checked = 0

    while len(halos) < 352 and checked < 5000:
        try:
            url = f"{BASE_URL}/snapshots/{SNAPSHOT}/halos/{halo_id}/"
            data = api_get_json(url)
            checked += 1

            is_primary = data.get("GroupPrimaryZoomTarget", 0)

            if is_primary == 1:
                m500 = data.get("Group_M_Crit500", 0) * UNIT_MASS_MSUN
                r500 = data.get("Group_R_Crit500", 0) * UNIT_LENGTH_KPC
                central_sub = data.get("GroupFirstSub", -1)
                orig_id = data.get("GroupOrigHaloID", -1)
                n_gas = data.get("GroupLenType", [0]*6)[0]

                if m500 > 0 and r500 > 0 and central_sub >= 0:
                    halos.append({
                        "halo_id": halo_id,
                        "subhalo_id": central_sub,
                        "M500c": m500,
                        "R500c_kpc": r500,
                        "OrigHaloID": orig_id,
                        "n_gas_fof": n_gas,
                    })

                    if len(halos) % 50 == 0:
                        log.info(f"  Found {len(halos)}/352 primary halos...")

            halo_id += 1

        except Exception as e:
            log.warning(f"  Halo {halo_id}: {e}")
            halo_id += 1
            continue

    log.info(f"Found {len(halos)} primary zoom targets")
    return halos


def get_gas_cutout(subhalo_id, fields=None):
    """
    Download gas cutout for a subhalo (central subhalo = all bound gas).
    Returns h5py File object (in-memory).
    """
    if fields is None:
        fields = "Coordinates,Masses,InternalEnergy,ElectronAbundance,Density,StarFormationRate"

    url = f"{BASE_URL}/snapshots/{SNAPSHOT}/subhalos/{subhalo_id}/cutout.hdf5"
    params = {"gas": fields}

    return api_get_hdf5(url, params)


# --- Physics calculations ----------------------------------------------------
def compute_entropy_profile(cutout_h5, center_kpc, r500_kpc, n_bins=N_RADIAL_BINS):
    """
    Compute radial entropy profile K(r) = kB*T * ne^(-2/3).

    Args:
        cutout_h5: h5py File with gas cutout
        center_kpc: (3,) array, subhalo center in kpc
        r500_kpc: R500 in kpc
        n_bins: number of radial bins

    Returns:
        r_mid: bin midpoints in kpc
        K_profile: entropy in keV cm^2
        T_profile: temperature in keV (mass-weighted)
        ne_profile: electron density in cm^-3 (mass-weighted)
        n_cells: number of cells per bin
    """
    gas = cutout_h5["PartType0"]

    # Load fields
    coords = gas["Coordinates"][:] * UNIT_LENGTH_KPC  # kpc
    masses = gas["Masses"][:] * UNIT_MASS_MSUN  # Msun (for weighting)
    u = gas["InternalEnergy"][:]  # (km/s)^2
    xe = gas["ElectronAbundance"][:]  # ne/nH
    rho = gas["Density"][:]  # code units: 1e10 Msun/h / (ckpc/h)^3
    sfr = gas["StarFormationRate"][:]

    # Exclude star-forming gas (effective EOS, not physical T)
    mask_nosf = sfr == 0
    coords = coords[mask_nosf]
    masses = masses[mask_nosf]
    u = u[mask_nosf]
    xe = xe[mask_nosf]
    rho = rho[mask_nosf]

    # Radial distance from center
    dx = coords - center_kpc
    r = np.sqrt(np.sum(dx**2, axis=1))  # kpc

    # Temperature: T = (gamma-1) * u * mu * mp / kB
    # u is in (km/s)^2 = 1e10 cm^2/s^2
    gamma = 5.0 / 3.0
    mu = 4.0 / (1.0 + 3.0 * XH + 4.0 * XH * xe)  # mean molecular weight
    T_K = (gamma - 1.0) * u * 1e10 * mu * MP_G / 1.3807e-16  # Kelvin
    T_keV = T_K * KB_KEV  # keV

    # Electron number density: ne = xe * nH = xe * XH * rho / mp
    # rho in code units -> g/cm^3
    rho_cgs = rho * (1e10 * 1.989e33 / HUBBLE_h) / (CM_PER_KPC / HUBBLE_h)**3
    nH = XH * rho_cgs / MP_G  # cm^-3
    ne = xe * nH  # cm^-3

    # Entropy: K = kB*T * ne^(-2/3)
    K = T_keV * ne**(-2.0/3.0)  # keV cm^2

    # Radial binning (log-spaced)
    r_edges = np.logspace(np.log10(R_MIN_KPC), np.log10(r500_kpc), n_bins + 1)
    r_mid = np.sqrt(r_edges[:-1] * r_edges[1:])  # geometric mean

    K_profile = np.full(n_bins, np.nan)
    T_profile = np.full(n_bins, np.nan)
    ne_profile = np.full(n_bins, np.nan)
    n_cells = np.zeros(n_bins, dtype=int)

    for i in range(n_bins):
        mask = (r >= r_edges[i]) & (r < r_edges[i+1])
        n_cells[i] = np.sum(mask)

        if n_cells[i] < 10:  # minimum cells for reliable estimate
            continue

        w = masses[mask]
        w_sum = np.sum(w)

        # Mass-weighted means
        T_profile[i] = np.sum(T_keV[mask] * w) / w_sum
        ne_profile[i] = np.sum(ne[mask] * w) / w_sum

        # Entropy from mass-weighted T and ne
        K_profile[i] = T_profile[i] * ne_profile[i]**(-2.0/3.0)

    return r_mid, K_profile, T_profile, ne_profile, n_cells


# --- Profile fitting ---------------------------------------------------------
def entropy_model(r, K0, K100, alpha):
    """ACCEPT entropy model: K(r) = K0 + K100 * (r/100)^alpha"""
    return K0 + K100 * (r / 100.0)**alpha


def fit_entropy_profile(r_kpc, K_kevcm2, r500_kpc):
    """
    Fit K(r) = K0 + K100 * (r/100 kpc)^alpha to the entropy profile.

    Returns:
        popt: (K0, K100, alpha)
        pcov: covariance matrix
        fit_quality: dict with chi2, dof, etc.
    """
    # Valid data mask
    mask = np.isfinite(K_kevcm2) & np.isfinite(r_kpc)
    mask &= (r_kpc >= R_FIT_MIN_KPC) & (r_kpc <= R_FIT_MAX_FRAC * r500_kpc)
    mask &= (K_kevcm2 > 0)

    r_fit = r_kpc[mask]
    K_fit = K_kevcm2[mask]

    if len(r_fit) < 5:
        return None, None, {"status": "FAIL", "reason": "too_few_bins"}

    # Initial guesses
    K0_guess = np.min(K_fit)
    K100_guess = np.median(K_fit)
    alpha_guess = 1.1  # self-similar

    try:
        popt, pcov = curve_fit(
            entropy_model, r_fit, K_fit,
            p0=[K0_guess, K100_guess, alpha_guess],
            bounds=([0, 0, 0.01], [1000, 5000, 5.0]),
            maxfev=10000,
            sigma=K_fit * 0.1,  # 10% relative weight
            absolute_sigma=False,
        )

        # Fit quality
        K_pred = entropy_model(r_fit, *popt)
        residuals = K_fit - K_pred
        chi2 = np.sum((residuals / (K_fit * 0.1))**2)
        dof = len(r_fit) - 3

        perr = np.sqrt(np.diag(pcov))

        return popt, pcov, {
            "status": "OK",
            "K0": popt[0],
            "K100": popt[1],
            "alpha": popt[2],
            "e_K0": perr[0],
            "e_K100": perr[1],
            "e_alpha": perr[2],
            "chi2": chi2,
            "dof": dof,
            "chi2_dof": chi2 / max(dof, 1),
            "n_bins_fit": len(r_fit),
        }

    except Exception as e:
        return None, None, {"status": "FAIL", "reason": str(e)}


# --- CC classification -------------------------------------------------------
def classify_cc(K0):
    """
    Classify cool-core state based on central entropy K0.
    Hudson et al. (2010) / Lehle et al. (2024) thresholds.
    """
    if K0 <= 22:
        return "SCC"  # Strong cool-core
    elif K0 <= 150:
        return "WCC"  # Weak cool-core
    else:
        return "NCC"  # Non-cool-core


# --- Main pipeline -----------------------------------------------------------
def process_halo(halo_info, output_dir):
    """
    Process a single halo: download gas, compute profile, fit alpha.

    Returns dict with results or None on failure.
    """
    hid = halo_info["halo_id"]
    sid = halo_info["subhalo_id"]
    r500 = halo_info["R500c_kpc"]
    m500 = halo_info["M500c"]

    log.info(f"  Halo {hid} (sub {sid}): M500={m500:.2e} Msun, R500={r500:.0f} kpc")

    try:
        # Get subhalo center
        sub_url = f"{BASE_URL}/snapshots/{SNAPSHOT}/subhalos/{sid}/"
        sub_data = api_get_json(sub_url)
        center = np.array(sub_data["pos"]) * UNIT_LENGTH_KPC  # kpc
        n_gas = sub_data.get("len_gas", 0)

        log.info(f"    Center: {center}, n_gas={n_gas}")

        if n_gas < 1000:
            log.warning(f"    Too few gas cells ({n_gas}), skipping")
            return None

        # Download gas cutout
        t0 = time.time()
        cutout = get_gas_cutout(sid)
        dt = time.time() - t0
        log.info(f"    Cutout downloaded in {dt:.1f}s")

        # Compute entropy profile
        r_mid, K_prof, T_prof, ne_prof, n_cells = compute_entropy_profile(
            cutout, center, r500
        )
        cutout.close()

        valid_bins = np.sum(np.isfinite(K_prof))
        log.info(f"    Profile: {valid_bins}/{N_RADIAL_BINS} valid bins")

        if valid_bins < 10:
            log.warning(f"    Too few valid bins ({valid_bins}), skipping")
            return None

        # Fit entropy profile
        popt, pcov, fit_info = fit_entropy_profile(r_mid, K_prof, r500)

        if fit_info["status"] != "OK":
            log.warning(f"    Fit failed: {fit_info.get('reason', 'unknown')}")
            return None

        # CC classification
        cc_class = classify_cc(fit_info["K0"])

        log.info(
            f"    alpha={fit_info['alpha']:.3f}+/-{fit_info['e_alpha']:.3f}, "
            f"K0={fit_info['K0']:.1f}, K100={fit_info['K100']:.1f}, "
            f"CC={cc_class}"
        )

        # Save profile
        profile_dir = output_dir / "besr3_profiles"
        profile_dir.mkdir(exist_ok=True)
        np.savez(
            profile_dir / f"halo_{hid:04d}.npz",
            r_kpc=r_mid,
            K_kevcm2=K_prof,
            T_keV=T_prof,
            ne_cm3=ne_prof,
            n_cells=n_cells,
            fit_K0=fit_info["K0"],
            fit_K100=fit_info["K100"],
            fit_alpha=fit_info["alpha"],
        )

        # Compute CCT proxy: y = log10(K0 / K100) if K100 > 0
        y_proxy = np.log10(fit_info["K0"] / fit_info["K100"]) if fit_info["K100"] > 0 else np.nan

        return {
            "halo_id": hid,
            "subhalo_id": sid,
            "OrigHaloID": halo_info.get("OrigHaloID", -1),
            "M500c_Msun": m500,
            "R500c_kpc": r500,
            "n_gas": n_gas,
            "n_bins_valid": int(valid_bins),
            "K0": fit_info["K0"],
            "e_K0": fit_info["e_K0"],
            "K100": fit_info["K100"],
            "e_K100": fit_info["e_K100"],
            "alpha": fit_info["alpha"],
            "e_alpha": fit_info["e_alpha"],
            "chi2_dof": fit_info["chi2_dof"],
            "n_bins_fit": fit_info["n_bins_fit"],
            "CC_class": cc_class,
            "y_CCT_proxy": y_proxy,
        }

    except Exception as e:
        log.error(f"    FAILED: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="BESR3: Extract alpha_sim from TNG-Cluster")
    parser.add_argument("--start", type=int, default=0, help="Start halo index (0-351)")
    parser.add_argument("--end", type=int, default=352, help="End halo index (exclusive)")
    parser.add_argument("--output", type=str, default="results", help="Output directory")
    parser.add_argument("--fast", action="store_true", help="Use fast halo enumeration")
    parser.add_argument("--catalog", type=str, default=None,
                        help="Path to pre-downloaded halo catalog JSON")
    args = parser.parse_args()

    load_env()

    if not API_KEY:
        log.error("Set TNG_API_KEY environment variable!")
        log.error("Get your key at: https://www.tng-project.org/users/login/")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get halo catalog
    catalog_file = output_dir / "halo_catalog.json"

    if args.catalog and Path(args.catalog).exists():
        log.info(f"Loading catalog from {args.catalog}")
        with open(args.catalog) as f:
            halos = json.load(f)
    elif catalog_file.exists():
        log.info(f"Loading cached catalog from {catalog_file}")
        with open(catalog_file) as f:
            halos = json.load(f)
    else:
        if args.fast:
            halos = get_primary_halos_fast()
        else:
            halos = get_primary_halos()

        # Cache catalog
        with open(catalog_file, "w") as f:
            json.dump(halos, f, indent=2)
        log.info(f"Saved halo catalog to {catalog_file}")

    # Step 2: Process halos
    halos_to_process = halos[args.start:args.end]
    log.info(f"Processing halos {args.start}-{args.end} ({len(halos_to_process)} halos)")

    results = []
    results_file = output_dir / "besr3_alpha_results.csv"

    # Write CSV header
    if not results_file.exists() or args.start == 0:
        with open(results_file, "w") as f:
            f.write("halo_id,subhalo_id,OrigHaloID,M500c_Msun,R500c_kpc,"
                    "n_gas,n_bins_valid,K0,e_K0,K100,e_K100,alpha,e_alpha,"
                    "chi2_dof,n_bins_fit,CC_class,y_CCT_proxy\n")

    for i, halo in enumerate(halos_to_process):
        log.info(f"\n{'='*60}")
        log.info(f"Halo {i+1}/{len(halos_to_process)} (index {args.start + i})")

        result = process_halo(halo, output_dir)

        if result:
            results.append(result)

            # Append to CSV immediately (crash-safe)
            with open(results_file, "a") as f:
                f.write(
                    f"{result['halo_id']},{result['subhalo_id']},"
                    f"{result['OrigHaloID']},{result['M500c_Msun']:.6e},"
                    f"{result['R500c_kpc']:.2f},{result['n_gas']},"
                    f"{result['n_bins_valid']},{result['K0']:.4f},"
                    f"{result['e_K0']:.4f},{result['K100']:.4f},"
                    f"{result['e_K100']:.4f},{result['alpha']:.6f},"
                    f"{result['e_alpha']:.6f},{result['chi2_dof']:.4f},"
                    f"{result['n_bins_fit']},{result['CC_class']},"
                    f"{result['y_CCT_proxy']:.6f}\n"
                )

            log.info(f"  Saved ({len(results)} total)")

        # Rate limiting
        time.sleep(0.5)

    # Step 3: Summary statistics
    if results:
        alphas = [r["alpha"] for r in results]
        K0s = [r["K0"] for r in results]
        cc_counts = {}
        for r in results:
            cc = r["CC_class"]
            cc_counts[cc] = cc_counts.get(cc, 0) + 1

        summary = {
            "n_processed": len(halos_to_process),
            "n_success": len(results),
            "n_fail": len(halos_to_process) - len(results),
            "alpha_mean": float(np.mean(alphas)),
            "alpha_median": float(np.median(alphas)),
            "alpha_std": float(np.std(alphas)),
            "alpha_min": float(np.min(alphas)),
            "alpha_max": float(np.max(alphas)),
            "K0_mean": float(np.mean(K0s)),
            "K0_median": float(np.median(K0s)),
            "CC_counts": cc_counts,
        }

        # Correlation: alpha vs y_CCT_proxy
        y_vals = [r["y_CCT_proxy"] for r in results if np.isfinite(r["y_CCT_proxy"])]
        a_vals = [r["alpha"] for r in results if np.isfinite(r["y_CCT_proxy"])]
        if len(y_vals) > 5:
            from scipy.stats import spearmanr
            rho, pval = spearmanr(a_vals, y_vals)
            summary["spearman_alpha_vs_yCCT"] = {"rho": float(rho), "p_value": float(pval)}

        with open(output_dir / "besr3_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        log.info(f"\n{'='*60}")
        log.info(f"BESR3 SUMMARY")
        log.info(f"  Processed: {summary['n_processed']}")
        log.info(f"  Success:   {summary['n_success']}")
        log.info(f"  alpha mean:    {summary['alpha_mean']:.3f} +/- {summary['alpha_std']:.3f}")
        log.info(f"  alpha median:  {summary['alpha_median']:.3f}")
        log.info(f"  K0 median: {summary['K0_median']:.1f} keV cm^2")
        log.info(f"  CC state:  {cc_counts}")
        if "spearman_alpha_vs_yCCT" in summary:
            s = summary["spearman_alpha_vs_yCCT"]
            log.info(f"  rho(alpha, y_CCT): {s['rho']:.3f} (p={s['p_value']:.4f})")

    log.info("\nDone!")


if __name__ == "__main__":
    main()
