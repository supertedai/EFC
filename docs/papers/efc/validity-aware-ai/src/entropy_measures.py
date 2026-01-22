"""
Entropy Measures for Knowledge Graphs

Implements the four entropy components used in Validity-Aware AI:
- Edge entropy (relationship uncertainty)
- Node entropy (concept uncertainty)
- Structural entropy (topology uncertainty)
- Retrieval entropy (contradiction in retrieved chunks)

Part of: Validity-Aware AI
DOI: 10.6084/m9.figshare.31122970
"""

import math
from typing import List, Dict, Any, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


def compute_edge_entropy(subgraph: Dict[str, Any]) -> float:
    """
    Compute edge entropy based on variance in relationship confidence.
    
    H_E = variance-based entropy of edge confidence scores.
    High variance = high entropy = contested relationships.
    
    Args:
        subgraph: Dict with 'edges' containing edge objects with 'confidence'
        
    Returns:
        Normalized entropy score [0, 1]
    """
    edges = subgraph.get("edges", [])
    
    if not edges:
        return 0.0
    
    # Extract confidence scores
    confidences = []
    for edge in edges:
        conf = edge.get("confidence", 1.0)
        if isinstance(conf, (int, float)):
            confidences.append(float(conf))
    
    if not confidences:
        return 0.0
    
    if len(confidences) == 1:
        # Single edge - entropy based on confidence itself
        return 1.0 - confidences[0]
    
    # Compute variance-based entropy
    mean_conf = sum(confidences) / len(confidences)
    variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
    
    # Normalize: max variance is 0.25 (when half are 0 and half are 1)
    normalized_variance = min(variance / 0.25, 1.0)
    
    # Also factor in mean confidence (low mean = higher uncertainty)
    mean_factor = 1.0 - mean_conf
    
    # Combine: both variance and low confidence increase entropy
    entropy = 0.6 * normalized_variance + 0.4 * mean_factor
    
    return min(max(entropy, 0.0), 1.0)


def compute_node_entropy(subgraph: Dict[str, Any]) -> float:
    """
    Compute node entropy based on concept definition disagreement.
    
    H_V = entropy from conflicting definitions/properties per node.
    Multiple definitions for same concept = high entropy.
    
    Args:
        subgraph: Dict with 'nodes' containing node objects
        
    Returns:
        Normalized entropy score [0, 1]
    """
    nodes = subgraph.get("nodes", [])
    
    if not nodes:
        return 0.0
    
    disagreement_scores = []
    
    for node in nodes:
        # Check for multiple definitions
        definitions = node.get("definitions", [])
        if isinstance(definitions, str):
            definitions = [definitions]
        
        # Check for conflicting properties
        conflicts = node.get("conflicts", [])
        conflict_count = len(conflicts) if conflicts else 0
        
        # Check confidence in node definition
        node_confidence = node.get("confidence", 1.0)
        
        # Compute node-level disagreement
        if len(definitions) > 1:
            # Multiple definitions = higher entropy
            definition_entropy = min(len(definitions) / 5, 1.0)  # Cap at 5 definitions
        else:
            definition_entropy = 0.0
        
        # Conflicts directly increase entropy
        conflict_entropy = min(conflict_count / 3, 1.0)  # Cap at 3 conflicts
        
        # Low confidence = higher entropy
        confidence_entropy = 1.0 - node_confidence
        
        # Combine for this node
        node_score = 0.4 * definition_entropy + 0.4 * conflict_entropy + 0.2 * confidence_entropy
        disagreement_scores.append(node_score)
    
    # Average across all nodes
    return sum(disagreement_scores) / len(disagreement_scores)


def compute_structural_entropy(
    subgraph: Dict[str, Any],
    graph_client: Any = None,
    window_days: int = 30
) -> float:
    """
    Compute structural entropy based on graph topology instability.
    
    H_VE = entropy from topology changes over time.
    Rapid structural changes = high entropy.
    
    Args:
        subgraph: Current subgraph
        graph_client: Client to query historical snapshots (optional)
        window_days: Time window for drift calculation
        
    Returns:
        Normalized entropy score [0, 1]
    """
    edges = subgraph.get("edges", [])
    nodes = subgraph.get("nodes", [])
    
    if not edges and not nodes:
        return 0.0
    
    # If we have a graph client, try to get historical data
    if graph_client is not None:
        try:
            return _compute_temporal_drift(subgraph, graph_client, window_days)
        except Exception as e:
            logger.warning(f"Could not compute temporal drift: {e}")
    
    # Fallback: estimate from current structure
    return _estimate_structural_entropy(subgraph)


def _compute_temporal_drift(
    subgraph: Dict[str, Any],
    graph_client: Any,
    window_days: int
) -> float:
    """Compute actual temporal drift from graph history."""
    # This would query the graph for historical versions
    # Implementation depends on graph schema
    
    # Placeholder: return moderate value
    # In production, query for:
    # - Edge creation/deletion rates
    # - Node property changes
    # - Relationship type changes
    return 0.3


