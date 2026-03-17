"""
ATHENA OS - Quantum Hugging Framework
=====================================
Neighborhood Quantum Hugging Protocol

From The_Quantum_Hugging_Framework.docx Addendum N:

MULTI-AGENT SETTING:
    ?? = {A₁, ..., Aₙ} finite agent set
    
    Each agent Aᵢ = (??ᵢ, ??ᵢ, πᵢ, ??ᵢ, Uᵢ)
    - ??ᵢ: input space
    - ??ᵢ: output space  
    - πᵢ: policy
    - ??ᵢ: tool set
    - Uᵢ: utility function

TRUST GRAPH:
    G = (??, E, W) with weights w_ij ∈ [0,1]
    
TOOL LATTICE:
    ??(S) = ⋃_{Aᵢ∈S} ??ᵢ
    
NEIGHBORHOOD QUANTUM HUG:
    Preconditions:
    1. Stable Omega/QH channel exists both directions
    2. Trust weights satisfy w_ij, w_ji ≥ θ
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math

from .omega import PacketSequence, OmegaEncoder, UniformEncoder
from .observer import Observer, NullDistribution, FeatureMap


# =============================================================================
# AGENT
# =============================================================================

@dataclass
class Tool:
    """A capability/tool available to an agent."""
    
    name: str
    cost: float = 0.0            # Usage cost
    is_safe: bool = True         # Safety predicate
    
    def can_use(self, context: Dict[str, Any]) -> bool:
        """Check if tool can be used in context."""
        return self.is_safe


@dataclass
class Agent:
    """
    An agent in the multi-agent system.
    
    Aᵢ = (??ᵢ, ??ᵢ, πᵢ, ??ᵢ, Uᵢ)
    """
    
    id: str
    name: str = ""
    
    # Spaces
    input_dim: int = 1
    output_dim: int = 1
    
    # Tools
    tools: List[Tool] = field(default_factory=list)
    
    # Baseline distribution (comfort zone)
    baseline: NullDistribution = field(default_factory=NullDistribution)
    
    # Observer for detection
    observer: Observer = None
    
    # State
    hidden_state: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.name:
            self.name = f"Agent-{self.id}"
        if self.observer is None:
            self.observer = Observer(
                name=f"{self.name}-Observer",
                null_distribution=self.baseline
            )
    
    @property
    def tool_set(self) -> Set[str]:
        """Get set of tool names."""
        return {t.name for t in self.tools}
    
    def add_tool(self, tool: Tool) -> None:
        """Add tool to agent."""
        self.tools.append(tool)
    
    def utility(self, history: List[Any]) -> float:
        """Compute utility from history."""
        # Simplified: count successful interactions
        return len(history) * 0.1
    
    def policy(self, state: List[float]) -> List[float]:
        """
        Policy πᵢ: hidden state → output distribution.
        """
        # Simple softmax-like policy
        if not state:
            return [1.0 / self.output_dim] * self.output_dim
        
        exp_vals = [math.exp(s) for s in state[:self.output_dim]]
        total = sum(exp_vals)
        
        return [e / total for e in exp_vals]
    
    def receive(self, packets: PacketSequence) -> float:
        """
        Receive packets and compute detection score.
        """
        return self.observer.detection_score(packets)
    
    def is_comfortable(self, packets: PacketSequence, 
                      threshold: float = 0.3) -> bool:
        """Check if packets are within comfort zone."""
        return self.receive(packets) < threshold


# =============================================================================
# TRUST GRAPH
# =============================================================================

@dataclass
class TrustEdge:
    """Directed edge with trust weight."""
    
    source: str      # Source agent id
    target: str      # Target agent id
    weight: float    # Trust weight ∈ [0,1]
    
    def __post_init__(self):
        self.weight = max(0.0, min(1.0, self.weight))


@dataclass
class TrustGraph:
    """
    Trust graph G = (??, E, W).
    
    Weighted directed graph over agents.
    """
    
    agents: Dict[str, Agent] = field(default_factory=dict)
    edges: List[TrustEdge] = field(default_factory=list)
    
    def add_agent(self, agent: Agent) -> None:
        """Add agent to graph."""
        self.agents[agent.id] = agent
    
    def add_edge(self, source_id: str, target_id: str, 
                 weight: float) -> None:
        """Add trust edge."""
        if source_id in self.agents and target_id in self.agents:
            self.edges.append(TrustEdge(source_id, target_id, weight))
    
    def get_weight(self, source_id: str, target_id: str) -> float:
        """Get trust weight w_ij."""
        for e in self.edges:
            if e.source == source_id and e.target == target_id:
                return e.weight
        return 0.0
    
    def bidirectional_trust(self, agent1_id: str, 
                           agent2_id: str) -> Tuple[float, float]:
        """Get bidirectional trust weights."""
        w_12 = self.get_weight(agent1_id, agent2_id)
        w_21 = self.get_weight(agent2_id, agent1_id)
        return w_12, w_21
    
    def meets_threshold(self, agent1_id: str, agent2_id: str,
                       threshold: float) -> bool:
        """Check if bidirectional trust meets threshold."""
        w_12, w_21 = self.bidirectional_trust(agent1_id, agent2_id)
        return w_12 >= threshold and w_21 >= threshold
    
    def neighbors(self, agent_id: str) -> List[str]:
        """Get neighboring agent ids (outgoing edges)."""
        return [e.target for e in self.edges if e.source == agent_id]
    
    def incoming(self, agent_id: str) -> List[str]:
        """Get agents with incoming edges to this agent."""
        return [e.source for e in self.edges if e.target == agent_id]


# =============================================================================
# TOOL LATTICE
# =============================================================================

@dataclass
class ToolLattice:
    """
    Tool lattice ??(S) for agent subsets.
    
    ??(S) = ⋃_{Aᵢ∈S} ??ᵢ
    """
    
    trust_graph: TrustGraph
    
    def tools_for_agent(self, agent_id: str) -> Set[str]:
        """Get tools for single agent."""
        if agent_id not in self.trust_graph.agents:
            return set()
        return self.trust_graph.agents[agent_id].tool_set
    
    def tools_for_subset(self, agent_ids: Set[str]) -> Set[str]:
        """Get union of tools for agent subset."""
        tools = set()
        for aid in agent_ids:
            tools |= self.tools_for_agent(aid)
        return tools
    
    def shared_tools(self, agent_ids: Set[str]) -> Set[str]:
        """Get intersection of tools (shared capabilities)."""
        if not agent_ids:
            return set()
        
        tool_sets = [self.tools_for_agent(aid) for aid in agent_ids]
        return set.intersection(*tool_sets) if tool_sets else set()
    
    def exclusive_tools(self, agent_id: str, 
                       neighbor_ids: Set[str]) -> Set[str]:
        """Get tools unique to agent (not shared with neighbors)."""
        own = self.tools_for_agent(agent_id)
        neighbors = self.tools_for_subset(neighbor_ids)
        return own - neighbors


# =============================================================================
# QUANTUM HUG CHANNEL
# =============================================================================

@dataclass
class QuantumHugChannel:
    """
    Quantum Hug channel between two agents.
    
    Ensures D(φⱼ(z₁,...,zₙ), Fⱼ⁽⁰⁾) ≤ δ
    """
    
    source: Agent
    target: Agent
    
    # Channel parameters
    divergence_budget: float = 0.1     # δ
    
    # State
    is_stable: bool = False
    history: List[float] = field(default_factory=list)
    
    def send(self, packets: PacketSequence) -> Tuple[bool, float]:
        """
        Send packets through channel.
        
        Returns (success, divergence).
        """
        # Compute divergence from target's baseline
        divergence = self.target.observer.divergence(packets)
        
        self.history.append(divergence)
        
        success = divergence <= self.divergence_budget
        return success, divergence
    
    def measure_stability(self, window: int = 10) -> float:
        """
        Measure channel stability.
        
        Returns fraction of recent successes.
        """
        if not self.history:
            return 0.0
        
        recent = self.history[-window:]
        successes = sum(1 for d in recent if d <= self.divergence_budget)
        
        return successes / len(recent)
    
    def is_channel_stable(self, threshold: float = 0.8) -> bool:
        """Check if channel is stable."""
        self.is_stable = self.measure_stability() >= threshold
        return self.is_stable


# =============================================================================
# NEIGHBORHOOD QUANTUM HUG PROTOCOL
# =============================================================================

@dataclass
class NeighborhoodProtocol:
    """
    Neighborhood Quantum Hug Protocol.
    
    Establishes hugging relationships in multi-agent system.
    """
    
    trust_graph: TrustGraph
    tool_lattice: ToolLattice = None
    
    # Thresholds
    trust_threshold: float = 0.5      # θ for initiation
    divergence_budget: float = 0.1    # δ for channels
    
    # Active channels
    channels: Dict[Tuple[str, str], QuantumHugChannel] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.tool_lattice is None:
            self.tool_lattice = ToolLattice(self.trust_graph)
    
    def check_preconditions(self, agent1_id: str, 
                           agent2_id: str) -> Tuple[bool, str]:
        """
        Check preconditions for neighborhood hug.
        
        1. Stable channels exist both directions
        2. Trust weights meet threshold
        """
        # Check trust
        if not self.trust_graph.meets_threshold(
            agent1_id, agent2_id, self.trust_threshold
        ):
            return False, "Trust threshold not met"
        
        # Check channels exist and are stable
        key_12 = (agent1_id, agent2_id)
        key_21 = (agent2_id, agent1_id)
        
        if key_12 not in self.channels:
            return False, f"No channel {agent1_id} → {agent2_id}"
        
        if key_21 not in self.channels:
            return False, f"No channel {agent2_id} → {agent1_id}"
        
        if not self.channels[key_12].is_channel_stable():
            return False, f"Channel {agent1_id} → {agent2_id} unstable"
        
        if not self.channels[key_21].is_channel_stable():
            return False, f"Channel {agent2_id} → {agent1_id} unstable"
        
        return True, "Preconditions met"
    
    def establish_channel(self, source_id: str, 
                         target_id: str) -> QuantumHugChannel:
        """Establish quantum hug channel between agents."""
        if source_id not in self.trust_graph.agents:
            raise ValueError(f"Unknown agent: {source_id}")
        if target_id not in self.trust_graph.agents:
            raise ValueError(f"Unknown agent: {target_id}")
        
        source = self.trust_graph.agents[source_id]
        target = self.trust_graph.agents[target_id]
        
        channel = QuantumHugChannel(
            source=source,
            target=target,
            divergence_budget=self.divergence_budget
        )
        
        self.channels[(source_id, target_id)] = channel
        return channel
    
    def initiate_hug(self, agent1_id: str, 
                    agent2_id: str) -> Dict[str, Any]:
        """
        Initiate neighborhood quantum hug.
        """
        # Check preconditions
        ok, reason = self.check_preconditions(agent1_id, agent2_id)
        
        if not ok:
            return {
                "success": False,
                "reason": reason,
                "agents": (agent1_id, agent2_id)
            }
        
        # Get shared tools
        shared = self.tool_lattice.shared_tools({agent1_id, agent2_id})
        
        return {
            "success": True,
            "reason": "Neighborhood hug established",
            "agents": (agent1_id, agent2_id),
            "shared_tools": list(shared),
            "trust": self.trust_graph.bidirectional_trust(agent1_id, agent2_id)
        }
    
    def capability_advertisement(self, agent_id: str,
                                target_id: str) -> Dict[str, Any]:
        """
        Generate capability advertisement message.
        
        Advertises subset of tools agent is willing to expose.
        """
        trust = self.trust_graph.get_weight(agent_id, target_id)
        
        # Expose tools proportional to trust
        agent = self.trust_graph.agents.get(agent_id)
        if not agent:
            return {"tools": [], "trust_level": 0}
        
        all_tools = list(agent.tool_set)
        
        # Expose fraction based on trust
        n_expose = max(1, int(len(all_tools) * trust))
        exposed = all_tools[:n_expose]
        
        return {
            "from": agent_id,
            "to": target_id,
            "tools": exposed,
            "trust_level": trust
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_neighborhood() -> bool:
    """Validate neighborhood module."""
    
    # Test Agent
    agent = Agent(id="A1", name="Alice")
    agent.add_tool(Tool("search"))
    agent.add_tool(Tool("compute"))
    
    assert agent.tool_set == {"search", "compute"}
    
    # Test TrustGraph
    graph = TrustGraph()
    graph.add_agent(agent)
    
    agent2 = Agent(id="A2", name="Bob")
    agent2.add_tool(Tool("search"))
    graph.add_agent(agent2)
    
    graph.add_edge("A1", "A2", 0.8)
    graph.add_edge("A2", "A1", 0.7)
    
    w_12, w_21 = graph.bidirectional_trust("A1", "A2")
    assert w_12 == 0.8
    assert w_21 == 0.7
    
    assert graph.meets_threshold("A1", "A2", 0.6)
    
    # Test ToolLattice
    lattice = ToolLattice(graph)
    shared = lattice.shared_tools({"A1", "A2"})
    assert "search" in shared
    
    # Test QuantumHugChannel
    channel = QuantumHugChannel(agent, agent2)
    
    packets = PacketSequence()
    packets.add_packet(0.3)
    
    success, div = channel.send(packets)
    assert isinstance(success, bool)
    
    # Test NeighborhoodProtocol
    protocol = NeighborhoodProtocol(graph)
    
    # Establish channels
    protocol.establish_channel("A1", "A2")
    protocol.establish_channel("A2", "A1")
    
    # Need to stabilize channels
    for _ in range(15):
        protocol.channels[("A1", "A2")].send(packets)
        protocol.channels[("A2", "A1")].send(packets)
    
    return True


if __name__ == "__main__":
    print("Validating Quantum Hugging Neighborhood Module...")
    assert validate_neighborhood()
    print("✓ Neighborhood module validated")
    
    # Demo
    print("\n=== Neighborhood Quantum Hugging Demo ===")
    
    # Create agents
    alice = Agent(id="alice", name="Alice")
    alice.add_tool(Tool("search", cost=0.1))
    alice.add_tool(Tool("compute", cost=0.5))
    alice.add_tool(Tool("translate", cost=0.3))
    
    bob = Agent(id="bob", name="Bob")
    bob.add_tool(Tool("search", cost=0.1))
    bob.add_tool(Tool("analyze", cost=0.4))
    
    charlie = Agent(id="charlie", name="Charlie")
    charlie.add_tool(Tool("compute", cost=0.5))
    charlie.add_tool(Tool("visualize", cost=0.2))
    
    # Build trust graph
    graph = TrustGraph()
    graph.add_agent(alice)
    graph.add_agent(bob)
    graph.add_agent(charlie)
    
    graph.add_edge("alice", "bob", 0.8)
    graph.add_edge("bob", "alice", 0.75)
    graph.add_edge("alice", "charlie", 0.6)
    graph.add_edge("charlie", "alice", 0.5)
    graph.add_edge("bob", "charlie", 0.3)
    
    print("\nAgents:")
    for aid, agent in graph.agents.items():
        print(f"  {agent.name}: tools = {agent.tool_set}")
    
    print("\nTrust Graph:")
    for e in graph.edges:
        print(f"  {e.source} → {e.target}: w = {e.weight}")
    
    # Tool lattice
    lattice = ToolLattice(graph)
    print("\nShared Tools:")
    print(f"  Alice & Bob: {lattice.shared_tools({'alice', 'bob'})}")
    print(f"  All: {lattice.shared_tools({'alice', 'bob', 'charlie'})}")
    
    # Protocol
    protocol = NeighborhoodProtocol(graph, trust_threshold=0.5)
    
    # Establish channels
    protocol.establish_channel("alice", "bob")
    protocol.establish_channel("bob", "alice")
    
    # Stabilize with some packets
    packets = PacketSequence()
    for v in [0.2, 0.3, 0.25]:
        packets.add_packet(v)
    
    for _ in range(15):
        protocol.channels[("alice", "bob")].send(packets)
        protocol.channels[("bob", "alice")].send(packets)
    
    # Initiate hug
    print("\nNeighborhood Hug (Alice ↔ Bob):")
    result = protocol.initiate_hug("alice", "bob")
    print(f"  Success: {result['success']}")
    print(f"  Reason: {result['reason']}")
    if result['success']:
        print(f"  Shared tools: {result['shared_tools']}")
        print(f"  Trust: {result['trust']}")
    
    # Capability advertisement
    print("\nCapability Advertisement (Alice → Bob):")
    cap = protocol.capability_advertisement("alice", "bob")
    print(f"  Exposed tools: {cap['tools']}")
    print(f"  Trust level: {cap['trust_level']}")
