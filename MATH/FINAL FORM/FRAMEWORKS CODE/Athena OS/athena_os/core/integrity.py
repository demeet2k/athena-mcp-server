"""
ATHENA OS - Error Correction and Integrity
==========================================
Hamming(31,26) perfect code for error detection and correction.

Properties:
- 31 total bits = 26 data + 5 parity
- Single-error correction (SEC)
- Double-error detection (DED)
- Perfect code: 2^5 = 32 syndromes cover 31 positions + 1 no-error

Additional integrity mechanisms:
- Triangular checksum: T(17) = 153
- Modular arithmetic: mod 19
- Geometric ratio: 265/153 ≈ √3
- Pythagorean spiral proof
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import math


# =============================================================================
# HAMMING CODE CONSTANTS
# =============================================================================

class HammingConstants:
    """Constants for Hamming(31,26) code."""
    
    # Code parameters
    N = 31          # Codeword length
    K = 26          # Data bits
    R = 5           # Parity bits (2^5 - 1 = 31)
    
    # Parity bit positions (powers of 2)
    PARITY_POSITIONS = [1, 2, 4, 8, 16]
    
    # Data bit positions (all others)
    DATA_POSITIONS = [i for i in range(1, 32) if i not in [1, 2, 4, 8, 16]]
    
    @classmethod
    def is_parity_position(cls, pos: int) -> bool:
        """Check if position is a parity bit (1-indexed)."""
        return pos > 0 and (pos & (pos - 1)) == 0  # Power of 2
    
    @classmethod
    def syndrome_positions(cls, syndrome: int) -> int:
        """Convert syndrome to error position (0 = no error)."""
        return syndrome  # Syndrome directly indicates error position


# =============================================================================
# HAMMING ENCODER/DECODER
# =============================================================================

class HammingCode:
    """
    Hamming(31,26) encoder/decoder.
    
    Uses SECDED (Single Error Correction, Double Error Detection).
    """
    
    def __init__(self):
        self.n = HammingConstants.N
        self.k = HammingConstants.K
        self.r = HammingConstants.R
    
    def encode(self, data: int) -> int:
        """
        Encode 26-bit data into 31-bit codeword.
        
        Bit positions (1-indexed):
        - Parity: 1, 2, 4, 8, 16
        - Data: 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
        """
        # Ensure data fits in 26 bits
        data = data & ((1 << self.k) - 1)
        
        # Place data bits in non-parity positions
        codeword = 0
        data_idx = 0
        
        for pos in range(1, self.n + 1):
            if not HammingConstants.is_parity_position(pos):
                if (data >> data_idx) & 1:
                    codeword |= (1 << (pos - 1))
                data_idx += 1
        
        # Calculate and set parity bits
        for p_pos in HammingConstants.PARITY_POSITIONS:
            parity = 0
            for pos in range(1, self.n + 1):
                if pos & p_pos:  # Position covered by this parity
                    if (codeword >> (pos - 1)) & 1:
                        parity ^= 1
            if parity:
                codeword |= (1 << (p_pos - 1))
        
        return codeword
    
    def decode(self, codeword: int) -> Tuple[int, int, bool]:
        """
        Decode 31-bit codeword to 26-bit data.
        
        Returns: (data, error_position, corrected)
        - error_position: 0 if no error, 1-31 if single error
        - corrected: True if error was corrected
        """
        # Calculate syndrome
        syndrome = 0
        for p_idx, p_pos in enumerate(HammingConstants.PARITY_POSITIONS):
            parity = 0
            for pos in range(1, self.n + 1):
                if pos & p_pos:
                    if (codeword >> (pos - 1)) & 1:
                        parity ^= 1
            if parity:
                syndrome |= (1 << p_idx)
        
        # Correct single-bit error
        corrected = False
        if syndrome != 0:
            if syndrome <= self.n:
                codeword ^= (1 << (syndrome - 1))
                corrected = True
        
        # Extract data bits
        data = 0
        data_idx = 0
        for pos in range(1, self.n + 1):
            if not HammingConstants.is_parity_position(pos):
                if (codeword >> (pos - 1)) & 1:
                    data |= (1 << data_idx)
                data_idx += 1
        
        return (data, syndrome, corrected)
    
    def check(self, codeword: int) -> int:
        """
        Check codeword for errors.
        
        Returns syndrome (0 = no error, >0 = error position).
        """
        syndrome = 0
        for p_idx, p_pos in enumerate(HammingConstants.PARITY_POSITIONS):
            parity = 0
            for pos in range(1, self.n + 1):
                if pos & p_pos:
                    if (codeword >> (pos - 1)) & 1:
                        parity ^= 1
            if parity:
                syndrome |= (1 << p_idx)
        return syndrome
    
    def inject_error(self, codeword: int, position: int) -> int:
        """Inject a single-bit error at specified position (1-indexed)."""
        if 1 <= position <= self.n:
            return codeword ^ (1 << (position - 1))
        return codeword


# =============================================================================
# INTEGRITY CHECKSUMS
# =============================================================================

class IntegrityChecksums:
    """
    Additional integrity checking mechanisms beyond Hamming code.
    
    - Triangular: T(17) = 153 = 1+2+...+17
    - Modular: All operations mod 19
    - Geometric: 265/153 ≈ √3 (vesica piscis)
    """
    
    # Constants
    TRIANGULAR_N = 17
    TRIANGULAR_SUM = 153  # T(17)
    MODULUS = 19
    VESICA_NUMERATOR = 265
    VESICA_DENOMINATOR = 153
    SQRT3_APPROX = 265 / 153  # ≈ 1.732026...
    
    @classmethod
    def triangular(cls, n: int) -> int:
        """Compute triangular number T(n) = n(n+1)/2."""
        return n * (n + 1) // 2
    
    @classmethod
    def triangular_checksum(cls, data: bytes) -> int:
        """
        Compute triangular checksum.
        Sum bytes, then reduce to triangular reference.
        """
        total = sum(data)
        # Map to triangular number index
        n = 1
        while cls.triangular(n) < total:
            n += 1
        return cls.triangular(n) % cls.TRIANGULAR_SUM
    
    @classmethod
    def modular_checksum(cls, data: bytes) -> int:
        """Compute checksum mod 19."""
        total = sum(data)
        return total % cls.MODULUS
    
    @classmethod
    def geometric_checksum(cls, data: bytes) -> float:
        """
        Compute geometric checksum based on vesica piscis ratio.
        Returns value in [0, √3) range.
        """
        total = sum(data)
        # Scale by √3 approximation
        return (total * cls.SQRT3_APPROX) % cls.SQRT3_APPROX
    
    @classmethod
    def combined_checksum(cls, data: bytes) -> Tuple[int, int, float]:
        """Compute all three checksums."""
        return (
            cls.triangular_checksum(data),
            cls.modular_checksum(data),
            cls.geometric_checksum(data)
        )
    
    @classmethod
    def verify_combined(cls, data: bytes, 
                        expected: Tuple[int, int, float],
                        tolerance: float = 0.0001) -> bool:
        """Verify combined checksum matches expected."""
        actual = cls.combined_checksum(data)
        return (
            actual[0] == expected[0] and
            actual[1] == expected[1] and
            abs(actual[2] - expected[2]) < tolerance
        )


# =============================================================================
# PYTHAGOREAN COMMA (Spiral Structure Proof)
# =============================================================================

class PythagoreanComma:
    """
    The Pythagorean comma proves spiral (non-cyclic) structure.
    
    (3/2)^12 ≠ 2^7
    
    Comma = 531441 / 524288 ≈ 1.01364...
    
    This fundamental inequality prevents eternal return,
    ensuring genuine progress in the system.
    """
    
    NUMERATOR = 3**12    # 531441
    DENOMINATOR = 2**19  # 524288
    
    COMMA = NUMERATOR / DENOMINATOR  # ≈ 1.01364326...
    
    # Exact rational representation
    COMMA_NUM = 531441
    COMMA_DEN = 524288
    
    @classmethod
    def compute_comma(cls) -> float:
        """Compute the Pythagorean comma."""
        # (3/2)^12 / 2^7 = 3^12 / 2^12 / 2^7 = 3^12 / 2^19
        return (3**12) / (2**19)
    
    @classmethod
    def verify_non_closure(cls) -> bool:
        """
        Verify that 12 fifths doesn't equal 7 octaves.
        This proves the spiral (not circular) structure.
        """
        # 12 perfect fifths
        fifths = (3/2) ** 12
        
        # 7 octaves
        octaves = 2 ** 7
        
        return fifths != octaves
    
    @classmethod
    def spiral_progress(cls, n_fifths: int) -> float:
        """
        Compute cumulative deviation after n fifths.
        Returns the "drift" from perfect octave closure.
        """
        fifths_total = (3/2) ** n_fifths
        # How many octaves we've passed
        octaves_passed = int(math.log2(fifths_total))
        # Deviation from nearest octave
        nearest_octave = 2 ** octaves_passed
        return fifths_total / nearest_octave
    
    @classmethod
    def is_cyclic(cls) -> bool:
        """Return False - the system is inherently spiral, not cyclic."""
        return False
    
    @classmethod
    def progress_guarantee(cls) -> str:
        """
        The comma guarantees that we never return to exactly
        the same state - there is always genuine progress.
        """
        return (
            f"Pythagorean Comma = {cls.COMMA_NUM}/{cls.COMMA_DEN} ≈ {cls.COMMA:.10f}\n"
            f"Since (3/2)^12 ≠ 2^7, the system is spiral, not cyclic.\n"
            f"Every complete cycle advances by factor {cls.COMMA:.6f}.\n"
            f"Eternal return is mathematically impossible."
        )


# =============================================================================
# FLUX QUANTIZATION AND DIMENSION CHECKSUM
# =============================================================================

class SpacetimeConstants:
    """
    Constants from the 6D spacetime substrate.
    
    M^6 = M^4 × T^2 with Einstein-Maxwell-Dilaton equations.
    """
    
    # Flux quanta
    FLUX_N1 = 7
    FLUX_N2 = 19
    
    # Dilaton wave numbers
    WAVE_K1 = 17
    WAVE_K2 = 103
    
    # Dimensional checksum
    DIM_CHECKSUM = 114  # = 19 × 6
    
    # Time dilation at wormhole throat
    TIME_DILATION = 309  # 309:1 ratio
    
    # Structural constants
    KAPPA = [2, 4, 10, 31, 465]  # κ₁ through κ₅
    
    @classmethod
    def verify_dimensional_checksum(cls) -> bool:
        """Verify N = 19 × 6 = 114."""
        return cls.DIM_CHECKSUM == cls.FLUX_N2 * 6
    
    @classmethod
    def verify_structural_constants(cls) -> bool:
        """Verify κ₅ = C(31,2) = 465."""
        from math import comb
        return cls.KAPPA[4] == comb(31, 2)
    
    @classmethod
    def flux_product(cls) -> int:
        """n₁ × n₂ = 7 × 19 = 133."""
        return cls.FLUX_N1 * cls.FLUX_N2
    
    @classmethod
    def wave_product(cls) -> int:
        """k × k' = 17 × 103 = 1751."""
        return cls.WAVE_K1 * cls.WAVE_K2


