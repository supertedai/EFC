# Advocate review — round 2

## Mandate and evidentiary posture

This is the strongest source-grounded defense of the reconciliation manuscript against the round-1 high-severity and contradictory findings. It does **not** convert a provenance/status reconciliation into an empirical validation. The manuscript's central claim is narrower: it maps a heterogeneous EFC corpus, preserves unresolved source conflicts, assigns claim maturity, and records future discriminators without claiming that they have been run.

The governing scope is explicit in `EFC_Model_Family_Reconciliation.tex:83-91` and `:215-225`: the document is not a new empirical test, physical confirmation, supersession claim, or independent peer review; no new fit is performed; and no selection or physical falsification is asserted. This is claim `C01` and, with the package metadata, `C17`. The round-1 review is therefore strongest when it tests whether the manuscript accurately describes provenance and epistemic status, and weakest when it treats unresolved source-level physics as though this reconciliation had claimed to close it.

## Verdict

| Round-1 finding | Advocate disposition | Consequence | Core reason |
|---|---|---:|---|
| FORM-001 / FORM-002 and PHYS-GAMMA-002: `Gamma_B` dimensionality and missing normalization | **Partially valid as a source-consistency objection; not a demonstrated manuscript fabrication or empirical failure** | MINOR/DEFER for this reconciliation; BLOCKING for any future unified physical use of the forms | The manuscript transcribes the declared source form and explicitly records the source's internal A/B divergence and unresolved status. The missing prefactor belongs to the source declaration; it is not evidence that the reconciliation silently selected or validated `Gamma_B`. |
| FORM-003 / FORM-004: “two orthogonal axes” and `Gamma_B` omission | **Partially valid; the intended claim is a narrative synthesis, not a proved metric orthogonality** | MINOR for wording/table completeness; no damage to the provenance thesis | The text calls them model-family axes and warns not to conflate them. “Orthogonal” is defensible as a taxonomy of distinct choices, not as a theorem of statistical or geometric independence. |
| KC1 represented as a threshold rather than a result | **Reviewer premise is wrong on the central point** | NO CHANGE to epistemic status | The manuscript explicitly calls KC1 a conditional falsification criterion and says it is not a reported result; source metadata has null `delta_chi2`/significance and “no new fit performed.” |
| Preregistrations represented as proposed/not yet valid | **Reviewer premise is wrong or overstates the objection** | NO CHANGE | Both preregistration files explicitly say `proposed — awaiting author freeze`, `not executed`, and identify the exact blockers. Axis 1 is explicitly `INVALID until this is fixed`; Axis 2 says its numeric EFC prediction is not frozen. |
| Siren test described as predictive | **Partially valid against one adjective; not a valid charge against the status claim** | MINOR wording risk; no empirical overclaim | The formula is a source-traceable candidate mechanism, but the manuscript also says parameters are not frozen, the test is future, and no result is claimed. “Single paradigm-resistant discriminator” is interpretive and stronger than the source evidence, but it does not turn the test into an executed prediction. |
| “Related packages empty” | **Reviewer is correct that the literal categorical statement is overbroad; central provenance conclusion survives** | MINOR | `31941465` has `builds_on`/`informs` relations and `31878760` has a companion relation. Four of six package indexes are empty. The defensible reading is that the package corpus is not reliably cross-linked as a complete graph and that the ledger remains the authoritative cross-link layer. |

## 1. `Gamma_B`: dimensionality and missing normalization

### Reviewer concern

FORM-001, FORM-002, and PHYS-GAMMA-002 observe that, if `rho` and `rho_crit` carry the same density dimension, then

- `Gamma_A = rho/(rho+rho_crit)` is dimensionless;
- `Gamma_C = sqrt(rho/rho_crit)/(1+sqrt(rho/rho_crit))` is dimensionless;
- `Gamma_B = rho^(3/2)/(rho+rho_crit)` has residual dimension `sqrt([rho])` unless a prefactor or reference scale is supplied.

That algebraic observation is correct **under the reviewer’s common-unit interpretation**. It does not, however, establish that the manuscript made a hidden empirical claim that the three source declarations are already one dimensionally normalized observable.

### Defense

The manuscript is a reconciliation of declared corpus forms, not a new derivation that imposes a common normalization. It reports the three forms exactly as they occur in the source/status layer at `EFC_Model_Family_Reconciliation.tex:133-141`. It then assigns different maturity labels at `:143-149`: `Gamma_A` is proposed, `Gamma_B` is declared derived but internally tense and non-saturating, and `Gamma_C` is a declared companion upgrade, untested, with supersession not established. That is the opposite of silently asserting that A, B, and C are interchangeable calibrated functions.

