"""
EFC-BIC v0.2 — Resonance-aware bar instability model
=====================================================

Lifts the criterion from local Toomre-Q-style (v0.1, falsified) to a global
m=2 resonance test:

For each candidate r_CR/R_d ∈ [1, 4]:
   Ω_p   = Ω(r_CR)              (pattern speed implied by trial corotation)
   r_ILR = solve Ω(r) − κ_eff(r)/2 = Ω_p
   X     = κ²_eff(r_CR) · r_CR / (2π · G · Σ(r_CR) · m)     [m=2]
   A(X)  = Gaussian window peaked at X ≈ 1.5 (swing-amplification proxy)
   Q_ILR = σ_R(r_ILR) · κ_eff(r_ILR) / (3.36 G Σ(r_ILR))    (damping)
   score = A(X) / max(Q_ILR, ε)

Bar prediction: max over r_CR-grid of score, threshold by AUC.

EFC enters via κ²_eff = κ² + ζ · g_EFC / r  with g_EFC = α · v · r · dΩ/dr
(shear proxy from v0.1.1). Same σ_R = √(πGΣR_d) from sparc_loader.

Per Mortens directives:
  • A(X) window peaked ~ X=1.5 (else thin disks dominate)
  • ILR-absent → small Q_ILR (no damping → bar-favorable)
  • r_CR/R_d grid (not raw Ω_p) — numerically stable
  • Σ, κ_eff evaluated LOCALLY at r_CR and r_ILR
  • σ_R unchanged
  • Log: r_CR, X, A(X), r_ILR (or absent), Q_ILR, score
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
from classify_fit import LABELS_PATH, confusion, auc

ZETA_GRID = [0.0, 0.5, 1.0, 1.5]   # within physical regime found in v0.1
R_CR_OVER_RD_GRID = np.linspace(1.0, 4.0, 25)   # 25 trial corotation positions
M_MODE = 2                                       # bar mode
X_PEAK = 1.5                                     # swing-amp peak
X_SIGMA = 0.7                                    # window width
Q_FLOOR = 0.01                                   # floor for Q_ILR (avoid div-by-0)


# --------------------------------------------------------------------------
# Numerics
# --------------------------------------------------------------------------

def find_first_crossing(r: np.ndarray, f: np.ndarray) -> float | None:
    """Find smallest r where f(r) = 0, via linear interpolation."""
    finite = np.isfinite(f)
    if finite.sum() < 2:
        return None
    fi = f[finite]
    ri = r[finite]
    signs = np.sign(fi)
    # Treat exact zero as crossing
    for i in range(len(fi) - 1):
        s1, s2 = signs[i], signs[i + 1]
        if s1 == 0:
            return float(ri[i])
        if s1 != s2 and s2 != 0:
            # Linear interp
            f1, f2 = fi[i], fi[i + 1]
            r1, r2 = ri[i], ri[i + 1]
            return float(r1 + (r2 - r1) * (-f1) / (f2 - f1))
    if signs[-1] == 0:
        return float(ri[-1])
    return None


def A_window(X: float, peak: float = X_PEAK, sigma: float = X_SIGMA) -> float:
    """Gaussian window peaked at X≈peak. Penalises both X<<1 (no amp) and X>>2 (damped)."""
    return float(np.exp(-((X - peak) ** 2) / (2 * sigma ** 2)))


# --------------------------------------------------------------------------
# Per-galaxy state
# --------------------------------------------------------------------------

def galaxy_state(g, zeta: float) -> dict:
    """Compute Ω, κ_eff, Σ, σ_R arrays in SI for one galaxy."""
    r = g.r_kpc * KPC_TO_M
    v = g.v_kms * KMS_TO_MS
    sigma_R = g.sigma_R_kms * KMS_TO_MS
    Sigma = g.Sigma_Msun_pc2 * MSUN_PER_PC2_TO_KG_PER_M2
    R_d = g.R_d_kpc * KPC_TO_M

    omega = v / r                                          # 1/s
    nablaS = v * r * central_diff(r, omega)                # m/s² (shear-mode)
    dvdr = central_diff(r, v)
    kappa2 = (2.0 * v / r) * (v / r) + (2.0 * v / r) * dvdr
    g_EFC = g.alpha * nablaS
    kappa2_eff = kappa2 + zeta * g_EFC / r

    return {
        "r": r, "v": v, "omega": omega,
        "kappa2": kappa2, "kappa2_eff": kappa2_eff,
        "Sigma": Sigma, "sigma_R": sigma_R, "R_d": R_d,
    }


def evaluate_at(state: dict, r_target: float, kappa_eff_only: bool = False):
    """Linear-interpolate Σ, κ_eff, σ_R at r_target. Returns dict or None."""
    r = state["r"]
    if r_target < r.min() or r_target > r.max():
        return None
    # κ_eff = sign(κ²_eff)·sqrt(|κ²_eff|)
    k2eff = state["kappa2_eff"]
    if not np.isfinite(k2eff).any():
        return None
    sgn = np.sign(k2eff)
    k_eff = np.sqrt(np.abs(k2eff)) * sgn
    finite = np.isfinite(k_eff) & np.isfinite(state["Sigma"]) & np.isfinite(state["sigma_R"])
    if finite.sum() < 2:
        return None
    rf = r[finite]
    if r_target < rf.min() or r_target > rf.max():
        return None
    out = {
        "kappa_eff": float(np.interp(r_target, rf, k_eff[finite])),
        "Sigma":     float(np.interp(r_target, rf, state["Sigma"][finite])),
        "sigma_R":   float(np.interp(r_target, rf, state["sigma_R"][finite])),
    }
    return out


# --------------------------------------------------------------------------
# Bar score for one (galaxy, ζ, r_CR_target) triple
# --------------------------------------------------------------------------

def bar_score_at(g, zeta: float, r_CR_over_Rd: float) -> dict | None:
    """Compute one bar-score record at a given trial r_CR/R_d."""
    s = galaxy_state(g, zeta)
    R_d = s["R_d"]
    r_CR = r_CR_over_Rd * R_d

    # Need Ω(r_CR) — use raw Ω data (always positive, monotonic decreasing typically)
    if r_CR < s["r"].min() or r_CR > s["r"].max():
        return None
    omega_p = float(np.interp(r_CR, s["r"], s["omega"]))

    # ----- Corotation evaluation -----
    cr = evaluate_at(s, r_CR)
    if cr is None or cr["Sigma"] <= 0 or not np.isfinite(cr["kappa_eff"]):
        return None
    kappa_eff_CR = cr["kappa_eff"]
    Sigma_CR = cr["Sigma"]

    # If κ²_eff at CR is negative, sample is unphysical at CR — flag and skip
    if kappa_eff_CR <= 0:
        return {
            "r_CR_over_Rd": r_CR_over_Rd,
            "omega_p": omega_p,
            "X": float("nan"),
            "A": 0.0,
            "ilr_flag": "k2eff_negative_at_CR",
            "r_ILR_kpc": None,
            "Q_ILR": float("nan"),
            "score": 0.0,
        }

    # ----- Toomre X parameter at corotation, m=2 -----
    X = kappa_eff_CR ** 2 * r_CR / (2 * np.pi * G_SI * Sigma_CR * M_MODE)
    A = A_window(X)

    # ----- ILR search: Ω(r) - κ_eff(r)/2 = Ω_p -----
    # Build κ_eff array (signed)
    k2 = s["kappa2_eff"]
    sgn = np.sign(k2)
    k_eff_arr = np.sqrt(np.abs(k2)) * sgn
    f = s["omega"] - k_eff_arr / 2.0 - omega_p

    r_ILR = find_first_crossing(s["r"], f)
    if r_ILR is None:
        # No ILR → no damping → bar-favorable
        Q_ILR = Q_FLOOR
        ilr_flag = "absent"
        r_ILR_kpc = None
    else:
        ilr_eval = evaluate_at(s, r_ILR)
        if ilr_eval is None or ilr_eval["Sigma"] <= 0 or ilr_eval["kappa_eff"] <= 0:
            Q_ILR = Q_FLOOR
            ilr_flag = "ilr_unphysical"
            r_ILR_kpc = float(r_ILR / KPC_TO_M)
        else:
            Q_ILR = (ilr_eval["sigma_R"] * ilr_eval["kappa_eff"]
                     / (3.36 * G_SI * ilr_eval["Sigma"]))
            ilr_flag = "present"
            r_ILR_kpc = float(r_ILR / KPC_TO_M)

    score = A / max(Q_ILR, Q_FLOOR)

    return {
        "r_CR_over_Rd": float(r_CR_over_Rd),
        "r_CR_kpc": float(r_CR / KPC_TO_M),
        "omega_p_per_s": omega_p,
        "X": float(X),
        "A": float(A),
        "Sigma_CR_Msun_pc2": float(Sigma_CR / MSUN_PER_PC2_TO_KG_PER_M2),
        "kappa_eff_CR_per_s": float(kappa_eff_CR),
        "ilr_flag": ilr_flag,
        "r_ILR_kpc": r_ILR_kpc,
        "Q_ILR": float(Q_ILR),
        "score": float(score),
    }


def best_bar_score(g, zeta: float):
    """Scan r_CR/R_d grid, return record with max score."""
    records = []
    for r_over in R_CR_OVER_RD_GRID:
        rec = bar_score_at(g, zeta, r_over)
        if rec is not None:
            records.append(rec)
    if not records:
        return None, []
    best = max(records, key=lambda r: r["score"])
    return best, records


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> dict:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    labels = json.load(open(LABELS_PATH))
    cls = load_classification(CLS_PATH)
    raw = parse_sparc_dat(DAT_PATH)

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
    name_to_regime = {i.name: i.regime for i in infos}
    y_true = np.array([1 if name_to_label[g.name] == "bar" else 0 for g in inputs])

    # Per ζ: best score per galaxy + AUC + confusion at best threshold
    zeta_results = {}
    for z in ZETA_GRID:
        scores = []
        details = []
        for g in inputs:
            best, all_recs = best_bar_score(g, z)
            if best is None:
                scores.append(np.nan)
                details.append(None)
            else:
                scores.append(best["score"])
                details.append(best)
        scores = np.array(scores)
        finite = np.isfinite(scores)
        # AUC (positive class = bar; high score = more bar-like)
        a = auc(y_true[finite], scores[finite])
        # Threshold via maximum accuracy on score grid
        if finite.sum() >= 5:
            sorted_thresh = np.sort(np.unique(scores[finite]))
            best_acc = -1
            best_thr = float(np.median(scores[finite]))
            for thr in sorted_thresh:
                pred = (scores[finite] >= thr).astype(int)
                cm = confusion(y_true[finite], pred)
                if cm["accuracy"] > best_acc:
                    best_acc = cm["accuracy"]
                    best_thr = thr
            pred_at_best = (scores[finite] >= best_thr).astype(int)
            cm_best = confusion(y_true[finite], pred_at_best)
        else:
            best_thr = float("nan")
            cm_best = {"accuracy": None}
        zeta_results[z] = {
            "n_used": int(finite.sum()),
            "auc": a,
            "best_threshold": float(best_thr),
            "confusion_at_best_threshold": cm_best,
            "scores": scores.tolist(),
            "details": details,
        }
        print(f"  ζ={z:.1f}  N={finite.sum():2d}  AUC={a:.3f}  "
              f"best_thr={best_thr:.3f}  acc@best_thr={cm_best['accuracy']:.3f}")

    # Pick best ζ by AUC
    best_zeta = max(ZETA_GRID, key=lambda z: (zeta_results[z]["auc"] or 0))
    bz = zeta_results[best_zeta]
    print(f"\nBest ζ by AUC: ζ={best_zeta} (AUC={bz['auc']:.3f})")

    # Per-galaxy at best ζ
    per_galaxy = []
    for g, det in zip(inputs, bz["details"]):
        per_galaxy.append({
            "name": g.name,
            "label": name_to_label[g.name],
            "regime": name_to_regime[g.name],
            "alpha": g.alpha,
            "R_d_kpc": g.R_d_kpc,
            "score": det["score"] if det else float("nan"),
            "X": det["X"] if det else float("nan"),
            "A": det["A"] if det else float("nan"),
            "Q_ILR": det["Q_ILR"] if det else float("nan"),
            "ilr_flag": det["ilr_flag"] if det else "no_data",
            "r_CR_kpc": det["r_CR_kpc"] if det else float("nan"),
            "r_CR_over_Rd": det["r_CR_over_Rd"] if det else float("nan"),
            "r_ILR_kpc": det["r_ILR_kpc"] if det else None,
        })

    # Per-regime medians
    regime_med = {}
    for reg in ("FLOW", "TRANSITION", "LATENT"):
        sub = [r for r in per_galaxy if r["regime"] == reg and np.isfinite(r["score"])]
        if not sub:
            continue
        regime_med[reg] = {
            "n": len(sub),
            "median_score": float(np.median([r["score"] for r in sub])),
            "median_X":     float(np.median([r["X"] for r in sub])),
            "median_Q_ILR": float(np.median([r["Q_ILR"] for r in sub])),
            "frac_ilr_absent": float(np.mean([r["ilr_flag"] == "absent" for r in sub])),
        }

    # Distribution stats
    Xs = np.array([r["X"] for r in per_galaxy if np.isfinite(r["X"])])
    Qs = np.array([r["Q_ILR"] for r in per_galaxy if np.isfinite(r["Q_ILR"])])
    scores_finite = np.array([r["score"] for r in per_galaxy if np.isfinite(r["score"])])
    ilr_counts = {}
    for r in per_galaxy:
        ilr_counts[r["ilr_flag"]] = ilr_counts.get(r["ilr_flag"], 0) + 1

    # Plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax_score, ax_X, ax_Q, ax_metrics = axes.flatten()

    # Score distribution by label
    sc_bar = np.array([r["score"] for r in per_galaxy
                       if r["label"] == "bar" and np.isfinite(r["score"])])
    sc_nob = np.array([r["score"] for r in per_galaxy
                       if r["label"] == "no_bar" and np.isfinite(r["score"])])
    if sc_bar.size and sc_nob.size:
        bins = np.linspace(0, max(sc_bar.max(), sc_nob.max()) * 1.05, 25)
        ax_score.hist(sc_nob, bins=bins, alpha=0.6, color="steelblue",
                      label=f"no_bar (N={len(sc_nob)})", edgecolor="k")
        ax_score.hist(sc_bar, bins=bins, alpha=0.6, color="crimson",
                      label=f"bar (N={len(sc_bar)})", edgecolor="k")
        ax_score.axvline(bz["best_threshold"], color="k", ls="--",
                         label=f"best_thr = {bz['best_threshold']:.2f}")
        ax_score.set_xlabel(f"bar-score (ζ={best_zeta})")
        ax_score.set_ylabel("count")
        ax_score.set_title(f"v0.2 bar-score distribution by label  AUC={bz['auc']:.3f}")
        ax_score.legend()
        ax_score.grid(True, alpha=0.2)

    # X distribution + window
    if Xs.size:
        bins_X = np.linspace(0, min(Xs.max() * 1.1, 10), 30)
        ax_X.hist(Xs, bins=bins_X, color="tab:purple", alpha=0.7, edgecolor="k")
        # Overlay window
        x_grid = np.linspace(0, bins_X.max(), 200)
        ax_X.twinx().plot(x_grid, [A_window(x) for x in x_grid], color="orange",
                          lw=2, label="A(X)")
        ax_X.axvline(X_PEAK, color="orange", ls="--", lw=1)
        ax_X.set_xlabel("X = κ_eff² r_CR / (2π G Σ m), m=2")
        ax_X.set_ylabel("count")
        ax_X.set_title("X distribution at best r_CR + A(X) window")
        ax_X.grid(True, alpha=0.2)

    # Q_ILR distribution
    if Qs.size:
        Q_log = np.log10(np.clip(Qs, 1e-3, None))
        ax_Q.hist(Q_log, bins=20, color="tab:green", alpha=0.7, edgecolor="k")
        ax_Q.axvline(np.log10(Q_FLOOR), color="r", ls=":", label=f"Q_floor={Q_FLOOR}")
        ax_Q.set_xlabel("log10(Q_ILR)")
        ax_Q.set_ylabel("count")
        ax_Q.set_title(f"Q_ILR distribution (ILR absent → Q_floor)\n"
                       f"ilr counts: {ilr_counts}")
        ax_Q.legend()
        ax_Q.grid(True, alpha=0.2)

    # ζ-grid: AUC and accuracy
    zs = ZETA_GRID
    aucs = [zeta_results[z]["auc"] or 0 for z in zs]
    accs = [(zeta_results[z]["confusion_at_best_threshold"]["accuracy"] or 0) for z in zs]
    ax_metrics.plot(zs, aucs, "o-", label="AUC", color="tab:orange")
    ax_metrics.plot(zs, accs, "s-", label="acc @ best_thr", color="tab:blue")
    ax_metrics.axhline(0.5, color="gray", ls=":", label="AUC=0.5 (random)")
    ax_metrics.axvline(best_zeta, color="black", ls=":", label=f"best ζ={best_zeta}")
    ax_metrics.set_xlabel("ζ")
    ax_metrics.set_ylabel("metric")
    ax_metrics.set_ylim(0, 1.05)
    ax_metrics.set_title("v0.2 metrics vs ζ")
    ax_metrics.legend(fontsize=9)
    ax_metrics.grid(True, alpha=0.2)

    fig.suptitle(f"EFC-BIC v0.2 (resonance) — N={len(inputs)}  "
                 f"({(y_true == 1).sum()} bars, {(y_true == 0).sum()} no_bars)")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = OUTDIR / "v02_resonance.png"
    fig.savefig(out_png, dpi=140)
    plt.close(fig)

    out = {
        "version": "efc_bic_v0.2_resonance",
        "n_galaxies": len(inputs),
        "n_bar": int((y_true == 1).sum()),
        "n_no_bar": int((y_true == 0).sum()),
        "zeta_grid": ZETA_GRID,
        "r_CR_over_Rd_grid": R_CR_OVER_RD_GRID.tolist(),
        "X_window": {"peak": X_PEAK, "sigma": X_SIGMA},
        "Q_floor": Q_FLOOR,
        "best_zeta": best_zeta,
        "best_AUC": bz["auc"],
        "zeta_results": {
            str(z): {k: v for k, v in zeta_results[z].items() if k != "details"}
            for z in ZETA_GRID
        },
        "per_galaxy_at_best_zeta": per_galaxy,
        "by_regime_at_best_zeta": regime_med,
        "ilr_counts": ilr_counts,
        "X_distribution": {
            "n": int(Xs.size),
            "median": float(np.median(Xs)) if Xs.size else None,
            "p10": float(np.percentile(Xs, 10)) if Xs.size else None,
            "p90": float(np.percentile(Xs, 90)) if Xs.size else None,
        },
    }
    out_path = OUTDIR / "v02_resonance.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)

    # ---- Console report ----
    print(f"\n=== Per-regime medians at best ζ={best_zeta} ===")
    print(f"{'regime':12s} {'N':>3s} {'med_score':>10s} {'med_X':>8s} "
          f"{'med_Q_ILR':>10s} {'frac_no_ILR':>12s}")
    for reg, d in regime_med.items():
        print(f"{reg:12s} {d['n']:>3d} {d['median_score']:>10.3f} "
              f"{d['median_X']:>8.2f} {d['median_Q_ILR']:>10.3f} "
              f"{d['frac_ilr_absent']:>12.2f}")
    print(f"\n=== ILR flag counts ===")
    for flag, n in ilr_counts.items():
        print(f"  {flag:30s}  {n}")
    print(f"\n=== X distribution ===")
    print(f"  N={Xs.size}, median={out['X_distribution']['median']:.2f}, "
          f"p10={out['X_distribution']['p10']:.2f}, p90={out['X_distribution']['p90']:.2f}")

    # Confusion matrix at best ζ + best_thr
    cm = bz["confusion_at_best_threshold"]
    print(f"\n=== Confusion matrix at best ζ={best_zeta}, thr={bz['best_threshold']:.3f} ===")
    print(f"                pred_no_bar  pred_bar")
    print(f"  true_no_bar   {cm['tn']:11d}  {cm['fp']:8d}")
    print(f"  true_bar      {cm['fn']:11d}  {cm['tp']:8d}")
    print(f"  accuracy={cm['accuracy']:.3f}  precision={cm['precision']:.3f}  "
          f"recall={cm['recall']:.3f}  F1={cm['f1']:.3f}")
    print(f"  AUC={bz['auc']:.3f}")

    # Misclassified (TP/TN/FP/FN listing)
    print(f"\n=== Misclassified at best ζ={best_zeta}, thr={bz['best_threshold']:.3f} ===")
    for r in per_galaxy:
        if not np.isfinite(r["score"]):
            continue
        pred_bar = r["score"] >= bz["best_threshold"]
        true_bar = r["label"] == "bar"
        if pred_bar != true_bar:
            err = "FP" if pred_bar else "FN"
            print(f"  [{err}] {r['name']:14s} {r['regime']:11s} {r['label']:7s} "
                  f"score={r['score']:.2f} X={r['X']:.2f} Q_ILR={r['Q_ILR']:.3f} "
                  f"ilr={r['ilr_flag']} r_CR/R_d={r['r_CR_over_Rd']:.2f}")

    print(f"\nWrote: {out_path}")
    print(f"Wrote: {out_png}")
    return out


if __name__ == "__main__":
    main()
