"""
EFC vs ΛCDM: Complete Kill-Test (v6 final)

Package exports:
    - KRhoBridge, theta_rho, R_k    (K(ρ) bridge)
    - GravSlip, slip_scan           (slip calibration)
    - run_all_probes, probe_result  (six-probe kill-test suite)
    - aggregate_runs, delta_chi2    (cobaya minimize aggregator)

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
DOI:    10.6084/m9.figshare.31964847
License: CC-BY-4.0
"""

from .k_rho_bridge import KRhoBridge, theta_rho, R_k
from .gravitational_slip import GravSlip, slip_scan
from .kill_test_suite import run_all_probes, probe_result
from .cobaya_minimize import aggregate_runs, delta_chi2

__all__ = [
    "KRhoBridge",
    "theta_rho",
    "R_k",
    "GravSlip",
    "slip_scan",
    "run_all_probes",
    "probe_result",
    "aggregate_runs",
    "delta_chi2",
]

__version__ = "6.0"
__doi__ = "10.6084/m9.figshare.31964847"