More importantly, the source corpus itself supplies the reason the reconciliation must preserve the discrepancy rather than repair it by inference:

- `docs/papers/efc/Derivation_of_the_Entropy_Production/index.json:49-55,108` gives a saturating `Gamma_0 rho/(rho+rho_crit)` in the description/core equation and a `rho^(3/2)/(rho+rho_crit)` Scenario B in `key_result`.
- The same index has null `delta_chi2`, null significance, no datasets, and verdict `N/A` at `:54-63`; it therefore cannot support a claim that the dimensional issue was empirically resolved.
- The authoritative maturity register records `Gamma_B` as `declared_derived`, non-saturating, tested false, and `supersession_status: not_established` at `form_status_register.json:23-32`.
- The companion package records `Gamma_C` as a separate declared bridge, also untested, at `Density_of_States_of_Gravitationally/index.json:41-62` and the register `:35-45`.

The manuscript also states the critical provenance conclusion plainly at `:151-153`: the divergence is an A/B bifurcation in the package's own fields, not a settled selection, and the forms are treated as a family rather than a maturation chain. Thus the missing `Gamma_B` prefactor is best classified as a **source-level normalization defect/open dependency**, not as a failure of the reconciliation to report what the source says. The round-1 criticism becomes a manuscript error only if the manuscript had claimed that the forms were already dimensionally unified or physically interchangeable. It does not make that claim; its status vocabulary and non-supersession language expressly prevent that inference (`C04`, `C05`, `C06`, `C12`).

### Chain-rule objection

The sentence `sigma_s = Gamma(rho) dot-rho (chain rule)` at `:127-131` is algebraically valid for each model once an entropy function and its units are specified: `dot S = (dS/drho) dot-rho`. The review correctly identifies that a **single common dimensional convention** for all three source forms is not established. But that is not a contradiction of the manuscript's narrower provenance statement. It is a boundary condition for future model unification.

The strongest fair conclusion is therefore:

> `Gamma_B` must not be used in a common normalized likelihood, linear combination, or shared entropy-density interpretation until the source author supplies the missing scale or declares separate entropy conventions. This unresolved source issue does not falsify the manuscript's claim that the corpus contains the declared forms and that their relation is not settled.

**Disposition:** `DELVIS VALID / MINOR + DEFER / E0-E1`. The review has identified a real prerequisite for future physics closure, but it has not shown that the reconciliation misrepresented the source or promoted `Gamma_B` to a validated result. The missing prefactor is source inconsistency, not a new manuscript result.

## 2. “Orthogonal axes”: narrative synthesis or mathematical theorem?

### Reviewer concern

FORM-003 and FORM-004 argue that “orthogonal” normally requires a parameter space and metric/inner product, that no joint generative model is supplied, and that `Gamma_B` is absent from the table describing the `Gamma` axis. FORM-004 also notes tension between `:158` (“each with a discriminant”) and `:209` (no preregistered `Gamma` discriminator).

### Defense

The manuscript's actual semantic anchor is **model-family structure**, not a claim of a proven statistical factorization. Section 2 says the two axes are “model-family axes,” distinguishes them from the preregistered test axes, and explicitly warns that the taxonomies must not be merged (`:155-164`). It further says that the reconciliation “freezes the structure as two open selections,” not that data have established their independence (`:164`). Section 8 says no selection on either axis is made (`:217-225`).

The axes are defensible as a narrative/synthetic coordinate system because they separate two different source-level choices:

1. the BE/screening exponent, `E proportional to g^alpha`, with `alpha=1` versus `alpha=1/2`, sourced to the grid-action package (`:160`; `31941465/index.json:53-75`); and
2. the density-response shape, with the saturating A form and square-root saturation C form (`:162`; `31942821/index.json:49-55`; `31942800/index.json:41-51`).

This separation is not invented from no evidence. The source packages describe different mechanisms and observables: the grid-action index makes `E proportional to sqrt(g)` conditional on the gravitational regime `alpha g >> kappa_0` (`:53-59`), while the density-of-states package derives its own `D_eff` and `Gamma` bridge (`:41-47`). The ledger claim `C07` correctly calls this a “partially supported synthesis,” not a demonstrated independence theorem.

