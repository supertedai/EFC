from __future__ import annotations

import numpy as np

from homo_fluxus_a_thermodynamic_framework import (
    PAPER_TITLE,
    PAPER_DOI,
    PAPER_ORCID,
    evaluate_condition,
)


def main() -> None:
    # Synthetic 2D demonstration of Eq. (1): dS/dt < 0 => Ef · ∇Phi > 0
    nx, ny = 60, 40
    x = np.linspace(0.0, 1.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    X, Y = np.meshgrid(x, y, indexing="ij")

    # Define a coherence potential with a gentle spatial gradient
    phi = 0.8 * X + 0.3 * Y

    # Construct an energy flow field mostly aligned with grad(phi)
    # Compute grad(phi)
    gx, gy = np.gradient(phi, x[1] - x[0], y[1] - y[0], edge_order=2)
    g = np.stack([gx, gy], axis=-1)
    g_norm = np.linalg.norm(g, axis=-1, keepdims=True) + 1e-9
    Ef = 1.5 * g / g_norm  # aligned

    # Introduce a small misalignment in a corner to show partial violation
    Ef[-10:, -10:, :] *= -0.5

    # Build an entropy timeseries decreasing over time across the grid
    T = 25
    t = np.arange(T, dtype=float)
    S0, alpha = 5.0, 0.05
    S_series = (S0 - alpha * t)[:, None, None] * np.ones_like(phi)[None, :, :]

    results = evaluate_condition(
        Ef=Ef,
        phi=phi,
        S_series=S_series,
        dt=1.0,
        spacing=(x[1] - x[0], y[1] - y[0]),
    )

    mask_t = results["implication_mask_t"]  # shape (T, nx, ny)
    dS_dt = results["dS_dt"]
    dot_field = results["dot_field"]

    satisfied_fraction = float(mask_t.mean())
    satisfied_last = float(mask_t[-1].mean())

    print("Homo Fluxus demo (Eq. 1)")
    print("Paper:", PAPER_TITLE)
    print("DOI:", PAPER_DOI)
    print("ORCID:", PAPER_ORCID)
    print("Overall satisfied fraction across time and space:", round(satisfied_fraction, 4))
    print("Satisfied fraction at final time step:", round(satisfied_last, 4))

    # Optional visualization if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
        im0 = axs[0].imshow(dot_field.T, origin="lower", cmap="viridis")
        axs[0].set_title("Ef · ∇Phi (spatial)")
        plt.colorbar(im0, ax=axs[0], fraction=0.046)

        im1 = axs[1].imshow(dS_dt[-1].T, origin="lower", cmap="coolwarm")
        axs[1].set_title("dS/dt (final time)")
        plt.colorbar(im1, ax=axs[1], fraction=0.046)

        im2 = axs[2].imshow(mask_t[-1].T, origin="lower", cmap="Greens")
        axs[2].set_title("Implication holds (final)")
        plt.colorbar(im2, ax=axs[2], fraction=0.046)

        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("matplotlib not available or plotting failed:", e)


if __name__ == "__main__":
    main()
