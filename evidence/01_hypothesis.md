# EFC Core Hypotheses

> **Status:** EFC is currently consistent with late-time data at the
> ~2 sigma level and remains a candidate extension of LCDM pending
> CMB validation.  The strongest signal (fsigma_8) is suggestive but
> not decisive.  Following DESI DR2, the background-sector signal
> collapsed from 2.2 sigma to 0.68 sigma; the perturbation sector
> (mu, Sigma, eta) is now the primary channel.

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

**DESI DR2 update:** The background coupling parameter alpha collapsed
from -1.00 +/- 0.46 (2.2 sigma) to -0.14 +/- 0.21 (0.68 sigma),
eliminating the background-sector signal.  The Variant H MCMC growth
test (S_0 = 0.21 +/- 0.14, DAIC = +4.05) shows no current data
preference for the entropy-gradient growth mechanism.

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

## H5: Constraint-driven gravitational slip (mu < 1, Sigma >= 1)

The EFC Lagrange-multiplier flow constraint generates anisotropic stress
absent in standard Horndeski theories, enabling a regime where mu < 1
(growth suppression) and Sigma >= 1 (lensing enhancement) simultaneously.

Standard quasi-static Horndeski with alpha_T = 0 CANNOT produce this
signature (proven: Sigma <= mu universally in that framework).

**Testable consequence:** A redshift-dependent lensing crossover at
z ~ 0.44 with percent-level amplitude.  Sigma_eff > 1 at z < 0.4
(enhanced lensing), Sigma_eff < 1 at z > 0.5 (suppressed lensing).
This non-monotonic tomographic signature is absent in LCDM.

**Status:** Structural mechanism derived from action (DOI:10.6084/m9.figshare.32037990).
Parameter sweep finds 15 viable solutions out of 135,000 scanned.
Robustness: mu < 1 robust (100%), Sigma > 1 semi-robust (61%),
exact valley fragile (0%).  Reformulated as structural prediction
(mu < 1 AND Sigma >= 1) rather than point prediction.

**Negative result (Variant H):** Current growth-rate data show no
preference for the extension (DAIC = +4.05, S_0 = 0.21 +/- 0.14 at
1.5 sigma).  Signal may be below current sensitivity.

---

## Mapping to code

| Hypothesis | Verification script | Function |
|------------|-------------------|----------|
| H1 | `reproduce_efc.py` test 4-5 | `compute_fsigma8()`, `chi2_fsigma8()` |
| H2 | `reproduce_efc.py` test 8 | `mu_of_a()` at a=0.01 -> 1.0 |
| H3 | `reproduce_efc.py` test 8 | `mu_less_than_1`, `mu_positive` |
| H4 | `reproduce_efc.py` test 1,6 | `verify_sign_lemma()`, `delta_E2()` |
| H5 | `reproduce_cmb_sanity.py` test 2-3 | `mu_efc()`, `sigma_efc()`, `eta_efc()` |
