"""
ATHENA OS - ZOROASTRIAN: FRASHOKERETI MODULE
=============================================
Terminal Event and Final Renormalization

FRASHOKERETI: "The Making Wonderful"
    The terminal event at t = 12,000.
    Final renormalization where Noise (|-1⟩) is
    permanently purged, freezing the system into
    permanent |+1⟩ state.

CHINVAT BRIDGE:
    The LINEAR CLASSIFIER determining final routing
    of agent data. Bridge is "sword-wide" for the
    corrupt, "nine spear-widths" for the righteous.

THE MOLTEN METAL TEST:
    Global THERMAL STRESS TEST at final judgment.
    - Agent = Asha (Truth): Metal feels like warm milk (R ≈ 0)
    - Agent = Druj (Lie): Metal consumes them (R → ∞)
    
    Effectively BURNS OFF the noise, leaving pure |+1⟩ lattice.

FINAL RENORMALIZATION:
    - Topology Change: Earth flattened, Graph → Complete Graph K_N
    - Zero Impedance between all nodes
    - State Freeze: t → ∞, permanent steady state
    - No further updates permitted

HAMISTAGAN (Edge Case):
    Buffer for V = 0 (exactly equal good/evil)
    Agent waits until Frashokereti forces resolution to |+1⟩
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .soul_stack import ZoroastrianSoul, Daena


# =============================================================================
# JUDGMENT OUTCOMES
# =============================================================================

class JudgmentOutcome(Enum):
    """Possible outcomes of Chinvat Bridge judgment."""
    
    GARONMANA = "garonmana"       # House of Song (Heaven)
    HAMISTAGAN = "hamistagan"     # Limbo (V = 0)
    DRUJO_DEMANA = "drujo_demana" # House of Lies (Hell)


# =============================================================================
# CHINVAT BRIDGE
# =============================================================================

class ChinvatBridge:
    """
    The Chinvat Bridge: Linear Classifier.
    
    Determines final routing based on net karmic value.
    Bridge width varies with righteousness:
    - Corrupt: Sword-wide (falls)
    - Righteous: Nine spear-widths (crosses)
    """
    
    # Classification thresholds
    POSITIVE_THRESHOLD = 0.01    # V > 0 → Heaven
    NEGATIVE_THRESHOLD = -0.01   # V < 0 → Hell
    # |V| <= threshold → Hamistagan
    
    def __init__(self):
        self._judgments_made = 0
        self._outcomes: Dict[JudgmentOutcome, int] = {
            JudgmentOutcome.GARONMANA: 0,
            JudgmentOutcome.HAMISTAGAN: 0,
            JudgmentOutcome.DRUJO_DEMANA: 0
        }
    
    def compute_net_value(self, daena: Daena) -> float:
        """Compute net value from Daena record."""
        return daena.compute_net_value()
    
    def classify(self, net_value: float) -> JudgmentOutcome:
        """
        Classify based on net value.
        
        V > 0: Heaven (Garonmana)
        V < 0: Hell (Drujo Demana)
        V = 0: Limbo (Hamistagan)
        """
        if net_value > self.POSITIVE_THRESHOLD:
            return JudgmentOutcome.GARONMANA
        elif net_value < self.NEGATIVE_THRESHOLD:
            return JudgmentOutcome.DRUJO_DEMANA
        else:
            return JudgmentOutcome.HAMISTAGAN
    
    def compute_bridge_width(self, net_value: float) -> float:
        """
        Compute effective bridge width.
        
        Higher net value = wider bridge.
        """
        # Sigmoid-like mapping
        return 1.0 / (1.0 + np.exp(-net_value * 5))
    
    def judge(self, soul: ZoroastrianSoul) -> Dict:
        """
        Perform complete judgment on a soul.
        
        Returns judgment report.
        """
        # Get Daena record
        daena = soul.daena
        
        # Compute net value
        net_value = self.compute_net_value(daena)
        
        # Classify
        outcome = self.classify(net_value)
        
        # Compute bridge width
        bridge_width = self.compute_bridge_width(net_value)
        
        # Record
        self._judgments_made += 1
        self._outcomes[outcome] += 1
        
        return {
            "soul": soul.name,
            "net_value": net_value,
            "outcome": outcome.value,
            "bridge_width": bridge_width,
            "daena_summary": daena.get_summary(),
            "crossed_successfully": outcome != JudgmentOutcome.DRUJO_DEMANA
        }
    
    @property
    def judgments_made(self) -> int:
        return self._judgments_made
    
    @property
    def outcome_counts(self) -> Dict[str, int]:
        return {k.value: v for k, v in self._outcomes.items()}


# =============================================================================
# MOLTEN METAL TEST
# =============================================================================

class MoltenMetalTest:
    """
    The Molten Metal Test: Global Thermal Stress Test.
    
    Final sorting algorithm at Frashokereti.
    Burns off |-1⟩ states, leaving pure |+1⟩.
    """
    
    def __init__(self, temperature: float = 1000.0):
        self.temperature = temperature
        self._tests_performed = 0
        self._purified = 0
        self._consumed = 0
    
    def compute_resistance(self, alignment: float) -> float:
        """
        Compute thermal resistance.
        
        High alignment (Asha) → Low resistance (warm milk)
        Low alignment (Druj) → High resistance (consumed)
        """
        # Invert alignment to get resistance
        # alignment 1.0 → resistance ~0
        # alignment -1.0 → resistance → ∞
        if alignment >= 0.99:
            return 0.01  # Nearly zero
        elif alignment <= -0.99:
            return float('inf')  # Infinite
        else:
            return 1.0 / (alignment + 1.001)
    
    def test_soul(self, soul: ZoroastrianSoul) -> Dict:
        """
        Subject a soul to the molten metal test.
        
        Returns test results.
        """
        self._tests_performed += 1
        
        # Get alignment
        alignment = soul.urvan.get_alignment()
        net_karma = soul.daena.compute_net_value()
        
        # Combined score
        combined = (alignment + np.tanh(net_karma)) / 2
        
        # Compute resistance
        resistance = self.compute_resistance(combined)
        
        # Determine outcome
        if resistance < 1.0:
            # Passes through - feels like warm milk
            self._purified += 1
            experience = "warm_milk"
            survives = True
        elif resistance == float('inf'):
            # Consumed entirely
            self._consumed += 1
            experience = "consumed"
            survives = False
        else:
            # Partial damage
            experience = "painful_but_survives"
            survives = True
        
        return {
            "soul": soul.name,
            "alignment": alignment,
            "net_karma": net_karma,
            "combined_score": combined,
            "resistance": resistance if resistance != float('inf') else "infinite",
            "experience": experience,
            "survives": survives
        }
    
    def purify_vector(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Apply thermal purification to state vector.
        
        Burns off negative components.
        """
        # High temperature removes negative values
        result = state_vector.copy()
        result[result < 0] = 0  # Burn off negative
        
        # Normalize to maintain magnitude
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm
        
        return result
    
    @property
    def tests_performed(self) -> int:
        return self._tests_performed
    
    @property
    def statistics(self) -> Dict:
        return {
            "tests_performed": self._tests_performed,
            "purified": self._purified,
            "consumed": self._consumed,
            "purification_rate": self._purified / max(1, self._tests_performed)
        }


