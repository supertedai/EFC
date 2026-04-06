"""EFC Applications and Implications - classes for cross-domain EFC applications.

This module implements parameter and concept access for the paper examining
how Energy-Flow Cosmology extends into practical, theoretical, and
cross-domain applications.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ApplicationDomain:
    """Represents a domain where EFC concepts apply."""

    name: str
    description: str
    key_mechanisms: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    observables: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a human-readable summary of this application domain."""
        lines = [f"Domain: {self.name}", f"  Description: {self.description}"]
        if self.key_mechanisms:
            lines.append("  Key mechanisms:")
            for m in self.key_mechanisms:
                lines.append(f"    - {m}")
        if self.predictions:
            lines.append("  Predictions:")
            for p in self.predictions:
                lines.append(f"    - {p}")
        if self.observables:
            lines.append("  Observables:")
            for o in self.observables:
                lines.append(f"    - {o}")
        return "\n".join(lines)


class EFCApplications:
    """Access class for EFC applications and their cross-domain implications.

    Provides structured access to the domains, concepts, and predictions
    described in the EFC Applications and Implications paper.
    """

    def __init__(self) -> None:
        self.domains: Dict[str, ApplicationDomain] = {}
        self._init_default_domains()

    def _init_default_domains(self) -> None:
        """Populate the default application domains from the paper."""
        self.add_domain(ApplicationDomain(
            name="Astrophysics",
            description="Energy-flow dynamics replacing dark matter/energy explanations",
            key_mechanisms=["Entropy-gradient driven structure formation",
                            "Energy-flow field (Ef) as gravitational proxy"],
            predictions=["Galaxy rotation curves explained by Ef gradients",
                         "Large-scale structure from entropy flow networks"],
            observables=["Rotation curve profiles", "Cluster mass distributions"],
        ))
        self.add_domain(ApplicationDomain(
            name="Biology",
            description="Living systems as entropy-flow optimisers",
            key_mechanisms=["Metabolic energy flow channelling",
                            "Self-organisation via entropy gradients"],
            predictions=["Metabolic scaling follows Ef constraints",
                         "Ecosystem energy budgets obey EFC flow rules"],
            observables=["Metabolic rates", "Ecosystem energy throughput"],
        ))
        self.add_domain(ApplicationDomain(
            name="Technology",
            description="Engineering systems analysed through energy-flow principles",
            key_mechanisms=["Entropy management in computation",
                            "Energy flow efficiency optimisation"],
            predictions=["Landauer limit derivable from EFC framework",
                         "Heat dissipation patterns follow entropy gradients"],
            observables=["Computational energy costs", "Thermal profiles"],
        ))
        self.add_domain(ApplicationDomain(
            name="Information Systems",
            description="Information processing as a manifestation of energy flow",
            key_mechanisms=["Information entropy as physical entropy analogue",
                            "Data flow as energy-flow proxy"],
            predictions=["Information channel capacity bounded by Ef",
                         "Network topology reflects entropy flow optimisation"],
            observables=["Channel capacities", "Network efficiency metrics"],
        ))

    def add_domain(self, domain: ApplicationDomain) -> None:
        """Register an application domain."""
        self.domains[domain.name] = domain

    def get_domain(self, name: str) -> Optional[ApplicationDomain]:
        """Retrieve a domain by name."""
        return self.domains.get(name)

    def list_domains(self) -> List[str]:
        """Return names of all registered domains."""
        return list(self.domains.keys())

    def summary(self) -> str:
        """Return a full summary of all application domains."""
        lines = ["EFC Applications and Implications", "=" * 40]
        for domain in self.domains.values():
            lines.append("")
            lines.append(domain.summary())
        return "\n".join(lines)
