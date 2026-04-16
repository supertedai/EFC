# EFC Core Hypotheses

> **Status:** EFC is currently consistent with late-time data at the
> ~2 sigma level and remains a candidate extension of LCDM pending
> CMB validation.  The strongest signal (fsigma_8) is suggestive but
> not decisive.

## H1: Entropy-driven gravitational modification

Late-time cosmic entropy gradients modify the effective gravitational
coupling, producing mu(a) < 1 at z < z_t.  This suppresses structure
growth (sigma_8) without altering early-universe physics.

**Testable consequence:** sigma_8 from growth-rate data is lower than
the Planck LCDM prediction; fsigma_8(z) at z < 1 is systematically
below the LCDM curve.

**Status:** Suggestive but not decisive (2.2 sigma, DAIC = -2.91).
Below the 3-sigma threshold for a firm detection; currently an indication,
not a claim.  Requires Stage-IV data (DESI DR3, Euclid DR1) to reach
decisive significance.

## H2: Regime-dependent validity

EFC effects are confined to specific regimes:

| Regime | Scale | Behaviour |
|--------|-------|-----------|
| L0 | CMB / linear | LCDM recovered exactly |
| L1 | BAO / quasi-linear | Small perturbative modification |
| L2 | Galaxy / nonlinear | Entropy-structure coupling active |
| L3 | Cluster / strong-field | Full EFC dynamics |

**Testable consequence:** EFC predictions must reduce to LCDM in the
L0 limit.  Any deviation at CMB scales falsifies the framework.

**Status:** Consistent with Planck 2018 (mu-Sigma degeneracy valley found).

## H3: Sign constraint

The perturbation-level coupling mu must satisfy mu < 1 at late times.
mu > 1 (strengthened gravity) is excluded by fsigma_8 data with
Dchi^2 = +495 to +2680.

**Testable consequence:** Any physical mechanism that produces mu > 1
at z < 1 is ruled out.

**Status:** Locked by data (B0 Bridge Test).

## H4: Background sign lemma

The background modification DE^2(z) <= 0 for all z > 0, meaning
H_EFC(z) <= H_LCDM(z) (reduced Hubble friction, enhanced growth).

**Testable consequence:** EFC expansion rate is never faster than LCDM
at any redshift.

**Status:** Proven analytically (Lemma 1) and verified numerically.

---

## Mapping to code

| Hypothesis | Verification script | Function |
|------------|-------------------|----------|
| H1 | `reproduce_efc.py` test 4-5 | `compute_fsigma8()`, `chi2_fsigma8()` |
| H2 | `reproduce_efc.py` test 8 | `mu_of_a()` at a=0.01 -> 1.0 |
| H3 | `reproduce_efc.py` test 8 | `mu_less_than_1`, `mu_positive` |
| H4 | `reproduce_efc.py` test 1,6 | `verify_sign_lemma()`, `delta_E2()` |
