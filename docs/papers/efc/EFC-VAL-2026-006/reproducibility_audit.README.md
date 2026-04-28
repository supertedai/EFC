# Reproducibility & Correctness Audit Protocol

**Version:** v2.0
**Last updated:** 2026-04-28
**Script:** `tools/reproducibility_audit.py`
**Output spec:** `docs/audit/RERUN_EXPECTED_OUTPUT_2026-04-26.md`

---

## Purpose

Mechanical correctness gates for the EFC inference pipeline. **Every gate must produce
PASS, WARN, or FAIL with a clear deterministic check** — no LLM judgment, no narrative.

This is the bottom layer of the validation stack:

```
    ┌─────────────────────────────────────────────────────────┐
    │  Scientific interpretation (VAL-006, ledgers, atlas)   │  ← human + LLM
    ├─────────────────────────────────────────────────────────┤
    │  Statistical evidence (G1-G5 from RERUN_EXPECTED)      │  ← daemon output
    ├─────────────────────────────────────────────────────────┤
    │  Mechanical correctness (this README — A-H)             │  ← THIS LAYER
    │     If anything FAILs here, nothing above is trustable. │
    └─────────────────────────────────────────────────────────┘
```

**If reproducibility_audit.py reports FAIL, no inference run from after that
moment can be cited or published until either (a) the FAIL is fixed and re-run,
or (b) the FAIL is documented as a historical fact whose effect on conclusions
is bounded.**

---

## How to run

```bash
cd "/Users/morpheus/Documents/Claud Code/AGI-Test"
python3 tools/reproducibility_audit.py
```

Output looks like:

```
=== A. DATA PROVENANCE ===
=== B. CODE SYNC ===
=== C. MATH SANITY ===
=== D. KNOWN BUGS ===
=== E. NUMERICAL SANITY ===
=== F. SEALED DERIVATION CHAIN ===
=== G. CYCLE STATISTICAL VALIDITY ===
=== H. PRIOR DRIFT vs SEALED ===
==============================================================================
Status Gate                                                       Verdict
==============================================================================
✅  A1: BAO=DESI DR2 real (13+ pts, full cov)                     PASS
✅  A2: fσ8 DOI-traced (≥6 lines)                                 PASS
...
==============================================================================
PASS: 39  FAIL: 3  WARN: 1  Total: 43
VERDICT: BLOCKED
```

`VERDICT` is one of:
- **GREEN**: 0 FAILs, 0 WARNs → safe to use latest results
- **YELLOW**: 0 FAILs, ≥1 WARN → results usable but flag warnings in publication
- **BLOCKED**: ≥1 FAIL → results from this state cannot be cited/published until FAIL is documented as historical (with bounded impact) or fixed

---

## Gate categories

Section letters correspond to the gate prefixes (A1, B6, C12, etc.).

### A. Data Provenance — "Are we using real, traceable, documented data?"

| Gate | Check | PASS criterion |
|---|---|---|
| **A1** | DESI DR2 BAO file present and well-formed | `n≥13`, `source` contains "DESI DR2", `cov.txt` exists |
| **A2** | fσ8 hybrid file has DOI provenance per row | ≥6 lines containing "DOI:" |
| **A3** | H(z) cosmic chronometer file has DOI provenance | ≥3 lines containing "DOI:" |
| **A4** | Pantheon SNIa data + covariance present | `pantheon_binned.csv` and `_covtotal.npy` both exist |
| **A5** | No stub/smoketest references in research_mcmc.py | None of `bao_starter`, `bao_smoketest`, `fs8_starter`, etc. in code |

**Why this matters:** A5 specifically catches a class of bug seen 2026-04-22:
the code referenced `bao_starter.csv` (synthetic stub) for several months,
producing artificial signals. Switching to real data caused signal collapse —
which the paper VAL-005 published as "DESI DR1 ΔΧ²=−22 STRONG" but would have
never appeared with real DR2.

### B. Code Sync — "Is the code in container == repo?"

| Gate | Check | PASS criterion |
|---|---|---|
| **B1-B5** | SHA256 of 5 critical files matches between Test repo and AGI repo | hashes equal |
| **B6** | `research_mcmc.py` SHA256 in container matches Test | hashes equal |

**Why this matters:** Two-repo Docker architecture (`/AGI-Test/` for editing,
`/Users/morpheus/AGI/` for Docker volume mount) means edits in one repo don't
take effect in the running daemon until rsync + restart. Multiple cycles in
2026-04-27 produced "identical" results because patches hadn't been propagated.

**Critical files audited:**
1. `efc_inference/runs/research_mcmc.py` — MCMC functions
2. `efc_inference/runs/research_daemon.py` — Daemon orchestration
3. `efc_inference/core/cosmology_model.py` — Variant definitions
4. `efc_inference/runs/jax_efc_nuts.py` — NUTS likelihood
5. `efc_inference/runs/gpu_nuts_daemon.py` — GPU daemon

