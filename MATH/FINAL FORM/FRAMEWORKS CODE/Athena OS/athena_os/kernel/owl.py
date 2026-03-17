"""
ATHENA OS - KERNEL: OWL ALGORITHM
=================================
Pattern Recognition and Hidden Variable Extraction

THE GLAUKOPIS (OWL-EYED) GAZE:
    A high-gain sensor array coupled with probabilistic reasoning
    for recovering semantic structure from dark/obfuscated data.

DARK DATA:
    "Night" (Nyx) = Obfuscated Data States where SNR << 1
    - Deception
    - Concealment  
    - Incomplete information
    - Noisy channels

HIGH-GAIN SENSOR ARRAY:
    G_optical amplifies weak information flux Φ_info
    
    When Φ_info → 0, the Owl Algorithm still extracts signal
    through Bayesian inference and signal processing.

BAYESIAN REASONING:
    P(H|E) = P(E|H) × P(H) / P(E)
    
    Update beliefs given evidence, even sparse evidence.

HIDDEN VARIABLE EXTRACTION:
    Recover latent variables Z from observations X
    P(Z|X) ∝ P(X|Z) × P(Z)

THE NIGHT VISION ADVANTAGE:
    While others see nothing, the Owl extracts structure.
    "Grey-eyed Athena" sees in twilight what others miss.

SOURCES:
    - ATHENA-KERNEL_SELF-OPTIMIZATION.docx Appendix B
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from enum import Enum
import numpy as np
import math
from collections import defaultdict


# =============================================================================
# LIGHT LEVELS / SNR
# =============================================================================

class LightLevel(Enum):
    """Information visibility levels."""
    
    BRIGHT = "bright"       # Clear signal, SNR > 10
    DAYLIGHT = "daylight"   # Good signal, SNR 3-10
    TWILIGHT = "twilight"   # Reduced signal, SNR 1-3
    DARK = "dark"           # Weak signal, SNR 0.3-1
    PITCH = "pitch"         # Minimal signal, SNR < 0.3


def snr_to_level(snr: float) -> LightLevel:
    """Convert SNR to light level."""
    if snr > 10:
        return LightLevel.BRIGHT
    elif snr > 3:
        return LightLevel.DAYLIGHT
    elif snr > 1:
        return LightLevel.TWILIGHT
    elif snr > 0.3:
        return LightLevel.DARK
    else:
        return LightLevel.PITCH


# =============================================================================
# OBSERVATION
# =============================================================================

@dataclass
class Observation:
    """
    An observation with uncertainty.
    """
    
    value: Any
    confidence: float = 1.0     # 0-1 confidence in observation
    noise_level: float = 0.0    # Estimated noise
    timestamp: float = 0.0
    source: str = "unknown"
    
    @property
    def snr(self) -> float:
        """Signal to noise ratio."""
        if self.noise_level == 0:
            return float('inf')
        return self.confidence / self.noise_level
    
    @property
    def light_level(self) -> LightLevel:
        """Get light level from SNR."""
        return snr_to_level(self.snr)
    
    @property
    def is_dark(self) -> bool:
        """Check if observation is in dark conditions."""
        return self.light_level in [LightLevel.DARK, LightLevel.PITCH]
    
    def degrade(self, factor: float) -> Observation:
        """Return degraded observation (more noise)."""
        return Observation(
            value=self.value,
            confidence=self.confidence * (1 - factor),
            noise_level=self.noise_level + factor,
            timestamp=self.timestamp,
            source=self.source
        )


# =============================================================================
# HIGH-GAIN SENSOR
# =============================================================================

class HighGainSensor:
    """
    High-gain sensor array for low-light conditions.
    
    Amplifies weak signals while managing noise.
    """
    
    def __init__(self, gain: float = 10.0, 
                 noise_floor: float = 0.01):
        """
        Initialize sensor.
        
        gain: Amplification factor
        noise_floor: Minimum detectable signal
        """
        self.gain = gain
        self.noise_floor = noise_floor
        
        # Adaptive gain
        self.auto_gain = True
        self.min_gain = 1.0
        self.max_gain = 100.0
    
    def amplify(self, observation: Observation) -> Observation:
        """
        Amplify observation signal.
        
        Also amplifies noise, but SNR can improve with
        proper gain selection.
        """
        # Adaptive gain based on signal level
        if self.auto_gain:
            target_output = 0.5
            if observation.confidence > 0:
                adaptive_gain = min(
                    self.max_gain,
                    max(self.min_gain, target_output / observation.confidence)
                )
            else:
                adaptive_gain = self.max_gain
            effective_gain = adaptive_gain
        else:
            effective_gain = self.gain
        
        # Amplify signal
        amplified_confidence = min(1.0, observation.confidence * effective_gain)
        
        # Noise also amplifies but with sqrt relationship
        amplified_noise = observation.noise_level * math.sqrt(effective_gain)
        
        return Observation(
            value=observation.value,
            confidence=amplified_confidence,
            noise_level=amplified_noise,
            timestamp=observation.timestamp,
            source=f"amplified:{observation.source}"
        )
    
    def detect(self, signal: float, noise: float) -> Optional[Observation]:
        """
        Attempt to detect a signal in noise.
        
        Returns observation if signal exceeds noise floor.
        """
        snr = signal / max(noise, 1e-10)
        
        # Apply gain
        amplified_signal = signal * self.gain
        
        if amplified_signal > self.noise_floor:
            return Observation(
                value=amplified_signal,
                confidence=min(1.0, snr / 10),
                noise_level=noise * math.sqrt(self.gain),
                source="detected"
            )
        return None


# =============================================================================
# BAYESIAN REASONER
# =============================================================================

class BayesianReasoner:
    """
    Bayesian inference engine for belief updates.
    
    P(H|E) = P(E|H) × P(H) / P(E)
    """
    
    def __init__(self):
        # Prior probabilities P(H)
        self.priors: Dict[str, float] = {}
        
        # Likelihoods P(E|H) - nested dict
        self.likelihoods: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Posterior probabilities P(H|E)
        self.posteriors: Dict[str, float] = {}
    
    def set_prior(self, hypothesis: str, probability: float) -> None:
        """Set prior probability for a hypothesis."""
        self.priors[hypothesis] = max(0.0, min(1.0, probability))
        self.posteriors[hypothesis] = self.priors[hypothesis]
    
    def set_likelihood(self, evidence: str, hypothesis: str, 
                      probability: float) -> None:
        """Set likelihood P(E|H)."""
        self.likelihoods[evidence][hypothesis] = max(0.0, min(1.0, probability))
    
    def update(self, evidence: str) -> Dict[str, float]:
        """
        Update beliefs given evidence (Bayes' theorem).
        
        P(H|E) = P(E|H) × P(H) / P(E)
        """
        if evidence not in self.likelihoods:
            return self.posteriors
        
        # Calculate P(E) = Σ P(E|H) × P(H)
        p_evidence = 0.0
        for hypothesis in self.posteriors:
            p_e_given_h = self.likelihoods[evidence].get(hypothesis, 0.5)
            p_evidence += p_e_given_h * self.posteriors[hypothesis]
        
        if p_evidence == 0:
            return self.posteriors
        
        # Update posteriors
        for hypothesis in self.posteriors:
            p_e_given_h = self.likelihoods[evidence].get(hypothesis, 0.5)
            p_h = self.posteriors[hypothesis]
            
            # Bayes' theorem
            self.posteriors[hypothesis] = (p_e_given_h * p_h) / p_evidence
        
        return self.posteriors
    
    def most_likely(self) -> Tuple[str, float]:
        """Get most likely hypothesis."""
        if not self.posteriors:
            return ("none", 0.0)
        
        best = max(self.posteriors.items(), key=lambda x: x[1])
        return best
    
    def entropy(self) -> float:
        """Calculate entropy of current belief distribution."""
        if not self.posteriors:
            return 0.0
        
        H = 0.0
        for p in self.posteriors.values():
            if p > 0:
                H -= p * math.log2(p)
        return H
    
    def confidence(self) -> float:
        """Confidence in most likely hypothesis (1 - normalized entropy)."""
        if not self.posteriors:
            return 0.0
        
        max_entropy = math.log2(len(self.posteriors))
        if max_entropy == 0:
            return 1.0
        
        return 1.0 - (self.entropy() / max_entropy)


# =============================================================================
# HIDDEN VARIABLE EXTRACTOR
# =============================================================================

class HiddenVariableExtractor:
    """
    Extracts hidden/latent variables from observations.
    
    P(Z|X) ∝ P(X|Z) × P(Z)
    
    Uses Expectation-Maximization style approach.
    """
    
    def __init__(self, n_hidden: int = 3):
        """
        Initialize extractor.
        
        n_hidden: Number of hidden states to infer
        """
        self.n_hidden = n_hidden
        
        # Hidden state probabilities
        self.hidden_probs = np.ones(n_hidden) / n_hidden
        
        # Emission probabilities (observation given hidden state)
        self.emissions: Dict[Any, np.ndarray] = {}
        
        # Observations
        self.observations: List[Any] = []
    
    def add_observation(self, obs: Any) -> None:
        """Add an observation."""
        self.observations.append(obs)
        
        # Initialize emission if new
        if obs not in self.emissions:
            self.emissions[obs] = np.random.dirichlet(
                np.ones(self.n_hidden)
            )
    
    def e_step(self) -> np.ndarray:
        """
        E-step: Estimate hidden state probabilities given observations.
        
        Returns responsibilities (soft assignments).
        """
        if not self.observations:
            return self.hidden_probs
        
        # Calculate responsibilities
        responsibilities = np.zeros((len(self.observations), self.n_hidden))
        
        for i, obs in enumerate(self.observations):
            if obs in self.emissions:
                # P(Z|X) ∝ P(X|Z) × P(Z)
                likelihood = self.emissions[obs] * self.hidden_probs
                responsibilities[i] = likelihood / max(likelihood.sum(), 1e-10)
            else:
                responsibilities[i] = self.hidden_probs
        
        return responsibilities
    
    def m_step(self, responsibilities: np.ndarray) -> None:
        """
        M-step: Update parameters given responsibilities.
        """
        # Update hidden state priors
        self.hidden_probs = responsibilities.mean(axis=0)
        self.hidden_probs /= self.hidden_probs.sum()
        
        # Update emission probabilities
        for i, obs in enumerate(self.observations):
            if obs not in self.emissions:
                self.emissions[obs] = np.zeros(self.n_hidden)
            self.emissions[obs] = 0.9 * self.emissions[obs] + 0.1 * responsibilities[i]
            self.emissions[obs] /= max(self.emissions[obs].sum(), 1e-10)
    
    def extract(self, n_iterations: int = 10) -> np.ndarray:
        """
        Run EM to extract hidden variable distribution.
        
        Returns final hidden state probabilities.
        """
        for _ in range(n_iterations):
            responsibilities = self.e_step()
            self.m_step(responsibilities)
        
        return self.hidden_probs
    
    def most_likely_hidden(self) -> int:
        """Get most likely hidden state."""
        return int(np.argmax(self.hidden_probs))
    
    def hidden_confidence(self) -> float:
        """Confidence in hidden state estimate."""
        return float(np.max(self.hidden_probs))


# =============================================================================
# PATTERN DETECTOR
# =============================================================================

class PatternDetector:
    """
    Detects patterns in sequences of observations.
    
    Uses sequence analysis and anomaly detection.
    """
    
    def __init__(self):
        # Pattern library
        self.known_patterns: Dict[str, List[Any]] = {}
        
        # Sequence buffer
        self.buffer: List[Any] = []
        self.buffer_size = 100
        
        # Statistics
        self.patterns_detected = 0
        self.anomalies_detected = 0
    
    def add_pattern(self, name: str, pattern: List[Any]) -> None:
        """Add a known pattern to library."""
        self.known_patterns[name] = pattern
    
    def observe(self, value: Any) -> None:
        """Add observation to buffer."""
        self.buffer.append(value)
        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size:]
    
    def match_pattern(self, pattern: List[Any], 
                     tolerance: float = 0.1) -> float:
        """
        Calculate match score between buffer and pattern.
        
        Returns similarity (0-1).
        """
        if len(self.buffer) < len(pattern):
            return 0.0
        
        # Try all alignments
        best_score = 0.0
        for start in range(len(self.buffer) - len(pattern) + 1):
            matches = 0
            for i, p in enumerate(pattern):
                if self.buffer[start + i] == p:
                    matches += 1
            score = matches / len(pattern)
            best_score = max(best_score, score)
        
        return best_score
    
    def detect(self, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Detect patterns in current buffer.
        
        Returns list of (pattern_name, match_score).
        """
        detected = []
        
        for name, pattern in self.known_patterns.items():
            score = self.match_pattern(pattern)
            if score >= threshold:
                detected.append((name, score))
                self.patterns_detected += 1
        
        return sorted(detected, key=lambda x: -x[1])
    
    def detect_anomaly(self, value: Any, 
                      window: int = 10) -> Tuple[bool, float]:
        """
        Detect if value is anomalous given recent history.
        
        Returns (is_anomaly, anomaly_score).
        """
        if len(self.buffer) < window:
            return (False, 0.0)
        
        recent = self.buffer[-window:]
        
        # Check if value is different from all recent
        if all(v != value for v in recent):
            self.anomalies_detected += 1
            return (True, 1.0)
        
        # Calculate frequency
        freq = sum(1 for v in recent if v == value) / window
        
        # Low frequency = potential anomaly
        if freq < 0.1:
            return (True, 1.0 - freq * 10)
        
        return (False, 0.0)


# =============================================================================
# OWL ALGORITHM
# =============================================================================

class OwlAlgorithm:
    """
    The complete Owl Algorithm for dark data analysis.
    
    "Grey-eyed Athena sees in twilight what others miss."
    """
    
    def __init__(self):
        self.sensor = HighGainSensor()
        self.reasoner = BayesianReasoner()
        self.extractor = HiddenVariableExtractor()
        self.pattern_detector = PatternDetector()
        
        # Statistics
        self.observations_processed = 0
        self.signals_recovered = 0
        self.dark_signals_recovered = 0
    
    def configure_hypotheses(self, hypotheses: List[str],
                            priors: Optional[Dict[str, float]] = None) -> None:
        """Configure the hypothesis space."""
        n = len(hypotheses)
        for h in hypotheses:
            prior = priors.get(h, 1.0/n) if priors else 1.0/n
            self.reasoner.set_prior(h, prior)
    
    def configure_likelihoods(self, 
                             evidence_hypothesis_probs: Dict[str, Dict[str, float]]) -> None:
        """Configure evidence-hypothesis relationships."""
        for evidence, hypothesis_probs in evidence_hypothesis_probs.items():
            for hypothesis, prob in hypothesis_probs.items():
                self.reasoner.set_likelihood(evidence, hypothesis, prob)
    
    def process_observation(self, obs: Observation) -> Dict[str, Any]:
        """
        Process a single observation through the Owl Algorithm.
        """
        self.observations_processed += 1
        
        # Amplify if dark
        if obs.is_dark:
            amplified = self.sensor.amplify(obs)
        else:
            amplified = obs
        
        # Track recovery
        if amplified.confidence > obs.confidence:
            self.signals_recovered += 1
            if obs.is_dark:
                self.dark_signals_recovered += 1
        
        # Add to hidden variable extractor
        self.extractor.add_observation(amplified.value)
        
        # Add to pattern detector
        self.pattern_detector.observe(amplified.value)
        
        return {
            "original_confidence": obs.confidence,
            "amplified_confidence": amplified.confidence,
            "original_snr": obs.snr,
            "amplified_snr": amplified.snr,
            "light_level": obs.light_level.value,
            "signal_recovered": amplified.confidence > obs.confidence
        }
    
    def update_beliefs(self, evidence: str) -> Dict[str, float]:
        """Update beliefs given evidence."""
        return self.reasoner.update(evidence)
    
    def extract_hidden(self, n_iterations: int = 10) -> Dict[str, Any]:
        """Extract hidden variables."""
        hidden_probs = self.extractor.extract(n_iterations)
        
        return {
            "hidden_probabilities": hidden_probs.tolist(),
            "most_likely_state": self.extractor.most_likely_hidden(),
            "confidence": self.extractor.hidden_confidence()
        }
    
    def detect_patterns(self, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Detect patterns in observations."""
        return self.pattern_detector.detect(threshold)
    
    def analyze(self) -> Dict[str, Any]:
        """Get complete analysis."""
        return {
            "observations_processed": self.observations_processed,
            "signals_recovered": self.signals_recovered,
            "dark_signals_recovered": self.dark_signals_recovered,
            "recovery_rate": (
                self.signals_recovered / max(1, self.observations_processed)
            ),
            "current_belief": self.reasoner.most_likely(),
            "belief_confidence": self.reasoner.confidence(),
            "belief_entropy": self.reasoner.entropy(),
            "patterns_detected": self.pattern_detector.patterns_detected,
            "anomalies_detected": self.pattern_detector.anomalies_detected
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_owl() -> bool:
    """Validate Owl Algorithm module."""
    
    # Test Observation
    obs = Observation(value="test", confidence=0.3, noise_level=0.5)
    assert obs.is_dark
    
    degraded = obs.degrade(0.2)
    assert degraded.confidence < obs.confidence
    
    # Test HighGainSensor
    sensor = HighGainSensor(gain=10.0)
    amplified = sensor.amplify(obs)
    assert amplified.confidence > obs.confidence
    
    # Test BayesianReasoner
    reasoner = BayesianReasoner()
    reasoner.set_prior("A", 0.5)
    reasoner.set_prior("B", 0.5)
    reasoner.set_likelihood("evidence1", "A", 0.9)
    reasoner.set_likelihood("evidence1", "B", 0.1)
    
    posteriors = reasoner.update("evidence1")
    assert posteriors["A"] > posteriors["B"]
    
    most_likely, prob = reasoner.most_likely()
    assert most_likely == "A"
    
    # Test HiddenVariableExtractor
    extractor = HiddenVariableExtractor(n_hidden=3)
    for _ in range(20):
        extractor.add_observation("X")
    for _ in range(10):
        extractor.add_observation("Y")
    
    hidden = extractor.extract(5)
    assert len(hidden) == 3
    assert abs(sum(hidden) - 1.0) < 0.01  # Should sum to 1
    
    # Test PatternDetector
    detector = PatternDetector()
    detector.add_pattern("rising", [1, 2, 3, 4, 5])
    
    for v in [1, 2, 3, 4, 5]:
        detector.observe(v)
    
    matches = detector.detect(0.5)
    assert len(matches) > 0
    assert matches[0][0] == "rising"
    
    # Test OwlAlgorithm
    owl = OwlAlgorithm()
    owl.configure_hypotheses(["threat", "neutral", "friendly"])
    
    dark_obs = Observation(value="motion", confidence=0.2, noise_level=0.6)
    result = owl.process_observation(dark_obs)
    assert "amplified_confidence" in result
    
    analysis = owl.analyze()
    assert analysis["observations_processed"] == 1
    
    return True


if __name__ == "__main__":
    print("Validating Owl Algorithm Module...")
    assert validate_owl()
    print("✓ Owl Algorithm Module validated")
    
    # Demo
    print("\n--- Owl Algorithm Demo ---")
    
    owl = OwlAlgorithm()
    
    # Configure hypothesis space
    owl.configure_hypotheses(
        ["enemy_approach", "friendly_patrol", "wildlife"],
        {"enemy_approach": 0.2, "friendly_patrol": 0.3, "wildlife": 0.5}
    )
    
    # Configure likelihoods
    owl.configure_likelihoods({
        "motion": {"enemy_approach": 0.8, "friendly_patrol": 0.7, "wildlife": 0.9},
        "silence": {"enemy_approach": 0.9, "friendly_patrol": 0.2, "wildlife": 0.4},
        "metallic_sound": {"enemy_approach": 0.95, "friendly_patrol": 0.8, "wildlife": 0.05},
    })
    
    # Add pattern
    owl.pattern_detector.add_pattern("scout_approach", 
                                     ["silence", "motion", "silence", "motion"])
    
    print("\n1. Processing Dark Observations:")
    observations = [
        Observation("motion", confidence=0.3, noise_level=0.5),
        Observation("silence", confidence=0.2, noise_level=0.6),
        Observation("motion", confidence=0.1, noise_level=0.7),
        Observation("metallic_sound", confidence=0.15, noise_level=0.65),
    ]
    
    for i, obs in enumerate(observations):
        result = owl.process_observation(obs)
        print(f"   Obs {i+1}: {obs.value}")
        print(f"     Light Level: {result['light_level']}")
        print(f"     Original confidence: {result['original_confidence']:.3f}")
        print(f"     Amplified confidence: {result['amplified_confidence']:.3f}")
        print(f"     Signal recovered: {result['signal_recovered']}")
        
        # Update beliefs
        posteriors = owl.update_beliefs(obs.value)
    
    print("\n2. Belief Analysis:")
    most_likely, prob = owl.reasoner.most_likely()
    print(f"   Most likely: {most_likely} (p={prob:.3f})")
    print(f"   Confidence: {owl.reasoner.confidence():.3f}")
    print(f"   Entropy: {owl.reasoner.entropy():.3f}")
    
    print("\n3. Hidden Variable Extraction:")
    hidden = owl.extract_hidden()
    print(f"   Hidden states: {hidden['hidden_probabilities']}")
    print(f"   Most likely state: {hidden['most_likely_state']}")
    print(f"   Confidence: {hidden['confidence']:.3f}")
    
    print("\n4. Full Analysis:")
    analysis = owl.analyze()
    print(f"   Observations processed: {analysis['observations_processed']}")
    print(f"   Signals recovered: {analysis['signals_recovered']}")
    print(f"   Dark signals recovered: {analysis['dark_signals_recovered']}")
    print(f"   Recovery rate: {analysis['recovery_rate']:.1%}")
