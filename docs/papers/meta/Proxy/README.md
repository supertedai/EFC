# Proxy

> *Proxy* is the EFC meta-principle that **measurement of complex systems
> is always cartography, not verdict.** Any observable used to stand in
> for an underlying quantity — a biomarker for disease, a benchmark for
> AI ability, a power spectrum for cosmic structure, a mirror neuron for
> intent — is **regime-bound**: valid in some part of the response
> surface, mistaken in others. The meta-principle gives a unified
> vocabulary (*regime, proxy, placement, episenter, compression*) for
> spotting when a proxy generalises and when it silently breaks.

**Originator (within EFC):** Morten Magnusson (Symbiose Research).
**Source publication (in `docs/papers/efc/`):**
- `Regime_Bound_Measurement_in_Complex_Systems_Proxy_Placement_and_Validity/`
  (2026-03-07, DOI [10.6084/m9.figshare.31564123](https://doi.org/10.6084/m9.figshare.31564123)).

This meta-layer reference places that framework inside the wider
methodological literature on **surrogate endpoints, biomarker validation,
mirror systems, and entropy proxies** — and links it forward to medicine,
cognitive science, and ML evaluation.

---

## 1. Five operative concepts

| Concept | One-line definition |
|---|---|
| **Regime** | A connected region of the system's response surface where a single law-form fits and predictions remain coherent. |
| **Proxy** | An observable variable taken to stand in for an unobserved/expensive target quantity within a given regime. |
| **Placement** | The combined choice of *where* the observer sits (instrument, sample, coordinate frame) and *how* the proxy is computed. |
| **Episenter** | The interpretive frame used to read the result (e.g. accuracy vs calibration; `z`-space vs `S`-space). The episenter shapes which residual structure looks like signal. |
| **Compression** | Reduction of high-dimensional data to a low-dimensional summary; valid compressions preserve regime topology, invalid ones average across regime boundaries. |

When all five are *aligned* — same regime, same proxy semantics, same
placement, same episenter, same compression — apparent conflicts between
models or measurements vanish. When they are misaligned, papers fight
over what are in fact different objects.

## 2. Sealed predictions (P1–P4 from the source paper)

| ID | Prediction | Falsified by |
|---|---|---|
| **P1** | Residuals at *regime boundaries* are systematically larger and less coherent than residuals within *regime interiors* when analysed on `R(k,S)`. | Boundary and interior residual distributions indistinguishable after noise/sampling control across multiple datasets. |
| **P2** | Substituting proxies (e.g. alternative `Ŝ(z)`; swapping AI metrics) induces **structured, directionally consistent drift** in fitted parameters / model rankings within the same regime. | No systematic drift beyond statistical noise under controlled proxy substitutions. |
| **P3** | Shifting the *episenter* (e.g. accuracy ↔ calibration; `z`-space ↔ `S`-space) reorganises apparent signal/residual structure without changing the raw data. | Invariance of residual maps and rankings under episenter shifts. |
| **P4** | **Placement matching** (aligning physical, instrument, and interpretive placement) reduces apparent conflicts between models or measurements. | Repeated cases where conflicts persist unchanged after rigorous placement matching and calibration checks. |

## 3. Cross-layer proxy zoo

The meta-principle is named for three classes of proxy that span the
cosmos, cognitive, and medicine layers — none of which is reducible to
the others, but all of which obey the regime-bound rule:

### 3.1 Pharmacological proxies (medicine layer)

- **Surrogate endpoints**: laboratory measurements substituting for
  clinical outcomes (e.g. LDL cholesterol for cardiovascular death,
  HbA1c for diabetic complications). Prentice (1989) criteria; Fleming
  & DeMets (1996) cautions. *Regime warning*: a surrogate validated in
  one disease, drug class, or population is **not transferable** without
  re-validation — the regime literally changes.
- **Biomarkers**: NIH BEST (2016) taxonomy (susceptibility, diagnostic,
  monitoring, predictive, prognostic, response, safety). Each is a
  proxy with its own regime.

### 3.2 Mirror proxies (cognitive layer)

- **Mirror neurons / mirror systems**: parieto-frontal cells active for
  both self-action and observed-other-action (Rizzolatti & Craighero
  2004). The empathic system, theory-of-mind, and AST's *attention
  schema* (`../../cognitive/AST/`) are all *mirror proxies* for others'
  mental states — they substitute internal simulations for direct access
  to another agent's interior.
- *Regime warning*: mirror-systems generalise within species and modality
  but fail across (e.g., motor mirroring is well-replicated; affective
  mirroring is contested — Lamm et al. 2011).

### 3.3 Entropy proxies (cross-layer)

- **Information-theoretic proxies for consciousness**: Lempel–Ziv
  complexity, PCI (Casali 2013), Φ-proxies. All proxies for *integrated
  information* — none equivalent to it.
- **Cosmological entropy proxies**: SZ-derived gas thermodynamic
  entropy, halo-virial entropy. Different definitions, different
  regimes. (Cf. EFC growth-sector paper on `WP3/R(k,S)`.)
- **Computational entropy proxies in AI**: log-perplexity, KL to base
  model, RLHF reward gap. Each is a proxy for a different abstract
  quantity (uncertainty, drift, value alignment).

## 4. Bridge claims

| Direction | Bridge claim |
|---|---|
| **Proxy → HomoFluxus** | The `R`-coefficient itself is a proxy: it compresses a high-dimensional flow field into a single scalar. Its validity *as a proxy* must be defended regime-by-regime — galaxies vs. brains vs. RL agents. (See `../HomoFluxus/`.) |
| **Proxy → Autopoiesis** | Autopoietic systems define their own operational closure; the proxies that work for *non*-autopoietic systems often fail at the boundary of self-production. The Maturana–Varela boundary itself is a placement/episenter shift. (See `../Autopoiesis/`.) |
| **Proxy → Cognitive** | Each consciousness theory deploys a different proxy: GWT uses behavioural report (a proxy via P3b), IIT uses Φ (a proxy via PCI), AST uses introspective report (a proxy for the attention-schema's read-out). The COGITATE adversarial collaboration (Nature 2025) is in EFC terms a *placement-matching* exercise. |
| **Proxy → Medicine** | Allostatic load is a multi-proxy composite (cortisol, HRV, inflammation); its predictive utility for cardiovascular and psychiatric outcomes depends critically on *regime* (life-stage, comorbidity, population). |

## 5. Wider methodological lineage

| Author | Year | Contribution |
|---|---|---|
| Donald **Campbell** | 1969–1986 | Construct validity; trait–method matrix; "looking glass" for proxies. |
| Ross **Prentice** | 1989 | Formal criteria for surrogate endpoints (a "proxy" must capture the *full treatment effect* on the true endpoint). |
| Thomas **Fleming & David DeMets** | 1996 | Demonstrated multiple failures where validated surrogates *misled* (CAST trial, AIDS surrogates). |
| Marcel **Frank & Hanno Klein** | 2018 | Surrogate-paradox under model misspecification. |
| NIH BEST | 2016 | Biomarkers, EndpointS, and other Tools (BEST) — biomarker taxonomy. |
| Giacomo **Rizzolatti** | 1992– | Mirror neurons in macaque F5. |
| Vittorio **Gallese** | 2001– | Embodied simulation hypothesis. |
| Eric **Schneider** | 2005 | Gradient-reduction proxies (MEP debate). |
| FDA / EMA | 2020s | Drug Development Tool qualification frameworks for surrogate biomarkers. |

## 6. Criticisms / open issues

1. **Concept-creep risk** — Calling everything a proxy can dilute the
   word. The framework needs explicit *non-proxy* counterexamples to
   stay sharp.
2. **Operationalising "regime"** — Regimes are easy to draw post-hoc
   from data; pre-registered regime boundaries are rare. P1 needs
   pre-registration to avoid being unfalsifiable.
3. **Episenter as observer-relative** — Critics may read the episenter
   concept as constructivist; defenders argue it is just *coordinate
   choice*, no different from rotating a basis in linear algebra.
4. **Compression validity** — Information-bottleneck and rate-distortion
   theory already give one rigorous frame for "valid compression"; the
   EFC version needs to connect to that literature explicitly.
5. **Surrogate paradox** — Even *perfectly* correlated surrogates can
   yield wrong treatment-effect conclusions when the surrogate and the
   true endpoint share an unmeasured confounder; this is a known limit
   of any proxy framework.

## 7. Key references (chronological)

- Campbell D.T., Fiske D.W. (1959) "Convergent and discriminant
  validation by the multitrait-multimethod matrix." *Psychol Bull*
  56:81–105.
- Campbell D.T., Stanley J.C. (1963) *Experimental and Quasi-Experimental
  Designs for Research*. Houghton Mifflin.
- Prentice R.L. (1989) "Surrogate endpoints in clinical trials:
  definition and operational criteria." *Stat Med* 8:431–440.
  DOI: 10.1002/sim.4780080407
- Fleming T.R., DeMets D.L. (1996) "Surrogate end points in clinical
  trials: are we being misled?" *Ann Intern Med* 125:605–613.
  DOI: 10.7326/0003-4819-125-7-199610010-00011
- Rizzolatti G., Craighero L. (2004) "The mirror-neuron system."
  *Annu Rev Neurosci* 27:169–192.
  DOI: 10.1146/annurev.neuro.27.070203.144230
- Lamm C., Decety J., Singer T. (2011) "Meta-analytic evidence for
  common and distinct neural networks associated with directly
  experienced pain and empathy for pain." *NeuroImage* 54:2492–2502.
  DOI: 10.1016/j.neuroimage.2010.10.014
- FDA-NIH Biomarker Working Group (2016) *BEST (Biomarkers,
  EndpointS, and other Tools) Resource*.
- VanderWeele T.J. (2013) "Surrogate measures and consistent surrogates."
  *Biometrics* 69:561–565. DOI: 10.1111/biom.12071
- Frank M., Klein H. (2018) "When can we identify a surrogate paradox?"
  *Stat Med* 37:471–482. DOI: 10.1002/sim.7558
- Casali A.G. et al. (2013) "A theoretically based index of consciousness
  independent of sensory processing and behavior." *Sci Transl Med*
  5:198ra105. DOI: 10.1126/scitranslmed.3006294
- Magnusson M. (2026) *Regime-Bound Measurement in Complex Systems:
  Proxy, Placement, and Validity*. Figshare preprint 31564123.

---

## EFC bridge — where to read next

- `docs/papers/efc/Regime_Bound_Measurement_in_Complex_Systems_Proxy_Placement_and_Validity/` — source paper
- `docs/papers/efc/Regime_Dependent_Growth_Enhancement___A_Transition_Metric_Interpretation_of_the_Fugaku_DESI_Matter_Density_Offset/` — concrete regime-dependence in cosmology
- `docs/papers/efc/A_Pre-Registered_Test_of_Entropy–Structure_Coupling_in_Simulated_and_Observed_Galaxy_Clusters/` — pre-registered proxy test
- `docs/papers/cognitive/IIT/papers/Casali-2013-PCI.md` (when downloaded) — PCI as Φ-proxy

---

*Curated theoretical reference. Last reviewed: 2026-05-13.*
