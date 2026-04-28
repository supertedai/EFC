# Re-run Expected Output Spec — Tier 1 Patches

**Date:** 2026-04-26
**Patches applied:**
1. `research_daemon.py:_run_divergence_analysis` — `posterior_robustness` + `null_test` integration
2. `research_mcmc.py:_log_prior_variant_h` — `S_bar_0` prior `U(0, 0.5)` → `U(-0.5, 0.5)`
3. `research_mcmc.py:_init_p0_5param_h` — walker init straddles zero
4. `cosmology_model.py:EFCVariantH.growth_source` — clamp `[0.5, 10]` → `[0.3, 10]`

**Untouched (Tier 2/3, deferred):**
- Axiom 0 secondary status promotion
- Forbidden Pattern `+1.0` offset
- VariantG G10 null-test classification

---

## Validation checklist for next research_daemon cycle

After cycle completes, inspect log + outputs for the following. **If any item fails, the patch did not take effect — do NOT trust the verdict.**

### MANDATORY validity gates (before ANY interpretation)

These are mechanical checks. They must ALL pass before anyone reads ΔAIC or σ-values. If any gate fails, re-run is INVALID and conclusions cannot be drawn.

| Gate | Check | Pass criterion |
|---|---|---|
| **G1: posterior straddles zero** | `P(S̄₀ < 0)` from chain | **30% ≤ P(S̄₀ < 0) ≤ 70%** if mechanism null. <5% or >95% means walker init or prior didn't take effect — **INVALID** |
| **G2: clamp not engaged** | `min(μ)` over all chain samples | `min(μ) > 0.3` strictly. If min == 0.3 across many samples, posterior is hitting wall — **INVALID** |
| **G3: posterior_robustness produced** | log + JSON file | Log must contain `Total ΔlogL = X.XX ± Y.YY` AND `efc_inference/outputs/divergence/divergence_robustness_*.json` exists with `posterior_robustness.total.std_delta_logL` populated — else patch 1 didn't fire — **INVALID** |
| **G4: null_test floor reported** | log | Must contain `Null floor (LCDM-vs-LCDM) std = N.NN` — else null_test didn't run |
| **G5: walker init verification** | first iteration of VariantH chain | ~50% of walkers should have S̄₀ < 0 at iteration 0. If init was wrong (all positive), **INVALID** |

### Outcome classification (only after ALL gates pass)

| Outcome | ΔlogL_robustness | P(EFC > LCDM) | Action |
|---|---|---|---|
| 🔴 **NEGATIVE** | < 0 | < 30% | Genuine falsification. VAL-006 with negative result. |
| ⚠️ **AMBIGUOUS** (most likely) | ≈ 0 ± small | 50-60% | Defer VAL-006. Need different observable. |
| 🟡 **WEAK INDICATION** | > 0, < 1·null_std | 60-70% | Hold. Not enough for any conclusion. |
| 🟢 **INTERESTING** | > 1·null_std, consistent across probes | > 70% | Begin investigating mechanism. Not yet a "finding". |
| 🔵 **STRONG SIGNAL** | > 2·null_std | > 80% | Real result. Combined with Axiom 0 secondary p=0.0195 may reset narrative. |

### What we are NOT doing this cycle

- ❌ Inspecting individual probe trends visually
- ❌ Comparing to sealed predictions before robustness gate passes
- ❌ Drawing conclusions from VariantG, Forbidden Pattern, or Axiom 0 (Tier 2 — deferred)
- ❌ Writing VAL-006 until outcome class is determined

### 1. Divergence Engine — must produce `posterior_robustness` block

**MUST appear in log:**
```
POSTERIOR ROBUSTNESS:
  Total ΔlogL = +X.XXX ± Y.YYY (self-significance Z.ZZσ)
  Null floor (LCDM-vs-LCDM) std = N.NNN
  Signal vs null floor: M.MMσ
  bao: ΔXX ± YY (EFC better in PP% of draws)
  hz: ...
  growth: ...
  snia: ...
```

**MUST exist on disk:**
- `efc_inference/outputs/divergence/divergence_robustness_*.json`

**Sanity values:**
- `null_floor.total.std_delta_logL` should be ~0.1–0.3 (typical noise floor)
- `posterior_robustness.total.std_delta_logL` should be ~0.3–1.0 (genuine posterior spread)
- If `pct_efc_better` for any probe is ~50%, that probe is genuinely undecided
- If `pct_efc_better` is >70% or <30% for a probe, that's a real per-probe signal

### 2. VariantH — must explore both signs of S_bar_0

**MUST appear in log:**
```
VariantH (entropy-gradient mu): ...
Best-fit S̄₀ = X.XXXXXX, β₀ = Y.YYYY
```

**Sanity values for new prior:**
- Best-fit `S̄₀` may be **negative** for the first time. This is the actual test.
- The `S̄₀ posterior` should now have meaningful left tail. If posterior median is **clamped at 0**, walker init didn't take effect.
- Walker init should put ~50% of walkers at S̄₀ < 0 initially. Check: `_init_p0_5param_h` returns `uniform(-0.15, 0.15)` for column 3.

