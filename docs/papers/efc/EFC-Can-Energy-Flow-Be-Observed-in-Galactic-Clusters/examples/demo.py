#!/usr/bin/env python3
"""Demo for EFC Galactic Clusters package.

Shows how to model galaxy clusters, compute lensing deflections with
Ef corrections, and list predicted observable signatures.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.galactic_clusters import GalaxyCluster, ClusterObservatory


def main() -> None:
    obs = ClusterObservatory()

    # Add example clusters
    coma = GalaxyCluster(
        name="Coma Cluster",
        mass_solar=1.2e15,
        temperature_keV=8.2,
        redshift=0.0231,
        ef_magnitude_W_m2=1e-12,
    )
    perseus = GalaxyCluster(
        name="Perseus Cluster",
        mass_solar=6.6e14,
        temperature_keV=6.0,
        redshift=0.0179,
        ef_magnitude_W_m2=8e-13,
    )
    obs.add_cluster(coma)
    obs.add_cluster(perseus)

    print(obs.summary())

    # Lensing deflection at 500 kpc impact parameter
    for cluster in [coma, perseus]:
        defl = cluster.lensing_deflection_arcsec(impact_param_kpc=500)
        print(f"\n{cluster.name} lensing deflection at 500 kpc: {defl:.4f} arcsec")

    print("\nDone.")


if __name__ == "__main__":
    main()
