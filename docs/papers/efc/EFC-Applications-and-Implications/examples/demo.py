#!/usr/bin/env python3
"""Demo for EFC Applications and Implications package.

Shows how to access application domains, list predictions, and
generate summaries of cross-domain EFC implications.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.applications import ApplicationDomain, EFCApplications


def main() -> None:
    apps = EFCApplications()

    # List all domains
    print("Registered EFC application domains:")
    for name in apps.list_domains():
        print(f"  - {name}")

    # Detailed summary
    print()
    print(apps.summary())

    # Access a single domain
    print()
    astro = apps.get_domain("Astrophysics")
    if astro:
        print(f"Astrophysics predictions: {len(astro.predictions)}")
        for p in astro.predictions:
            print(f"  * {p}")

    # Add a custom domain
    apps.add_domain(ApplicationDomain(
        name="Climate Science",
        description="Climate dynamics viewed as planetary-scale energy flow",
        key_mechanisms=["Atmospheric entropy gradients"],
        predictions=["Storm systems follow Ef channelling patterns"],
    ))
    print(f"\nDomains after addition: {apps.list_domains()}")
    print("\nDone.")


if __name__ == "__main__":
    main()
