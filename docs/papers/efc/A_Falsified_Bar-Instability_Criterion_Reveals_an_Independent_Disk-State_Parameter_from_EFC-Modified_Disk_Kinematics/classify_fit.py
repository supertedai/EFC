"""
EFC-BIC Classification Fit
==========================

Drop SAB and not_disk; keep cleanly-labeled SA (no_bar) and SB (bar) galaxies.
For each ζ in [1.0, 1.5, 2.0, 2.5, 3.0]:
  - Compute Π_min in disk window per galaxy (shear proxy, σ_R = Jeans)
  - Predict bar if Π_min < 1.0 (no threshold tuning per directive)
  - Compute confusion matrix, accuracy, precision, recall, F1
  - Compute AUC by treating −Π_min as the score (lower Π = more bar-prone)
  - Compute ζ_max from κ²_eff ≥ 0 constraint per galaxy

Monotonicity test: median Π_min by regime (FLOW > TRANSITION > LATENT?).

Output:
  output/classify_fit.json
  output/classify_fit_summary.png   (Π distribution per class)
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

from efc_bic_pipeline import (
    G_SI, KMS_TO_MS, KPC_TO_M, MSUN_PER_PC2_TO_KG_PER_M2, central_diff,
)
from sparc_loader import load_classification, load_sparc_pilot, parse_sparc_dat
from run_pilot import DAT_PATH, CLS_PATH, OUTDIR

LABELS_PATH = Path("/Users/morpheus/Documents/Claud Code/AGI-Test/data/sparc/sparc_bar_labels.json")
ZETA_GRID = [1.0, 1.5, 2.0, 2.5, 3.0]
PI_THRESHOLD = 1.0


# --------------------------------------------------------------------------
# Per-galaxy compute
# --------------------------------------------------------------------------

def pi_min_disk(g, zeta: float) -> tuple[float, bool]:
    """Π_min in [R_d, 3·R_d] using shear proxy. Returns (Pi_min, kappa2eff_negative)."""
    r = g.r_kpc * KPC_TO_M
    v = g.v_kms * KMS_TO_MS
    sigma_R = g.sigma_R_kms * KMS_TO_MS
    Sigma = g.Sigma_Msun_pc2 * MSUN_PER_PC2_TO_KG_PER_M2
    R_d_m = g.R_d_kpc * KPC_TO_M

    omega = v / r
    nablaS = v * r * central_diff(r, omega)
    dvdr = central_diff(r, v)
    kappa2 = (2.0 * v / r) * (v / r) + (2.0 * v / r) * dvdr
    g_EFC = g.alpha * nablaS
    kappa2_eff = kappa2 + zeta * g_EFC / r

    sgn = np.sign(kappa2_eff)
    kappa_eff = np.sqrt(np.abs(kappa2_eff)) * sgn
    with np.errstate(divide="ignore", invalid="ignore"):
        Pi = sigma_R * kappa_eff / (3.36 * G_SI * Sigma)

    disk = (r >= R_d_m) & (r <= 3.0 * R_d_m)
    if not disk.any():
        return float("nan"), False
    Pi_disk = Pi[disk]
    finite = np.isfinite(Pi_disk)
    if not finite.any():
        return float("nan"), False
    pi_min = float(np.min(Pi_disk[finite]))
    # κ²_eff went negative anywhere in disk?
    k2eff_neg = bool((kappa2_eff[disk][finite] < 0).any())
    return pi_min, k2eff_neg


def zeta_max_physical(g) -> float:
    """
    Find largest ζ such that κ²_eff(r) ≥ 0 everywhere in disk window.
    Returns +inf if g_EFC ≥ 0 (never violated, but then no bar driver).
    Returns ζ where the WORST-CASE radius first hits κ²_eff = 0:
        ζ_max = min over disk r of (κ² · r / |g_EFC|) where g_EFC < 0
    """
    r = g.r_kpc * KPC_TO_M
    v = g.v_kms * KMS_TO_MS
    R_d_m = g.R_d_kpc * KPC_TO_M

    omega = v / r
    nablaS = v * r * central_diff(r, omega)
    dvdr = central_diff(r, v)
    kappa2 = (2.0 * v / r) * (v / r) + (2.0 * v / r) * dvdr
    g_EFC = g.alpha * nablaS

    disk = (r >= R_d_m) & (r <= 3.0 * R_d_m)
    if not disk.any():
        return float("nan")
    # We need κ² + ζ·g_EFC/r ≥ 0
    # If g_EFC < 0:  ζ ≤ κ² · r / |g_EFC|
    # Take the min over disk window
    g_term = g_EFC[disk] / r[disk]
    k2 = kappa2[disk]
    mask_neg = (g_term < 0) & np.isfinite(g_term) & np.isfinite(k2)
    if not mask_neg.any():
        return float("inf")
    z_caps = -k2[mask_neg] / g_term[mask_neg]   # positive, equals κ²·r/|g_EFC|
    return float(np.min(z_caps))


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def confusion(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """y_true and y_pred are 0/1 arrays. 1 = bar, 0 = no_bar."""
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    n = tp + fp + tn + fn
    acc = (tp + tn) / n if n else float("nan")
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if (np.isfinite(prec) and np.isfinite(rec)
                                            and (prec + rec) > 0) else float("nan")
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": n,
            "accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


def auc(y_true: np.ndarray, score: np.ndarray) -> float:
    """
    AUC via Mann-Whitney U. Score should be monotonic with positive class
    likelihood (we use −Π_min: lower Π = more bar-prone → higher score).
    """
    pos = score[y_true == 1]
    neg = score[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # Pairs where pos > neg / 2 if equal
    n_concordant = 0
    n_tied = 0
    for p in pos:
        n_concordant += int((p > neg).sum())
        n_tied += int((p == neg).sum())
    return (n_concordant + 0.5 * n_tied) / (len(pos) * len(neg))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> dict:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    labels = json.load(open(LABELS_PATH))
    cls = load_classification(CLS_PATH)
    raw = parse_sparc_dat(DAT_PATH)

    # Pick galaxies with bar∈{bar, no_bar}, ≥10 RC points, regime in known set
    selected = []
    for name, lbl in labels["labels"].items():
        if lbl["bar_class"] not in ("bar", "no_bar"):
            continue
        if name not in raw or len(raw[name]["R_kpc"]) < 10:
            continue
        if name not in cls or cls[name]["regime"] not in ("FLOW", "TRANSITION", "LATENT"):
            continue
        selected.append(name)
    print(f"Selected (cleanly labeled, ≥10 pts, regime known): N={len(selected)}")

    inputs, infos = load_sparc_pilot(DAT_PATH, CLS_PATH, selected, sigma_mode="sigma_jeans")
    name_to_label = {n: labels["labels"][n]["bar_class"] for n in selected}
    name_to_morph = {n: labels["labels"][n]["morph_raw"] for n in selected}
    name_to_regime = {i.name: i.regime for i in infos}

    # Truth array (1 = bar, 0 = no_bar)
    y_true = np.array([1 if name_to_label[g.name] == "bar" else 0 for g in inputs])

    # Compute ζ_max physical per galaxy
    z_max_per = {g.name: zeta_max_physical(g) for g in inputs}
    finite_zmax = [v for v in z_max_per.values() if np.isfinite(v)]
    z_max_global = float(min(finite_zmax)) if finite_zmax else float("inf")
    print(f"ζ_max physical (worst case across sample, κ²_eff≥0): {z_max_global:.2f}")
    print(f"ζ_max physical p25={np.percentile(finite_zmax, 25):.2f} "
          f"med={np.median(finite_zmax):.2f} "
          f"p75={np.percentile(finite_zmax, 75):.2f}")

    # ζ-grid scan
    fits = []
    pi_per_galaxy = {z: {} for z in ZETA_GRID}
    for z in ZETA_GRID:
        scores, k2neg = [], []
        for g in inputs:
            pi, neg = pi_min_disk(g, z)
            scores.append(pi)
            k2neg.append(neg)
            pi_per_galaxy[z][g.name] = pi
        scores = np.array(scores)
        k2neg = np.array(k2neg)
        finite = np.isfinite(scores)
        if not finite.all():
            print(f"  ζ={z}: {(~finite).sum()} non-finite Π — skipping those")
        # Predict: Π_min < 1 → bar
        y_pred = (scores < PI_THRESHOLD).astype(int)
        # AUC: score = -Π_min (lower Π → more bar)
        score_for_auc = -scores
        cm = confusion(y_true[finite], y_pred[finite])
        a = auc(y_true[finite], score_for_auc[finite])
        n_unphysical = int(k2neg.sum())
        fits.append({
            "zeta": z,
            "n_used": int(finite.sum()),
            "n_unphysical_kappa2eff_negative": n_unphysical,
            "confusion": cm,
            "auc": a,
        })
        print(f"  ζ={z:.1f}  acc={cm['accuracy']:.3f}  prec={cm['precision']:.3f}  "
              f"rec={cm['recall']:.3f}  F1={cm['f1']:.3f}  AUC={a:.3f}  "
              f"unphysical={n_unphysical}/{len(inputs)}")

    # Best fit by accuracy (within physical regime)
    physical = [f for f in fits if f["zeta"] <= z_max_global]
    physical_or_all = physical if physical else fits
    best = max(physical_or_all, key=lambda f: (f["confusion"]["accuracy"] or 0))
    print(f"\nBest physical ζ: {best['zeta']} (acc={best['confusion']['accuracy']:.3f}, "
          f"AUC={best['auc']:.3f})")

    # Per-regime monotonicity at best ζ
    z_best = best["zeta"]
    regime_pi = {"FLOW": [], "TRANSITION": [], "LATENT": []}
    for g in inputs:
        pi = pi_per_galaxy[z_best][g.name]
        if np.isfinite(pi):
            regime_pi[name_to_regime[g.name]].append(pi)
    monotonicity = {}
    for r, vals in regime_pi.items():
        monotonicity[r] = {
            "n": len(vals),
            "median": float(np.median(vals)) if vals else None,
            "min": float(np.min(vals)) if vals else None,
            "max": float(np.max(vals)) if vals else None,
        }
    medians = [monotonicity[r]["median"] for r in ("FLOW", "TRANSITION", "LATENT")]
    is_monotonic = (medians[0] is not None and medians[1] is not None and medians[2] is not None
                    and medians[0] >= medians[1] >= medians[2])

    # Per-galaxy detail at best ζ
    per_galaxy = []
    for g in inputs:
        per_galaxy.append({
            "name": g.name,
            "label": name_to_label[g.name],
            "morph_raw": name_to_morph[g.name],
            "regime": name_to_regime[g.name],
            "alpha": g.alpha,
            "R_d_kpc": g.R_d_kpc,
            "Pi_min_at_best_zeta": pi_per_galaxy[z_best][g.name],
            "predicted_bar_at_best_zeta": bool(np.isfinite(pi_per_galaxy[z_best][g.name])
                                              and pi_per_galaxy[z_best][g.name] < PI_THRESHOLD),
            "zeta_max_physical": z_max_per[g.name],
        })

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax_dist, ax_grid = axes

    # Distribution at best ζ, by label
    pi_bar = np.array([r["Pi_min_at_best_zeta"] for r in per_galaxy
                       if r["label"] == "bar" and np.isfinite(r["Pi_min_at_best_zeta"])])
    pi_nob = np.array([r["Pi_min_at_best_zeta"] for r in per_galaxy
                       if r["label"] == "no_bar" and np.isfinite(r["Pi_min_at_best_zeta"])])
    bins = np.linspace(min(pi_bar.min(), pi_nob.min(), -2),
                       max(pi_bar.max(), pi_nob.max(), 10), 25)
    ax_dist.hist(pi_nob, bins=bins, alpha=0.6, color="steelblue",
                 label=f"no_bar (N={len(pi_nob)})", edgecolor="k")
    ax_dist.hist(pi_bar, bins=bins, alpha=0.6, color="crimson",
                 label=f"bar (N={len(pi_bar)})", edgecolor="k")
    ax_dist.axvline(PI_THRESHOLD, color="k", ls="--", lw=2, label="Π=1")
    ax_dist.set_xlabel(f"Π_min (disk window, ζ={z_best})")
    ax_dist.set_ylabel("count")
    ax_dist.set_title(f"Π_min distribution by label  (best ζ={z_best})")
    ax_dist.legend()
    ax_dist.grid(True, alpha=0.2)

    # ζ-grid metrics
    zs = [f["zeta"] for f in fits]
    accs = [f["confusion"]["accuracy"] for f in fits]
    aucs = [f["auc"] for f in fits]
    f1s = [f["confusion"]["f1"] for f in fits]
    ax_grid.plot(zs, accs, "o-", label="accuracy", color="tab:blue")
    ax_grid.plot(zs, aucs, "s-", label="AUC", color="tab:orange")
    ax_grid.plot(zs, f1s, "^-", label="F1", color="tab:green")
    ax_grid.axvline(z_max_global, color="red", ls="--", lw=1,
                    label=f"ζ_max physical ≈ {z_max_global:.2f}")
    ax_grid.axvline(z_best, color="black", ls=":", lw=1,
                    label=f"best ζ = {z_best}")
    ax_grid.set_xlabel("ζ")
    ax_grid.set_ylabel("metric")
    ax_grid.set_ylim(0, 1.05)
    ax_grid.set_title("Classification metrics vs ζ")
    ax_grid.legend(fontsize=9)
    ax_grid.grid(True, alpha=0.2)

    fig.suptitle(f"EFC-BIC Classification Fit  N={len(inputs)}  "
                 f"({(y_true == 1).sum()} bars, {(y_true == 0).sum()} no_bars)")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = OUTDIR / "classify_fit.png"
    fig.savefig(out_png, dpi=140)
    plt.close(fig)

    out = {
        "version": "classify_fit_v0.1",
        "n_galaxies": len(inputs),
        "n_bar": int((y_true == 1).sum()),
        "n_no_bar": int((y_true == 0).sum()),
        "Pi_threshold": PI_THRESHOLD,
        "zeta_grid": ZETA_GRID,
        "zeta_max_physical_global": z_max_global,
        "zeta_max_physical_per_galaxy": z_max_per,
        "best_physical_zeta": best["zeta"],
        "fits": fits,
        "monotonicity_at_best_zeta": monotonicity,
        "monotonicity_holds": is_monotonic,
        "per_galaxy": per_galaxy,
    }
    out_path = OUTDIR / "classify_fit.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)

    # Console summary
    print(f"\n=== MONOTONICITY (median Π_min by regime, ζ={z_best}) ===")
    for r in ("FLOW", "TRANSITION", "LATENT"):
        d = monotonicity[r]
        print(f"  {r:11s}  N={d['n']:2d}  median={d['median']:.2f}  "
              f"range=[{d['min']:.2f}, {d['max']:.2f}]")
    print(f"  Monotonic FLOW > TRANSITION > LATENT: {is_monotonic}")

    print(f"\n=== CONFUSION MATRIX at best ζ={z_best} ===")
    cm = best["confusion"]
    print(f"                pred_no_bar  pred_bar")
    print(f"  true_no_bar   {cm['tn']:11d}  {cm['fp']:8d}")
    print(f"  true_bar      {cm['fn']:11d}  {cm['tp']:8d}")
    print(f"  accuracy = {cm['accuracy']:.3f}")
    print(f"  precision = {cm['precision']:.3f}  recall = {cm['recall']:.3f}  F1 = {cm['f1']:.3f}")
    print(f"  AUC = {best['auc']:.3f}")

    print(f"\n=== MISCLASSIFIED GALAXIES at best ζ={z_best} ===")
    for r in per_galaxy:
        is_truth_bar = r["label"] == "bar"
        is_pred_bar = r["predicted_bar_at_best_zeta"]
        if is_truth_bar != is_pred_bar:
            err = "FN" if is_truth_bar else "FP"
            print(f"  [{err}] {r['name']:14s} {r['regime']:11s} "
                  f"morph={r['morph_raw']:8s} α={r['alpha']:.2f} "
                  f"R_d={r['R_d_kpc']:.2f} Π_min={r['Pi_min_at_best_zeta']:.2f}")

    print(f"\nWrote: {out_path}")
    print(f"Wrote: {out_png}")
    return out


if __name__ == "__main__":
    main()
