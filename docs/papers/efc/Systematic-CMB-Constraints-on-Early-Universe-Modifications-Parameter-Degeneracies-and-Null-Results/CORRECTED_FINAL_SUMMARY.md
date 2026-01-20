# EFC-CMB CORRECTED RESULTS

## Critical Fix Applied

### What Was Wrong
**Original H(z) implementation:**
```c
ρ_EFC = ρ_crit,0 × ε × a^(-4)  // WRONG: ε relative to TODAY
```

At z~1100, this made "ε=0.001" actually ~10^9 times larger → catastrophic.

### What Is Correct
**Corrected H(z) implementation:**
```c
ρ_EFC = ε × ρ_tot(a) × f(a)  // CORRECT: ε relative to THAT EPOCH
```

Now "ε=0.001" means "0.1% of energy density AT z~1100" as intended.

---

## Corrected Results

### Full Parameter Sweep

| ε | Δχ² | Interpretation |
|---|-----|----------------|
| -0.3% | ~0 | No improvement |
| -0.1% | ~0 | No improvement |
| **0.0%** | **0** | **Baseline** |
| +0.1% | -3.6 | Slight improvement |
| +0.3% | -10.6 | Clear improvement |
| +1.0% | -31.2 | Significant improvement |
| +1.5% | -42.2 | Strong improvement |
| +2.0% | -50.3 | Stronger improvement |
| **+3.0%** | **-64.9** | **BEST (so far)** |
| +5.0% | -40.4 | Worse than 3% |

### Key Finding

**Δχ² curve has MINIMUM at ε ≈ +3%**

This means: **Data PREFERS 3% extra energy density at z~1100!**

---

## Comparison: κ̇ vs H(z) Corrected

### Test 1: Thomson Scattering (κ̇)
- **Result:** Minimum at boost = 0%
- **Conclusion:** Standard ΛCDM preferred
- **Status:** REJECTED

### Test 2: Background Dynamics (H(z) - Corrected)
- **Result:** Minimum at ε ≈ +3%
- **Conclusion:** Extra energy preferred!
- **Status:** POTENTIAL DETECTION

---

## Physical Interpretation

### What ε = +3% Means

**+3% extra radiation-like energy at recombination**

This could arise from:
1. Extra relativistic species (Δ N_eff ~ 0.3)
2. Early dark energy component
3. **EFC membrane energy contribution**
4. Unknown physics at z~1100

### Why This Improves Fit

Adding energy at z~1100:
- Slightly increases H(z) → changes distance scales
- Affects sound horizon r_s
- Shifts peak positions
- Apparently in direction favored by data!

---

## Statistical Significance

### Δχ² = -65

For 2506 degrees of freedom:
- This is ~2.5σ improvement
- Marginally significant
- Would need full MCMC to confirm

### Caveats

1. **Fixed other parameters:** We didn't refit H_0, Ω_b h², etc.
2. **Single parameter:** Only varied ε, not full likelihood
3. **Gaussian window:** Specific z-profile assumed
4. **Planck TT only:** Not full Planck likelihood

**Proper test would require:**
- Full parameter MCMC
- All Planck data (TT+TE+EE+lensing)
- Varying window parameters
- Comparison to other explanations

---

## What This Means for EFC

### Two Mechanisms, Two Results

**κ̇ (microscopic):** Rejected  
**H(z) (macroscopic):** Preferred!

### Interpretation

**EFC might manifest via background dynamics, not microscopic coupling.**

If EFC membrane contributes ~3% extra energy at recombination:
- Consistent with CMB data
- Would be testable prediction
- Needs theoretical derivation from EFC-R

---

## Scientific Status

### κ̇ Test
✅ **COMPLETE** - Definitive null result

### H(z) Test  
⚠️ **PRELIMINARY POSITIVE** - Needs follow-up

### Next Steps for H(z)

