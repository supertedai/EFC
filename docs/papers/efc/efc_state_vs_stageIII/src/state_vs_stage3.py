"""
EFC vs Stage-III Cosmology State Assessment

Evaluates EFC's position in the post-tension weak-lensing landscape,
with SCE O-layer/M-layer classification.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class WeakLensingMeasurement:
    """A weak-lensing S8 measurement."""
    survey: str
    probe: str
    S8: float
    S8_err_plus: float
    S8_err_minus: float
    reference: str
    year: int

    @property
    def S8_err(self) -> float:
        return (self.S8_err_plus + self.S8_err_minus) / 2.0

    def pull_from(self, sigma8_model: float) -> float:
        """Compute pull relative to a model sigma8 value."""
        return (sigma8_model - self.S8) / self.S8_err


class SCELayerClassification:
    """
    SCE O-layer / M-layer classification for weak-lensing quantities.

    O-layer: Observation-native (minimal theory input)
    M-layer: Mapping-dependent (passes through model pipeline)
    T-layer: Theory consumption
    """

    O_LAYER = {
        'name': 'Observation-Native Ontology',
        'examples': [
            'Shear two-point correlations xi_pm(theta)',
            'Convergence power spectra C_l^kk',
            'Tomographic bin statistics',
        ],
    }

    M_LAYER = {
        'name': 'Mapping Transparency',
        'S8_assumptions': [
            'GR lensing kernel (Sigma = 1)',
            'GR linear perturbation theory',
            'Friedmann + LCDM background',
            'LCDM transfer function',
        ],
    }

    T_LAYER = {
        'name': 'Theory Consumption',
        'description': 'Theories consume M-layer products as compressed constraints',
    }

    @staticmethod
    def classify_observable(name: str) -> str:
        """Classify an observable into O/M/T layer."""
        o_observables = ['xi_plus', 'xi_minus', 'C_l_kk', 'shear', 'convergence']
        m_observables = ['S8', 'sigma8', 'Omega_m', 'w0', 'wa']

        for obs in o_observables:
            if obs in name.lower():
                return 'O-layer'
        for obs in m_observables:
            if obs in name.lower():
                return 'M-layer'
        return 'Unknown'


class StageIIIAssessment:
    """
    Stage-III observational update and EFC impact assessment.

    Evaluates EFC's sigma8=0.805 prediction against converging
    Stage-III weak-lensing measurements.
    """

    EFC_SIGMA8 = 0.805
    EFC_BETA = 0.08

    def __init__(self):
        self.measurements = self._load_measurements()
        self.sce = SCELayerClassification()

    def _load_measurements(self) -> List[WeakLensingMeasurement]:
        return [
            WeakLensingMeasurement(
                survey='KiDS Legacy', probe='cosmic shear',
                S8=0.815, S8_err_plus=0.016, S8_err_minus=0.021,
                reference='Wright et al. (2025), A&A 703, A158', year=2025,
            ),
            WeakLensingMeasurement(
                survey='HSC Y3 + DESI', probe='DESI-calibrated n(z)',
                S8=0.805, S8_err_plus=0.018, S8_err_minus=0.018,
                reference='Choppin de Janvry et al. (2025), arXiv:2511.18134', year=2025,
            ),
            WeakLensingMeasurement(
                survey='KiDS+DES+HSC combined', probe='combined WL',
                S8=0.813, S8_err_plus=0.009, S8_err_minus=0.010,
                reference='Choppin de Janvry et al. (2025)', year=2025,
            ),
            WeakLensingMeasurement(
                survey='CMB lensing combined', probe='CMB lensing',
                S8=0.828, S8_err_plus=0.012, S8_err_minus=0.012,
                reference='Choppin de Janvry et al. (2025)', year=2025,
            ),
        ]

    def evaluate_efc_position(self) -> Dict:
        """Evaluate EFC's sigma8 prediction against Stage-III data."""
        results = {
            'efc_sigma8': self.EFC_SIGMA8,
            'efc_beta': self.EFC_BETA,
            'measurements': [],
        }

        for m in self.measurements:
            pull = m.pull_from(self.EFC_SIGMA8)
            results['measurements'].append({
                'survey': m.survey,
                'S8': m.S8,
                'S8_err': f"+{m.S8_err_plus}/-{m.S8_err_minus}",
                'pull_from_efc': f"{pull:+.2f}sigma",
                'consistent': abs(pull) < 2.0,
            })

        all_consistent = all(m['consistent'] for m in results['measurements'])
        results['sigma8_comparison'] = (
            'EFC sigma8=0.805 consistent with all Stage-III measurements'
            if all_consistent else
            'Some measurements in tension with EFC prediction'
        )

        return results

    def narrative_update(self) -> Dict:
        """Return the narrative transition."""
        return {
            'deprecated': 'EFC resolves a 3sigma S8 tension',
            'current': (
                "EFC's background coupling yields sigma8=0.805 consistent with "
                "converging Stage-III lensing; Sigma(k,z) becomes model-selection "
                "diagnostic for scale-dependent matter-lensing response"
            ),
            'category_from': 'Alternative model that explains a tension',
            'category_to': 'Alternative model that matches standard cosmology and predicts second-order deviations',
        }

    def stage_iv_tests(self) -> List[Dict]:
        """Discriminating tests for Stage-IV surveys."""
        return [
            {'test': 'Scale-dependent growth f(k,z)', 'efc': 'Entropy-gradient modulation', 'lcdm': 'Scale-independent', 'data': 'Euclid, DESI DR3'},
            {'test': 'Lensing vs dynamical mass', 'efc': 'Sigma != 1 at low-z', 'lcdm': 'Sigma = 1 everywhere', 'data': 'Euclid clusters, Rubin'},
            {'test': 'ISW cross-correlation', 'efc': 'Cancellation from mu/mu_prime', 'lcdm': 'Standard ISW', 'data': 'DESI x Planck/ACT'},
            {'test': 'Cluster abundance N(M,z)', 'efc': 'Modified growth function', 'lcdm': 'Standard Press-Schechter', 'data': 'eROSITA, SPT-3G'},
        ]


# Paper results for reference
PAPER_RESULTS = {
    'stage_iii_observations': {
        'kids_legacy': {'S8': 0.815, 'err_plus': 0.016, 'err_minus': 0.021, 'planck_consistency': '0.73sigma'},
        'hsc_y3_desi': {'S8': 0.805, 'err': 0.018},
        'combined_wl': {'S8': 0.813, 'err_plus': 0.009, 'err_minus': 0.010},
        'cmb_lensing': {'S8': 0.828, 'err': 0.012},
    },
    'efc_impact': {
        'sigma8': 0.805,
        'beta': 0.08,
        'updated_role': 'Matches converging Stage-III amplitude',
        'status': 'Strengthened',
    },
    'narrative': {
        'deprecated': 'EFC resolves a 3sigma S8 tension',
        'current': 'EFC sigma8=0.805 consistent with converging Stage-III landscape',
    },
    'strengths': [
        'beta=0.08 -> sigma8=0.805 matches data without tuning',
        'Growth suppression via Hubble friction (correct mechanism)',
        'One transition function T(z) for all regimes',
        'Five pre-registered falsification criteria, none triggered',
    ],
}


if __name__ == '__main__':
    assessment = StageIIIAssessment()
    result = assessment.evaluate_efc_position()
    print(result['sigma8_comparison'])
