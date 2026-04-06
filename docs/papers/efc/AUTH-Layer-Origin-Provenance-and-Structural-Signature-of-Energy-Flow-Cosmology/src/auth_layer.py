"""
AUTH Layer -- Origin, Provenance, and Structural Signature of Energy-Flow Cosmology

Implements provenance chain verification, structural signature analysis,
and identity validation for the EFC framework.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.30656828
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import hashlib
import json


class LayerType(Enum):
    """EFC architecture layers."""
    THEORY = "theory"
    METHODOLOGY = "methodology"
    COGNITION = "cognition"
    META = "meta"
    AUTH = "auth"


class TransitionState(Enum):
    """s0/s1 transition states for insight stabilisation."""
    S0_LATENT = "s0_latent"
    S1_ACTIVE = "s1_active"
    STABILISED = "stabilised"


@dataclass
class ProvenanceRecord:
    """Single provenance entry in the AUTH chain."""
    layer: LayerType
    description: str
    timestamp: Optional[str] = None
    parent_hash: Optional[str] = None
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this record."""
        content = f"{self.layer.value}:{self.description}:{self.parent_hash or ''}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class StructuralSignature:
    """Structural signature linking theory, methodology, and cognition layers."""
    theory_anchors: List[str] = field(default_factory=list)
    methodology_anchors: List[str] = field(default_factory=list)
    cognition_anchors: List[str] = field(default_factory=list)
    cross_links: List[Dict[str, str]] = field(default_factory=list)

    def signature_depth(self) -> int:
        """Number of distinct anchor points across all layers."""
        return (len(self.theory_anchors)
                + len(self.methodology_anchors)
                + len(self.cognition_anchors))

    def cross_link_density(self) -> float:
        """Ratio of cross-links to total anchors."""
        depth = self.signature_depth()
        if depth == 0:
            return 0.0
        return len(self.cross_links) / depth

    def is_structurally_consistent(self) -> bool:
        """Check whether signature has anchors in all three layers."""
        return (len(self.theory_anchors) > 0
                and len(self.methodology_anchors) > 0
                and len(self.cognition_anchors) > 0)


@dataclass
class InsightTransition:
    """Models s0/s1 insight transitions and stabilisation."""
    concept: str
    state: TransitionState = TransitionState.S0_LATENT
    stabilisation_count: int = 0
    confirmation_layers: List[LayerType] = field(default_factory=list)

    def activate(self) -> None:
        """Transition from s0 (latent) to s1 (active)."""
        if self.state == TransitionState.S0_LATENT:
            self.state = TransitionState.S1_ACTIVE

    def confirm(self, layer: LayerType) -> None:
        """Confirm insight from a given layer."""
        if layer not in self.confirmation_layers:
            self.confirmation_layers.append(layer)
            self.stabilisation_count += 1
        if self.stabilisation_count >= 3:
            self.state = TransitionState.STABILISED

    def is_stabilised(self) -> bool:
        """Check if insight has been confirmed across sufficient layers."""
        return self.state == TransitionState.STABILISED


class ProvenanceChain:
    """Full provenance chain for an EFC concept or result."""

    def __init__(self, origin: str):
        self.origin = origin
        self.records: List[ProvenanceRecord] = []

    def add_record(self, layer: LayerType, description: str,
                   timestamp: Optional[str] = None) -> ProvenanceRecord:
        """Add a new record to the provenance chain."""
        parent_hash = self.records[-1].hash if self.records else None
        record = ProvenanceRecord(
            layer=layer,
            description=description,
            timestamp=timestamp,
            parent_hash=parent_hash,
        )
        self.records.append(record)
        return record

    def verify_chain(self) -> bool:
        """Verify that the chain is internally consistent (linked hashes)."""
        for i, record in enumerate(self.records):
            if i == 0:
                if record.parent_hash is not None:
                    return False
            else:
                if record.parent_hash != self.records[i - 1].hash:
                    return False
        return True

    def chain_length(self) -> int:
        """Number of records in the chain."""
        return len(self.records)

    def layers_covered(self) -> List[LayerType]:
        """Unique layers represented in the chain."""
        return list(dict.fromkeys(r.layer for r in self.records))

    def summary(self) -> Dict:
        """Return a summary dictionary of the provenance chain."""
        return {
            "origin": self.origin,
            "chain_length": self.chain_length(),
            "layers_covered": [l.value for l in self.layers_covered()],
            "chain_valid": self.verify_chain(),
            "records": [
                {
                    "layer": r.layer.value,
                    "description": r.description,
                    "hash": r.hash,
                }
                for r in self.records
            ],
        }


