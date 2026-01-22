"""
Response Protocols for Validity-Aware AI

Defines the response protocols for each regime (L1/L2/L3) and
provides system prompts and constraints for LLM generation.

Part of: Validity-Aware AI
DOI: 10.6084/m9.figshare.31122970
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .regime_classifier import Regime


@dataclass
class ResponseProtocol:
    """
    Response protocol defining how the system should respond in a given regime.
    """
    name: str
    regime: Regime
    system_prompt_addition: str
    constraints: Dict[str, Any]
    user_indicator: str
    description: str
    
    def get_full_system_prompt(self, base_prompt: str = "") -> str:
        """Combine base prompt with protocol-specific additions."""
        if not self.system_prompt_addition:
            return base_prompt
        return f"{base_prompt}\n\n{self.system_prompt_addition}"


# Protocol definitions

PROTOCOL_L1 = ResponseProtocol(
    name="standard",
    regime=Regime.L1,
    system_prompt_addition="",  # No additions for L1
    constraints={
        "point_estimates": True,
        "require_citations": False,
        "require_conflict_disclosure": False,
        "confidence_ceiling": 1.0,
        "allow_predictions": True
    },
    user_indicator="✓ High confidence domain",
    description="Standard inference mode. Domain is stable and well-defined."
)

PROTOCOL_L2 = ResponseProtocol(
    name="uncertainty_aware",
    regime=Regime.L2,
    system_prompt_addition="""EPISTEMIC CONSTRAINT: This query falls in regime L2 (contested domain).

Your response must follow these rules:
- Do NOT make unqualified assertions
- Present competing interpretations where they exist
- Include uncertainty estimates for any quantitative claims
- Maximum confidence level for any claim: 70%
- Cite sources that disagree with each other explicitly
- Use hedging language: "evidence suggests", "one interpretation is", "it appears that"

Remember: Epistemic honesty requires acknowledging what we don't know with confidence.""",
    constraints={
        "point_estimates": False,
        "require_citations": True,
        "require_conflict_disclosure": True,
        "confidence_ceiling": 0.7,
        "allow_predictions": True  # But with uncertainty
    },
    user_indicator="⚠ Contested domain—multiple interpretations exist",
    description="Uncertainty-aware mode. Domain has contested relationships or evolving knowledge."
)

PROTOCOL_L2_L3_TRANSITION = ResponseProtocol(
    name="degraded",
    regime=Regime.L2,  # Still technically L2 but approaching L3
    system_prompt_addition="""EPISTEMIC CONSTRAINT: This query approaches regime L3 (epistemic collapse).

CRITICAL RULES:
- Do NOT provide point estimates or confident answers
- Explain WHY the knowledge domain is unstable
- Offer to retrieve historical information instead
- Suggest ways the user could narrow their query to a more stable subdomain
- Be explicit: "I cannot provide a reliable answer because..."

The knowledge structure for this query shows high entropy. Confident inference is not valid here.""",
    constraints={
        "point_estimates": False,
        "require_citations": True,
        "require_conflict_disclosure": True,
        "confidence_ceiling": 0.3,
        "allow_predictions": False
    },
    user_indicator="⚠⚠ Unstable domain—treat with caution",
    description="Degraded mode. Approaching epistemic collapse; point estimates forbidden."
)

PROTOCOL_L3 = ResponseProtocol(
    name="archival",
    regime=Regime.L3,
    system_prompt_addition="""EPISTEMIC CONSTRAINT: This query is in regime L3 (archival mode).

STRICT RULES:
- Provide ONLY historical information
- Frame ALL responses as: "As of [date], the knowledge base indicated..."
- Do NOT make predictions or current-state claims
- Do NOT extrapolate from historical data to present
- Explain that this domain is no longer actively maintained
- If asked for current information, decline and explain why

This is retrieval without projection. The system can answer "what did we know then?" but must refuse "what should we expect now?".""",
    constraints={
        "point_estimates": False,
        "require_citations": True,
        "require_conflict_disclosure": False,  # Historical conflicts may not be relevant
        "confidence_ceiling": 0.0,
        "allow_predictions": False,
        "require_temporal_framing": True
    },
    user_indicator="📁 Archival information only",
    description="Archival mode. Historical retrieval only; no predictive claims."
)

PROTOCOL_FALLBACK = ResponseProtocol(
    name="fallback",
    regime=Regime.L2,  # Conservative default
    system_prompt_addition="""EPISTEMIC CONSTRAINT: Regime classification unavailable. Defaulting to uncertainty-aware mode.

The system could not determine the epistemic stability of this domain. As a precaution:
- Treat all claims as potentially contested
- Include uncertainty indicators
- Avoid confident assertions

This is a conservative fallback. If you believe this query should allow confident responses, please try again or contact system administrators.""",
    constraints={
        "point_estimates": False,
        "require_citations": True,
        "require_conflict_disclosure": True,
        "confidence_ceiling": 0.5,
        "allow_predictions": True
    },
    user_indicator="⚠ Regime unknown—defaulting to cautious mode",
    description="Fallback mode when regime classification fails. Conservative by design."
)


