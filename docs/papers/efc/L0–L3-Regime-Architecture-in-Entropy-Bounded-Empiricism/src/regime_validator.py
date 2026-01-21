#!/usr/bin/env python3
"""
Regime Validator for L0-L3 Architecture
Provides tools for checking regime validity and detecting regime leakage
"""

import json
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Regime(Enum):
    """Enumeration of L0-L3 regimes"""
    L0 = "latent"
    L1 = "stable_active"
    L2 = "complex_active"
    L3 = "residual"


class InferenceType(Enum):
    """Types of inference operations"""
    CAUSAL_HISTORY = "causal_history"
    ACTIVE_DYNAMICS = "active_dynamics"
    CONFIGURATION_ANALYSIS = "configuration_analysis"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    LINEAR_PREDICTION = "linear_prediction"
    NONLINEAR_PREDICTION = "nonlinear_prediction"
    HISTORICAL_RECONSTRUCTION = "historical_reconstruction"


class RegimeValidator:
    """Validates inference operations against regime constraints"""
    
    def __init__(self, regime_definitions_path: str = "data/regime_definitions.json",
                 transition_definitions_path: str = "data/regime_transitions.json"):
        """
        Initialize validator with regime and transition definitions
        
        Args:
            regime_definitions_path: Path to regime_definitions.json
            transition_definitions_path: Path to regime_transitions.json
        """
        with open(regime_definitions_path) as f:
            self.regime_data = json.load(f)
        
        with open(transition_definitions_path) as f:
            self.transition_data = json.load(f)
        
        self.regimes = self.regime_data["regimes"]
    
    def validate_inference(self, regime: Regime, inference_type: InferenceType) -> Tuple[bool, str]:
        """
        Check if an inference type is valid in a given regime
        
        Args:
            regime: The regime being analyzed
            inference_type: The type of inference operation
        
        Returns:
            Tuple of (is_valid, explanation)
        """
        regime_name = regime.name
        regime_info = self.regimes[regime_name]
        validity_rules = regime_info["inference_validity"]
        
        # Map inference types to validity checks
        checks = {
            InferenceType.CAUSAL_HISTORY: self._check_causal_history,
            InferenceType.ACTIVE_DYNAMICS: self._check_active_dynamics,
            InferenceType.CONFIGURATION_ANALYSIS: self._check_configuration,
            InferenceType.STRUCTURAL_ANALYSIS: self._check_structural,
            InferenceType.LINEAR_PREDICTION: self._check_linear_prediction,
            InferenceType.NONLINEAR_PREDICTION: self._check_nonlinear_prediction,
            InferenceType.HISTORICAL_RECONSTRUCTION: self._check_historical
        }
        
        check_func = checks.get(inference_type)
        if check_func:
            return check_func(regime, validity_rules)
        
        return False, f"Unknown inference type: {inference_type}"
    
    def _check_causal_history(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if causal history inference is valid"""
        if regime == Regime.L0:
            return False, "L0 is latent configuration without causal history"
        elif regime in [Regime.L1, Regime.L2]:
            return True, "Active regimes have valid causal histories"
        elif regime == Regime.L3:
            return False, "L3 is residual structure; causal inference requires active dynamics"
        return False, "Regime not recognized"
    
    def _check_active_dynamics(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if active dynamics inference is valid"""
        if regime in [Regime.L1, Regime.L2]:
            return True, "Active regimes support dynamics inference"
        elif regime == Regime.L0:
            return False, "L0 is latent; no active dynamics present"
        elif regime == Regime.L3:
            return False, "L3 is residual; active dynamics have ceased"
        return False, "Regime not recognized"
    
    def _check_configuration(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if configuration analysis is valid"""
        # Configuration analysis is valid in all regimes
        return True, "Configuration analysis valid in all regimes"
    
    def _check_structural(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if structural analysis is valid"""
        if regime in [Regime.L1, Regime.L2, Regime.L3]:
            return True, "Structural analysis valid when structure exists"
        elif regime == Regime.L0:
            return True, "L0 has latent structure that can be analyzed"
        return True, "Structural analysis generally valid"
    
    def _check_linear_prediction(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if linear prediction is valid"""
        if regime == Regime.L1:
            return True, "L1 stable dynamics support linear approximations"
        elif regime == Regime.L2:
            return False, "L2 non-linear dynamics require non-linear models"
        elif regime in [Regime.L0, Regime.L3]:
            return False, "No active dynamics to predict"
        return False, "Regime not recognized"
    
    def _check_nonlinear_prediction(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if non-linear prediction is valid"""
        if regime == Regime.L2:
            return True, "L2 complex dynamics require non-linear models"
        elif regime == Regime.L1:
            return True, "Non-linear models valid in L1 (though not necessary)"
        elif regime in [Regime.L0, Regime.L3]:
            return False, "No active dynamics to predict"
        return False, "Regime not recognized"
    
    def _check_historical(self, regime: Regime, rules: List[str]) -> Tuple[bool, str]:
        """Check if historical reconstruction is valid"""
        if regime == Regime.L3:
            return True, "L3 residual structure permits limited historical reconstruction"
        elif regime in [Regime.L1, Regime.L2]:
            return True, "Active regimes support historical analysis"
        elif regime == Regime.L0:
            return False, "L0 has no history; it is latent configuration"
        return False, "Regime not recognized"
    
    def detect_regime_leakage(self, source_regime: Regime, target_regime: Regime,
                             inference_type: InferenceType) -> Tuple[bool, str]:
        """
        Detect if applying inference from source_regime to target_regime is regime leakage
        
        Args:
            source_regime: Regime where inference model was developed
            target_regime: Regime where model is being applied
            inference_type: Type of inference being performed
        
        Returns:
            Tuple of (is_leakage, explanation)
        """
        source_valid, source_msg = self.validate_inference(source_regime, inference_type)
        target_valid, target_msg = self.validate_inference(target_regime, inference_type)
        
        if source_valid and not target_valid:
            return True, (f"REGIME LEAKAGE DETECTED: {inference_type.value} is valid in "
                         f"{source_regime.name} but invalid in {target_regime.name}. "
                         f"Reason: {target_msg}")
        
        if not source_valid and target_valid:
            return False, (f"Model from {source_regime.name} was already invalid; "
                          f"no new leakage in {target_regime.name}")
        
        if source_valid and target_valid:
            return False, f"{inference_type.value} valid in both {source_regime.name} and {target_regime.name}"
        
        return False, f"{inference_type.value} invalid in both regimes"
    
    def get_regime_info(self, regime: Regime) -> Dict:
        """Get full information about a regime"""
        return self.regimes[regime.name]
    
    def get_transition_info(self, from_regime: Regime, to_regime: Regime) -> Optional[Dict]:
        """Get information about transition between regimes"""
        transition_key = f"{from_regime.name}_to_{to_regime.name}"
        return self.transition_data["transitions"].get(transition_key)


# Example usage
if __name__ == "__main__":
    validator = RegimeValidator()
    
    print("=== L0-L3 Regime Validator ===\n")
    
    # Test 1: Check if causal history inference is valid in L0
    valid, msg = validator.validate_inference(Regime.L0, InferenceType.CAUSAL_HISTORY)
    print(f"Test 1: Causal history in L0")
    print(f"Valid: {valid}")
    print(f"Explanation: {msg}\n")
    
    # Test 2: Check if active dynamics inference is valid in L2
    valid, msg = validator.validate_inference(Regime.L2, InferenceType.ACTIVE_DYNAMICS)
    print(f"Test 2: Active dynamics in L2")
    print(f"Valid: {valid}")
    print(f"Explanation: {msg}\n")
    
    # Test 3: Detect regime leakage
    is_leakage, msg = validator.detect_regime_leakage(
        Regime.L1, Regime.L3, InferenceType.LINEAR_PREDICTION
    )
    print(f"Test 3: Applying L1 linear prediction model to L3")
    print(f"Leakage detected: {is_leakage}")
    print(f"Explanation: {msg}\n")
    
    # Test 4: Get regime info
    l2_info = validator.get_regime_info(Regime.L2)
    print(f"Test 4: L2 Regime Information")
    print(f"Name: {l2_info['name']}")
    print(f"Description: {l2_info['description']}")
    print(f"Energy flow: {l2_info['dynamics']['energy_flow']}")
