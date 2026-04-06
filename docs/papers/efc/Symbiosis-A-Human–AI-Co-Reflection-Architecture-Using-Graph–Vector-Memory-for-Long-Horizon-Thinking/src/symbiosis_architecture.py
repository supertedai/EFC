"""
Symbiosis: Human-AI Co-Reflection Architecture.

Implements a co-reflection system integrating LLMs with hybrid memory
(knowledge graph + vector database) for long-horizon thinking,
hypothesis tracking, and metacognitive feedback.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    CONCEPT = "concept"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    REFLECTION = "reflection"
    QUESTION = "question"


class HypothesisStatus(Enum):
    """Lifecycle status of a tracked hypothesis."""
    PROPOSED = "proposed"
    ACTIVE = "active"
    SUPPORTED = "supported"
    CHALLENGED = "challenged"
    ARCHIVED = "archived"


@dataclass
class GraphNode:
    """A node in the knowledge graph.

    Attributes:
        node_id: Unique identifier.
        node_type: Category of the node.
        label: Human-readable label.
        content: Full textual content.
        timestamp: Creation time (Unix).
        metadata: Arbitrary key-value metadata.
    """
    node_id: str
    node_type: NodeType
    label: str
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """A directed edge in the knowledge graph.

    Attributes:
        source: Source node ID.
        target: Target node ID.
        relation: Relationship type label.
        weight: Edge weight (0-1).
    """
    source: str
    target: str
    relation: str
    weight: float = 1.0


@dataclass
class VectorEntry:
    """An entry in the vector database.

    Attributes:
        entry_id: Unique identifier.
        text: Source text that was embedded.
        embedding: Vector embedding (list of floats).
        metadata: Arbitrary metadata.
    """
    entry_id: str
    text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridMemory:
    """Hybrid memory substrate combining knowledge graph and vector store.

    Provides unified retrieval across structured (graph) and
    unstructured (vector) memory for long-horizon reasoning.

    Attributes:
        nodes: Knowledge graph nodes by ID.
        edges: Knowledge graph edges.
        vectors: Vector database entries by ID.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.vectors: Dict[str, VectorEntry] = {}

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the knowledge graph."""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the knowledge graph."""
        self.edges.append(edge)

    def add_vector(self, entry: VectorEntry) -> None:
        """Add an entry to the vector store."""
        self.vectors[entry.entry_id] = entry

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str]]:
        """Get all neighbors of a node.

        Returns:
            List of (neighbor_id, relation) tuples.
        """
        result = []
        for e in self.edges:
            if e.source == node_id:
                result.append((e.target, e.relation))
            elif e.target == node_id:
                result.append((e.source, e.relation))
        return result

    def search_nodes(self, node_type: Optional[NodeType] = None, keyword: str = "") -> List[GraphNode]:
        """Search graph nodes by type and/or keyword."""
        results = []
        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if keyword and keyword.lower() not in (node.label + node.content).lower():
                continue
            results.append(node)
        return results

    def summary(self) -> Dict[str, int]:
        """Return counts of nodes, edges, and vectors."""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "vectors": len(self.vectors),
        }


@dataclass
class ReflectionEntry:
    """A single reflection event in the co-reflection loop."""
    reflection_id: int
    trigger: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metacognitive_tag: str = ""


class ReflectionLoop:
    """Manages the iterative reflection cycle between human and AI.

    Tracks reflection entries, metacognitive feedback, and
    hypothesis state transitions.

    Attributes:
        entries: Ordered list of reflection events.
        hypotheses: Tracked hypotheses with lifecycle status.
    """

    def __init__(self):
        self.entries: List[ReflectionEntry] = []
        self.hypotheses: Dict[str, HypothesisStatus] = {}
        self._counter: int = 0

    def reflect(self, trigger: str, content: str, metacognitive_tag: str = "") -> ReflectionEntry:
        """Record a new reflection event.

        Args:
            trigger: What initiated the reflection.
            content: The reflection content.
            metacognitive_tag: Optional metacognitive label.

        Returns:
            The created ReflectionEntry.
        """
        self._counter += 1
        entry = ReflectionEntry(
            reflection_id=self._counter,
            trigger=trigger,
            content=content,
            metacognitive_tag=metacognitive_tag,
        )
        self.entries.append(entry)
        return entry

    def propose_hypothesis(self, hypothesis_id: str) -> None:
        """Register a new hypothesis."""
        self.hypotheses[hypothesis_id] = HypothesisStatus.PROPOSED

    def update_hypothesis(self, hypothesis_id: str, status: HypothesisStatus) -> None:
        """Update a hypothesis status."""
        if hypothesis_id in self.hypotheses:
            self.hypotheses[hypothesis_id] = status

    def get_active_hypotheses(self) -> List[str]:
        """Return IDs of all active hypotheses."""
        return [h for h, s in self.hypotheses.items()
                if s in (HypothesisStatus.PROPOSED, HypothesisStatus.ACTIVE)]

    def reflection_depth(self) -> int:
        """Return the total number of reflection events."""
        return len(self.entries)


class SymbiosisArchitecture:
    """Top-level Symbiosis co-reflection architecture.

    Integrates hybrid memory with reflection loops for
    long-horizon human-AI thinking.

    Attributes:
        memory: The hybrid memory substrate.
        reflection: The reflection loop manager.
    """

    def __init__(self):
        self.memory = HybridMemory()
        self.reflection = ReflectionLoop()

    def ingest_concept(self, concept_id: str, label: str, content: str) -> GraphNode:
        """Add a concept to the knowledge graph.

        Args:
            concept_id: Unique identifier.
            label: Human-readable label.
            content: Full description.

        Returns:
            The created GraphNode.
        """
        node = GraphNode(
            node_id=concept_id,
            node_type=NodeType.CONCEPT,
            label=label,
            content=content,
        )
        self.memory.add_node(node)
        return node

    def link_concepts(self, source: str, target: str, relation: str) -> None:
        """Create a relationship between two concepts."""
        self.memory.add_edge(GraphEdge(source=source, target=target, relation=relation))

    def reflect_on(self, trigger: str, content: str) -> ReflectionEntry:
        """Record a reflection event."""
        return self.reflection.reflect(trigger, content)

    def summary(self) -> Dict:
        """Return a summary of the entire architecture state."""
        return {
            "memory": self.memory.summary(),
            "reflections": self.reflection.reflection_depth(),
            "active_hypotheses": len(self.reflection.get_active_hypotheses()),
            "total_hypotheses": len(self.reflection.hypotheses),
        }


if __name__ == "__main__":
    arch = SymbiosisArchitecture()
    arch.ingest_concept("c1", "EFC", "Energy-Flow Cosmology")
    arch.ingest_concept("c2", "EBE", "Entropy-Bounded Empiricism")
    arch.link_concepts("c1", "c2", "foundational_basis")
    arch.reflect_on("init", "Linked EFC to EBE")
    assert arch.memory.summary()["nodes"] == 2
    print("Symbiosis Architecture module OK")
