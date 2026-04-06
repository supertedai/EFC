#!/usr/bin/env python3
"""
Demo: EFC Unresolved Questions and Challenges -- Entropy
=========================================================
Loads open questions and entropy gaps and prints a challenge summary.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.entropy_challenges import OpenQuestion, EntropyGap, ChallengeTracker


def main() -> None:
    data_path = os.path.join(_pkg, "data", "entropy_challenges.json")
    with open(data_path) as f:
        raw = json.load(f)

    questions = [OpenQuestion(**q) for q in raw["questions"]]
    gaps = [EntropyGap(**g) for g in raw["gaps"]]
    tracker = ChallengeTracker(questions=questions, gaps=gaps)

    print("=== EFC Entropy Challenges Demo ===\n")

    print("Open Questions:")
    for q in questions:
        crit = " [CRITICAL]" if q.is_critical else ""
        print(f"  {q.id} ({q.category}) sev={q.severity} [{q.status}]{crit}")
        print(f"    {q.title}")

    print("\nEntropy Gaps:")
    for g in gaps:
        print(f"  {g.name}: expected={g.expected_value} vs observed={g.observed_value} "
              f"{g.unit}  => {g.gap_label} (rel={g.relative_gap:.2f})")

    print("\n--- Summary ---")
    summary = tracker.summary()
    for k, v in summary.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
