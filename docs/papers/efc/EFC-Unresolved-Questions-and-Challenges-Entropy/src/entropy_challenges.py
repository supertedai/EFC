"""
EFC -- Unresolved Questions and Challenges: Entropy
=====================================================
Tracks and analyses open problems in the role of entropy within
Energy-Flow Cosmology: theoretical, observational, mathematical,
and computational gaps.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OpenQuestion:
    """A single unresolved question in EFC entropy theory.

    Parameters
    ----------
    id : str
        Short identifier.
    category : str
        One of: 'theoretical', 'observational', 'mathematical', 'computational'.
    title : str
        Brief title of the question.
    description : str
        Detailed description.
    severity : int
        Severity / importance level (1=low, 5=critical).
    status : str
        One of: 'open', 'partial', 'addressed'.
    """

    id: str
    category: str
    title: str
    description: str
    severity: int = 3
    status: str = "open"

    @property
    def is_critical(self) -> bool:
        return self.severity >= 4

    @property
    def is_resolved(self) -> bool:
        return self.status == "addressed"


@dataclass
class EntropyGap:
    """A quantified gap in entropy modelling.

    Parameters
    ----------
    name : str
        Gap identifier.
    expected_value : float
        Theoretically expected entropy value / rate.
    observed_value : float
        Currently observed or estimated value.
    unit : str
        Physical unit.
    """

    name: str
    expected_value: float
    observed_value: float
    unit: str = ""

    @property
    def absolute_gap(self) -> float:
        return abs(self.expected_value - self.observed_value)

    @property
    def relative_gap(self) -> float:
        if self.expected_value == 0:
            return float("inf") if self.observed_value != 0 else 0.0
        return self.absolute_gap / abs(self.expected_value)

    @property
    def gap_label(self) -> str:
        r = self.relative_gap
        if r < 0.1:
            return "minor"
        elif r < 0.5:
            return "moderate"
        else:
            return "major"


@dataclass
class ChallengeTracker:
    """Track and summarise a collection of open questions and gaps."""

    questions: List[OpenQuestion] = field(default_factory=list)
    gaps: List[EntropyGap] = field(default_factory=list)

    def n_open(self) -> int:
        return sum(1 for q in self.questions if q.status == "open")

    def n_critical(self) -> int:
        return sum(1 for q in self.questions if q.is_critical)

    def by_category(self) -> dict:
        cats: dict = {}
        for q in self.questions:
            cats.setdefault(q.category, []).append(q.id)
        return cats

    def mean_severity(self) -> float:
        if not self.questions:
            return 0.0
        return sum(q.severity for q in self.questions) / len(self.questions)

    def major_gaps(self) -> List[EntropyGap]:
        return [g for g in self.gaps if g.gap_label == "major"]

    def summary(self) -> dict:
        return {
            "n_questions": len(self.questions),
            "n_open": self.n_open(),
            "n_critical": self.n_critical(),
            "mean_severity": round(self.mean_severity(), 2),
            "categories": self.by_category(),
            "n_gaps": len(self.gaps),
            "n_major_gaps": len(self.major_gaps()),
        }
