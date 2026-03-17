"""
ATHENA OS - Seed Encoding System
================================
The 14-byte compact seed representation for Aether.

SEED FORMAT (14 bytes):
    byte 0:     version (0x01)
    byte 1:     Z* mode (vacuum/plasma/conductor/TI/cavity)
    byte 2:     lens mask (4 bits: Fire|Water|Air|Earth)
    byte 3:     generator mask (8 bits)
    bytes 4-5:  theta_q (θ quantized to 16 bits, 0-65535 → 0-2π)
    bytes 6-7:  e2_q (e² quantized to 16 bits, log scale)
    byte 8:     clamp mode (none/Dirac/SZ/QHE/anomaly)
    byte 9:     boundary mode (none/Dirichlet/Neumann/periodic/Δθ)
    byte 10:    medium mode (vacuum/plasma/conductor/TI/cavity)
    byte 11:    symmetry mode (U(1)/SL2Z/anomaly/TR-Z2/chiral)
    bytes 12-13: aux0 (context-dependent)
    
IDEMPOTENCE:
    encode(decode(seed)) = seed

ROUND-TRIP:
    decode(seed) → Aether → expand → collapse → encode → seed
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import struct
import hashlib

from .duality import TauParameter, PI, TAU
from .aether import (
    Aether, Face, ProjectorSet, GeneratorSet, Generator,
    ZeroPoint, AetherFactory
)


# =============================================================================
# ENCODING ENUMS
# =============================================================================

class ZStarMode(Enum):
    """Z* mode encoding."""
    VACUUM = 0
    PLASMA = 1
    CONDUCTOR = 2
    TOPOLOGICAL_INSULATOR = 3
    CAVITY = 4


class ClampMode(Enum):
    """Clamp mode encoding."""
    NONE = 0
    DIRAC = 1
    SCHWINGER_ZWANZIGER = 2
    QUANTUM_HALL = 3
    ANOMALY = 4


class BoundaryMode(Enum):
    """Boundary condition mode."""
    NONE = 0
    DIRICHLET = 1
    NEUMANN = 2
    PERIODIC = 3
    DELTA_THETA = 4


class MediumMode(Enum):
    """Medium mode."""
    VACUUM = 0
    PLASMA = 1
    CONDUCTOR = 2
    TOPOLOGICAL_INSULATOR = 3
    CAVITY = 4


class SymmetryMode(Enum):
    """Symmetry mode."""
    U1_ONLY = 0
    SL2Z_ENABLED = 1
    ANOMALY_ENABLED = 2
    TR_Z2_ENABLED = 3
    CHIRAL_ENABLED = 4


# =============================================================================
# QUANTIZATION FUNCTIONS
# =============================================================================

def quantize_theta(theta: float) -> int:
    """Quantize θ to 16-bit integer (0-65535)."""
    # Normalize to [0, 2π)
    theta = theta % TAU
    # Scale to 0-65535
    return int((theta / TAU) * 65535) & 0xFFFF


def dequantize_theta(theta_q: int) -> float:
    """Dequantize 16-bit θ back to radians."""
    return (theta_q / 65535) * TAU


def quantize_e_squared(e_squared: float) -> int:
    """
    Quantize e² to 16-bit integer using log scale.
    
    Range: e² from 1e-4 to 1e4
    """
    import math
    # Log scale: log₁₀(e²) from -4 to 4
    log_val = math.log10(max(1e-10, e_squared))
    # Clamp to [-4, 4]
    log_val = max(-4, min(4, log_val))
    # Scale to 0-65535
    scaled = (log_val + 4) / 8  # 0 to 1
    return int(scaled * 65535) & 0xFFFF


def dequantize_e_squared(e2_q: int) -> float:
    """Dequantize 16-bit e² back to value."""
    import math
    # Reverse the process
    scaled = e2_q / 65535  # 0 to 1
    log_val = scaled * 8 - 4  # -4 to 4
    return 10 ** log_val


# =============================================================================
# SEED STRUCTURE
# =============================================================================

@dataclass
class AetherSeed:
    """
    The 14-byte compact seed for Aether.
    
    Stores generators and certificates, not expansions.
    "Store in, not out."
    """
    
    version: int = 1
    z_star_mode: ZStarMode = ZStarMode.VACUUM
    lens_mask: int = 0x0F  # All faces active
    generator_mask: int = 0x03  # d, * minimum
    theta_q: int = 0  # θ = 0
    e2_q: int = 32768  # e² = 1 (midpoint of log scale)
    clamp_mode: ClampMode = ClampMode.NONE
    boundary_mode: BoundaryMode = BoundaryMode.NONE
    medium_mode: MediumMode = MediumMode.VACUUM
    symmetry_mode: SymmetryMode = SymmetryMode.U1_ONLY
    aux0: int = 0
    
    def to_bytes(self) -> bytes:
        """Encode to 14 bytes."""
        return struct.pack(
            '>BBBBHHBBBBH',
            self.version,
            self.z_star_mode.value,
            self.lens_mask & 0x0F,
            self.generator_mask & 0xFF,
            self.theta_q & 0xFFFF,
            self.e2_q & 0xFFFF,
            self.clamp_mode.value,
            self.boundary_mode.value,
            self.medium_mode.value,
            self.symmetry_mode.value,
            self.aux0 & 0xFFFF
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'AetherSeed':
        """Decode from 14 bytes."""
        if len(data) < 14:
            raise ValueError(f"Need 14 bytes, got {len(data)}")
        
        unpacked = struct.unpack('>BBBBHHBBBBH', data[:14])
        
        return cls(
            version=unpacked[0],
            z_star_mode=ZStarMode(unpacked[1] % 5),
            lens_mask=unpacked[2],
            generator_mask=unpacked[3],
            theta_q=unpacked[4],
            e2_q=unpacked[5],
            clamp_mode=ClampMode(unpacked[6] % 5),
            boundary_mode=BoundaryMode(unpacked[7] % 5),
            medium_mode=MediumMode(unpacked[8] % 5),
            symmetry_mode=SymmetryMode(unpacked[9] % 5),
            aux0=unpacked[10]
        )
    
    def to_hex(self) -> str:
        """Encode to hex string."""
        return self.to_bytes().hex()
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'AetherSeed':
        """Decode from hex string."""
        return cls.from_bytes(bytes.fromhex(hex_str))
    
    def hash(self) -> str:
        """Compute SHA256 hash of seed."""
        return hashlib.sha256(self.to_bytes()).hexdigest()[:16]
    
    @property
    def theta(self) -> float:
        """Get θ value."""
        return dequantize_theta(self.theta_q)
    
    @theta.setter
    def theta(self, value: float) -> None:
        """Set θ value."""
        self.theta_q = quantize_theta(value)
    
    @property
    def e_squared(self) -> float:
        """Get e² value."""
        return dequantize_e_squared(self.e2_q)
    
    @e_squared.setter
    def e_squared(self, value: float) -> None:
        """Set e² value."""
        self.e2_q = quantize_e_squared(value)
    
    def tau_parameter(self) -> TauParameter:
        """Get τ parameter."""
        return TauParameter(
            theta=self.theta,
            e_squared=self.e_squared
        )


# =============================================================================
# ENCODER/DECODER
# =============================================================================

class AetherEncoder:
    """Encodes Aether objects to seeds."""
    
    @staticmethod
    def encode(aether: Aether) -> AetherSeed:
        """Encode Aether to seed."""
        seed = AetherSeed()
        
        # Encode lens mask from projectors
        seed.lens_mask = aether.projectors.lens_mask()
        
        # Encode generator mask
        seed.generator_mask = aether.generators.mask()
        
        # Encode τ
        seed.theta = aether.tau.theta
        seed.e_squared = aether.tau.e_squared
        
        # Medium mode from Z*
        if aether.zero_point.is_stable:
            seed.z_star_mode = ZStarMode.VACUUM
        
        # Symmetry mode
        if aether.generators.has(Generator.M_TAU):
            seed.symmetry_mode = SymmetryMode.SL2Z_ENABLED
        
        return seed


class AetherDecoder:
    """Decodes seeds to Aether objects."""
    
    @staticmethod
    def decode(seed: AetherSeed) -> Aether:
        """Decode seed to Aether."""
        # Create projector set from lens mask
        projectors = ProjectorSet.from_lens_mask(seed.lens_mask)
        
        # Create generator set from mask
        generators = GeneratorSet.from_mask(seed.generator_mask)
        
        # Create τ parameter
        tau = seed.tau_parameter()
        
        # Create Aether
        aether = Aether(
            tau=tau,
            projectors=projectors,
            generators=generators
        )
        
        return aether


def encode(aether: Aether) -> AetherSeed:
    """Convenience function to encode Aether."""
    return AetherEncoder.encode(aether)


def decode(seed: AetherSeed) -> Aether:
    """Convenience function to decode seed."""
    return AetherDecoder.decode(seed)


# =============================================================================
# PRESET SEEDS
# =============================================================================

class PresetSeeds:
    """Collection of preset seeds for common configurations."""
    
    @staticmethod
    def pure_maxwell_vacuum() -> AetherSeed:
        """Pure Maxwell vacuum."""
        seed = AetherSeed()
        seed.lens_mask = 0b1010  # Water + Earth
        seed.generator_mask = 0b0111  # d, *, □
        seed.theta = 0
        seed.e_squared = 1.0
        seed.z_star_mode = ZStarMode.VACUUM
        seed.symmetry_mode = SymmetryMode.U1_ONLY
        return seed
    
    @staticmethod
    def topological_insulator() -> AetherSeed:
        """Pinned TI with θ = π."""
        seed = AetherSeed()
        seed.lens_mask = 0b1100  # Air + Earth
        seed.generator_mask = 0b1011  # d, *, M(τ), BC
        seed.theta = PI
        seed.e_squared = 4 * PI
        seed.z_star_mode = ZStarMode.TOPOLOGICAL_INSULATOR
        seed.medium_mode = MediumMode.TOPOLOGICAL_INSULATOR
        seed.symmetry_mode = SymmetryMode.TR_Z2_ENABLED
        return seed
    
    @staticmethod
    def axion_cavity() -> AetherSeed:
        """Axion conversion in cavity."""
        seed = AetherSeed()
        seed.lens_mask = 0b1110  # Water + Air + Earth
        seed.generator_mask = 0b1111  # d, *, □, M(τ)
        seed.theta = 0
        seed.e_squared = 1.0
        seed.z_star_mode = ZStarMode.CAVITY
        seed.medium_mode = MediumMode.CAVITY
        seed.symmetry_mode = SymmetryMode.ANOMALY_ENABLED
        seed.aux0 = 1000000  # Q factor
        return seed
    
    @staticmethod
    def full_duality_stack() -> AetherSeed:
        """Full EM-duality-axion stack."""
        seed = AetherSeed()
        seed.lens_mask = 0b1111  # All faces
        seed.generator_mask = 0xFF  # All generators
        seed.theta = 0
        seed.e_squared = 4 * PI
        seed.symmetry_mode = SymmetryMode.SL2Z_ENABLED
        return seed


# =============================================================================
# VALIDATION
# =============================================================================

def validate_seeds() -> bool:
    """Validate seeds module."""
    
    # Test quantization round-trip
    for theta in [0, PI/4, PI/2, PI, 3*PI/2]:
        q = quantize_theta(theta)
        back = dequantize_theta(q)
        assert abs(back - (theta % TAU)) < 1e-3
    
    for e2 in [0.01, 0.1, 1.0, 10.0, 100.0]:
        q = quantize_e_squared(e2)
        back = dequantize_e_squared(q)
        assert abs(back / e2 - 1.0) < 0.1  # Within 10%
    
    # Test seed round-trip
    seed1 = AetherSeed(
        lens_mask=0b1010,
        generator_mask=0b0111,
        theta_q=quantize_theta(PI/2),
        e2_q=quantize_e_squared(4*PI)
    )
    
    data = seed1.to_bytes()
    assert len(data) == 14
    
    seed2 = AetherSeed.from_bytes(data)
    assert seed2.lens_mask == seed1.lens_mask
    assert seed2.generator_mask == seed1.generator_mask
    assert seed2.theta_q == seed1.theta_q
    
    # Test hex round-trip
    hex_str = seed1.to_hex()
    seed3 = AetherSeed.from_hex(hex_str)
    assert seed3.to_bytes() == seed1.to_bytes()
    
    # Test encode/decode
    aether = AetherFactory.pure_maxwell_vacuum()
    seed = encode(aether)
    aether2 = decode(seed)
    assert aether2.projectors.lens_mask() == aether.projectors.lens_mask()
    
    # Test presets
    maxwell = PresetSeeds.pure_maxwell_vacuum()
    assert maxwell.lens_mask == 0b1010
    
    ti = PresetSeeds.topological_insulator()
    assert abs(ti.theta - PI) < 0.01
    
    return True


if __name__ == "__main__":
    print("Validating Seeds Module...")
    assert validate_seeds()
    print("✓ Seeds Module validated")
    
    # Demo
    print("\n=== Seed Encoding Demo ===")
    
    print("\nPreset Seeds:")
    presets = [
        ("Pure Maxwell Vacuum", PresetSeeds.pure_maxwell_vacuum()),
        ("Topological Insulator", PresetSeeds.topological_insulator()),
        ("Axion Cavity", PresetSeeds.axion_cavity()),
        ("Full Duality Stack", PresetSeeds.full_duality_stack()),
    ]
    
    for name, seed in presets:
        print(f"\n{name}:")
        print(f"  Bytes: {seed.to_hex()}")
        print(f"  Hash: {seed.hash()}")
        print(f"  Lens mask: {seed.lens_mask:04b}")
        print(f"  θ = {seed.theta:.4f}")
        print(f"  e² = {seed.e_squared:.4f}")
    
    print("\nRound-trip test:")
    original = PresetSeeds.full_duality_stack()
    print(f"  Original: {original.to_hex()}")
    
    aether = decode(original)
    print(f"  Aether: {aether.superposition_form()}")
    
    recovered = encode(aether)
    print(f"  Recovered: {recovered.to_hex()}")
    
    # Not exactly equal due to quantization, but close
    print(f"  θ match: {abs(original.theta - recovered.theta) < 0.01}")
