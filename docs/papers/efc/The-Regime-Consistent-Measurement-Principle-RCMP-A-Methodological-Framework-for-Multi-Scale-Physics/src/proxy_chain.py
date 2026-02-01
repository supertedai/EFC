"""
Proxy Chain

Documents and manages the transformation chain from raw measurements
to derived quantities, tracking uncertainties at each step.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import math


@dataclass
class ProxyStep:
    """
    Single step in a proxy chain.

    Attributes:
        name: Name of this step (e.g., "rotation_velocity")
        layer: Epistemic layer (L0, L1, L2, L3)
        sigma: Uncertainty introduced at this step
        transformation: Description of transformation applied
        assumptions: List of assumptions required
        parameters: Parameters used in transformation
    """
    name: str
    layer: str
    sigma: float = 0.0
    transformation: Optional[str] = None
    assumptions: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "layer": self.layer,
            "sigma": self.sigma,
            "transformation": self.transformation,
            "assumptions": self.assumptions,
            "parameters": self.parameters,
            "description": self.description,
        }


class ProxyChain:
    """
    Manages and documents a proxy chain for RCMP compliance.

    A proxy chain tracks the sequence of transformations from raw
    measurement (L0) through to final derived/theoretical quantities,
    accumulating uncertainty at each step.

    Example:
        chain = ProxyChain()

        chain.add_step(
            name="spectral_velocity",
            layer="L0",
            sigma=0.01,
            description="Raw spectral line measurement"
        )

        chain.add_step(
            name="rotation_velocity",
            layer="L1",
            sigma=0.02,
            transformation="inclination_correction",
            assumptions=["thin disk", "circular orbits"]
        )

        chain.add_step(
            name="centripetal_acceleration",
            layer="L2",
            sigma=0.05,
            transformation="g = V²/R",
            assumptions=["known distance"]
        )

        print(f"Total uncertainty: {chain.total_uncertainty()}")
        print(f"Chain depth: {chain.depth()}")
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize a proxy chain.

        Args:
            name: Optional name for this chain
        """
        self.name = name
        self.steps: List[ProxyStep] = []

    def add_step(
        self,
        name: str,
        layer: str,
        sigma: float = 0.0,
        transformation: Optional[str] = None,
        assumptions: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> "ProxyChain":
        """
        Add a step to the proxy chain.

        Args:
            name: Step name
            layer: Epistemic layer (L0, L1, L2, L3)
            sigma: Uncertainty added at this step
            transformation: Transformation description
            assumptions: Required assumptions
            parameters: Parameters involved
            description: Human-readable description

        Returns:
            Self for method chaining
        """
        step = ProxyStep(
            name=name,
            layer=layer,
            sigma=sigma,
            transformation=transformation,
            assumptions=assumptions or [],
            parameters=parameters or [],
            description=description,
        )
        self.steps.append(step)
        return self

    def total_uncertainty(self, correlation: float = 0.0) -> float:
        """
        Calculate total propagated uncertainty.

        Args:
            correlation: Average correlation between steps (0 = independent)

        Returns:
            Total uncertainty (quadrature sum with optional correlation)
        """
        if not self.steps:
            return 0.0

        sigmas = [s.sigma for s in self.steps]

        # Quadrature sum
        sum_sq = sum(s**2 for s in sigmas)

        # Add correlation terms if specified
        if correlation > 0:
            for i, si in enumerate(sigmas):
                for j, sj in enumerate(sigmas):
                    if i < j:
                        sum_sq += 2 * correlation * si * sj

        return math.sqrt(sum_sq)

    def depth(self) -> int:
        """
        Return the number of steps in the chain.
        """
        return len(self.steps)

    def max_layer(self) -> Optional[str]:
        """
        Return the highest epistemic layer reached.
        """
        if not self.steps:
            return None

        layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
        max_layer_step = max(
            self.steps,
            key=lambda s: layer_order.get(s.layer, 0)
        )
        return max_layer_step.layer

    def all_assumptions(self) -> List[str]:
        """
        Return all assumptions across the chain.
        """
        assumptions = []
        for step in self.steps:
            assumptions.extend(step.assumptions)
        return list(set(assumptions))  # Remove duplicates

    def all_parameters(self) -> List[str]:
        """
        Return all parameters across the chain.
        """
        parameters = []
        for step in self.steps:
            parameters.extend(step.parameters)
        return list(set(parameters))

    def to_dict(self) -> Dict[str, Any]:
        """
        Export chain as dictionary.
        """
        return {
            "name": self.name,
            "steps": [s.to_dict() for s in self.steps],
            "total_uncertainty": self.total_uncertainty(),
            "depth": self.depth(),
            "max_layer": self.max_layer(),
            "all_assumptions": self.all_assumptions(),
        }

    def summary(self) -> str:
        """
        Generate human-readable summary.
        """
        lines = [
            f"Proxy Chain: {self.name or 'Unnamed'}",
            f"{'=' * 40}",
            f"Depth: {self.depth()} steps",
            f"Max Layer: {self.max_layer()}",
            f"Total σ: {self.total_uncertainty():.4f}",
            "",
            "Steps:",
        ]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"  {i}. {step.name} ({step.layer})")
            if step.transformation:
                lines.append(f"      Transformation: {step.transformation}")
            lines.append(f"      σ = {step.sigma}")
            if step.assumptions:
                lines.append(f"      Assumptions: {', '.join(step.assumptions)}")

        lines.append("")
        lines.append(f"Total assumptions: {len(self.all_assumptions())}")

        return "\n".join(lines)

    def validate(self) -> List[str]:
        """
        Validate the proxy chain for RCMP compliance.

        Returns:
            List of warnings/issues (empty if valid)
        """
        issues = []

        if not self.steps:
            issues.append("Empty proxy chain")
            return issues

        # Check for layer ordering
        layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
        prev_layer = -1
        for step in self.steps:
            current = layer_order.get(step.layer, -1)
            if current < prev_layer:
                issues.append(
                    f"Layer regression: {step.name} is {step.layer} "
                    f"but follows higher layer"
                )
            prev_layer = current

        # Check for missing uncertainties
        for step in self.steps:
            if step.sigma == 0 and step.layer != "L0":
                issues.append(
                    f"Step '{step.name}' has zero uncertainty (unusual for {step.layer})"
                )

        # Check for missing assumptions in derived layers
        for step in self.steps:
            if step.layer in ["L2", "L3"] and not step.assumptions:
                issues.append(
                    f"Step '{step.name}' ({step.layer}) has no documented assumptions"
                )

        return issues

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProxyChain":
        """
        Create chain from dictionary.
        """
        chain = cls(name=data.get("name"))
        for step_data in data.get("steps", []):
            chain.add_step(**step_data)
        return chain