### C. Math Sanity — "Do variants reduce to LCDM in their limit?"

| Gate | Check | PASS criterion |
|---|---|---|
| **C1** | LCDM E²(a=1) = 1 | `\|E²-1\| < 1e-10` |
| **C2** | LCDM E²(z=0.5) matches analytic | `\|E²(z=0.5) - (Ω_m·1.5³ + Ω_Λ)\| < 1e-8` |
| **C3** | EFCVariantA(α=0) ≡ LCDM | max\|ΔE²\| < 1e-10 |
| **C4** | EFCVariantB(α=0) ≡ LCDM | max\|ΔE²\| < 1e-10 |
| **C5** | EFCVariantC(α=0, μ₀=1) ≡ LCDM (E² and growth source) | both < 1e-10 |
| **C6** | EFCVariantF(α=0) ≡ LCDM | max\|ΔE²\| < 1e-10 (WARN if class missing) |
| **C7** | EFCVariantH(S̄₀=0) ≡ LCDM (E² and growth source) | both < 1e-10 |
| **C8** | VariantG.is_null_test correctly classifies G10/G02/G01 | G10=True, G02=False, G01=False |
| **C9** | VariantH α prior is symmetric U(-0.5, 0.5) | code contains `not (-0.5 < S_bar_0 < 0.5)` |
| **C10** | VariantH walker init straddles 0 | code contains `uniform(-0.15, 0.15` |
| **C11** | VariantH μ-clamp lower bound = 0.3 | code contains `np.clip(mu, 0.3, 10.0)` |
| **C12** | posterior_robustness + null_test wired in daemon | both `engine.posterior_robustness` and `engine.null_test` present |
| **C13** | VariantH μ stays in physical range at typical posterior | 0.5 ≤ μ(a=0.5, S̄₀=0.1, β₀=1) ≤ 1.5 |
| **C14** | All variants produce finite, positive E² at typical params | `np.isfinite(E²)` and `E² > 0` for sample points |

**Why C3-C7 are critical:** Every EFC variant claims to be a parametric
extension of ΛCDM. If ΛCDM is recovered when the EFC parameter is zero, the
test of "is α (or S̄₀) different from zero?" is mathematically clean. If the
limit fails, the test's null hypothesis is ill-defined.

**Why C9-C12 are critical:** These four are the patches applied 2026-04-26
that converted VariantH from a structurally-biased one-sided test into a
genuine two-sided test. C12 ensures the daemon actually runs the robustness
band, without which σ-claims have no error band.

### D. Known Bugs — "Have specific historical bugs been re-fixed?"

| Gate | Check | PASS criterion |
|---|---|---|
| **D1** | `neo4j_uri AttributeError` regression fixed | `self.neo4j_uri = ` present in research_daemon.py |
| **D2** | Axiom 0 Cypher 'END' bug not regressed | no orphan `END` line near 1380-1395 |
| **D3** | VariantG NULL_TEST_BY_DESIGN classification present | `NULL_TEST_BY_DESIGN` in cosmology_model.py |
| **D4** | Forbidden Pattern +1.0 magic offset removed | string `+ 1.0 if min_dll > 0` NOT in forbidden_pattern_distance.py |

**Why this matters:** These are bugs we already found and fixed once. The
audit ensures they don't quietly come back via a merge, refactor, or AI
regenerating broken code.

### E. Numerical Sanity — "Are covariances and constants well-behaved?"

| Gate | Check | PASS criterion |
|---|---|---|
| **E1** | DESI DR2 BAO covariance positive-definite | all eigenvalues > 0 |
| **E2** | Pantheon covariance positive-definite + invertible | square + all eigenvalues > 0 |
| **E3** | r_d D2b safety warnings within tolerance | <5000 occurrences in last 10k log lines |

**Why this matters:** A non-positive-definite covariance produces meaningless
χ². A flood of D2b safety warnings indicates EFC variants are pushing r_d
into unphysical regions, which silently distorts likelihoods.

### F. Sealed Derivation Chain — "Does sealed = real data + correct math + symmetric prior?"

This category is **historical** — it audits the past commit recorded in each
`freeze_*.json` file's `provenance.code_commit`.

| Gate | Check | PASS criterion |
|---|---|---|
| **F1** | freeze provenance has cycle_id, code_commit, cosmology_model, sampler_type | all 4 present |
| **F2** | freeze cosmology_model is documented variant | one of efc_variant_a/b/c/f/h |
| **F3** | freeze sampler_type is documented | "nuts" or "emcee" |
| **F4** | fs8 data at freeze commit ≡ fs8 data now | git show identical to current file |
| **F5** | DESI DR2 BAO file existed at freeze commit | git show succeeds |
| **F6** | NUTS α prior is symmetric | `Normal(0.0, 1.0)` reparameterization in jax_efc_nuts.py |
| **F7** | At least one sealed freeze exists | n_freezes ≥ 1 |

