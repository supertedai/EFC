# Predictive Processing (PP)

> The brain is fundamentally a *prediction machine*: it constantly generates
> top-down hypotheses about the causes of its sensory inputs, compares them
> against bottom-up signals, and propagates only the residual *prediction
> errors* upward — weighted by an estimate of their precision. Perception,
> action, attention, and learning all fall out of this single recurrent
> dynamic.

**Key originators / synthesisers:**
- **Helmholtz** (1860s) — perception as unconscious inference.
- **Rao & Ballard (1999)** — first concrete *predictive coding* model in
  visual cortex.
- **Friston (2005, 2010)** — generalised PP into the Free Energy Principle.
- **Andy Clark (2013, 2016)** — *Surfing Uncertainty*; philosophical
  synthesis.
- **Jakob Hohwy (2013)** — *The Predictive Mind*; epistemological treatment.
- **Anil Seth (2014, 2021)** — *Being You*; interoceptive predictive
  processing and the "controlled hallucination" view of perception.

---

## 1. The canonical microcircuit

Predictive coding stipulates a recurrent hierarchy in which each level `ℓ`:

1. Maintains an internal **expectation** `μ_ℓ` (a generative model state).
2. Sends a **prediction** `g_ℓ(μ_ℓ)` *down* to level `ℓ−1` via deep
   pyramidal/feedback connections.
3. Receives **prediction errors** `ε_{ℓ-1} = x_{ℓ-1} − g_ℓ(μ_ℓ)` *up* from
   level `ℓ−1` via superficial pyramidal/feedforward connections.
4. Weights those errors by an estimate of **precision** `π_{ℓ-1}` —
   inverse variance — controlled by neuromodulation (acetylcholine,
   dopamine, noradrenaline).
5. Updates `μ_ℓ` along the gradient of the precision-weighted error.

```
∂μ_ℓ / ∂t = − ∂F / ∂μ_ℓ
           ≈   π_ℓ⁻¹ ε_ℓ          (bottom-up driving)
             − π_{ℓ-1} ∂g_ℓ/∂μ_ℓ · ε_{ℓ-1}   (top-down correction)
             − Λ (μ_ℓ − m_ℓ)      (lateral prior pull)
```

Anatomically:
- **Deep pyramidals** (layers V/VI) carry predictions.
- **Superficial pyramidals** (layers II/III) carry prediction errors.
- **Inhibitory interneurons / matrix thalamus** modulate precision.

