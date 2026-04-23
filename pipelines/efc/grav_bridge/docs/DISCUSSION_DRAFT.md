# 9. Discussion

_Draft v1 — journal-style. Prose ready for tightening. Section numbers match PAPER_STRUCTURE_DRAFT.md._

---

## 9.1 What the three nulls have in common

The three coupling classes tested in Sections 5–7 are not independent failures.
They span the natural operator basis for modifying a second-order linear growth
equation: the source term (Class A, multiplicative G_eff), the first-order
friction coefficient in its local form (Class B), and the first-order friction
coefficient in its non-local form (Class C, where the coupling depends on
accumulated gate-activation rather than the instantaneous gate value). Any
simple scalar-tensor or effective-action modification of the growth sector with
a logistic-gate temporal activation reduces to one of these three forms.

The result is one null, not three. When geometry is locked by BAO+H(z) to
Ω_m = 0.299 ± 0.009, the β posterior collapses from (0.22 ± 0.47) to
(−0.02 ± 0.24) in Class B and remains consistent with zero at 0.2σ in Class C.
What appeared to be a non-trivial growth signature in the fσ8-only run of
VariantJ was an Ω_m–β degeneracy along a data-allowed diagonal; removing
Ω_m freedom removed the apparent signal. The correlation coefficient fell
from r = +0.85 to r = +0.19 in Class B and behaved identically in Class C.
For Class A the rejection is more direct: the k_Λ sweep shows monotone
growth of Δχ² beyond the visibility floor (G_eff/G > 1.03), with no interior
minimum and 2σ exclusion reached at k_Λ ≈ 0.033.

## 9.2 Locality was not the bottleneck

The motivation for testing Class C was the hypothesis that a Markov growth
equation — where δ(a) evolves based only on its instantaneous state — might
be the structural reason why Classes A and B failed. Breaking Markov
evolution through the memory kernel G(a) = ∫_0^a gate(a′)da′ should, in
principle, open an independent degree of freedom unreachable by local
ansätze.

The data do not support this interpretation. VariantK returns a β-posterior
that, when normalized to equivalent amplitude at a=1 (β_K ≈ 2·β_J, since
G(1) ≈ 0.5 while gate(1) ≈ 1), is statistically indistinguishable from the
VariantJ null of Section 6. The Bayes factor for β=0 is lower (BF = 3.4
versus 6.6 for VariantJ), but this reflects the wider β-posterior permitted
by weaker per-unit-β response — not a genuine preference for non-zero β.
**Breaking the Markov assumption neither improved nor worsened the fit; it
did not move the degeneracy direction; it did not open a new observable
axis.** The bottleneck is not locality.

## 9.3 Why E_G with Σ=1 carries no new information

The E_G statistic (Zhang et al. 2007) was designed as a bias-independent
probe of modified gravity through the ratio E_G = Σ·Ω_{m,0}/f. Section 8
tested its discriminating power for the coupling classes we had ruled out
in fσ8. The result is a null of a specific kind: for any coupling that
modifies only the growth equation (f) without modifying the lensing sector
(Σ), the E_G statistic collapses to Ω_{m,0}/f — the same f(z) that fσ8
already measures, reshaped. A modification strong enough to produce a
2σ E_G shift (VariantJ β = +1) is the same modification that fσ8
already excludes at Δχ² ≈ 15. Two observables, one information
direction.

The general point is that the E_G ratio only carries independent
information when numerator and denominator respond differently to the
theory modification. Any theory that touches only one of them — as
growth-ODE couplings by construction do — cannot distinguish itself from
ΛCDM in this ratio.

## 9.4 A structural result about observable choice

These findings establish a constraint on coupling structure rather than a
constraint on parameters. The class of modifications we tested is broad:
it includes any coupling representable as a gate-activated perturbation
of the linear growth ODE, whether entering through the Poisson source,
through local friction, or through a memory kernel of the gate. For this
entire class, current geometry-locked growth observables are either
decisive against or silent on the modification. No parameter choice
within the class evades the result.

