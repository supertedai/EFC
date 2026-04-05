# HCP Bridge B1* Validation Pipeline

**Goal:** Test whether the EFC prediction η = C/(1 + λ₂·τ_c) holds on real
Human Connectome Project data, with C = 4.4 fixed from galactic dynamics.

## Quick Start

```bash
# 1. Download HCP data (see below)
# 2. Run the pipeline
python run_hcp_pipeline.py --hcp-dir /path/to/HCP --n-subjects 50

# 3. Run model comparison on the output
python ../../scripts/efc_model_comparison.py --data output/lambda2.npy output/eta.npy output/results.json
```

## Data Requirements

### Option A: Full HCP (recommended, most rigorous)

Download from [ConnectomeDB](https://db.humanconnectome.org/):

1. **Structural preprocessed** (for connectome):
   - `{subject}/T1w/Diffusion/` — diffusion data
   - `{subject}/MNINonLinear/fsaverage_LR32k/` — surface parcellation

2. **Resting-state fMRI** (for entropy):
   - `{subject}/MNINonLinear/Results/rfMRI_REST1_LR/`
   - File: `rfMRI_REST1_LR_Atlas_MSMAll_hp2000_clean.dtseries.nii`

3. **Atlas**: HCP MMP1.0 (Glasser et al. 2016), 360 cortical parcels

Minimum: 30 subjects (for statistical power per Monte Carlo analysis).
Recommended: 50+ subjects.

### Option B: Pre-computed connectomes (faster)

Use published HCP group-average connectomes from:
- Yeh et al. (2018) HCP-842 connectome atlas
- Available at: https://brain.labsolver.org/hcp_template.html

### Option C: Minimal test with public data

Use the UCLA Consortium for Neuropsychiatric Phenomics dataset:
- OpenNeuro: ds000030
- Includes structural + resting-state fMRI
- Smaller sample but freely accessible without registration

## Pipeline Steps

```
HCP raw data
    │
    ├─ Step 1: Build structural connectome W (360×360)
    │           probabilistic tractography → streamline density
    │
    ├─ Step 2: Compute λ₂ (Fiedler eigenvalue)
    │           L_sym = I - D^{-1/2} W D^{-1/2}
    │
    ├─ Step 3: Extract BOLD time series per parcel
    │           ICA-FIX denoised, parcellated to MMP1.0
    │
    ├─ Step 4: Compute MSE at scales 4-6 per parcel
    │
    ├─ Step 5: Classify hub (top 10%) vs peripheral (bottom 30%)
    │
    ├─ Step 6: Compute κ = <S_hub> / <S_periph>
    │
    └─ Step 7: Model comparison (EFC vs power-law vs linear)
```

## Output

```
output/
├── lambda2.npy          # λ₂ per subject
├── eta.npy              # κ per subject
├── subjects.json        # subject metadata
├── per_subject/         # individual results
│   ├── 100206.json
│   └── ...
└── results.json         # model comparison results
```

## Decision Criteria

| Outcome | Interpretation |
|---------|---------------|
| EFC wins BIC, τ_c ≈ 3-4, r > 0.4 | Strong: C=4.4 from galaxies predicts brains |
| EFC ≈ Linear | Structure correct, not uniquely EFC |
| Power-law wins | Generic network scaling, B1* fails |
| r < 0.2 | Hypothesis falsified |
