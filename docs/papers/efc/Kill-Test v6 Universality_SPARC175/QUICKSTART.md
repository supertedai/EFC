# QUICKSTART — Kill-Test v6 Universality (SPARC 175)

**Regime:** L3 (galactic rotation curves, flow-dominated, z ~ 0)

## What this package answers in one line

> Does the Kill-Test v6 EFC advantage on 5 SPARC galaxies (probe-2) hold
> when the same methodology is applied to all 175? **Yes — 60.2 % EFC win rate.**

## What you need

- Python ≥ 3.10
- `numpy`, `scipy`
- ~2 minutes of single-core CPU

Install deps:
```bash
pip install numpy scipy
```

## Reproduce the full result

From the repository root:

```bash
python "docs/papers/efc/Kill-Test v6 Universality_SPARC175/src/sparc175_killtest_universality.py" \
    "docs/papers/efc/Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling" \
    "docs/papers/efc/Kill-Test v6 Universality_SPARC175/data"
```

This reads `sparc_rotation_curves.dat` (3391 rows, 175 galaxies) from
the parent SPARC 175 paper, fits EFC and NFW to each galaxy using
`scipy.differential_evolution` (seed = 42), and writes
`sparc175_killtest_results.json` alongside the existing summary files.

## Look at the headline numbers without running code

Open `data/summary.json`:

```json
{
  "efc_win_rate_percent": 60.2,
  "lcdm_win_rate_percent": 12.9,
  "tie_rate_percent": 26.9,
  "median_delta_aic": 6.213,
  "median_chi2_red_efc": 0.4402,
  "median_chi2_red_nfw": 1.6866,
  "universality": {
    "cherry_picking_refuted": true,
    "universality_verdict": "CONFIRMED"
  }
}
```

## Look at the top 10 EFC / LCDM wins

Open `data/top_galaxies.json`:

```json
{
  "top_10_efc_wins": [
    {"name": "UGC11914", "delta_aic": 4218.1, "regime": "FLOW", ...},
    {"name": "UGC05253", "delta_aic": 3965.3, "regime": "FLOW", ...},
    ...
  ],
  "top_10_lcdm_wins": [
    {"name": "UGC02953", "delta_aic": -4305.6, "regime": "LATENT", ...},
    {"name": "NGC5055",  "delta_aic": -2921.5, "regime": "LATENT", ...},
    ...
  ]
}
```

## Sign convention

**Positive ΔAIC ⇒ EFC wins.** This matches Kill-Test v6 probe-2 where
DDO 154 gives ΔAIC = +35.4. Under this work's single-component fit
DDO 154 gives **ΔAIC = +125.2**, confirming the sign convention.

## What each file in `data/` is

| File | Contents |
|---|---|
| `sparc175_killtest_results.json` | 171 full per-galaxy fits (EFC + NFW params, χ², AIC, verdict) + 4 failed entries + aggregated statistics |
| `summary.json` | Headline numbers only — safe for quick inspection |
| `verdict_distribution.json` | Verdict and regime counts |
| `top_galaxies.json` | Top-10 EFC and LCDM wins + probe-2 anchor cross-check |

## Reading the full results file

```python
import json
with open("data/sparc175_killtest_results.json") as f:
    d = json.load(f)

# Top EFC win
top = max(d["per_galaxy_results"], key=lambda r: r["comparison"]["delta_aic"])
print(top["name"], top["comparison"]["delta_aic"], top["comparison"]["regime"])

# All LATENT galaxies
latent = [r["name"] for r in d["per_galaxy_results"]
          if r["comparison"]["regime"] == "LATENT"]
print(f"{len(latent)} LATENT galaxies:", latent)

# DDO 154 cross-check
ddo = next(r for r in d["per_galaxy_results"] if r["name"] == "DDO154")
print(f"DDO 154: ΔAIC = {ddo['comparison']['delta_aic']}, "
      f"verdict = {ddo['comparison']['verdict']}")
```

## What the verdict labels mean

| ΔAIC range | Verdict | Interpretation |
|---|---|---|
| ΔAIC > +10 | **EFC_decisive** | Strong EFC preference |
| +2 < ΔAIC ≤ +10 | EFC | Weak EFC preference |
| −2 ≤ ΔAIC ≤ +2 | tied | Indistinguishable |
| −10 ≤ ΔAIC < −2 | LCDM | Weak NFW preference |
| ΔAIC < −10 | LCDM_decisive | Strong NFW preference |

## Where to go next

- **Full write-up:** `README.md`
- **Parent Kill-Test v6:** `../EFC_vs_LCDM_Kill_Test_v6_final/`
- **SPARC 175 data paper:** `../Comprehensive-analysis-of-175-SPARC-galaxies-.../`