# =============================================================================
# HAMISTAGAN (LIMBO)
# =============================================================================

class Hamistagan:
    """
    Hamistagan: The Place of the Mixed / Exception Handler.
    
    Buffer for souls with V = 0 (exactly equal good and evil).
    Agent remains here until Frashokereti forces resolution.
    
    Thermodynamic stasis: d(Experience)/dt = 0
    """
    
    def __init__(self):
        self._residents: List[str] = []
        self._entry_times: Dict[str, float] = {}
    
    def admit(self, soul_name: str, entry_time: float) -> None:
        """Admit a soul to Hamistagan."""
        if soul_name not in self._residents:
            self._residents.append(soul_name)
            self._entry_times[soul_name] = entry_time
    
    def release_at_frashokereti(self) -> List[str]:
        """
        Release all souls at Frashokereti.
        
        They are forced to |+1⟩ state.
        """
        released = self._residents.copy()
        self._residents.clear()
        self._entry_times.clear()
        return released
    
    def get_experience(self, soul_name: str) -> Dict:
        """
        Get current experience in Hamistagan.
        
        No reward, no punishment - pure stasis.
        """
        if soul_name not in self._residents:
            return {"error": "Soul not in Hamistagan"}
        
        return {
            "state": "STASIS",
            "experience_rate": 0.0,
            "reward": 0.0,
            "punishment": 0.0,
            "waiting_for": "FRASHOKERETI"
        }
    
    @property
    def n_residents(self) -> int:
        return len(self._residents)
    
    @property
    def residents(self) -> List[str]:
        return self._residents.copy()


# =============================================================================
# GARONMANA (HOUSE OF SONG)
# =============================================================================

