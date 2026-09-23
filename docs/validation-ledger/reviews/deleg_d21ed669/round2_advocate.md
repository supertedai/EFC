# Round-2 Advocate Rebuttal — EFC v2 Reading-Consistency Review

**Scope.** This is an adversarial defense of the frozen manuscript's claims against the round-1 findings. “Established” below means established as a source/provenance or formal statement, not empirically true. The reviewer files themselves state that this is same-model-family reading consistency, not independent validation.

## 1. C1/C2 — form inventory and “bifurcation, not maturation chain”

### (a) What the primary sources do establish

**31942821 genuinely contains both A and B, in the same package and version.** Its top-level `description` and `core_equations.gamma_result` give the saturating form
\(\Gamma_0\rho/(\rho+\rho_{\rm crit})\) (`/home/morten/EFC-prov/docs/papers/efc/Derivation_of_the_Entropy_Production/index.json:5,49-51`). The same file's `key_results.main_finding` repeats that form (`:54-55`), while its separate `key_result` field names \(\Gamma(\rho)\propto\rho^{3/2}/(\rho+\rho_{\rm crit})\) as Scenario B (`:108`). This is not an inference from two later papers: the coexistence is in one local package.

The executable source confirms that the two forms are not merely a metadata typo. The module header states the Scenario-B proportionality and identifies 31942800 as the companion upgrade (`.../31942821/src/entropy_production.py:5-15`). `GammaDerivation.gamma_total` implements the \(\rho^{3/2}/(\rho+\rho_{\rm crit})\) shape, while `gamma_phenomenological` implements \(\rho/(\rho+\rho_{\rm crit})\) (`.../src/entropy_production.py:198-213`). The JSON-LD likewise records the B key result and a companion-paper link to 31942800 (`.../entropy_production.jsonld:21-29`).

**31942800 contains the manuscript's C form, although the source calls it Scenario B+, not “Gamma_C.”** Its `core_equations.gamma_bridge` is \(\Gamma_0 y/(1+y)\), \(y=\sqrt{\rho/\rho_{\rm crit}}\), and its `key_results.main_finding` states the same square-root bridge (`/home/morten/EFC-prov/docs/papers/efc/Density_of_States_of_Gravitationally/index.json:41-47,50-62`). The package's `key_result` labels it Scenario B+ (`:116`), and the implementation returns that form in `EntropyProductionFunction.gamma_derived` (`.../31942800/src/density_of_states.py:201-238`). The register's cross-package label explicitly maps this form to `Gamma_C` and 31942800 (`.../docs/validation-ledger/data/form_status_register.json:35-44`). Thus C is a legitimate review label for the companion form, not a claim that the source package itself used that letter.

**“Bifurcation, not maturation chain” is faithful at the source/provenance level.** The frozen manuscript explicitly calls the three displayed expressions “distinct realized forms” and preserves the A/B divergence in 31942821 (`snapshot.tex:133-155`). More importantly, the lifecycle register does not record an empirical succession: Gamma_A is `proposed`, Gamma_B is `declared_derived` with `tested: false` and `supersession_status: not_established`, and Gamma_C is `declared_companion_upgrade` with `tested: false` and the same non-established supersession status (`form_status_register.json:12-44`). “Upgrade” is therefore a recorded relation, not evidence that B+ has physically replaced B. The source record establishes coexistence, a declared companion relation, and unresolved selection; it does not establish \(A\to B\to C\) as a tested historical maturation sequence.

This conclusion does **not** assert that the three formulas are already three independently identified physical observables. The manuscript itself says that a common \(\sigma_s\) convention and cross-object identification are not assumed until units and normalizations are fixed (`snapshot.tex:127-143`). The defensible claim is a provenance-controlled model-family bifurcation.

### (b) Round-1 finding that over-reaches, and why

