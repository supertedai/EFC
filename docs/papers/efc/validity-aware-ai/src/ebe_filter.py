"""
EBE Filter: Entropy-Bounded Empiricism Filter for Regime-Aware RAG

This module implements the core EBE filter that measures entropy in knowledge
structures and determines the appropriate inference regime (L1/L2/L3).

Part of: Validity-Aware AI
DOI: 10.6084/m9.figshare.31122970
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

from .entropy_measures import (
    compute_edge_entropy,
    compute_node_entropy,
    compute_structural_entropy,
    compute_retrieval_entropy
)
from .regime_classifier import Regime, classify_regime
from .response_protocols import get_protocol, ResponseProtocol

logger = logging.getLogger(__name__)


@dataclass
class EntropyResult:
    """Result of entropy computation."""
    total: float
    components: Dict[str, float]
    warnings: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "components": self.components,
            "warnings": self.warnings
        }


@dataclass
class RegimeResult:
    """Result of regime classification."""
    regime: Regime
    confidence: float
    entropy: EntropyResult
    protocol: ResponseProtocol
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime.name,
            "confidence": self.confidence,
            "entropy": self.entropy.to_dict(),
            "protocol": self.protocol.name
        }


class EBEFilter:
    """
    Entropy-Bounded Empiricism Filter.
    
    Measures entropy in knowledge structures and classifies queries into
    L1 (stable), L2 (contested), or L3 (archival) regimes.
    
    Usage:
        ebe = EBEFilter(graph_client, vector_client, domain_config)
        result = ebe.evaluate(query, retrieved_chunks, subgraph)
    """
    
    def __init__(
        self,
        graph_client: Any,
        vector_client: Any,
        domain_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the EBE filter.
        
        Args:
            graph_client: Neo4j or compatible graph database client
            vector_client: Qdrant or compatible vector store client
            domain_config: Domain-specific thresholds and weights
        """
        self.graph_client = graph_client
        self.vector_client = vector_client
        self.config = domain_config or self._default_config()
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "theta_L1": 0.3,
            "theta_L2": 0.7,
            "confidence_ceiling_L2": 0.7,
            "entropy_weights": {
                "edge": 0.30,
                "node": 0.25,
                "structural": 0.25,
                "retrieval": 0.20
            }
        }
    
    def compute_entropy(
        self,
        subgraph: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        temporal_window_days: int = 30
    ) -> EntropyResult:
        """
        Compute total entropy for the query-relevant knowledge structure.
        
        Args:
            subgraph: Relevant subgraph from knowledge graph
            retrieved_chunks: Chunks from vector retrieval
            temporal_window_days: Window for structural drift calculation
            
        Returns:
            EntropyResult with total, components, and warnings
        """
        weights = self.config["entropy_weights"]
        warnings = []
        
        # Compute component entropies
        H_edge = compute_edge_entropy(subgraph)
        H_node = compute_node_entropy(subgraph)
        H_structural = compute_structural_entropy(
            subgraph, 
            self.graph_client,
            window_days=temporal_window_days
        )
        H_retrieval = compute_retrieval_entropy(retrieved_chunks)
        
        # Generate warnings for high component values
        if H_edge > 0.6:
            warnings.append("High edge variance detected")
        if H_node > 0.6:
            warnings.append("Node definitions show significant divergence")
        if H_structural > 0.5:
            warnings.append("High temporal instability in graph structure")
        if H_retrieval > 0.7:
            warnings.append("High retrieval contradiction detected")
        
        # Compute weighted total
        H_total = (
            weights["edge"] * H_edge +
            weights["node"] * H_node +
            weights["structural"] * H_structural +
            weights["retrieval"] * H_retrieval
        )
        
        return EntropyResult(
            total=H_total,
            components={
                "edge": H_edge,
                "node": H_node,
                "structural": H_structural,
                "retrieval": H_retrieval
            },
            warnings=warnings
        )
    
    def evaluate(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        subgraph: Optional[Dict[str, Any]] = None
    ) -> RegimeResult:
        """
        Evaluate a query and return regime classification with protocol.
        
        This is the main entry point for the EBE filter.
        
        Args:
            query: The user query
            retrieved_chunks: Chunks from vector retrieval
            subgraph: Optional pre-computed subgraph (will fetch if not provided)
            
        Returns:
            RegimeResult with regime, confidence, entropy, and protocol
        """
        # Get subgraph if not provided
        if subgraph is None:
            subgraph = self._extract_subgraph(query)
        
        # Compute entropy
        entropy_result = self.compute_entropy(subgraph, retrieved_chunks)
        
        # Classify regime
        regime, confidence = classify_regime(
            entropy_result.total,
            theta_L1=self.config["theta_L1"],
            theta_L2=self.config["theta_L2"]
        )
        
        # Apply confidence ceiling for L2
        if regime == Regime.L2:
            confidence = min(confidence, self.config["confidence_ceiling_L2"])
        
        # Get response protocol
        protocol = get_protocol(regime)
        
        # Log the decision
        logger.info(f"EBE evaluation: regime={regime.name}, confidence={confidence:.2f}, entropy={entropy_result.total:.2f}")
        
        return RegimeResult(
            regime=regime,
            confidence=confidence,
            entropy=entropy_result,
            protocol=protocol
        )
    
    def _extract_subgraph(self, query: str) -> Dict[str, Any]:
        """
        Extract relevant subgraph from knowledge graph.
        
        Override this method for custom subgraph extraction logic.
        """
        # Default implementation - fetch nodes related to query concepts
        # This should be customized based on your graph schema
        try:
            result = self.graph_client.query(
                """
                MATCH (n)-[r]-(m)
                WHERE n.name CONTAINS $query OR n.description CONTAINS $query
                RETURN n, r, m
                LIMIT 100
                """,
                {"query": query}
            )
            return self._parse_graph_result(result)
        except Exception as e:
            logger.warning(f"Subgraph extraction failed: {e}")
            return {"nodes": [], "edges": []}
    
    def _parse_graph_result(self, result: Any) -> Dict[str, Any]:
        """Parse graph query result into standard format."""
        nodes = []
        edges = []
        
        for record in result:
            if "n" in record:
                nodes.append(dict(record["n"]))
            if "r" in record:
                edges.append({
                    "type": record["r"].type,
                    "properties": dict(record["r"]),
                    "confidence": record["r"].get("confidence", 1.0)
                })
            if "m" in record:
                nodes.append(dict(record["m"]))
        
        # Deduplicate nodes
        seen = set()
        unique_nodes = []
        for node in nodes:
            node_id = node.get("id") or str(node)
            if node_id not in seen:
                seen.add(node_id)
                unique_nodes.append(node)
        
        return {"nodes": unique_nodes, "edges": edges}


def create_ebe_filter(
    graph_client: Any,
    vector_client: Any,
    domain: str = "default"
) -> EBEFilter:
    """
    Factory function to create an EBE filter with domain-specific config.
    
    Args:
        graph_client: Graph database client
        vector_client: Vector store client
        domain: Domain name for threshold lookup
        
    Returns:
        Configured EBEFilter instance
    """
    import json
    from pathlib import Path
    
    # Try to load domain config
    config_path = Path(__file__).parent.parent / "data" / "domain_thresholds.json"
    
    try:
        with open(config_path) as f:
            all_configs = json.load(f)
            domain_config = all_configs["domains"].get(domain, all_configs["domains"]["default"])
    except FileNotFoundError:
        logger.warning(f"Config file not found, using defaults")
        domain_config = None
    
    return EBEFilter(graph_client, vector_client, domain_config)
