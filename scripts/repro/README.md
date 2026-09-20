# Reproduction kit — the sealed EFC prediction fσ8(z≈0.7) = 0.430

This kit lets a person **outside byOpus** reproduce the sealed
EFC prediction directly from the source code.

## What you reproduce

The sealed prediction:

> fσ8(z ≈ 0.7) = **0.430**

Sealed in `DOI 10.6084/m9.figshare.32013156` (the DESI DR2 full-shape
fσ8 criterion). The prediction rests on the μ channel ("linear growth with
entropy damping"): μ(a) = 1 + (μ_0 − 1)·g(a) with μ_0 = 0.5 in
EFCVariantC, run with canonical parameters (Ω_m = 0.3, H0 = 70,
σ8 = 0.8).

## How to do it

```bash
git clone https://github.com/supertedai/EFC.git
cd EFC
python -m venv .venv && . .venv/bin/activate
pip install numpy scipy
python scripts/repro/sealed_fs8_repro.py
```

Expected result:

```
Sealed value:          fσ8(z≈0.7) = 0.430
Computed:              fσ8(z=0.7) = 0.4301
Deviation:             0.0001 (OK — within 0.5 %)
```

## What the reproduction shows — and does not show

- **Shows:** that the engine returns the sealed value with the declared
  inputs. The seal was made BEFORE this code was public;
  the reproduction confirms the consistency.
- **Does not show:** that the prediction is right against data. That is
  the arbiter's verdict: `efc_inference/arbiter/sealed_fs8.py` compares
  against the actual DESI DR2 measurement once it exists.

## Contact

Questions about the kit or the result: open an issue at
github.com/supertedai/EFC.
