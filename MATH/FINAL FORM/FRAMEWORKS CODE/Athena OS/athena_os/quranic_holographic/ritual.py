"""
ATHENA OS - QUR'ANIC HOLOGRAPHIC LATTICE
========================================
Part IV: The Ritual Topology (Somatic Interface)

THE SOMATIC TOPOLOGY:
    Physical rituals as "machine code" execution of boundary checksums.
    The body functions as a read/write head, inscribing mathematical
    boundary conditions into local spacetime through quantized movement.

HAJJ PROTOCOL:
    - Tawaf: 7-circuit circumambulation (flux winding)
    - Sa'y: 7 oscillations (standing wave)
    - Ramy: 7×3×3+7 = 70 stones (KK pointer approximation)

SALAH PROTOCOL:
    - 5 prayer times (warp synchronization)
    - 17 daily rakaat (dilaton harmonic k₁)
    - 7 prostration points (flux grounding)
    - 19-letter Basmala (unity guard)

SOURCES:
    - Qur'anic Holographic Lattice manuscript, Appendix D
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np

from .lattice import IntegerLattice


# =============================================================================
# PRAYER TIMES
# =============================================================================

class PrayerTime(Enum):
    """The five daily prayer times."""
    
    FAJR = ("dawn", 2, "morning twilight")
    ZUHR = ("noon", 4, "solar zenith")
    ASR = ("afternoon", 4, "late afternoon")
    MAGHRIB = ("sunset", 3, "evening twilight")
    ISHA = ("night", 4, "night darkness")
    
    def __init__(self, name: str, rakaat: int, description: str):
        self._name = name
        self.rakaat = rakaat
        self.description = description


@dataclass
class SalahCycle:
    """A single prayer cycle (rakah)."""
    
    prayer_time: PrayerTime
    cycle_number: int
    
    # Components
    qiyam_seconds: float = 60.0      # Standing
    ruku_seconds: float = 10.0       # Bowing
    sujud_seconds: float = 15.0      # Prostration (×2)
    juloos_seconds: float = 5.0      # Sitting
    
    @property
    def total_duration(self) -> float:
        """Total duration of one rakah."""
        return self.qiyam_seconds + self.ruku_seconds + 2*self.sujud_seconds + self.juloos_seconds
    
    @property
    def sujud_contact_points(self) -> int:
        """7 points of ground contact in sujud."""
        return 7  # Forehead, 2 hands, 2 knees, 2 feet


@dataclass
class DailySalahProtocol:
    """
    Complete daily prayer protocol.
    
    Total: 2+4+4+3+4 = 17 rakaat (matches k₁)
    """
    
    def __post_init__(self):
        self.prayers = list(PrayerTime)
        self.lattice = IntegerLattice()
    
    @property
    def total_rakaat(self) -> int:
        """Sum of all rakaat = 17."""
        return sum(p.rakaat for p in self.prayers)
    
    @property
    def matches_harmonic_k1(self) -> bool:
        """Verify match with dilaton wave-number."""
        return self.total_rakaat == self.lattice.HARMONIC_K1
    
    def prayer_breakdown(self) -> Dict[str, int]:
        """Breakdown of rakaat by prayer."""
        return {p.name: p.rakaat for p in self.prayers}
    
    def total_sujud_groundings(self) -> int:
        """
        Total ground contact instances.
        
        Each rakah has 2 sujud, each with 7 contact points.
        """
        return self.total_rakaat * 2 * 7  # 17 × 2 × 7 = 238
    
    def basmala_letters_per_day(self) -> int:
        """
        Basmala recited in each rakah.
        
        19 letters × 17 rakaat = 323
        """
        return 19 * self.total_rakaat
    
    def flux_activation_summary(self) -> Dict[str, Any]:
        """Summary of flux-related activations."""
        return {
            "prayer_times": 5,
            "total_rakaat": self.total_rakaat,
            "k1_match": self.matches_harmonic_k1,
            "sujud_points_per_rakah": 7,
            "basmala_letters": 19,
            "daily_basmala_total": self.basmala_letters_per_day(),
        }


# =============================================================================
# HAJJ PROTOCOL
# =============================================================================

class HajjRite(Enum):
    """The rites of Hajj pilgrimage."""
    
    IHRAM = ("consecration", 0, "entry into sacred state")
    TAWAF = ("circumambulation", 7, "7-circuit Ka'ba orbit")
    SAY = ("running", 7, "oscillation between Safa-Marwa")
    WUQUF = ("standing", 1, "standing at Arafat")
    MUZDALIFAH = ("gathering", 1, "night at Muzdalifah")
    RAMY_1 = ("stoning_day1", 7, "first day stoning")
    RAMY_2 = ("stoning_day2", 21, "second day (7×3)")
    RAMY_3 = ("stoning_day3", 21, "third day (7×3)")
    RAMY_4 = ("stoning_day4", 21, "fourth day (7×3)")
    TAWAF_IFADAH = ("tawaf_return", 7, "return circumambulation")
    FAREWELL = ("farewell", 7, "farewell tawaf")
    
    def __init__(self, name: str, count: int, description: str):
        self._name = name
        self.count = count
        self.description = description


@dataclass
class TawafCircuit:
    """
    A single circuit of Tawaf.
    
    Circumambulation of the Ka'ba counter-clockwise.
    Total: 7 circuits (flux winding).
    """
    
    circuit_number: int  # 1-7
    
    # Geometric parameters
    radius_m: float = 10.0  # Approximate radius from Ka'ba center
    
    @property
    def circumference(self) -> float:
        """Circuit length."""
        return 2 * np.pi * self.radius_m
    
    @property
    def winding_number(self) -> int:
        """Topological winding number for this circuit."""
        return self.circuit_number


@dataclass
class SayOscillation:
    """
    A single oscillation of Sa'y.
    
    Running between Safa and Marwa hills.
    Total: 7 laps (standing wave).
    """
    
    lap_number: int  # 1-7
    
    # The two poles
    start_hill: str = "Safa"
    end_hill: str = "Marwa"
    
    # Distance
    distance_m: float = 450.0  # Approximate
    
    @property
    def direction(self) -> str:
        """Direction of this lap."""
        if self.lap_number % 2 == 1:
            return f"{self.start_hill} → {self.end_hill}"
        return f"{self.end_hill} → {self.start_hill}"
    
    @property
    def phase(self) -> float:
        """Phase of standing wave (0 to 2π over 7 laps)."""
        return 2 * np.pi * self.lap_number / 7


@dataclass
class RamyAlJamarat:
    """
    Stoning of the pillars.
    
    Three pillars: Sughra (small), Wusta (medium), Kubra (large)
    7 stones at each pillar.
    """
    
    day: int  # 1-4 of Tashreeq
    pillar: str  # "sughra", "wusta", "kubra"
    stones_thrown: int = 7
    
    @property
    def target_position(self) -> Tuple[str, str]:
        """Location identifier."""
        return (f"day_{self.day}", self.pillar)


@dataclass
class HajjProtocol:
    """
    Complete Hajj protocol execution.
    
    Total stones: ~70 (approximates KK pointer 71)
    Total circuits: 21 (3 × 7 for multiple tawafs)
    """
    
    def __post_init__(self):
        self.rites = list(HajjRite)
        self.lattice = IntegerLattice()
        
        # Generate Tawaf circuits
        self.tawaf_circuits = [TawafCircuit(i) for i in range(1, 8)]
        
        # Generate Sa'y oscillations
        self.say_oscillations = [SayOscillation(i) for i in range(1, 8)]
    
    def total_tawaf_circuits(self) -> int:
        """Total circuits across all tawafs."""
        # Main Tawaf + Ifadah Tawaf + Farewell Tawaf = 7 × 3 = 21
        return 21
    
    def total_say_laps(self) -> int:
        """Total Sa'y oscillations."""
        return 7
    
    def total_stones(self) -> int:
        """
        Total stones thrown during Ramy.
        
        Day 1: 7 (Kubra only)
        Day 2: 21 (7 × 3 pillars)
        Day 3: 21 (7 × 3 pillars)
        Day 4: 21 (7 × 3 pillars)
        
        Total: 7 + 21 + 21 + 21 = 70
        """
        return 7 + 21 + 21 + 21  # = 70
    
    def total_with_intention(self) -> int:
        """
        Total including intention stone.
        
        70 + 1 (intention) = 71 (KK pointer)
        """
        return self.total_stones() + 1
    
    def matches_kk_pointer(self) -> bool:
        """Verify approximation to KK pointer."""
        return abs(self.total_with_intention() - self.lattice.KK_POINTER_1) <= 1
    
    def winding_summary(self) -> Dict[str, Any]:
        """Summary of topological windings."""
        return {
            "tawaf_circuits_per_set": 7,
            "total_tawaf_sets": 3,
            "total_circuits": self.total_tawaf_circuits(),
            "say_oscillations": self.total_say_laps(),
            "total_stones": self.total_stones(),
            "with_intention": self.total_with_intention(),
            "kk_pointer_match": self.matches_kk_pointer(),
        }


