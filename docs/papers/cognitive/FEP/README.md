# Free Energy Principle (FEP)

> A unifying mathematical framework proposing that all self-organising systems
> that resist a tendency to disorder must minimise variational free energy —
> equivalently, an upper bound on sensory surprise — to maintain their
> existence.

**Originator:** Karl J. Friston (Wellcome Centre for Human Neuroimaging, UCL)
**First formal statement:** Friston, Kilner & Harrison (2006), *Journal of
Physiology — Paris*; expanded in Friston (2010), *Nature Reviews Neuroscience*.
**Current synthesis:** Friston et al. (2023), *Physics of Life Reviews*
("The free energy principle made simpler but not too simple").

---

## 1. Core claim

For any system that maintains a non-equilibrium steady state (i.e. a
*Markov-blanketed* system separating internal from external states), the
internal states will appear — from an external observer's point of view — to
**infer** the causes of their sensory states. Equivalently, the system can be
described **as if** it minimises a single quantity:

```
F[q, o] = E_q(s) [ log q(s) − log p(s, o) ]
        = D_KL[ q(s) ‖ p(s | o) ] − log p(o)
```

where:

- `o` are sensory observations,
- `s` are hidden (external) states,
- `q(s)` is the system's *recognition density* (encoded in internal states),
- `p(s, o)` is the system's *generative model* of how observations are caused,
- `D_KL[·‖·]` is Kullback–Leibler divergence.

Because `D_KL ≥ 0`, free energy is an **upper bound on surprise**
`−log p(o)` (the negative log-evidence for the model). Minimising `F` therefore
(a) makes `q(s)` approximate the true posterior `p(s | o)` (perception), and
(b) makes the agent's sensorium itself less surprising (action).

This is the same quantity used as the **Evidence Lower Bound (ELBO)** in
variational Bayes / variational autoencoders, with the sign flipped.

## 2. Active Inference (the action branch)

Action is recast as inference over future trajectories. Policies `π` (sequences
of actions) are selected to minimise **expected free energy**:

```
G(π) = − E_q(o,s|π) [ log p(o | C) ]      # pragmatic value (goal-seeking)
       − E_q(o,s|π) [ D_KL[ q(s|o,π) ‖ q(s|π) ] ]   # epistemic value (info gain)
```

- The first term drives behaviour toward preferred outcomes encoded in a prior
  `p(o | C)` (often written as preferences `C`).
- The second term is the mutual information between hidden states and
  observations under the policy — i.e. *curiosity* or *information-seeking*.

Active inference therefore unifies exploration and exploitation under a single
objective and naturally produces **habit formation**, **planning as
inference**, and **Bayesian goal-directed behaviour**.

## 3. Markov blankets and the "particular partition"

The FEP requires that the system's states can be partitioned into:

| Subset | Symbol | Role |
|---|---|---|
| Internal | μ | Encode beliefs `q(s)` |
| Sensory | s | Caused by external states, influence internal |
| Active | a | Caused by internal, influence external |
| External | η | Everything outside the blanket |

`s ∪ a` form the **Markov blanket**: internal and external states are
conditionally independent given the blanket. This partition is what allows the
"as if" inferential description.

## 4. Hierarchical / predictive coding implementation

In neural systems, FEP is most often realised as **hierarchical predictive
coding** (Rao & Ballard 1999; Friston 2005):

- Higher cortical levels send **predictions** down via deep-pyramidal feedback.
- Lower levels return **prediction errors** weighted by **precision**
  (inverse variance) up via superficial-pyramidal feedforward connections.
- Synaptic gain (often linked to neuromodulators — dopamine, acetylcholine,
  noradrenaline) implements precision weighting.

Free-energy gradient descent on this hierarchy yields the canonical update:

```
Δμ ∝ −∂F/∂μ = (precision · prediction error) − (prior pull)
```

## 5. Empirical signatures and predictions

| Domain | Prediction | Status |
|---|---|---|
| Mismatch negativity (MMN) | Modulated by precision of priors | Replicated (Garrido et al. 2009) |
| P300 | Tracks Bayesian surprise on policy-relevant cues | Supported |
| Repetition suppression | Reduced prediction error with learning | Replicated |
| Psychosis | Aberrant precision weighting → strong likelihood, weak priors | Active research (Sterzer et al. 2018) |
| Autism | High prior precision / low sensory precision (or inverse: HIPPEA, Van de Cruys et al. 2014) | Contested |
| Depression | Allostatic priors over interoception (Stephan et al. 2016) | Promising |
| Anaesthesia | Loss of precision over deep layers → integration collapse | Cross-talks with IIT/GWT |

## 6. Relation to other frameworks

