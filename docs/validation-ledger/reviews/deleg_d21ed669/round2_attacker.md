# Round-2 ATTACKER rebuttal — EFC v2

This is an adversarial reading-consistency review of the frozen manuscript, not independent validation. Citations are repository-relative paths under `/home/morten/EFC-prov/`; line numbers refer to the files read for this round, and JSON citations name the exact field where useful.

## C3 — `Gamma_B` dimensionality

### A. Sharpest real weakness

The residual dimension is not the deepest problem. The deeper failure is **object identity**: the manuscript uses the same symbol `Γ` for at least three different roles without establishing a typed bridge between them.

1. The manuscript defines the effective response as `Γ = dS/dρ` and uses it in the chain rule for `S_i(ρ)` (`docs/validation-ledger/reviews/deleg_d21ed669/snapshot.tex:127-131`). The entropy-production package separately records the step-2 chain as `Γ = (ds/dn)(dn/dρ)`, with `dn/dρ` explicitly negative, but then assembles a positive per-mode magnitude `|Γ|` and a positive total form (`docs/papers/efc/Derivation_of_the_Entropy_Production/data/entropy_production_data.json:29-41`; `docs/papers/efc/Derivation_of_the_Entropy_Production/src/entropy_production.py:63-73,151-160,198-207`). Its `DoubleCounting.gamma_rate` likewise returns the positive quantity `n(n+1)`, not the signed derivative (`.../src/entropy_production.py:280-291`). Thus even within 31942821, the signed `dS/dρ`, a per-mode absolute rate, and the positive normalized total are not shown to be one object.

2. The relativistic-action package uses `Γ(ρ)` as the source in the constraint `□φ = Γ(ρ)` (`docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/index.json:168-176,209-212`). Its implementation labels `gamma0` an entropy-production **rate** scale with units `[1/time]` and uses the saturating `ρ/(ρ+ρcrit)` form (`.../src/efc_relativistic.py:37-51`). No source equation identifies that rate-source normalization with the entropy derivative in the 31942821 chain, whose entropy and density normalizations are not specified here.

3. The grid-action package does not define a `Γ(ρ)` object in its enumerated core equations or implementation. Those fields define the grid action, `κ_eff`, dispersion, `E`, and the BE screening function `μ(g)` (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:28-72`; `.../src/grid_action.py:19-215`). Its machine-readable derivation chain ends at thermal occupation and `μ(g)`/screening, not at a Gamma response (`.../data/grid_action_data.json:132-139`). Therefore the manuscript's reference to “the grid-action `Γ`” (`snapshot.tex:143`) is not supported by an explicit Gamma definition in that package.

The dimensional observation is conditional and narrower: under the manuscript's own treatment of `ρ` and `ρcrit` as dimensional densities, the displayed bare `ρ^(3/2)/(ρ+ρcrit)` has a residual `sqrt([ρ])` (`snapshot.tex:135-143`). But the source package writes the result with proportionality and its executable `gamma_total` accepts the dimensionless ratio `ρ/ρcrit`, multiplies by `Γ0`, and calls the result normalized (`.../src/entropy_production.py:198-207`; `.../index.json:108`). The real defect is therefore a missing cross-package definition, sign convention, and normalization map. Until that map exists, it is not even well-typed to decide whether the source expression is a dimensional error, a shape-only notation, or a different `Γ` from the relativistic source.

### B. Round-1 finding that was under-weighted or over-credited

- `F-cart-1` noticed the author-gated non-identification, but under-weighted its consequence: this is not just an omitted caveat around C3; it blocks the claim that the three packages are discussing a common physical response.
- `F-form-3` correctly verifies the literal residual dimension, but over-credits that as the central defect. `F-form-4` is right that the source's proportionality sign and dimensionless implementation weaken the stronger claim of an unavoidable package-level inconsistency. The attack that should be elevated is the signed/magnitude and cross-object mismatch.

### C. Attack conceded not to hold

The literal dimensional calculation does hold under the manuscript's stated convention. It is also fair to report that the displayed `Γ_B` form lacks an explicitly documented common prefactor. What does **not** hold is the stronger claim that the implementation is necessarily dimensionally inconsistent, or that the chain-rule identities themselves are invalid when `S` is genuinely a one-variable function of `ρ`. The source gives a plausible normalization convention; it does not give the missing identity map.

## C5/C6 — two axes and separation of the square-root roles

### A. Sharpest real weakness

The two axes are presently a **bookkeeping decomposition**, not an empirically demonstrated factorization of the model. The manuscript itself says that physical independence is not demonstrated and that only the E-axis has a preregistration proposal (`docs/validation-ledger/reviews/deleg_d21ed669/snapshot.tex:157-180`). The primary preregistration is explicit about the limitation: its observable is `μ(g) = g_obs/g_bar`, its target is the BE exponent, and the test “does not test `Γ(ρ)`” (`docs/validation-ledger/preregistrations/axis_e_sparc_rar.md:29-42,98-102`). The siren proposal independently says that it tests neither the E exponent nor the Gamma density form (`docs/validation-ledger/preregistrations/axis_dl_gw_em.md:93-97`).

The source packages supply no executed joint forward model that would vary the E exponent and Gamma form while predicting separate observables. The grid-action package maps its action to `E ∝ √g` and then to `μ(g)` (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:53-72`), while the density-of-states package proposes a theoretical `Γ(ρ)` bridge with no data and `verdict: N/A` (`docs/papers/efc/Density_of_States_of_Gravitationally/index.json:45-62`). The relativistic package does contain `Γ'` in its perturbation equations, but it likewise records no dataset or fit (`docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/index.json:225-242; .../index.json:58-70`). That is a possible future coupling, not evidence that the RAR proxy identifies the Gamma shape independently.