# =============================================================================
# QIBLA ALIGNMENT
# =============================================================================

@dataclass 
class QiblaVector:
    """
    Direction vector to Ka'ba (Qibla).
    
    All prayers aligned to single geodesic vector,
    minimizing angular deviation in teleportation geometry.
    """
    
    # Observer location (latitude, longitude in degrees)
    observer_lat: float = 0.0
    observer_lon: float = 0.0
    
    # Ka'ba coordinates
    KAABA_LAT: float = 21.4225
    KAABA_LON: float = 39.8262
    
    def qibla_angle(self) -> float:
        """
        Calculate Qibla direction from observer location.
        
        Returns bearing angle in degrees (0 = North, 90 = East).
        """
        lat1 = np.radians(self.observer_lat)
        lat2 = np.radians(self.KAABA_LAT)
        dlon = np.radians(self.KAABA_LON - self.observer_lon)
        
        x = np.sin(dlon) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        
        angle = np.degrees(np.arctan2(x, y))
        return (angle + 360) % 360
    
    def distance_km(self) -> float:
        """Great circle distance to Ka'ba in km."""
        R = 6371  # Earth radius
        
        lat1 = np.radians(self.observer_lat)
        lat2 = np.radians(self.KAABA_LAT)
        dlat = lat2 - lat1
        dlon = np.radians(self.KAABA_LON - self.observer_lon)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c


