"""WP3 - First Empirical Slice Through the Regime Response Surface R(k,S).

Classes for the RSD-based empirical mapping of R(k,S), structural
maturity S(z), model comparison (LCDM vs R(k,S) slice), and data
handling for BOSS, eBOSS, and DESI measurements.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

from .wp3_rks_slice import (
    RSDMeasurement,
    WP3Trajectory,
    ModelComparison,
)