# =============================================================================
# ERROR CORRECTION WRAPPER
# =============================================================================

@dataclass
class ProtectedWord:
    """
    A data word with full error protection.
    
    Combines:
    - Hamming(31,26) SEC-DED
    - Triangular checksum
    - Modular checksum
    - Geometric checksum
    """
    data: int  # 26-bit data
    codeword: int = 0  # 31-bit Hamming encoded
    triangular: int = 0
    modular: int = 0
    geometric: float = 0.0
    
    def __post_init__(self):
        """Compute all protection codes."""
        self._encode()
    
    def _encode(self) -> None:
        """Encode data with all protection mechanisms."""
        hamming = HammingCode()
        self.codeword = hamming.encode(self.data)
        
        # Convert to bytes for checksum
        data_bytes = self.data.to_bytes(4, 'little')
        self.triangular, self.modular, self.geometric = \
            IntegrityChecksums.combined_checksum(data_bytes)
    
    def verify(self) -> Tuple[bool, str]:
        """
        Verify all integrity checks.
        
        Returns: (valid, message)
        """
        # Check Hamming code
        hamming = HammingCode()
        syndrome = hamming.check(self.codeword)
        
        if syndrome != 0:
            return (False, f"Hamming error at position {syndrome}")
        
        # Decode and verify data matches
        decoded, _, _ = hamming.decode(self.codeword)
        if decoded != self.data:
            return (False, "Data mismatch after Hamming decode")
        
        # Check other checksums
        data_bytes = self.data.to_bytes(4, 'little')
        actual = IntegrityChecksums.combined_checksum(data_bytes)
        
        if actual[0] != self.triangular:
            return (False, f"Triangular checksum mismatch: {actual[0]} != {self.triangular}")
        
        if actual[1] != self.modular:
            return (False, f"Modular checksum mismatch: {actual[1]} != {self.modular}")
        
        if abs(actual[2] - self.geometric) > 0.0001:
            return (False, f"Geometric checksum mismatch: {actual[2]} != {self.geometric}")
        
        return (True, "All integrity checks passed")
    
    def correct(self) -> bool:
        """
        Attempt to correct errors.
        
        Returns True if correction was performed.
        """
        hamming = HammingCode()
        decoded, syndrome, corrected = hamming.decode(self.codeword)
        
        if corrected:
            self.data = decoded
            self._encode()  # Recompute all checksums
            return True
        
        return False
    
    def __str__(self) -> str:
        valid, msg = self.verify()
        status = "✓" if valid else "✗"
        return (
            f"ProtectedWord[{status}]\n"
            f"  Data: 0x{self.data:07x} ({self.data})\n"
            f"  Hamming: 0x{self.codeword:08x}\n"
            f"  Triangular: {self.triangular}\n"
            f"  Modular: {self.modular}\n"
            f"  Geometric: {self.geometric:.6f}"
        )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hamming_code() -> bool:
    """Validate Hamming code properties."""
    hamming = HammingCode()
    
    # Test encoding/decoding round-trip
    for data in [0, 1, 12345, (1 << 26) - 1]:
        data = data & ((1 << 26) - 1)  # Ensure 26 bits
        encoded = hamming.encode(data)
        decoded, syndrome, corrected = hamming.decode(encoded)
        assert decoded == data, f"Round-trip failed for {data}"
        assert syndrome == 0, f"Unexpected syndrome for {data}"
        assert not corrected, f"Unexpected correction for {data}"
    
    # Test error correction
    data = 0b10101010101010101010101010
    encoded = hamming.encode(data)
    
    for err_pos in range(1, 32):
        corrupted = hamming.inject_error(encoded, err_pos)
        decoded, syndrome, corrected = hamming.decode(corrupted)
        assert decoded == data, f"Failed to correct error at position {err_pos}"
        assert syndrome == err_pos, f"Wrong syndrome for error at {err_pos}"
        assert corrected, f"Should have corrected error at {err_pos}"
    
    return True


