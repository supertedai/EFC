# EFC Falsification Criteria

> **Status:** EFC is currently consistent with late-time data at the
> ~2 sigma level and remains a candidate extension of LCDM pending
> CMB validation.

These are explicit, pre-registered conditions under which EFC would be
considered falsified.  A testable model must define where it fails.

---

## F1: CMB power spectrum deviation (KILL)

**Condition:** EFC predicts any deviation from LCDM at z > 1100 (CMB decoupling).

**Threshold:** |D C_l / C_l| > 0.1% for any multipole l in Planck TTTEEE.

**Why this kills EFC:** The regime framework requires L0 (CMB scales)
to recover LCDM exactly.  Any modification at CMB scales means the
regime boundary is wrong.

**Data needed:** Planck 2018 + future CMB-S4.
**Status:** Sanity checks pass (GR recovery at z=1100, ISW +0.3%,
dClTT ~1% at ell=66).  However, sanity checks verify necessary
conditions only — they are NOT a likelihood test.  Full Boltzmann
analysis (plik_lite TTTEEE) is pending.  This remains the single
most critical unresolved test for EFC.

## F2: mu > 1 at late times (KILL)

**Condition:** If data require mu > 1 (strengthened gravity) at z < z_t
to fit growth-rate observations.

**Threshold:** Best-fit mu_0 > 1.0 at > 3 sigma.

**Why this kills EFC:** The sign constraint (B0 Bridge Test) shows
mu > 1 is excluded by Dchi^2 = +495 to +2680.  The entropy mechanism
predicts mu < 1 at late times.

**Data needed:** Future DESI DR3 + Euclid DR1 fsigma_8 measurements.
**Status:** Currently excluded. Locked by existing data.

## F3: AQUAL void leakage (KILL)

**Condition:** If AQUAL nonlinearity activates in low-density void regions,
modifying ISW cross-correlation, void lensing, or growth at k < 0.02 h/Mpc.

**Threshold:** ISW-void cross-correlation amplitude deviates from LCDM
by > 5%.  Or void lensing tangential shear shows AQUAL enhancement at
r > 10 Mpc/h.

**Why this kills EFC:** Voids are low-acceleration environments that are
cosmologically relevant and not screened.  If AQUAL leaks here, the
LCDM-as-L0/L1-limit claim is broken.

**Data needed:** BOSS/DESI void catalogs, DES Y6/KiDS void lensing.
**Status:** Tier-1 falsification test (planned).

## F4: Sigma_8 tension reversal (DAMAGE)

**Condition:** Future lensing surveys find sigma_8 consistent with
Planck LCDM (sigma_8 = 0.811 +/- 0.006) with no S8 tension.

**Threshold:** S8 tension reduced to < 1 sigma across all Stage-IV surveys.

**Why this damages EFC:** The primary motivation for EFC's growth
suppression mechanism disappears.  EFC becomes an unnecessary extension.

**Data needed:** Euclid DR1 + LSST Y1 + CMB-S4 combined.
**Status:** Current tension at ~2-3 sigma from KiDS/DES.

## F5: Unified chi^2 significantly worse (DAMAGE)

**Condition:** When tested on all probes jointly (BAO + SN + RSD + CMB),
EFC has Dchi^2 > +5 relative to LCDM.

**Threshold:** Dchi^2 > +5 (33+ data points, EFC penalised by > 2 extra
parameters).

**Why this damages EFC:** The framework claims non-rejection.  A significant
penalty means EFC is disfavoured by data.

**Data needed:** DESI DR2 final + Pantheon+ + Planck.
**Status:** Current unified result: Dchi^2 = +1.72 (within tolerance).

## F6: Rotation curve failure mode (DAMAGE)

**Condition:** EFC phenomenological model fails for > 50% of SPARC galaxies
(chi^2/dof > 3) in the FLOW regime.

**Threshold:** EFC win rate drops below 40% on SPARC-175.

**Why this damages EFC:** The rotation curve analysis is a key cross-check
of the entropy-structure coupling mechanism.

**Data needed:** SPARC + MaNGA extended sample.
**Status:** Current win rate: 60.2%.

## F7: Gravitational slip eta = 1 (KILL for perturbation sector)

**Condition:** If Stage-IV data establish eta = 1 at > 3 sigma
across all scales and redshifts.

**Threshold:** eta consistent with 1.00 at 3 sigma in Euclid/Rubin
tomographic bins.

**Why this kills EFC perturbation sector:** The EFC mechanism
requires anisotropic stress (eta != 1) from the Lagrange-multiplier
flow constraint.  If eta = 1, the slip sector is falsified.

**Data needed:** Euclid DR1 + Rubin LSST weak lensing + galaxy clustering.
**Status:** Untested.  Source: DOI:10.6084/m9.figshare.32037990, FA4.

## F8: No viable (mu, Sigma) region (KILL for perturbation sector)

**Condition:** If parameter sweeps find zero physical solutions
satisfying mu in [0.93, 0.96] and Sigma in [1.03, 1.07] simultaneously.

**Why this kills EFC:** The action must admit a region where growth
is suppressed (mu < 1) while lensing is enhanced (Sigma > 1).
Without this, the perturbation sector mechanism fails.

**Status:** Currently 15 solutions found in 135,000-point scan.
Mu < 1 robust (100%), Sigma > 1 semi-robust (61%).
Source: DOI:10.6084/m9.figshare.32037990, FA5.

## F9: Sigma_eff(z) monotonic (KILL for lensing crossover)

**Condition:** If Sigma_eff(z) is monotonically decreasing or
increasing across all redshifts, with no sign change.

**Why this kills the prediction:** The lensing crossover at z ~ 0.44
is the distinctive observable signature of EFC.  A monotonic profile
is degenerate with standard modified gravity models.

**Data needed:** Euclid DR1 tomographic cosmic shear (4+ z-bins).
**Status:** Pre-registered prediction.  Untested.
Source: DOI:10.6084/m9.figshare.32037990, FA-new.

---

## Summary table

| ID | Type | Observable | Threshold | Status |
|----|------|-----------|-----------|--------|
| F1 | KILL | CMB C_l | DC_l/C_l > 0.1% | Sanity pass, likelihood pending |
| F2 | KILL | mu_0 | mu_0 > 1 at 3sigma | Excluded |
| F3 | KILL | Void ISW/lensing | >5% LCDM deviation | Planned |
| F4 | DAMAGE | S8 tension | <1 sigma | Monitoring |
| F5 | DAMAGE | Unified chi^2 | Dchi^2 > +5 | Current +1.72 |
| F6 | DAMAGE | SPARC win rate | <40% | Current 60.2% |
| F7 | KILL | Grav. slip eta | eta = 1 at 3sigma | Untested |
| F8 | KILL | (mu, Sigma) region | Zero solutions | 15 found (semi-robust) |
| F9 | KILL | Sigma_eff monotonic | No crossover | Pre-registered |

## Interpretation

- **KILL:** Would fundamentally invalidate the EFC framework.
- **DAMAGE:** Would weaken motivation but not necessarily invalidate.
  EFC could survive with reduced scope.
