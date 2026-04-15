"""Minimal demonstration of the EFC -> Bellini-Sawicki mapping."""
from __future__ import annotations

import math

from efc_effective_horndeski_reduction_src.alpha_functions import (  # type: ignore  # noqa: E402
    alpha_B,
    alpha_M,
    alpha_T,
)


def main() -> None:
    # Evaluate the alpha functions across the entropy transition
    scale_factors = [0.05, 0.10, 0.30, 0.60, 1.00]
    print(f"{'a':>6}  {'ln_a':>8}  {'alpha_M':>10}  {'alpha_B':>10}  {'alpha_T':>10}")
    for a in scale_factors:
        ln_a = math.log(a)
        print(f"{a:>6.2f}  {ln_a:>8.3f}  {alpha_M(ln_a):>10.5f}  "
              f"{alpha_B(ln_a):>10.5f}  {alpha_T():>10.5f}")


if __name__ == "__main__":  # pragma: no cover
    main()
