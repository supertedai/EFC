# Integrated Information Theory (IIT)

> Consciousness *is* integrated information (Φ): the cause-effect power that
> a physical system has over itself, irreducibly, from its own intrinsic point
> of view. A system is conscious to the degree it is *one* — i.e. cannot be
> partitioned without informational loss — and the *quality* of consciousness
> is the *shape* of its cause-effect structure in qualia space.

**Originator:** Giulio Tononi (Wisconsin Institute for Sleep and Consciousness,
University of Wisconsin–Madison).
**Lineage:** Tononi & Edelman (1998) → Tononi (2004, "IIT 1.0") →
Balduzzi & Tononi (2008, IIT 2.0) → Oizumi, Albantakis & Tononi (2014,
IIT 3.0) → Albantakis, Barbosa, Findlay, Grasso, Haun, Marshall, Mayner,
Zaeemzadeh, Hendren, Mathis, Williford, Tononi (2023, IIT 4.0).

---

## 1. The five phenomenological axioms

IIT begins not with the brain but with what we know about consciousness from
the inside. Tononi (2008, 2015) distils experience itself into five axioms;
each is then mapped onto a postulate about physical substrates.

| # | Axiom (phenomenal) | Postulate (physical) |
|---|---|---|
| 0 | **Existence** — Experience exists, intrinsically, for itself. | A conscious system must have intrinsic cause–effect power — it must make a difference *to itself*. |
| 1 | **Intrinsicality** | Power must be exercised from within, not from an external observer's perspective. |
| 2 | **Information** | Each experience is *specific*: it is *this* one rather than any other. Substrate must specify a particular cause-effect structure. |
| 3 | **Integration** | Experience is *unified*: not decomposable into independent parts. Substrate's Φ must be > 0 across any partition. |
| 4 | **Exclusion** | Experience has *definite borders* (this much, not more, not less; over this time-grain). Substrate is the *maximally* irreducible complex — Φ_max. |
| 5 | **Composition** | Experience is structured: it has parts, each with its own quality. The cause-effect *structure* is composed of distinctions and relations. |

(IIT 4.0 collapses Intrinsicality + Existence and adds Composition explicitly.)

## 2. The mathematical object: Φ

For a finite, discrete system in a state, IIT defines:

```
φ(mechanism, purview) =
    distance between the cause-effect repertoire of the mechanism
    and the partitioned repertoire (where the mechanism's elements
    are cut from its purview).
```

Aggregating over all mechanisms and all purviews yields the system's
**cause-effect structure** (CES). The system-level integrated information is

```
Φ = irreducibility of the entire CES under the minimum-information partition.
```

A *complex* is a set of elements whose Φ is locally **maximal** — Φ_max —
no overlapping or larger set has higher Φ. By the **exclusion postulate**,
only the Φ_max set is conscious; overlapping non-maximal candidates are not.

### Distance metrics through history

- IIT 2.0 (2008): KL divergence (`Φ_E`, "effective information").
- IIT 3.0 (2014): Earth-Mover's Distance (Wasserstein) over repertoires.
- IIT 4.0 (2023): Intrinsic information measured by *intrinsic difference*
  (a generalised KL with monotonicity properties matching the axioms).

## 3. Qualia space and structure

The CES is interpreted as a point in **qualia space** Q — a high-dimensional
manifold whose axes are concept-purview combinations. Two experiences are
*qualitatively similar* iff their CESs are close in Q. This is IIT's
attempt to explain not only the *amount* but the *quality* of experience.

## 4. Empirical predictions and tests

