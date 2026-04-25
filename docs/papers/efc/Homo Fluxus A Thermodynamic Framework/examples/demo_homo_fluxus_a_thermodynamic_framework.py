# demo_homo_fluxus_a_thermodynamic_framework.py
# Demonstration of Eq. (1) operationalization using the reference implementation.

import numpy as np
import sys

try:
    from homo_fluxus_a_thermodynamic_framework import (
        evaluate_equation_1,
        PAPER_DOI,
        EQUATION_1,
    )
except ImportError:
    print("Please ensure homo_fluxus_a_thermodynamic_framework.py is on PYTHONPATH.")
    sys.exit(1)


def make_demo_fields(nx=80, ny=60, T=7, misalign=False, noise=0.0):
    x = np.linspace(-1.0, 1.0, nx)
    y = np.linspace(-1.0, 1.0, ny)
    X, Y = np.meshgrid(x, y, indexing='xy')

    # Coherence potential: bowl + tilt to create structured gradients
    phi = 0.5 * (X**2 + 0.2 * Y**2) + 0.3 * X

    # Energy flow: generally follows +grad(phi), optionally misaligned
    dphidx, dphidy = np.gradient(phi, x, y, edge_order=2)
    Ex = dphidx.copy()
    Ey = dphidy.copy()
    if misalign:
        # Rotate by 90 degrees to break alignment
        Ex, Ey = -dphidy, dphidx
    # Normalize and add optional noise
    mag = np.sqrt(Ex**2 + Ey**2) + 1e-12
    Ex = Ex / mag + noise * np.random.default_rng(0).normal(scale=0.1, size=Ex.shape)
    Ey = Ey / mag + noise * np.random.default_rng(1).normal(scale=0.1, size=Ey.shape)

    # Entropy field decreases over time (global cooling trend)
    t = np.linspace(0.0, 1.0, T)
    S = np.empty((T, ny, nx))
    for i, ti in enumerate(t):
        S[i] = 1.0 - 0.8 * ti + 0.05 * np.sin(2 * np.pi * X) * np.cos(2 * np.pi * Y)

    return S, t, phi, (x, y), (Ex, Ey)


def main():
    print("DOI:", PAPER_DOI)
    print("Equation:", EQUATION_1)

    # Well-aligned case
    S, t, phi, coords, Ef = make_demo_fields(misalign=False, noise=0.0)
    mask_a, frac_a, E_dot_a = evaluate_equation_1(S, t, phi, coords, Ef, tol=1e-8)
    print(f"Aligned case: fraction satisfying Eq. (1) = {frac_a:.3f}")

    # Misaligned case
    S, t, phi, coords, Ef = make_demo_fields(misalign=True, noise=0.0)
    mask_b, frac_b, E_dot_b = evaluate_equation_1(S, t, phi, coords, Ef, tol=1e-8)
    print(f"Misaligned case: fraction satisfying Eq. (1) = {frac_b:.3f}")

    # Optional visualization
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipping plot.")
        return

    fig, axs = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for ax, mask, title in zip(
        axs,
        (mask_a, mask_b),
        ("Aligned E with ∇Φ", "E rotated ⟂ to ∇Φ"),
    ):
        im = ax.imshow(mask.T, origin='lower', cmap='viridis', extent=(coords[0][0], coords[0][-1], coords[1][0], coords[1][-1]))
        ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
    fig.colorbar(im, ax=axs.ravel().tolist(), shrink=0.8, label='Eq. (1) satisfied')
    plt.show()


if __name__ == "__main__":
    main()
