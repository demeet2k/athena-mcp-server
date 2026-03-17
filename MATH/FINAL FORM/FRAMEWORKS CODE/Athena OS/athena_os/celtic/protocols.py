"""
ATHENA OS - CELTIC OGHAM KERNEL: PROTOCOLS MODULE
==================================================
Geis, Ríastrad, Satire, and Sovereignty Protocols

GEIS (Taboo) - Hard-Coded Boundary Condition:
    IF (Action == Geis) THEN (State = Terminated)
    
    Specific to individual agents.
    Violation triggers immediate SYSTEM_HALT.
    
RÍASTRAD (Warp Spasm) - Biomechanical Overclocking:
    Temporarily bypasses safety governors to maximize
    kinetic output at cost of structural integrity.
    
    T_sys → ∞ (thermal runaway risk)
    
SATIRE (Glám Dícenn) - Zero-Day Exploit:
    Adversarial payload injection.
    Compiles error into high-density acoustic packet.
    Targets reputation/integrity vectors.
    
SOVEREIGNTY (Hieros Gamos) - Thermodynamic Feedback Loop:
    Connects processing node (King) to physical hardware (Land).
    System stability contingent on coupling integrity.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import numpy as np
import hashlib
import time


# =============================================================================
# GEIS (TABOO) SYSTEM
# =============================================================================

class GeisType(Enum):
    """Types of Geis (taboo/prohibition)."""
    
    ACTION = "action"              # Forbidden action
    OBJECT = "object"              # Forbidden object
    LOCATION = "location"          # Forbidden place
    TIME = "time"                  # Forbidden time
    PERSON = "person"              # Forbidden interaction
    COMPOUND = "compound"          # Multiple conditions


@dataclass
class Geis:
    """
    A Geis - Hard-Coded Boundary Condition.
    
    Personal taboo that constrains agent behavior.
    Violation triggers immediate termination.
    
    IF (Action == Geis) THEN (State = Terminated)
    """
    
    id: str
    description: str
    geis_type: GeisType
    
    # The forbidden condition
    condition: Callable[[Any], bool] = None
    trigger_pattern: str = ""
    
    # Consequences
    consequence: str = "termination"
    severity: float = 1.0          # 0-1
    
    # State
    is_active: bool = True
    violations: int = 0
    
    def check(self, action: Any) -> bool:
        """
        Check if action violates this geis.
        
        Returns True if violated.
        """
        if not self.is_active:
            return False
        
        if self.condition:
            return self.condition(action)
        
        # String pattern matching
        if self.trigger_pattern:
            action_str = str(action).lower()
            return self.trigger_pattern.lower() in action_str
        
        return False
    
    def violate(self) -> Dict[str, Any]:
        """Record a violation and return consequence."""
        self.violations += 1
        
        return {
            "geis_id": self.id,
            "description": self.description,
            "consequence": self.consequence,
            "severity": self.severity,
            "total_violations": self.violations,
            "state": "TERMINATED" if self.severity >= 1.0 else "DAMAGED"
        }


class GeisManager:
    """
    Manages Geis constraints for agents.
    
    Each agent has personal geis that must not be violated.
    """
    
    def __init__(self):
        self.agent_geis: Dict[str, List[Geis]] = {}
        self.violation_log: List[Dict[str, Any]] = []
    
    def add_geis(self, agent_id: str, geis: Geis) -> None:
        """Add a geis to an agent."""
        if agent_id not in self.agent_geis:
            self.agent_geis[agent_id] = []
        
        self.agent_geis[agent_id].append(geis)
    
    def check_action(self, agent_id: str, action: Any) -> Tuple[bool, Optional[Dict]]:
        """
        Check if action violates any of agent's geis.
        
        Returns (is_permitted, violation_info).
        """
        if agent_id not in self.agent_geis:
            return True, None  # No geis = all permitted
        
        for geis in self.agent_geis[agent_id]:
            if geis.check(action):
                violation = geis.violate()
                violation["agent_id"] = agent_id
                violation["action"] = str(action)[:50]
                
                self.violation_log.append(violation)
                
                return False, violation
        
        return True, None
    
    def get_agent_geis(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all geis for an agent."""
        if agent_id not in self.agent_geis:
            return []
        
        return [{
            "id": g.id,
            "description": g.description,
            "type": g.geis_type.value,
            "severity": g.severity,
            "active": g.is_active
        } for g in self.agent_geis[agent_id]]


# =============================================================================
# RÍASTRAD (WARP SPASM) - OVERCLOCKING
# =============================================================================