The strongest defensible status is therefore: two named coordinates exist in the author's model-family taxonomy; physical independence, separable identifiability, and a joint likelihood are unshown. The RAR chain can select an exponent conditional on its nuisance model, but it cannot by itself select `Γ_A`, `Γ_B`, or `Γ_C`. Calling both “open selections” risks implying that both have operational selection channels when the manuscript expressly says the Gamma axis has none (`snapshot.tex:160,164,179; .../snapshot.tex:208-211`).

### B. Round-1 finding that was under-weighted or over-credited

- `F-alt-2` and `F-mp-5` identify the right direction, but the real defect is larger than a missing factorial design: there is no source-level Gamma-to-measurand forward map or independent Gamma observable at all.
- `F-cart-3` over-credits the phrase “two open axes” as though it were already a physical architecture. It is presently a descriptive partition with one operational test channel.
- `F-fals-5` is substantially correct, but “no preregistered discriminator” should be read as non-identification, not merely as an administrative gap that leaves the second axis otherwise intact.

### C. Attack conceded not to hold

The algebraic role separation is real. `E ∝ √g` and `Γ_C ∝ √(ρ/ρcrit)/(1+√(ρ/ρcrit))` use different variables and arise in different source chains (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:53-72`; `docs/papers/efc/Density_of_States_of_Gravitationally/index.json:41-48`). It is not a valid attack to say that choosing the exponent automatically chooses the Gamma form. The unsupported step is the stronger physical implication that the two choices are independently testable axes now.

## C7/C8 — KC1 and the `>=5σ` provenance gate

### A. Sharpest real weakness

KC1 is not operational merely because it contains a nominal `>=5σ` threshold. The source criterion requires “robust,” “bias-controlled,” “preferred,” “significantly exclude,” and “diverse systems,” but supplies no decision rules for those predicates (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:102-107`). The Axis-1 preregistration says that the statistic and threshold must be fixed before the fit, but leaves them as future protocol choices; it is still `proposed — awaiting author freeze` and requires an unfitted a0, nuisance treatment, and holdout (`docs/validation-ledger/preregistrations/axis_e_sparc_rar.md:1-4,44-75,91-96`). No covariance, likelihood-ratio convention, multiple-testing rule, sample strata, or exact conversion from the reported statistic to sigma is present in the cited package fields.

