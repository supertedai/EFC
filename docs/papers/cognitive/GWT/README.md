# Global Workspace Theory (GWT) / Global Neuronal Workspace (GNW)

> Consciousness is the *broadcast* of selected information from many local,
> unconscious processors into a brain-wide "global workspace" that is, in turn,
> available to all of those processors. The theater metaphor: a lit stage
> (workspace) attended to by a dark audience (specialised modules).

**Originators:**
- **Bernard J. Baars** — *A Cognitive Theory of Consciousness* (1988),
  Cambridge UP. Psychological / cognitive-architecture version.
- **Stanislas Dehaene & Jean-Pierre Changeux** — Global Neuronal Workspace
  (GNW), neural instantiation, 1998 onward.

**Current synthesis:** Mashour, Roelfsema, Changeux & Dehaene (2020),
*Neuron* — "Conscious processing and the global neuronal workspace
hypothesis."

---

## 1. Core architecture

| Element | Function |
|---|---|
| **Specialised processors** | Massively parallel, unconscious modules (vision, language, motor, memory…) compete via salience and task-relevance. |
| **Global workspace** | A capacity-limited bottleneck (≈ one coherent content at a time) implemented by long-range cortical neurons. |
| **Broadcast** | When a coalition wins competition, its content is *ignited* and made widely available — this is the moment of conscious access. |
| **Attentional spotlight** | Modulates which coalitions can compete for ignition; precision/gain on prediction errors (FEP overlap). |
| **Audience (the unconscious)** | All non-broadcasting processors that nonetheless receive the broadcast. |

Capacity ≈ 1 content × ~250 ms refresh ≈ 4 bits / s of conscious throughput
(Baars 1988, Tononi 1998) — compared to ~10^7 bits / s sensory bandwidth.

## 2. Neural correlates (GNW)

Dehaene & Changeux identify the workspace with a network of long-axon
pyramidal neurons in layers II/III and V of:

- **dorsolateral and inferior prefrontal cortex** (PFC),
- **anterior cingulate / medial frontal cortex**,
- **inferior parietal lobule / temporoparietal junction**,
- **precuneus / posterior cingulate** (under dispute — see § 6).

These neurons form a **small-world, high-degree** connector hub whose
non-linear ignition dynamics give a sharp all-or-none transition.

### Empirical signatures of ignition

| Marker | Latency | Modality | Reference |
|---|---|---|---|
| **P3b (P300)** | ~ 300–500 ms post-stimulus | EEG | Sergent et al. 2005 |
| **Late frontoparietal gamma** | > 200 ms | iEEG / MEG | Gaillard et al. 2009 |
| **Long-range theta–gamma coupling** | > 200 ms | iEEG | Noy et al. 2015 |
| **Sudden BOLD ignition in PFC + parietal** | > 250 ms | fMRI | Dehaene et al. 2001 |
| **Increased meta-stability of large modules** | sustained | EEG/MEG | Demertzi et al. 2019 |

These all *follow* the early sensory volley (< 200 ms) which is largely
unconscious.

## 3. Predictions and contrast experiments

GWT/GNW makes sharp predictions in **threshold, masking, and inattention**
paradigms:

1. **Attentional blink** — second target (T2) presented 200–500 ms after T1
   is suppressed because the workspace is busy. ✓ Replicated.
2. **Masking** — Backward masking abolishes ignition while preserving early
   visual response. ✓
3. **Inattentional blindness** — Unattended salient stimuli (e.g. the
   "gorilla") never enter the workspace. ✓
4. **No-report paradigms** — Even without overt report, ignition correlates
   appear when stimuli are *reportable in principle* (Pitts et al. 2014).
5. **Anaesthesia / NREM sleep** — Long-range coupling collapses; perturbation
   complexity index (PCI) falls below ~ 0.31 (Casali et al. 2013).
6. **Disorders of consciousness** — Vegetative-state patients lack P3b;
   minimally-conscious patients retain it (Naccache et al. 2017).

## 4. Computational model (Dehaene–Changeux 2003 / 2005)

Spiking simulation with two layers:

- **Sensory layer:** stimulus-driven, fast, local.
- **Workspace layer:** sparse long-range neurons with reciprocal excitatory
  loops, NMDA-dominated for slow recurrent ignition; GABAergic interneurons
  enforce winner-take-all.

The system shows a **bifurcation** between sub-threshold (unconscious,
graded) and supra-threshold (conscious, all-or-none) regimes — matching the
ignition signature in EEG.

```
Ignition ⇔ stimulus strength × top-down attention > θ_critical
```

This is mathematically a soft-max with a temperature parameter set by
neuromodulatory gain (cf. precision in FEP).

## 5. Variants and successors

