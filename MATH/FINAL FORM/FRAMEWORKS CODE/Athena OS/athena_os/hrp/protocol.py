"""
ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL
==========================================
Protocol: Main Holographic Rotation Protocol

From Holographic_Rotation_Protocol.docx:

THE HOLOGRAPHIC ROTATION PROTOCOL:

1. Object Initialization
   - Parse/construct the object O
   - Identify native element
   
2. Project to All Four Frames
   - W(O): Water projection
   - E(O): Earth projection
   - F(O): Fire projection
   - A(O): Air projection
   
3. Compute Texture in Each Frame
   - (H_W, D_W, λ_W)
   - (H_E, D_E, λ_E)
   - (H_F, D_F, λ_F)
   - (H_A, D_A, λ_A)
   
4. Identify Invariants
   - Quantities preserved under rotation
   - Cross-frame correlations
   
5. Analyze Structure
   - Texture inequality: T ≤ E_bind(S)
   - Coherence evolution: dC/dt = -T·C
   
6. Recombine Insights
   - Cross-frame compatibility
   - Contradiction detection
   - Global structure assessment
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
import numpy as np

from .frames import (
    Element, Frame, WaterFrame, EarthFrame, FireFrame, AirFrame,
    StateSpace, Dynamics, Measure, create_frame
)
from .texture import (
    TextureTriple, TextureAnalyzer, TextureFunctional,
    BindingEnergy, CoherenceTracker
)
from .rotation import (
    RotationOperator, RotationCycle, RotationChain,
    WaterToEarth, EarthToFire, FireToAir, AirToWater,
    get_rotation
)
from .objects import (
    HolographicObject, CanonicalConstant, MetallicMean, ProblemObject,
    ConstantType, ProblemType
)


# =============================================================================
# PROTOCOL CONFIGURATION
# =============================================================================

@dataclass
class ProtocolConfig:
    """Configuration for holographic rotation protocol."""
    
    # Discretization parameters
    grid_resolution: int = 10
    time_step: float = 0.1
    
    # Randomization parameters
    temperature: float = 1.0
    noise_level: float = 0.1
    
    # Texture estimation
    n_samples: int = 1000
    block_size: int = 2
    
    # Coherence tracking
    coherence_threshold: float = 0.01
    max_time: float = 100.0
    
    # Output control
    verbose: bool = False
    save_trajectories: bool = False


# =============================================================================
# PROTOCOL RESULT
# =============================================================================

@dataclass
class ProtocolResult:
    """Result of holographic rotation protocol."""
    
    # Input
    object_name: str
    config: ProtocolConfig
    
    # Frames
    frames: Dict[Element, Frame] = field(default_factory=dict)
    
    # Textures
    textures: Dict[Element, TextureTriple] = field(default_factory=dict)
    
    # Rotation metrics
    distortions: Dict[str, float] = field(default_factory=dict)
    
    # Invariants
    invariants: Dict[str, float] = field(default_factory=dict)
    
    # Analysis
    texture_functional: float = 0.0
    binding_energies: Dict[str, float] = field(default_factory=dict)
    coherence_decay: float = 0.0
    
    # Diagnostics
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def log(self, message: str) -> None:
        """Add log message."""
        self.logs.append(message)
    
    def error(self, message: str) -> None:
        """Add error message."""
        self.errors.append(message)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of results."""
        return {
            "object": self.object_name,
            "frames": list(self.frames.keys()),
            "textures": {e.value: str(t) for e, t in self.textures.items()},
            "total_distortion": sum(self.distortions.values()),
            "invariants": self.invariants,
            "texture_value": self.texture_functional,
            "n_errors": len(self.errors)
        }
    
    def texture_profile_array(self) -> np.ndarray:
        """Get texture as 4x3 array [element x (H,D,λ)]."""
        arr = np.zeros((4, 3))
        elements = [Element.WATER, Element.EARTH, Element.FIRE, Element.AIR]
        
        for i, elem in enumerate(elements):
            if elem in self.textures:
                t = self.textures[elem]
                arr[i] = [t.H, t.D, t.lam]
        
        return arr


