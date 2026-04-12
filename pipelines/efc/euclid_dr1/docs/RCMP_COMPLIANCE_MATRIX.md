# RCMP Compliance Matrix -- EFC x Euclid DR1
## Regime-Consistent Measurement Principle Applied to Kill Criteria

**Reference:** The Regime-Consistent Measurement Principle (RCMP),
DOI: 10.6084/m9.figshare.31222900

**Principle:** A measurement is valid only within the regime where
the instrument, the observable, and the theory share overlapping
validity domains. Each prediction below declares its regime assumptions
explicitly.

---

## Priority Order (RCMP-ranked, not information-ranked)

| Rank | KC  | Channel         | RCMP risk | RCMP systematic | Signal  | S/N ratio | Why this rank                            |
|------|-----|-----------------|-----------|-----------------|---------|-----------|------------------------------------------|
| 1    | KC4 | E_G(k,z)        | LOW       | ~1%             | 5-7%    | 5-7x      | Bias cancels, minimal proxy chain        |
| 2    | KC2 | fsigma8 (RSD)   | MODERATE  | 3-5%            | ~7%     | 1.5-2x    | Direct velocity, but RSD model dependent |
| 3    | KC5 | BAO / H(z)      | LOW       | <1%             | ~0%     | N/A       | Geometric consistency check              |
| 4    | KC3 | S8 (WL shear)   | HIGH      | 5-15%           | 3-5%    | 0.3-1x    | IA + photo-z + nonlinear model           |
| 5    | KC1 | P(k) full-shape | HIGH      | 10-30%          | ~6%     | 0.2-0.6x  | Bias + nonlinear + RSD coupling          |

**Critical:** Channels where RCMP systematics exceed the predicted signal
(S/N < 1) are not valid primary falsification tests. KC3 and KC1 fall
in this category. They provide supporting evidence only.

This is opposite to standard information-content ranking.
It is correct for falsification under regime consistency.

**Neutrino degeneracy:** Massive neutrinos suppress growth (like mu < 1)
but do not produce scale-localized gravitational slip (eta != 1) or
band-pass E_G enhancement at k_c. The EFC signature is qualitatively
distinct: eta(k_c) = 1.09 at z=0.5 vs eta = 1 everywhere for neutrinos.

---

## KC4 -- E_G Statistic (PRIMARY CHANNEL)

**What is measured:** Ratio of lensing convergence to galaxy velocity divergence.

**Observable:** E_G(k,z) = Omega_m * Sigma / (f * mu)

**EFC prediction:** +5.5% bump at k_c = 0.05 h/Mpc (ell ~ 66 at z=0.5),
detectable at 2.5-3.5 sigma with Euclid WL x GC cross-correlation.

**RCMP declaration:**

| Component          | Assumption                                    | Regime validity |
|--------------------|-----------------------------------------------|-----------------|
| Galaxy bias        | CANCELS in E_G ratio by construction          | N/A             |
| Intrinsic alignment| Subdominant at ell < 200 (EFC signal range)   | Valid           |
| Nonlinear scales   | Excluded: k < 0.1 h/Mpc only                 | Valid           |
| Photo-z            | Enters via lensing kernel; calibrated on spec-z| Check with DR1 |
| k <-> ell mapping  | k[h/Mpc] = k[1/Mpc]/h, verified end-to-end   | Valid           |

**Interpretation rule:**
- If |E_G - E_G^GR| < 2% at k_c across z=[0.3, 1.0]: EFC mu-Sigma coupling falsified
- If deviation present at > 3 sigma: model survives RCMP-clean test

---

## KC2 -- fsigma8 Growth Rate (SECONDARY)

**What is measured:** Anisotropy in galaxy redshift-space clustering.

**Observable:** fsigma8(z) = f(z) * sigma8(z)

**EFC prediction:** Suppressed growth (mu < 1) -> fsigma8 lower than LCDM
by ~2.2 sigma (current) extending to z ~ 2 with Euclid spectroscopic.