- **Predictive Processing (PP):** PP is essentially the *neuronal-process
  theory* expressing the FEP in the brain. FEP is broader (it applies to any
  Markov-blanketed system); PP is its cognitive-neuroscience instantiation.
  See `../PP/`.
- **Global Workspace Theory (GWT):** Conscious ignition can be cast as a
  precision-weighted broadcast that wins a soft-max competition across
  high-level expected free energy estimates (Whyte & Smith 2021). See
  `../GWT/`.
- **Integrated Information Theory (IIT):** Φ measures *integration*; FEP
  measures *self-evidencing*. Friston (2019) showed Φ can be re-expressed as a
  KL divergence — the same currency as `F`. See `../IIT/`.
- **Attention Schema Theory (AST):** AST's "schema of attention" can be read
  as a generative model of the agent's own precision-allocation process.
  See `../AST/`.
- **Energy-Flow Cosmology (EFC):** The EFC reflection coefficient `R` and the
  FEP's `F` both measure self-modelling capacity through the lens of
  thermodynamic openness. The bridging document is
  `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`.

## 7. Criticisms and open problems

1. **Unfalsifiability concerns** — Colombo & Wright (2018) argue FEP is so
   general it risks being a tautology. Friston counters that the *form* of the
   generative model is empirically constrained.
2. **The "dark room" problem** — If agents minimise surprise, why don't they
   sit in a dark, silent room? Resolved by **expected free energy** (epistemic
   term forces information-seeking).
3. **Existence of Markov blankets** — Biehl, Pollock & Kanai (2021) showed
   that the existence of a non-trivial blanket is a strong assumption, not a
   theorem, in continuous-state systems.
4. **Computational tractability** — Full Bayesian inference is intractable;
   FEP uses *mean-field* or *Laplace* approximations whose biological realism
   is debated.
5. **Normative vs. descriptive** — Is FEP a *law* (every system must minimise
   F) or a *description* (every system can be re-described that way)? Friston
   (2023) explicitly endorses the descriptive reading.

## 8. Key references (chronological)

- Friston K., Kilner J., Harrison L. (2006) "A free energy principle for the
  brain." *J. Physiol. Paris* 100:70–87. DOI: 10.1016/j.jphysparis.2006.10.001
- Friston K. (2010) "The free-energy principle: a unified brain theory?"
  *Nat. Rev. Neurosci.* 11:127–138. DOI: 10.1038/nrn2787
- Friston K., FitzGerald T., Rigoli F., Schwartenbeck P., Pezzulo G. (2017)
  "Active inference: a process theory." *Neural Computation* 29:1–49.
  DOI: 10.1162/NECO_a_00912
- Parr T., Pezzulo G., Friston K. (2022) *Active Inference: The Free Energy
  Principle in Mind, Brain, and Behavior.* MIT Press. ISBN 978-0262045353.
- Ramstead M.J.D., Sakthivadivel D.A.R., Heins C., Koudahl M., Millidge B.,
  Da Costa L., Klein B., Friston K. (2023) "On Bayesian mechanics: a
  physics of and by beliefs." *Interface Focus* 13:20220029.
  DOI: 10.1098/rsfs.2022.0029
- Friston K., Da Costa L., Sakthivadivel D., Heins C., Pavliotis G.A.,
  Ramstead M., Parr T. (2023) "Path integrals, particular kinds, and
  strange things." *Physics of Life Reviews* 47:35–62.
  DOI: 10.1016/j.plrev.2023.08.016

## 9. Canonical implementations

- **pymdp** — Python active-inference toolkit, Heins et al. (2022).
  https://github.com/infer-actively/pymdp
- **SPM12 DEM toolbox** — MATLAB, Friston lab.
  https://www.fil.ion.ucl.ac.uk/spm/
- **RxInfer.jl** — Julia reactive message passing, Bagaev et al. (2023).
  https://github.com/biaslab/RxInfer.jl

---

## EFC ↔ FEP bridge (Stage-IV context)

Inside this repository, FEP is the **neural-process layer** of the
*Consciousness–Ego–Mirror* (CEM) field model. The reflection coefficient
`R = κ · ⟨τ_ref⟩_E / τ_leak` of CEM is dimensionally analogous to the ratio
of internal-to-external precision in active inference; CEM's critical
threshold `R_c ≈ 1/e ≈ 0.37` matches the soft-max ignition point at which
expected-free-energy gradients become globally broadcast (Whyte & Smith 2021).

See:
- `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`
- `docs/papers/efc/Connecting_Cosmology_Neural_Entropy_and_RLHF_Bridge/`
- `docs/papers/efc/CEM-Consciousness-Ego-Mirror/`

---

*This file is a curated theoretical reference. It is not a peer-reviewed
publication; original papers are linked above. Last reviewed: 2026-05-13.*