# =============================================================================
# PROSTRATION GEOMETRY
# =============================================================================

@dataclass
class SujudGeometry:
    """
    The geometry of prostration (Sujud).
    
    7 contact points form a grounding circuit
    for the flux checksum.
    """
    
    # Contact points
    CONTACT_POINTS = [
        "forehead",
        "right_hand",
        "left_hand",
        "right_knee",
        "left_knee",
        "right_foot_toes",
        "left_foot_toes",
    ]
    
    def __post_init__(self):
        self.n_points = len(self.CONTACT_POINTS)
    
    @property
    def flux_quantum(self) -> int:
        """Matches n₁ = 7."""
        return self.n_points
    
    def contact_polygon(self) -> Dict[str, Tuple[float, float]]:
        """
        Approximate 2D positions of contact points.
        
        Returns relative coordinates (x, y) in body lengths.
        """
        return {
            "forehead": (0.0, 0.3),
            "right_hand": (0.15, 0.2),
            "left_hand": (-0.15, 0.2),
            "right_knee": (0.1, 0.0),
            "left_knee": (-0.1, 0.0),
            "right_foot_toes": (0.1, -0.3),
            "left_foot_toes": (-0.1, -0.3),
        }
    
    def grounding_area(self) -> float:
        """
        Calculate area of contact polygon.
        
        Uses shoelace formula.
        """
        points = list(self.contact_polygon().values())
        n = len(points)
        
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2


# =============================================================================
# UNIFIED RITUAL INTERFACE
# =============================================================================

