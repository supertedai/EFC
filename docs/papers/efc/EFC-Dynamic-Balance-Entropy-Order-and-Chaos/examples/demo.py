#!/usr/bin/env python3
"""Demo for EFC Dynamic Balance: Entropy, Order, and Chaos package.

Shows system states, their regimes, balance indices, and phase transitions.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dynamic_balance import DynamicBalance, SystemState


def main() -> None:
    db = DynamicBalance()

    print(db.summary())

    # Show balance index for each state
    print("\nBalance indices:")
    for s in db.states:
        print(f"  {s.label}: B = {s.balance_index:.4f} ({s.regime})")

    # Add a custom state
    star = SystemState("Main-sequence star", 0.6, 1e6, 1e26)
    db.states.append(star)
    print(f"\nAdded: {star.summary()}")
    print(f"New most balanced: {db.most_balanced().label}")
    print("\nDone.")


if __name__ == "__main__":
    main()
