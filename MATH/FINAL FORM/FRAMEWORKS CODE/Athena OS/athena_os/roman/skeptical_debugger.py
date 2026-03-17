"""
ATHENA OS - ROMAN KERNEL: SKEPTICAL DEBUGGER MODULE
====================================================
Adversarial Argument Generator and Epistemic Safety Layer

THE SKEPTICAL DEBUGGER:
    A systematic adversarial argument generator that prevents
    overfitting to dogma and enforces epistemic humility.

ACADEMIC SKEPTICISM (Cicero's stance):
    - No certainty is possible about most matters
    - Use probability (pithanon/probabile) as guide
    - Examine both sides of every question
    - Withhold definitive assent

PYRRHONIAN SKEPTICISM (Sextus Empiricus):
    - Suspend judgment (epochē) on all non-evident matters
    - Oppose every argument with equal counterargument
    - Achieve tranquility through suspension
    - Ten Modes (tropoi) for generating doubt

DEBUGGER FUNCTIONS:
    1. Argument Adversarial: Generate counterarguments
    2. Equipollence Check: Balance opposing views
    3. Probability Assessment: Assign credence levels
    4. Dogma Detection: Flag overconfident assertions
    5. Suspension Recommendation: When to withhold judgment

SOURCES:
    - Cicero: Academica, De Natura Deorum
    - Sextus Empiricus: Outlines of Pyrrhonism
    - Diogenes Laertius: Lives of the Philosophers
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


# =============================================================================
# SKEPTICAL MODES
# =============================================================================

class SkepticalMode(Enum):
    """The Ten Modes of Aenesidemus for inducing doubt."""
    
    # Modes based on the judging subject
    ANIMAL_VARIATION = "animal_variation"       # Different animals perceive differently
    HUMAN_VARIATION = "human_variation"         # Different humans perceive differently
    SENSE_VARIATION = "sense_variation"         # Different senses give different reports
    CIRCUMSTANCE = "circumstance"               # State of perceiver affects perception
    
    # Modes based on the object
    POSITION_DISTANCE = "position_distance"     # Position and distance affect appearance
    MIXTURE = "mixture"                         # Objects mixed with environment
    QUANTITY = "quantity"                       # Quantity affects quality
    RELATIVITY = "relativity"                   # Everything is relative to something
    
    # Modes based on both
    FREQUENCY = "frequency"                     # Rare vs common affects judgment
    CUSTOM_LAW = "custom_law"                   # Culture affects judgment


class JudgmentType(Enum):
    """Types of philosophical judgments."""
    
    EVIDENT = "evident"           # Self-evidently true (e.g., 2+2=4)
    NON_EVIDENT = "non_evident"   # Not immediately apparent
    DOGMATIC = "dogmatic"         # Claimed as certain without justification
    PROBABLE = "probable"         # More likely than alternatives
    SUSPENDED = "suspended"       # Judgment withheld


class ConfidenceLevel(Enum):
    """Levels of epistemic confidence."""
    
    CERTAIN = "certain"           # 1.0 - Reserved for self-evident truths
    HIGHLY_PROBABLE = "highly_probable"  # 0.8-0.99
    PROBABLE = "probable"         # 0.6-0.79
    EQUIPOLLENT = "equipollent"   # ~0.5 - Equal evidence each way
    IMPROBABLE = "improbable"     # 0.2-0.39
    SUSPEND = "suspend"           # Unknown - no basis for judgment


# =============================================================================
# ARGUMENT STRUCTURES
# =============================================================================

@dataclass
class Proposition:
    """A philosophical proposition."""
    
    content: str
    confidence: float = 0.5      # 0-1
    judgment_type: JudgmentType = JudgmentType.NON_EVIDENT
    evidence: List[str] = field(default_factory=list)
    counterevidence: List[str] = field(default_factory=list)
    
    def is_dogmatic(self) -> bool:
        """Check if proposition is dogmatically held."""
        return self.confidence > 0.9 and len(self.counterevidence) > 0
    
    def equipollence_ratio(self) -> float:
        """Calculate ratio of evidence to counterevidence."""
        ev = len(self.evidence) + 0.1
        counter = len(self.counterevidence) + 0.1
        return ev / (ev + counter)


@dataclass
class Argument:
    """A philosophical argument."""
    
    premises: List[Proposition]
    conclusion: Proposition
    argument_type: str = "deductive"
    
    def soundness_check(self) -> Dict[str, Any]:
        """Check argument soundness."""
        # Check if all premises are evident or probable
        weak_premises = [p for p in self.premises if p.confidence < 0.5]
        
        # Check for hidden assumptions
        total_confidence = np.prod([p.confidence for p in self.premises])
        
        return {
            "weak_premises": len(weak_premises),
            "total_confidence": total_confidence,
            "conclusion_max_confidence": total_confidence,
            "is_sound": len(weak_premises) == 0 and total_confidence > 0.5
        }


@dataclass
class CounterArgument:
    """A counterargument generated by the debugger."""
    
    original: Argument
    objection_type: str
    objection: str
    affected_premise: Optional[int] = None
    mode_used: Optional[SkepticalMode] = None
    
    def strength(self) -> float:
        """Calculate counterargument strength."""
        base = 0.5
        if self.mode_used:
            base += 0.1
        if self.affected_premise is not None:
            base += 0.1
        return min(1.0, base)


# =============================================================================
# MODE GENERATORS
# =============================================================================

class ModeGenerator:
    """
    Generates skeptical objections using the Ten Modes.
    """
    
    @staticmethod
    def apply_mode(mode: SkepticalMode, 
                   proposition: Proposition) -> Dict[str, Any]:
        """Apply a skeptical mode to a proposition."""
        
        objections = {
            SkepticalMode.ANIMAL_VARIATION: {
                "objection": f"Different animals would perceive '{proposition.content[:30]}...' differently. A bat, a bee, and a dog experience the same reality differently. How do we know human perception is privileged?",
                "effect": "Undermines sensory-based claims"
            },
            SkepticalMode.HUMAN_VARIATION: {
                "objection": f"Different humans judge '{proposition.content[:30]}...' differently based on temperament, culture, and constitution. Which human judgment is correct?",
                "effect": "Undermines claims to universal human knowledge"
            },
            SkepticalMode.SENSE_VARIATION: {
                "objection": f"Our different senses give conflicting reports. Honey looks one way, feels another, tastes another. Which sense tells us what '{proposition.content[:30]}...' really is?",
                "effect": "Undermines multi-sensory claims"
            },
            SkepticalMode.CIRCUMSTANCE: {
                "objection": f"Your judgment of '{proposition.content[:30]}...' depends on whether you are young or old, healthy or sick, awake or dreaming. In which state do you truly know?",
                "effect": "Undermines circumstance-dependent judgments"
            },
            SkepticalMode.POSITION_DISTANCE: {
                "objection": f"The appearance of '{proposition.content[:30]}...' changes with position and distance. A tower looks round from far, square from near. Which is true?",
                "effect": "Undermines spatial judgments"
            },
            SkepticalMode.MIXTURE: {
                "objection": f"We never perceive '{proposition.content[:30]}...' in isolation but always mixed with light, air, and our own perceptual apparatus. What is the thing itself?",
                "effect": "Undermines claims about isolated objects"
            },
            SkepticalMode.QUANTITY: {
                "objection": f"The quantity affects our judgment of '{proposition.content[:30]}...'. A little wine cheers, much intoxicates. Is wine good or bad?",
                "effect": "Undermines absolute quality judgments"
            },
            SkepticalMode.RELATIVITY: {
                "objection": f"'{proposition.content[:30]}...' is always relative to something else - to a perceiver, a context, a comparison. What is it in itself?",
                "effect": "Undermines non-relational claims"
            },
            SkepticalMode.FREQUENCY: {
                "objection": f"We judge '{proposition.content[:30]}...' differently based on how common it is. The sun amazes at eclipse, not daily. Is our valuation rational?",
                "effect": "Undermines frequency-biased judgments"
            },
            SkepticalMode.CUSTOM_LAW: {
                "objection": f"Different cultures and legal systems judge '{proposition.content[:30]}...' differently. Greeks and Persians, Romans and Germans differ. Which custom is right?",
                "effect": "Undermines culturally-dependent claims"
            },
        }
        
        return objections.get(mode, {
            "objection": "This claim should be examined more carefully",
            "effect": "General skeptical caution"
        })
    
    @staticmethod
    def generate_all_objections(proposition: Proposition) -> List[Dict[str, Any]]:
        """Generate objections using all applicable modes."""
        objections = []
        for mode in SkepticalMode:
            obj = ModeGenerator.apply_mode(mode, proposition)
            obj["mode"] = mode.value
            objections.append(obj)
        return objections


# =============================================================================
# PROBABILITY ASSESSOR
# =============================================================================

class ProbabilityAssessor:
    """
    Academic skeptical probability assessment.
    
    Following Cicero's Academic stance: use probability (pithanon)
    as a guide for action when certainty is unavailable.
    """
    
    @staticmethod
    def assess_proposition(prop: Proposition) -> Dict[str, Any]:
        """Assess the probability of a proposition."""
        
        # Calculate base probability from evidence ratio
        ratio = prop.equipollence_ratio()
        
        # Adjust for confidence inflation
        adjusted = ratio * (1 - (prop.confidence - ratio) * 0.5)
        
        # Determine confidence level
        if adjusted > 0.9 and prop.judgment_type == JudgmentType.EVIDENT:
            level = ConfidenceLevel.CERTAIN
        elif adjusted > 0.75:
            level = ConfidenceLevel.HIGHLY_PROBABLE
        elif adjusted > 0.55:
            level = ConfidenceLevel.PROBABLE
        elif adjusted > 0.45:
            level = ConfidenceLevel.EQUIPOLLENT
        elif adjusted > 0.2:
            level = ConfidenceLevel.IMPROBABLE
        else:
            level = ConfidenceLevel.SUSPEND
        
        return {
            "proposition": prop.content[:50],
            "evidence_ratio": ratio,
            "claimed_confidence": prop.confidence,
            "assessed_probability": adjusted,
            "confidence_level": level.value,
            "is_overconfident": prop.confidence > adjusted + 0.2,
            "recommendation": ProbabilityAssessor._get_recommendation(level)
        }
    
    @staticmethod
    def _get_recommendation(level: ConfidenceLevel) -> str:
        """Get action recommendation based on confidence level."""
        recommendations = {
            ConfidenceLevel.CERTAIN: "Accept as true; act accordingly",
            ConfidenceLevel.HIGHLY_PROBABLE: "Accept provisionally; act with confidence",
            ConfidenceLevel.PROBABLE: "Accept tentatively; act with caution",
            ConfidenceLevel.EQUIPOLLENT: "Suspend judgment; seek more evidence",
            ConfidenceLevel.IMPROBABLE: "Reject tentatively; act as if false",
            ConfidenceLevel.SUSPEND: "Suspend judgment entirely; refrain from action based on this"
        }
        return recommendations.get(level, "Exercise caution")
    
    @staticmethod
    def compare_propositions(p1: Proposition, p2: Proposition) -> Dict[str, Any]:
        """Compare two competing propositions."""
        a1 = ProbabilityAssessor.assess_proposition(p1)
        a2 = ProbabilityAssessor.assess_proposition(p2)
        
        diff = abs(a1["assessed_probability"] - a2["assessed_probability"])
        
        if diff < 0.1:
            comparison = "equipollent"
            recommendation = "Suspend judgment between these alternatives"
        elif a1["assessed_probability"] > a2["assessed_probability"]:
            comparison = "first_more_probable"
            recommendation = f"Favor first proposition with probability {a1['assessed_probability']:.2f}"
        else:
            comparison = "second_more_probable"
            recommendation = f"Favor second proposition with probability {a2['assessed_probability']:.2f}"
        
        return {
            "proposition_1": a1,
            "proposition_2": a2,
            "probability_difference": diff,
            "comparison": comparison,
            "recommendation": recommendation
        }


# =============================================================================
# SKEPTICAL DEBUGGER
# =============================================================================

class SkepticalDebugger:
    """
    The complete Skeptical Debugger system.
    
    Functions:
    1. Generate counterarguments to any position
    2. Assess probability of claims
    3. Detect dogmatic overconfidence
    4. Recommend suspension of judgment
    5. Enforce epistemic humility
    """
    
    def __init__(self):
        self.mode_generator = ModeGenerator()
        self.probability_assessor = ProbabilityAssessor()
        
        # Log of processed claims
        self.processed_claims: List[Dict[str, Any]] = []
        self.dogma_alerts: List[Dict[str, Any]] = []
    
    def debug_proposition(self, prop: Proposition) -> Dict[str, Any]:
        """
        Full debug analysis of a proposition.
        
        Returns comprehensive skeptical analysis.
        """
        # Probability assessment
        prob_assessment = self.probability_assessor.assess_proposition(prop)
        
        # Generate objections
        objections = self.mode_generator.generate_all_objections(prop)
        
        # Check for dogmatism
        is_dogmatic = prop.is_dogmatic()
        
        # Determine recommendation
        if is_dogmatic:
            recommendation = "ALERT: Dogmatic claim detected. Reduce confidence or provide more justification."
            self.dogma_alerts.append({
                "proposition": prop.content,
                "claimed_confidence": prop.confidence,
                "counterevidence_count": len(prop.counterevidence)
            })
        elif prob_assessment["confidence_level"] == "equipollent":
            recommendation = "SUSPEND: Evidence balanced. Withhold judgment."
        elif prob_assessment["is_overconfident"]:
            recommendation = f"CALIBRATE: Reduce confidence from {prop.confidence:.2f} to {prob_assessment['assessed_probability']:.2f}"
        else:
            recommendation = "PROCEED: Claim reasonably supported"
        
        result = {
            "proposition": prop.content,
            "probability_assessment": prob_assessment,
            "objections_available": len(objections),
            "sample_objections": objections[:3],
            "is_dogmatic": is_dogmatic,
            "recommendation": recommendation
        }
        
        self.processed_claims.append(result)
        
        return result
    
    def debug_argument(self, arg: Argument) -> Dict[str, Any]:
        """Debug an entire argument."""
        # Check each premise
        premise_analyses = []
        for i, premise in enumerate(arg.premises):
            analysis = self.debug_proposition(premise)
            analysis["premise_index"] = i
            premise_analyses.append(analysis)
        
        # Check conclusion
        conclusion_analysis = self.debug_proposition(arg.conclusion)
        
        # Soundness check
        soundness = arg.soundness_check()
        
        # Generate counterargument
        weakest_premise = min(
            enumerate(arg.premises),
            key=lambda x: x[1].confidence
        )
        
        counter = CounterArgument(
            original=arg,
            objection_type="weakest_premise",
            objection=f"Premise {weakest_premise[0]} is insufficiently supported",
            affected_premise=weakest_premise[0],
            mode_used=SkepticalMode.RELATIVITY
        )
        
        return {
            "premise_analyses": premise_analyses,
            "conclusion_analysis": conclusion_analysis,
            "soundness": soundness,
            "counterargument": {
                "objection": counter.objection,
                "strength": counter.strength(),
                "affected_premise": counter.affected_premise
            },
            "overall_assessment": "SOUND" if soundness["is_sound"] else "UNSOUND"
        }
    
    def induce_epochē(self, prop: Proposition) -> Dict[str, Any]:
        """
        Induce epochē (suspension of judgment).
        
        Generate opposing arguments of equal strength.
        """
        # Create antithesis
        anti_content = f"It is not the case that: {prop.content}"
        antithesis = Proposition(
            content=anti_content,
            confidence=1 - prop.confidence,
            evidence=prop.counterevidence,
            counterevidence=prop.evidence
        )
        
        # Assess both
        thesis_prob = self.probability_assessor.assess_proposition(prop)
        anti_prob = self.probability_assessor.assess_proposition(antithesis)
        
        # Check equipollence
        diff = abs(thesis_prob["assessed_probability"] - anti_prob["assessed_probability"])
        is_equipollent = diff < 0.15
        
        return {
            "thesis": {
                "content": prop.content,
                "probability": thesis_prob["assessed_probability"]
            },
            "antithesis": {
                "content": antithesis.content,
                "probability": anti_prob["assessed_probability"]
            },
            "difference": diff,
            "is_equipollent": is_equipollent,
            "epochē_achieved": is_equipollent,
            "recommendation": "Suspend judgment and achieve tranquility" if is_equipollent else "Continue inquiry"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get debugger statistics."""
        return {
            "claims_processed": len(self.processed_claims),
            "dogma_alerts": len(self.dogma_alerts),
            "average_overconfidence": np.mean([
                c["probability_assessment"]["claimed_confidence"] - c["probability_assessment"]["assessed_probability"]
                for c in self.processed_claims
            ]) if self.processed_claims else 0
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_skeptical_debugger() -> bool:
    """Validate skeptical debugger module."""
    
    # Test proposition
    prop = Proposition(
        content="The soul is immortal",
        confidence=0.9,
        evidence=["Argument from recollection", "Argument from simplicity"],
        counterevidence=["No empirical evidence", "Materialist objections"]
    )
    assert prop.is_dogmatic()
    
    ratio = prop.equipollence_ratio()
    assert 0 < ratio < 1
    
    # Test mode generator
    objection = ModeGenerator.apply_mode(SkepticalMode.HUMAN_VARIATION, prop)
    assert "objection" in objection
    
    all_obj = ModeGenerator.generate_all_objections(prop)
    assert len(all_obj) == len(SkepticalMode)
    
    # Test probability assessor
    assessment = ProbabilityAssessor.assess_proposition(prop)
    assert "assessed_probability" in assessment
    assert assessment["is_overconfident"]
    
    # Test comparison
    prop2 = Proposition(
        content="The soul is mortal",
        confidence=0.6,
        evidence=["Materialist arguments"],
        counterevidence=["Immortality arguments"]
    )
    comparison = ProbabilityAssessor.compare_propositions(prop, prop2)
    assert "comparison" in comparison
    
    # Test debugger
    debugger = SkepticalDebugger()
    
    result = debugger.debug_proposition(prop)
    assert "is_dogmatic" in result
    assert result["is_dogmatic"]
    
    # Test epochē
    epochē = debugger.induce_epochē(prop)
    assert "thesis" in epochē
    assert "antithesis" in epochē
    
    # Test argument debugging
    arg = Argument(
        premises=[prop, prop2],
        conclusion=Proposition("Therefore, we should live virtuously", 0.7)
    )
    arg_result = debugger.debug_argument(arg)
    assert "overall_assessment" in arg_result
    
    return True


if __name__ == "__main__":
    print("Validating Skeptical Debugger Module...")
    assert validate_skeptical_debugger()
    print("✓ Skeptical Debugger Module validated")
    
    # Demo
    print("\n--- Skeptical Debugger Demo ---")
    debugger = SkepticalDebugger()
    
    # Create a dogmatic proposition
    prop = Proposition(
        content="The Stoic view is certainly correct about emotions",
        confidence=0.95,
        evidence=["Rational argument", "Practical success"],
        counterevidence=["Epicurean objections", "Skeptical doubts", "Common sense"]
    )
    
    print(f"\nAnalyzing: '{prop.content}'")
    print(f"Claimed confidence: {prop.confidence}")
    
    result = debugger.debug_proposition(prop)
    print(f"\nAssessed probability: {result['probability_assessment']['assessed_probability']:.2f}")
    print(f"Is dogmatic: {result['is_dogmatic']}")
    print(f"Recommendation: {result['recommendation']}")
    
    print("\nSample objection:")
    if result['sample_objections']:
        obj = result['sample_objections'][0]
        print(f"  Mode: {obj['mode']}")
        print(f"  {obj['objection'][:100]}...")
    
    # Induce epochē
    print("\n--- Inducing Epochē ---")
    epochē = debugger.induce_epochē(prop)
    print(f"Thesis probability: {epochē['thesis']['probability']:.2f}")
    print(f"Antithesis probability: {epochē['antithesis']['probability']:.2f}")
    print(f"Epochē achieved: {epochē['epochē_achieved']}")