**F-cart-1 over-reaches if its completeness objection is treated as a refutation of C1.** The frozen claim map makes C1 the inventory proposition and C3 the separate dimensional proposition (`claim_map.json:7-9`). The definition \(\Gamma=dS/d\rho\), chain-rule caveat, and non-identification of the various Gamma objects are important adjacent claims, but their omission from a three-form inventory does not make the inventory false. F-cart-1 correctly requests atomization and boundary conditions; it does not show that the three forms are absent or misreported.

Conversely, any reading of **F-alt-1** that denies the defensibility of the word “bifurcation” altogether would also over-reach. The source fields really do branch: A and B coexist in 31942821, and the square-root B+ expression appears in the companion package. What F-alt-1 properly blocks is promotion of that source-level branch into a claim of physical independence or empirical selection.

### (c) Round-1 findings conceded as correct

**F-prov-2 is directly correct.** It identifies exactly the decisive field-level fact: 31942821's `main_finding` and `key_result` carry different forms, and this supports coexistence/non-selection only. It does not support a preferred physical form.

**F-alt-1 is correct on the scope of the defense.** Writing \(r=\rho/\rho_{\rm crit}\), the A and C shapes are related by the reparameterization \(r\mapsto\sqrt r\), whereas \(\Gamma_B/\Gamma_A=\sqrt r\), so a constant amplitude alone does not identify B with A. That is consistent with the manuscript's open normalization/measurand caveat. The round-1 finding is therefore a valid warning against calling the inventory a completed physical taxonomy, not a reason to discard the inventory.

**F-cart-1 is correct that the surrounding definition and cross-object identity caveat must remain visible.** The defense is only that these are separate scope qualifiers, not grounds for rejecting C1/C2.

## 2. C3 — the Gamma_B residual dimension: inconsistency or normalization gap?

### (a) What the primary sources do establish

Under the manuscript's explicit premise that \(\rho\) and \(\rho_{\rm crit}\) are dimensional densities, the literal displayed B shape has residual dimension \([\rho]^{1/2}\): the numerator has dimension \([\rho]^{3/2}\), the denominator \([\rho]\), while A and C are dimensionless shape factors (`snapshot.tex:135-143`). This is the formal result identified by **F-form-3**, and it is not removed by merely naming the expression a “shape.”

But the source package also contains a normalization convention that materially narrows the diagnosis. The 31942821 source header writes the B result with proportionality, not an equality with a unitless prefactor (`.../31942821/src/entropy_production.py:5-10`). Its implementation accepts `rho_ratio` as a dimensionless input, returns `Gamma_0 * rho_ratio**1.5/(1+rho_ratio)`, and says that the result is normalized to `Gamma_0` at \(\rho=\rho_{\rm crit}\) (`.../src/entropy_production.py:167-170,198-207`). The package index likewise records the B key result with `\propto` (`.../31942821/index.json:108`).

Therefore two statements must be separated:

1. **Literal-form statement:** if the unqualified expression \(\rho^{3/2}/(\rho+\rho_{\rm crit})\) is read as a complete common response with dimensional \(\rho\), it is dimensionally incomplete. A prefactor with the compensating unit or an explicit reference-scale rewrite is needed.
2. **Implementation statement:** the code's B shape is evaluated in the dimensionless ratio \(\rho/\rho_{\rm crit}\) and multiplied by `Gamma_0`. That implementation is not shown to be dimensionally inconsistent merely because the unnormalized key-result shorthand has residual units.

The unresolved issue is **common physical normalization across A, B, and C**, not whether a dimensionless code shape can be evaluated. The register records Gamma_B's internal tension, `tested: false`, and author-gated relation status, but it does not supply a common unit convention (`form_status_register.json:23-32`). The manuscript's phrase “dimensional inconsistency is present in the source package” is thus defensible only when scoped to the source-level bare/displayed expression; read as a verdict that every implementation path is dimensionally invalid, it is too strong.

### (b) Round-1 finding that over-reaches, and why