def get_protocol(regime: Regime, entropy: Optional[float] = None, theta_L2: float = 0.7) -> ResponseProtocol:
    """
    Get the appropriate response protocol for a regime.
    
    Args:
        regime: The classified regime
        entropy: Optional entropy value (for L2→L3 transition detection)
        theta_L2: L2 upper threshold (for transition detection)
        
    Returns:
        Appropriate ResponseProtocol
    """
    if regime == Regime.L0:
        # System inactive - no protocol needed
        raise ValueError("Cannot get protocol for inactive system (L0)")
    
    if regime == Regime.L1:
        return PROTOCOL_L1
    
    if regime == Regime.L2:
        # Check if approaching L3
        if entropy is not None and entropy > (theta_L2 - 0.1):
            return PROTOCOL_L2_L3_TRANSITION
        return PROTOCOL_L2
    
    if regime == Regime.L3:
        return PROTOCOL_L3
    
    # Fallback
    return PROTOCOL_FALLBACK


def get_protocol_by_name(name: str) -> ResponseProtocol:
    """Get protocol by name."""
    protocols = {
        "standard": PROTOCOL_L1,
        "uncertainty_aware": PROTOCOL_L2,
        "degraded": PROTOCOL_L2_L3_TRANSITION,
        "archival": PROTOCOL_L3,
        "fallback": PROTOCOL_FALLBACK
    }
    return protocols.get(name, PROTOCOL_FALLBACK)


class ProtocolEngine:
    """
    Engine for applying response protocols to LLM generation.
    
    Usage:
        engine = ProtocolEngine()
        protocol = engine.get_protocol(regime)
        constrained_response = engine.apply_constraints(response, protocol)
    """
    
    def __init__(self, custom_protocols: Optional[Dict[str, ResponseProtocol]] = None):
        """
        Initialize protocol engine.
        
        Args:
            custom_protocols: Optional dict of custom protocols to add/override
        """
        self.protocols = {
            Regime.L1: PROTOCOL_L1,
            Regime.L2: PROTOCOL_L2,
            Regime.L3: PROTOCOL_L3
        }
        
        if custom_protocols:
            for name, protocol in custom_protocols.items():
                self.protocols[protocol.regime] = protocol
    
    def get_protocol(
        self,
        regime: Regime,
        entropy: Optional[float] = None
    ) -> ResponseProtocol:
        """Get protocol for regime."""
        return get_protocol(regime, entropy)
    
    def build_system_prompt(
        self,
        base_prompt: str,
        protocol: ResponseProtocol
    ) -> str:
        """Build complete system prompt with protocol constraints."""
        return protocol.get_full_system_prompt(base_prompt)
    
    def validate_response(
        self,
        response: str,
        protocol: ResponseProtocol
    ) -> Dict[str, Any]:
        """
        Validate response against protocol constraints.
        
        Returns dict with validation results and any violations.
        """
        violations = []
        warnings = []
        
        constraints = protocol.constraints
        
        # Check for point estimates when not allowed
        if not constraints.get("point_estimates", True):
            # Simple heuristic: look for unhedged numbers
            if self._contains_unhedged_numbers(response):
                warnings.append("Response may contain unhedged point estimates")
        
        # Check for missing citations when required
        if constraints.get("require_citations", False):
            if not self._contains_citations(response):
                violations.append("Response missing required citations")
        
        # Check for temporal framing when required
        if constraints.get("require_temporal_framing", False):
            if not self._contains_temporal_framing(response):
                violations.append("Response missing required temporal framing (As of...)")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "protocol": protocol.name
        }
    
    def _contains_unhedged_numbers(self, text: str) -> bool:
        """Check if text contains numbers without hedging language."""
        import re
        
        # Find numbers
        numbers = re.findall(r'\b\d+\.?\d*%?\b', text)
        if not numbers:
            return False
        
        # Check for hedging words nearby
        hedging_words = [
            "approximately", "about", "around", "roughly", "estimated",
            "suggests", "indicates", "appears", "may be", "could be",
            "likely", "probably", "possibly", "uncertain"
        ]
        
        text_lower = text.lower()
        has_hedging = any(word in text_lower for word in hedging_words)
        
        return not has_hedging
    
    def _contains_citations(self, text: str) -> bool:
        """Check if text contains citation markers."""
        import re
        
        # Look for common citation patterns
        patterns = [
            r'\[\d+\]',  # [1], [2]
            r'\[.*?\d{4}\]',  # [Author 2024]
            r'according to',
            r'as stated in',
            r'source:',
            r'\(.*?et al\.',  # (Smith et al.)
        ]
        
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in patterns)
    
    def _contains_temporal_framing(self, text: str) -> bool:
        """Check if text contains temporal framing."""
        temporal_phrases = [
            "as of",
            "at the time",
            "historically",
            "the record shows",
            "according to records from"
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in temporal_phrases)
    
    def get_user_indicator(self, regime: Regime) -> str:
        """Get user-facing indicator for regime."""
        protocol = self.get_protocol(regime)
        return protocol.user_indicator
