"""
ATHENA OS - EPICS: MINING PROTOCOL
===================================
Multi-Pass Mining Protocol for Extracting Computational Frameworks

THE MINING PROCESS:
    Transform any epic into:
    1. A FORMAL SYSTEM MODEL (state space, variables, operators, constraints)
    2. A FAILURE-ANALYSIS REPORT (how the system breaks)
    3. A PROTOCOL SPECIFICATION (patches, invariants, lessons)

NINE PRIMARY PASSES:
    Pass 0: Text Stabilization and Boundary Definition
    Pass 1: Narrative Decomposition (Data Structuring)
    Pass 2: State Space Extraction
    Pass 3: Resource, Token, and Economy Modeling
    Pass 4: Protocol Discovery (Codes, Rituals, Rules)
    Pass 5: Error and Crash Pattern Extraction
    Pass 6: Patch and Resolution Modeling
    Pass 7: Formal Modeling
    Pass 8: Cross-Epic Pattern Recognition
    Pass 9: Epic-to-Protocol Document Encoding

OUTPUT:
    - Formal state machine and graphs
    - Game-theoretic sketches of core conflicts
    - Dynamical and information-theoretic models
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .epic_registry import EpicEntry, SystemDomain, FailureCategory, PatchType, EPIC_REGISTRY
from .state_extraction import StateVariable, StateVector, StateSpace, StateDimension
from .failure_modes import CrashSignature, CrashSeverity, FailureAnalyzer
from .protocols import Protocol, ProtocolStep, ProtocolPhase, Invariant


# =============================================================================
# MINING PASS
# =============================================================================

class MiningPass(Enum):
    """The nine passes of the mining protocol."""
    
    PASS_0_STABILIZATION = 0
    PASS_1_DECOMPOSITION = 1
    PASS_2_STATE_SPACE = 2
    PASS_3_ECONOMY = 3
    PASS_4_PROTOCOLS = 4
    PASS_5_ERRORS = 5
    PASS_6_PATCHES = 6
    PASS_7_FORMAL = 7
    PASS_8_CROSS_EPIC = 8
    PASS_9_ENCODING = 9


# =============================================================================
# NARRATIVE SEGMENT
# =============================================================================

@dataclass
class NarrativeSegment:
    """A segment of narrative (scene, chapter, book)."""
    
    name: str
    description: str
    
    # Location in narrative
    book: int = 0
    chapter: int = 0
    
    # Agents involved
    agents: List[str] = field(default_factory=list)
    
    # Actions
    actions: List[str] = field(default_factory=list)
    
    # State changes
    state_changes: Dict[str, float] = field(default_factory=dict)
    
    # Input signals (omens, dreams, commands)
    inputs: List[str] = field(default_factory=list)
    
    # Outputs (deaths, oaths, power changes)
    outputs: List[str] = field(default_factory=list)


# =============================================================================
# TOKEN/RESOURCE
# =============================================================================

@dataclass
class NarrativeToken:
    """
    A token or resource tracked in the epic.
    
    Can be tangible (sword, treasure) or intangible (honor, prophecy).
    """
    
    name: str
    token_type: str  # tangible, intangible
    
    # What it represents
    represents: str = ""
    
    # Current holder
    holder: Optional[str] = None
    
    # Value/power
    value: float = 1.0
    
    # Conservation
    is_conserved: bool = False  # Is total fixed in system?
    
    # Transfer history
    transfers: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, to, reason)
    
    def transfer(self, from_agent: str, to_agent: str, reason: str) -> None:
        """Transfer token between agents."""
        self.transfers.append((from_agent, to_agent, reason))
        self.holder = to_agent


# =============================================================================
# MINING RESULT
# =============================================================================

@dataclass
class MiningResult:
    """Result of mining a single pass."""
    
    pass_number: MiningPass
    success: bool
    
    # Outputs
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Warnings/notes
    notes: List[str] = field(default_factory=list)


@dataclass
class FullMiningResult:
    """Complete result of mining an epic."""
    
    epic_name: str
    
    # Pass results
    passes: Dict[MiningPass, MiningResult] = field(default_factory=dict)
    
    # Final outputs
    state_space: Optional[StateSpace] = None
    crash_signatures: List[CrashSignature] = field(default_factory=list)
    protocol: Optional[Protocol] = None
    
    # Quality metrics
    completeness: float = 0.0
    
    def is_complete(self) -> bool:
        """Check if all passes completed."""
        return len(self.passes) == 10


# =============================================================================
# EPIC MINER
# =============================================================================

class EpicMiner:
    """
    The Epic Miner: Extracts computational frameworks from narratives.
    
    Implements the 9-pass mining protocol.
    """
    
    def __init__(self):
        self._results: Dict[str, FullMiningResult] = {}
        self._failure_analyzer = FailureAnalyzer()
    
    def mine(self, epic: EpicEntry) -> FullMiningResult:
        """
        Execute full mining protocol on an epic.
        
        Returns complete mining result.
        """
        result = FullMiningResult(epic_name=epic.name)
        
        # Execute all passes
        result.passes[MiningPass.PASS_0_STABILIZATION] = self._pass_0_stabilization(epic)
        result.passes[MiningPass.PASS_1_DECOMPOSITION] = self._pass_1_decomposition(epic)
        result.passes[MiningPass.PASS_2_STATE_SPACE] = self._pass_2_state_space(epic)
        result.passes[MiningPass.PASS_3_ECONOMY] = self._pass_3_economy(epic)
        result.passes[MiningPass.PASS_4_PROTOCOLS] = self._pass_4_protocols(epic)
        result.passes[MiningPass.PASS_5_ERRORS] = self._pass_5_errors(epic)
        result.passes[MiningPass.PASS_6_PATCHES] = self._pass_6_patches(epic)
        result.passes[MiningPass.PASS_7_FORMAL] = self._pass_7_formal(epic, result)
        result.passes[MiningPass.PASS_8_CROSS_EPIC] = self._pass_8_cross_epic(epic)
        result.passes[MiningPass.PASS_9_ENCODING] = self._pass_9_encoding(epic, result)
        
        # Compute completeness
        successful = sum(1 for p in result.passes.values() if p.success)
        result.completeness = successful / 10.0
        
        self._results[epic.name] = result
        
        return result
    
    def _pass_0_stabilization(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 0: Text Stabilization and Boundary Definition.
        
        Create stable, well-defined object of analysis.
        """
        return MiningResult(
            pass_number=MiningPass.PASS_0_STABILIZATION,
            success=True,
            data={
                "epic_name": epic.name,
                "culture": epic.culture,
                "approximate_date": epic.approximate_date,
                "key_agents": epic.key_agents,
                "domain": epic.domain.value
            },
            notes=["Corpus boundaries established", "Segmentation complete"]
        )
    
    def _pass_1_decomposition(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 1: Narrative Decomposition.
        
        Convert story into structured data model.
        """
        # Generate synthetic segments based on epic information
        segments = []
        
        # Opening segment
        segments.append(NarrativeSegment(
            name="opening",
            description=f"Introduction of {epic.key_agents[0] if epic.key_agents else 'protagonist'}",
            agents=epic.key_agents[:2] if len(epic.key_agents) >= 2 else epic.key_agents
        ))
        
        # Challenge segment
        segments.append(NarrativeSegment(
            name="challenge",
            description=epic.objective,
            agents=epic.key_agents
        ))
        
        # Resolution segment
        segments.append(NarrativeSegment(
            name="resolution",
            description=f"Resolution via {epic.patches[0].value if epic.patches else 'unknown means'}",
            agents=epic.key_agents
        ))
        
        return MiningResult(
            pass_number=MiningPass.PASS_1_DECOMPOSITION,
            success=True,
            data={
                "segments": [s.name for s in segments],
                "agent_count": len(epic.key_agents),
                "timeline_type": "linear" if epic.domain != SystemDomain.MIGRATION else "cyclic"
            }
        )
    
    def _pass_2_state_space(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 2: State Space Extraction.
        
        Identify key state variables that the epic tracks.
        """
        state_space = StateSpace(epic)
        
        return MiningResult(
            pass_number=MiningPass.PASS_2_STATE_SPACE,
            success=True,
            data={
                "state_variables": epic.state_variables,
                "domain": epic.domain.value,
                "dimension": state_space.state.dimension
            }
        )
    
    def _pass_3_economy(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 3: Resource, Token, and Economy Modeling.
        
        Identify currencies and how they flow.
        """
        # Infer tokens from epic information
        tokens = []
        
        # Standard tokens by domain
        if epic.domain == SystemDomain.CONFLICT:
            tokens.extend([
                NarrativeToken("kleos", "intangible", "glory/fame", is_conserved=True),
                NarrativeToken("time", "intangible", "honor/respect"),
            ])
        
        elif epic.domain == SystemDomain.MIGRATION:
            tokens.extend([
                NarrativeToken("penates", "tangible", "ancestral gods/identity"),
                NarrativeToken("destination", "intangible", "home/origin"),
            ])
        
        elif epic.domain == SystemDomain.COSMIC:
            tokens.extend([
                NarrativeToken("dharma", "intangible", "cosmic order", is_conserved=True),
                NarrativeToken("karma", "intangible", "action consequences"),
            ])
        
        return MiningResult(
            pass_number=MiningPass.PASS_3_ECONOMY,
            success=True,
            data={
                "tokens": [t.name for t in tokens],
                "conserved_tokens": [t.name for t in tokens if t.is_conserved],
                "zero_sum": epic.domain == SystemDomain.CONFLICT
            }
        )
    
    def _pass_4_protocols(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 4: Protocol Discovery.
        
        Extract explicit and implicit protocols.
        """
        # Infer protocols from information encoded
        protocols = []
        
        for info in epic.information_encoded:
            if "patch" in info.lower() or "protocol" in info.lower():
                protocols.append(info)
        
        return MiningResult(
            pass_number=MiningPass.PASS_4_PROTOCOLS,
            success=True,
            data={
                "protocols_found": len(protocols),
                "protocol_descriptions": protocols,
                "access_roles": ["hero", "king", "priest", "god"]
            }
        )
    
    def _pass_5_errors(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 5: Error and Crash Pattern Extraction.
        
        Diagnose what breaks, how, and why.
        """
        signatures = self._failure_analyzer.analyze_epic(epic)
        
        return MiningResult(
            pass_number=MiningPass.PASS_5_ERRORS,
            success=True,
            data={
                "crash_signatures": [s.name for s in signatures],
                "failure_modes": [f.value for f in epic.failure_modes],
                "severity_distribution": {
                    s.severity.value: 1 for s in signatures
                }
            }
        )
    
    def _pass_6_patches(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 6: Patch and Resolution Modeling.
        
        Model how problems are resolved.
        """
        return MiningResult(
            pass_number=MiningPass.PASS_6_PATCHES,
            success=True,
            data={
                "patches": [p.value for p in epic.patches],
                "patch_count": len(epic.patches),
                "full_resolution": len(epic.patches) > 0
            }
        )
    
    def _pass_7_formal(self, epic: EpicEntry, 
                       result: FullMiningResult) -> MiningResult:
        """
        Pass 7: Formal Modeling.
        
        Build formal mathematical model.
        """
        # Create state machine model
        state_space = StateSpace(epic)
        result.state_space = state_space
        
        # Build transition matrix (simplified)
        dim = state_space.state.dimension
        transition = np.eye(dim)  # Identity base
        
        # Add dynamics based on domain
        if epic.domain == SystemDomain.CONFLICT:
            # Rage escalation dynamics
            transition[0, 0] = 1.1  # Amplification
        
        return MiningResult(
            pass_number=MiningPass.PASS_7_FORMAL,
            success=True,
            data={
                "state_dimension": dim,
                "transition_matrix_shape": transition.shape,
                "dynamics_type": "amplifying" if epic.domain == SystemDomain.CONFLICT else "stable"
            }
        )
    
    def _pass_8_cross_epic(self, epic: EpicEntry) -> MiningResult:
        """
        Pass 8: Cross-Epic Pattern Recognition.
        
        Place epic in larger meta-framework.
        """
        # Find similar epics
        similar = []
        
        for other in EPIC_REGISTRY:
            if other.name == epic.name:
                continue
            
            # Check domain match
            if other.domain == epic.domain:
                similar.append(other.name)
            
            # Check failure mode overlap
            overlap = set(epic.failure_modes) & set(other.failure_modes)
            if overlap:
                similar.append(other.name)
        
        return MiningResult(
            pass_number=MiningPass.PASS_8_CROSS_EPIC,
            success=True,
            data={
                "similar_epics": list(set(similar)),
                "domain_category": epic.domain.value,
                "unique_contribution": epic.system_designation
            }
        )
    
    def _pass_9_encoding(self, epic: EpicEntry,
                         result: FullMiningResult) -> MiningResult:
        """
        Pass 9: Epic-to-Protocol Document Encoding.
        
        Express mined framework as protocol document.
        """
        # Build protocol
        protocol = Protocol(
            name=epic.get_protocol_name(),
            epic_source=epic.name,
            system_designation=epic.system_designation,
            domain=epic.domain,
            objective=epic.objective,
            state_variables=epic.state_variables,
            agents=epic.key_agents,
            failure_modes=epic.failure_modes,
            patches=epic.patches
        )
        
        # Add invariants from information encoded
        for i, info in enumerate(epic.information_encoded):
            protocol.invariants.append(Invariant(
                name=f"invariant_{i}",
                description=info,
                violation_consequence="System failure"
            ))
        
        result.protocol = protocol
        
        return MiningResult(
            pass_number=MiningPass.PASS_9_ENCODING,
            success=True,
            data={
                "protocol_name": protocol.name,
                "objective": protocol.objective,
                "invariant_count": len(protocol.invariants)
            }
        )
    
    def get_result(self, epic_name: str) -> Optional[FullMiningResult]:
        """Get mining result for an epic."""
        return self._results.get(epic_name)
    
    def mine_all(self) -> Dict[str, FullMiningResult]:
        """Mine all epics in the registry."""
        for epic in EPIC_REGISTRY:
            self.mine(epic)
        return self._results
    
    def get_cross_epic_patterns(self) -> Dict:
        """
        Extract patterns that appear across multiple epics.
        
        Returns the universal patterns and invariants.
        """
        patterns = {
            "by_domain": {},
            "by_failure_mode": {},
            "universal_invariants": []
        }
        
        # Group by domain
        for domain in SystemDomain:
            epics = EPIC_REGISTRY.get_by_domain(domain)
            if epics:
                patterns["by_domain"][domain.value] = [e.name for e in epics]
        
        # Group by failure mode
        for mode in FailureCategory:
            epics = EPIC_REGISTRY.get_by_failure_mode(mode)
            if epics:
                patterns["by_failure_mode"][mode.value] = [e.name for e in epics]
        
        # Universal invariants (appear in multiple epics)
        patterns["universal_invariants"] = [
            "Mortality awareness enables de-escalation",
            "Identity must be actively preserved against forgetting",
            "Recursive threat escalation (defeating one spawns another)",
            "Soft persistence outlasts hard persistence",
            "System reset required when constraints irreparably violated"
        ]
        
        return patterns


# =============================================================================
# VALIDATION
# =============================================================================

def validate_mining() -> bool:
    """Validate mining module."""
    
    # Test NarrativeSegment
    segment = NarrativeSegment(
        name="test_segment",
        description="Test description",
        agents=["agent1", "agent2"]
    )
    
    assert segment.name == "test_segment"
    
    # Test NarrativeToken
    token = NarrativeToken(
        name="test_token",
        token_type="tangible",
        holder="agent1"
    )
    
    token.transfer("agent1", "agent2", "gift")
    assert token.holder == "agent2"
    assert len(token.transfers) == 1
    
    # Test EpicMiner
    miner = EpicMiner()
    
    gilgamesh = EPIC_REGISTRY.get("Epic of Gilgamesh")
    assert gilgamesh is not None
    
    result = miner.mine(gilgamesh)
    
    assert result.epic_name == "Epic of Gilgamesh"
    assert result.is_complete()
    assert result.completeness == 1.0
    
    # Check all passes
    for pass_type in MiningPass:
        assert pass_type in result.passes
        assert result.passes[pass_type].success
    
    # Check outputs
    assert result.protocol is not None
    assert result.protocol.name == "EPIC_OF_GILGAMESH_PROTOCOL"
    
    # Test mining multiple epics
    iliad = EPIC_REGISTRY.get("Iliad")
    iliad_result = miner.mine(iliad)
    
    assert iliad_result.is_complete()
    
    # Test cross-epic patterns
    patterns = miner.get_cross_epic_patterns()
    
    assert "by_domain" in patterns
    assert "by_failure_mode" in patterns
    assert "universal_invariants" in patterns
    
    return True


if __name__ == "__main__":
    print("Validating Mining Module...")
    assert validate_mining()
    print("✓ Mining Module validated")
    
    # Demo mining
    print("\n--- Mining Demo ---")
    miner = EpicMiner()
    
    for epic in list(EPIC_REGISTRY)[:3]:
        result = miner.mine(epic)
        print(f"\n{epic.name}:")
        print(f"  Completeness: {result.completeness:.0%}")
        print(f"  Protocol: {result.protocol.name if result.protocol else 'None'}")
