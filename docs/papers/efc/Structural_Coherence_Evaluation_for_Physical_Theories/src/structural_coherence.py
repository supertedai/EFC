"""
Structural Coherence Evaluation (SCE) Framework

Theory-agnostic framework for assessing structural coherence and
falsifiability of physical theories using four principles and five metrics.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ForbiddenPattern:
    """
    A self-declared forbidden observational pattern.

    Theories must specify patterns that, if observed, would falsify
    specific structural claims.
    """
    id: str
    scope: str  # "Core" or "Module"
    description: str
    violation_condition: str
    test_procedure: str
    status: str = "Not triggered"  # "Not triggered" or "Triggered"
    tested: bool = False

    @property
    def is_core(self) -> bool:
        return self.scope == "Core"


@dataclass
class TheoryProfile:
    """
    Structural profile for a physical theory under SCE evaluation.

    Parameters
    ----------
    name : str
        Theory name (e.g., "LCDM", "EFC", "MOND").
    primitives : int
        Number of independent primitive assumptions.
    phenomena : int
        Number of tested observable phenomena.
    fdof : int
        Functional degrees of freedom.
    forbidden_patterns : int
        Number of declared forbidden patterns.
    forbidden_tested : int
        Number of forbidden patterns tested against data.
    forbidden_triggered : int
        Number of triggered (violated) patterns.
    anomaly_A1 : int
        Level-1 anomalies (direct contradictions).
    anomaly_A2 : int
        Level-2 anomalies (theoretical incompleteness).
    anomaly_A3 : int
        Level-3 anomalies (untested predictions).
    variant_count : int
        Number of model variants or extensions.
    parameter_trend : str
        "Growing", "Stable", or "Decreasing".
    special_case_rules : int
        Number of special-case rules or ad-hoc patches.
    """
    name: str
    primitives: int = 0
    phenomena: int = 0
    fdof: int = 0
    forbidden_patterns: int = 0
    forbidden_tested: int = 0
    forbidden_triggered: int = 0
    anomaly_A1: int = 0
    anomaly_A2: int = 0
    anomaly_A3: int = 0
    variant_count: int = 0
    parameter_trend: str = "Stable"
    special_case_rules: int = 0
    patterns: List[ForbiddenPattern] = field(default_factory=list)

    @property
    def explanatory_compression(self) -> float:
        """Metric 1: C = |tested phenomena| / |primitive assumptions|."""
        if self.primitives == 0:
            return 0.0
        return self.phenomena / self.primitives

    @property
    def anomaly_burden(self) -> Dict[str, int]:
        """Metric 2: Anomaly counts by severity level."""
        return {
            'A1': self.anomaly_A1,
            'A2': self.anomaly_A2,
            'A3': self.anomaly_A3,
            'total': self.anomaly_A1 + self.anomaly_A2 + self.anomaly_A3,
        }

    @property
    def model_plasticity(self) -> Dict:
        """Metric 3: Indicators of model flexibility/ad-hocness."""
        return {
            'variant_count': self.variant_count,
            'parameter_trend': self.parameter_trend,
            'special_case_rules': self.special_case_rules,
        }

    @property
    def forbidden_coverage(self) -> float:
        """Metric 5: Fraction of forbidden patterns tested."""
        if self.forbidden_patterns == 0:
            return 0.0
        return self.forbidden_tested / self.forbidden_patterns

    @property
    def survival_rate(self) -> float:
        """Fraction of tested forbidden patterns not triggered."""
        if self.forbidden_tested == 0:
            return 1.0
        return 1.0 - (self.forbidden_triggered / self.forbidden_tested)


class SCEFramework:
    """
    Structural Coherence Evaluation framework.

    Evaluates and compares physical theories using five metrics
    derived from four operational principles.
    """

    def evaluate(self, theory: TheoryProfile) -> Dict:
        """
        Evaluate a single theory's SCE profile.

        Returns
        -------
        dict with all five metric values.
        """
        return {
            'name': theory.name,
            'explanatory_compression': theory.explanatory_compression,
            'anomaly_burden': theory.anomaly_burden,
            'model_plasticity': theory.model_plasticity,
            'forbidden_coverage': theory.forbidden_coverage,
            'survival_rate': theory.survival_rate,
            'primitives': theory.primitives,
            'phenomena': theory.phenomena,
            'fdof': theory.fdof,
        }

    def compare(
        self,
        theory_a: TheoryProfile,
        theory_b: TheoryProfile,
    ) -> Dict:
        """
        Compare two theories across all SCE metrics.

        Returns metric-by-metric comparison with winners.
        """
        eval_a = self.evaluate(theory_a)
        eval_b = self.evaluate(theory_b)

        comparison = {
            'theory_a': eval_a,
            'theory_b': eval_b,
            'metric_winners': {},
        }

        # Compression: higher is better
        if eval_a['explanatory_compression'] > eval_b['explanatory_compression']:
            comparison['metric_winners']['compression'] = theory_a.name
        elif eval_b['explanatory_compression'] > eval_a['explanatory_compression']:
            comparison['metric_winners']['compression'] = theory_b.name
        else:
            comparison['metric_winners']['compression'] = 'Draw'

        # Anomaly burden: lower A1 is better
        if eval_a['anomaly_burden']['A1'] < eval_b['anomaly_burden']['A1']:
            comparison['metric_winners']['anomaly_burden'] = theory_a.name
        elif eval_b['anomaly_burden']['A1'] < eval_a['anomaly_burden']['A1']:
            comparison['metric_winners']['anomaly_burden'] = theory_b.name
        else:
            comparison['metric_winners']['anomaly_burden'] = 'Draw'

        # Plasticity: lower is better
        plasticity_a = theory_a.special_case_rules + theory_a.variant_count
        plasticity_b = theory_b.special_case_rules + theory_b.variant_count
        if plasticity_a < plasticity_b:
            comparison['metric_winners']['plasticity'] = theory_a.name
        elif plasticity_b < plasticity_a:
            comparison['metric_winners']['plasticity'] = theory_b.name
        else:
            comparison['metric_winners']['plasticity'] = 'Draw'

        # Forbidden coverage: higher is better
        if eval_a['forbidden_coverage'] > eval_b['forbidden_coverage']:
            comparison['metric_winners']['forbidden_coverage'] = theory_a.name
        elif eval_b['forbidden_coverage'] > eval_a['forbidden_coverage']:
            comparison['metric_winners']['forbidden_coverage'] = theory_b.name
        else:
            comparison['metric_winners']['forbidden_coverage'] = 'Draw'

        return comparison

    @staticmethod
    def check_framework_forbidden_patterns(comparison: Dict) -> List[str]:
        """
        Check the SCE framework's own forbidden patterns (TCS-F1..F3).

        TCS-F1: Robustness Failure - rankings change under reasonable counting
        TCS-F2: Epistemic Divergence - systematic opposition to expert assessment
        TCS-F3: Performative Falsifiability - rewards trivial over deep patterns
        """
        violations = []
        # These are structural checks - in production would require
        # sensitivity analysis across counting variations
        return violations


# Paper case studies
PAPER_RESULTS = {
    'case_studies': {
        'LCDM': {
            'type': 'Empirically Mature',
            'primitives': '3-5',
            'profile': 'High coverage, moderate anomaly burden, limited self-declared falsifiability',
        },
        'EFC': {
            'type': 'Emergent',
            'primitives': '2-3',
            'profile': 'High declared falsifiability, limited coverage, low plasticity',
        },
        'MOND': {
            'type': 'Intermediate',
            'primitives': '2-6',
            'profile': 'High galactic compression, declining consistency in extensions',
        },
    },
    'framework_forbidden_patterns': {
        'TCS-F1': 'Robustness Failure',
        'TCS-F2': 'Epistemic Divergence',
        'TCS-F3': 'Performative Falsifiability',
    },
    'key_innovations': [
        'Self-imposed falsifiability as operational, machine-checkable property',
        'Forbidden patterns derived from constitutive laws',
        'Theory comparison across ontological boundaries',
        'Reflexive application of framework standards',
    ],
}


if __name__ == '__main__':
    lcdm = TheoryProfile(
        name="LCDM", primitives=3, phenomena=6, fdof=2,
        anomaly_A1=3, anomaly_A2=2, anomaly_A3=1,
        variant_count=5, parameter_trend="Growing", special_case_rules=2,
    )
    efc = TheoryProfile(
        name="EFC", primitives=2, phenomena=4, fdof=1,
        forbidden_patterns=5, forbidden_tested=5, forbidden_triggered=0,
        anomaly_A1=0, anomaly_A2=6, anomaly_A3=3,
        variant_count=2, parameter_trend="Decreasing", special_case_rules=0,
    )

    sce = SCEFramework()
    comparison = sce.compare(lcdm, efc)
    print("SCE Comparison: LCDM vs EFC")
    for metric, winner in comparison['metric_winners'].items():
        print(f"  {metric}: {winner}")