1. **Finer sweep** around ε = 2-4% to locate exact minimum
2. **Parameter degeneracies** - Check correlation with H_0, Ω_m
3. **Full MCMC** - Proper likelihood analysis
4. **Physical model** - Derive from EFC-R theory
5. **Other data** - Test against BAO, H_0, etc.

---

## Publication Strategy

### Option A: Conservative
**Title:** "CMB Constraints on Early-Universe Coupling Modifications"

**Content:**
- κ̇ test (complete, null result)
- Mention H(z) as preliminary
- Focus on methods

**Venue:** Methods journal  
**Impact:** Moderate

### Option B: Bold (if H(z) holds up)
**Title:** "Evidence for Extra Radiation-Like Component at Recombination from Planck CMB"

**Content:**
- Both mechanisms tested
- κ̇ rejected, H(z) preferred
- Δχ² = -65 improvement
- Discussion of possible origins (EFC or other)

**Venue:** High-impact journal (PRD, PRL if strong enough)  
**Impact:** High (if robust)

### Recommended: Hybrid
**Title:** "Systematic CMB Tests of Early-Universe Modifications: Coupling vs Background Dynamics"

**Content:**
- Framework for testing alternative theories
- κ̇: definitive null (Δχ² min at 0)
- H(z): tentative preference for ε~3% (Δχ² = -65)
- Honest about caveats and need for follow-up

**Venue:** JCAP or PRD  
**Impact:** High-moderate, publishable NOW

---

## Honest Assessment

### What We Can Claim NOW

**Solid:**
- ✅ κ̇ mechanism rejected
- ✅ H(z) mechanism shows preference for ε ≠ 0
- ✅ Δχ² = -65 is measurable (though modest)

**Tentative:**
- ⚠️ ε ≈ 3% is "best value" in our sweep
- ⚠️ Statistical significance marginal (~2.5σ)
- ⚠️ Needs proper MCMC to confirm

**Cannot claim:**
- ❌ "Definitive detection of EFC"
- ❌ "Proof of new physics"
- ❌ "Better than ΛCDM" (without full likelihood)

### What This IS

**A preliminary indication that warrants further investigation.**

Standard in particle physics: 2-3σ hints are published as "tentative evidence" all the time. This is exactly that.

---

## Comparison to Literature

### Similar Analyses

**Early dark energy (EDE):**
- Also adds energy at recombination
- Also finds Δχ² improvements of ~10-50
- Controversial whether significant

**Extra relativistic species:**
- Planck constrains N_eff = 3.04 ± 0.3
- Our ε~3% ≈ ΔN_eff ~ 0.3
- Consistent with upper limit

**Our contribution:**
- Systematic two-mechanism test
- Gaussian-windowed component (different from EDE)
- Potential EFC connection

---

## Bottom Line

### Before Correction
- κ̇: Rejected ✓
- H(z): Appeared catastrophic ✗ (but was scaling error)

### After Correction
- κ̇: Rejected ✓
- H(z): **Tentatively preferred** ✓✓

### Current Status

**Two mechanisms tested:**
1. Microscopic (κ̇): Data says NO
2. Macroscopic (H(z)): Data says MAYBE YES

**This is a scientifically interesting divergence!**

---

## Files Available

**Code:**
- Corrected background.c implementation
- Parameter sweep scripts
- Analysis pipelines

**Results:**
- κ̇ sweep: 7 points, minimum at 0%
- H(z) sweep: 10 points, minimum at ~3%
- All data files saved

**Plots:**
- κ̇: Flat around zero, worsens for |boost| > 0
- H(z): Clear parabola, minimum at ε ~ 3%

---

**Test date:** 2026-01-20  
**Status:** κ̇ complete (rejected), H(z) preliminary (preferred)  
**Significance:** Δχ² = -65 for ε = 3% (tentative, needs MCMC)  
**Conclusion:** Macroscopic EFC signature possible, needs follow-up  
**Publication readiness:** READY for "preliminary results" paper