**Output verification commands:**
```bash
# Inspect VariantH chain
python3 -c "
import numpy as np
chain = np.load('efc_inference/outputs/research/rc_<NEW_ID>/variant_h_chain.npz')['chain']
sb0 = chain[:, :, 3].flatten()
print(f'S_bar_0 posterior: median={np.median(sb0):+.4f}, '
      f'pct < 0 = {(sb0 < 0).mean()*100:.1f}%, '
      f'pct > 0 = {(sb0 > 0).mean()*100:.1f}%')
print(f'CI68: [{np.percentile(sb0, 16):+.4f}, {np.percentile(sb0, 84):+.4f}]')
"
```

### 3. VariantH AIC — must be re-evaluated under symmetric prior

**Comparison to previous (biased) result:**
- Previous (one-sided): `ΔAIC = +3.9` (LCDM wins by ~2σ)
- New (two-sided): expected `ΔAIC` outcome falls in one of three regimes:

  | Outcome | Interpretation |
  |---|---|
  | `ΔAIC > +2` | LCDM still wins. Mechanism genuinely unsupported under current data. |
  | `-2 < ΔAIC < +2` | Inconclusive. Mechanism not strongly preferred either way. |
  | `ΔAIC < -2` | EFC mechanism preferred. Original result was prior-bias artifact. |

  All three are valid scientific outcomes. Critical: previous bias prevented us from distinguishing `+3.9 (real null)` from `+3.9 (prior trap)`. After patch, this distinction becomes resolvable.

### 4. VariantH posterior shape — diagnostic for whether prior bias was the problem

If under symmetric prior the posterior:
- **Stays at S̄₀ ≈ 0 with both tails populated symmetrically** → mechanism is genuinely null. Original ΔAIC = +3.9 was correctly null-detected, just for the wrong reason.
- **Shifts to S̄₀ < 0 (suppression) with significance**  → original test was hiding a real signal in the wrong direction. Sealed α<0 background-deceleration **may actually couple to growth-suppression**, validating EFC as a mechanism while suggesting the published parameterization (α only) was misnamed.
- **Posterior bimodal** (peaks at S̄₀ < 0 AND S̄₀ > 0) → degeneracy. Need additional probe to discriminate.

---

## Decision tree after re-run

```
Did posterior_robustness produce |total| / null_std > 2σ?
├── YES → Real EFC-vs-LCDM signal. Examine sign and per-probe contributions.
│         Combined with Axiom 0 secondary p=0.0195, may warrant new ledger entry.
└── NO → Confirms degeneracy / no detectable mechanism in expansion+growth probes.

Did VariantH find S_bar_0 ≠ 0 at >2σ in new symmetric prior?
├── YES, S_bar_0 < 0 → Mechanism is growth-SUPPRESSION (not enhancement).
│                       Original VAL-005 framing was inverted in sign.
│                       Strong case for VAL-006 corrigendum.
├── YES, S_bar_0 > 0 → Mechanism is growth-enhancement, but original ΔAIC=+3.9 was
│                       wrong number (prior cut off real S_bar_0 < 0 nuisance modes).
│                       Less likely; would mean prior was unintentionally optimistic.
└── NO  → Mechanism genuinely consistent with zero. Original ΔAIC=+3.9 was a real
          null. EFC NOT supported in this parameterization. VAL-006 corrigendum
          warranted (without sign-flip language).
```

---

## What NOT to conclude before this re-run

1. ❌ "EFC is falsified" — current data only says α-as-free-parameter is consistent with 0
2. ❌ "VariantH disproves EFC mechanism" — that test was rigged toward null by the one-sided prior
3. ❌ "Forbidden Pattern triggered" — that was a metric artifact, not data
4. ❌ "Axiom 0 is null" — only the underpowered primary; secondary p=0.0195 is real signal that's being suppressed by status-gate logic
5. ❌ "Divergence is microscopic" — without `posterior_robustness`, we don't know the uncertainty band

---

## What we CAN conclude with current evidence

1. ✅ α as free parameter under joint BAO_DR2 + fσ8_extended + Hz + SNIa: posterior centers near 0
2. ✅ Real-data update (post-2026-04-16) collapsed the apparent VAL-005 DR1 Δχ²=−22.01 signal
3. ✅ Sealed predictions (`freeze_20260221`, `freeze_20260218`) remain prereg-protected; their integrity is intact
4. ✅ The EFC mechanism as a *physical hypothesis* has not yet had a fair test under the current testing infrastructure
5. ✅ The infrastructure itself (research_daemon + atlas + ledger) successfully self-flagged code-level biases — this is a system strength, not weakness

---

## Re-run command

```bash
docker restart efc-research-daemon
# Wait ~14 hours for next 6h cycle, OR force immediate run:
docker exec efc-research-daemon python -m efc_inference.runs.research_daemon --force
```

**Note:** The first cycle after these patches will use the NEW prior. Verify item #2 (S̄₀ posterior shape) before drawing conclusions.

---

## After re-run: decision matrix for VAL-006

| Re-run outcome | Action |
|---|---|
| Posterior_robustness < 1σ AND VariantH S̄₀≈0 AND Axiom-0 secondary not promoted | Defer VAL-006. Status: "EFC underdetermined under current data + tests." |
| Posterior_robustness ≥ 2σ in either direction | Write VAL-006 with new findings. Probably new DOI. |
| VariantH S̄₀ ≠ 0 at ≥ 2σ | Write VAL-006 + reframe published parameterization. New DOI. |
| Mixed (some signals positive, some null) | Carefully scoped VAL-006 reporting only what holds up to robustness check. |