# =============================================================================
# HOLOGRAPHIC ROTATION PROTOCOL
# =============================================================================

@dataclass
class HolographicRotationProtocol:
    """
    The main Holographic Rotation Protocol.
    
    Systematically rotates an object through four elemental frames,
    computing texture at each stage and analyzing invariants.
    """
    
    config: ProtocolConfig = field(default_factory=ProtocolConfig)
    
    # Rotation operators (initialized in __post_init__)
    rotations: Dict[Tuple[Element, Element], RotationOperator] = field(
        default_factory=dict
    )
    
    # Analyzers
    texture_analyzer: TextureAnalyzer = field(default_factory=TextureAnalyzer)
    texture_functional: TextureFunctional = field(default_factory=TextureFunctional)
    
    def __post_init__(self):
        """Initialize rotation operators."""
        self.rotations = {
            (Element.WATER, Element.EARTH): WaterToEarth(
                grid_resolution=self.config.grid_resolution,
                time_step=self.config.time_step
            ),
            (Element.EARTH, Element.FIRE): EarthToFire(
                temperature=self.config.temperature,
                noise_level=self.config.noise_level
            ),
            (Element.FIRE, Element.AIR): FireToAir(),
            (Element.AIR, Element.WATER): AirToWater()
        }
    
    def run(self, obj: HolographicObject) -> ProtocolResult:
        """
        Run the holographic rotation protocol.
        
        Args:
            obj: HolographicObject to analyze
        
        Returns:
            ProtocolResult with frames, textures, and analysis
        """
        result = ProtocolResult(
            object_name=obj.name,
            config=self.config
        )
        
        result.log(f"Starting HRP for: {obj.name}")
        
        # Step 1: Initialize from existing frames
        result.log("Step 1: Initializing frames")
        self._initialize_frames(obj, result)
        
        # Step 2: Complete rotation cycle
        result.log("Step 2: Completing rotation cycle")
        self._complete_rotation(obj, result)
        
        # Step 3: Compute textures
        result.log("Step 3: Computing textures")
        self._compute_textures(obj, result)
        
        # Step 4: Identify invariants
        result.log("Step 4: Identifying invariants")
        self._identify_invariants(result)
        
        # Step 5: Analyze structure
        result.log("Step 5: Analyzing structure")
        self._analyze_structure(result)
        
        # Step 6: Recombine insights
        result.log("Step 6: Recombining insights")
        self._recombine_insights(result)
        
        result.log("Protocol complete")
        return result
    
    def _initialize_frames(self, obj: HolographicObject, 
                          result: ProtocolResult) -> None:
        """Initialize from object's existing frames."""
        for elem, frame in obj.frames.items():
            result.frames[elem] = frame
            result.log(f"  Found {elem.value} frame")
    
    def _complete_rotation(self, obj: HolographicObject,
                          result: ProtocolResult) -> None:
        """Complete rotation to fill all frames."""
        # Find starting frame
        if not result.frames:
            result.error("No initial frames found")
            return
        
        # Determine rotation order based on what we have
        elements = [Element.WATER, Element.EARTH, Element.FIRE, Element.AIR]
        
        # Find first available frame
        start_idx = None
        for i, elem in enumerate(elements):
            if elem in result.frames:
                start_idx = i
                break
        
        if start_idx is None:
            result.error("No valid starting frame")
            return
        
        # Rotate forward
        current_elem = elements[start_idx]
        for _ in range(3):
            next_elem = current_elem.next()
            
            if next_elem not in result.frames:
                rotation_key = (current_elem, next_elem)
                
                if rotation_key in self.rotations:
                    rotation = self.rotations[rotation_key]
                    try:
                        new_frame = rotation(result.frames[current_elem])
                        result.frames[next_elem] = new_frame
                        
                        dist = rotation.estimate_distortion(
                            result.frames[current_elem], new_frame
                        )
                        result.distortions[rotation.name] = dist
                        result.log(f"  Rotated {current_elem.value} → {next_elem.value}")
                    except Exception as e:
                        result.error(f"Rotation failed: {e}")
            
            current_elem = next_elem
    
    def _compute_textures(self, obj: HolographicObject,
                         result: ProtocolResult) -> None:
        """Compute texture at each frame."""
        for elem, frame in result.frames.items():
            try:
                texture = self._texture_for_frame(frame)
                result.textures[elem] = texture
                result.log(f"  {elem.value}: {texture}")
            except Exception as e:
                result.error(f"Texture computation failed for {elem.value}: {e}")
                result.textures[elem] = TextureTriple()
    
    def _texture_for_frame(self, frame: Frame) -> TextureTriple:
        """Compute texture for a specific frame."""
        if isinstance(frame, WaterFrame):
            samples = frame.sample(self.config.n_samples)
            points = np.array(samples)
            return self.texture_analyzer.analyze_points(points)
        
        elif isinstance(frame, EarthFrame):
            trajectory = frame.iterate(0, self.config.n_samples)
            return self.texture_analyzer.analyze_sequence(np.array(trajectory))
        
        elif isinstance(frame, FireFrame):
            if frame.transition_matrix is not None:
                return self.texture_analyzer.analyze_transition_matrix(
                    frame.transition_matrix
                )
            return TextureTriple()
        
        elif isinstance(frame, AirFrame):
            samples = frame.sample(10)
            combined = ''.join(samples)
            H = frame.entropy_rate(combined)
            return TextureTriple(H=H, D=1.0, lam=1.0)
        
        return TextureTriple()
    
    def _identify_invariants(self, result: ProtocolResult) -> None:
        """Identify quantities preserved under rotation."""
        if len(result.textures) < 2:
            return
        
        textures = list(result.textures.values())
        
        # Compute cross-frame statistics
        H_values = [t.H for t in textures]
        D_values = [t.D for t in textures]
        lam_values = [t.lam for t in textures]
        
        # Mean and variance (potential invariants)
        result.invariants["H_mean"] = float(np.mean(H_values))
        result.invariants["H_var"] = float(np.var(H_values))
        result.invariants["D_mean"] = float(np.mean(D_values))
        result.invariants["D_var"] = float(np.var(D_values))
        result.invariants["λ_mean"] = float(np.mean(lam_values))
        result.invariants["λ_var"] = float(np.var(lam_values))
        
        # Total texture (summed)
        result.invariants["total_texture"] = sum(
            self.texture_functional(t) for t in textures
        )
        
        # Roughness ratio
        if result.invariants["λ_mean"] > 0:
            result.invariants["roughness"] = (
                result.invariants["H_mean"] * result.invariants["D_mean"] /
                result.invariants["λ_mean"]
            )
        
        result.log(f"  Found {len(result.invariants)} invariants")
    
    def _analyze_structure(self, result: ProtocolResult) -> None:
        """Analyze structural persistence."""
        # Compute overall texture
        if result.textures:
            avg_texture = TextureTriple(
                H=result.invariants.get("H_mean", 0),
                D=result.invariants.get("D_mean", 1),
                lam=result.invariants.get("λ_mean", 1)
            )
            result.texture_functional = self.texture_functional(avg_texture)
        
        # Coherence decay estimate
        tracker = CoherenceTracker(
            initial_coherence=1.0,
            texture=result.texture_functional
        )
        
        result.coherence_decay = tracker.half_life()
        result.invariants["coherence_half_life"] = result.coherence_decay
        
        result.log(f"  Texture functional: {result.texture_functional:.4f}")
        result.log(f"  Coherence half-life: {result.coherence_decay:.4f}")
    
    def _recombine_insights(self, result: ProtocolResult) -> None:
        """Synthesize insights from all frames."""
        # Check for cross-frame compatibility
        compatibility = self._check_compatibility(result)
        result.invariants["compatibility"] = compatibility
        
        # Check for contradictions
        contradictions = self._detect_contradictions(result)
        for c in contradictions:
            result.log(f"  Contradiction: {c}")
        
        result.log(f"  Compatibility score: {compatibility:.4f}")
    
    def _check_compatibility(self, result: ProtocolResult) -> float:
        """Check compatibility between frame representations."""
        if len(result.textures) < 2:
            return 1.0
        
        # Compute pairwise texture distances
        textures = list(result.textures.values())
        distances = []
        
        for i in range(len(textures)):
            for j in range(i + 1, len(textures)):
                d = textures[i].distance(textures[j])
                distances.append(d)
        
        if distances:
            avg_dist = np.mean(distances)
            # Convert to compatibility (lower distance = higher compatibility)
            return float(np.exp(-avg_dist))
        
        return 1.0
    
    def _detect_contradictions(self, result: ProtocolResult) -> List[str]:
        """Detect contradictions between frames."""
        contradictions = []
        
        # Check for extreme texture variations
        if result.invariants.get("H_var", 0) > 2.0:
            contradictions.append("High entropy variation across frames")
        
        if result.invariants.get("D_var", 0) > 2.0:
            contradictions.append("High dimension variation across frames")
        
        # Check distortion accumulation
        total_dist = sum(result.distortions.values())
        if total_dist > 1.0:
            contradictions.append(f"High cumulative distortion: {total_dist:.2f}")
        
        return contradictions