There is also a provenance contradiction that can leak into Level 2. The source PDF states that the chi-square difference is significant at `>5σ` across the SPARC sample and says the surviving C5 form “Matches SPARC data” (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/EFC_Gradient_Coupled_Grid_Action.pdf:48-72`). The package index simultaneously records `delta_chi2: null`, `significance_sigma: null`, datasets as only “Conceptual consistency with SPARC rotation curves (referenced; no new fit performed),” and `verdict: N/A` (`.../index.json:74-88`). The form register confirms that the wording of KC1 was resolved, but that the provenance question—executed fit versus externally repeated claim—remains author-gated (`docs/validation-ledger/data/form_status_register.json:67-73`).

The manuscript does state the provenance gap at Level 3, but it still presents the PDF's operator selection as “favoring the square-root form” and calls it consistent with KC1 (`snapshot.tex:186-192`). That is a source-internal claim, not downstream evidence. Without an explicit quarantine sentence, a reader can treat the Level-2 direction as indirect empirical support for the branch whose supposed `>5σ` exclusion is simultaneously unverified.

### B. Round-1 finding that was under-weighted or over-credited

- `F-fals-1` correctly identifies the undefined operational terms, but under-ranks the consequence: KC1 is not an executable gate until those terms and the statistic are frozen; nominal `5σ` is only a label.
- `F-fals-2` finds the PDF/metadata conflict, but is too generous in treating quarantine as a remaining wording improvement. The manuscript's Level-2 paragraph already exposes the unsupported internal selection as a possible downstream signal.
- `F-cart-4` over-credits C7 by treating the logical conditional as the whole criterion; its conditions are not yet a reproducible decision rule.

### C. Attack conceded not to hold

The conditional logic itself is genuine: if a properly specified future comparison produces the stated result, the square-root theorem would be challenged. KC1 is not unfalsifiable in principle, and the wording-resolution entry is supported. Nor is there evidence here that the PDF's `>5σ` sentence was fabricated. It may be an external result; the defect is that the source does not provide enough provenance to use it as evidence in this reconciliation.

## C9 — SPARC/RAR, `a0`, and imported calibration

### A. Sharpest real weakness

The manuscript is right that `a0` is not shown to be EFC-derived, but it is too noncommittal about provenance. The primary source already labels the value as external MOND/SPARC material: the preregistration calls `1.2e-10 m/s²` the “MOND scale” and says it is the value in the papers' code and `index.json` (`docs/validation-ledger/preregistrations/axis_e_sparc_rar.md:46-56`). The microphysics package lists “MOND phenomenology” among its keywords, calls the value a “measured SPARC value,” and makes it assumption A3 rather than deriving it (`docs/papers/efc/From_Grid_Microphysics_to_the_Radial_Acceleration/index.json:15-20,129-146`). The executable source hard-codes `A0_SPARC = 1.2e-10` with the comment “measured SPARC value” (`.../src/grid_microphysics.py:15-17`). The same MOND-labelled constant is hard-coded in the entropy and density packages (`.../Derivation_of_the_Entropy_Production/src/entropy_production.py:22-29`; `.../Density_of_States_of_Gravitationally/src/density_of_states.py:24-30`).

Consequently, the manuscript's statement that the origin must later be chosen among “MOND/SPARC input, EFC output, or nuisance calibration” (`snapshot.tex:211-213`) leaves open a choice that the source record already constrains: the cited value is an external MOND/SPARC input, not an EFC prediction. Freezing it is necessary for a fair comparison, but it cannot convert the borrowed scale into a prediction.

The same problem applies to the observable chain. The preregistration does specify raw rotation velocities, photometry/gas maps, instruments, `g_obs`, `g_bar`, and `μ(g)` (`axis_e_sparc_rar.md:29-42`), but it also calls M/L the dominant paradigm leak, requires a pre-declared nuisance treatment and holdout, and says the proxy is model-laden rather than paradigm-free (`.../axis_e_sparc_rar.md:61-68,72-88`). The theory package itself uses `rar_curve(g_bar_values)` to compute `g_obs` and `g_obs/g_bar` from already supplied baryonic accelerations, while its metadata says `datasets_used: None (theoretical derivation)` (`docs/papers/efc/From_Grid_Microphysics_to_the_Radial_Acceleration/src/grid_microphysics.py:121-130`; `.../index.json:50-63`). Thus the proposed test is a comparison on a borrowed, calibration-dependent RAR proxy, not yet independent evidence for the E exponent.

The precise criticism is not that exact same-galaxy reuse has been proven. The sources do not establish which galaxies, if any, calibrated the quoted a0. The real defect is that no independent calibration/holdout status is established, while the manuscript fails to carry the already documented external provenance into the discriminator paragraph.

### B. Round-1 finding that was under-weighted or over-credited

- `F-para-1` is correct but should be sharpened from “label the origin later” to “the source already supports the external MOND/SPARC-input label; EFC-output status is unsupported.”
- `F-para-2` and `F-mp-2` correctly identify the sample/proxy and nuisance dependence, but they should distinguish absent independence evidence from proven same-sample reuse.
- `F-mp-1` overstates the omission of the measurement chain: the preregistration does explicitly provide the raw-signal/instrument/measurer/proxy table. Its stronger, supportable criticism is that the chain is proposed and unexecuted, and the implementation consumes derived `g_bar` rather than raw data.

### C. Attack conceded not to hold

The manuscript does not falsely call `a0` an EFC-derived output; it explicitly says the opposite, and the a0 freeze is a legitimate anti-shopping rule. It also names “SPARC/RAR,” so the sample label is not hidden. The unsupported claim would be that the future result is independent or paradigm-free merely because a0 is frozen. That claim is not made explicitly and should not be invented.

## C10 — siren specificity and parameter freezing

### A. Sharpest real weakness

The final sentence of the siren paragraph overclaims: freezing parameters does not make a non-unit GW/EM distance ratio **uniquely EFC-discriminating**. The same paragraph first correctly says that the inequality is not EFC-specific and cannot by itself distinguish EFC from GR systematics or other modified-gravity friction models, then asserts that it becomes unique once `α`, `φ0`, and `φ(z)` are frozen (`snapshot.tex:215`). No source supplies the required uniqueness or injectivity result.

The preregistration defines only `H0 = GR/ΛCDM` versus `H1 = EFC deviation` (`docs/validation-ledger/preregistrations/axis_dl_gw_em.md:14-18`). It calls the EFC relation a code-supported candidate, says the numerical parameters and field normalization are illustrative rather than frozen, and lists waveform, lensing, host, peculiar-velocity, and EM-distance issues as declared nuisances (`.../axis_dl_gw_em.md:19-34,41-63`). The source package records the formula and the mechanism but no dataset or fit (`docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/index.json:58-70,281-301`). A frozen EFC curve is therefore a testable candidate against a comparator; it is not automatically unique to EFC merely because its parameters are no longer free.

There is a second, more formal problem with the proposed freeze. The source defines `F(φ) = 1 + αφ` (`.../index.json:152-156`) and the observable as `sqrt(F(φ0)/F(φz))` (`.../index.json:288-301`; `src/efc_relativistic.py:148-156`). Under `φ → cφ` and `α → α/c`, `F` and the distance ratio are unchanged. Separate numerical values for `α`, `φ0`, and `φ(z)` are therefore coordinate-dependent until a canonical field normalization is supplied. The manuscript itself admits that the field normalization remains to be fixed (`snapshot.tex:215`). The physically relevant freeze is the invariant trajectory `F(φ0)/F(φz)`, or equivalently the product `α[φ(z)-φ0]` after a declared normalization—not three separately frozen coordinates.

The PDF's phrase “Independent observable” means independent of the scalar-sector observables `μ`, `Σ`, and `η`, not unique among all propagation-sector theories (`.../EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction.pdf:327-346`). That distinction is not preserved by the manuscript's “uniquely EFC-discriminating” sentence.

### B. Round-1 finding that was under-weighted or over-credited

- `F-para-4` and `F-alt-6` identify the model/systematics degeneracy; this is the central defect, not merely a missing downstream comparison.
- `F-form-7` should be elevated: separate freezing of `α` and field coordinates is stronger than the observable mathematics supports, and does not cure model non-uniqueness.
- `F-para-3` is too generous in calling the paragraph appropriately cautious; its first caveat and final uniqueness assertion are internally inconsistent.
- `F-alt-5` correctly notes the asymmetric GR-versus-EFC preregistration, but the non-uniqueness remains even if the comparator set is later widened.

### C. Attack conceded not to hold

Freezing a physical, invariant EFC prediction is necessary before a siren test can evaluate the candidate relation; a null result can constrain the EFC coupling. The formula is also transcribed correctly. The attack is only against the sufficiency of parameter freezing for uniqueness, and against treating separate field-coordinate values as observables before normalization.

## C11/C12 — scope, fit provenance, and reproducibility

### A. Sharpest real weakness

“No new fit is executed” is a statement about this reconciliation, not evidence that no fit occurred anywhere. The manuscript is actually scoped that way: it says “No new fit is performed in this work” (`snapshot.tex:83-90`) and later says that numerical results cited are inherited from source packages rather than recomputed (`snapshot.tex:217-227`). The reconciliation package itself contains no `src/`, `data/`, or `examples/` and its manifest lists only 11 files (`docs/papers/efc/EFC_Model_Family_Reconciliation/ai_manifest.json:18-61`), so the narrow absence claim is supported. But it cannot close the provenance of earlier or external fits. That matters because the grid-action PDF contains the `>5σ`/“matches SPARC” assertions while its index says null fit fields and no new fit (`docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/EFC_Gradient_Coupled_Grid_Action.pdf:69-70`; `.../index.json:74-88`). The correct status is “fit provenance unresolved,” not “no fit anywhere.”

The more serious C12 defect is the opening assertion that the reconciliation is “reproducible ... by construction” (`snapshot.tex:242-244`). The current package manifest contains no `.build.sha256`, no build script, no container digest, and no `src/`, `data/`, or `examples/` stage (`ai_manifest.json:18-61`). The build script's comment says the output is deterministic given the `.tex` (`scripts/maintenance/efc_pdf_bygg.sh:24-27`), but the script only writes a checksum after the build (`.../efc_pdf_bygg.sh:43-56`), uses the mutable image tag `efc-tex:2026`, and gives a recipe based on `texlive/texlive:latest-minimal` (`.../efc_pdf_bygg.sh:10-19,38-50`). A checksum records one output; it does not establish byte determinism or pin the environment.

I ran the versioned script twice on an unchanged isolated copy. Both builds exited successfully, but the PDFs were not byte-identical: the first SHA-256 was `1316f12e4d86d3164c24c14f439e5ae16e2a107e9e5b4d29753a9f189b36e277`, the second was `32b9bd88f12ad7430780fa0f30d814f8ae46dbfeb870d79d82923c73b8229b1e`; embedded `/CreationDate` changed from `20260922204206Z` to `20260922204208Z`. The build also emitted 13 Overfull-hbox diagnostics and one float-placement warning. This reproduces the manuscript's narrower admission that byte-for-byte reproducibility is open, but it contradicts any broader reading of “reproducible by construction.” The named review gate checks deterministic regeneration of `findings_index.json`, not PDF bytes (`.github/workflows/efc-review-gate.yml:11-18,64-68`).

### B. Round-1 finding that was under-weighted or over-credited

- `F-rep-5` is correct when read narrowly: the reconciliation package contains no fit code or dataset. It is over-credited only if promoted to the global claim that no fit exists anywhere. The source PDF prevents that negative inference.
- `F-rep-6` correctly finds that the promised full AI-friendly stack is not present, but under-weights the separate environment-pinning and CI gap: the script tag and `latest-minimal` recipe do not define a byte-reproducible build, and the cited CI workflow does not test the PDF.
- `F-rep-3` is the strongest round-1 reproducibility finding and should be retained. `F-rep-1` establishes that the path is runnable in the present environment, not that it is deterministic.

### C. Attack conceded not to hold

It would be wrong to claim that the build path cannot run. The script passes syntax checking, the required Docker image was present, two-pass builds completed, and a checksum was emitted. It is also wrong to read C11 as asserting that no prior or external fit exists. The genuine failure is the absence of provenance for inherited numerical claims and the gap between a rerunnable build and a pinned, byte-reproducible build.

## Most damaging genuine defects, ranked

1. **C3: Gamma is not a demonstrated common object.** The signed entropy derivative, positive absolute/rate implementations, relativistic `□φ` source, and purported grid-action Gamma are not connected by a shared normalization or even an explicit grid-action Gamma definition. This undermines cross-package comparisons more deeply than the residual unit alone. 2. **C7/C8: KC1 is neither operationally specified nor evidentially sourced.** The PDF's `>5σ` language can leak through the Level-2 “internal direction” paragraph even though the package records null fit statistics and no new fit. 3. **C10: the siren paragraph overclaims uniqueness.** Freezing a candidate `F(φ0)/F(φz)` curve does not exclude other propagation models or systematics, and separately freezing field coordinates is not invariant before normalization. 4. **C5/C6: the two-axis claim is only taxonomy.** The RAR test measures the E-exponent proxy and explicitly does not test `Γ(ρ)`; no independent Gamma measurand or joint forward model is supplied. 5. **C9: the proposed RAR test imports a MOND/SPARC-labeled scale and a model-laden proxy.** Freezing a0 prevents post-fit shopping but does not supply independent calibration or holdout. 6. **C12/C11: artifact reproducibility and inherited-fit provenance remain open.** The PDF can be rebuilt, but the current package and CI do not establish a pinned byte-reproducible path, and “no new fit here” does not resolve prior-fit provenance.

## Weaknesses I could not substantiate

I could not substantiate that the literal `Γ_B` shape is necessarily fatal: the source uses proportionality and its code normalizes a dimensionless `ρ/ρcrit` input. I could not substantiate that the exact SPARC galaxies used to calibrate a0 are the same galaxies that a future test will fit; the record shows missing independence evidence, not proven sample reuse. I could not substantiate that no fit occurred anywhere, that KC1 is logically unfalsifiable, or that the two square-root formulas are algebraically conflated. Finally, I could not substantiate that the build is unrunnable: it runs successfully; the verified defect is nondeterministic PDF bytes and incomplete environment/provenance pinning.
