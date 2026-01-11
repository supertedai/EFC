# EFC-R Core v1 - Implementation Status

**Date:** 2026-01-11  
**Status:** FROZEN - Ready for regime mapping

## Implementation Features

### ✅ Correctly Implemented
- **Gauge-invariant formulation**: ΔΦ_N(r) = Φ_N(r) - Φ_N(r_max)
- **Numerical Φ_N integration**: ∫(v_b²/r)dr with trapezoid rule
- **Entropy profiles**: 1-scale and 2-scale parametrizations
- **SPARC data parsing**: v_gas, v_disk, v_bulge → v_baryon
- **L-BFGS-B optimization**: with physical parameter bounds
- **Epistemic layers**: L0 (data) → L1 (fits) → L2 (interpretation) → L3 (methodology)

### 🔬 Core Equations (v1)
```
Φ_eff = Φ_N(1 + αS)
v²/r = dΦ_eff/dr = dΦ_N/dr(1+αS) + α·ΔΦ_N·dS/dr

S(r) = S_c + (S_∞ - S_c)[1 - exp(-r/r_S)]
ΔΦ_N(r) = ∫[r to r_max] (v_b²/r')dr'  [gauge-invariant]
```

## Known Limitations (Empirically Validated)

### ❌ Regime B: Flat Outer Rotation Curves
**Galaxies:** NGC3198, NGC2403  
**Symptom:** Model velocity falls (v → ~100 km/s) while observations stay flat (v ~ 150 km/s)  
**Residual:** Systematic ~40 km/s underprediction in outer disk (r > 0.7*r_max)  
**χ²/dof:** 139-309  
**Cause:** dS/dr dies exponentially → α·ΔΦ_N·dS/dr term vanishes → insufficient acceleration at large r

### ❌ Regime C: Ultra-LSB Galaxies  
**Galaxies:** DDO154  
**Symptom:** Model produces constant boost factor instead of radial structure  
**χ²/dof:** 201-211  
**Cause:** Φ_N too weak and featureless → shape term cannot anchor → reduces to amplitude scaling

## Files
- `/home/claude/efc_r_correct.py` - Core implementation (gauge-invariant)
- `/home/claude/two_scale_entropy.py` - 2-scale entropy extension
- `/home/claude/sparc-data/` - SPARC rotation curve data (N=175)

## Next Steps
1. ✅ Regime mapping (works/partial/fails)
2. ⏳ Test 1 dwarf/irregular galaxy
3. ⏳ Document regime boundaries
4. ⏳ Compare with SPARC N=20 paper results