def _estimate_structural_entropy(subgraph: Dict[str, Any]) -> float:
    """Estimate structural entropy from current graph structure."""
    edges = subgraph.get("edges", [])
    nodes = subgraph.get("nodes", [])
    
    if not edges:
        return 0.5  # No edges = uncertain structure
    
    # Check for structural indicators of instability
    
    # 1. Edge type diversity (more types = potentially contested domain)
    edge_types = [e.get("type", "unknown") for e in edges]
    type_counts = Counter(edge_types)
    type_entropy = len(type_counts) / max(len(edges), 1)
    
    # 2. Graph density (very sparse or very dense can indicate issues)
    if nodes:
        max_edges = len(nodes) * (len(nodes) - 1) / 2
        if max_edges > 0:
            density = len(edges) / max_edges
            # Moderate density is most stable
            density_entropy = abs(density - 0.3) / 0.7
        else:
            density_entropy = 0.5
    else:
        density_entropy = 0.5
    
    # 3. Check for temporal markers on edges
    temporal_markers = sum(1 for e in edges if "updated_at" in e or "created_at" in e)
    has_temporal = temporal_markers / max(len(edges), 1)
    
    # Combine factors
    return 0.4 * type_entropy + 0.3 * density_entropy + 0.3 * (1.0 - has_temporal)


def compute_retrieval_entropy(retrieved_chunks: List[Dict[str, Any]]) -> float:
    """
    Compute entropy based on contradiction in retrieved chunks.
    
    H_retrieval = entropy from conflicting information in RAG context.
    Contradictory chunks = high entropy.
    
    Args:
        retrieved_chunks: List of retrieved document chunks
        
    Returns:
        Normalized entropy score [0, 1]
    """
    if not retrieved_chunks:
        return 0.5  # No context = moderate uncertainty
    
    if len(retrieved_chunks) == 1:
        # Single source - check its confidence
        conf = retrieved_chunks[0].get("confidence", 0.8)
        return 1.0 - conf
    
    # Check for contradiction indicators
    
    # 1. Source diversity
    sources = [c.get("source", "unknown") for c in retrieved_chunks]
    unique_sources = len(set(sources))
    source_diversity = unique_sources / len(retrieved_chunks)
    
    # 2. Confidence variance
    confidences = [c.get("confidence", 0.8) for c in retrieved_chunks]
    mean_conf = sum(confidences) / len(confidences)
    conf_variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
    
    # 3. Explicit contradiction flags
    contradictions = sum(1 for c in retrieved_chunks if c.get("contradiction_flag", False))
    contradiction_ratio = contradictions / len(retrieved_chunks)
    
    # 4. Temporal spread (old + new sources = potential outdated info)
    timestamps = [c.get("timestamp") for c in retrieved_chunks if c.get("timestamp")]
    if len(timestamps) >= 2:
        # Check if timestamps span long period (could indicate evolving topic)
        temporal_spread = 0.3  # Placeholder
    else:
        temporal_spread = 0.0
    
    # Combine factors
    entropy = (
        0.2 * source_diversity +
        0.2 * min(conf_variance / 0.25, 1.0) +
        0.4 * contradiction_ratio +
        0.2 * temporal_spread
    )
    
    # Also factor in overall confidence
    low_confidence_penalty = max(0, 0.5 - mean_conf) * 0.5
    
    return min(max(entropy + low_confidence_penalty, 0.0), 1.0)


def compute_total_entropy(
    subgraph: Dict[str, Any],
    retrieved_chunks: List[Dict[str, Any]],
    graph_client: Any = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Compute total graph entropy with all components.
    
    This is the main entropy function combining all measures.
    
    Args:
        subgraph: Relevant knowledge graph subgraph
        retrieved_chunks: Retrieved RAG chunks
        graph_client: Optional graph client for temporal queries
        weights: Component weights (default: equal weighting)
        
    Returns:
        Dict with total entropy and component breakdown
    """
    if weights is None:
        weights = {
            "edge": 0.30,
            "node": 0.25,
            "structural": 0.25,
            "retrieval": 0.20
        }
    
    # Compute components
    H_edge = compute_edge_entropy(subgraph)
    H_node = compute_node_entropy(subgraph)
    H_structural = compute_structural_entropy(subgraph, graph_client)
    H_retrieval = compute_retrieval_entropy(retrieved_chunks)
    
    # Weighted sum
    H_total = (
        weights["edge"] * H_edge +
        weights["node"] * H_node +
        weights["structural"] * H_structural +
        weights["retrieval"] * H_retrieval
    )
    
    return {
        "total": H_total,
        "components": {
            "edge": H_edge,
            "node": H_node,
            "structural": H_structural,
            "retrieval": H_retrieval
        },
        "weights": weights
    }