class RiastradState(Enum):
    """States of Ríastrad (warp spasm)."""
    
    DORMANT = "dormant"            # Normal operation
    TRIGGERING = "triggering"      # Activation beginning
    ACTIVE = "active"              # Full warp spasm
    PEAK = "peak"                  # Maximum output
    COOLING = "cooling"            # Coming down
    EXHAUSTED = "exhausted"        # Post-spasm recovery


@dataclass
class RiastradMetrics:
    """Metrics during Ríastrad activation."""
    
    power_output: float = 1.0      # Multiplier on normal
    temperature: float = 1.0       # Thermal state (danger > 2.0)
    stability: float = 1.0         # Structural integrity
    duration: float = 0.0          # Time in state
    
    max_duration: float = 10.0     # Safety limit
    thermal_limit: float = 3.0     # Thermal runaway threshold


class Riastrad:
    """
    Ríastrad (Warp Spasm) - Biomechanical Overclocking Protocol.
    
    Temporarily bypasses safety governors to maximize
    kinetic output at cost of structural integrity.
    
    Risk: T_sys → ∞ (thermal runaway)
    
    Based on Cú Chulainn's battle transformation.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = RiastradState.DORMANT
        self.metrics = RiastradMetrics()
        
        # Configuration
        self.max_power_multiplier: float = 5.0
        self.heat_generation_rate: float = 0.3
        self.stability_decay_rate: float = 0.1
        
        # History
        self.activation_count: int = 0
        self.total_damage: float = 0.0
    
    def trigger(self) -> Dict[str, Any]:
        """
        Trigger the Ríastrad.
        
        Warning: Bypasses safety governors.
        """
        if self.state != RiastradState.DORMANT:
            return {"error": "Already in non-dormant state"}
        
        self.state = RiastradState.TRIGGERING
        self.activation_count += 1
        
        # Begin power ramp
        self.metrics.power_output = 1.5
        self.metrics.temperature = 1.2
        
        return {
            "status": "triggering",
            "agent": self.agent_id,
            "power": self.metrics.power_output,
            "warning": "Safety governors bypassed"
        }
    
    def activate(self) -> Dict[str, Any]:
        """Full activation of Ríastrad."""
        if self.state != RiastradState.TRIGGERING:
            return {"error": "Must trigger first"}
        
        self.state = RiastradState.ACTIVE
        
        # Maximum power
        self.metrics.power_output = self.max_power_multiplier
        self.metrics.temperature = 2.0
        self.metrics.stability = 0.8
        
        return {
            "status": "active",
            "power_multiplier": self.metrics.power_output,
            "temperature": self.metrics.temperature,
            "warning": "CRITICAL: High thermal state"
        }
    
    def update(self, dt: float) -> Dict[str, Any]:
        """Update Ríastrad state over time."""
        if self.state in [RiastradState.DORMANT, RiastradState.EXHAUSTED]:
            return {"status": self.state.value}
        
        self.metrics.duration += dt
        
        # Heat accumulation
        if self.state in [RiastradState.ACTIVE, RiastradState.PEAK]:
            self.metrics.temperature += self.heat_generation_rate * dt
            self.metrics.stability -= self.stability_decay_rate * dt
        
        # Check for peak
        if (self.state == RiastradState.ACTIVE and 
            self.metrics.temperature >= 2.5):
            self.state = RiastradState.PEAK
        
        # Check for thermal runaway
        if self.metrics.temperature >= self.metrics.thermal_limit:
            return self._thermal_failure()
        
        # Check for duration limit
        if self.metrics.duration >= self.metrics.max_duration:
            return self._forced_cooling()
        
        # Check stability failure
        if self.metrics.stability <= 0:
            return self._structural_failure()
        
        return {
            "status": self.state.value,
            "power": self.metrics.power_output,
            "temperature": self.metrics.temperature,
            "stability": self.metrics.stability,
            "duration": self.metrics.duration
        }
    
    def deactivate(self) -> Dict[str, Any]:
        """Voluntarily deactivate Ríastrad."""
        if self.state not in [RiastradState.ACTIVE, RiastradState.PEAK]:
            return {"status": "not_active"}
        
        self.state = RiastradState.COOLING
        damage = self._calculate_damage()
        
        return {
            "status": "cooling",
            "damage_sustained": damage,
            "recovery_time": self.metrics.duration * 2
        }
    
    def _thermal_failure(self) -> Dict[str, Any]:
        """Handle thermal runaway."""
        self.state = RiastradState.EXHAUSTED
        damage = 0.5  # Severe damage
        self.total_damage += damage
        
        return {
            "status": "THERMAL_FAILURE",
            "damage": damage,
            "warning": "Thermal runaway - system critically damaged"
        }
    
    def _structural_failure(self) -> Dict[str, Any]:
        """Handle structural collapse."""
        self.state = RiastradState.EXHAUSTED
        damage = 0.7  # Critical damage
        self.total_damage += damage
        
        return {
            "status": "STRUCTURAL_FAILURE",
            "damage": damage,
            "warning": "Structural integrity lost"
        }
    
    def _forced_cooling(self) -> Dict[str, Any]:
        """Handle forced cooling due to duration limit."""
        self.state = RiastradState.COOLING
        damage = self._calculate_damage()
        
        return {
            "status": "forced_cooling",
            "reason": "Duration limit exceeded",
            "damage": damage
        }
    
    def _calculate_damage(self) -> float:
        """Calculate damage from Ríastrad use."""
        temp_damage = max(0, (self.metrics.temperature - 1.5) * 0.2)
        stability_damage = max(0, (1 - self.metrics.stability) * 0.3)
        
        total = temp_damage + stability_damage
        self.total_damage += total
        
        return total
    
    def reset(self) -> None:
        """Reset to dormant state after recovery."""
        self.state = RiastradState.DORMANT
        self.metrics = RiastradMetrics()


# =============================================================================
# SATIRE (GLÁM DÍCENN) - ZERO-DAY EXPLOIT
# =============================================================================

@dataclass
class SatirePayload:
    """
    Satire attack payload.
    
    High-density acoustic packet encoding logical errors.
    """
    
    target_flaw: str               # The weakness being exploited
    rhyme_scheme: str              # Checksum for delivery
    power_level: int = 3           # 1-7 (number of verses)
    
    # Compiled payload
    verses: List[str] = field(default_factory=list)
    hash_signature: str = ""
    
    def compile(self) -> None:
        """Compile the satire payload."""
        # Generate verses attacking the flaw
        self.verses = [
            f"Verse {i+1}: The flaw of {self.target_flaw}"
            for i in range(self.power_level)
        ]
        
        # Generate hash for verification
        content = ''.join(self.verses)
        self.hash_signature = hashlib.md5(content.encode()).hexdigest()[:8]


class SatireSystem:
    """
    The Satire System (Glám Dícenn) - Zero-Day Exploit.
    
    Adversarial payload injection targeting reputation/integrity.
    
    Protocol:
    1. Identify Flaw (Research Phase)
    2. Compile Payload (Rhyming couplet encoding)
    3. Broadcast (Bardic Network transmission)
    4. Verify Impact (Check for blemish)
    
    Risk: If target is righteous, satire rebounds on initiator.
    """
    
    def __init__(self):
        self.active_attacks: Dict[str, SatirePayload] = {}
        self.attack_log: List[Dict[str, Any]] = []
    
    def identify_flaw(self, target_id: str, 
                      target_data: Dict[str, Any]) -> Optional[str]:
        """
        Identify exploitable flaw in target.
        
        Research Phase: Find weakness.
        """
        flaws = []
        
        # Check various weakness categories
        if target_data.get("integrity", 1.0) < 0.8:
            flaws.append("compromised_integrity")
        
        if target_data.get("legitimacy", 1.0) < 0.5:
            flaws.append("illegitimate_authority")
        
        if target_data.get("broken_oaths"):
            flaws.append("oath_breaker")
        
        if target_data.get("injustice"):
            flaws.append("unjust_ruler")
        
        return flaws[0] if flaws else None
    
    def compile_satire(self, target_id: str, flaw: str,
                       power_level: int = 3) -> SatirePayload:
        """
        Compile satire payload.
        
        Creates high-density acoustic packet.
        """
        payload = SatirePayload(
            target_flaw=flaw,
            rhyme_scheme="AABB",
            power_level=power_level
        )
        
        payload.compile()
        self.active_attacks[target_id] = payload
        
        return payload
    
    def broadcast(self, target_id: str) -> Dict[str, Any]:
        """
        Broadcast satire via Bardic Network.
        
        Transmit payload to target.
        """
        if target_id not in self.active_attacks:
            return {"error": "No compiled payload for target"}
        
        payload = self.active_attacks[target_id]
        
        return {
            "status": "broadcast",
            "target": target_id,
            "verses": payload.power_level,
            "hash": payload.hash_signature,
            "flaw_targeted": payload.target_flaw
        }
    
    def verify_impact(self, target_id: str,
                      target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if satire had effect.
        
        Check Target_Node for Blemish_Status.
        """
        if target_id not in self.active_attacks:
            return {"error": "No active attack on target"}
        
        payload = self.active_attacks[target_id]
        
        # Determine success based on target's true state
        target_integrity = target_data.get("integrity", 1.0)
        target_righteousness = target_data.get("righteousness", 0.5)
        
        # If target is righteous, satire fails and rebounds
        if target_righteousness > 0.7:
            result = {
                "success": False,
                "blemish_applied": False,
                "reason": "Target is righteous",
                "rebound": True,
                "rebound_damage": payload.power_level * 0.1
            }
        else:
            # Calculate blemish based on payload power and flaw severity
            blemish_strength = payload.power_level * 0.15 * (1 - target_integrity)
            
            result = {
                "success": True,
                "blemish_applied": True,
                "blemish_strength": blemish_strength,
                "effect": "Reputation damaged",
                "rebound": False
            }
            
            if blemish_strength > 0.5:
                result["abdication_triggered"] = True
        
        # Log attack
        self.attack_log.append({
            "target": target_id,
            "flaw": payload.target_flaw,
            "result": result
        })
        
        # Clear attack
        del self.active_attacks[target_id]
        
        return result


