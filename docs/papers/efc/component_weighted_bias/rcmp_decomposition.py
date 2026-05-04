#!/usr/bin/env python3
"""
rcmp_decomposition.py
=====================
Closes all four red points from reviewer for component-weighted bias paper.

Reads:
  - sparc175_model_curves.json  (from --save-curves patch)
  - sparc175_killtest_results.json  (regime classifications)

Computes (per galaxy):
  - DeltaAIC_inner  (r < r_c)
  - DeltaAIC_outer  (r >= r_c)
  - sign-flip detection
  - reweighting test (uniform, capped)

Produces:
  - rcmp_decomposition.json    : per-galaxy split AIC + reweighting
  - rcmp_summary.json          : aggregate statistics + regime-stratified
  - rcmp_signflip_table.json   : galaxies where sign(global) != sign(outer)
  - rcmp_robustness_rc.json    : sensitivity to r_c in {2,3,4,5} kpc
  - figs/rcmp_signflip.png     : main causal figure

CONVENTION (matches Kill-Test v6):
  delta_aic = AIC_NFW - AIC_EFC   (positive = EFC wins)

Usage:
  python rcmp_decomposition.py <curves_file> <killtest_file> <output_dir>
"""

import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


K_EFC = 3
K_NFW = 2


def compute_split_aic(galaxy_record, r_c, weight_scheme="standard"):
    pts = galaxy_record["datapoints"]
    r = np.array([p["r_kpc"] for p in pts])
    V_obs = np.array([p["V_obs"] for p in pts])
    sigma = np.array([p["sigma"] for p in pts])
    V_efc = np.array([p["V_EFC"] for p in pts])
    V_nfw = np.array([p["V_NFW"] for p in pts])

    if weight_scheme == "standard":
        w = 1.0 / sigma ** 2
    elif weight_scheme == "uniform":
        w = np.ones_like(sigma)
    elif weight_scheme == "capped":
        w = np.minimum(1.0 / sigma ** 2, np.median(1.0 / sigma ** 2))
    else:
        raise ValueError(f"unknown weight_scheme: {weight_scheme}")

    contrib_efc = w * (V_obs - V_efc) ** 2
    contrib_nfw = w * (V_obs - V_nfw) ** 2

    mask_in = r < r_c
    mask_out = ~mask_in

    def split(c_efc, c_nfw, mask):
        n = int(mask.sum())
        if n == 0:
            return None, 0
        chi2_e = float(c_efc[mask].sum())
        chi2_n = float(c_nfw[mask].sum())
        return chi2_n - chi2_e + 2 * (K_NFW - K_EFC), n

    inner_val, n_inner = split(contrib_efc, contrib_nfw, mask_in)
    outer_val, n_outer = split(contrib_efc, contrib_nfw, mask_out)
    glob_val, n_total = split(contrib_efc, contrib_nfw, np.ones_like(mask_in, dtype=bool))

    return {
        "delta_aic_inner": inner_val,
        "delta_aic_outer": outer_val,
        "delta_aic_global": glob_val,
        "n_inner": n_inner,
        "n_outer": n_outer,
        "n_total": n_total,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("curves_file")
    ap.add_argument("killtest_file")
    ap.add_argument("output_dir")
    ap.add_argument("--rc", type=float, default=3.0,
                    help="Critical radius in kpc (default: 3.0)")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    fig_dir = out_dir / "figs"
    fig_dir.mkdir(exist_ok=True)

    print(f"Loading curves from {args.curves_file}")
    with open(args.curves_file) as f:
        curves = json.load(f)
    galaxies = curves["galaxies"] if "galaxies" in curves else curves

    print(f"Loading regime classifications from {args.killtest_file}")
    with open(args.killtest_file) as f:
        kt_data = json.load(f)
    kt_results = kt_data.get("per_galaxy_results", kt_data.get("results", kt_data))
    if isinstance(kt_results, list):
        kt_lookup = {e.get("name") or e.get("galaxy"): e for e in kt_results
                     if e.get("name") or e.get("galaxy")}
    else:
        kt_lookup = kt_results

    decomp = []
    for gal in galaxies:
        name = gal["galaxy"]
        kt = kt_lookup.get(name, {})
        regime = kt.get("comparison", {}).get("regime") or gal.get("regime", "UNKNOWN")
        delta_aic_kt = kt.get("comparison", {}).get("delta_aic")

        std = compute_split_aic(gal, args.rc, "standard")
        unif = compute_split_aic(gal, args.rc, "uniform")
        cap = compute_split_aic(gal, args.rc, "capped")

        sign_global = np.sign(std["delta_aic_global"]) if std["delta_aic_global"] is not None else 0
        sign_outer = np.sign(std["delta_aic_outer"]) if std["delta_aic_outer"] is not None else 0
        sign_flip = bool(sign_global != sign_outer
                         and std["delta_aic_outer"] is not None
                         and sign_global != 0 and sign_outer != 0)

        decomp.append({
            "galaxy": name,
            "regime": regime,
            "delta_aic_killtest": delta_aic_kt,
            "delta_aic_global_recomputed": std["delta_aic_global"],
            "delta_aic_inner": std["delta_aic_inner"],
            "delta_aic_outer": std["delta_aic_outer"],
            "delta_aic_uniform_weight": unif["delta_aic_global"],
            "delta_aic_capped_weight": cap["delta_aic_global"],
            "sign_flip": sign_flip,
            "n_inner": std["n_inner"],
            "n_outer": std["n_outer"],
        })

    with open(out_dir / "rcmp_decomposition.json", "w") as f:
        json.dump({"r_c_kpc": args.rc,
                   "convention": "AIC_NFW - AIC_EFC (positive = EFC wins)",
                   "galaxies": decomp}, f, indent=2)
    print(f"  wrote rcmp_decomposition.json (N={len(decomp)})")

    flips = [d for d in decomp if d["sign_flip"]]
    flips_sorted = sorted(flips,
                          key=lambda d: abs(d["delta_aic_global_recomputed"] or 0),
                          reverse=True)
    with open(out_dir / "rcmp_signflip_table.json", "w") as f:
        json.dump({"n_signflip": len(flips), "n_total": len(decomp),
                   "fraction": len(flips) / len(decomp) if decomp else 0,
                   "galaxies": flips_sorted}, f, indent=2)
    print(f"  sign-flip count: {len(flips)}/{len(decomp)} "
          f"({100*len(flips)/len(decomp):.1f}%)")

    summary = {"r_c_kpc": args.rc, "n_total": len(decomp)}

    # Aggregate Spearman correlations
    glob_arr = np.array([d["delta_aic_global_recomputed"] for d in decomp
                         if d["delta_aic_global_recomputed"] is not None])
    out_arr = np.array([d["delta_aic_outer"] for d in decomp
                        if d["delta_aic_outer"] is not None])
    in_arr = np.array([d["delta_aic_inner"] for d in decomp
                       if d["delta_aic_inner"] is not None])
    if len(glob_arr) > 5:
        rho_go, p_go = spearmanr(
            [d["delta_aic_global_recomputed"] for d in decomp
             if d["delta_aic_outer"] is not None],
            [d["delta_aic_outer"] for d in decomp
             if d["delta_aic_outer"] is not None])
        summary["spearman_global_vs_outer"] = {
            "rho": float(rho_go), "p_value": float(p_go)}

    for regime in ["FLOW", "TRANSITION", "LATENT", "UNKNOWN"]:
        sub = [d for d in decomp if d["regime"] == regime]
        if not sub:
            continue
        global_aic = [d["delta_aic_global_recomputed"] for d in sub
                      if d["delta_aic_global_recomputed"] is not None]
        outer_aic = [d["delta_aic_outer"] for d in sub
                     if d["delta_aic_outer"] is not None]
        inner_aic = [d["delta_aic_inner"] for d in sub
                     if d["delta_aic_inner"] is not None]
        n_flip = sum(1 for d in sub if d["sign_flip"])
        summary[regime] = {
            "n": len(sub),
            "mean_global": float(np.mean(global_aic)) if global_aic else None,
            "median_global": float(np.median(global_aic)) if global_aic else None,
            "mean_outer": float(np.mean(outer_aic)) if outer_aic else None,
            "median_outer": float(np.median(outer_aic)) if outer_aic else None,
            "mean_inner": float(np.mean(inner_aic)) if inner_aic else None,
            "median_inner": float(np.median(inner_aic)) if inner_aic else None,
            "n_signflip": n_flip,
            "fraction_signflip": n_flip / len(sub),
        }
    with open(out_dir / "rcmp_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  wrote rcmp_summary.json")

    robust = {}
    for rc_test in [2.0, 3.0, 4.0, 5.0]:
        sub_decomp = []
        for gal in galaxies:
            res = compute_split_aic(gal, rc_test, "standard")
            sg = np.sign(res["delta_aic_global"]) if res["delta_aic_global"] is not None else 0
            so = np.sign(res["delta_aic_outer"]) if res["delta_aic_outer"] is not None else 0
            flip = (sg != so
                    and res["delta_aic_outer"] is not None
                    and sg != 0 and so != 0)
            sub_decomp.append({"flip": flip,
                               "global": res["delta_aic_global"],
                               "outer": res["delta_aic_outer"],
                               "n_inner": res["n_inner"],
                               "n_outer": res["n_outer"]})
        n_flip = sum(1 for d in sub_decomp if d["flip"])
        robust[f"rc_{rc_test}"] = {
            "n_signflip": n_flip,
            "fraction": n_flip / len(sub_decomp) if sub_decomp else 0,
            "n_with_inner_data": sum(1 for d in sub_decomp if d["n_inner"] > 0),
            "n_with_outer_data": sum(1 for d in sub_decomp if d["n_outer"] > 0),
        }
    with open(out_dir / "rcmp_robustness_rc.json", "w") as f:
        json.dump(robust, f, indent=2)
    print("  wrote rcmp_robustness_rc.json")

    fig, ax = plt.subplots(figsize=(8, 6))
    regime_colors = {"FLOW": "#1a7abf", "TRANSITION": "#f5a623",
                     "LATENT": "#d0021b", "UNKNOWN": "#888"}
    for regime, color in regime_colors.items():
        sub = [d for d in decomp
               if d["regime"] == regime and d["delta_aic_outer"] is not None]
        if not sub:
            continue
        xs = [d["delta_aic_global_recomputed"] for d in sub]
        ys = [d["delta_aic_outer"] for d in sub]
        ax.scatter(xs, ys, c=color, alpha=0.7, s=30, label=f"{regime} (N={len(sub)})",
                   edgecolors="none")
    ax.axhline(0, color="black", lw=0.6, ls="--", alpha=0.5)
    ax.axvline(0, color="black", lw=0.6, ls="--", alpha=0.5)

    valid_glob = [d["delta_aic_global_recomputed"] for d in decomp
                  if d["delta_aic_global_recomputed"] is not None]
    if valid_glob:
        lo = min(valid_glob)
        hi = max(valid_glob)
        ax.plot([lo, hi], [lo, hi], color="grey", lw=0.5, alpha=0.4,
                label="identity (no decomposition effect)")

    ax.set_xlabel(r"$\Delta\mathrm{AIC}_{\mathrm{global}}$  "
                  r"(positive = EFC wins)")
    ax.set_ylabel(r"$\Delta\mathrm{AIC}_{\mathrm{outer}}$  "
                  r"($r \geq r_c$)")
    ax.set_title(f"RCMP decomposition: outer vs global "
                 f"($r_c = {args.rc}$ kpc, "
                 f"sign-flip in {len(flips)}/{len(decomp)} galaxies)")
    ax.legend(fontsize=9, loc="best")
    plt.tight_layout()
    plt.savefig(fig_dir / "rcmp_signflip.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  wrote figs/rcmp_signflip.png")

    print("Done.")


if __name__ == "__main__":
    main()
