# Reproduction Guide

Complete step-by-step instructions to reproduce all results from the paper.

**Expected time:** ~2 hours  
**Requirements:** Python 3.8+, standard scientific stack

## Quick Start

```bash
# 1. Clone repository
git clone [your-repo-url]
cd EFC-Regime-Transition-Framework-A-CMB-Consistent-Approach-to-Late-Time-Cosmology

# 2. Install dependencies
pip install numpy scipy matplotlib

# 3. Run solver
cd code
python landau_solver.py

# 4. Verify output
ls ../data/gz_solution.csv
```

## Step-by-Step Reproduction

### Step 1: Solve Landau Equation

```bash
cd code
python landau_solver.py
```

**Output:**
- `../data/gz_solution.csv` - Complete G(z) solution (15,000 points)

**Expected key results:**
```
G(z=1100) = 1.00×10⁻¹²  ← CMB epoch
G(z=10)   = 9.20×10⁻¹⁶  ← ISW epoch
G(z=2)    = 0.25        ← Activation starting
G(z=0)    = 0.9999      ← Today
```

### Step 2: Verify CMB Safety

```bash
python cmb_safety_check.py
```

**Checks:**
- Point evaluation at z=1100
- Visibility-weighted average
- Extended window [900, 1300]
- Sensitivity to parameters

**Expected:** All checks pass with 8 orders of magnitude margin.

### Step 3: Generate Figures

```bash
cd plotting
python generate_figure1.py  # Regime transition dynamics
python generate_figure2.py  # CLASS integration results
```

**Output:**
- `../../figures/figure1_regime_transition_dynamics.png`
- `../../figures/figure2_class_integration_results.png`

### Step 4: (Optional) CLASS Integration

**Requirements:** CLASS v3.2.0

```bash
# Download CLASS
wget https://github.com/lesgourg/class_public/archive/v3.2.0.tar.gz
tar -xzf v3.2.0.tar.gz
cd class_public-3.2.0

# Compile
make

# Run baseline
./class ../docs/class_planck2018.ini

# Compare with paper results
python ../code/compare_class_output.py
```

## Parameter Variations

To test different parameters, edit `../data/parameters.json`:

```json
{
  "regime_transition": {
    "chi_c": 1.0,      ← Change critical point
    "z_transition": 50, ← Change transition redshift
    "alpha": 10.0       ← Change coupling strength
  }
}
```

Then rerun `landau_solver.py`.

## Verification Checklist

✅ **Numerical convergence**
```bash
python test_convergence.py
# Tests: N=1000, 5000, 15000, 30000
# Expected: Converged at N=15000
```

✅ **CMB safety**
```bash
python cmb_safety_check.py
# Expected: G_CMB < 10⁻⁴ by 8 orders
```

✅ **Parameter sensitivity**
```bash
python parameter_scan.py
# Scans: χ_c ∈ [0.5, 1.5], z_t ∈ [20, 500]
# Expected: Robust CMB safety across range
```

## Troubleshooting

**Problem:** Integration fails / produces NaN

**Solution:** Check parameters in `parameters.json`:
- τ must be > 0
- b must be > 0
- φ_init should be small (10⁻⁶)

**Problem:** G(z=1100) > 10⁻⁴

**Solution:** This indicates CMB contamination. Check:
- χ_early must be < χ_c
- z_transition must be < 500
- Try increasing α or decreasing χ_early

**Problem:** Figures don't match paper

**Solution:** Ensure you're using exact parameters from `parameters.json`:
- Planck 2018 cosmology
- Fiducial regime parameters
- N=15000 grid points

## Expected Outputs

### Data files

1. `gz_solution.csv` (15,000 rows × 4 columns)
   - Columns: z, χ(z), φ(z), G(φ)
   - Size: ~1 MB

2. `cmb_verification.csv`
   - CMB safety verification data
   - Visibility-weighted averages

### Figures

1. `figure1_regime_transition_dynamics.png` (1920×1440 px)
   - 4 panels showing complete solution
   
2. `figure2_class_integration_results.png` (1920×1440 px)
   - 5 panels showing CLASS results

## Performance

**Typical runtime (Intel i5 / Ryzen 5):**
- Landau solver: 30 seconds
- CMB verification: 10 seconds
- Figure generation: 20 seconds
- Total: ~1 minute

**Memory usage:** <500 MB

## Citation

If you reproduce these results, please cite:

```
Magnusson, M. (2026). Dynamical Regime Transitions in Cosmology.
DOI: 10.6084/m9.figshare.31096951
```

## Support

**Issues:** Use GitHub Issues  
**Questions:** See main README.md  
**Updates:** Check DOI page for latest version

---

**Last updated:** 2026-01-20  
**Version:** 1.0
