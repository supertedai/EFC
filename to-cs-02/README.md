# TO-CS-02: EFC-C Product Hypothesis Test

Tests whether consciousness is better predicted by the **product** of differentiation (Omega) and causal integration (Kappa) than by either component alone.

## Quick Start

```bash
pip install -r requirements.txt
python run_to_cs_02.py --data-dir /path/to/sedation-restingstate/Sedation-RestingState/
```

## Data

Download `sedation-restingstate.zip` (3.44 GB) from:
https://www.repository.cam.ac.uk/handle/1810/252736

Or use locally available EEGLAB `.set`/`.fdt` files from Chennu et al. 2016.

## Pipeline

| Phase | What | Time |
|-------|------|------|
| 1 | Load & verify 20 subjects x 4 conditions | ~5 min |
| 2 | Compute Omega (PE + SE) at two bands | ~5 min |
| 3 | Compute Kappa (TE, 56 directed pairs) | ~16 min |
| 4 | Dissociation check: corr(Omega, Kappa) | <1 min |
| 5 | Four-way bootstrap comparison | ~10 min |
| 6 | Decision tree scoring | <1 min |

## Key Test

**C = Omega(4-40 Hz) x Kappa** vs **Omega(4-40 Hz)** alone.

If C beats delta-free Omega, it means causal integration captures consciousness-related information NOT in the power spectrum.

## Pre-registered Parameters (locked)

See `TO-CS-02_Appendix_B_Statistics.md` for all locked parameters.
