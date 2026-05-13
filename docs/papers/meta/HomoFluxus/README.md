# Homo Fluxus

> *Homo Fluxus* is the EFC meta-principle that treats the human (and any
> living system) **not as a static entity but as a dynamic, far-from-
> equilibrium energy-flow process** — a node embedded in, and constituted by,
> gradients of matter, energy, information, and meaning. The same EFC
> formalism that governs galaxy clusters governs cells, brains, societies,
> and AI agents: minimise locally-resolvable entropy production along
> available flow channels while preserving the topology that makes those
> channels possible.

**Originator (within EFC):** Morten Magnusson (Symbiose Research).
**Source publications (in `docs/papers/efc/`):**
- `Homo Fluxus A Thermodynamic Framework/` (v1.0, 2026-04-25, DOI
  [10.6084/m9.figshare.32099389](https://doi.org/10.6084/m9.figshare.32099389))
  — thermodynamic substrate for consciousness, systemic empathy, AI alignment.
- `Homo_Fluxus/Homo_Fluxus_v2.0.pdf` (v2.0, 2026-04-01, DOI
  [10.6084/m9.figshare.31940604](https://doi.org/10.6084/m9.figshare.31940604))
  — civilisation map: Grid → EF → S → D → C; empirical anchor κ ≈ −0.97.

This meta-layer reference places that EFC-internal framework inside the
wider scientific lineage of **non-equilibrium thermodynamics of life** —
Schrödinger, Prigogine, Kauffman, Schneider/Sagan, England — and links it
forward to the cognitive layer (FEP, IIT, GWT, PP, AST) and to the
medicine layer.

---

## 1. The core principle

> A living/cognitive agent is not a *thing* that happens to move; it is a
> *flow pattern* whose persistence requires continued passage of energy
> and entropy. Identity is a temporal invariant of a dissipative
> structure, not a substance.

Formally, letting `J(r,t)` denote energy flux, `ρ_E(r,t)` energy density,
and `S̃(r,t) ∈ [0,1]` normalised local entropy:

```
∂_t ρ_E  +  ∇·J  =  − L            (open-system continuity)
σ(r,t)  =  max( J·∇S̃ , 0 )         (non-negative dissipation)
τ_ref(r) = ρ_E / (σ + ε)           (local reflection time, ε = η⟨|σ|⟩)
R = κ · ⟨τ_ref⟩_E / τ_leak         (interior reflection coefficient)
```

When `R > R_c ≈ 1/e ≈ 0.37` the system has enough self-coupling to model
its own state — i.e. it becomes a *Homo Fluxus* in the strong sense
(self-aware flow). Below `R_c` it is a *flow object*; above, a *flow
subject*. This same coefficient is identified with the onset of
self-modelling in the CEM cognitive paper.

## 2. Five linked operative claims

| # | Claim | Where falsified |
|---|---|---|
| HF1 | Coherence proxies — `Φ̇I` (integrated information rate), `C_phase` (cross-frequency phase coherence), `I_body` (interoceptive–allostatic integration) — load on a single low-dimensional latent factor. | Simultaneous EEG/MEG + autonomic/fMRI failing to recover a stable cross-modal factor. |
| HF2 | Higher coherence-potential agents display stronger **systemic empathy** — weighting extra-boundary entropy changes in their decisions. | Controlled behavioural experiments showing no positive (or negative) association after confound control. |
| HF3 | In coupled-field environments, locally-optimal RL policies externalise entropy; field-aware policies aligned to `∇Φ_coh` reduce that externalisation at equal or lower energetic cost. | Benchmark coupled-RL evaluations failing to reduce externalised entropy under field-aware policies. |
| HF4 | At population scale, *local* structural metrics (degree ratio) predict the functional variability gradient `κ` with `|r| > 0.8`; *global* graph metrics (`λ_2`) fail. | Connectome cohorts showing global metrics matching or exceeding local. |
| HF5 | Targeted modulation of local degree ratio causally shifts `κ` in the direction predicted by HF4. | Pre/post stimulation, lesion, or longitudinal plasticity studies showing no causal effect. |

HF1–HF3 are taken from `Homo Fluxus v1`; HF4–HF5 from v2.0. The
meta-layer adds the bridge claims below.

## 3. Bridge claims to other layers

| Layer | Cross-layer claim | Evidence anchor |
|---|---|---|
| **Cosmos (`efc/`)** | Same `R`–threshold and `Λ`-locked scaling that explain galaxy-cluster bar-instability and KiDS-1000 cosmic-shear fits constrain the same coefficient when applied to brain energy gradients. | `Closing_the_EFC_Consciousness_Bridge`, `CEM-Consciousness-Ego-Mirror` |
| **Cognitive (`cognitive/`)** | `Φ̇I` is operationalised by **IIT** Φ; `C_phase` by **GWT** ignition signatures; `I_body` by **PP** interoceptive inference (Seth 2013); `R` by **FEP** precision allocation. | `cognitive/IIT/`, `cognitive/GWT/`, `cognitive/PP/`, `cognitive/FEP/` |
| **Medicine** | Disease ≡ regime breakdown of `R`; allostatic load (McEwen) ≡ chronic `σ` increase with stagnant `τ_ref`. | Sterzer 2018 psychosis as aberrant precision; Stephan 2016 allostatic self-efficacy. |
| **Society / AI alignment** | Civilisation as a meta-Fluxus: governance, economy, and AI policy are control surfaces on `κ` at population scale; misalignment ≡ externalised entropy. | `Homo Fluxus v2.0` empirical anchor; RLHF-as-thermodynamic-entropy-minimisation paper (Track 3). |

## 4. Wider scientific lineage

Homo Fluxus is the EFC-specific instantiation of a much older claim that
**life is a non-equilibrium thermodynamic phenomenon**:

| Author | Year | Contribution |
|---|---|---|
| Erwin **Schrödinger** | 1944 | *What is Life?* — life as that which "feeds on negative entropy." |
| Ilya **Prigogine** | 1967–1977 | Dissipative structures; far-from-equilibrium order; Nobel 1977. |
| Stuart **Kauffman** | 1993 | *The Origins of Order* — autocatalytic sets at the edge of chaos. |
| Eric **Schneider & Dorion Sagan** | 2005 | *Into the Cool* — life as gradient-reduction (the *MEP* principle). |
| Jeremy **England** | 2013–2022 | Dissipation-driven adaptation (DDA); "physics of becoming". |
| Karl **Friston** | 2006–2023 | Free Energy Principle — life as upper-bound-on-surprise minimisation. (See `cognitive/FEP/`.) |
| Terrence **Deacon** | 2011 | *Incomplete Nature* — teleodynamics: thermodynamic constraint as the origin of intentionality. |
| Michael **Levin** | 2019– | Bioelectric pattern as morphogenetic memory; cognition without neurons. |

The Homo Fluxus paper synthesis (this meta-principle) inherits from all
of these and adds the EFC-specific bridge to cosmological structure.

## 5. Empirical workhorses

- **κ** — functional variability gradient (CamCAN, HCP, UK Biobank
  connectomes).
- **Φ̇I / Φ_proxy** — empirical integrated-information proxy via
  PyPhi-ST or perturbation complexity index (PCI; Casali 2013).
- **C_phase** — cross-frequency coupling, especially theta–gamma in
  EEG/MEG.
- **I_body** — heart-evoked potentials, interoceptive accuracy, gastric
  rhythm coupling.
- **Externalised entropy index** — net entropy export per unit energy
  intake, applicable to organisms, organisations, RL agents.

## 6. Criticisms / open issues

1. **Reduction-vs.-claim debate** — Critics (e.g., Bickhard 2009) note that
   thermodynamic descriptions of life have explanatory limits; symbolic
   structure (genes, language) cannot be reduced to flow patterns alone.
2. **Latent-factor risk** — HF1's "single coherence variable" is a strong
   factorisation claim; if multiple latent dimensions are required, the
   parsimony of Homo Fluxus weakens.
3. **Operationalising `κ` across modalities** — Comparing rotation curves
   (galaxies) to functional variability (brains) requires care that the
   units, normalisation, and noise characteristics genuinely justify the
   same `R`-threshold.
4. **MEP debate** — Maximum Entropy Production has been contested
   (Dewar 2003 vs. Grinstein & Linsker 2007); HF3 is not strictly MEP, but
   inherits some of the controversy.
5. **Causal directionality** — HF4 is correlational; HF5 demands
   intervention studies that are clinically and ethically constrained.

## 7. Key references (chronological)

- Schrödinger E. (1944) *What is Life?* Cambridge UP.
- Prigogine I., Nicolis G. (1977) *Self-Organization in Nonequilibrium
  Systems*. Wiley. ISBN 978-0471024019.
- Maturana H.R., Varela F.J. (1980) *Autopoiesis and Cognition*. Reidel.
  (See also `../Autopoiesis/`.)
- Kauffman S. (1993) *The Origins of Order*. Oxford UP.
  ISBN 978-0195079517.
- Schneider E.D., Sagan D. (2005) *Into the Cool*. Chicago UP.
  ISBN 978-0226739366.
- Deacon T.W. (2011) *Incomplete Nature: How Mind Emerged from Matter*.
  Norton. ISBN 978-0393049916.
- England J.L. (2013) "Statistical physics of self-replication."
  *J Chem Phys* 139:121923. DOI: 10.1063/1.4818538
- Friston K. (2010) "The free-energy principle: a unified brain theory?"
  *Nat Rev Neurosci* 11:127–138. DOI: 10.1038/nrn2787
- Levin M. (2019) "The computational boundary of a 'self': developmental
  bioelectricity drives multicellularity and scale-free cognition."
  *Front Psychol* 10:2688. DOI: 10.3389/fpsyg.2019.02688
- Magnusson M. (2026a) *Homo Fluxus: A Thermodynamic Framework*. Figshare
  preprint 32099389.
- Magnusson M. (2026b) *Homo Fluxus v2.0 — A Civilization Map Through EFC*.
  Figshare preprint 31940604.

---

## EFC bridge — where to read next

- `docs/papers/efc/Homo Fluxus A Thermodynamic Framework/` — v1 paper
- `docs/papers/efc/Homo_Fluxus/` — v2 paper (with κ ≈ −0.97 empirical anchor)
- `docs/papers/efc/CEM-Consciousness-Ego-Mirror/` — `R`-threshold formalism
- `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/` — formal cross-layer bridge
- `docs/papers/efc/Reinforcement_Learning_from_Human_Feedback_as_Thermodynamic_Entropy_Minimisation_A_Formal_Isomorphism_Track_3/` — AI alignment as field-aware policy

---

*Curated theoretical reference. Last reviewed: 2026-05-13.*
