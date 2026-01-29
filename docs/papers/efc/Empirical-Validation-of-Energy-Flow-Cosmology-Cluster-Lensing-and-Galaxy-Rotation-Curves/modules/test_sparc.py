"""
SPARC Rotation Curve Test for EFC
==================================
Test if the SAME λ from cluster fits works for galaxy rotation curves.

This is the critical cross-regime test:
- Clusters: λ ~ 1.5' ~ 250 kpc
- Galaxies: λ should be ~ few kpc (scaled by system size?)

Key question: Is λ a universal physical scale, or does it scale with system?

SPARC database: http://astroweb.cwru.edu/SPARC/
"""

import numpy as np
from pathlib import Path
import requests
from scipy.optimize import minimize

# =============================================================================
# SPARC DATA FETCHER
# =============================================================================

SPARC_URL = "http://astroweb.cwru.edu/SPARC/SPARC_Lelli2016c.mrt"

def fetch_sparc_data(cache_dir=None):
    """
    Fetch SPARC database from CWRU.
    
    Returns metadata table with galaxy properties.
    """
    if cache_dir is None:
        cache_dir = Path("/home/claude/sparc_data")
    cache_dir.mkdir(exist_ok=True)
    
    local_file = cache_dir / "SPARC_Lelli2016c.mrt"
    
    if not local_file.exists():
        print("Downloading SPARC database...")
        try:
            resp = requests.get(SPARC_URL, timeout=60)
            if resp.status_code == 200:
                with open(local_file, 'wb') as f:
                    f.write(resp.content)
                print(f"Saved: {local_file}")
            else:
                print(f"Download failed: HTTP {resp.status_code}")
                return None
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    # Parse MRT format (Machine Readable Table)
    galaxies = []
    with open(local_file, 'r') as f:
        in_data = False
        for line in f:
            if line.startswith('---'):
                in_data = True
                continue
            if in_data and line.strip():
                # Parse fixed-width columns
                try:
                    name = line[0:12].strip()
                    dist = float(line[25:30]) if line[25:30].strip() else np.nan
                    inc = float(line[31:36]) if line[31:36].strip() else np.nan
                    galaxies.append({
                        'name': name,
                        'distance_Mpc': dist,
                        'inclination_deg': inc,
                    })
                except:
                    pass
    
    print(f"Loaded {len(galaxies)} SPARC galaxies")
    return galaxies


def fetch_single_galaxy(name, cache_dir=None):
    """
    Fetch rotation curve data for a single SPARC galaxy.
    
    Returns r, v_obs, v_err, v_gas, v_disk, v_bul
    """
    if cache_dir is None:
        cache_dir = Path("/home/claude/sparc_data")
    cache_dir.mkdir(exist_ok=True)
    
    # Individual galaxy files
    url = f"http://astroweb.cwru.edu/SPARC/MassModels_Lelli2016c.mrt/{name}_rotmod.dat"
    local_file = cache_dir / f"{name}_rotmod.dat"
    
    if not local_file.exists():
        print(f"Downloading {name}...")
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                with open(local_file, 'wb') as f:
                    f.write(resp.content)
            else:
                # Try alternative URL format
                url2 = f"http://astroweb.cwru.edu/SPARC/{name}_rotmod.dat"
                resp = requests.get(url2, timeout=30)
                if resp.status_code == 200:
                    with open(local_file, 'wb') as f:
                        f.write(resp.content)
                else:
                    print(f"  Failed to download {name}")
                    return None
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    # Parse data file
    try:
        data = np.loadtxt(local_file)
        # Columns: Rad, Vobs, errV, Vgas, Vdisk, Vbul (typically)
        return {
            'r_kpc': data[:, 0],
            'v_obs': data[:, 1],
            'v_err': data[:, 2],
            'v_gas': data[:, 3] if data.shape[1] > 3 else np.zeros_like(data[:, 0]),
            'v_disk': data[:, 4] if data.shape[1] > 4 else np.zeros_like(data[:, 0]),
            'v_bul': data[:, 5] if data.shape[1] > 5 else np.zeros_like(data[:, 0]),
        }
    except Exception as e:
        print(f"  Parse error: {e}")
        return None


# =============================================================================
# CREATE EXAMPLE SPARC-LIKE DATA
# =============================================================================

