"""
Unification Analysis

Complete analysis demonstrating that the Hubble tension and RAR
arise from the same mechanism: entropy-driven gravity modification.
"""

import math
from dataclasses import dataclass
from typing import Optional

from .entropy_mapping import EntropyMapping
from .phase_calculator import PhaseCalculator
from .mond_interpolation import MONDInterpolator, compute_aG_from_mond
from .h0_predictor import H0Predictor, derive_aG_from_h0_tension


@dataclass
class UnificationResult:
    """Result of the unification analysis."""
    # From H₀ tension
    aG_cosmological: float
    aH0_cosmological: float

    # From MOND
    aG_galactic: float
    g_ratio_used: float

    # Comparison
    discrepancy_percent: float
    discrepancy_acceptable: bool

    # Prediction
    h0_predicted: float
    h0_observed: float
    prediction_accuracy_percent: float

    # Verdict
    unified: bool

    def __str__(self) -> str:
        status = "UNIFIED" if self.unified else "NOT UNIFIED"
        return (
            f"Unification Result: {status}\n"
            f"  a_G (cosmological): {self.aG_cosmological:.4f}\n"
            f"  a_G (galactic): {self.aG_galactic:.4f}\n"
            f"  Discrepancy: {self.discrepancy_percent:.1f}%\n"
            f"  H₀ predicted: {self.h0_predicted:.1f} km/s/Mpc\n"
            f"  H₀ observed: {self.h0_observed:.1f} km/s/Mpc\n"
            f"  Prediction accuracy: {self.prediction_accuracy_percent:.1f}%\n"
        )