# =============================================================================
# SOVEREIGNTY (HIEROS GAMOS)
# =============================================================================

@dataclass
class SovereigntyBond:
    """
    The bond between Sovereign and Land.
    
    Thermodynamic feedback loop where system stability
    depends on coupling integrity.
    """
    
    sovereign_id: str
    land_id: str
    
    # Bond strength
    strength: float = 1.0          # 0-1
    harmony: float = 1.0           # Alignment
    
    # Effects
    land_fertility: float = 1.0
    sovereign_power: float = 1.0
    
    # Tracking
    bond_age: float = 0.0
    stresses: int = 0


class SovereigntySystem:
    """
    Sovereignty (Hieros Gamos) - Thermodynamic Feedback Loop.
    
    Connects processing node (King) to physical hardware (Land).
    System stability contingent on coupling integrity.
    
    If King is unfit → Land becomes barren
    If Land is damaged → King loses power
    """
    
    def __init__(self):
        self.bonds: Dict[str, SovereigntyBond] = {}
    
    def create_bond(self, sovereign_id: str, land_id: str) -> SovereigntyBond:
        """
        Create sovereignty bond (Hieros Gamos).
        
        The sacred marriage of King and Land.
        """
        bond = SovereigntyBond(
            sovereign_id=sovereign_id,
            land_id=land_id
        )
        
        bond_key = f"{sovereign_id}:{land_id}"
        self.bonds[bond_key] = bond
        
        return bond
    
    def update_bond(self, sovereign_id: str, land_id: str,
                    sovereign_state: Dict[str, Any],
                    land_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update bond based on current states.
        
        Implements feedback loop.
        """
        bond_key = f"{sovereign_id}:{land_id}"
        
        if bond_key not in self.bonds:
            return {"error": "Bond not found"}
        
        bond = self.bonds[bond_key]
        
        # Get states
        sov_integrity = sovereign_state.get("integrity", 1.0)
        sov_justice = sovereign_state.get("justice", 0.5)
        land_health = land_state.get("health", 1.0)
        
        # Calculate harmony (alignment between sovereign and land)
        bond.harmony = (sov_integrity * sov_justice * land_health) ** (1/3)
        
        # Update effects
        # If sovereign is unfit → land suffers
        if sov_integrity < 0.5:
            bond.land_fertility = sov_integrity
        else:
            bond.land_fertility = min(1.0, bond.land_fertility + 0.1)
        
        # If land is damaged → sovereign loses power
        if land_health < 0.5:
            bond.sovereign_power = land_health
        else:
            bond.sovereign_power = min(1.0, bond.sovereign_power + 0.1)
        
        # Update bond strength
        bond.strength = (bond.land_fertility + bond.sovereign_power) / 2
        
        return {
            "bond_strength": bond.strength,
            "harmony": bond.harmony,
            "land_fertility": bond.land_fertility,
            "sovereign_power": bond.sovereign_power,
            "stable": bond.strength > 0.5
        }
    
    def check_stability(self, sovereign_id: str, 
                        land_id: str) -> Dict[str, Any]:
        """Check if sovereignty is stable."""
        bond_key = f"{sovereign_id}:{land_id}"
        
        if bond_key not in self.bonds:
            return {"error": "Bond not found", "stable": False}
        
        bond = self.bonds[bond_key]
        
        stable = bond.strength > 0.5 and bond.harmony > 0.3
        
        warnings = []
        if bond.land_fertility < 0.5:
            warnings.append("Land fertility declining")
        if bond.sovereign_power < 0.5:
            warnings.append("Sovereign power weakening")
        if bond.harmony < 0.3:
            warnings.append("Disharmony between King and Land")
        
        return {
            "stable": stable,
            "strength": bond.strength,
            "warnings": warnings,
            "recommendation": "Remove unfit sovereign" if not stable else "Continue reign"
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_protocols() -> bool:
    """Validate protocols module."""
    
    # Test Geis System
    geis_mgr = GeisManager()
    
    geis = Geis(
        id="test_geis",
        description="Never eat dog meat",
        geis_type=GeisType.ACTION,
        trigger_pattern="dog meat"
    )
    
    geis_mgr.add_geis("hero", geis)
    
    permitted, violation = geis_mgr.check_action("hero", "eat bread")
    assert permitted
    
    permitted, violation = geis_mgr.check_action("hero", "eat dog meat")
    assert not permitted
    assert violation["state"] == "TERMINATED"
    
    # Test Ríastrad
    riastrad = Riastrad("warrior")
    
    result = riastrad.trigger()
    assert result["status"] == "triggering"
    
    result = riastrad.activate()
    assert result["status"] == "active"
    assert result["power_multiplier"] == 5.0
    
    result = riastrad.update(1.0)
    assert riastrad.metrics.temperature > 2.0
    
    result = riastrad.deactivate()
    assert result["status"] == "cooling"
    
    # Test Satire
    satire = SatireSystem()
    
    target_data = {"integrity": 0.3, "righteousness": 0.2}
    flaw = satire.identify_flaw("corrupt_king", target_data)
    assert flaw is not None
    
    payload = satire.compile_satire("corrupt_king", flaw, power_level=5)
    assert len(payload.verses) == 5
    
    broadcast = satire.broadcast("corrupt_king")
    assert broadcast["status"] == "broadcast"
    
    impact = satire.verify_impact("corrupt_king", target_data)
    assert impact["success"]
    assert impact["blemish_applied"]
    
    # Test Sovereignty
    sov = SovereigntySystem()
    
    bond = sov.create_bond("king", "ireland")
    assert bond.strength == 1.0
    
    # Good king
    result = sov.update_bond(
        "king", "ireland",
        {"integrity": 0.9, "justice": 0.8},
        {"health": 0.9}
    )
    assert result["stable"]
    
    # Bad king
    result = sov.update_bond(
        "king", "ireland",
        {"integrity": 0.2, "justice": 0.3},
        {"health": 0.9}
    )
    # Land should suffer
    assert result["land_fertility"] < 0.5
    
    return True


if __name__ == "__main__":
    print("Validating Protocols Module...")
    assert validate_protocols()
    print("✓ Protocols Module validated")
    
    # Demo
    print("\n--- Geis Demo ---")
    geis_mgr = GeisManager()
    
    cu_chulainn_geis = [
        Geis("g1", "Never refuse hospitality", GeisType.ACTION, trigger_pattern="refuse"),
        Geis("g2", "Never eat dog meat", GeisType.ACTION, trigger_pattern="dog"),
        Geis("g3", "Never pass a cooking fire", GeisType.ACTION, trigger_pattern="pass fire"),
    ]
    
    for g in cu_chulainn_geis:
        geis_mgr.add_geis("cu_chulainn", g)
    
    print("Cú Chulainn's Geis:")
    for g in geis_mgr.get_agent_geis("cu_chulainn"):
        print(f"  - {g['description']}")
    
    print("\n--- Ríastrad Demo ---")
    riastrad = Riastrad("cu_chulainn")
    print(f"Initial state: {riastrad.state.value}")
    
    riastrad.trigger()
    riastrad.activate()
    print(f"Active - Power: {riastrad.metrics.power_output}x")
    print(f"Temperature: {riastrad.metrics.temperature}")
    
    riastrad.update(2.0)
    print(f"After 2s - Temperature: {riastrad.metrics.temperature:.1f}")
    
    print("\n--- Sovereignty Demo ---")
    sov = SovereigntySystem()
    bond = sov.create_bond("high_king", "erin")
    
    result = sov.update_bond(
        "high_king", "erin",
        {"integrity": 0.95, "justice": 0.9},
        {"health": 0.85}
    )
    print(f"Bond Strength: {result['bond_strength']:.2f}")
    print(f"Land Fertility: {result['land_fertility']:.2f}")
    print(f"Stable: {result['stable']}")