The strongest over-reading would be to take **F-form-4** as showing that there is no source-level issue at all. The `\propto` sign and dimensionless implementation prevent the conclusion “the implemented model is necessarily inconsistent,” but they do not supply the missing units of the proportionality factor or establish that `Gamma_0` has the same physical meaning and units in all three packages. The source still leaves a cross-package normalization gap.

Likewise, **F-alt-1** would over-reach if “normalization gap” were taken to mean that the three shapes are physically identical. The ratio \(\Gamma_B/\Gamma_A=\sqrt{\rho}\) in the literal dimensional notation, or \(\sqrt{\rho_{\rm crit}}\sqrt r\) after substitution, is density-dependent and cannot be absorbed by one constant. The gap weakens the physical comparison; it does not erase the shape difference in a fixed common measurand.

### (c) Round-1 findings conceded as correct

**F-form-3 is correct exactly as stated:** the dimensional-analysis component of C3 follows under the manuscript's stated density premise.

**F-form-4 is correct on the necessary narrowing:** the source uses proportionality and the executable path uses a dimensionless ratio plus `Gamma_0`, so “unavoidable source-package inconsistency” or “implemented model necessarily dimensionally inconsistent” is not established.

**F-alt-1 is correct that the strongest honest status is a normalization/provenance gap until one physical Gamma measurand, one unit convention, and one reference-scale convention are fixed.** The appropriate defense is therefore not to insist on a universal contradiction, but to preserve C3 as a scoped warning: *the bare source expression is dimensionally incomplete for common use; the code supplies a shape-only normalization whose cross-package physical identification remains open.*

## 3. C7/C8 — KC1 as a conditional falsifier and the no-new-fit admission

### (a) What the primary sources do establish

**KC1 is a genuine conditional falsifier at the logical level.** The 31941465 package states: if robust, bias-controlled galaxy data prefer the linear-exponent screening form and significantly exclude the square-root form across diverse systems at \(\ge5\sigma\), then the \(E\propto\sqrt g\) theorem is falsified (`/home/morten/EFC-prov/docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:102-107`). That is an explicit antecedent and a falsification consequence. It is not an executed result and does not claim that the antecedent has occurred.

The theorem itself is conditional too: the same package gives \(E\propto\sqrt g\) **when** \(\alpha g\gg\kappa_0\), and defines the crossover \(g_{\rm cross}=\kappa_0/\alpha\) (`.../index.json:53-59`). The source PDF also presents the gravitational regime and the operator-selection direction in its own internal argument (`.../EFC_Gradient_Coupled_Grid_Action.pdf:67-72,103-110`). The manuscript is therefore entitled to distinguish (i) a source-internal operator-selection narrative, (ii) a conditional kill criterion, and (iii) an executed empirical fit.

**The C8 provenance admission is directly supported and honest.** The package index gives `delta_chi2: null`, `significance_sigma: null`, `datasets_used: ["Conceptual consistency with SPARC rotation curves (referenced; no new fit performed)]`, and `verdict: "N/A"` (`.../31941465/index.json:74-88`). The form register preserves the same distinction: KC1 is proposed, while its wording is resolved but the provenance of the claimed \(>5\sigma\) comparison remains author-gated (`form_status_register.json:67-74`). The manuscript says exactly that the comparison is unexecuted or externally referenced and unsubstantiated, and that no downstream status rests on it (`snapshot.tex:186-192`).

### (b) Round-1 findings that over-reach, and why

**F-fals-1 over-reaches if it uses missing operational details to deny KC1's status as a conditional falsifier.** A conditional criterion can be logically genuine before it is a complete preregistered analysis protocol. The explicit direction, threshold, and consequence make KC1 falsifiable in principle. The missing rules affect executability and reproducibility, not the existence of the conditional implication.

**F-fals-2 over-reaches only if it suggests the manuscript already treats the PDF language as measured support.** The manuscript does not do that: it records null likelihood fields, “no new fit performed,” an open provenance gate, and no physical falsification or axis selection (`snapshot.tex:192,219-227`). The finding's request for a more conspicuous quarantine is a useful editorial hardening, but not evidence that C8 is dishonest.

