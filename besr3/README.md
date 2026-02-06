# BESR3: Entropy Gradient Extraction from TNG-Cluster

## What This Does

Extracts entropy power-law index **alpha_sim** from all 352 TNG-Cluster zoom halos at z=0,
fitting the ACCEPT model:

```
K(r) = K0 + K100 * (r / 100 kpc)^alpha
```

where K = k_B T n_e^{-2/3} is the ICM entropy.

### Key test (BESR3)
The correlation rho(alpha_sim, y_CCT) in simulations should show a **sign flip** relative to
ACCEPT observations (rho_obs = +0.36), because simulations lack the EFC entropy-structure
coupling that produces the observed correlation.

---

## Quick Start

### 1. Get TNG API Key
Register at https://www.tng-project.org/users/login/ and get your API key.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API Key
```bash
# Option A: environment variable
export TNG_API_KEY="your-key-here"

# Option B: .env file
cp .env.template .env
# edit .env with your key
```

### 4. Run Extraction
```bash
# Full run (all 352 halos, ~15-18 hours)
python besr3_extract_alpha.py --output results/

# Pilot run (first 30 halos, ~1.5 hours)
python besr3_extract_alpha.py --start 0 --end 30 --output results/

# Resume from halo 100 (crash-safe, appends to CSV)
python besr3_extract_alpha.py --start 100 --end 352 --output results/
```

### 5. Analyze Results
```bash
python besr3_analyze.py --input results/besr3_alpha_results.csv --output results/plots/
```

---

## Output Files

```
results/
├── halo_catalog.json           # Cached halo list (reused on restart)
├── besr3_alpha_results.csv     # Per-halo: alpha, K0, K100, CC class, etc.
├── besr3_summary.json          # Aggregate statistics
├── besr3_profiles/             # Per-halo radial profiles (.npz)
│   ├── halo_0000.npz
│   ├── halo_0001.npz
│   └── ...
└── plots/                      # Analysis plots
    ├── alpha_distribution.png
    ├── alpha_vs_yCCT.png       # <-- KEY TEST
    ├── alpha_vs_mass.png
    ├── K0_vs_alpha.png
    ├── cc_comparison.png
    ├── entropy_profiles_sample.png
    └── besr3_analysis_report.txt
```

---

## CSV Columns

| Column | Description |
|--------|-------------|
| `halo_id` | FoF halo ID in TNG-Cluster |
| `subhalo_id` | Central subhalo ID |
| `OrigHaloID` | Original halo ID from parent DMO box |
| `M500c_Msun` | M500c in solar masses |
| `R500c_kpc` | R500c in kpc |
| `n_gas` | Number of bound gas cells |
| `n_bins_valid` | Valid radial bins (out of 25) |
| `K0` | Central entropy excess [keV cm^2] |
| `e_K0` | K0 uncertainty |
| `K100` | Entropy normalization at 100 kpc |
| `e_K100` | K100 uncertainty |
| `alpha` | **Entropy power-law index** (the key quantity) |
| `e_alpha` | alpha uncertainty |
| `chi2_dof` | Reduced chi-squared of fit |
| `n_bins_fit` | Number of bins used in fit |
| `CC_class` | Cool-core class: SCC/WCC/NCC |
| `y_CCT_proxy` | log10(K0/K100) -- CCT proxy for correlation test |

---

## CC Classification (Hudson et al. 2010 / Lehle et al. 2024)

- **SCC** (Strong Cool-Core): K0 <= 22 keV cm^2
- **WCC** (Weak Cool-Core): 22 < K0 <= 150 keV cm^2
- **NCC** (Non-Cool-Core): K0 > 150 keV cm^2

---

## Physics Notes

- Gas data: all cells bound to central subhalo (SUBFIND)
- Star-forming cells excluded (effective EOS, not physical T)
- Entropy: K = k_B T * n_e^{-2/3}
- Temperature: from InternalEnergy with mean molecular weight mu(X_e)
- Electron density: n_e = X_e * X_H * rho / m_p
- Radial bins: 25 log-spaced from 10 kpc to R500c
- Mass-weighted averages in each bin
- Minimum 10 cells per bin for validity
- Fit range: 10 kpc to R500c

---

## Early Results (N=6 pilot)

From previous session testing:
- alpha range: 0.41-1.92 (ACCEPT has 0.5-2.5)
- K0 scales with CC class: SCC < WCC < NCC
- Preliminary rho(alpha, y_CCT) = -0.49 (opposite sign to observed +0.36)
- All 6/6 passed QC with 25/25 valid bins

---

## Performance

- ~3 minutes per halo (download + compute)
- Largest halos: ~1.4 GB cutout, 30M+ cells
- Smallest halos: ~50-100 MB cutout, 400k-2M cells
- Total run: ~15-18 hours for all 352
- Crash-safe: results appended to CSV after each halo

---

## Citations

If you use this pipeline, cite:
- Nelson et al. (2024) -- TNG-Cluster simulation
- Nelson et al. (2019) -- TNG data release
- Cavagnolo et al. (2009) -- ACCEPT catalog / entropy model
- Hudson et al. (2010) -- CC classification criteria
- Lehle et al. (2024) -- TNG-Cluster CC/NCC analysis