The reviewer is right that “orthogonal” is too strong if read as a formal metric statement. The advocate defense is not that a metric exists; it is that the manuscript uses “orthogonal” narratively to prevent a known category error: the occurrence of a square root in the energy exponent does not select the square-root density form. The text makes that anti-conflation purpose explicit at `:164`.

### `Gamma_B` and the table

The reviewer correctly notices that `Gamma_B` appears in `:133-140` and `:147` but is omitted from the compact axis table at `:171-174`. That is a completeness defect in the visualization, not evidence that the corpus mapping is false. `C04` and `C06` show that B is explicitly part of the reconciliation, and the prose records its non-saturating status. The table can therefore be read as showing the two principal *axis endpoints/representative realizations* rather than an exhaustive list, but the absence is still a legitimate minor ambiguity. It cannot be elevated to a high-severity failure because the immediately preceding prose names all three forms and explains why B is unresolved.

### “Each with a discriminator” versus no Gamma preregistration

There is a coherent distinction between:

- an axis being conceptually discriminable in a future model comparison; and
- an axis having a currently frozen, valid preregistration.

The manuscript uses “future test” at `:158`, then explicitly states at `:209` that the `Gamma` shape has no preregistered discriminator. The two claims are compatible if “discriminant” means a possible future discriminating observable, not an already frozen test protocol. The round-1 critique correctly identifies a wording ambiguity, but not a logical impossibility.

**Disposition:** `DELVIS VALID / MINOR / E1`. Defensible as narrative synthesis; not defensible as a claim of formal independence. The strongest interpretation is “two presently separate descriptive axes whose physical independence remains to be demonstrated.”

## 3. KC1 is a threshold, not a result

This is the clearest case where the round-1 high-severity framing should be rejected.

The manuscript explicitly separates three levels at `EFC_Model_Family_Reconciliation.tex:181-190`:

1. **Wording:** KC1 is an explicit conditional criterion: if a robust, bias-controlled comparison prefers the linear form and excludes the square-root form at `>=5 sigma`, then the `E proportional to sqrt(g)` theorem is falsified (`:184-186`).
2. **Internal direction:** the source PDF's operator-selection argument favors the square-root operator (`:188`). This is described as internal direction, not as an external fit.
3. **Provenance gap:** `delta_chi2` and significance are null and the package records “no new fit performed”; the status is open and author-gated (`:190`).

The source index independently confirms this reading:

- `EFC_Gradient_Coupled_Grid_Action/index.json:74-88` has null fit/significance fields, a referenced SPARC conceptual consistency statement, and verdict `N/A`.
- `:102-107` states KC1 conditionally: only if the linear form is preferred and the square-root form is excluded at `>=5 sigma` is the theorem falsified.
- The status register records KC1 as `proposed`, not tested, with the remaining provenance question author-gated (`form_status_register.json:67-73`).

The preregistration review also supports the distinction: the Axis 1 proposal says the two forms are competing forms, not two regimes, and defines a predeclared comparison, but marks the exact `a0` and other protocol fields as not yet frozen (`axis_e_sparc_rar.md:1-5,16-26,44-67`).

The round-1 statement that KC1 is “not executable as written” can be accepted as a future protocol critique, but it cannot be used to say that the manuscript presents KC1 as an executed result. The manuscript does the opposite: it labels the criterion conditional and preserves the open provenance. It also avoids the invalid converse: failure to obtain `>=5 sigma` would not prove the theorem. That is consistent with the falsification review's own logic.

**Disposition:** `STRAW-MAN / NO CHANGE / E0`. Any remaining issue is protocol completion for the future test, not a misrepresentation in this reconciliation.

## 4. Preregistrations are proposed and not valid/executed yet

The manuscript's treatment is directly supported and should be defended without qualification.

At `EFC_Model_Family_Reconciliation.tex:206-213`, it says both discriminators are proposals, status `proposed`, awaiting author freeze, and not executed. It separately states that the `Gamma` axis has no preregistered discriminator. It then identifies the open `a0` and siren parameter decisions rather than implying they are frozen.

### Axis 1: SPARC/RAR

`docs/validation-ledger/preregistrations/axis_e_sparc_rar.md` is unambiguous:

- status is `proposed — awaiting author freeze`, not executed, not fitted, not published (`:1-5`);
- the two exponent forms are specified as competing forms (`:9-18`);
- three `a0` candidates circulate and exactly one must be fixed (`:44-56`);
- the record states: “The preregistration is INVALID until this is fixed” (`:55-56`);
- M/L, distance, inclination, gas model, likelihood, and holdout discipline remain declared/open requirements (`:61-76`);
- the open author decisions are explicitly blocking (`:113-117`).

