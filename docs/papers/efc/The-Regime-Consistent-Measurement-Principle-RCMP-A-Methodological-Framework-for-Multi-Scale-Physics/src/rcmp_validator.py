"""
RCMP Validator

Validates analyses against the Regime-Consistent Measurement Principle.
Checks the five core principles: driver proximity, regime tagging,
proxy accounting, coordinate humility, and cross-validation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationStatus(Enum):
    """Status of RCMP validation."""
    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"


@dataclass
class ChecklistItem:
    """Single item in RCMP validation checklist."""
    name: str
    requirement: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of RCMP validation."""
    is_valid: bool
    status: ValidationStatus
    checklist: List[ChecklistItem]
    summary: str
    warnings: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            "RCMP Validation Report",
            "=" * 22,
            f"Status: {self.status.value.upper()}",
            "",
            "Checklist:"
        ]
        for item in self.checklist:
            mark = "✓" if item.passed else "✗"
            lines.append(f"  {mark} {item.name}: {item.message}")

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        lines.append("")
        lines.append(f"Summary: {self.summary}")
        return "\n".join(lines)


@dataclass
class Driver:
    """Physical driver specification."""
    name: str
    regime: str
    boundary_condition: Optional[str] = None
    primary_variable: Optional[str] = None


class RCMPValidator:
    """
    Validates analyses against RCMP requirements.

    The five core principles checked:
    1. Driver Proximity - physical driver is explicit
    2. Regime Tagging - measurements are labeled with regimes
    3. Proxy Accounting - transformation chain is documented
    4. Coordinate Humility - coordinate assumptions are stated
    5. Cross-Validation - multiple proxy chains are compared
    """

    def __init__(self):
        self.checklist_items = [
            ("driver_identified", "Physical driver explicit for each regime"),
            ("regime_tagged", "Each data point labeled with dominant regime"),
            ("proxy_chain_documented", "Full transformation sequence recorded"),
            ("uncertainties_propagated", "Each transformation adds to error budget"),
            ("cross_validation_performed", "Multiple proxy chains compared"),
        ]

    def validate(
        self,
        driver: Optional[Driver] = None,
        proxy_chain: Optional[Any] = None,
        measurements: Optional[List[Dict]] = None,
        cross_validation_chains: Optional[List[Any]] = None,
        coordinate_system: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate an analysis against RCMP requirements.

        Args:
            driver: Physical driver specification
            proxy_chain: Primary proxy chain documentation
            measurements: List of measurements with regime tags
            cross_validation_chains: Additional proxy chains for cross-validation
            coordinate_system: Stated coordinate system

        Returns:
            ValidationResult with checklist and status
        """
        checklist = []
        warnings = []

        # 1. Driver Proximity
        driver_check = self._check_driver(driver)
        checklist.append(driver_check)

        # 2. Regime Tagging
        regime_check = self._check_regime_tagging(measurements)
        checklist.append(regime_check)

        # 3. Proxy Accounting
        proxy_check = self._check_proxy_chain(proxy_chain)
        checklist.append(proxy_check)

        # 4. Uncertainties Propagated
        uncertainty_check = self._check_uncertainties(proxy_chain)
        checklist.append(uncertainty_check)

        # 5. Cross-Validation
        cross_val_check = self._check_cross_validation(
            proxy_chain, cross_validation_chains
        )
        checklist.append(cross_val_check)
        if not cross_val_check.passed:
            warnings.append("Single proxy chain - add alternative for full validation")

        # Coordinate humility warning if not stated
        if coordinate_system is None:
            warnings.append("Coordinate system not explicitly stated")

        # Determine overall status
        passed_count = sum(1 for c in checklist if c.passed)
        total_count = len(checklist)

        if passed_count == total_count:
            status = ValidationStatus.VALID
            is_valid = True
            summary = "All RCMP requirements satisfied"
        elif passed_count >= 3:
            status = ValidationStatus.PARTIAL
            is_valid = False
            summary = f"Partial compliance ({passed_count}/{total_count} checks passed)"
        else:
            status = ValidationStatus.INVALID
            is_valid = False
            summary = f"RCMP validation failed ({passed_count}/{total_count} checks passed)"

        return ValidationResult(
            is_valid=is_valid,
            status=status,
            checklist=checklist,
            summary=summary,
            warnings=warnings,
        )

    def _check_driver(self, driver: Optional[Driver]) -> ChecklistItem:
        """Check if physical driver is identified."""
        if driver is None:
            return ChecklistItem(
                name="Driver identified",
                requirement="Physical driver explicit for each regime",
                passed=False,
                message="No driver specified",
            )

        if driver.name and driver.regime:
            return ChecklistItem(
                name="Driver identified",
                requirement="Physical driver explicit for each regime",
                passed=True,
                message=f"{driver.name} in {driver.regime} regime",
                details={"driver": driver.name, "regime": driver.regime},
            )

        return ChecklistItem(
            name="Driver identified",
            requirement="Physical driver explicit for each regime",
            passed=False,
            message="Incomplete driver specification",
        )

    def _check_regime_tagging(
        self, measurements: Optional[List[Dict]]
    ) -> ChecklistItem:
        """Check if measurements have regime tags."""
        if measurements is None:
            return ChecklistItem(
                name="Regime tagged",
                requirement="Each data point labeled with dominant regime",
                passed=False,
                message="No measurements provided",
            )

        tagged_count = sum(
            1 for m in measurements
            if m.get("regime") or m.get("layer")
        )
        total = len(measurements)

        if tagged_count == total and total > 0:
            return ChecklistItem(
                name="Regime tagged",
                requirement="Each data point labeled with dominant regime",
                passed=True,
                message=f"All {total} measurements tagged",
            )

        return ChecklistItem(
            name="Regime tagged",
            requirement="Each data point labeled with dominant regime",
            passed=False,
            message=f"Only {tagged_count}/{total} measurements tagged",
        )

    def _check_proxy_chain(self, proxy_chain: Optional[Any]) -> ChecklistItem:
        """Check if proxy chain is documented."""
        if proxy_chain is None:
            return ChecklistItem(
                name="Proxy chain documented",
                requirement="Full transformation sequence recorded",
                passed=False,
                message="No proxy chain provided",
            )

        # Check if it's a ProxyChain object or dict
        if hasattr(proxy_chain, 'steps'):
            step_count = len(proxy_chain.steps)
        elif isinstance(proxy_chain, dict) and 'steps' in proxy_chain:
            step_count = len(proxy_chain['steps'])
        else:
            step_count = 0

        if step_count > 0:
            return ChecklistItem(
                name="Proxy chain documented",
                requirement="Full transformation sequence recorded",
                passed=True,
                message=f"{step_count} transformation steps documented",
            )

        return ChecklistItem(
            name="Proxy chain documented",
            requirement="Full transformation sequence recorded",
            passed=False,
            message="Empty proxy chain",
        )

    def _check_uncertainties(self, proxy_chain: Optional[Any]) -> ChecklistItem:
        """Check if uncertainties are propagated."""
        if proxy_chain is None:
            return ChecklistItem(
                name="Uncertainties propagated",
                requirement="Each transformation adds to error budget",
                passed=False,
                message="No proxy chain to check",
            )

        # Check for uncertainty information
        has_uncertainties = False
        if hasattr(proxy_chain, 'total_uncertainty'):
            has_uncertainties = proxy_chain.total_uncertainty() > 0
        elif hasattr(proxy_chain, 'steps'):
            has_uncertainties = any(
                hasattr(s, 'sigma') and s.sigma > 0
                for s in proxy_chain.steps
            )

        if has_uncertainties:
            return ChecklistItem(
                name="Uncertainties propagated",
                requirement="Each transformation adds to error budget",
                passed=True,
                message="Uncertainty budget documented",
            )

        return ChecklistItem(
            name="Uncertainties propagated",
            requirement="Each transformation adds to error budget",
            passed=False,
            message="No uncertainty information in proxy chain",
        )

    def _check_cross_validation(
        self,
        primary_chain: Optional[Any],
        additional_chains: Optional[List[Any]],
    ) -> ChecklistItem:
        """Check if cross-validation is performed."""
        chain_count = 0
        if primary_chain is not None:
            chain_count = 1
        if additional_chains:
            chain_count += len(additional_chains)

        if chain_count >= 2:
            return ChecklistItem(
                name="Cross-validation performed",
                requirement="Multiple proxy chains compared",
                passed=True,
                message=f"{chain_count} proxy chains available for comparison",
            )

        return ChecklistItem(
            name="Cross-validation performed",
            requirement="Multiple proxy chains compared",
            passed=False,
            message="Single proxy chain only",
        )