**RCMP declaration:**

| Component          | Assumption                                    | Regime validity |
|--------------------|-----------------------------------------------|-----------------|
| RSD model          | Kaiser + FoG (linear + Lorentzian damping)    | Valid at k < 0.15 |
| Galaxy bias        | Linear bias b(z); enters as b*fsigma8 product | Partially cancels |
| Nonlinear fingers  | Excluded via scale cuts                       | Valid           |
| Alcock-Paczynski   | Geometric correction; background-dependent    | Valid (LCDM bg) |

**Regime caveat:** RSD Kaiser model assumes GR velocity-density closure
(continuity equation with G_eff = G_N). In EFC, mu != 1 modifies this
relation -- this is not merely a "systematic" but a model-inconsistency
in the observable definition itself. The induced error is O(|1-mu|) ~ 6%
on f, partially absorbed in sigma8 (net ~3-5% on fsigma8). Kill-Test v6
accounts for this by using the EFC-modified growth equation.
For Euclid analysis, either a modified RSD model or explicit
marginalization over the velocity-density closure is required.

**f(z) approximation:** The E_G estimator currently uses f ~ Omega_m(z)^0.55
(GR growth index). In EFC, the modified growth equation shifts the
effective gamma by delta_gamma ~ 0.1*(1-mu). This introduces a ~0.3% systematic
on E_G -- well below the 5-7% signal. For final analysis, f(z) must
be extracted from hi_class output to ensure full consistency.

---

## KC5 -- BAO / H(z) (BACKGROUND CONSISTENCY)

**What is measured:** Geometric standard ruler (sound horizon).

**Observable:** D_M(z)/r_d, D_H(z)/r_d

**EFC prediction:** LCDM background (alpha-gate closed). BAO should match LCDM.
Deviation -> EFC has background physics (currently excluded by No-Go result).

**RCMP declaration:**

| Component          | Assumption                                    | Regime validity |
|--------------------|-----------------------------------------------|-----------------|
| Sound horizon r_d  | Pre-recombination physics; EFC = GR at z>50   | Valid (verified) |
| Reconstruction     | Removes nonlinear broadening; GR-calibrated   | Minor risk      |
| Template fitting   | BAO-only, not full-shape                       | Valid           |

**RCMP status:** Nearly model-independent. Low risk.

---

## KC3 -- S8 Weak Lensing (HIGH RISK)

**What is measured:** Galaxy shape correlations -> projected mass -> Sigma.

**Observable:** S8 = sigma8 * sqrt(Omega_m/0.3)

**EFC prediction:** Sigma > 1 at k_c shifts S8 relative to CMB-inferred value.
Direction: reduces S8 tension (Sigma > 1 -> more lensing -> lower sigma8 needed).

**RCMP declaration:**

| Component            | Assumption                                    | Regime validity |
|----------------------|-----------------------------------------------|-----------------|
| Intrinsic alignment  | NLA model calibrated on GR simulations        | REGIME MISMATCH |
| Photo-z errors       | Self-calibrated via cross-correlations         | Check with DR1  |
| Nonlinear P(k)       | HMCode calibrated on GR N-body               | REGIME MISMATCH |
| Multiplicative bias  | Calibrated on image simulations               | Valid           |
| Galaxy bias (GGL)    | Enters galaxy-galaxy lensing; must model      | Risk            |

**Critical RCMP caveat:** Two instruments (IA model, HMCode) are calibrated
in GR regime but applied to EFC. This introduces systematic error of unknown
magnitude. Mitigation: restrict to ell < 300 where nonlinear corrections < 5%,
and marginalize over IA amplitude freely.

---

## KC1 -- P(k) Full-Shape (HIGHEST RISK)

**What is measured:** 3D galaxy power spectrum with full k-dependence.