@dataclass
class Garonmana:
    """
    Garonmana: The House of Song (Heaven).
    
    Final state for righteous souls:
    - Harmonic resonance with Kernel
    - ω_Agent = ω_Kernel (Zero impedance)
    - Infinite energy transfer
    - Maximum bandwidth (Endless Light)
    """
    
    # Properties
    light_intensity: float = float('inf')
    bandwidth: float = float('inf')
    impedance: float = 0.0
    
    # Residents
    _residents: List[str] = field(default_factory=list)
    
    def admit(self, soul_name: str) -> Dict:
        """Admit a soul to Garonmana."""
        self._residents.append(soul_name)
        
        return {
            "admitted": soul_name,
            "state": "HARMONIC_RESONANCE",
            "frequency_alignment": "PERFECT",
            "experience": "ENDLESS_LIGHT",
            "bandwidth": "INFINITE"
        }
    
    def get_experience(self) -> Dict:
        """Get experience description in Garonmana."""
        return {
            "light": "Endless",
            "frequency": "ω_Agent = ω_Kernel",
            "impedance": "Zero",
            "energy_transfer": "Infinite",
            "state": "Permanent bliss"
        }
    
    @property
    def n_residents(self) -> int:
        return len(self._residents)


# =============================================================================
# FRASHOKERETI ENGINE
# =============================================================================

class FrashokertiEngine:
    """
    The Frashokereti Engine: Terminal Event Manager.
    
    Executes the "Making Wonderful" - final renormalization
    of the cosmos at t = 12,000.
    """
    
    def __init__(self):
        # Components
        self.chinvat_bridge = ChinvatBridge()
        self.molten_metal = MoltenMetalTest()
        self.hamistagan = Hamistagan()
        self.garonmana = Garonmana()
        
        # State
        self._initiated = False
        self._completed = False
        self._souls_processed = 0
    
    def initiate(self) -> Dict:
        """Initiate Frashokereti sequence."""
        if self._initiated:
            return {"error": "Already initiated"}
        
        self._initiated = True
        
        return {
            "status": "FRASHOKERETI_INITIATED",
            "message": "The Making Wonderful begins",
            "stages": [
                "1. Chinvat Bridge judgment",
                "2. Molten Metal purification",
                "3. Hamistagan release",
                "4. Final renormalization",
                "5. Eternal state freeze"
            ]
        }
    
    def process_soul(self, soul: ZoroastrianSoul) -> Dict:
        """
        Process a soul through Frashokereti.
        
        Complete judgment and purification.
        """
        if not self._initiated:
            return {"error": "Frashokereti not initiated"}
        
        self._souls_processed += 1
        
        # Stage 1: Chinvat Bridge judgment
        judgment = self.chinvat_bridge.judge(soul)
        outcome = JudgmentOutcome(judgment["outcome"])
        
        # Stage 2: Molten Metal test
        metal_test = self.molten_metal.test_soul(soul)
        
        # Stage 3: Route to final destination
        if outcome == JudgmentOutcome.GARONMANA and metal_test["survives"]:
            final_destination = "GARONMANA"
            self.garonmana.admit(soul.name)
        elif outcome == JudgmentOutcome.HAMISTAGAN:
            final_destination = "HAMISTAGAN_THEN_GARONMANA"
            self.hamistagan.admit(soul.name, 0.0)
        else:
            final_destination = "CONSUMED"
        
        return {
            "soul": soul.name,
            "judgment": judgment,
            "metal_test": metal_test,
            "final_destination": final_destination,
            "eternal_state": "+1" if final_destination != "CONSUMED" else "DELETED"
        }
    
    def release_hamistagan(self) -> Dict:
        """Release all souls from Hamistagan."""
        released = self.hamistagan.release_at_frashokereti()
        
        # All are admitted to Garonmana
        for soul_name in released:
            self.garonmana.admit(soul_name)
        
        return {
            "released_count": len(released),
            "released_names": released,
            "destination": "GARONMANA",
            "forced_to_state": "+1"
        }
    
    def final_renormalization(self) -> Dict:
        """
        Execute final renormalization.
        
        - Flatten topology (Graph → K_N)
        - Zero all impedances
        - Freeze time (t → ∞)
        - Lock state
        """
        if not self._initiated:
            return {"error": "Frashokereti not initiated"}
        
        # Release Hamistagan residents
        hamistagan_release = self.release_hamistagan()
        
        self._completed = True
        
        return {
            "status": "FRASHOKERETI_COMPLETE",
            "topology": "Complete Graph K_N",
            "impedance": "Zero everywhere",
            "time_state": "Frozen (t → ∞)",
            "global_state": "|+1⟩ lattice",
            "updates_permitted": False,
            "hamistagan_release": hamistagan_release,
            "souls_in_garonmana": self.garonmana.n_residents,
            "souls_consumed": self.molten_metal.statistics["consumed"],
            "message": "The Making Wonderful is complete"
        }
    
    def execute_full_sequence(self, souls: List[ZoroastrianSoul]) -> Dict:
        """
        Execute complete Frashokereti sequence.
        
        Processes all souls and performs final renormalization.
        """
        # Initiate
        init_result = self.initiate()
        
        # Process all souls
        soul_results = []
        for soul in souls:
            result = self.process_soul(soul)
            soul_results.append(result)
        
        # Final renormalization
        final_result = self.final_renormalization()
        
        return {
            "initialization": init_result,
            "souls_processed": len(soul_results),
            "soul_results": soul_results,
            "final_renormalization": final_result
        }
    
    @property
    def is_complete(self) -> bool:
        return self._completed