def create_example_galaxy():
    """
    Create example galaxy data for testing.
    
    Based on typical SPARC spiral galaxy (NGC 2403-like).
    """
    # Radial points
    r_kpc = np.linspace(0.5, 15, 30)
    
    # Stellar disk (exponential)
    R_d = 2.5  # kpc, disk scale length
    Sigma_0 = 500  # M_sun/pc², central surface density
    Sigma_star = Sigma_0 * np.exp(-r_kpc / R_d)
    
    # Gas disk (flatter)
    R_gas = 5.0  # kpc
    Sigma_gas_0 = 10  # M_sun/pc²
    Sigma_gas = Sigma_gas_0 * np.exp(-r_kpc / R_gas)
    
    # "Observed" rotation curve (with flat outer part)
    # This mimics what SPARC galaxies look like
    v_max = 130  # km/s
    r_turn = 3.0  # kpc
    v_obs = v_max * np.sqrt(1 - np.exp(-r_kpc / r_turn))
    
    # Add noise
    v_err = 5 + 0.03 * v_obs  # Typical uncertainties
    rng = np.random.default_rng(42)
    v_obs = v_obs + rng.normal(0, v_err)
    
    return {
        'name': 'Example_Galaxy',
        'r_kpc': r_kpc,
        'v_obs': v_obs,
        'v_err': v_err,
        'Sigma_star': Sigma_star,
        'Sigma_gas': Sigma_gas,
    }


# =============================================================================
# EFC ROTATION CURVE MODEL
# =============================================================================

def v_efc_model(theta, r_kpc, Sigma_star, Sigma_gas, r0_kpc=0.1):
    """
    EFC rotation curve model with Yukawa kernel.
    
    v²(r) = G M_eff(r) / r
    
    where M_eff includes Yukawa-weighted contributions from all radii.
    
    Parameters
    ----------
    theta : [logA, loglam]
        logA: amplitude (mass-to-light scaling)
        loglam: Yukawa range in kpc
    r_kpc : array
        Radial distances
    Sigma_star, Sigma_gas : arrays
        Surface densities in M_sun/pc²
    """
    logA, loglam = theta
    A = np.exp(logA)
    lam = np.exp(loglam)
    
    G = 4.302e-6  # kpc/M_sun * (km/s)²
    
    nr = len(r_kpc)
    dr = np.gradient(r_kpc)
    
    # Total surface density (convert pc² → kpc²)
    Sigma_tot = A * (Sigma_star + Sigma_gas) * 1e6
    
    v2 = np.zeros(nr)
    
    for i in range(nr):
        r = r_kpc[i]
        if r < 0.01:
            continue
        
        # Yukawa-weighted enclosed mass
        M_eff = 0
        for j in range(nr):
            r_prime = r_kpc[j]
            if r_prime < 0.01:
                continue
            
            # Yukawa weight
            dist = np.abs(r - r_prime)
            w = np.exp(-dist / lam) / (dist + r0_kpc)
            
            # Add contribution
            M_eff += Sigma_tot[j] * w * 2 * np.pi * r_prime * dr[j]
        
        # Normalize weights
        v2[i] = G * M_eff / r
    
    return np.sqrt(np.maximum(v2, 0))


def v_newtonian_model(theta, r_kpc, Sigma_star, Sigma_gas):
    """
    Standard Newtonian rotation curve (no dark matter).
    
    For comparison with EFC.
    """
    logA = theta[0]
    A = np.exp(logA)
    
    G = 4.302e-6
    
    nr = len(r_kpc)
    dr = np.gradient(r_kpc)
    
    Sigma_tot = A * (Sigma_star + Sigma_gas) * 1e6
    
    v2 = np.zeros(nr)
    
    for i in range(nr):
        r = r_kpc[i]
        if r < 0.01:
            continue
        
        # Standard enclosed mass (no Yukawa)
        mask = r_kpc <= r
        M_enc = np.sum(Sigma_tot[mask] * 2 * np.pi * r_kpc[mask] * dr[mask])
        
        v2[i] = G * M_enc / r
    
    return np.sqrt(np.maximum(v2, 0))


# =============================================================================
# FITTING
# =============================================================================

def fit_rotation_curve(galaxy_data, model='efc'):
    """
    Fit rotation curve with EFC or Newtonian model.
    
    Returns best-fit parameters and chi².
    """
    r = galaxy_data['r_kpc']
    v_obs = galaxy_data['v_obs']
    v_err = galaxy_data['v_err']
    Sigma_star = galaxy_data['Sigma_star']
    Sigma_gas = galaxy_data['Sigma_gas']
    
    if model == 'efc':
        # EFC: 2 parameters (A, λ)
        def neg_logL(theta):
            if not (np.log(0.1) < theta[0] < np.log(10)): return 1e30
            if not (np.log(0.5) < theta[1] < np.log(50)): return 1e30
            
            v_model = v_efc_model(theta, r, Sigma_star, Sigma_gas)
            chi2 = np.sum(((v_obs - v_model) / v_err)**2)
            return chi2
        
        theta0 = [np.log(1.0), np.log(5.0)]
        result = minimize(neg_logL, theta0, method='Nelder-Mead')
        
        A = np.exp(result.x[0])
        lam = np.exp(result.x[1])
        v_best = v_efc_model(result.x, r, Sigma_star, Sigma_gas)
        
        return {
            'model': 'EFC',
            'A': A,
            'lambda_kpc': lam,
            'chi2': result.fun,
            'chi2_red': result.fun / (len(r) - 2),
            'v_model': v_best,
        }
    
    else:
        # Newtonian: 1 parameter (A)
        def neg_logL(theta):
            if not (np.log(0.1) < theta[0] < np.log(10)): return 1e30
            
            v_model = v_newtonian_model(theta, r, Sigma_star, Sigma_gas)
            chi2 = np.sum(((v_obs - v_model) / v_err)**2)
            return chi2
        
        theta0 = [np.log(1.0)]
        result = minimize(neg_logL, theta0, method='Nelder-Mead')
        
        A = np.exp(result.x[0])
        v_best = v_newtonian_model(result.x, r, Sigma_star, Sigma_gas)
        
        return {
            'model': 'Newtonian',
            'A': A,
            'chi2': result.fun,
            'chi2_red': result.fun / (len(r) - 1),
            'v_model': v_best,
        }