The manuscript's phrase “the papers record `a0=1.2e-10` as the normative screening scale” is not a claim that the preregistration is valid. The next sentence says the canonical value is author-gated and the test is not valid until one value is fixed (`EFC_Model_Family_Reconciliation.tex:211`). That is exactly the distinction the review asks for.

### Axis 2: GW/EM siren

`axis_dl_gw_em.md:1-5` gives the same proposed/awaiting-freeze status. It distinguishes a code/metadata-supported candidate formula from a frozen numerical prediction at `:19-34`, and says the formula's parameters are illustrative defaults, not frozen predictions. The exact remaining decisions are listed at `:105-110`. The null test may be registered as a constraint, but a numeric EFC prediction is not valid until `alpha`, `phi_0`, field normalization, and evolution are frozen (`:85-91`).

The manuscript therefore does not call either preregistration executed, published, or valid in its current state. It records intent plus blockers. That is the correct status for a provenance reconciliation.

**Disposition:** `STRAW-MAN / NO CHANGE / E0`. The reviewer is right that the tests are not yet runnable as definitive preregistered predictions; that is already the manuscript's explicit conclusion, not a defect in it.

## 5. Siren-test predictive status

### Strongest criticism

PHYS-SIREN-001 and the alternatives review correctly warn that `d_L^GW != d_L^EM` is not unique to EFC, and that the expression requires parameter freezing, field normalization, positivity/regularity, and control of waveform, lensing, host, and EM-distance systematics. The phrase “single paradigm-resistant discriminator” at `EFC_Model_Family_Reconciliation.tex:213` is therefore an interpretive characterization, not a source-established theorem.

### Defense of the manuscript's actual status claim

The manuscript does not present a numerical siren forecast or a measured anomaly. It says:

- the relativistic-action package contains the ratio formula;
- a future multi-messenger sample would test the inequality;
- the coupling parameters are not frozen; and
- freezing them is a separate author-gated step (`:213`).

Those statements are source-backed:

- `EFC_Relativistic_Action.../index.json:28-35` gives the non-minimal action and flow constraint;
- `:58-70` records null fit/significance and no dataset;
- `:281-301` gives `d_L^GW = d_L^EM sqrt(F(phi_0)/F(phi(z)))` and the linearized relation;
- `axis_dl_gw_em.md:19-34` expressly labels the formula code/metadata-supported and not a frozen numeric prediction;
- `:85-91` makes a null result legitimate and requires parameter freezing before testing the EFC curve.

The correct defense is therefore limited: the manuscript is entitled to call this a **candidate discriminator/mechanism** because a source package supplies an action-level propagation sector and a closed-form candidate ratio. It is not entitled to claim that any observed distance mismatch would uniquely confirm EFC. The manuscript's own scope and “not tested” section prevent that stronger reading (`:215-225`).

The phrase “paradigm-resistant” can be defended only in the narrow operational sense used by the preregistration: the equality null `r(z)=1` is a directly stated propagation comparison rather than a fit that presupposes a particular `Gamma(rho)` or galaxy-sector model. It does not mean immune to all model alternatives or systematics. The alternatives review is correct that this stronger connotation should be treated as a wording risk.

**Disposition:** `DELVIS VALID / MINOR / E0-E1`. The test's predictive status is correctly marked proposed and unfrozen; only the comparative adjective is stronger than the evidence. No empirical overclaim has been demonstrated.

## 6. The “related packages empty” finding

### What the round-1 review got wrong

The Cartographers' “dangling DOI” objection is a reviewer miss. `EFC_Gradient_Coupled_Grid_Action/index.json:111-126` identifies DOI `10.6084/m9.figshare.31940469` as the `efc-screening` package that informs the grid-action package. The verified package mapping is therefore not a dangling DOI merely because the repository review scope did not locate a matching local directory. The manuscript's six primary Table 1 mappings are separately verified by `C02`: all six paths exist and their `index.json` DOI fields match `EFC_Model_Family_Reconciliation.tex:104-123`.

The source package also has valid cross-links that the round-1 categorical reading missed:

- `31941465` has `builds_on` relations to `31878760` and `31878334`, and `informs` `31940469` (`index.json:111-126`);
- `31878760` has a companion relation to `31878334` (`index.json:91-97`).

