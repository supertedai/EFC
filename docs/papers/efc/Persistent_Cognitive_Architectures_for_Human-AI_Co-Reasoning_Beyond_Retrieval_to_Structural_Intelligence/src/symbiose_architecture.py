"""
Symbiose Cognitive Architecture - Reference Implementation

From: Magnusson (2026) "Persistent Cognitive Architectures for Human-AI
Co-Reasoning: Beyond Retrieval to Structural Intelligence"
DOI: 10.6084/m9.figshare.31271707

This module provides simplified reference implementations of the core
algorithms described in the paper.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
import math


# =============================================================================
# L0-L3 Epistemic Framework
# =============================================================================

class EpistemicLevel(Enum):
    """Four-level epistemic framework for response tagging."""
    L0 = "Canonical"    # Ground truth, verified
    L1 = "Derived"      # Logical from L0
    L2 = "Supported"    # Evidence-backed
    L3 = "Inferred"     # LLM hypothesis


EPISTEMIC_LEVELS = {
    "L0": {
        "name": "Canonical",
        "description": "Ground truth from authoritative sources",
        "certainty": "Known with certainty",
        "sources": ["neo4j_canonical", "life_contract", "sensor_data"]
    },
    "L1": {
        "name": "Derived",
        "description": "Facts logically derived from L0",
        "certainty": "True given L0 premises",
        "sources": ["causal_inference", "mathematical_consequence"]
    },
    "L2": {
        "name": "Supported",
        "description": "Claims backed by evidence but not fully verified",
        "certainty": "Probable given evidence",
        "sources": ["rag_retrieved", "llm_with_citations"]
    },
    "L3": {
        "name": "Inferred",
        "description": "LLM-generated content without explicit grounding",
        "certainty": "Plausible but unverified",
        "sources": ["synthesis", "analogies", "llm_generation"]
    }
}


@dataclass
class Source:
    """Represents a source for epistemic tagging."""
    id: str
    type: str  # neo4j_canonical, neo4j_derived, rag, llm
    content: str
    confidence: float = 1.0


@dataclass
class TaggedResponse:
    """Response with epistemic level tag."""
    content: str
    level: EpistemicLevel
    note: str
    sources: List[Source]


class EpistemicTagger:
    """
    Algorithm 3: Epistemic Tagging

    Tags every response by source and verifiability.
    """

    def tag_response(self, response: str, sources: List[Source]) -> TaggedResponse:
        """
        Determine epistemic level based on sources.

        From paper Algorithm 3:
        - If all sources are neo4j_canonical → L0
        - If all sources are canonical or derived → L1
        - If any source is RAG → L2
        - Otherwise → L3
        """
        if not sources:
            return TaggedResponse(
                content=response,
                level=EpistemicLevel.L3,
                note="LLM inference - verify independently",
                sources=[]
            )

        source_types = {s.type for s in sources}

        if source_types == {"neo4j_canonical"}:
            level = EpistemicLevel.L0
            note = "Canonical fact from knowledge graph"
        elif source_types <= {"neo4j_canonical", "neo4j_derived"}:
            level = EpistemicLevel.L1
            note = "Derived from canonical facts"
        elif "rag" in source_types:
            level = EpistemicLevel.L2
            note = "Supported by documents"
        else:
            level = EpistemicLevel.L3
            note = "LLM inference - verify independently"

        return TaggedResponse(
            content=response,
            level=level,
            note=note,
            sources=sources
        )


# =============================================================================
# Graph-Vector Fusion
# =============================================================================

@dataclass
class Chunk:
    """Represents a document chunk with embedding."""
    id: str
    content: str
    score: float  # Semantic similarity score
    concepts: List[str] = field(default_factory=list)
    fused_score: float = 0.0


@dataclass
class GraphPath:
    """Represents a path in the knowledge graph."""
    nodes: List[str]
    length: int


class GraphVectorFusion:
    """
    Algorithm 1: Graph-Vector Fusion

    Combines vector embeddings with graph traversal for
    semantic + structural reasoning.
    """

    def __init__(self,
                 semantic_weight: float = 0.6,
                 structural_weight: float = 0.4,
                 max_depth: int = 3):
        """
        Initialize fusion parameters.

        Args:
            semantic_weight: Weight for semantic similarity (default 0.6)
            structural_weight: Weight for structural relevance (default 0.4)
            max_depth: Maximum graph traversal depth (default 3)
        """
        self.semantic_weight = semantic_weight
        self.structural_weight = structural_weight
        self.max_depth = max_depth

    def fuse(self,
             query: str,
             vector_results: List[Chunk],
             graph_paths: Dict[str, List[GraphPath]]) -> List[Chunk]:
        """
        Perform graph-vector fusion.

        From paper Algorithm 1:
        1. Vector retrieval (already done - passed as vector_results)
        2. Graph expansion (already done - passed as graph_paths)
        3. Fusion scoring
        4. Return ranked results

        Args:
            query: The search query
            vector_results: Results from vector search (Qdrant)
            graph_paths: Paths from graph traversal (Neo4j)
                        Key: chunk_id, Value: list of paths

        Returns:
            Ranked list of chunks by fused score
        """
        for chunk in vector_results:
            # Semantic score from vector search
            s_semantic = chunk.score

            # Structural score from graph paths
            paths = graph_paths.get(chunk.id, [])
            if paths:
                # Inverse path length: shorter paths = higher relevance
                s_structural = max(1.0 / p.length for p in paths)
            else:
                s_structural = 0.0

            # Fusion scoring formula from paper
            chunk.fused_score = (
                self.semantic_weight * s_semantic +
                self.structural_weight * s_structural
            )

        # Sort by fused score descending
        return sorted(vector_results, key=lambda c: c.fused_score, reverse=True)


# =============================================================================
# Memory Consolidation
# =============================================================================

@dataclass
class ConversationLog:
    """Raw conversation log."""
    timestamp: str
    topics: List[str]
    content: str


@dataclass
class ConsolidatedMemory:
    """Hierarchically consolidated memory."""
    level: str  # "daily", "weekly", "monthly"
    period: str
    summary: str
    key_topics: List[str]
    insights: List[str]


class MemoryConsolidation:
    """
    Algorithm 2: Post-Conversation Consolidation

    Implements hierarchical memory consolidation:
    Raw Conversations → Daily Logs → Weekly Summaries → Monthly Themes
    """

    def __init__(self):
        self.memories: Dict[str, List[ConsolidatedMemory]] = {
            "daily": [],
            "weekly": [],
            "monthly": []
        }

    def consolidate_daily(self, conversations: List[ConversationLog]) -> ConsolidatedMemory:
        """
        Consolidate raw conversations into daily summary.

        From paper Algorithm 2:
        - Find new connections
        - Identify clusters
        - Find bridge nodes
        - Find orphans
        - Generate insights
        """
        all_topics = []
        for conv in conversations:
            all_topics.extend(conv.topics)

        # Identify unique topics
        unique_topics = list(set(all_topics))

        # Find connections (topics appearing together)
        connections = self._find_connections(conversations)

        # Find clusters (groups of related topics)
        clusters = self._identify_clusters(unique_topics)

        # Find bridge nodes (topics connecting clusters)
        bridges = self._find_bridges(clusters)

        # Find orphans (isolated topics)
        orphans = self._find_orphans(unique_topics, connections)

        return ConsolidatedMemory(
            level="daily",
            period=conversations[0].timestamp[:10] if conversations else "",
            summary=f"Discussed {len(unique_topics)} topics with {len(connections)} connections",
            key_topics=unique_topics[:10],
            insights=[
                f"Clusters: {len(clusters)}",
                f"Bridge nodes: {bridges}",
                f"Orphan topics: {orphans}"
            ]
        )

    def _find_connections(self, conversations: List[ConversationLog]) -> List[Tuple[str, str]]:
        """Find topic co-occurrences within conversations."""
        connections = []
        for conv in conversations:
            topics = conv.topics
            for i, t1 in enumerate(topics):
                for t2 in topics[i+1:]:
                    connections.append((t1, t2))
        return connections

    def _identify_clusters(self, topics: List[str]) -> List[List[str]]:
        """Identify topic clusters (simplified)."""
        # Placeholder: real implementation would use Louvain clustering
        if len(topics) <= 3:
            return [topics]
        return [topics[:len(topics)//2], topics[len(topics)//2:]]

    def _find_bridges(self, clusters: List[List[str]]) -> List[str]:
        """Find topics that bridge clusters."""
        # Placeholder: real implementation uses betweenness centrality
        return []

    def _find_orphans(self, topics: List[str], connections: List[Tuple[str, str]]) -> List[str]:
        """Find isolated topics with no connections."""
        connected = set()
        for t1, t2 in connections:
            connected.add(t1)
            connected.add(t2)
        return [t for t in topics if t not in connected]


# =============================================================================
# Quantum Leap (QL) Orchestration Layer
# =============================================================================

@dataclass
class ProactiveTrigger:
    """Represents a proactive suggestion trigger."""
    type: str  # temporal, evidence_gap, pattern, causal
    condition: str
    suggestion: str
    confidence: float


class QuantumLeap:
    """
    Quantum Leap (QL) - Persistent Cognitive Orchestration Layer

    Coordinates:
    - Memory consolidation
    - Graph-vector fusion
    - Causal reasoning
    - Preference learning
    - Proactive triggers
    """

    def __init__(self):
        self.graph_vector_fusion = GraphVectorFusion()
        self.epistemic_tagger = EpistemicTagger()
        self.memory_consolidation = MemoryConsolidation()

        # Preference learning state
        self.preferences: Dict[str, float] = {}
        self.feedback_history: List[Dict] = []

        # Trigger configuration
        self.triggers: List[ProactiveTrigger] = []

    def update_preference(self, suggestion_type: str, accepted: bool,
                          context: List[str] = None):
        """
        Bayesian update of preference confidence.

        From paper Section 3.6:
        1. User provides feedback (accept/reject)
        2. Update confidence via Bayesian update
        3. Track context keywords
        """
        # Initialize if new type
        if suggestion_type not in self.preferences:
            self.preferences[suggestion_type] = 0.5  # Prior

        # Bayesian update (simplified)
        current = self.preferences[suggestion_type]
        if accepted:
            # Increase confidence
            self.preferences[suggestion_type] = current + 0.1 * (1 - current)
        else:
            # Decrease confidence
            self.preferences[suggestion_type] = current - 0.1 * current

        # Store feedback
        self.feedback_history.append({
            "type": suggestion_type,
            "accepted": accepted,
            "context": context or []
        })

    def check_triggers(self, context: Dict[str, Any]) -> List[ProactiveTrigger]:
        """
        Check which proactive triggers should fire.

        Trigger types from paper:
        1. Temporal: "X days since last Y"
        2. Evidence gap: "Claim without support"
        3. Pattern: "Recurring topic"
        4. Causal: "Change may affect downstream"
        """
        fired = []
        for trigger in self.triggers:
            if self._evaluate_trigger(trigger, context):
                # Filter by preference confidence
                if self.preferences.get(trigger.type, 0.5) > 0.3:
                    fired.append(trigger)
        return fired

    def _evaluate_trigger(self, trigger: ProactiveTrigger,
                          context: Dict[str, Any]) -> bool:
        """Evaluate if a trigger condition is met."""
        # Placeholder: real implementation evaluates condition
        return False

    def process_response(self, response: str, sources: List[Source]) -> TaggedResponse:
        """
        Process a response through the full QL pipeline.

        1. Tag with epistemic level
        2. Check for proactive triggers
        3. Update memory
        """
        return self.epistemic_tagger.tag_response(response, sources)


# =============================================================================
# Demonstration
# =============================================================================

def demonstrate_epistemic_tagging():
    """Demonstrate the L0-L3 epistemic tagging."""
    tagger = EpistemicTagger()

    # L0: Canonical fact
    l0_sources = [Source("1", "neo4j_canonical", "EFC transition acceleration")]
    l0_response = tagger.tag_response(
        "The EFC transition acceleration is g† = 1.2e-10 m/s²",
        l0_sources
    )
    print(f"L0 Example: {l0_response.level.value} - {l0_response.note}")

    # L1: Derived from canonical
    l1_sources = [
        Source("1", "neo4j_canonical", "g† value"),
        Source("2", "neo4j_derived", "screening calculation")
    ]
    l1_response = tagger.tag_response(
        "At 1 AU, |μ-1| < 8e-9 (derived from g†/g_bar)",
        l1_sources
    )
    print(f"L1 Example: {l1_response.level.value} - {l1_response.note}")

    # L2: Supported by documents
    l2_sources = [
        Source("1", "rag", "BOSS DR12 paper"),
        Source("2", "neo4j_canonical", "EFC model")
    ]
    l2_response = tagger.tag_response(
        "BOSS DR12 data shows Δχ² = -7.77 for EFC vs ΛCDM",
        l2_sources
    )
    print(f"L2 Example: {l2_response.level.value} - {l2_response.note}")

    # L3: LLM inference
    l3_sources = [Source("1", "llm", "synthesis")]
    l3_response = tagger.tag_response(
        "EFC might explain the S8 tension through entropy coupling",
        l3_sources
    )
    print(f"L3 Example: {l3_response.level.value} - {l3_response.note}")


if __name__ == "__main__":
    demonstrate_epistemic_tagging()
