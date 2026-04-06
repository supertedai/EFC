"""
COSMOS-Web Galaxy Abundance Analysis Module
=============================================
Implements galaxy sample analysis, halo mass function comparison,
abundance excess computation, and redshift bin analysis.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import math


class GalaxySample:
    """A sample of galaxies from the COSMOS-Web catalog.

    Parameters
    ----------
    galaxies : list of dict
        Each dict should contain at least 'z_phot' and 'mass_med' keys.
    mass_cut : float
        Minimum log stellar mass (default: 9.0 for log M*/Msun > 9).
    """

    def __init__(self, galaxies, mass_cut=9.0):
        self.galaxies = list(galaxies)
        self.mass_cut = float(mass_cut)

    @property
    def n_total(self):
        """Total number of galaxies in the sample."""
        return len(self.galaxies)

    def above_mass_cut(self):
        """Return galaxies above the mass cut."""
        return [g for g in self.galaxies if g.get("mass_med", 0) >= self.mass_cut]

    def in_redshift_range(self, z_min, z_max):
        """Return galaxies within a redshift range.

        Parameters
        ----------
        z_min : float
            Minimum redshift (inclusive).
        z_max : float
            Maximum redshift (exclusive).

        Returns
        -------
        list of dict
            Galaxies in the specified range.
        """
        return [
            g for g in self.galaxies
            if z_min <= g.get("z_phot", 0) < z_max
        ]

    def count_in_bin(self, z_min, z_max):
        """Count galaxies in a redshift bin above mass cut."""
        return len([
            g for g in self.galaxies
            if z_min <= g.get("z_phot", 0) < z_max
            and g.get("mass_med", 0) >= self.mass_cut
        ])

    def redshift_distribution(self, bins):
        """Compute galaxy counts per redshift bin.

        Parameters
        ----------
        bins : list of tuple
            List of (z_min, z_max) bin edges.

        Returns
        -------
        list of dict
            Count per bin.
        """
        result = []
        for z_min, z_max in bins:
            count = self.count_in_bin(z_min, z_max)
            result.append({
                "z_min": z_min,
                "z_max": z_max,
                "z_mid": (z_min + z_max) / 2.0,
                "count": count,
            })
        return result

    def __repr__(self):
        return f"GalaxySample(n={self.n_total}, mass_cut={self.mass_cut})"


class HaloMassFunction:
    """Simplified halo mass function for LCDM predictions.

    Provides expected galaxy counts as a function of redshift
    under halo-limited assumptions.

    Parameters
    ----------
    survey_area_deg2 : float
        Survey area in square degrees.
    mass_threshold : float
        Minimum halo mass log(M/Msun) for galaxy hosting.
    """

    def __init__(self, survey_area_deg2=0.54, mass_threshold=11.0):
        self.survey_area_deg2 = float(survey_area_deg2)
        self.mass_threshold = float(mass_threshold)

    def predicted_count(self, z_mid, dz=1.0):
        """Predict galaxy count at a given redshift.

        Simplified model: count drops exponentially at high z.

        Parameters
        ----------
        z_mid : float
            Central redshift of the bin.
        dz : float
            Bin width in redshift.

        Returns
        -------
        float
            Predicted galaxy count.
        """
        # Normalization based on COSMOS-Web area and typical HMF
        n0 = 5000.0 * self.survey_area_deg2
        # Exponential suppression at high z
        return n0 * dz * math.exp(-0.8 * (z_mid - 3.0))

    def predicted_density(self, z_mid):
        """Predict comoving number density at redshift z.

        Returns density in arbitrary units (normalized to z=3).
        """
        return math.exp(-0.8 * (z_mid - 3.0))

    def __repr__(self):
        return (
            f"HaloMassFunction(area={self.survey_area_deg2} deg^2, "
            f"M_thresh={self.mass_threshold})"
        )


class AbundanceExcess:
    """Compute the excess of observed galaxies over LCDM predictions.

    Parameters
    ----------
    observed : int or float
        Observed galaxy count.
    predicted : float
        LCDM-predicted galaxy count.
    """

    def __init__(self, observed, predicted):
        self.observed = float(observed)
        self.predicted = float(predicted)

    @property
    def excess_factor(self):
        """Ratio of observed to predicted counts."""
        if self.predicted <= 0:
            return float("inf")
        return self.observed / self.predicted

    @property
    def excess_sigma(self):
        """Approximate significance assuming Poisson statistics.

        sigma = (observed - predicted) / sqrt(predicted)
        """
        if self.predicted <= 0:
            return float("inf")
        return (self.observed - self.predicted) / math.sqrt(self.predicted)

    @property
    def is_excess(self):
        """Whether observed exceeds predicted."""
        return self.observed > self.predicted

    def __repr__(self):
        return (
            f"AbundanceExcess(obs={self.observed:.0f}, "
            f"pred={self.predicted:.1f}, "
            f"factor={self.excess_factor:.1f}x)"
        )


class RedshiftBin:
    """Analysis of a single redshift bin.

    Parameters
    ----------
    z_min : float
        Lower redshift boundary.
    z_max : float
        Upper redshift boundary.
    observed_count : int
        Observed galaxy count in this bin.
    predicted_count : float
        LCDM-predicted count for this bin.
    """

    def __init__(self, z_min, z_max, observed_count, predicted_count):
        self.z_min = float(z_min)
        self.z_max = float(z_max)
        self.observed_count = int(observed_count)
        self.predicted_count = float(predicted_count)

    @property
    def z_mid(self):
        """Central redshift of the bin."""
        return (self.z_min + self.z_max) / 2.0

    @property
    def dz(self):
        """Bin width."""
        return self.z_max - self.z_min

    @property
    def excess(self):
        """AbundanceExcess object for this bin."""
        return AbundanceExcess(self.observed_count, self.predicted_count)

    @property
    def log_excess(self):
        """Log10 of excess factor (useful for plotting)."""
        ef = self.excess.excess_factor
        if ef <= 0:
            return float("-inf")
        return math.log10(ef)

    def __repr__(self):
        return (
            f"RedshiftBin(z=[{self.z_min:.1f}, {self.z_max:.1f}], "
            f"obs={self.observed_count}, "
            f"excess={self.excess.excess_factor:.1f}x)"
        )