**Why F4 and F5 are likely to FAIL forever:** The published predictions
(EFC-VAL-2026-005, freezes from Feb 2026) used **stub data** for fσ8
(`fs8_smoketest`, ~3 points) and **DESI DR1** for BAO. Real fs8 hybrid (now 16
DOI-traced points) and DR2 BAO did not exist in the repo at those commits.
This is a **historical fact**, not a bug. The audit reports it as FAIL so it
does not get forgotten.

**Bounded-impact protocol for FAILs in F:** Document in `docs/audit/SESSION_*_AUDIT_REPORT.md`
under "Sealed prediction risk classification" how each FAIL affects each
sealed prediction's defensibility. This conversion of FAIL → "documented
historical limit" is the only legitimate way to pass without re-sealing.

### G. Cycle Statistical Validity — "Are PPC and per-probe checks healthy?"

| Gate | Check | PASS criterion |
|---|---|---|
| **G1** | PPC artifact present in latest cycle | `ppc.json` or `ppc*.json` exists in latest rc_* dir |
| **G2** | PPC growth p_value < 0.95 (known issue) | currently FAIL (growth p≈0.99) |

**G2 is currently FAIL:** PPC growth p-value of 0.99 means the EFC posterior
makes growth predictions that are systematically *too far* from the
calibrated null distribution. This was uncovered 2026-04-28 and is unsolved.
**Effect:** weakens any growth-sector claim until calibration is fixed. Atlas
should reflect this.

### H. Prior Drift vs Sealed — "Is current prior compatible with what was sealed?"

| Gate | Check | PASS criterion |
|---|---|---|
| **H1** | emcee α prior bounds are symmetric | regex extracts (lo, hi) and lo == -hi |
| **H2** | NUTS α prior is N(0, ~3) | hard-documented PASS based on jax_efc_nuts.py reparameterization |

**Why this matters:** Different priors → different posteriors → different
sealed-vs-current comparisons. If today's α prior is U(-2, 2) but the seal's
prior was U(-1, 1), the sealed prediction is conditional on a *narrower* α
range than what we now allow, and the comparison is no longer apples-to-apples.

---

## Interpretation matrix (FAIL handling)

| Category | If FAIL, then... |
|---|---|
| **A** Data provenance | BLOCKING — re-run with real data before any new claims |
| **B** Code sync | BLOCKING — rsync + restart container before any new claims |
| **C** Math sanity | BLOCKING — investigate immediately. Often indicates a regression in variant code |
| **D** Known bugs | BLOCKING — these are bugs we already fixed; if they recur, audit cycle is invalid |
| **E** Numerical sanity | BLOCKING (E1, E2). E3 → WARN unless severe |
| **F** Sealed derivation | **Historical** — document once in audit report; subsequent FAILs are no-ops if documented |
| **G** Cycle statistical | G1 FAIL = BLOCKING. G2 FAIL = WARN (currently flagged as known calibration issue) |
| **H** Prior drift | If HARD FAIL, sealed predictions cannot be cleanly compared |

---

## When to re-run the audit

1. **Before every new ledger publication** — never publish without GREEN or
   YELLOW (with documented WARN) audit
2. **After every research_daemon code patch** — verify patches landed and
   nothing else regressed
3. **Before claiming a sealed prediction is confirmed/falsified** — verify
   F-category state for that specific freeze
4. **After every container rebuild** — verify B6 (container sha == repo sha)
5. **Before adding a new variant** — extend C-category to include it (template:
   add `Cn: VariantX(zero_param) ≡ LCDM` test)

---

## Adding a new gate

1. Pick the right category (A-H)
2. Add a `gate(name, status, detail)` call in the appropriate section
3. The `name` must use the next number in that category (e.g. `C15`, `D5`)
4. The `status` must be one of `PASS`, `WARN`, `FAIL`, `SKIP`
5. The check must be **deterministic** (no LLM, no random sampling)
6. Update this README with the new gate's purpose

**DO NOT** add a gate whose verdict depends on non-deterministic input
(e.g. "is the latest cycle's α more than 1σ away from zero?"). That
belongs in `RERUN_EXPECTED_OUTPUT.md`'s G1-G5 mandatory gates instead.

---

## Audit history

| Date | PASS/FAIL/WARN | Verdict | Notes |
|---|---|---|---|
| 2026-04-28 (post-Tier 1 patches) | 39/3/1 | BLOCKED→DOCUMENTED | F4, F5 historical; G2 deferred |

When status changes, append a row.

---

## Relationship to RERUN_EXPECTED_OUTPUT_2026-04-26.md

| File | Layer | Scope |
|---|---|---|
| `tools/reproducibility_audit.py` | Mechanical correctness | Static — does the code/data state look right? |
| `docs/audit/RERUN_EXPECTED_OUTPUT_2026-04-26.md` | Statistical validity | Dynamic — do the next cycle's chains satisfy G1-G5? |

Both must pass before drawing scientific conclusions. The first is the
"is the lab clean?" check. The second is the "did the experiment work?" check.
