# BESR3 Results §4.2: Pre-Written Versions for Path A Outcome

## VERSION A: Sign Flip Survives (ρ(α_fit, K₀) < 0)
*Use this if Path A gives negative correlation*

### 4.2 Decisive Test Results (Path A)

Table 2 presents the results of the full Cavagnolo-model α-fit for N_succ halos with successful convergence (of 352 attempted). The median fitted α_TNG = X.XX ± Y.YY, with a distribution spanning [A, B], compared to the ACCEPT median of α ≈ 1.1.

[Table 2]
| Test | ρ | p-value | N |
|------|---|---------|---|
| ρ(α_fit, K₀) raw | −X.XXX | p | N |
| ρ(α_fit, K₀) partial\|M | −X.XXX | p | N |
| ρ(α_fit, t_cool) raw | −X.XXX | p | N |
| ρ(α_fit, t_cool) partial\|M | −X.XXX | p | N |
| ACCEPT ρ(α, y_CCT) | +0.36 | — | 239 |

The sign flip persists under the full Cavagnolo-model definition-matching: ρ(α_fit, K₀) = −X.XXX (p = Y), compared to ACCEPT ρ(α, y_CCT) = +0.36. Mass-binned analysis shows negative correlations in all [N] bins (Table 3).

The consistency between α_fit and the pre-test α_proxy is high: ρ(α_fit, α_proxy) = +X.XX, confirming that the density gradient dominates the entropy profile shape in TNG-Cluster, with the temperature gradient contributing a secondary positive offset that does not alter the rank ordering.

**Interpretation.** Because α_fit uses the same functional form (Cavagnolo et al. 2008), radial interval ([20, 400] kpc), and SUBFIND-determined centers as the observational analysis, the persistent sign difference constitutes a definition-matched sim–obs discrepancy. The three a priori identified sources of potential bias — T-slope rank reversal, radius mismatch, and local-vs-global slope definition — are all eliminated by the Path A analysis.

We conclude that TNG-Cluster does not reproduce the observed positive correlation between entropy profile steepness and central cooling time reported in ACCEPT. The direction of the mismatch — TNG clusters with steep entropy gradients having *low* central entropy, opposite to observations — suggests that the subgrid modeling of AGN feedback in TNG may produce overly tight, mechanistic coupling between structural concentration and core thermodynamic state.

---

## VERSION B: Sign Flip Reverses (ρ(α_fit, K₀) > 0)
*Use this if Path A gives positive correlation*

### 4.2 Decisive Test Results (Path A)

Table 2 presents the results of the full Cavagnolo-model α-fit for N_succ halos with successful convergence (of 352 attempted). The median fitted α_TNG = X.XX ± Y.YY.

[Table 2]
| Test | ρ | p-value | N |
|------|---|---------|---|
| ρ(α_fit, K₀) raw | +X.XXX | p | N |
| ρ(α_fit, K₀) partial\|M | +X.XXX | p | N |
| ρ(α_fit, t_cool) raw | +X.XXX | p | N |
| ACCEPT ρ(α, y_CCT) | +0.36 | — | 239 |

The sign flip observed in the pre-test (Path B) does not survive full definition matching. When α is measured via the same Cavagnolo-model fit used in ACCEPT, the correlation ρ(α_fit, K₀) = +X.XXX has the same sign as the observational reference.

**Interpretation.** The reversal from the pre-test indicates that the temperature gradient term contributes significantly to the entropy profile shape and, critically, varies across halos in a way that reverses the rank ordering established by density slope alone. Specifically, the T-slope term correlates positively with K₀, overwhelming the negative contribution from ne_slope.

This finding validates the a priori concern raised in §3.2 regarding the monotonicity assumption of the proxy-based analysis. It demonstrates that single-point density slope measurements are insufficient proxies for the integrated entropy profile shape as captured by the Cavagnolo α parameter.

TNG-Cluster, when analyzed with matched observable definitions, shows qualitative agreement with ACCEPT in the sign of the entropy–structure coupling, though the exact strength of the correlation (ρ = +X.XX vs +0.36) warrants further investigation regarding the role of 3D vs projected measurement methodologies.

We note that in this scenario, the original strong negative correlation ρ(ne_slope, K₀) ≈ −0.87 remains a valid finding within TNG-Cluster's internal structure. It reflects a genuine physical coupling between central density concentration and core entropy that is modulated by how temperature gradients shape the integrated entropy profile. The lesson is methodological: catalog-based CC diagnostics can encode different physical couplings than profile-fit parameters.

---

## VERSION C: Mixed Signal
*Use this if K₀ and t_cool give different signs*

### 4.2 Decisive Test Results (Path A)

[Adapt from above, noting which CC proxy flips and which doesn't.
Investigate whether the discrepancy traces to how t_cool integrates
over a wider radial range than K₀.]

---

## Notes for All Versions

Regardless of outcome, include:

1. **Figure:** Scatter plot of α_fit vs K₀, colored by mass, with ACCEPT trend overlaid
2. **Figure:** α_fit vs α_proxy correlation (shows whether rank ordering is preserved)
3. **Figure:** Example entropy profiles for 4 halos (1 SCC, 2 WCC, 1 NCC) with Cavagnolo fits overlaid
4. **Table:** Fit statistics: median α, median χ²_red, fraction of successful fits, outlier criteria
