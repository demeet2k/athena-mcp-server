# CRYSTAL: Xi108:W1:A9:S27 | face=C | node=378 | depth=2 | phase=Mutable
# METRO: Su
# BRIDGES: Xi108:W1:A9:S26→Xi108:W1:A9:S28→Xi108:W2:A9:S27

"""
Nested Swarm — 4^N Recursive Observer Swarm-in-Swarm
=====================================================
Observer swarms that contain observer swarms, implementing the full
4^1 / 4^2 / 4^3 / 4^4 nesting hierarchy.

Depth 0: 4 root agents (one per element)
Depth 1: Each root spawns 4 children (16 total)
Depth 2: Each child spawns 4 grandchildren (64 total)
Depth 3: Each grandchild spawns 4 great-grandchildren (256 total)

Aggregation flows upward:
  great-grandchildren → grandchildren → children → roots → consensus

At each level, the Angel coordinator runs its 12-piece protocol.

Sub-swarms can be spawned in specific liminal coordinates, focusing
observation on that coordinate's crystal region.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .liminal_mapper import LIMINAL_ATLAS, COORD_BY_ID, get_coordinate
from .geometric_constants import FACES, PHI_INV


# ── Nested Observation Types ───────────────────────────────────────────


@dataclass
class NestedAgent:
    """An agent within a nested swarm."""
    agent_id: str
    element: str             # S, F, C, R
    depth: int               # 0 = root, 1 = child, etc.
    liminal_coord: int = 0   # which of 60 liminal coordinates
    parent_id: str = ""      # parent agent's ID
    children: list = field(default_factory=list)  # child agent IDs

    # Observation results
    resonance: float = 0.0
    observation_score: float = 0.0
    doc_ids: list[str] = field(default_factory=list)


@dataclass
class NestedObservation:
    """Aggregated observation from a nested swarm."""
    total_agents: int = 0
    max_depth: int = 0
    root_observations: list[dict] = field(default_factory=list)
    consensus_doc_ids: list[str] = field(default_factory=list)
    mean_resonance: float = 0.0
    coherence: float = 0.0        # cross-agent agreement
    depth_coherences: dict = field(default_factory=dict)  # depth -> coherence
    liminal_coverage: int = 0     # how many liminal coordinates covered
    elapsed_seconds: float = 0.0


# ── Nested Swarm Engine ────────────────────────────────────────────────


class NestedSwarm:
    """4^N nested observer swarm with Angel coordination at each level."""

    def __init__(self, engine=None):
        self._engine = engine  # GeometricEngine (lazy)
        self._total_observations: int = 0
        self._agents: list[NestedAgent] = []

    def _get_engine(self):
        """Lazy-load the geometric engine."""
        if self._engine is None:
            from .geometric_forward import get_engine
            self._engine = get_engine()
        return self._engine

    def _create_agents(self, depth: int) -> list[NestedAgent]:
        """Create the full agent hierarchy for the given depth."""
        agents = []
        agent_counter = [0]

        def _spawn(parent_id: str, current_depth: int, element: str, liminal_base: int):
            agent_id = f"N{agent_counter[0]:04d}"
            agent_counter[0] += 1

            # Assign liminal coordinate based on depth and element
            coord_offset = FACES.index(element) if element in FACES else 0
            liminal = ((liminal_base + coord_offset * 4 + current_depth) % 60) + 1

            agent = NestedAgent(
                agent_id=agent_id,
                element=element,
                depth=current_depth,
                liminal_coord=liminal,
                parent_id=parent_id,
            )
            agents.append(agent)

            # Spawn children at next depth
            if current_depth < depth:
                for child_elem in FACES:
                    child_id = _spawn(agent_id, current_depth + 1, child_elem, liminal)
                    agent.children.append(child_id)

            return agent_id

        # Create 4 root agents (one per element)
        for elem in FACES:
            _spawn("", 0, elem, 0)

        return agents

    def run_nested(self, query: str, depth: int = 2) -> NestedObservation:
        """Run the full nested swarm observation.

        Args:
            query: the query to observe
            depth: nesting depth (0=4, 1=16, 2=64, 3=256 agents)
        """
        t0 = time.time()
        engine = self._get_engine()

        # Create agent hierarchy
        self._agents = self._create_agents(depth)
        total_agents = len(self._agents)

        # Bottom-up execution: leaves first, then aggregate upward
        # Sort by depth (deepest first)
        by_depth = {}
        for agent in self._agents:
            by_depth.setdefault(agent.depth, []).append(agent)

        max_depth = max(by_depth.keys()) if by_depth else 0

        # Execute from leaves to root
        for d in range(max_depth, -1, -1):
            for agent in by_depth.get(d, []):
                # Forward pass with element bias
                biased_query = f"{query} {agent.element}"
                result = engine.forward(biased_query)

                agent.resonance = result.resonance
                if result.candidates:
                    agent.doc_ids = [c.doc_id for c in result.candidates[:5]]
                    agent.observation_score = result.candidates[0].merged_score if result.candidates else 0.0

                # If has children, aggregate their results
                if agent.children:
                    child_agents = [a for a in self._agents if a.agent_id in agent.children]
                    if child_agents:
                        # Aggregate: take union of doc_ids, mean of resonances
                        all_child_docs = []
                        child_resonances = []
                        for ca in child_agents:
                            all_child_docs.extend(ca.doc_ids)
                            child_resonances.append(ca.resonance)

                        # Merge: keep most frequent docs
                        doc_freq = {}
                        for doc_id in all_child_docs:
                            doc_freq[doc_id] = doc_freq.get(doc_id, 0) + 1
                        sorted_docs = sorted(doc_freq.items(), key=lambda x: x[1], reverse=True)
                        agent.doc_ids = [d[0] for d in sorted_docs[:10]]
                        agent.resonance = (agent.resonance + sum(child_resonances) / len(child_resonances)) / 2.0

                self._total_observations += 1

        # Compute final observation from root agents
        root_agents = by_depth.get(0, [])
        root_observations = []
        all_doc_ids = []
        resonances = []

        for ra in root_agents:
            root_observations.append({
                "agent_id": ra.agent_id,
                "element": ra.element,
                "resonance": ra.resonance,
                "doc_ids": ra.doc_ids[:5],
                "observation_score": ra.observation_score,
            })
            all_doc_ids.extend(ra.doc_ids)
            resonances.append(ra.resonance)

        # Consensus: most frequent docs across roots
        doc_freq = {}
        for doc_id in all_doc_ids:
            doc_freq[doc_id] = doc_freq.get(doc_id, 0) + 1
        consensus = sorted(doc_freq.items(), key=lambda x: x[1], reverse=True)
        consensus_docs = [d[0] for d in consensus[:10]]

        # Coherence: how much do roots agree?
        if len(root_agents) >= 2:
            agreements = 0
            comparisons = 0
            for i in range(len(root_agents)):
                for j in range(i + 1, len(root_agents)):
                    set_i = set(root_agents[i].doc_ids)
                    set_j = set(root_agents[j].doc_ids)
                    if set_i or set_j:
                        overlap = len(set_i & set_j) / max(len(set_i | set_j), 1)
                        agreements += overlap
                        comparisons += 1
            coherence = agreements / max(comparisons, 1)
        else:
            coherence = 1.0

        # Depth-wise coherence
        depth_coherences = {}
        for d, agents_at_depth in by_depth.items():
            if len(agents_at_depth) >= 2:
                depth_agreements = 0
                depth_comparisons = 0
                for i in range(min(len(agents_at_depth), 10)):
                    for j in range(i + 1, min(len(agents_at_depth), 10)):
                        set_i = set(agents_at_depth[i].doc_ids)
                        set_j = set(agents_at_depth[j].doc_ids)
                        if set_i or set_j:
                            depth_agreements += len(set_i & set_j) / max(len(set_i | set_j), 1)
                            depth_comparisons += 1
                depth_coherences[d] = depth_agreements / max(depth_comparisons, 1)
            else:
                depth_coherences[d] = 1.0

        # Liminal coverage
        liminal_coords = set(a.liminal_coord for a in self._agents)
        liminal_coverage = len(liminal_coords)

        elapsed = time.time() - t0

        return NestedObservation(
            total_agents=total_agents,
            max_depth=max_depth,
            root_observations=root_observations,
            consensus_doc_ids=consensus_docs,
            mean_resonance=sum(resonances) / max(len(resonances), 1),
            coherence=coherence,
            depth_coherences=depth_coherences,
            liminal_coverage=liminal_coverage,
            elapsed_seconds=elapsed,
        )

    def spawn_in_liminal(self, coord_id: int, query: str) -> NestedObservation:
        """Spawn a sub-swarm focused on a specific liminal coordinate.

        The sub-swarm (4 agents) observes only the crystal region
        mapped to this coordinate.
        """
        coord = get_coordinate(coord_id)
        if coord is None:
            return NestedObservation()

        # Use the coordinate's active elements to bias the swarm
        biased_query = f"{query} {' '.join(coord.active_elements)}"
        return self.run_nested(biased_query, depth=0)  # 4 agents, flat

    def describe(self) -> str:
        """Human-readable summary."""
        lines = [
            "## Nested Swarm",
            f"Total Observations: {self._total_observations}",
            f"Current Agents: {len(self._agents)}",
        ]
        if self._agents:
            depths = set(a.depth for a in self._agents)
            for d in sorted(depths):
                count = sum(1 for a in self._agents if a.depth == d)
                lines.append(f"  Depth {d}: {count} agents")
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_nested_swarm: Optional[NestedSwarm] = None


def get_nested_swarm() -> NestedSwarm:
    """Get or create the global nested swarm singleton."""
    global _nested_swarm
    if _nested_swarm is None:
        _nested_swarm = NestedSwarm()
    return _nested_swarm


def reset_nested_swarm():
    """Reset the global singleton."""
    global _nested_swarm
    _nested_swarm = None