The practical implication is that observable choice matters at least as
much as theory choice when testing a theory of this kind. The growth
sector is not the axis of discrimination for this class of couplings.
If entropy-flow cosmology has a cosmological signature of the form
contemplated here, it cannot appear primarily in fσ8 or E_G-with-Σ=1;
it must appear in observables that are not reducible to f(z) under
BAO-locked Ω_m. Candidates are the lensing coupling Σ itself, the
gravitational slip η = Φ/Ψ, the integrated Sachs–Wolfe signal which
responds directly to the time-derivative of the gravitational potentials,
and cross-correlations between lensing and galaxy clustering — each of
which carries a component orthogonal to growth-rate information.

## 9.5 Relation to the discrete-gravity sector

The measurements that motivated this test — the Grid-AQUAL prefactor
C ≈ 2.32 from the kill-test KT2 — stand within the discrete-gravity
framework from which they were derived. Our result does not bear on
that measurement's internal consistency. What is excluded is the
_mapping_ of C into cosmological growth observables through the
multiplicative μ-factor ansatz (Class A) or through growth-sector
friction with a gate-activated amplitude (Classes B, C). The
discrete-gravity sector and the cosmological growth sector remain
mutually consistent only in the subset of parameter space where the
coupling amplitude is effectively zero in the growth observable.
Whether this implies that (a) the correct cosmological embedding of
discrete gravity lies in a different operator class, or (b) the
cosmological embedding is scale-dependent in a way that does not
survive the BAO-locked Ω_m projection, is not determined by this
work.

## 9.6 What the result does not claim

This is not a falsification of EFC as a theoretical framework. The
claims about entropy flow, emergent gravitation, and the relation
between local gravitational phenomenology and cosmological dynamics are
not exhausted by the three coupling ansätze tested. It is not a
falsification of modified gravity in general; the phenomenological
μ–Σ space explored by recent lensing-based analyses remains open. It
is not a statement that future data cannot constrain this theory class;
the Phase 3 memory result shows that the degeneracy is in the observable,
not in the noise, so improvements in fσ8 precision alone would not
recover a signal even in the optimistic case that one exists. It is
not a final statement; it is the empirical floor against which future
work on this program must be measured.

## 9.7 What the result does claim

It claims a structural closure: the combined BAO DR2 + H(z) + fσ8 + E_G
dataset used here admits no cosmologically visible EFC signature through
local or simple non-local modifications of the linear growth ODE. The
next informative direction must lie in observables not reducible to f(z)
after Ω_m is locked by geometry. Before further variant-building, this
direction should be identified and its sensitivity mapped independently
of theory.

---

## Notes on tone and calibration

- The text above is calibrated for a modified-gravity constraints paper
  (Amon+2023, Simpson+2013, Reyes+2010 neighborhood). Strip mathematical
  symbols further only if submitting to a broader-audience venue.
- Numerical values cross-referenced: all β posteriors, r values, BF values,
  χ² values, and prior widths are consistent with summary JSONs in
  `outputs/grav_bridge/`. No placeholders.
- Sub-headings 9.1–9.7 match the logical flow in Morten's plain-language
  draft but consolidated where the original had separate bullets for the
  same structural point.
- Length: ~1,100 words. Journal Discussion sections for constraint papers
  typically run 800–1,500 words; this is within range and can be trimmed
  if the target venue requires.
- Explicit non-claims in 9.6 serve dual purpose: reviewer protection and
  intellectual honesty. Keep all five.
- 9.5 (discrete-gravity relation) is the most sensitive paragraph — it
  protects the GRAV-sector work from collateral damage by this result.
  Tighten further if reviewers push.

## What to consider trimming

If length constraints require cuts, prioritize in this order:
1. 9.5 can compress to 3 sentences if the discrete-gravity framework is
   covered in the Introduction.
2. 9.6 can become a single paragraph rather than five separate non-claims.
3. 9.2 can compress if the Methods section carries the memory-kernel
   derivation (currently scheduled for Appendix B).

## What to keep intact

- 9.1's "one null, not three" framing. This is the paper's core thesis
  and should not be weakened for brevity.
- 9.3's explicit demonstration of why E_G with Σ=1 is redundant.
  Reviewers unfamiliar with the argument will need this.
- 9.4's observable-choice emphasis — this is the methodological
  contribution beyond the specific EFC context.