Thus the source graph is not “all related_packages empty.” Four of six packages do have empty arrays, but the other two contain meaningful relations. This is material because it confirms that the corpus has both package-local and ledger-mediated provenance, rather than no provenance links at all.

### What can still be defended in the manuscript

The manuscript's substantive provenance point at `:95-102` is that package linkage should not be treated as a complete, silently authoritative graph and that the validation ledger is the source of truth for claim status. That remains defensible even after correcting the literal parenthetical “their related packages fields are empty.” The package indexes are heterogeneous: some carry relations and some do not; the ledger additionally records status, preregistration dependencies, and unresolved author gates. A complete reconciliation therefore cannot infer the whole claim graph from `related_packages` alone.

The strongest fair disposition is not to deny the literal mismatch. It is to narrow its consequence:

> The manuscript overstates the emptiness of package-local relation fields, but it does not thereby lose the six-package identity mapping, the ledger status mapping, or the central claim that provenance and claim maturity must be reconciled across both package metadata and the validation ledger.

The claim map itself records the correction: `package_graph.edges` contains the `31941465 -> 31878760`, `31941465 -> 31878334`, and `31878760 -> 31878334` relations at `claim_map.json:195-205`; the verified DOI `31940469` is the `informs` edge at `:122-126`. The related-package issue is therefore a minor textual overstatement, not a high-severity collapse of provenance.

**Disposition:** `VALID / MINOR / E0`. Correct the scope of the sentence in a future wording pass, but reject the conclusion that the manuscript's provenance architecture is unsupported.

## Cross-cutting defense of the central claims

### Claim family and bifurcation

`C04-C06` are not claims that A, B, and C are empirically selected or dimensionally interchangeable. They are claims that the corpus contains distinct declared forms with different ledger maturity and that the evidence supports a bifurcation label rather than an established A-to-B-to-C maturation chain. The source conflict in `31942821` is itself evidence for why the reconciliation must preserve a family/status view. The manuscript's “shape bifurcation” is therefore a synthesis label, explicitly not a source-derived theorem (`claim_map.json:49-54`; `EFC_Model_Family_Reconciliation.tex:151-153`).

### `E proportional to sqrt(g)`

`C08` is a declared derivation, not a test result. The grid-action source supplies the minimal action, effective stiffness, dispersion relation, and gravitational-regime condition `alpha g >> kappa_0` (`31941465/index.json:28-71`). Its fit fields are null and its dataset entry says no new fit (`:74-88`). The manuscript accurately preserves that status and uses KC1 as a conditional falsifier rather than as evidence that the theorem has survived data.

### Future tests are kept separate

`C13-C16` distinguish the SPARC/RAR proxy for the exponent axis from the GW/EM propagation observable. The preregistration files explicitly say the SPARC test does not test `Gamma(rho)` and the siren test does not decide the internal motor-lag mapping (`axis_e_sparc_rar.md:98-102`; `axis_dl_gw_em.md:93-97`). This separation directly answers the reviewer's concern that the siren test cannot select the density-response form: the manuscript says so.

### No confirmation is claimed

`C17` is strongly supported by the manuscript's explicit negative scope (`:215-225`) and the six package indexes' null fit/significance metadata. The reviewer's physical objections — missing GR limits, degeneracies, alternatives, and incomplete likelihoods — are valid requirements for future validation, but they do not refute a document whose declared purpose is to expose those gates without pretending they have been passed.

## Final recommendation

Defend the manuscript's central status/provenance claims. Do not defend the literal strongest reading of every adjective or compact table:

1. defend `Gamma_B` as a faithfully transcribed, unresolved source form; classify its missing normalization as a source inconsistency/open physics gate, not as an executed manuscript result;
2. defend the two axes as a narrative model-family coordinate system, while treating formal orthogonality as unproved;
3. reject the claim that KC1 is presented as a result — it is explicitly a conditional threshold with null provenance;
4. reject the claim that the preregistrations are represented as valid/executed — both files explicitly say proposed and blocked;
5. narrow “paradigm-resistant” to a future propagation-sector discriminator, not unique confirmation of EFC;
6. acknowledge the literal overstatement about empty `related_packages`, while rejecting the stronger claim that DOI provenance is dangling or that the corpus has no source relations.

The appropriate round-2 decision is therefore: **the reconciliation is defensible as a provenance- and claim-status document; several round-1 objections identify future physics/wording gates, but none overturns the manuscript's central non-confirmatory scope.**