(Bastos et al. 2012, *Neuron* — "Canonical microcircuits for predictive
coding.")

## 2. Active inference (the motor branch)

Movements minimise *proprioceptive* prediction error: high-precision priors
over desired body states cause classical reflex arcs to enact those states.
Action is therefore "inference made flesh" — there is no separate
optimal-control hierarchy; the motor system is the descending limb of the
generative model. Equivalent forms:

| Classical view | Predictive-processing view |
|---|---|
| Sense → decide → act | Predict → suppress sensory mismatch by acting |
| Reward maximisation | Expected-free-energy minimisation |
| Belief + value separated | Beliefs *include* preferences (priors over outcomes) |

This collapses the perception/action divide and provides a single unified
optimisation: minimise (variational + expected) free energy.

## 3. Precision and attention

Attention is recast as the *gain* (inverse-variance weight) on prediction
errors. Increasing attentional precision:

- Sharpens neural tuning curves (Maunsell 2015).
- Amplifies superficial-layer gamma power (Bauer et al. 2014).
- Is controlled by cholinergic and pulvinar feedback (Yu & Dayan 2005).

This makes PP a *single* theory of attention, working memory, and conscious
access — all three reflect precision-weighted gain.

## 4. The "controlled hallucination" picture

Because perception is generated top-down and only *corrected* by sensory
data, much of conscious experience is the brain's best guess. In limits of
weak sensory drive (dreams, hallucinations, full sensory deprivation) the
hallucination is *uncontrolled*. The empirical signature: hallucinations
correlate with reduced sensory precision and increased prior strength
(Powers, Mathys & Corlett 2017, *Science*).

## 5. Empirical predictions and supporting evidence

| Phenomenon | PP account | Evidence |
|---|---|---|
| **MMN / oddball** | Prediction error on stimulus identity | Garrido et al. 2009 |
| **Repetition suppression** | Reduced error with familiar input | Summerfield et al. 2008 |
| **Binocular rivalry** | Two priors compete for high-precision interpretation | Hohwy, Roepstorff & Friston 2008 |
| **Perceptual filling-in (blind spot, Kanizsa)** | Top-down completion of generative model | Kok et al. 2012 |
| **Hallucinations (psychosis, Charles Bonnet)** | Strong priors + weak likelihoods | Powers et al. 2017 |
| **Autism** | Atypical precision allocation (Van de Cruys et al. 2014; Pellicano & Burr 2012) | Mixed |
| **Pain** | Predictive nociception, placebo as prediction effect | Büchel et al. 2014 |
| **Interoception / emotion** | Anil Seth's "interoceptive inference" — feelings are predicted body states | Seth 2013, 2021 |

## 6. Variants

- **Predictive coding (Rao-Ballard / Friston style)** — the neurally
  literal microcircuit.
- **Active inference** — adds policy selection via expected free energy
  (see `../FEP/`).
- **Hierarchical Gaussian filter (HGF)** — Mathys et al. 2014; tractable
  Bayesian filter implementing PP at meta-volatility levels. Used in
  computational psychiatry.
- **Predictive processing in the wide sense** (Clark 2016) — a philosophical
  superset that need not commit to Friston's free-energy bound.
- **Conservative vs. radical PP** — radical PP (Clark, Constant, Kirchhoff)
  claims the brain *is* a generative model (constitutive identity);
  conservative PP says the brain merely *implements* one (modelling claim).

## 7. Relationship to neighbouring theories

- **FEP** is the generalised information-theoretic foundation of PP. PP is
  the cognitive-neuroscience instantiation. (`../FEP/`)
- **GWT** ignition can be modelled as a *high-precision broadcast* of a
  winning prediction. (`../GWT/`; Whyte & Smith 2021).
- **IIT** describes the *intrinsic structure* of the conscious complex; PP
  describes the *temporal dynamics* of its hidden-state estimates. The two
  can co-exist: a system with high Φ implementing predictive coding.
  (`../IIT/`)
- **AST** says the brain models its own attention. In PP terms, AST is a
  meta-level generative model over the precision allocation process itself.
  (`../AST/`)

## 8. Critiques

1. **Where do the priors come from?** — PP can fit any data given enough
   priors; without independent constraints on prior content, the theory is
   under-determined (Williams 2018).
2. **Cognitive penetration / Müller-Lyer persistence** — many illusions are
   robust to belief change, contradicting strong top-down accounts
   (Macpherson 2012).
3. **Neuroanatomical mismatch** — Kogo & Trengove (2015) note feedforward
   error / feedback prediction segregation is not strictly observed in
   primate cortex; Bastos et al. 2012 reply with laminar-specific markers.
4. **Dark room problem** — already addressed under FEP (epistemic value
   forces information-seeking).
5. **Phenomenal-content problem** — explaining *what* it is like, not just
   the dynamics, is unsolved (Bayne 2018, Hohwy 2020).
6. **Self-fulfilling prophecy worry** (Conant–Ashby) — if predictions cause
   their own confirmation through action, why do we ever update?
   Resolved via precision allocation and counterfactual modelling.

## 9. Key references (chronological)

- Helmholtz H. (1867) *Handbuch der Physiologischen Optik.* Voss.
- Rao R.P.N., Ballard D.H. (1999) "Predictive coding in the visual cortex."
  *Nat Neurosci* 2:79–87. DOI: 10.1038/4580
- Friston K. (2005) "A theory of cortical responses." *Phil. Trans. R. Soc.
  B* 360:815–836. DOI: 10.1098/rstb.2005.1622
- Friston K. (2010) "The free-energy principle: a unified brain theory?"
  *Nat Rev Neurosci* 11:127–138. DOI: 10.1038/nrn2787
- Bastos A.M., Usrey W.M., Adams R.A., Mangun G.R., Fries P., Friston K.J.
  (2012) "Canonical microcircuits for predictive coding."
  *Neuron* 76:695–711. DOI: 10.1016/j.neuron.2012.10.038
- Clark A. (2013) "Whatever next? Predictive brains, situated agents, and
  the future of cognitive science." *Behav Brain Sci* 36:181–204.
  DOI: 10.1017/S0140525X12000477
- Hohwy J. (2013) *The Predictive Mind*. Oxford UP. ISBN 978-0199682737.
- Clark A. (2016) *Surfing Uncertainty: Prediction, Action, and the
  Embodied Mind*. Oxford UP. ISBN 978-0190217013.
- Seth A.K. (2013) "Interoceptive inference, emotion, and the embodied
  self." *Trends Cogn Sci* 17:565–573. DOI: 10.1016/j.tics.2013.09.007
- Powers A.R., Mathys C., Corlett P.R. (2017) "Pavlovian conditioning-induced
  hallucinations result from overweighting of perceptual priors."
  *Science* 357:596–600. DOI: 10.1126/science.aan3458
- Seth A.K. (2021) *Being You: A New Science of Consciousness*. Dutton.
  ISBN 978-1524742874.

### Critical / contrarian

- Macpherson F. (2012) "Cognitive penetration of colour experience."
  *Philos Phenomenol Res* 84:24–62.
- Kogo N., Trengove C. (2015) "Is predictive coding theory articulated
  enough to be testable?" *Front Comput Neurosci* 9:111.
- Williams D. (2018) "Hierarchical Bayesian models of delusion."
  *Conscious Cogn* 61:129–147. DOI: 10.1016/j.concog.2018.03.005
- Bayne T., Hohwy J. (2020) "Levels of consciousness — the predictive
  processing account." *Conscious Cogn* 81:102921.

---

## EFC ↔ PP bridge

PP supplies the dynamic *temporal* layer of CEM: the local reflection time
`τ_ref(r) = ρ_E / (σ + ε)` is dimensionally the precision-weighted timescale
of error correction. When `R > R_c ≈ 1/e`, the recurrent prediction loop
acquires sufficient gain to self-stabilise — exactly the regime in which
predictive coding becomes self-sustaining rather than driven. Bridge
documents:

- `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`
- `docs/papers/efc/Connecting_Cosmology_Neural_Entropy_and_RLHF_Bridge/`
- `docs/papers/efc/CEM-Consciousness-Ego-Mirror/`

---

*Curated theoretical reference. Last reviewed: 2026-05-13.*