# =============================================================================
# MAIN TEST
# =============================================================================

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("=" * 60)
    print("SPARC ROTATION CURVE TEST FOR EFC")
    print("=" * 60)
    
    # Create example galaxy
    galaxy = create_example_galaxy()
    print(f"\nGalaxy: {galaxy['name']}")
    print(f"Radii: {galaxy['r_kpc'].min():.1f} - {galaxy['r_kpc'].max():.1f} kpc")
    print(f"Max v_obs: {galaxy['v_obs'].max():.0f} km/s")
    
    # Fit with both models
    print("\nFitting Newtonian model...")
    fit_newton = fit_rotation_curve(galaxy, model='newtonian')
    print(f"  A = {fit_newton['A']:.3f}")
    print(f"  χ² = {fit_newton['chi2']:.1f}, χ²_red = {fit_newton['chi2_red']:.2f}")
    
    print("\nFitting EFC model...")
    fit_efc = fit_rotation_curve(galaxy, model='efc')
    print(f"  A = {fit_efc['A']:.3f}")
    print(f"  λ = {fit_efc['lambda_kpc']:.2f} kpc")
    print(f"  χ² = {fit_efc['chi2']:.1f}, χ²_red = {fit_efc['chi2_red']:.2f}")
    
    # Key comparison
    print("\n" + "=" * 60)
    print("KEY COMPARISON")
    print("=" * 60)
    print(f"Δχ² (Newton - EFC) = {fit_newton['chi2'] - fit_efc['chi2']:.1f}")
    
    if fit_efc['chi2'] < fit_newton['chi2']:
        print("→ EFC fits BETTER than pure Newtonian")
    else:
        print("→ Newtonian fits better (EFC not needed)")
    
    # Compare λ with cluster result
    lambda_cluster_kpc = 250  # From Bullet ~1.5' at z=0.3
    print(f"\nλ comparison:")
    print(f"  Galaxy: {fit_efc['lambda_kpc']:.1f} kpc")
    print(f"  Cluster: ~{lambda_cluster_kpc} kpc")
    print(f"  Ratio: {lambda_cluster_kpc / fit_efc['lambda_kpc']:.0f}×")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    ax = axes[0]
    ax.errorbar(galaxy['r_kpc'], galaxy['v_obs'], yerr=galaxy['v_err'],
                fmt='ko', label='Observed', capsize=3)
    ax.plot(galaxy['r_kpc'], fit_newton['v_model'], 'b--', lw=2, 
            label=f"Newton (χ²={fit_newton['chi2']:.0f})")
    ax.plot(galaxy['r_kpc'], fit_efc['v_model'], 'r-', lw=2,
            label=f"EFC λ={fit_efc['lambda_kpc']:.1f}kpc (χ²={fit_efc['chi2']:.0f})")
    ax.set_xlabel('r (kpc)')
    ax.set_ylabel('v (km/s)')
    ax.set_title('Rotation Curve')
    ax.legend()
    
    ax = axes[1]
    ax.plot(galaxy['r_kpc'], galaxy['Sigma_star'], 'orange', lw=2, label='Σ_star')
    ax.plot(galaxy['r_kpc'], galaxy['Sigma_gas'], 'blue', lw=2, label='Σ_gas')
    ax.set_xlabel('r (kpc)')
    ax.set_ylabel('Σ (M☉/pc²)')
    ax.set_title('Surface Density')
    ax.set_yscale('log')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('/home/claude/sparc_data/sparc_test_example.png', dpi=150)
    print(f"\nSaved: sparc_test_example.png")
    
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print(f"""
For this example galaxy:
  - EFC with λ = {fit_efc['lambda_kpc']:.1f} kpc fits the rotation curve
  - This is ~{lambda_cluster_kpc / fit_efc['lambda_kpc']:.0f}× smaller than cluster λ
  
What this means:
  - If λ were universal, galaxy should need λ ~ 250 kpc
  - But best fit gives λ ~ {fit_efc['lambda_kpc']:.0f} kpc
  - λ appears to SCALE with system size

This suggests:
  - λ is NOT a universal constant
  - Or: λ scales with some physical property (mass, density, size)
  - Or: The 1D rotation curve model is too simplified
  
NEXT: Test on real SPARC data with proper 2D disk potential
""")