| Domain | Prediction | Status (2026-05) |
|---|---|---|
| **Cortical posterior "hot zone"** | The neural substrate of phenomenal experience is in posterior cortex, *not* prefrontal. | Partially supported (Boly et al. 2017; COGITATE 2025) |
| **Cerebellum** | Despite ~ 80 % of neurons, cerebellum has low Φ (feed-forward, modular). Removal should not abolish consciousness. | Consistent with clinical data (aplasia cases). |
| **Anaesthesia / NREM** | Long-range integration breaks down → Φ falls. Perturbation Complexity Index (PCI) operationalises this. | Replicated in dozens of studies (Casali et al. 2013; Sarasso et al. 2015). |
| **Disorders of consciousness** | PCI distinguishes vegetative from minimally-conscious patients without behavioural report. | Replicated. |
| **Feed-forward networks** | Pure feed-forward systems (most large language models, current transformers) have Φ = 0 in their forward pass. | Theoretical; see Findlay et al. 2024 *Nat Neurosci* commentary. |
| **Split-brain** | After commissurotomy, Φ_max splits in two → two conscious complexes. | Consistent with Sperry, contested for partial cases. |

The **COGITATE adversarial collaboration** (Melloni & Koch *et al.* 2023–2025,
*Nature* 2025) tested IIT vs. GWT on:

1. **Posterior vs. prefrontal location of NCC** (IIT predicts posterior).
2. **Sustained vs. transient activity** (IIT predicts sustained synchrony
   during a continuous percept; GWT predicts transient ignition at onset/offset).
3. **Inter-areal connectivity pattern** (IIT predicts posterior recurrent
   connectivity; GWT predicts long-range frontoparietal at onset).

Results were mixed for both theories; both made falsified predictions, and
neither was decisively refuted.

## 5. Computational practicalities

Full Φ is **super-exponential** in system size (computing requires
enumerating all bipartitions). Tractable proxies include:

- **Φ\*** (Kitazono et al. 2018) — stochastic interaction approximation.
- **Mismatched decoding Φ** — using Kullback–Leibler distance.
- **PyPhi** — official IIT 3.0 / 4.0 implementation,
  https://github.com/wmayner/pyphi (Mayner et al. 2018, *PLOS Comp Biol*).
- **CompPhi** — fast lookup for small networks.
- **PCI / PCI-ST** — Perturbational Complexity Index, empirically usable in
  patients via TMS + hd-EEG.

## 6. Critiques

1. **Computational intractability** — Φ is in general PSPACE-hard
   (Hanson & Walker 2024 *Neurosci Conscious*).
2. **Expander graphs / unconscious supercomputers** — Aaronson (2014, blog
   "Why I am not an Integrated Information Theorist") showed expander graphs
   with very high Φ but no behavioural sign of consciousness; Tononi
   accepts this as a feature (consciousness need not be inferable
   behaviourally).
3. **"IIT is unscientific" open letter** — In September 2023 over 100
   neuroscientists signed a letter calling IIT *pseudoscience* (Lenharo,
   *Nature* 2023). Response: Tononi et al. (2024) defended axiomatic
   approach as proto-physics, not folk physics.
4. **The reduction problem** — Why should *integrated information* feel
   like anything? IIT answers with identity (consciousness = Φ-structure);
   critics call this brute identity unsatisfying (Bayne 2018).
5. **Substrate dependence** — IIT denies functionalism: two systems with
   identical I/O can have different Φ. This makes the theory
   non-equivalent to standard cognitive science.
6. **Combination problem** — How do micro-experiences combine? IIT 4.0
   answers via *composition postulate* and *exclusion*, but criticism
   persists (Chalmers 2017).

## 7. Variants and successors

- **IIT 1.0–4.0** — Tononi lab canonical versions.
- **PCI / PCI-ST** — empirical translation, Massimini lab.
- **Integrated World Modelling Theory (IWMT)** — Safron (2020) combines
  IIT with FEP/active inference. Treats Φ_max as a Markov-blanket-defined
  generative model.
- **Geometric IIT** — Esteban-Belver et al. 2024, differential-geometric
  formulation on qualia space.

## 8. Key references (chronological)

- Tononi G., Edelman G.M. (1998) "Consciousness and complexity."
  *Science* 282:1846–1851. DOI: 10.1126/science.282.5395.1846