**F-para-5 over-reaches if it reads the manuscript's model-axis inventory as a global, unconditional law.** The manuscript is describing the source's \(E\)-axis form, not reporting a completed galaxy-wide test or asserting that the asymptotic regime holds at every \(g\). The source's condition and crossover do, however, make a global reading unsafe; the omission is a real qualification gap, not a reason to reject KC1.

### (c) Round-1 findings conceded as correct

**F-fals-1 is correct on operational incompleteness.** “Robust,” “bias-controlled,” “preferred,” and “diverse systems” are not fully decision-defined in the package, and the package does not specify the common likelihood, nuisance treatment, pooling, covariance, or multiple-testing rule. KC1 is a conditional falsifier, but it is not yet a closed executable gate.

**F-fals-2 is correct that the PDF's “significant above 5 sigma” and “matches SPARC data” sentences must not be allowed to function as downstream empirical evidence.** The index fields control the current status. The manuscript already applies that rule in substance; it should be read as source-internal language pending provenance, not as a result.

**F-para-5 is correct that the \(\sqrt g\) theorem is regime-bounded.** The honest statement is “the action gives \(E\propto\sqrt g\) in the \(\alpha g\gg\kappa_0\) regime, with a crossover,” not “the action establishes a global square-root law.” This is a precision correction to the source-faithful defense, not a failure of KC1's conditional logic.

## 4. C11/C12 — no new fit and open byte reproducibility

### (a) What the primary sources and direct artifact checks establish

The manuscript explicitly states that no new fit is executed, no axis selection is made, no independent validation is claimed, and no physical falsification is asserted (`snapshot.tex:217-227`). This is a scope statement about this reconciliation, not a universal claim that no earlier EFC fit exists anywhere.

The distributed reconciliation package is also consistent with that narrow scope. Its complete `ai_manifest.json` lists 11 files consisting of the PDF, TeX, metadata, bibliography, schema, JSON-LD, and related documentation (`/home/morten/EFC-prov/docs/papers/efc/EFC_Model_Family_Reconciliation/ai_manifest.json:18-61`). It contains no `src/`, `data/`, or `examples/` directory and no executable fit implementation. That supports “this package does not execute a new fit,” while not proving that an external or earlier package never performed one.

The manuscript's byte-reproducibility disclosure is confirmed by the build path and by an isolated rerun. The versioned build script says it builds the TeX, writes `.build.sha256`, and claims deterministic output (`/home/morten/EFC-prov/scripts/maintenance/efc_pdf_bygg.sh:24-27`); it removes the old checksum, runs two pdfTeX passes, hashes the PDF, and writes the checksum (`:43-57`). On an isolated copy of the current package, two successive builds of unchanged TeX both exited successfully but produced:

- first PDF SHA-256: `258b2552ba42a17a65f23b4bb29a84bcc319de813caee1ad8bf23ba387a94531`;
- second PDF SHA-256: `7708870daec9115d174f7d499ce9d834446776be0137d3080b7f6f6cadb44711`;
- byte comparison: non-identical;
- embedded CreationDate: `20:41:06` versus `20:41:08` UTC.

The current distributed package has no `.build.sha256` (`ai_manifest.json:18-61` and direct filesystem check), while its TeX and PDF have identical export mtimes (`2026-09-22 17:09:55.343672104 UTC`), so mtime cannot establish PDF freshness. The direct result confirms the manuscript's statement that byte-for-byte reproducibility is open and that pdfTeX timestamp/trailer metadata is a present source of nondeterminism (`snapshot.tex:242-244`). It also exposes a contradiction in the build script's “deterministic” comment; that contradiction strengthens, rather than weakens, C12's open-status wording.

The coarse repository chronology also checks out: commit `750a2366` added the TeX and PDF; `90c20672` added the authored package files; `4fd3f203`, `43ee50d1`, and `059d7857` added/fixed the manifest. The current package therefore honors a text/PDF-before-metadata sequence in a limited sense, but it does not contain the promised executable/data/example stack.