- **Global Neuronal Workspace (GNW)** — Dehaene, Changeux, Naccache: the
  neural instantiation summarised above.
- **Conscious Turing Machine (CTM)** — Blum & Blum (2022) *Proc. Natl Acad.
  Sci.* — formal automaton expressing GWT in computer-science terms.
- **Predictive Global Neuronal Workspace (PGNW)** — Whyte & Smith (2021):
  GNW reformulated under active inference; ignition = soft-max over
  expected-free-energy estimates.
- **LIDA** (Franklin et al. 2014) — software cognitive architecture
  implementing Baars' theater literally.

## 6. The "front vs. back" debate

A major controversy: are conscious contents principally generated in
**posterior hot-zone** cortex (Koch, Tononi, Boly 2016) or **prefrontal
broadcast** (Dehaene, Naccache, Mashour)?

- **Posterior view (IIT-aligned):** Phenomenal experience lives in
  posterior cortex; PFC activity reflects *reporting and access*, not
  experience itself. Supported by no-report paradigms (Frässle et al. 2014)
  and stimulation studies.
- **Anterior view (GNW):** Without long-range ignition reaching prefrontal
  hubs, there is no awareness; PFC ablation reduces conscious access (Del
  Cul et al. 2009).

The COGITATE adversarial collaboration (Melloni, Mudrik, Koch et al.
2023–2025) is testing both head-on; first results (Cogitate Consortium,
*Nature* 2025) provided partial support for both and partial falsification
of strong-form predictions of each.

## 7. Relation to other frameworks

- **vs. IIT:** IIT predicts consciousness can exist *without* broadcast
  (e.g. silent posterior coalition); GWT denies this. (`../IIT/`)
- **vs. FEP / PP:** Ignition can be derived as a precision-weighted
  surprise-minimising broadcast (Whyte & Smith 2021). (`../FEP/`, `../PP/`)
- **vs. AST:** AST locates the *content of awareness* (the schema); GWT
  locates the *mechanism of broadcast*. They are compatible —
  Graziano (2019) explicitly aligns them. (`../AST/`)

## 8. Criticisms

1. **Reportability ≠ consciousness** — strong no-report data challenge the
   identification of ignition with phenomenal experience.
2. **PFC necessity** — Boly et al. (2017) argue lesions to PFC do not
   abolish phenomenal experience; Odegaard et al. (2017) reply.
3. **Capacity granularity** — Recent work (Forster et al. 2020) suggests the
   "one item at a time" rule is too strict; multiple chunks can coexist.
4. **Functional vs. phenomenal** — GWT is fundamentally a theory of
   *access* consciousness (Block 1995). Whether it explains phenomenal
   consciousness is unsettled.

## 9. Key references (chronological)

- Baars B.J. (1988) *A Cognitive Theory of Consciousness*. Cambridge UP.
  ISBN 978-0521427432.
- Dehaene S., Naccache L. (2001) "Towards a cognitive neuroscience of
  consciousness: basic evidence and a workspace framework." *Cognition*
  79:1–37. DOI: 10.1016/S0010-0277(00)00123-2
- Dehaene S., Changeux J.-P. (2011) "Experimental and theoretical
  approaches to conscious processing." *Neuron* 70:200–227.
  DOI: 10.1016/j.neuron.2011.03.018
- Dehaene S. (2014) *Consciousness and the Brain*. Viking.
  ISBN 978-0670025435.
- Mashour G.A., Roelfsema P., Changeux J.-P., Dehaene S. (2020)
  "Conscious processing and the global neuronal workspace hypothesis."
  *Neuron* 105:776–798. DOI: 10.1016/j.neuron.2020.01.026
- Blum L., Blum M. (2022) "A theory of consciousness from a theoretical
  computer science perspective: insights from the Conscious Turing Machine."
  *PNAS* 119:e2115934119. DOI: 10.1073/pnas.2115934119
- Cogitate Consortium (2025) "Adversarial testing of global neuronal
  workspace and integrated information theories of consciousness."
  *Nature* (in press). DOI: 10.1038/s41586-025-08888-x

---

## EFC ↔ GWT bridge

In the EFC / CEM model, ignition corresponds to the moment the *reflection
coefficient* `R` exceeds its critical threshold `R_c ≈ 1/e ≈ 0.37`, at
which point internal-reflection energy density dominates leakage and a
self-sustaining recurrent loop forms. Mashour et al.'s "long-range
ignition" is the *graph-level* expression of the same scalar transition.
Bridge documents:

- `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`
- `docs/papers/efc/Connecting_Cosmology_Neural_Entropy_and_RLHF_Bridge/`

---

*Curated theoretical reference. Last reviewed: 2026-05-13.*
