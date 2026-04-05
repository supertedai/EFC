# Local Degree Heterogeneity Predicts Functional Variability Gradients in the Human Connectome

**Morten Magnusson** — Symbiose Research, Sandnes, Norway

**DOI:** [10.6084/m9.figshare.31940370](https://doi.org/10.6084/m9.figshare.31940370)

## Summary

Hub regions exhibit systematically higher functional variability than peripheral regions in the human connectome. We quantify this as the centrifugal entropy score κ and show that:

- **κ > 1** across 5/6 parcellation atlases (68–400 regions)
- **κ = 2.20 ± 0.15** at the individual-subject level (8 DSI connectomes)
- **Degree ratio** predicts κ with r = −0.97 (p < 0.001, 94% variance explained)
- **Fiedler eigenvalue** (global connectivity) is unrelated to κ (r = 0.16, p = 0.70)

The gradient is robust to parcellation resolution (CV = 1.7%) and threshold choice (all 30 combinations tested yield κ > 1).

## Key Finding

> Functional variability gradients in the brain are governed by local degree heterogeneity, not global algebraic connectivity.

## Files

| File | Description |
|------|-------------|
| `article.md` | Complete manuscript |
| `index.json` | Machine-readable metadata |
| `CITATION.cff` | Citation metadata |
| `cover_letter.md` | Journal submission cover letter |

## Analysis Code

All scripts are in the repository root:

| Script | Purpose |
|--------|---------|
| `scripts/efc_c_kappa_analysis.py` | κ computation pipeline |
| `scripts/efc_model_comparison.py` | AIC/BIC model comparison |
| `pipelines/efc/hcp_bridge_b1/run_feature_test.py` | Network feature analysis |
| `pipelines/efc/hcp_bridge_b1/run_sensitivity.py` | Threshold sensitivity |
| `pipelines/efc/hcp_bridge_b1/run_real_hcp_test.py` | HCP group-average test |
| `pipelines/efc/hcp_bridge_b1/run_multiscale_test.py` | Multi-scale analysis |

## Data Sources

- **HCP group-average:** [ENIGMA Toolbox](https://github.com/MICA-MNI/ENIGMA)
- **Individual DSI connectomes:** [BCTpy](https://github.com/aestrivex/bctpy)

## License

CC-BY 4.0
