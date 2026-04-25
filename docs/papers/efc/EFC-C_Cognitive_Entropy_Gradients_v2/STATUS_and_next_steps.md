# EFC-C Status Report and Critical Path Forward

**April 5, 2026**

> **[HISTORICAL — superseded by EFC-C v2.1 (DOI 10.6084/m9.figshare.32091700 v2, April 2026)]**
> This document was a working research note from 5 April 2026 before the v2.1 revision was finalized. It is preserved for historical/process traceability. The published v2.1 paper supersedes the priority list and decision points discussed here.

## What We Have (Verified)

| Claim | Evidence | Strength |
|-------|----------|----------|
| Centrifugal gradient exists (κ > 1) | 5/6 HCP parcellations | ✅ Solid |
| Driver is degree_ratio, not λ₂ | r = -0.83, p = 0.04 | ✅ Significant |
| B1* (C=4.4, λ₂) overpredicts by 3x | 6 scales consistent | ✅ Clear failure |
| B1** (C_eff/D^γ) fits data | R² = 0.67, p = 0.047 | ⚠️ Marginal (n=6) |
| C_eff/C ≈ k within 0.3σ | 1.93/4.4 ≈ 0.415 | ⚠️ Suggestive only |
| k-chain C(n) = k^(n+1)/a_G | 2 data points | ❌ Not established |
| RLHF prediction C₃ = 0.76 | 0 data points | ❌ Untested hypothesis |

## What Must Be Done Before Any Publication

### Priority 1: Stabilise C_eff (CRITICAL)

The entire k-chain depends on C_eff ≈ 1.9 being real, not an artefact
of the FC-CV proxy or group-average smoothing.

**Required tests:**
1. Same analysis with MSE on BOLD (not FC-CV) — different proxy
2. Same analysis on independent dataset (Lausanne-70 or Czech-88)
3. Individual-subject variation: is C_eff consistent across subjects?
4. Robustness to hub/periphery threshold (5-15% / 20-40%)

**If C_eff shifts by > 50% with different proxy → k-chain is dead.**
**If C_eff is stable (±30%) across methods → k-chain is worth pursuing.**

### Priority 2: Test γ Stability

The power-law exponent γ = 0.6 ± 0.2 is poorly constrained.
Need more data points (parcellation scales or subjects) to
distinguish γ = 1/2 from γ = k from γ = arbitrary.

### Priority 3 (ONLY after 1 and 2): RLHF Prediction

The RLHF test (C₃ = 0.76) requires:
1. A precise definition of what "C" means in RLHF
2. A standardised alignment-capability metric
3. Multiple model families to test universality

This is NOT ready for testing yet. The definition problem must be
solved first.

## What NOT To Do

1. ❌ Do not claim "universal k-chain" based on 2 data points
2. ❌ Do not test RLHF before cortex result is stable
3. ❌ Do not cite C_eff = 1.93 as if it's established
4. ❌ Do not use "20 orders of magnitude" language
5. ❌ Do not build more theory before more data

## Honest Assessment of Where We Are

### Optimistic reading:
We found a quantitative, parameter-free prediction (C_eff = k²/a_G = 1.83)
that matches observation (1.93 ± 0.39) at 0.3σ. The screening exponent
from galaxy rotation curves appears as a regime-crossing factor in
cortical entropy gradients. This is the first empirical connection
between the three EFC tracks.

### Pessimistic reading:
We have n=6 group-average data points, a crude entropy proxy (FC-CV),
and a post-hoc match that could easily be numerical coincidence
(multiple candidates match within 1σ: 1/e is at 0.8σ). The "k-chain"
is a 2-parameter fit to 2 points — trivially achievable.

### Realistic reading:
We have a testable hypothesis that survived its first confrontation
with data (after appropriate correction). The original B1* was
falsified and replaced with B1**. The regime framework correctly
diagnosed the failure. Whether C_eff/C = k is real or coincidental
requires more data — specifically individual subjects and better
entropy proxies.

## Publication Strategy

### Paper A (publishable now):
"Centrifugal entropy gradients in the human connectome: a multi-scale
analysis across six parcellation atlases"
- κ > 1 across scales
- Driver = degree ratio
- No EFC claims needed
- Target: NeuroImage, Network Neuroscience

### Paper B (publishable after Priority 1):
"Cross-scale parameter transfer from galactic dynamics to cortical
entropy gradients: a falsification test"
- B1* falsified
- B1** proposed with regime correction
- C_eff/C ≈ k observation reported (not claimed as law)
- Target: Entropy, Physical Review E

### Paper C (publishable after Priority 1+2+3):
"The k-chain: regime-attenuated coupling across physical scales"
- Full three-track test
- Only if cortex AND RLHF match independently
- Target: Nature Physics (Perspective), Physical Review Letters

## Timeline

| Milestone | Dependency | Estimated effort |
|-----------|------------|-----------------|
| Individual connectome test | Data acquisition | 1-2 weeks |
| MSE proxy validation | HCP BOLD access | 2-3 weeks |
| Robustness analysis | Above | 1 week |
| Paper A draft | None (data sufficient) | 1 week |
| Paper B draft | Priority 1 complete | 2 weeks |
| RLHF definition work | Independent | 2-4 weeks |
