#!/usr/bin/env python3
"""
BESR3 Analysis: Visualize and analyze alpha_sim results
========================================================
Run after besr3_extract_alpha.py has produced results.

Usage:
    python besr3_analyze.py --input results/besr3_alpha_results.csv

Produces:
    - alpha_distribution.png
    - alpha_vs_yCCT.png
    - alpha_vs_mass.png
    - K0_vs_alpha.png
    - cc_comparison.png
    - entropy_profiles_sample.png
    - besr3_analysis_report.txt
"""

import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr, ks_2samp, norm, lognorm

matplotlib.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "legend.fontsize": 11,
    "figure.figsize": (10, 7),
    "figure.dpi": 150,
})


def load_results(csv_path):
    """Load BESR3 results CSV into structured array."""
    data = np.genfromtxt(
        csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8"
    )
    return data


def plot_alpha_distribution(data, outdir):
    """Plot alpha distribution with lognormal fit."""
    alpha = data["alpha"]
    alpha = alpha[np.isfinite(alpha) & (alpha > 0)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Linear histogram
    ax1.hist(alpha, bins=25, density=True, alpha=0.7, color="steelblue", edgecolor="white")

    # Lognormal fit
    shape, loc, scale = lognorm.fit(alpha, floc=0)
    x = np.linspace(0, np.max(alpha) * 1.2, 200)
    ax1.plot(x, lognorm.pdf(x, shape, loc, scale), "r-", lw=2,
             label=f"Lognormal (sigma={shape:.2f}, mu={np.log(scale):.2f})")

    ax1.axvline(1.1, color="green", ls="--", lw=1.5, alpha=0.7, label="Kaiser self-similar (1.1)")
    ax1.axvline(np.median(alpha), color="orange", ls=":", lw=2, label=f"Median ({np.median(alpha):.2f})")

    ax1.set_xlabel("alpha (entropy power-law index)")
    ax1.set_ylabel("Probability density")
    ax1.set_title(f"TNG-Cluster alpha_sim Distribution (N={len(alpha)})")
    ax1.legend()

    # Log-scale histogram
    log_alpha = np.log(alpha)
    ax2.hist(log_alpha, bins=25, density=True, alpha=0.7, color="coral", edgecolor="white")
    ax2.set_xlabel("ln(alpha)")
    ax2.set_ylabel("Probability density")
    ax2.set_title("ln(alpha) Distribution")

    # Normal fit on log-space
    mu_ln = np.mean(log_alpha)
    sig_ln = np.std(log_alpha)
    x_ln = np.linspace(np.min(log_alpha) - 0.5, np.max(log_alpha) + 0.5, 200)
    ax2.plot(x_ln, norm.pdf(x_ln, mu_ln, sig_ln), "r-", lw=2,
             label=f"Normal (mu={mu_ln:.2f}, sigma={sig_ln:.2f})")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(outdir / "alpha_distribution.png", bbox_inches="tight")
    plt.close()

    return {
        "n": len(alpha),
        "mean": float(np.mean(alpha)),
        "median": float(np.median(alpha)),
        "std": float(np.std(alpha)),
        "skewness": float(np.mean(((alpha - np.mean(alpha)) / np.std(alpha))**3)),
        "lognorm_shape": float(shape),
        "lognorm_scale": float(scale),
    }


def plot_alpha_vs_yCCT(data, outdir):
    """Plot alpha vs y_CCT_proxy -- the key BESR3 test."""
    alpha = data["alpha"]
    y = data["y_CCT_proxy"]
    cc = data["CC_class"]

    mask = np.isfinite(alpha) & np.isfinite(y)
    alpha_v = alpha[mask]
    y_v = y[mask]
    cc_v = cc[mask]

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = {"SCC": "blue", "WCC": "green", "NCC": "red"}
    labels_used = set()

    for a, yy, c in zip(alpha_v, y_v, cc_v):
        c_str = c if isinstance(c, str) else c.decode()
        color = colors.get(c_str, "gray")
        label = c_str if c_str not in labels_used else None
        labels_used.add(c_str)
        ax.scatter(a, yy, c=color, s=40, alpha=0.6, edgecolor="white", lw=0.5, label=label)

    # Spearman correlation
    rho, pval = spearmanr(alpha_v, y_v)

    # Linear fit for visual guide
    z = np.polyfit(alpha_v, y_v, 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.min(alpha_v), np.max(alpha_v), 100)
    ax.plot(x_line, p(x_line), "k--", alpha=0.5, lw=1.5)

    ax.set_xlabel("alpha_sim (entropy gradient)")
    ax.set_ylabel("y = log10(K0/K100) (CCT proxy)")
    ax.set_title(
        f"BESR3 Key Test: alpha_sim vs CCT Proxy\n"
        f"rho_Spearman = {rho:.3f} (p = {pval:.2e}), N = {len(alpha_v)}"
    )

    # ACCEPT reference
    ax.text(
        0.02, 0.98,
        f"ACCEPT observed: rho = +0.36\nTNG-Cluster sim: rho = {rho:.3f}\n"
        f"Sign flip = {rho < 0}",
        transform=ax.transAxes, va="top", fontsize=11,
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
    )

    ax.legend()
    plt.tight_layout()
    plt.savefig(outdir / "alpha_vs_yCCT.png", bbox_inches="tight")
    plt.close()

    return {"spearman_rho": float(rho), "spearman_p": float(pval), "n": len(alpha_v)}


def plot_alpha_vs_mass(data, outdir):
    """Plot alpha vs M500c."""
    alpha = data["alpha"]
    mass = data["M500c_Msun"]

    mask = np.isfinite(alpha) & (mass > 0)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(mass[mask], alpha[mask], s=30, alpha=0.5, c="steelblue")
    ax.set_xscale("log")
    ax.set_xlabel("M500c [Msun]")
    ax.set_ylabel("alpha_sim")
    ax.set_title("Entropy Gradient vs Cluster Mass")

    rho, pval = spearmanr(mass[mask], alpha[mask])
    ax.text(0.02, 0.98, f"rho = {rho:.3f} (p = {pval:.3f})",
            transform=ax.transAxes, va="top", fontsize=12,
            bbox=dict(boxstyle="round", facecolor="lightyellow"))

    plt.tight_layout()
    plt.savefig(outdir / "alpha_vs_mass.png", bbox_inches="tight")
    plt.close()

    return {"rho_alpha_mass": float(rho), "p_alpha_mass": float(pval)}


def plot_K0_vs_alpha(data, outdir):
    """Plot K0 vs alpha -- core state vs gradient."""
    K0 = data["K0"]
    alpha = data["alpha"]
    cc = data["CC_class"]

    mask = np.isfinite(K0) & np.isfinite(alpha) & (K0 > 0)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {"SCC": "blue", "WCC": "green", "NCC": "red"}
    labels_used = set()

    for k, a, c in zip(K0[mask], alpha[mask], cc[mask]):
        c_str = c if isinstance(c, str) else c.decode()
        color = colors.get(c_str, "gray")
        label = c_str if c_str not in labels_used else None
        labels_used.add(c_str)
        ax.scatter(a, k, c=color, s=40, alpha=0.6, label=label)

    ax.set_yscale("log")
    ax.axhline(22, color="blue", ls="--", alpha=0.5, label="SCC threshold (22)")
    ax.axhline(150, color="red", ls="--", alpha=0.5, label="NCC threshold (150)")
    ax.set_xlabel("alpha_sim")
    ax.set_ylabel("K0 [keV cm^2]")
    ax.set_title("Core Entropy vs Gradient")

    rho, pval = spearmanr(alpha[mask], K0[mask])
    ax.text(0.02, 0.98, f"rho(alpha, K0) = {rho:.3f} (p = {pval:.3f})",
            transform=ax.transAxes, va="top", fontsize=12,
            bbox=dict(boxstyle="round", facecolor="lightyellow"))

    ax.legend()
    plt.tight_layout()
    plt.savefig(outdir / "K0_vs_alpha.png", bbox_inches="tight")
    plt.close()


def plot_cc_comparison(data, outdir):
    """Compare alpha distributions across CC classes."""
    cc = data["CC_class"]
    alpha = data["alpha"]

    classes = ["SCC", "WCC", "NCC"]
    alpha_by_cc = {}

    for c in classes:
        mask_c = np.array([
            (x == c if isinstance(x, str) else x.decode() == c)
            for x in cc
        ])
        mask = mask_c & np.isfinite(alpha)
        if np.sum(mask) > 0:
            alpha_by_cc[c] = alpha[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    colors = {"SCC": "blue", "WCC": "green", "NCC": "red"}

    # Box plot
    box_data = [alpha_by_cc.get(c, []) for c in classes]
    bp = ax1.boxplot(box_data, labels=classes, patch_artist=True)
    for patch, c in zip(bp["boxes"], classes):
        patch.set_facecolor(colors[c])
        patch.set_alpha(0.5)
    ax1.set_ylabel("alpha_sim")
    ax1.set_title("alpha Distribution by CC Class")

    # Add N counts
    for i, c in enumerate(classes):
        n = len(alpha_by_cc.get(c, []))
        ax1.text(i + 1, ax1.get_ylim()[1] * 0.95, f"N={n}", ha="center", fontsize=10)

    # Histogram overlay
    for c in classes:
        if c in alpha_by_cc and len(alpha_by_cc[c]) > 3:
            ax2.hist(alpha_by_cc[c], bins=15, alpha=0.4, color=colors[c],
                     label=f"{c} (N={len(alpha_by_cc[c])})", density=True)

    ax2.set_xlabel("alpha_sim")
    ax2.set_ylabel("Density")
    ax2.set_title("alpha Distributions Overlaid")
    ax2.legend()

    # KS test SCC vs NCC
    if "SCC" in alpha_by_cc and "NCC" in alpha_by_cc:
        if len(alpha_by_cc["SCC"]) > 3 and len(alpha_by_cc["NCC"]) > 3:
            ks, p_ks = ks_2samp(alpha_by_cc["SCC"], alpha_by_cc["NCC"])
            ax2.text(0.02, 0.98, f"KS(SCC vs NCC): D={ks:.3f}, p={p_ks:.3f}",
                     transform=ax2.transAxes, va="top", fontsize=10,
                     bbox=dict(boxstyle="round", facecolor="lightyellow"))

    plt.tight_layout()
    plt.savefig(outdir / "cc_comparison.png", bbox_inches="tight")
    plt.close()


def plot_sample_profiles(profile_dir, outdir, n_samples=9):
    """Plot a grid of sample entropy profiles with fits."""
    profile_files = sorted(profile_dir.glob("halo_*.npz"))

    if not profile_files:
        return

    # Sample evenly
    indices = np.linspace(0, len(profile_files) - 1, min(n_samples, len(profile_files)), dtype=int)

    ncols = 3
    nrows = (len(indices) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4 * nrows))
    axes = np.atleast_2d(axes)

    for idx, (ax_idx, file_idx) in enumerate(zip(range(len(indices)), indices)):
        ax = axes.flat[ax_idx]
        d = np.load(profile_files[file_idx])

        r = d["r_kpc"]
        K = d["K_kevcm2"]
        K0 = float(d["fit_K0"])
        K100 = float(d["fit_K100"])
        alpha = float(d["fit_alpha"])

        mask = np.isfinite(K) & (K > 0)
        ax.scatter(r[mask], K[mask], s=15, c="steelblue", zorder=2)

        # Fit curve
        r_fit = np.logspace(np.log10(10), np.log10(np.max(r[mask])), 100)
        K_fit = K0 + K100 * (r_fit / 100)**alpha
        ax.plot(r_fit, K_fit, "r-", lw=2, zorder=3)

        halo_name = profile_files[file_idx].stem
        ax.set_title(f"{halo_name}\nalpha={alpha:.2f}, K0={K0:.0f}", fontsize=10)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("r [kpc]")
        ax.set_ylabel("K [keV cm^2]")
        ax.grid(True, alpha=0.3)

    # Hide empty axes
    for ax in axes.flat[len(indices):]:
        ax.set_visible(False)

    plt.suptitle("Sample Entropy Profiles with Power-Law Fits", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(outdir / "entropy_profiles_sample.png", bbox_inches="tight")
    plt.close()


def write_report(stats, outdir):
    """Write text analysis report."""
    with open(outdir / "besr3_analysis_report.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write("BESR3 ANALYSIS REPORT\n")
        f.write("TNG-Cluster Entropy Gradient Extraction\n")
        f.write("=" * 60 + "\n\n")

        for section, data in stats.items():
            f.write(f"\n--- {section} ---\n")
            if isinstance(data, dict):
                for k, v in data.items():
                    f.write(f"  {k}: {v}\n")
            else:
                f.write(f"  {data}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("END OF REPORT\n")


def main():
    parser = argparse.ArgumentParser(description="BESR3 Analysis")
    parser.add_argument("--input", type=str, default="results/besr3_alpha_results.csv")
    parser.add_argument("--profiles", type=str, default="results/besr3_profiles")
    parser.add_argument("--output", type=str, default="results/plots")
    args = parser.parse_args()

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    data = load_results(args.input)
    print(f"Loaded {len(data)} results")

    stats = {}

    stats["distribution"] = plot_alpha_distribution(data, outdir)
    print("  Alpha distribution plot done")

    stats["besr3_key_test"] = plot_alpha_vs_yCCT(data, outdir)
    print("  Alpha vs yCCT plot done (KEY TEST)")

    stats["mass_dependence"] = plot_alpha_vs_mass(data, outdir)
    print("  Alpha vs mass plot done")

    plot_K0_vs_alpha(data, outdir)
    print("  K0 vs alpha plot done")

    plot_cc_comparison(data, outdir)
    print("  CC comparison plot done")

    profile_dir = Path(args.profiles)
    if profile_dir.exists():
        plot_sample_profiles(profile_dir, outdir)
        print("  Sample profiles plot done")

    write_report(stats, outdir)
    print("  Analysis report written")

    # Print key result
    key = stats.get("besr3_key_test", {})
    print(f"\n{'='*50}")
    print(f"KEY BESR3 RESULT:")
    print(f"  rho(alpha_sim, y_CCT) = {key.get('spearman_rho', 'N/A')}")
    print(f"  p-value = {key.get('spearman_p', 'N/A')}")
    print(f"  N = {key.get('n', 'N/A')}")
    print(f"  ACCEPT observed: rho = +0.36")
    print(f"  Sign flip expected by EFC proxy test")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
