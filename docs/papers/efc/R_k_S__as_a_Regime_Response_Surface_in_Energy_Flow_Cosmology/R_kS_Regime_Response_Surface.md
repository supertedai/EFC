# R(k,S) as a Regime Response Surface in Energy-Flow Cosmology

**A Unified Framework for Structure-Dependent Gravitational Response**

Morten Magnusson  
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

January 2026

**DOI**: [10.6084/m9.figshare.31211437](https://doi.org/10.6084/m9.figshare.31211437)

---

**Scope**: This is a theoretical framework paper. It introduces a coordinate system for gravitational response, derives testable structure, and specifies falsification criteria. It does not perform quantitative fits, MCMC analysis, or Boltzmann-code implementation. Those are subsequent steps that this framework enables.

---

## Abstract

We extend Energy-Flow Cosmology (EFC) phenomenology from time-dependent modified gravity parameters μ(a) and μ(k,z) to a state-dependent response surface R(k,S), where S is a derived, model-dependent state variable quantifying nonlinear structure accumulation. This synthesizes two prior results: the regime-dependent transition estimator (Fugaku–DESI) and the operational μ(k,z) formalism (weak lensing phenomenology). We derive falsification criteria against DES Y6 data. The core prediction: the L1→L2 transition (CMB to late-universe) explains the S₈ tension, not probe-dependent variation within L2. This paper presents theoretical infrastructure for testing, not claimed validation.

---

## Core Postulate

> **The gravitational response μ in late-universe structure formation depends on the accumulated structural state S, not merely on cosmic time.**
>
> Formally: μ = μ(k, S) where S = S(z) is a derived measure of nonlinear maturity.
>
> This implies: (1) μ ≈ 1 when S ≈ 0 (linear regime, CMB epoch), and (2) μ ≠ 1 when S > 0 (nonlinear regime, late universe).
>
> The framework is falsifiable: a single R(k,S) surface must describe all late-universe probes consistently.

---

## Regime Coordinate Principle

> *Different cosmological probes do not measure different physics—they sample different coordinates (k, S) on a single gravitational response surface.*

---

## 1. Introduction: What Are We Modeling?

Cosmological observations present a consistent pattern:

| Regime | Observation | Gravitational behavior |
|--------|-------------|----------------------|
| **L1** (CMB, z~1100) | Planck temperature + polarization | G_eff ≈ G (standard GR) |
| **L2** (Late universe, z<2) | Weak lensing, RSD, cluster counts | G_eff > G (enhanced growth) |

The S₈ tension—where late-universe probes consistently measure S₈ ≈ 0.78–0.79 while CMB implies S₈ ≈ 0.83—can be interpreted as evidence that **gravitational response depends on structural state**.

This interpretation does not require new gravity everywhere. It requires a **response function** that activates when the universe transitions from linear to nonlinear structure formation.

Two prior EFC papers establish the foundation:

1. **Fugaku–DESI Transition Metric** (doi:10.6084/m9.figshare.31144030.v1): Demonstrates that a single μ(a) function satisfying μ≈1 at recombination and μ>1 at late times can reinterpret apparent matter density offsets as regime-dependent gravitational coupling.

2. **EFC Weak Lensing Phenomenology** (doi:10.6084/m9.figshare.31188193.v1): Introduces an operational closure (Postulate A) yielding μ(k,z) in standard cosmological perturbation form, enabling direct comparison with survey data.

The present work extends these results by replacing **cosmic time (z)** with **structural state (S)** as the fundamental variable controlling gravitational response.

---

## 2. Existing EFC Foundation

### 2.1 μ(a): Regime-Dependent Coupling (Fugaku–DESI)

The Fugaku–DESI analysis defines a transition estimator:

$$\Delta_F \equiv \int W(a)\,[\mu(a)-1]\,d\ln a$$

where W(a) represents the observational sensitivity window. Key results:

- **μ ≈ 1 at recombination**: Preserves CMB constraints
- **μ > 1 at late times**: Consistent with enhanced structure growth
- **Δ_F ≈ 0.1**: Empirical constraint on integrated transition strength

This establishes that **one transition function can connect multiple regimes**.

### 2.2 μ(k,z): Operational Field Closure (Weak Lensing)

The weak lensing phenomenology paper derives:

$$k^2 \Phi = -4\pi G a^2 \mu(k,z)\,\bar{\rho}\,\delta$$

where μ(k,z) emerges from Postulate A coupling entropy production to matter density. This places EFC in **standard cosmological perturbation formalism**, enabling direct interface with Boltzmann solvers and survey likelihood codes.

---

## 3. S as a Structural State Variable

### 3.1 Physical Motivation

Cosmic time z is a **proxy** for what physically matters: the degree of nonlinear structure accumulation. We therefore define a structural maturity parameter:

$$S(z) \equiv \ln\left[\frac{\sigma^2(R_8, z)}{\sigma^2_{\text{lin}}(R_8, z)}\right]$$

where R₈ = 8 h⁻¹ Mpc is the standard smoothing scale and σ²_lin is the linear-theory prediction.

### 3.2 Operational Definition

For practical implementation, S can be computed as:

$$S(z) = \ln\left[\frac{\sigma_8^2(z)}{\sigma_{8,\text{lin}}^2(z)}\right] = \ln\left[\frac{D^2(z) \cdot \sigma_8^2(z=0)}{D^2_{\text{lin}}(z) \cdot \sigma_{8,\text{lin}}^2(z=0)}\right]$$

This is deterministic given a background cosmology—**S is not a free parameter per data point**.

### 3.3 Regime Interpretation

| Regime | S value | Physical meaning |
|--------|---------|------------------|
| **L1** (CMB) | S ≈ 0 | Linear universe, σ ≈ σ_lin |
| **L1→L2 transition** | 0 < S < 1 | Nonlinear growth initiating |
| **Late L2** | S > 1 | Structure-dominated dynamics |

This makes the model **regime-based** (EFC-consistent), **operationally defined** (S is computable from observables under a specified nonlinear mapping), and **physically grounded** (S measures accumulated nonlinearity).

**Important caveat**: S depends on the choice of smoothing scale (R₈), nonlinear model (halofit, emulator, or N-body calibration), and reference linear prediction. It is therefore a *derived* state variable, not a direct observable.

**Robustness**: Different nonlinear prescriptions yield monotonic transformations of S, preserving regime ordering even when the exact numerical scale varies. The physically meaningful content is the *ordering* of states (S₁ < S₂ implies less nonlinear structure), not the absolute value. This makes the framework robust against reasonable methodological choices in computing S.

---

## 4. The R(k,S) Response Surface

### 4.1 Definition

We generalize the modified gravity parameter to:

$$\mu(k,S) = 1 + R(k,S)$$

where R(k,S) is the **regime response function** encoding how gravitational coupling deviates from GR as a function of both scale k and structural state S.

**Critical constraint**: R(k,S) is not a free function per probe; it is a single global surface that must simultaneously describe all late-universe observables. This is what makes the framework falsifiable.

### 4.2 Minimal Parametrization

A first-order Taylor expansion around a reference point (k₀, S₀):

$$R(k,S) = R_0 \left[1 + a\ln\left(\frac{k}{k_0}\right) + b(S-S_0) + c\ln\left(\frac{k}{k_0}\right)(S-S_0)\right]$$

This expansion is phenomenological and valid only locally in (k,S)-space around the reference point (k₀, S₀).

**Theoretical justification**: Locally, any smooth response surface can be expanded to first order; this represents the most general phenomenological form near a reference regime point. The logarithmic scale dependence ln(k/k₀) is standard in modified gravity phenomenology and ensures dimensionless coefficients.

**Reference point choice**: The point (k₀, S₀) should be chosen in a regime where data are most constraining—typically k₀ ~ 0.1 h/Mpc (linear-to-nonlinear transition) and S₀ corresponding to z ~ 0.5 (DES effective redshift). This is a coordinate choice, not an additional free parameter; different choices yield equivalent physics under parameter redefinition.

**Parameters:**
- **R₀**: Overall response amplitude
- **a**: Scale dependence (positive = stronger response at small scales)
- **b**: State dependence (positive = stronger response at higher S)
- **c**: Scale–state interaction (allows same R surface to produce different trends at different k)

**Limiting case**: Setting c = 0 reduces the model to separable scale and state dependence, providing a controlled null hypothesis for testing the interaction term.

### 4.3 Effect on Structure Growth

In linear perturbation theory, μ > 1 enhances the gravitational source term, modifying the growth equation. To first order, positive R(k,S) leads to *enhanced* gravitational response relative to GR, with magnitude depending on the integrated response history along the structure formation trajectory.

**Note**: The precise mapping from R(k,S) to observable quantities (S₈, fσ₈, etc.) requires solving the modified perturbation equations. The relation is not a simple multiplicative correction but depends on the full growth history.

---

## 5. DES Y6 Consistency and the L1↔L2 Test

### 5.1 Key Observational Fact

Recent DES Year 6 analyses report:

- **3×2pt S₈** ≈ 0.79 (with uncertainty ~0.01)
- **CMB (Planck+ACT+SPT) S₈** ~ 0.83
- **Tension**: ~2σ in full parameter space

Critically, DES Y6 shows **good internal consistency** between cosmic shear, galaxy clustering, and galaxy-galaxy lensing. The tension is not between L2 probes—it is between L1 (CMB) and L2 (late universe).

### 5.2 Model Prediction

The R(k,S) framework predicts this pattern:

| Epoch | S value | R(k,S) | Observed S₈ |
|-------|---------|--------|-------------|
| CMB (z~1100) | S ≈ 0 | R ≈ 0 | ~0.83 (Planck) |
| DES (z~0.3–1.0) | S > 0 | R > 0 | ~0.79 (suppressed) |

The sign of R determines whether inferred S₈ is enhanced or suppressed relative to the ΛCDM baseline. In this framework, R > 0 (enhanced μ) leads to *lower* inferred S₈ from late-universe probes. The physical intuition: a stronger effective gravitational coupling allows observed clustering to arise from a lower primordial fluctuation amplitude—gravity does more work, so less initial "seed" is needed. When late-universe surveys assume standard gravity but the true coupling is enhanced, they underestimate how much gravity has amplified structure, leading to a lower inferred S₈.

The **gradient in S** explains the L1→L2 offset without requiring different physics for different L2 probes.

### 5.3 Why L2 Probes Are Internally Consistent

Different late-universe probes (WL, RSD, clusters) sample different (k, S) windows on the same response surface. If the c coefficient (k×S interaction) is small, they see similar R values. This explains:

✓ WL and galaxy clustering agreeing within L2  
✓ Both disagreeing with CMB (different S regime)

---

## 6. Falsification Protocol

### 6.1 Test 1: Tomographic Consistency

DES Y6 provides tomographic bins across redshift. **All bins must follow a single global R(k,S)** with fixed (R₀, a, b, c). 

**Failure criterion**: Fitting requires different parameters per bin.

### 6.2 Test 2: Trend Sign Matching

When two probes are matched to the same k-window AND the same S/z-window, they must show the same trend sign in any residuals from ΛCDM.

**Failure criterion**: Probes with overlapping (k,S) coverage show opposite deviations.

### 6.3 Test 3: Predicted S-Gradient

Given R(k,S), compute the predicted S₈ offset as a function of effective redshift:

$$\Delta S_8(z_{\text{eff}}) \propto R(k_{\text{eff}}, S(z_{\text{eff}}))$$

This predicted gradient must be consistent with observed redshift trends in late-universe probes.

**Failure criterion**: Predicted gradient disagrees with observed redshift evolution in tomographic analyses.

---

## 7. Epistemic Status

| Component | Status |
|-----------|--------|
| Regime-dependent μ | ✅ Supported (Fugaku–DESI) |
| μ(k,z) formalism | ✅ Supported (Weak Lensing paper) |
| S as structural state | ⚠️ New, physically motivated extension |
| R(k,S) response surface | ⚠️ New model structure |
| k×S interaction explaining "fit vs. non-fit" | ⚠️ Hypothesis, requires testing |
| L1↔L2 as primary tension locus | ✅ Supported by DES Y6 internal consistency |

This framework does not claim validation. It provides the **minimal theoretical infrastructure** required to test whether EFC can explain structure growth phenomenology.

---

## 8. Conclusion

The R(k,S) framework unifies prior EFC phenomenology into a single response surface:

1. **μ(a)** from Fugaku–DESI → absorbed into S-dependence
2. **μ(k,z)** from Weak Lensing → absorbed into k-dependence
3. **New**: S as state variable, making response physically grounded

The key prediction is that the S₈ tension reflects an **L1→L2 regime transition**, not systematic errors or probe-dependent physics. A single R(k,S) surface should explain:

- μ ≈ 1 at CMB (S ≈ 0)
- μ > 1 at late times (S > 0)
- Internal consistency within L2 (probes sample similar S values)

This is testable with current data. Failure of the tomographic consistency test or the S-gradient prediction would falsify this formulation of EFC structure response.

---

## References

1. Magnusson, M. (2026). "Regime-Dependent Growth Enhancement: A Transition Metric Interpretation of the Fugaku–DESI Matter Density Offset." Figshare. doi:10.6084/m9.figshare.31144030.v1

2. Magnusson, M. (2026). "EFC Weak Lensing Phenomenology." Figshare. doi:10.6084/m9.figshare.31188193.v1

3. DES Collaboration (2026). "Dark Energy Survey Year 6 Results: Cosmological Constraints from the Analysis of Cosmic Shear, Galaxy–Galaxy Lensing, and Galaxy Clustering." arXiv:2601.14559

4. Planck Collaboration (2020). "Planck 2018 results. VI. Cosmological parameters." A&A 641, A6.

---

## Appendix A: Relation to Standard MG Parametrization

In the standard modified gravity literature, perturbations are characterized by:

$$k^2 \Psi = -4\pi G a^2 \mu(k,a)\,\bar{\rho}\,\delta$$
$$\frac{\Phi}{\Psi} = \gamma(k,a)$$

The R(k,S) framework sets:

$$\mu(k,a) = 1 + R(k, S(a))$$
$$\gamma(k,a) = 1 \quad \text{(no gravitational slip in minimal EFC)}$$

**Note on γ**: The choice γ = 1 is a simplifying assumption in this minimal framework, not a fundamental requirement. Future extensions may allow γ ≠ 1 to capture additional degrees of freedom in the gravitational sector. The present framework is modular: R(k,S) can be constrained independently before relaxing the slip assumption.

This is directly implementable in CLASS/CAMB with appropriate modifications.

---

## Appendix B: Computing S from Observables

For a given background cosmology:

```
1. Compute linear growth factor D_lin(z) from perturbation equations
2. Compute nonlinear growth from halofit or N-body calibration
3. S(z) = ln[σ₈²(z) / σ₈²_lin(z)]
```

For DES Y6 tomographic bins:
- Each bin has effective redshift z_eff
- Compute S(z_eff) for each bin
- This provides ~10 points along the S-axis without free parameters

---

*Document version: 1.0 | 30 January 2026*