class UnificationAnalysis:
    """
    Complete unification analysis.

    Demonstrates that:
    1. a_G from H₀ tension ≈ a_G from MOND transition
    2. The Friedmann constraint a_H₀ = ½ a_G holds
    3. H₀ can be predicted from galaxy data

    Example:
        analysis = UnificationAnalysis()
        result = analysis.run()
        print(result)
    """

    def __init__(
        self,
        h0_cmb: float = 67.4,
        h0_local: float = 73.0,
        g_ratio: float = 5.0,
        delta_phi: float = 1.71,
        discrepancy_threshold: float = 20.0
    ):
        """
        Initialize the analysis.

        Args:
            h0_cmb: CMB H₀ (Planck)
            h0_local: Local H₀ (SH0ES)
            g_ratio: g_bar/a₀ for MOND (transition zone)
            delta_phi: Phase difference
            discrepancy_threshold: Max acceptable discrepancy (%)
        """
        self.h0_cmb = h0_cmb
        self.h0_local = h0_local
        self.g_ratio = g_ratio
        self.delta_phi = delta_phi
        self.discrepancy_threshold = discrepancy_threshold

        # Initialize components
        self.mond = MONDInterpolator(delta_phi=delta_phi)
        self.h0_predictor = H0Predictor(
            h0_cmb=h0_cmb, h0_local=h0_local, delta_phi=delta_phi
        )

    def run(self) -> UnificationResult:
        """
        Run the complete unification analysis.

        Returns:
            UnificationResult with all findings
        """
        # Step 1: Get a_G from H₀ tension
        aG_cosmo = derive_aG_from_h0_tension(
            self.h0_local, self.h0_cmb, self.delta_phi
        )
        aH0_cosmo = aG_cosmo / 2

        # Step 2: Get a_G from MOND transition zone
        aG_galactic = compute_aG_from_mond(self.g_ratio, self.delta_phi)

        # Step 3: Compare
        discrepancy = abs(aG_galactic - aG_cosmo) / aG_cosmo * 100
        acceptable = discrepancy <= self.discrepancy_threshold

        # Step 4: Predict H₀ from MOND a_G
        prediction = self.h0_predictor.predict(aG_galactic)

        # Step 5: Verdict
        # Unified if discrepancy is acceptable AND prediction is close
        unified = acceptable and prediction.deviation_percent < 5.0

        return UnificationResult(
            aG_cosmological=aG_cosmo,
            aH0_cosmological=aH0_cosmo,
            aG_galactic=aG_galactic,
            g_ratio_used=self.g_ratio,
            discrepancy_percent=discrepancy,
            discrepancy_acceptable=acceptable,
            h0_predicted=prediction.h0_predicted,
            h0_observed=self.h0_local,
            prediction_accuracy_percent=100 - prediction.deviation_percent,
            unified=unified,
        )

    def full_report(self) -> str:
        """Generate complete analysis report."""
        result = self.run()

        # Build report
        lines = [
            "=" * 60,
            "UNIFIED ORIGIN OF RAR AND HUBBLE TENSION",
            "Complete Analysis Report",
            "=" * 60,
            "",
            "STEP 1: Derive a_G from Hubble Tension",
            "-" * 40,
            f"  H₀ (CMB/Planck): {self.h0_cmb} km/s/Mpc",
            f"  H₀ (Local/SH0ES): {self.h0_local} km/s/Mpc",
            f"  ln(H₀_local/H₀_CMB) = {math.log(self.h0_local/self.h0_cmb):.4f}",
            f"  ΔΦ = {self.delta_phi}",
            f"",
            f"  a_H₀ = ln(ratio) / ΔΦ = {result.aH0_cosmological:.4f}",
            f"  a_G = 2 × a_H₀ = {result.aG_cosmological:.4f}",
            "",
            "STEP 2: Derive a_G from MOND Transition Zone",
            "-" * 40,
            f"  g_bar/a₀ = {self.g_ratio}",
        ]

        mond_point = self.mond.get_point(self.g_ratio)
        lines.extend([
            f"  μ = {mond_point.mu:.3f}",
            f"  μ⁻¹ = {mond_point.mu_inverse:.3f}",
            f"  ln(μ⁻¹) = {mond_point.ln_mu_inv:.4f}",
            f"",
            f"  a_G = ln(μ⁻¹) / ΔΦ = {result.aG_galactic:.4f}",
            "",
            "STEP 3: Compare a_G Values",
            "-" * 40,
            f"  a_G (cosmological): {result.aG_cosmological:.4f}",
            f"  a_G (galactic):     {result.aG_galactic:.4f}",
            f"  Discrepancy:        {result.discrepancy_percent:.1f}%",
            f"  Acceptable (<{self.discrepancy_threshold}%): {'Yes' if result.discrepancy_acceptable else 'No'}",
            "",
            "STEP 4: Predict H₀ from MOND a_G",
            "-" * 40,
            f"  Using a_G = {result.aG_galactic:.4f} from MOND",
            f"  a_H₀ = ½ a_G = {result.aG_galactic/2:.4f}",
            f"",
            f"  H₀_pred = {self.h0_cmb} × exp({result.aG_galactic/2:.4f} × {self.delta_phi})",
            f"  H₀_pred = {result.h0_predicted:.1f} km/s/Mpc",
            f"",
            f"  H₀_observed = {result.h0_observed:.1f} km/s/Mpc",
            f"  Deviation = {100 - result.prediction_accuracy_percent:.1f}%",
            "",
            "=" * 60,
            f"VERDICT: {'UNIFIED' if result.unified else 'NOT UNIFIED'}",
            "=" * 60,
        ])

        if result.unified:
            lines.extend([
                "",
                "The Hubble tension and radial acceleration relation",
                "arise from the SAME MECHANISM: entropy-driven gravity",
                "modification with a_G ≈ 0.1",
            ])

        return "\n".join(lines)


def run_full_analysis() -> UnificationResult:
    """Run full analysis with default parameters."""
    analysis = UnificationAnalysis()
    return analysis.run()


def print_full_report() -> None:
    """Print complete analysis report."""
    analysis = UnificationAnalysis()
    print(analysis.full_report())
