"""
Π_EFC as Disk Evolutionary State Parameter — full SPARC analysis
=================================================================

Pivot from bar prediction (falsified) to disk-state characterization.

For all SPARC galaxies with regime classification + ≥10 RC points:
  Π_min(disk, ζ=1, shear)   ← v0.1 shear pipeline output
  log Σ_disk                 ← median Σ in [R_d, 3·R_d] (M_sun/pc²)
  f_gas                      ← V_gas² / (V_gas² + V_disk² + V_bulge²)
  disk_dominance             ← V_disk² / V_obs²
  V_max                      ← max V_obs (km/s)

Reports:
  • Pairwise Spearman ρ + p-value
  • Linear regression Π = a + b·log Σ + c·f_gas + d·disk_dom (OLS by hand)
  • Standardized coefficients (effect size)
  • AUC for binary predictions: gas-rich (top tertile), high-Σ (top tertile)
  • Per-regime diagnostics

Outputs:
  output/disk_state.json
  output/disk_state.png      (4-panel scatter + regression)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from sparc_loader import load_classification, load_sparc_pilot, parse_sparc_dat
from run_pilot import DAT_PATH, CLS_PATH, OUTDIR
from classify_fit import pi_min_disk, auc, confusion

ZETA = 1.0


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def spearman(a: np.ndarray, b: np.ndarray) -> tuple[float, float, int]:
    """Spearman ρ + two-sided t-test p-value approximation."""
    a, b = np.asarray(a), np.asarray(b)
    m = np.isfinite(a) & np.isfinite(b)
    n = int(m.sum())
    if n < 5:
        return float("nan"), float("nan"), n
    ra = np.argsort(np.argsort(a[m])).astype(float)
    rb = np.argsort(np.argsort(b[m])).astype(float)
    cov = np.mean((ra - ra.mean()) * (rb - rb.mean()))
    sa = np.sqrt(np.mean((ra - ra.mean()) ** 2))
    sb = np.sqrt(np.mean((rb - rb.mean()) ** 2))
    rho = cov / (sa * sb)
    # t-stat under null
    t = rho * np.sqrt((n - 2) / max(1 - rho ** 2, 1e-10))
    # Two-sided p (approximate via Student-t)
    from math import erf, sqrt
    z = abs(t) / sqrt(2)
    p_norm = 1 - erf(z)   # crude — fine for ρ rough screening
    return float(rho), float(p_norm), n


def ols_regression(X: np.ndarray, y: np.ndarray) -> dict:
    """OLS via normal equations. X is (n, p), y is (n,). Returns coefs + R², standardized betas."""
    mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    Xm, ym = X[mask], y[mask]
    # Add intercept
    Xi = np.hstack([np.ones((Xm.shape[0], 1)), Xm])
    beta, *_ = np.linalg.lstsq(Xi, ym, rcond=None)
    y_hat = Xi @ beta
    ss_res = np.sum((ym - y_hat) ** 2)
    ss_tot = np.sum((ym - np.mean(ym)) ** 2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    # Standardized coefs (for non-intercept terms)
    sd_X = Xm.std(axis=0, ddof=1)
    sd_y = ym.std(ddof=1)
    std_betas = beta[1:] * sd_X / sd_y
    return {
        "intercept": float(beta[0]),
        "coefs":     [float(b) for b in beta[1:]],
        "std_betas": [float(b) for b in std_betas],
        "r_squared": float(r_sq),
        "n_used":    int(mask.sum()),
    }


# --------------------------------------------------------------------------
# Per-galaxy feature extraction
# --------------------------------------------------------------------------

def galaxy_features(g, raw_g) -> dict:
    """Extract Π_min(disk) + structural features for one galaxy."""
    R_d = g.R_d_kpc
    r_kpc = g.r_kpc
    disk = (r_kpc >= R_d) & (r_kpc <= 3.0 * R_d)
    if not disk.any():
        return None
    # Velocity components (from SPARC .dat)
    V_obs = raw_g["V_obs"][disk]
    V_disk = raw_g["V_disk"][disk]
    V_gas = raw_g["V_gas"][disk]
    V_bul = raw_g["V_bulge"][disk]
    if (V_obs <= 0).all():
        return None
    # Surface density
    Sigma = g.Sigma_Msun_pc2[disk]
    if (Sigma <= 0).all():
        return None

    # Π_min via shear pipeline
    pi_min, _ = pi_min_disk(g, zeta=ZETA)
    if not np.isfinite(pi_min):
        return None

    # Disk dominance: median V_disk² / V_obs²
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.where(V_obs > 0, V_disk ** 2 / V_obs ** 2, np.nan)
    disk_dom = float(np.nanmedian(dd))

    # Gas fraction proxy: V_gas² / (V_gas² + V_disk² + V_bulge²)
    V_bar2 = V_disk ** 2 + V_bul ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        fg = np.where((V_bar2 + V_gas ** 2) > 0,
                       V_gas ** 2 / (V_bar2 + V_gas ** 2), np.nan)
    f_gas = float(np.nanmedian(fg))

    # Σ scale: log10 of median Σ in disk
    log_Sigma = float(np.log10(max(np.median(Sigma), 1e-3)))

    # V_max
    V_max = float(np.max(raw_g["V_obs"]))

    return {
        "Pi_min":     pi_min,
        "log_Sigma":  log_Sigma,
        "f_gas":      f_gas,
        "disk_dom":   disk_dom,
        "V_max":      V_max,
        "R_d_kpc":    R_d,
        "alpha":      g.alpha,
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> dict:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw = parse_sparc_dat(DAT_PATH)
    cls = load_classification(CLS_PATH)

    selected = [n for n in sorted(raw.keys())
                if len(raw[n]["R_kpc"]) >= 10
                and n in cls and cls[n]["regime"] in ("FLOW", "TRANSITION", "LATENT")]
    print(f"Loading {len(selected)} galaxies...")
    inputs, infos = load_sparc_pilot(DAT_PATH, CLS_PATH, selected, sigma_mode="sigma_jeans")
    regime_by = {i.name: i.regime for i in infos}

    rows = []
    for g in inputs:
        f = galaxy_features(g, raw[g.name])
        if f is None:
            continue
        f["name"] = g.name
        f["regime"] = regime_by[g.name]
        rows.append(f)
    print(f"N usable: {len(rows)}")

    Pi   = np.array([r["Pi_min"]    for r in rows])
    logS = np.array([r["log_Sigma"] for r in rows])
    fg   = np.array([r["f_gas"]     for r in rows])
    dd   = np.array([r["disk_dom"]  for r in rows])
    vm   = np.array([r["V_max"]     for r in rows])

    # Pairwise Spearman
    pairs = {
        "log_Sigma":     logS,
        "f_gas":         fg,
        "disk_dominance": dd,
        "V_max":         vm,
    }
    pairwise = {}
    for name, x in pairs.items():
        rho, p, n = spearman(Pi, x)
        pairwise[name] = {"spearman_rho": rho, "approx_p": p, "n": n}

    # Multivariate OLS: log10(Π) ~ log Σ + f_gas + disk_dom
    # Use log Π since Π spans orders of magnitude
    logPi = np.log10(np.maximum(Pi, 1e-3))
    X = np.column_stack([logS, fg, dd])
    feature_names = ["log_Sigma", "f_gas", "disk_dom"]
    ols = ols_regression(X, logPi)
    ols["features"] = feature_names

    # AUCs for binary predictions
    # 1. Predict "gas-rich" (top tertile of f_gas) using -Π_min as score (high Π → gas-rich)
    p33, p67 = np.percentile(fg, [33, 67])
    y_gasrich = (fg >= p67).astype(int)
    auc_gasrich = auc(y_gasrich, Pi)   # high Π → bigger score → gas-rich

    # 2. Predict "low Σ" (bottom tertile) using Π
    p33_S, p67_S = np.percentile(logS, [33, 67])
    y_lowS = (logS <= p33_S).astype(int)
    auc_lowS = auc(y_lowS, Pi)

    # 3. Predict "disk-faint" (low disk_dom)
    p33_D = np.percentile(dd, 33)
    y_lowD = (dd <= p33_D).astype(int)
    auc_lowD = auc(y_lowD, Pi)

    # Per-regime stats
    regime_stats = {}
    for reg in ("FLOW", "TRANSITION", "LATENT"):
        sub = [r for r in rows if r["regime"] == reg]
        if not sub:
            continue
        regime_stats[reg] = {
            "n": len(sub),
            "median_Pi": float(np.median([r["Pi_min"] for r in sub])),
            "median_log_Sigma": float(np.median([r["log_Sigma"] for r in sub])),
            "median_f_gas": float(np.median([r["f_gas"] for r in sub])),
            "median_disk_dom": float(np.median([r["disk_dom"] for r in sub])),
        }

    out = {
        "version": "disk_state_v0.1",
        "n_galaxies": len(rows),
        "zeta": ZETA,
        "proxy_mode": "shear",
        "sigma_mode": "sigma_jeans",
        "pairwise_spearman": pairwise,
        "multivariate_ols_log10_Pi": ols,
        "AUC_predictions": {
            "gas_rich_top_tertile":     auc_gasrich,
            "low_surfdens_bot_tertile": auc_lowS,
            "low_diskdom_bot_tertile":  auc_lowD,
        },
        "by_regime": regime_stats,
        "per_galaxy": rows,
    }
    out_path = OUTDIR / "disk_state.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)

    # ---- Plot ----
    REGIME_COLOR = {"FLOW": "tab:blue", "TRANSITION": "tab:orange", "LATENT": "tab:red"}
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    ax_S, ax_g, ax_d, ax_corr = axes.flatten()

    def scatter_with_fit(ax, x, y, x_label, y_label="log10(Π_min)"):
        for reg in ("FLOW", "TRANSITION", "LATENT"):
            mask = np.array([r["regime"] == reg for r in rows])
            if not mask.any():
                continue
            ax.scatter(x[mask], np.log10(np.maximum(y, 1e-3))[mask],
                       color=REGIME_COLOR[reg], alpha=0.65,
                       label=f"{reg} (N={mask.sum()})", s=35, edgecolor="k", lw=0.4)
        # Linear fit on all
        m = np.isfinite(x) & np.isfinite(y) & (y > 0)
        if m.sum() >= 5:
            xx = x[m]
            yy = np.log10(y[m])
            a, b = np.polyfit(xx, yy, 1)
            xline = np.linspace(xx.min(), xx.max(), 50)
            ax.plot(xline, a * xline + b, "k--", lw=2, label=f"slope={a:+.2f}")
        rho, p, _ = spearman(x, y)
        ax.set_title(f"{y_label} vs {x_label}\nSpearman ρ = {rho:+.3f}")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

    scatter_with_fit(ax_S, logS, Pi, "log10 Σ_disk [M_sun/pc²]")
    scatter_with_fit(ax_g, fg,   Pi, "f_gas (V_gas² / V_baryon²)")
    scatter_with_fit(ax_d, dd,   Pi, "V_disk² / V_obs² (disk dominance)")

    # Correlation summary as text in 4th panel
    ax_corr.axis("off")
    txt = "Π_EFC vs disk-state observables (N={})\n\n".format(len(rows))
    txt += "Spearman correlations:\n"
    for name, d in pairwise.items():
        txt += f"  {name:18s}  ρ = {d['spearman_rho']:+.3f}   approx_p = {d['approx_p']:.3g}\n"
    txt += "\nMultivariate OLS  log10(Π) = β₀ + β·X:\n"
    txt += f"  β₀ (intercept) = {ols['intercept']:+.3f}\n"
    for fn, b, sb in zip(ols["features"], ols["coefs"], ols["std_betas"]):
        txt += f"  β({fn:10s}) = {b:+.3f}   std-β = {sb:+.3f}\n"
    txt += f"  R² = {ols['r_squared']:.3f}   N_used = {ols['n_used']}\n"
    txt += "\nAUC (binary, score = Π_min):\n"
    for k, v in out["AUC_predictions"].items():
        txt += f"  {k:30s}  AUC = {v:.3f}\n"
    txt += "\nPer-regime medians:\n"
    for reg, s in regime_stats.items():
        txt += (f"  {reg:11s} N={s['n']:3d}  Π={s['median_Pi']:.2f}  "
                f"log Σ={s['median_log_Sigma']:+.2f}  f_gas={s['median_f_gas']:.2f}  "
                f"disk_dom={s['median_disk_dom']:.2f}\n")
    ax_corr.text(0.02, 0.98, txt, family="monospace", fontsize=9,
                 ha="left", va="top", transform=ax_corr.transAxes)

    fig.suptitle(f"Π_EFC as disk evolutionary state parameter — SPARC N={len(rows)}, "
                 f"shear proxy, ζ={ZETA}, σ_R=Jeans", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = OUTDIR / "disk_state.png"
    fig.savefig(out_png, dpi=140)
    plt.close(fig)

    # ---- Console ----
    print()
    print("=" * 80)
    print(f"DISK-STATE ANALYSIS  N={len(rows)}  ζ={ZETA}  σ_R=Jeans  proxy=shear")
    print("=" * 80)
    print(f"\n--- Pairwise Spearman (Π_min vs feature) ---")
    for name, d in pairwise.items():
        print(f"  {name:18s}  ρ = {d['spearman_rho']:+.3f}   approx_p = {d['approx_p']:.3g}")
    print(f"\n--- Multivariate OLS  log10(Π) = β₀ + β·X ---")
    print(f"  intercept = {ols['intercept']:+.3f}")
    for fn, b, sb in zip(ols["features"], ols["coefs"], ols["std_betas"]):
        print(f"  β({fn:10s}) = {b:+.3f}   std-β = {sb:+.3f}")
    print(f"  R² = {ols['r_squared']:.3f}   N_used = {ols['n_used']}")
    print(f"\n--- AUC (binary predictions, score = Π_min) ---")
    for k, v in out["AUC_predictions"].items():
        print(f"  {k:30s}  AUC = {v:.3f}")
    print(f"\n--- Per-regime medians ---")
    for reg, s in regime_stats.items():
        print(f"  {reg:11s} N={s['n']:3d}  Π={s['median_Pi']:.2f}  "
              f"log Σ={s['median_log_Sigma']:+.2f}  f_gas={s['median_f_gas']:.2f}  "
              f"disk_dom={s['median_disk_dom']:.2f}")
    print(f"\nWrote: {out_path}")
    print(f"Wrote: {out_png}")
    return out


if __name__ == "__main__":
    main()