### (b) Round-1 findings that over-reach, and why

**F-rep-5 would over-reach if package absence were generalized into proof that no fit occurred anywhere.** Its evidence establishes a narrow package-level absence only. The manuscript's wording is narrower—“No new fit is executed in this work”—and is also directly stated as a methodological scope boundary.

**F-rep-6 is not a refutation of C11 or the core of C12.** It correctly identifies an incomplete packaging promise, but C12's asserted core is the open status of byte-for-byte builds and current layout warnings, not the claim that every designed AI-friendly subdirectory was actually distributed. The chronology supports a partial ordering, not completion of the full stack.

### (c) Round-1 findings conceded as correct

**F-rep-2 is correct.** The distributed package has no checksum artifact, and equal source/PDF mtimes do not prove freshness or staleness. No stronger stale-PDF conclusion is warranted.

**F-rep-3 is independently confirmed.** Two unchanged-source builds differ in hash and embedded creation time. The open reproducibility claim is therefore not merely inherited from the manuscript; it is reproduced in the current build path.

**F-rep-5 is correct within its stated scope.** The package contains no fit code or dataset, supporting the claim that this reconciliation package does not itself execute a new fit.

**F-rep-6 is correct about the incomplete full-stack artifact.** The current package does not contain `src/`, `data/`, or `examples/`, and the git history shows that metadata/manifest generation followed the initial TeX/PDF commits. That should temper any claim that the package is already a completed executable reproduction, but it does not turn the manuscript's no-new-fit or open-byte-reproducibility admissions into overclaims.

## 5. C9/C10 — discriminators and the siren caveat

### (a) What the primary sources do establish

For context, the adjacent SPARC/RAR discriminator is explicitly proposed and not executed. The preregistration says its status is “proposed — awaiting author freeze” (`docs/validation-ledger/preregistrations/axis_e_sparc_rar.md:1-5`), says exactly one \(a_0\) must be frozen before validity, and identifies the baryonic mass-model nuisance chain (`:44-76`). The 31878760 package records the \(\mu(g)\) form and an \(a_0\) value described as a measured SPARC input, but its fit fields are null, its dataset is “None (theoretical derivation),” and its verdict is N/A (`.../31878760/index.json:41-63,129-146`). The manuscript's “not EFC-derived; freeze before fitting” discipline is therefore appropriate.

For C10, the primary relativistic package does establish a declared candidate mechanism and formula. Its `action.components.non_minimal_coupling` gives \(F(\phi)=1+\alpha\phi\) with the small-product condition \(|\alpha\phi|\ll1\) (`.../31876324/index.json:147-162`), and its tensor sector gives
\[
 d_L^{\rm GW}(z)=d_L^{\rm EM}(z)\sqrt{F(\phi_0)/F(\phi(z))}
\]
with a first-order approximation and the friction constraint (`.../index.json:281-301`). The executable source implements the same ratio and approximation (`.../src/efc_relativistic.py:135-160`).

The same package records `delta_chi2: null`, `significance_sigma: null`, `datasets_used: []`, and `verdict: "N/A"` (`.../31876324/index.json:58-70`). The companion preregistration explicitly marks the formula as code/metadata-supported rather than a frozen numeric prediction, says the test is proposed/not executed, and leaves \(\alpha\), \(\phi_0\), and field normalization as blocking decisions (`docs/validation-ledger/preregistrations/axis_dl_gw_em.md:1-3,19-34,85-109`). The frozen manuscript faithfully carries all of the important caution: the inequality is not EFC-specific, it does not by itself distinguish EFC from GR systematics or other modified-gravity friction models, and the parameters are not frozen (`snapshot.tex:208-215`).

### (b) Round-1 findings that over-reach, and why

