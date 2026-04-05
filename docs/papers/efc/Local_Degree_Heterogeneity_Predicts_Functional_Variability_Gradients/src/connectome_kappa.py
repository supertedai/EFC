"""Centrifugal Entropy Score (kappa) — Python implementation.

Implements the hub-to-periphery functional variability gradient analysis
from the Human Connectome Project and individual DSI connectomes.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31940370
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CentrifugalEntropyScore:
    """The centrifugal entropy score kappa = <S_hub> / <S_periph>.

    Quantifies the directional structure of functional variability
    across the connectome. kappa > 1 means hubs have higher entropy
    than peripheral regions.

    Attributes:
        hub_threshold: Fraction of top-degree nodes classified as hubs (default: 0.10).
        periphery_threshold: Fraction of bottom-degree nodes classified as peripheral (default: 0.30).
    """
    hub_threshold: float = 0.10
    periphery_threshold: float = 0.30

    def classify_nodes(self, degrees: List[float]) -> Tuple[List[int], List[int]]:
        """Classify nodes into hub and peripheral sets by weighted degree.

        Args:
            degrees: Weighted degree for each node.

        Returns:
            Tuple of (hub_indices, periphery_indices).
        """
        n = len(degrees)
        ranked = sorted(range(n), key=lambda i: degrees[i], reverse=True)
        n_hub = max(1, int(n * self.hub_threshold))
        n_periph = max(1, int(n * self.periphery_threshold))
        hub_idx = ranked[:n_hub]
        periph_idx = ranked[-n_periph:]
        return hub_idx, periph_idx

    def compute(self, entropy_values: List[float], degrees: List[float]) -> float:
        """Compute kappa from entropy values and degree ranking.

        Args:
            entropy_values: Entropy proxy S_i for each node.
            degrees: Weighted degree for each node.

        Returns:
            Centrifugal entropy score kappa.
        """
        hub_idx, periph_idx = self.classify_nodes(degrees)
        s_hub = sum(entropy_values[i] for i in hub_idx) / len(hub_idx)
        s_periph = sum(entropy_values[i] for i in periph_idx) / len(periph_idx)
        if s_periph == 0:
            return float('inf')
        return s_hub / s_periph

    def interpret(self, kappa: float) -> str:
        """Interpret kappa value."""
        if kappa > 1:
            return "Centrifugal gradient: hubs have higher functional variability"
        elif kappa < 1:
            return "Centripetal gradient: periphery has higher functional variability"
        else:
            return "No gradient: entropy uniformly distributed"


@dataclass
class ConnectomeAnalysis:
    """Analysis results from a connectome dataset.

    Stores kappa values across atlases or subjects, along with
    structural feature correlations.
    """
    dataset_name: str
    n_entries: int
    kappa_values: List[float] = field(default_factory=list)
    degree_ratios: List[float] = field(default_factory=list)
    fiedler_values: List[float] = field(default_factory=list)

    @property
    def kappa_mean(self) -> float:
        return sum(self.kappa_values) / len(self.kappa_values) if self.kappa_values else 0.0

    @property
    def kappa_std(self) -> float:
        if len(self.kappa_values) < 2:
            return 0.0
        mean = self.kappa_mean
        var = sum((k - mean) ** 2 for k in self.kappa_values) / (len(self.kappa_values) - 1)
        return math.sqrt(var)

    @property
    def kappa_cv(self) -> float:
        """Coefficient of variation."""
        mean = self.kappa_mean
        return self.kappa_std / mean if mean > 0 else 0.0

    @property
    def all_above_unity(self) -> bool:
        return all(k > 1.0 for k in self.kappa_values)

    def pearson_r(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """Compute Pearson correlation coefficient and approximate p-value."""
        n = len(x)
        if n < 3:
            return 0.0, 1.0
        mx = sum(x) / n
        my = sum(y) / n
        sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        sxx = sum((xi - mx) ** 2 for xi in x)
        syy = sum((yi - my) ** 2 for yi in y)
        if sxx == 0 or syy == 0:
            return 0.0, 1.0
        r = sxy / math.sqrt(sxx * syy)
        # Approximate p-value via t-distribution
        if abs(r) >= 1.0:
            return r, 0.0
        t = r * math.sqrt((n - 2) / (1 - r * r))
        # Simple approximation for two-tailed p
        p = 2.0 * math.exp(-0.717 * abs(t) - 0.416 * t * t) if abs(t) < 6 else 0.0001
        return r, p


@dataclass
class NetworkFeatures:
    """Structural network features computed for each atlas/subject.

    Features from Table 2 of the paper.
    """
    name: str
    fiedler_eigenvalue: float = 0.0
    modularity_q: float = 0.0
    clustering_coeff: float = 0.0
    degree_ratio: float = 0.0
    participation_ratio: float = 0.0
    betweenness_ratio: float = 0.0
    hub_mean_degree: float = 0.0
    periph_mean_degree: float = 0.0

    def feature_dict(self) -> dict:
        return {
            "fiedler_eigenvalue": self.fiedler_eigenvalue,
            "modularity_q": self.modularity_q,
            "clustering_coeff": self.clustering_coeff,
            "degree_ratio": self.degree_ratio,
            "participation_ratio": self.participation_ratio,
            "betweenness_ratio": self.betweenness_ratio,
            "hub_mean_degree": self.hub_mean_degree,
            "periph_mean_degree": self.periph_mean_degree,
        }


@dataclass
class ThresholdSensitivity:
    """Threshold sensitivity analysis (Section 3.5).

    Tests all combinations of hub (5-20%) and periphery (20-40%)
    thresholds to verify robustness of kappa > 1.
    """
    hub_thresholds: List[float] = field(default_factory=lambda: [0.05, 0.08, 0.10, 0.12, 0.15, 0.20])
    periphery_thresholds: List[float] = field(default_factory=lambda: [0.20, 0.25, 0.30, 0.35, 0.40])

    def run(self, entropy_values: List[float], degrees: List[float]) -> dict:
        """Test all threshold combinations."""
        results = []
        for ht in self.hub_thresholds:
            for pt in self.periphery_thresholds:
                scorer = CentrifugalEntropyScore(hub_threshold=ht, periphery_threshold=pt)
                kappa = scorer.compute(entropy_values, degrees)
                results.append({
                    "hub_threshold": ht,
                    "periphery_threshold": pt,
                    "kappa": kappa,
                    "above_unity": kappa > 1.0,
                })
        kappas = [r["kappa"] for r in results]
        mean_k = sum(kappas) / len(kappas)
        std_k = math.sqrt(sum((k - mean_k)**2 for k in kappas) / (len(kappas) - 1))
        return {
            "n_combinations": len(results),
            "all_above_unity": all(r["above_unity"] for r in results),
            "kappa_range": [min(kappas), max(kappas)],
            "kappa_mean": mean_k,
            "kappa_cv": std_k / mean_k if mean_k > 0 else 0,
            "results": results,
        }


@dataclass
class BiomarkerPredictions:
    """Clinical predictions for kappa as a biomarker (Section 4.5).

    Testable predictions for psychiatric, ageing, and pharmacological
    applications of the centrifugal entropy score.
    """

    @staticmethod
    def predictions() -> List[dict]:
        return [
            {
                "domain": "Schizophrenia",
                "prediction": "kappa reduced due to hub dysconnection",
                "mechanism": "Reduced hub degree → reduced degree heterogeneity → lower kappa",
                "testable_with": "OpenNeuro schizophrenia datasets"
            },
            {
                "domain": "Major Depressive Disorder",
                "prediction": "kappa altered in disorder-specific manner",
                "mechanism": "Anterior vs posterior hub dissociation",
                "testable_with": "HCP clinical datasets"
            },
            {
                "domain": "Ageing",
                "prediction": "kappa reduced with age",
                "mechanism": "White matter degeneration preferentially affects long-range hub connections",
                "testable_with": "HCP-Aging"
            },
            {
                "domain": "Psychedelics",
                "prediction": "kappa increased under psychedelic compounds",
                "mechanism": "Psychedelics increase global neural entropy, preferentially in hubs",
                "testable_with": "Carhart-Harris et al. datasets"
            },
        ]


# ─── Convenience functions ─────────────────────────────────────────

def compute_kappa(entropy_values: List[float], degrees: List[float],
                  hub_threshold: float = 0.10, periphery_threshold: float = 0.30) -> float:
    """Compute centrifugal entropy score kappa = <S_hub> / <S_periph>."""
    scorer = CentrifugalEntropyScore(hub_threshold, periphery_threshold)
    return scorer.compute(entropy_values, degrees)


def compute_fc_cv(fc_row: List[float]) -> float:
    """Compute FC coefficient of variation for a single node. Eq. (2)."""
    abs_vals = [abs(x) for x in fc_row]
    mean_abs = sum(abs_vals) / len(abs_vals) if abs_vals else 0
    if mean_abs == 0:
        return 0.0
    mean_fc = sum(fc_row) / len(fc_row)
    var = sum((x - mean_fc) ** 2 for x in fc_row) / len(fc_row)
    std = math.sqrt(var)
    return std / mean_abs


def compute_structural_log_degree(degree: float) -> float:
    """Compute structural log-degree entropy proxy. Eq. (3)."""
    return math.log(1 + degree)


def compute_degree_ratio(degrees: List[float],
                         hub_threshold: float = 0.10,
                         periphery_threshold: float = 0.30) -> float:
    """Compute hub-to-periphery degree ratio D_ratio = <deg_hub> / <deg_periph>."""
    scorer = CentrifugalEntropyScore(hub_threshold, periphery_threshold)
    hub_idx, periph_idx = scorer.classify_nodes(degrees)
    hub_mean = sum(degrees[i] for i in hub_idx) / len(hub_idx)
    periph_mean = sum(degrees[i] for i in periph_idx) / len(periph_idx)
    if periph_mean == 0:
        return float('inf')
    return hub_mean / periph_mean