- Tononi G. (2004) "An information integration theory of consciousness."
  *BMC Neuroscience* 5:42. DOI: 10.1186/1471-2202-5-42  *(Open Access)*
- Tononi G. (2008) "Consciousness as integrated information: a provisional
  manifesto." *Biological Bulletin* 215:216–242.
  DOI: 10.2307/25470707
- Balduzzi D., Tononi G. (2008) "Integrated information in discrete
  dynamical systems: motivation and theoretical framework."
  *PLOS Comp Biol* 4:e1000091. DOI: 10.1371/journal.pcbi.1000091
- Oizumi M., Albantakis L., Tononi G. (2014) "From the phenomenology to the
  mechanisms of consciousness: Integrated Information Theory 3.0."
  *PLOS Comp Biol* 10:e1003588. DOI: 10.1371/journal.pcbi.1003588
- Tononi G., Boly M., Massimini M., Koch C. (2016) "Integrated information
  theory: from consciousness to its physical substrate."
  *Nat. Rev. Neurosci.* 17:450–461. DOI: 10.1038/nrn.2016.44
- Mayner W.G.P., Marshall W., Albantakis L., Findlay G., Marchman R.,
  Tononi G. (2018) "PyPhi: A toolbox for integrated information theory."
  *PLOS Comp Biol* 14:e1006343. DOI: 10.1371/journal.pcbi.1006343
- Albantakis L. *et al.* (2023) "Integrated information theory (IIT) 4.0:
  formulating the properties of phenomenal existence in physical terms."
  *PLOS Comp Biol* 19:e1011465. DOI: 10.1371/journal.pcbi.1011465
- Findlay G., Marchman R., Mayner W., Marshall W., Albantakis L., Massimini
  M., Tononi G. (2024) "Dissociating intelligence from consciousness in
  artificial systems — implications of integrated information theory."
  *Proc. Natl. Acad. Sci. (PNAS)* 121:e2402549121.
  DOI: 10.1073/pnas.2402549121

### Major critiques

- Aaronson S. (2014) "Why I am not an integrated information theorist."
  *Shtetl-Optimized* blog (academic essay).
- Bayne T. (2018) "On the axiomatic foundations of the integrated
  information theory of consciousness." *Neurosci Conscious* 2018:niy007.
  DOI: 10.1093/nc/niy007
- Doerig A., Schurger A., Hess K., Herzog M.H. (2019) "The unfolding
  argument: why IIT and other causal structure theories cannot explain
  consciousness." *Conscious Cogn* 72:49–59.
  DOI: 10.1016/j.concog.2019.04.002
- Lenharo M. (2023) "Consciousness theory slammed as 'pseudoscience' —
  sparking uproar." *Nature* (news). DOI: 10.1038/d41586-023-02971-1
- Negro N. (2024) "Phenomenology-first versus third-person approaches in
  the science of consciousness: IIT as a case study." *Phenom Cogn Sci*
  23:1–28. DOI: 10.1007/s11097-022-09849-z

---

## EFC ↔ IIT bridge

The CEM internal reflection coefficient `R = κ ⟨τ_ref⟩_E / τ_leak` plays the
role of a thermodynamically grounded scalar surrogate for Φ. Friston (2019)
*Mind & Matter* notes that, under appropriate Markov-blanket assumptions,
integrated information itself can be rewritten as a KL divergence with the
same form as free-energy `F`. In the EFC frame this becomes:

```
Φ ~ ∫ ρ_E · D_KL[ q(s) ‖ q(s_partitioned) ] dV
```

so high-Φ regions are necessarily regions of high reflection coefficient `R`
and low leakage `L`. Bridge documents:

- `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`
- `docs/papers/efc/CEM-Consciousness-Ego-Mirror/`

---

*Curated theoretical reference. Last reviewed: 2026-05-13.*