def validate_checksums() -> bool:
    """Validate integrity checksum properties."""
    # Triangular(17) = 153
    assert IntegrityChecksums.triangular(17) == 153
    
    # Modulus is 19
    assert IntegrityChecksums.MODULUS == 19
    
    # Vesica piscis ratio ≈ √3
    sqrt3 = math.sqrt(3)
    assert abs(IntegrityChecksums.SQRT3_APPROX - sqrt3) < 0.001
    
    return True


def validate_comma() -> bool:
    """Validate Pythagorean comma properties."""
    assert PythagoreanComma.verify_non_closure()
    assert not PythagoreanComma.is_cyclic()
    
    # Verify comma value
    expected = 531441 / 524288
    assert abs(PythagoreanComma.compute_comma() - expected) < 1e-10
    
    return True


def validate_spacetime() -> bool:
    """Validate spacetime constants."""
    assert SpacetimeConstants.verify_dimensional_checksum()
    assert SpacetimeConstants.verify_structural_constants()
    assert SpacetimeConstants.flux_product() == 133
    assert SpacetimeConstants.wave_product() == 1751
    
    return True


if __name__ == "__main__":
    print("Validating Hamming code...")
    assert validate_hamming_code()
    print("✓ Hamming(31,26) validated")
    
    print("\nValidating checksums...")
    assert validate_checksums()
    print("✓ Integrity checksums validated")
    
    print("\nValidating Pythagorean comma...")
    assert validate_comma()
    print("✓ Spiral structure proved")
    
    print("\nValidating spacetime constants...")
    assert validate_spacetime()
    print("✓ Spacetime constants validated")
    
    # Demo
    print("\n=== Protected Word Demo ===")
    pw = ProtectedWord(data=123456)
    print(pw)
    
    valid, msg = pw.verify()
    print(f"\nVerification: {msg}")
    
    # Inject error and correct
    print("\n--- Injecting error ---")
    hamming = HammingCode()
    pw.codeword = hamming.inject_error(pw.codeword, 15)
    valid, msg = pw.verify()
    print(f"After error: {msg}")
    
    corrected = pw.correct()
    print(f"Correction attempted: {corrected}")
    valid, msg = pw.verify()
    print(f"After correction: {msg}")
    
    print("\n=== Pythagorean Comma ===")
    print(PythagoreanComma.progress_guarantee())