@dataclass
class RitualInterface:
    """
    Unified interface for all ritual protocols.
    
    The body as read/write head for spacetime geometry.
    """
    
    salah: DailySalahProtocol = field(default_factory=DailySalahProtocol)
    hajj: HajjProtocol = field(default_factory=HajjProtocol)
    sujud: SujudGeometry = field(default_factory=SujudGeometry)
    
    def __post_init__(self):
        self.lattice = IntegerLattice()
    
    def complete_integer_activation(self) -> Dict[str, int]:
        """
        All integers activated through ritual.
        
        Returns mapping of lattice integers to activation source.
        """
        return {
            "7_flux_primary": self.sujud.flux_quantum,
            "17_dilaton_k1": self.salah.total_rakaat,
            "19_unity_guard": 19,  # Basmala letters
            "71_kk_pointer": self.hajj.total_with_intention(),
            "5_prayer_times": len(self.salah.prayers),
        }
    
    def verify_lattice_coverage(self) -> Dict[str, bool]:
        """Verify that rituals activate key lattice integers."""
        activations = self.complete_integer_activation()
        
        return {
            "n1_activated": activations.get("7_flux_primary") == 7,
            "k1_activated": activations.get("17_dilaton_k1") == 17,
            "n2_activated": activations.get("19_unity_guard") == 19,
            "kk_pointer_activated": abs(activations.get("71_kk_pointer", 0) - 71) <= 1,
        }
    
    def daily_execution_log(self) -> List[str]:
        """Generate daily ritual execution log."""
        log = []
        
        for prayer in PrayerTime:
            log.append(f"[SALAH] {prayer.name}: {prayer.rakaat} rakaat × 7 sujud points")
        
        log.append(f"[TOTAL] Daily rakaat: {self.salah.total_rakaat} (= k₁)")
        log.append(f"[TOTAL] Basmala recitations: {self.salah.total_rakaat} × 19 letters")
        
        return log


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ritual() -> bool:
    """Validate the ritual module."""
    
    # Test DailySalahProtocol
    salah = DailySalahProtocol()
    assert salah.total_rakaat == 17
    assert salah.matches_harmonic_k1
    
    # Test HajjProtocol
    hajj = HajjProtocol()
    assert hajj.total_stones() == 70
    assert hajj.total_with_intention() == 71
    assert hajj.matches_kk_pointer()
    
    # Test Tawaf circuits
    assert len(hajj.tawaf_circuits) == 7
    
    # Test Sa'y oscillations
    assert len(hajj.say_oscillations) == 7
    
    # Test SujudGeometry
    sujud = SujudGeometry()
    assert sujud.flux_quantum == 7
    assert len(sujud.CONTACT_POINTS) == 7
    
    # Test QiblaVector
    qibla = QiblaVector(observer_lat=40.7128, observer_lon=-74.0060)  # New York
    angle = qibla.qibla_angle()
    assert 0 <= angle <= 360
    
    distance = qibla.distance_km()
    assert distance > 0
    
    # Test RitualInterface
    interface = RitualInterface()
    coverage = interface.verify_lattice_coverage()
    assert coverage["n1_activated"]
    assert coverage["k1_activated"]
    assert coverage["kk_pointer_activated"]
    
    return True


if __name__ == "__main__":
    print("Validating Ritual Module...")
    assert validate_ritual()
    print("✓ Ritual module validated")
    
    # Demo
    print("\n--- Ritual Topology Demo ---")
    
    print("\n1. Daily Salah Protocol:")
    salah = DailySalahProtocol()
    for prayer in PrayerTime:
        print(f"   {prayer.name}: {prayer.rakaat} rakaat")
    print(f"   Total: {salah.total_rakaat} = k₁ ✓")
    
    print("\n2. Hajj Protocol:")
    hajj = HajjProtocol()
    print(f"   Tawaf circuits: 7 × 3 = {hajj.total_tawaf_circuits()}")
    print(f"   Sa'y laps: {hajj.total_say_laps()}")
    print(f"   Ramy stones: {hajj.total_stones()} + 1 = {hajj.total_with_intention()} ≈ KK₁")
    
    print("\n3. Sujud Geometry:")
    sujud = SujudGeometry()
    print(f"   Contact points: {sujud.flux_quantum} = n₁ ✓")
    for point in sujud.CONTACT_POINTS[:3]:
        print(f"   - {point}")
    print("   ...")
    
    print("\n4. Qibla Vector (from New York):")
    qibla = QiblaVector(observer_lat=40.7128, observer_lon=-74.0060)
    print(f"   Bearing: {qibla.qibla_angle():.1f}°")
    print(f"   Distance: {qibla.distance_km():.0f} km")
    
    print("\n5. Lattice Coverage:")
    interface = RitualInterface()
    coverage = interface.verify_lattice_coverage()
    for key, val in coverage.items():
        status = "✓" if val else "✗"
        print(f"   {key}: {status}")