**Observable:** P_g(k,z) = b^2(z) * mu^2(k,z) * P_m(k,z) + shot noise

**EFC prediction:** Scale-dependent suppression at k ~ k_c via mu(k,z).

**RCMP declaration:**

| Component            | Assumption                                    | Regime validity |
|----------------------|-----------------------------------------------|-----------------|
| Galaxy bias b(k,z)   | Scale-dependent; calibrated on GR mocks       | REGIME MISMATCH |
| RSD                  | Full TNS/EFTofLSS model; GR-derived          | REGIME MISMATCH |
| Nonlinear P(k)       | EFTofLSS counterterms; GR-calibrated          | REGIME MISMATCH |
| Window function      | Survey geometry convolution                    | Valid           |
| AP effect            | Background geometry                            | Valid           |

**Critical RCMP caveat:** This channel has the highest information content
but the lowest regime consistency. THREE instruments (bias, RSD model,
nonlinear model) assume GR. Using them on EFC data without re-calibration
means you are not measuring EFC -- you are measuring EFC convolved with
GR-systematic error. This channel should be used LAST, and only after
the RCMP-clean channels (KC4, KC2) have established the signal.

---

## Summary: The Falsification Hierarchy

```
                    RCMP-clean                  RCMP-contaminated
                    <--------------------------------------------------->

    KC4 (E_G)  >  KC2 (RSD)  >  KC5 (BAO)  >  KC3 (WL)  >  KC1 (P(k))

    PRIMARY        SECONDARY     CONSISTENCY    SUPPORTING     LAST
    test           test          check          evidence       resort
```

**Decision rule for pre-registration:**

1. If KC4 shows deviation at > 3 sigma -> EFC survives cleanest test
2. If KC4 null AND KC2 null -> EFC falsified (two independent clean channels)
3. If KC4 shows signal but KC3/KC1 don't -> RCMP contamination suspected, not falsification
4. All kill criteria apply independently -- any single failure falsifies EFC in that channel

---

## Pre-Registration Template

Each frozen prediction should include:

```
PREDICTION: [observable] = [value +/- uncertainty]
REGIME: [scale range, redshift range]
RCMP STATUS:
  - [instrument 1]: [valid / mismatch / cancels]
  - [instrument 2]: [valid / mismatch / cancels]
INTERPRETATION:
  - If absent: [what is falsified]
  - If present: [what survives]
HASH: SHA-256 of this block
```

---

## Open Risks (must be resolved with hi_class output)

### Risk 1: alpha -> mu/Sigma mapping non-uniqueness
The mapping {alpha_B, alpha_M} -> {mu, Sigma} is not invertible. Different alpha-profiles
can produce identical mu and Sigma but different ISW, growth history, and CMB
lensing. **Validation required:** compare input mu(k,z) against effective mu
extracted from hi_class growth output. Mismatch > 2% -> mapping leaks.

### Risk 2: Limber approximation at low ell
The EFC signal peaks at ell ~ 66 (z=0.5). Limber approximation can induce
5-10% amplitude errors at ell < 100 -- comparable to the signal itself.
**Mitigation:** either use non-Limber integration in hi_class (exact
Bessel), or explicitly restrict predictions to ell > 50 in pre-registration.

### Risk 3: Window-function smearing
Euclid DR1 uses tomographic redshift bins (Delta_z ~ 0.2) and ell-bins.
The localized E_G bump at k_c will be smeared by integration over bin
width. Expected reduction: 5-7% -> 3-5% in binned data.
**Action:** freeze both unbinned and binned predictions. The binned
prediction is the one that gets compared to data.

### Coherence property (strongest argument)
All EFC effects point the same direction: mu down, Sigma up, eta up, fsigma8 down, E_G up.
Systematics (neutrinos, bias, IA) do not produce this coherent pattern.
A simultaneous detection across KC2 + KC4 with consistent direction
would be extremely difficult to explain without modified gravity.