class AUTHLayer:
    """
    AUTH Layer for Energy-Flow Cosmology.

    The AUTH layer sits above scientific content and tracks how
    structural insight forms, stabilises, and becomes part of the
    EFC continuum.
    """

    # EFC structural signature anchors from the paper
    EFC_SIGNATURE = StructuralSignature(
        theory_anchors=[
            "entropy_flow_equation",
            "regime_transition_dynamics",
            "gate_function_modification",
            "closure_normalisation",
        ],
        methodology_anchors=[
            "CLASS_integration",
            "BAO_fitting",
            "CMB_safety_verification",
            "sign_lemma_proof",
        ],
        cognition_anchors=[
            "s0_s1_transition_model",
            "insight_stabilisation",
            "structural_continuity",
            "provenance_integrity",
        ],
        cross_links=[
            {"from": "entropy_flow_equation", "to": "regime_transition_dynamics"},
            {"from": "gate_function_modification", "to": "CLASS_integration"},
            {"from": "closure_normalisation", "to": "CMB_safety_verification"},
            {"from": "s0_s1_transition_model", "to": "insight_stabilisation"},
            {"from": "sign_lemma_proof", "to": "gate_function_modification"},
        ],
    )

    # Core provenance metadata
    PROVENANCE = {
        "framework": "Energy-Flow Cosmology (EFC)",
        "author": "Morten Magnusson",
        "orcid": "0009-0002-4860-5095",
        "doi": "10.6084/m9.figshare.30656828",
        "layers": ["theory", "methodology", "cognition", "meta", "auth"],
    }

    def __init__(self):
        self.chains: Dict[str, ProvenanceChain] = {}
        self.transitions: List[InsightTransition] = []

    def create_chain(self, concept: str) -> ProvenanceChain:
        """Create a new provenance chain for a concept."""
        chain = ProvenanceChain(origin=concept)
        self.chains[concept] = chain
        return chain

    def get_chain(self, concept: str) -> Optional[ProvenanceChain]:
        """Retrieve a provenance chain by concept name."""
        return self.chains.get(concept)

    def create_transition(self, concept: str) -> InsightTransition:
        """Create a new s0/s1 insight transition."""
        transition = InsightTransition(concept=concept)
        self.transitions.append(transition)
        return transition

    def verify_all_chains(self) -> Dict[str, bool]:
        """Verify all registered provenance chains."""
        return {name: chain.verify_chain() for name, chain in self.chains.items()}

    def structural_signature(self) -> StructuralSignature:
        """Return the EFC structural signature."""
        return self.EFC_SIGNATURE

    def identity_check(self) -> Dict:
        """Verify AUTH layer identity and structural consistency."""
        sig = self.EFC_SIGNATURE
        chain_results = self.verify_all_chains()
        stabilised = [t for t in self.transitions if t.is_stabilised()]
        return {
            "provenance": self.PROVENANCE,
            "signature_depth": sig.signature_depth(),
            "cross_link_density": round(sig.cross_link_density(), 3),
            "structurally_consistent": sig.is_structurally_consistent(),
            "chains_valid": all(chain_results.values()) if chain_results else True,
            "chains_count": len(self.chains),
            "stabilised_insights": len(stabilised),
            "total_insights": len(self.transitions),
        }

    def summary(self) -> str:
        """Human-readable summary of the AUTH layer state."""
        check = self.identity_check()
        lines = [
            "AUTH Layer -- EFC Provenance Summary",
            "=" * 50,
            f"Framework:              {check['provenance']['framework']}",
            f"Author:                 {check['provenance']['author']}",
            f"DOI:                    {check['provenance']['doi']}",
            f"Signature depth:        {check['signature_depth']}",
            f"Cross-link density:     {check['cross_link_density']}",
            f"Structurally consistent: {check['structurally_consistent']}",
            f"Provenance chains:      {check['chains_count']}",
            f"All chains valid:       {check['chains_valid']}",
            f"Stabilised insights:    {check['stabilised_insights']}/{check['total_insights']}",
        ]
        return "\n".join(lines)