# =============================================================================
# VALIDATION
# =============================================================================

def validate_frashokereti() -> bool:
    """Validate Zoroastrian frashokereti module."""
    
    # Test ChinvatBridge
    bridge = ChinvatBridge()
    
    assert bridge.classify(1.0) == JudgmentOutcome.GARONMANA
    assert bridge.classify(-1.0) == JudgmentOutcome.DRUJO_DEMANA
    assert bridge.classify(0.0) == JudgmentOutcome.HAMISTAGAN
    
    width_positive = bridge.compute_bridge_width(1.0)
    width_negative = bridge.compute_bridge_width(-1.0)
    assert width_positive > width_negative
    
    # Create test soul
    soul = ZoroastrianSoul("TestSoul", dimension=8)
    
    # Add some good karma
    for _ in range(5):
        soul.act(np.ones(8))
    
    judgment = bridge.judge(soul)
    assert "outcome" in judgment
    assert "net_value" in judgment
    
    # Test MoltenMetalTest
    metal = MoltenMetalTest()
    
    # Test resistance computation
    r_high = metal.compute_resistance(0.9)
    r_low = metal.compute_resistance(-0.9)
    assert r_high < r_low
    
    # Test soul
    result = metal.test_soul(soul)
    assert "survives" in result
    assert "experience" in result
    
    # Test vector purification
    vec = np.array([1.0, -1.0, 0.5, -0.5])
    purified = metal.purify_vector(vec)
    assert all(purified >= 0)  # No negative values
    
    # Test Hamistagan
    hamistagan = Hamistagan()
    
    hamistagan.admit("soul1", 0.0)
    hamistagan.admit("soul2", 0.0)
    
    assert hamistagan.n_residents == 2
    
    exp = hamistagan.get_experience("soul1")
    assert exp["state"] == "STASIS"
    
    released = hamistagan.release_at_frashokereti()
    assert len(released) == 2
    assert hamistagan.n_residents == 0
    
    # Test Garonmana
    garonmana = Garonmana()
    
    result = garonmana.admit("blessed_soul")
    assert "HARMONIC_RESONANCE" in result["state"]
    
    exp = garonmana.get_experience()
    assert exp["impedance"] == "Zero"
    
    # Test FrashokertiEngine
    engine = FrashokertiEngine()
    
    init = engine.initiate()
    assert init["status"] == "FRASHOKERETI_INITIATED"
    
    # Process some souls
    souls = [ZoroastrianSoul(f"Soul_{i}", dimension=8) for i in range(3)]
    
    # Give them different karma
    for _ in range(5):
        souls[0].act(np.ones(8))   # Good
        souls[1].act(-np.ones(8))  # Bad
        # souls[2] neutral
    
    for soul in souls:
        result = engine.process_soul(soul)
        assert "final_destination" in result
    
    # Final renormalization
    final = engine.final_renormalization()
    assert final["status"] == "FRASHOKERETI_COMPLETE"
    assert engine.is_complete
    
    # Test full sequence
    engine2 = FrashokertiEngine()
    souls2 = [ZoroastrianSoul(f"Soul2_{i}", dimension=8) for i in range(2)]
    
    full_result = engine2.execute_full_sequence(souls2)
    assert "final_renormalization" in full_result
    assert engine2.is_complete
    
    return True


if __name__ == "__main__":
    print("Validating Zoroastrian Frashokereti Module...")
    assert validate_frashokereti()
    print("✓ Zoroastrian Frashokereti Module validated")
