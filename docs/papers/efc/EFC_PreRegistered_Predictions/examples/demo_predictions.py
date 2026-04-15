"""Print the sealed EFC pre-registered benchmarks and acceptance windows."""
from __future__ import annotations

from efc_preregistered_predictions_src.predictions import (  # type: ignore  # noqa: E402
    frozen_parameters,
    predicted_shifts,
    VERDICT_WINDOWS,
)


def main() -> None:
    print("Frozen EFC benchmark parameters:")
    for name, value in frozen_parameters().items():
        print(f"  {name:>10} = {value}")

    print("\nPredicted shifts vs LCDM (%) on Euclid DR1 scales:")
    for name, value in predicted_shifts().items():
        print(f"  {name:>10}: {value:+.2f}")

    print("\nAcceptance windows (outside window => kill criterion triggered):")
    for name, (lo, hi) in VERDICT_WINDOWS.items():
        print(f"  {name:>25}: [{lo:.2f}, {hi:.2f}]")


if __name__ == "__main__":  # pragma: no cover
    main()
