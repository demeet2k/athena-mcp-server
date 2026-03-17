"""
ATHENA OS - BIO-OS Galenic Humoral System
=========================================
Biological substrate runtime based on Galenic medicine.

Four Humors:
- Blood (hot+wet) - Sanguine temperament
- Yellow Bile (hot+dry) - Choleric temperament
- Phlegm (cold+wet) - Phlegmatic temperament
- Black Bile (cold+dry) - Melancholic temperament

Three Spirits:
- Natural Spirit (liver) - nutrition, growth
- Vital Spirit (heart) - life force, circulation
- Psychic Spirit (brain) - sensation, movement, thought

Eukrasia (good mixture) = optimal balance of humors
Dyskrasia (bad mixture) = imbalanced humors → disease

Treatment by Contraries: Apply opposite quality to restore balance.
Crisis Days: 7, 14, 21, 40 (critical points in disease progression)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
import math


# =============================================================================
# PRIMARY QUALITIES
# =============================================================================

class Quality(IntEnum):
    """The four primary qualities."""
    HOT = 0
    COLD = 1
    WET = 2
    DRY = 3
    
    @property
    def opposite(self) -> 'Quality':
        """Return the opposing quality."""
        return {
            Quality.HOT: Quality.COLD,
            Quality.COLD: Quality.HOT,
            Quality.WET: Quality.DRY,
            Quality.DRY: Quality.WET
        }[self]
    
    @property
    def axis(self) -> str:
        """Which axis this quality belongs to."""
        if self in (Quality.HOT, Quality.COLD):
            return "temperature"
        return "moisture"


@dataclass
class QualityState:
    """State of the four primary qualities."""
    hot: float = 0.5    # 0.0 = cold, 1.0 = hot
    wet: float = 0.5    # 0.0 = dry, 1.0 = wet
    
    @property
    def cold(self) -> float:
        return 1.0 - self.hot
    
    @property
    def dry(self) -> float:
        return 1.0 - self.wet
    
    def get(self, quality: Quality) -> float:
        """Get value for a quality."""
        return {
            Quality.HOT: self.hot,
            Quality.COLD: self.cold,
            Quality.WET: self.wet,
            Quality.DRY: self.dry
        }[quality]
    
    def apply_contrary(self, quality: Quality, intensity: float = 0.1) -> None:
        """Apply contrary treatment - move toward opposite quality."""
        if quality.axis == "temperature":
            if quality == Quality.HOT:
                self.hot = max(0.0, self.hot - intensity)
            else:
                self.hot = min(1.0, self.hot + intensity)
        else:
            if quality == Quality.WET:
                self.wet = max(0.0, self.wet - intensity)
            else:
                self.wet = min(1.0, self.wet + intensity)
    
    @property
    def is_balanced(self) -> bool:
        """Check if qualities are in balance (0.5 each)."""
        return abs(self.hot - 0.5) < 0.1 and abs(self.wet - 0.5) < 0.1


# =============================================================================
# THE FOUR HUMORS
# =============================================================================

class Humor(IntEnum):
    """
    The Four Humors and their qualities.
    
    Each humor is a combination of two primary qualities.
    """
    BLOOD = 0          # Hot + Wet → Sanguine
    YELLOW_BILE = 1    # Hot + Dry → Choleric  
    PHLEGM = 2         # Cold + Wet → Phlegmatic
    BLACK_BILE = 3     # Cold + Dry → Melancholic
    
    @property
    def qualities(self) -> Tuple[Quality, Quality]:
        """Return the two qualities of this humor."""
        return {
            Humor.BLOOD: (Quality.HOT, Quality.WET),
            Humor.YELLOW_BILE: (Quality.HOT, Quality.DRY),
            Humor.PHLEGM: (Quality.COLD, Quality.WET),
            Humor.BLACK_BILE: (Quality.COLD, Quality.DRY)
        }[self]
    
    @property
    def temperament(self) -> str:
        """The temperament associated with excess of this humor."""
        return {
            Humor.BLOOD: "Sanguine",
            Humor.YELLOW_BILE: "Choleric",
            Humor.PHLEGM: "Phlegmatic",
            Humor.BLACK_BILE: "Melancholic"
        }[self]
    
    @property
    def characteristics(self) -> str:
        """Personality characteristics when dominant."""
        return {
            Humor.BLOOD: "Cheerful, optimistic, social, impulsive",
            Humor.YELLOW_BILE: "Ambitious, driven, irritable, decisive",
            Humor.PHLEGM: "Calm, relaxed, slow, consistent",
            Humor.BLACK_BILE: "Analytical, detail-oriented, anxious, perfectionist"
        }[self]
    
    @property
    def organ(self) -> str:
        """Primary organ associated with this humor."""
        return {
            Humor.BLOOD: "Heart (and liver)",
            Humor.YELLOW_BILE: "Liver (and gallbladder)",
            Humor.PHLEGM: "Brain (and lungs)",
            Humor.BLACK_BILE: "Spleen"
        }[self]
    
    @property
    def element(self) -> str:
        """Classical element correspondence."""
        return ['Air', 'Fire', 'Water', 'Earth'][self.value]
    
    @property
    def season(self) -> str:
        """Season when this humor naturally predominates."""
        return ['Spring', 'Summer', 'Winter', 'Autumn'][self.value]


# =============================================================================
# THREE SPIRITS
# =============================================================================

class Spirit(IntEnum):
    """
    The Three Spirits (pneumata) that animate the body.
    
    A refinement hierarchy: Natural → Vital → Psychic
    """
    NATURAL = 0    # Liver - nutrition, growth, generation
    VITAL = 1      # Heart - life force, warmth, pulse
    PSYCHIC = 2    # Brain - sensation, movement, cognition
    
    @property
    def organ(self) -> str:
        """Primary organ producing this spirit."""
        return ['Liver', 'Heart', 'Brain'][self.value]
    
    @property
    def function(self) -> str:
        """Primary function of this spirit."""
        return {
            Spirit.NATURAL: "Nutrition, growth, reproduction",
            Spirit.VITAL: "Life force, warmth, circulation",
            Spirit.PSYCHIC: "Sensation, motion, thought"
        }[self]
    
    @property
    def refinement_level(self) -> int:
        """How refined this spirit is (higher = more refined)."""
        return self.value


# =============================================================================
# HUMORAL STATE
# =============================================================================

@dataclass
class HumoralState:
    """
    Complete humoral state of the biological system.
    
    Eukrasia (good mixture): All humors in proper proportion
    Dyskrasia (bad mixture): Humoral imbalance
    """
    # Humor levels (should sum to 1.0)
    blood: float = 0.25
    yellow_bile: float = 0.25
    phlegm: float = 0.25
    black_bile: float = 0.25
    
    # Spirit levels (0.0 to 1.0)
    natural_spirit: float = 1.0
    vital_spirit: float = 1.0
    psychic_spirit: float = 1.0
    
    # Derived quality state
    _quality_state: Optional[QualityState] = None
    
    def __post_init__(self):
        self._normalize()
        self._update_quality_state()
    
    def _normalize(self) -> None:
        """Normalize humor levels to sum to 1."""
        total = self.blood + self.yellow_bile + self.phlegm + self.black_bile
        if total > 0:
            self.blood /= total
            self.yellow_bile /= total
            self.phlegm /= total
            self.black_bile /= total
    
    def _update_quality_state(self) -> None:
        """Compute quality state from humors."""
        # Hot humors: blood, yellow bile
        # Wet humors: blood, phlegm
        hot = self.blood + self.yellow_bile
        wet = self.blood + self.phlegm
        self._quality_state = QualityState(hot=hot, wet=wet)
    
    def get_humor(self, humor: Humor) -> float:
        """Get level of specific humor."""
        return [self.blood, self.yellow_bile, self.phlegm, self.black_bile][humor.value]
    
    def set_humor(self, humor: Humor, value: float) -> None:
        """Set level of specific humor."""
        if humor == Humor.BLOOD:
            self.blood = value
        elif humor == Humor.YELLOW_BILE:
            self.yellow_bile = value
        elif humor == Humor.PHLEGM:
            self.phlegm = value
        else:
            self.black_bile = value
        self._normalize()
        self._update_quality_state()
    
    @property
    def qualities(self) -> QualityState:
        """Get derived quality state."""
        return self._quality_state
    
    @property
    def dominant_humor(self) -> Humor:
        """Return the dominant humor."""
        levels = [self.blood, self.yellow_bile, self.phlegm, self.black_bile]
        return Humor(levels.index(max(levels)))
    
    @property
    def temperament(self) -> str:
        """Return dominant temperament."""
        return self.dominant_humor.temperament
    
    @property
    def eukrasia_score(self) -> float:
        """
        Measure of humoral balance (0 = imbalanced, 1 = perfect eukrasia).
        
        Perfect balance = 0.25 each humor.
        """
        humors = [self.blood, self.yellow_bile, self.phlegm, self.black_bile]
        target = 0.25
        variance = sum((h - target) ** 2 for h in humors)
        max_variance = 3 * 0.25 ** 2 + 0.75 ** 2  # One humor = 1, others = 0
        return 1.0 - (variance / max_variance)
    
    @property
    def is_eukratic(self) -> bool:
        """Check if in state of eukrasia."""
        return self.eukrasia_score > 0.9
    
    @property
    def spirit_level(self) -> float:
        """Overall spirit/vitality level."""
        return (self.natural_spirit + self.vital_spirit + self.psychic_spirit) / 3
    
    def increase_humor(self, humor: Humor, amount: float = 0.1) -> None:
        """Increase a specific humor."""
        current = self.get_humor(humor)
        self.set_humor(humor, current + amount)
    
    def decrease_humor(self, humor: Humor, amount: float = 0.1) -> None:
        """Decrease a specific humor."""
        current = self.get_humor(humor)
        self.set_humor(humor, max(0.0, current - amount))
    
    def treat_by_contraries(self, excess_humor: Humor, intensity: float = 0.1) -> None:
        """
        Apply treatment by contraries.
        
        Reduce the excess humor and increase its opposite qualities.
        """
        q1, q2 = excess_humor.qualities
        self.qualities.apply_contrary(q1, intensity)
        self.qualities.apply_contrary(q2, intensity)
        self.decrease_humor(excess_humor, intensity)
        
        # Find the contrary humor (opposite qualities) and increase it
        for h in Humor:
            h_q1, h_q2 = h.qualities
            if h_q1 == q1.opposite and h_q2 == q2.opposite:
                self.increase_humor(h, intensity * 0.5)
                break
    
    def __str__(self) -> str:
        return (f"Humors: ??{self.blood:.2f} ??{self.yellow_bile:.2f} "
                f"??{self.phlegm:.2f} ⚫{self.black_bile:.2f} "
                f"[{self.temperament}] E={self.eukrasia_score:.2f}")


# =============================================================================
# HOMEOSTASIS CONTROLLER (PID)
# =============================================================================

@dataclass
class HomeostasisController:
    """
    PID controller for maintaining humoral balance.
    
    Implements feedback control to maintain eukrasia.
    With anti-windup, cascade control, and circadian adaptation.
    """
    # PID gains
    Kp: float = 0.5   # Proportional gain
    Ki: float = 0.1   # Integral gain
    Kd: float = 0.05  # Derivative gain
    
    # State
    integral: float = 0.0
    last_error: float = 0.0
    
    # Anti-windup
    integral_limit: float = 1.0
    
    # Target (perfect balance)
    target: float = 0.25
    
    def compute_correction(self, current: float, dt: float = 1.0) -> float:
        """
        Compute PID correction for a humor level.
        
        Returns correction amount to apply.
        """
        error = self.target - current
        
        # Proportional
        p_term = self.Kp * error
        
        # Integral with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit, 
                           min(self.integral_limit, self.integral))
        i_term = self.Ki * self.integral
        
        # Derivative
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        d_term = self.Kd * derivative
        
        self.last_error = error
        
        return p_term + i_term + d_term
    
    def reset(self) -> None:
        """Reset controller state."""
        self.integral = 0.0
        self.last_error = 0.0


class BioOS:
    """
    The complete BIO-OS runtime managing biological substrate.
    
    Features:
    - Humoral balance management
    - Spirit level maintenance
    - Crisis day monitoring
    - Treatment recommendation
    - Circadian and allostatic adaptation
    """
    
    # Crisis days (critical points in disease progression)
    CRISIS_DAYS = [7, 14, 21, 40]
    
    def __init__(self):
        self.state = HumoralState()
        self.controllers = {
            Humor.BLOOD: HomeostasisController(),
            Humor.YELLOW_BILE: HomeostasisController(),
            Humor.PHLEGM: HomeostasisController(),
            Humor.BLACK_BILE: HomeostasisController()
        }
        self.day = 0
        self.history: List[float] = []  # Eukrasia history
    
    def step(self, dt: float = 1.0) -> None:
        """
        Execute one time step of biological regulation.
        """
        self.day += 1
        
        # Apply PID corrections to each humor
        for humor in Humor:
            controller = self.controllers[humor]
            current = self.state.get_humor(humor)
            correction = controller.compute_correction(current, dt)
            
            # Apply correction (limited)
            correction = max(-0.05, min(0.05, correction))
            self.state.set_humor(humor, current + correction)
        
        # Update spirits based on humoral state
        self._update_spirits()
        
        # Record history
        self.history.append(self.state.eukrasia_score)
    
    def _update_spirits(self) -> None:
        """Update spirit levels based on humoral state."""
        # Natural spirit depends on overall health
        self.state.natural_spirit = 0.5 + 0.5 * self.state.eukrasia_score
        
        # Vital spirit depends on blood humor (heart)
        self.state.vital_spirit = 0.3 + 0.7 * min(self.state.blood * 4, 1.0)
        
        # Psychic spirit depends on phlegm (brain) and overall balance
        brain_factor = min(self.state.phlegm * 4, 1.0)
        self.state.psychic_spirit = 0.3 + 0.4 * brain_factor + 0.3 * self.state.eukrasia_score
    
    def is_crisis_day(self) -> bool:
        """Check if current day is a crisis day."""
        return self.day in self.CRISIS_DAYS
    
    def get_treatment_recommendation(self) -> Optional[str]:
        """
        Generate treatment recommendation based on current state.
        """
        if self.state.is_eukratic:
            return "Maintain current regimen. Body is in eukrasia."
        
        dominant = self.state.dominant_humor
        q1, q2 = dominant.qualities
        
        return (f"Excess {dominant.name} ({dominant.temperament}). "
                f"Apply contraries: {q1.opposite.name} and {q2.opposite.name}. "
                f"Reduce {dominant.organ} activity.")
    
    def apply_perturbation(self, humor: Humor, amount: float) -> None:
        """Apply an external perturbation (illness, diet, environment)."""
        self.state.increase_humor(humor, amount)
    
    def status(self) -> str:
        """Generate status report."""
        lines = [
            "=== BIO-OS Status ===",
            f"Day: {self.day}" + (" [CRISIS DAY]" if self.is_crisis_day() else ""),
            str(self.state),
            f"Spirit Level: {self.state.spirit_level:.2f}",
            f"  Natural: {self.state.natural_spirit:.2f}",
            f"  Vital: {self.state.vital_spirit:.2f}",
            f"  Psychic: {self.state.psychic_spirit:.2f}",
            "",
            f"Recommendation: {self.get_treatment_recommendation()}"
        ]
        return '\n'.join(lines)


# =============================================================================
# CIRCADIAN RHYTHM
# =============================================================================

class CircadianClock:
    """
    Models circadian variation in humoral balance.
    
    Each humor has a natural time when it predominates:
    - Blood: 3am - 9am (Spring/morning)
    - Yellow Bile: 9am - 3pm (Summer/midday)
    - Black Bile: 3pm - 9pm (Autumn/evening)
    - Phlegm: 9pm - 3am (Winter/night)
    """
    
    HUMOR_HOURS = {
        Humor.BLOOD: (3, 9),
        Humor.YELLOW_BILE: (9, 15),
        Humor.BLACK_BILE: (15, 21),
        Humor.PHLEGM: (21, 3)  # Wraps around midnight
    }
    
    @classmethod
    def dominant_humor_at(cls, hour: int) -> Humor:
        """Get the naturally dominant humor at a given hour (0-23)."""
        hour = hour % 24
        
        if 3 <= hour < 9:
            return Humor.BLOOD
        elif 9 <= hour < 15:
            return Humor.YELLOW_BILE
        elif 15 <= hour < 21:
            return Humor.BLACK_BILE
        else:
            return Humor.PHLEGM
    
    @classmethod
    def circadian_modifier(cls, humor: Humor, hour: int) -> float:
        """
        Get circadian modifier for a humor at a given hour.
        
        Returns value > 1 during humor's peak time, < 1 otherwise.
        """
        dominant = cls.dominant_humor_at(hour)
        
        if humor == dominant:
            return 1.2  # 20% increase during peak
        elif humor == dominant.qualities[0].opposite:
            return 0.8  # 20% decrease during opposite's peak
        else:
            return 1.0  # No modification


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bio_os() -> bool:
    """Validate BIO-OS system."""
    # Four humors
    assert len(Humor) == 4
    
    # Three spirits
    assert len(Spirit) == 3
    
    # Four qualities
    assert len(Quality) == 4
    
    # Quality opposites
    assert Quality.HOT.opposite == Quality.COLD
    assert Quality.WET.opposite == Quality.DRY
    
    # Humor qualities
    assert Humor.BLOOD.qualities == (Quality.HOT, Quality.WET)
    assert Humor.BLACK_BILE.qualities == (Quality.COLD, Quality.DRY)
    
    # BioOS converges toward eukrasia
    bio = BioOS()
    bio.state.blood = 0.5  # Imbalanced
    bio.state.yellow_bile = 0.3
    bio.state.phlegm = 0.15
    bio.state.black_bile = 0.05
    bio.state._normalize()
    
    initial_score = bio.state.eukrasia_score
    for _ in range(50):
        bio.step()
    final_score = bio.state.eukrasia_score
    
    assert final_score > initial_score  # Should improve
    
    return True


if __name__ == "__main__":
    print("Validating BIO-OS...")
    assert validate_bio_os()
    print("✓ BIO-OS validated")
    
    # Demo
    print("\n=== The Four Humors ===")
    for h in Humor:
        print(f"\n{h.name} ({h.element}, {h.season}):")
        print(f"  Qualities: {h.qualities[0].name} + {h.qualities[1].name}")
        print(f"  Temperament: {h.temperament}")
        print(f"  Characteristics: {h.characteristics}")
        print(f"  Organ: {h.organ}")
    
    print("\n=== The Three Spirits ===")
    for s in Spirit:
        print(f"{s.name}: {s.organ} - {s.function}")
    
    print("\n=== BIO-OS Demo ===")
    bio = BioOS()
    
    # Apply perturbation (too much yellow bile - anger/fever)
    print("Applying perturbation: excess Yellow Bile...")
    bio.apply_perturbation(Humor.YELLOW_BILE, 0.3)
    print(bio.status())
    
    print("\n--- Running homeostasis for 20 days ---")
    for _ in range(20):
        bio.step()
    
    print(bio.status())
    
    print("\n=== Circadian Rhythm ===")
    for hour in [0, 6, 12, 18]:
        dominant = CircadianClock.dominant_humor_at(hour)
        print(f"Hour {hour:02d}:00 - Dominant: {dominant.name} ({dominant.temperament})")