# =============================================================================
# PROTOCOL FACTORY
# =============================================================================

def create_protocol(config: Optional[ProtocolConfig] = None) -> HolographicRotationProtocol:
    """Create protocol with configuration."""
    return HolographicRotationProtocol(config=config or ProtocolConfig())


def run_protocol(obj: HolographicObject, 
                config: Optional[ProtocolConfig] = None) -> ProtocolResult:
    """Convenience function to run protocol on object."""
    protocol = create_protocol(config)
    return protocol.run(obj)


def analyze_problem(problem_type: ProblemType,
                   config: Optional[ProtocolConfig] = None) -> ProtocolResult:
    """Analyze canonical problem."""
    problem = ProblemObject(name=problem_type.value, problem_type=problem_type)
    return run_protocol(problem, config)


def analyze_constant(constant: CanonicalConstant,
                    config: Optional[ProtocolConfig] = None) -> ProtocolResult:
    """Analyze canonical constant."""
    obj = constant.to_holographic()
    return run_protocol(obj, config)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_protocol() -> bool:
    """Validate protocol module."""
    
    # Test ProtocolConfig
    config = ProtocolConfig(grid_resolution=5, verbose=True)
    assert config.grid_resolution == 5
    
    # Test ProtocolResult
    result = ProtocolResult(
        object_name="test",
        config=config
    )
    result.log("Test log")
    assert len(result.logs) == 1
    
    result.textures[Element.WATER] = TextureTriple(H=1.0, D=2.0, lam=0.5)
    result.textures[Element.EARTH] = TextureTriple(H=1.5, D=1.8, lam=0.6)
    
    arr = result.texture_profile_array()
    assert arr.shape == (4, 3)
    assert arr[0, 0] == 1.0  # Water H
    
    summary = result.summary()
    assert "object" in summary
    
    # Test HolographicRotationProtocol
    protocol = HolographicRotationProtocol(config=config)
    
    # Create test object with Water frame
    obj = HolographicObject(name="test_object")
    water = WaterFrame(
        state_space=StateSpace(StateSpaceType.MANIFOLD, dimension=2),
        dynamics=Dynamics(DynamicsType.FLOW),
        measure=Measure(MeasureType.LEBESGUE),
        field_dimension=2,
        flow_function=lambda x: -0.1 * x
    )
    obj.set_frame(Element.WATER, water)
    
    # Run protocol
    result = protocol.run(obj)
    
    assert result.object_name == "test_object"
    assert Element.WATER in result.frames
    assert len(result.logs) > 0
    
    # Should have computed textures
    assert len(result.textures) > 0
    
    # Test problem analysis
    collatz_result = analyze_problem(ProblemType.COLLATZ, config)
    assert collatz_result.object_name == "Collatz Conjecture"
    
    # Test constant analysis
    from .objects import PI
    pi_result = analyze_constant(PI, config)
    assert "Pi" in pi_result.object_name
    
    return True


if __name__ == "__main__":
    print("Validating Protocol...")
    assert validate_protocol()
    print("✓ Protocol module validated")
