# demo_efc_rcmp_convergence_observation.py
# Minimal demo using efc_rcmp_convergence_observation

from __future__ import annotations
import numpy as np

import efc_rcmp_convergence_observation as src


def main() -> None:
    print("=== Demo: RCMP compliance check ===")
    checks = {c: True for c in src.RCMP_COMPONENTS}
    comp = src.rcmp_compliance(checks)
    print(f"Compliant: {comp['compliant']} (score={comp['score']}/5)")

    print("\n=== Demo: DES Y6 S8-tension sensitivity to IA model ===")
    des = src.PAPER_NUMERICS["cosmic_shear_observation"]["des_y6_s8_tension"]
    metrics = src.s8_significance_metrics(des["nla_sigma_range"], des["tatt_sigma"])
    print(
        "NLA range: %.1f–%.1fσ (mean=%.2f), TATT: %.1fσ; |Δ|=%.2fσ (%.1f%%)"
        % (
            metrics["nla_min"],
            metrics["nla_max"],
            metrics["nla_mean"],
            metrics["tatt"],
            metrics["reduction_abs"],
            100.0 * metrics["reduction_frac"],
        )
    )

    print("\n=== Demo: Phenomenological (mu, Sigma) amplitudes as constants over z ===")
    z = np.linspace(0, 2, 6)
    mu_z, sig_z = src.mu_sigma_amplitudes(1.0, 1.0, z)
    print("z:", z)
    print("mu(z):", mu_z)
    print("Sigma(z):", sig_z)

    print("\n=== RCMP problem-definition sentence ===")
    sentence = src.rcmp_problem_definition(
        measurement_name="S8 from cosmic shear (DES Y6)",
        regime="L2",
        proxy_dependencies=["baryonic_feedback_model", "intrinsic_alignment_model"],
    )
    print(sentence)

    # Optional: quick plot of sigma values if matplotlib is available
    try:
        import matplotlib.pyplot as plt

        labels = ["NLA (mean)", "TATT"]
        values = [metrics["nla_mean"], metrics["tatt"]]
        colors = ["tab:blue", "tab:orange"]
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(labels, values, color=colors)
        ax.set_ylabel("Tension significance (σ)")
        ax.set_title("DES Y6 S8 tension vs IA model (from Magnusson 2026 note)")
        for i, v in enumerate(values):
            ax.text(i, v + 0.05, f"{v:.2f}σ", ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("(Plot skipped; matplotlib not available or failed:", e, ")")


if __name__ == "__main__":
    main()
