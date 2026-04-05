# Reinforcement Learning from Human Feedback as Thermodynamic Entropy Minimisation: A Formal Isomorphism and Testable Predictions

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31940535](https://doi.org/10.6084/m9.figshare.31940535)  
**Date:** March 31, 2026 (v1.0)

## Summary

RLHF is formally isomorphic to statistical-mechanical entropy minimisation. The mapping is algebraically exact: R -> -E, beta_KL -> T, policy -> Boltzmann distribution, RLHF objective -> negative Helmholtz free energy. Three falsifiable predictions derived.

## Key Isomorphism (Table 1)

| RLHF | Statistical Mechanics |
|------|----------------------|
| Policy pi(a|s) | Boltzmann distribution |
| Reward R(s,a) | Negative energy -E |
| KL penalty beta_KL | Temperature T |
| Reference policy | Prior / vacuum state |
| RLHF objective J | -Helmholtz free energy -F |
| Grokking | First-order phase transition |
| Alignment | Low-entropy policy attractor |
| Jailbreaking | Thermal fluctuation over barrier |

## Three Falsifiable Predictions

1. **P1**: Optimal beta_KL scales as H_task^{-1/2} (task-matched temperature)
2. **P2**: Grokking latent period scales as (H_mem - H_gen)/T_eff (latent heat)
3. **P3**: Universal A*C bound from free-energy constraint (alignment-capability trade-off)

## File Structure

```
├── README.md, index.json, schema.json, metadata.json
├── rlhf_thermodynamics.jsonld, citations.bib
├── src/rlhf_thermodynamics.py    # Python implementation
├── data/isomorphism.json         # Complete mapping table and predictions
└── examples/demo_rlhf_thermo.py  # Executable demonstration
```
