import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------
# 1) EFC: Simple demonstration H(S)
# ---------------------------------------------------
def H_efc(S):
    # Toy model for demonstration:
    # H increases smoothly with entropy
    return 70 * (1 + 0.25 * np.tanh(3*(S - 0.5)))


# ---------------------------------------------------
# 2) LCDM baseline (flat Ωm=0.3, ΩΛ=0.7)
# ---------------------------------------------------
def H_lcdm(z):
    H0 = 70
    Om = 0.3
    Ol = 0.7
    return H0 * np.sqrt(Om*(1+z)**3 + Ol)


# ---------------------------------------------------
# 3) Generate comparison plot
# ---------------------------------------------------
def main():
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    # EFC curve vs entropy
    S = np.linspace(0, 1, 400)
    H_EFC = H_efc(S)

    # LCDM vs z
    z = np.linspace(0, 6, 400)
    H_LCDM = H_lcdm(z)

    plt.figure(figsize=(10,6))
    plt.plot(S, H_EFC, label="EFC: H(S)", linewidth=2)
    plt.plot(z/6, H_LCDM/np.max(H_LCDM)*np.max(H_EFC),
             label="ΛCDM: H(z) scaled", linestyle="--")

    plt.xlabel("Entropy S  (normalized)")
    plt.ylabel("Expansion Rate H")
    plt.title("EFC vs ΛCDM — Demonstration Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path / "EFC_vs_LCDM_plot.png", dpi=300)

    print("Generated output/EFC_vs_LCDM_plot.png")


if __name__ == "__main__":
    main()