**F-para-3 is not an overreach; it is a direct confirmation of the manuscript's caution.** It correctly says that \(d_L^{\rm GW}\ne d_L^{\rm EM}\) is a class-level propagation anomaly until a specific curve and comparator are fixed.

**F-para-4 over-reaches only if it is read as saying the manuscript already claims a unique result.** The manuscript explicitly calls the siren test a candidate, says it is not executed, and says the parameters are not frozen. “Only when parameters are frozen” is best read as a necessary condition for an EFC-specific numerical prediction, not as a sufficient proof of uniqueness. If the sentence is read biconditionally, the attack is justified; if it is read as an achieved uniqueness claim, it mischaracterizes the surrounding caveats.

**F-form-7 does not overturn C10; it identifies an over-specified implementation of the freeze gate.** The source observable depends on \(F(\phi)\), and under \(\phi\mapsto c\phi\), \(\alpha\mapsto\alpha/c\), the product \(\alpha\phi\) and the exact distance ratio are unchanged. Thus freezing separate numerical values for \(\alpha\) and \(\phi\) is a convention unless a canonical field normalization is also declared. The manuscript's underlying caution is right, but its list of separately frozen quantities should be understood as a chosen parameterization, not as three separately observable requirements.

### (c) Round-1 findings conceded as correct

**F-para-3 is fully conceded.** The manuscript is appropriately cautious in refusing to treat a non-unit siren ratio as EFC-specific now.

**F-para-4 is conceded on the sufficiency point.** Freezing \(\alpha\), \(\phi_0\), and \(\phi(z)\) can turn the mechanism into a concrete candidate curve, but it does not by itself rule out generic scalar-tensor, running-Planck-mass, or other friction models. A real discriminator still requires a symmetric rival-model comparison and controlled waveform, calibration, lensing, host, and EM-distance systematics.

**F-form-6 is conceded and supports the manuscript.** The formula is source-faithful, and adding the dimensionless constant 1 to \(F=1+\alpha\phi\) requires the product \(\alpha\phi\) to be dimensionless. The source gives the functional form and small-coupling condition but does not provide a canonical field normalization or a fitted parameter set.

**F-form-7 is correct.** The invariant object to freeze is the predicted history of \(F(z)/F(0)\), equivalently the relevant product/difference under a declared field convention—not arbitrary separate coordinates \(\alpha\) and \(\phi\). This is a precision correction to the freeze language, not evidence that the proposed discriminator was executed.

**F-mp-4 is fully conceded.** The ratio is a model-derived proxy assembled from two distance estimators, not a raw detector observable that uniquely identifies EFC. The primary package has no dataset or likelihood result, and the manuscript correctly keeps the test proposed, unexecuted, and non-specific until the coupling history and comparator set are frozen.

## Strongest honest defense

The manuscript's central defense survives round 1: it accurately reports a source-level family of Gamma representations, including the A/B coexistence inside 31942821 and the B+ square-root companion in 31942800; it does not convert a declared companion upgrade into supersession; it treats KC1 as a real conditional kill criterion while keeping its execution/provenance gate open; it explicitly denies a new fit, model selection, independent validation, or physical confirmation; and its statement that byte-identical builds remain open is confirmed by two different hashes from unchanged-source builds. The strongest defensible reading is therefore “source-faithful inventory and status reconciliation with formal and operational gaps,” not “validated EFC.”

## Residual gaps I cannot close

I cannot close the common physical normalization of Gamma_A/B/C, the provenance of the source PDF's SPARC \(>5\sigma\) language, the operational definitions and regime coverage required by KC1, or the missing independent/raw-data fits. I also cannot make the siren ratio uniquely EFC-discriminating by freezing parameters alone: an invariant \(F(z)/F(0)\), a canonical normalization, rival propagation models, and full measurement-systematics treatment remain necessary. Finally, the distributed reconciliation package lacks the promised executable/data/example stack and the current build is not byte-deterministic; those are open artifact/workflow gaps, not evidence that the source inventory or the manuscript's non-confirmation status is false.
