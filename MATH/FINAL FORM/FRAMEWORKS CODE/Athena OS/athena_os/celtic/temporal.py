"""
ATHENA OS - CELTIC OGHAM KERNEL: TEMPORAL MODULE
=================================================
Seasonal Firewall and Tree Calendar

THE SEASONAL FIREWALL (Quarter Days):
    The Celtic system operates on Split-Reality Architecture.
    The Wheel of the Year is the Access Control Schedule.
    
SAMHAIN (November 1):
    - Firewall Permeability → 100%
    - Synchronization: Barrier dissolved
    - Agents from Otherworld enter physical plane
    - High entropy injection risk
    
BELTANE (May 1):
    - Firewall Permeability → 100% (opposite direction)
    - Creation window: Physical can imprint on Otherworld
    
IMBOLC (February 1):
    - Firewall Permeability: 50%
    - Initialization phase
    
LUGHNASADH (August 1):
    - Firewall Permeability: 50%
    - Harvest phase (data collection)

THE ARBOREAL CLOCK (Beth-Luis-Nion):
    Bio-morphic Timing Lattice synchronized with
    metabolic cycles of botanical substrate.
    
    T_year = (13 × 28) + 1 = 365
    
    Lunar-Solar Hybrid aligning computational cycle
    with lunar frequency (f_lunar ≈ 28 days).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import numpy as np


# =============================================================================
# QUARTER DAYS
# =============================================================================

class QuarterDay(Enum):
    """
    The Four Quarter Days (Fire Festivals).
    
    Mark transitions between seasons and
    firewall permeability states.
    """
    
    SAMHAIN = "samhain"           # Nov 1 - New Year / Death
    IMBOLC = "imbolc"             # Feb 1 - Spring begins
    BELTANE = "beltane"           # May 1 - Summer begins  
    LUGHNASADH = "lughnasadh"     # Aug 1 - Harvest begins


class CrossQuarter(Enum):
    """
    The Four Cross-Quarter Days (Solar festivals).
    
    Mark solstices and equinoxes.
    """
    
    WINTER_SOLSTICE = "winter_solstice"    # Dec 21
    SPRING_EQUINOX = "spring_equinox"      # Mar 21
    SUMMER_SOLSTICE = "summer_solstice"    # Jun 21
    AUTUMN_EQUINOX = "autumn_equinox"      # Sep 21


# =============================================================================
# FIREWALL STATES
# =============================================================================

class FirewallState(Enum):
    """States of the Otherworld firewall."""
    
    CLOSED = "closed"              # 0% permeability
    FILTERED = "filtered"          # 25% permeability
    PARTIAL = "partial"            # 50% permeability
    PERMEABLE = "permeable"        # 75% permeability
    OPEN = "open"                  # 100% permeability


@dataclass
class FirewallConfig:
    """Configuration for the Seasonal Firewall."""
    
    state: FirewallState
    permeability: float            # 0.0 - 1.0
    direction: str                 # "inbound", "outbound", "both"
    risk_level: float              # Entropy injection risk
    
    active_protocols: List[str] = field(default_factory=list)


# =============================================================================
# SEASONAL FIREWALL
# =============================================================================

class SeasonalFirewall:
    """
    The Seasonal Firewall - Access Control between Realms.
    
    Governs bandwidth between:
    - Runtime Environment (Physical World)
    - Developer Environment (Otherworld)
    
    Permeability varies with the Wheel of the Year.
    """
    
    # Permeability by Quarter Day
    QUARTER_PERMEABILITY = {
        QuarterDay.SAMHAIN: 1.0,      # Fully open (inbound)
        QuarterDay.IMBOLC: 0.5,       # Half open
        QuarterDay.BELTANE: 1.0,      # Fully open (outbound)
        QuarterDay.LUGHNASADH: 0.5,   # Half open
    }
    
    # Direction by Quarter Day
    QUARTER_DIRECTION = {
        QuarterDay.SAMHAIN: "inbound",    # Otherworld → Physical
        QuarterDay.IMBOLC: "both",        # Bidirectional
        QuarterDay.BELTANE: "outbound",   # Physical → Otherworld
        QuarterDay.LUGHNASADH: "both",    # Bidirectional
    }
    
    def __init__(self):
        self.current_config = FirewallConfig(
            state=FirewallState.FILTERED,
            permeability=0.25,
            direction="both",
            risk_level=0.0
        )
        
        # Transition tracking
        self.last_transition: Optional[QuarterDay] = None
        self.transition_count: int = 0
        
        # Access log
        self.access_log: List[Dict[str, Any]] = []
    
    def get_current_quarter(self, date: datetime = None) -> QuarterDay:
        """Determine current Quarter Day period."""
        if date is None:
            date = datetime.now()
        
        month = date.month
        day = date.day
        
        # Approximate quarters
        if (month == 11 and day >= 1) or (month in [12, 1]) or (month == 2 and day < 1):
            return QuarterDay.SAMHAIN
        elif (month == 2 and day >= 1) or (month in [3, 4]) or (month == 5 and day < 1):
            return QuarterDay.IMBOLC
        elif (month == 5 and day >= 1) or (month in [6, 7]) or (month == 8 and day < 1):
            return QuarterDay.BELTANE
        else:
            return QuarterDay.LUGHNASADH
    
    def update_for_date(self, date: datetime = None) -> FirewallConfig:
        """Update firewall configuration for current date."""
        quarter = self.get_current_quarter(date)
        
        permeability = self.QUARTER_PERMEABILITY[quarter]
        direction = self.QUARTER_DIRECTION[quarter]
        
        # Determine state
        if permeability >= 1.0:
            state = FirewallState.OPEN
        elif permeability >= 0.75:
            state = FirewallState.PERMEABLE
        elif permeability >= 0.5:
            state = FirewallState.PARTIAL
        elif permeability >= 0.25:
            state = FirewallState.FILTERED
        else:
            state = FirewallState.CLOSED
        
        # Calculate risk
        risk = permeability * 0.5  # Higher permeability = higher risk
        if quarter == QuarterDay.SAMHAIN:
            risk += 0.3  # Samhain has extra risk (dead walking)
        
        self.current_config = FirewallConfig(
            state=state,
            permeability=permeability,
            direction=direction,
            risk_level=min(1.0, risk)
        )
        
        if quarter != self.last_transition:
            self.last_transition = quarter
            self.transition_count += 1
        
        return self.current_config
    
    def check_access(self, source: str, destination: str,
                    packet_type: str = "data") -> Tuple[bool, str]:
        """
        Check if access is permitted through firewall.
        
        Returns (allowed, reason).
        """
        config = self.current_config
        
        # Determine direction
        if source == "physical" and destination == "otherworld":
            requested_direction = "outbound"
        elif source == "otherworld" and destination == "physical":
            requested_direction = "inbound"
        else:
            requested_direction = "internal"
        
        # Check direction permission
        if config.direction != "both" and config.direction != requested_direction:
            reason = f"Direction {requested_direction} blocked (current: {config.direction})"
            self._log_access(source, destination, False, reason)
            return False, reason
        
        # Check permeability (probabilistic)
        if np.random.random() > config.permeability:
            reason = f"Blocked by permeability filter ({config.permeability:.0%})"
            self._log_access(source, destination, False, reason)
            return False, reason
        
        reason = "Access granted"
        self._log_access(source, destination, True, reason)
        return True, reason
    
    def _log_access(self, source: str, destination: str,
                   allowed: bool, reason: str) -> None:
        """Log access attempt."""
        self.access_log.append({
            "source": source,
            "destination": destination,
            "allowed": allowed,
            "reason": reason,
            "state": self.current_config.state.value,
            "permeability": self.current_config.permeability
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current firewall status."""
        return {
            "state": self.current_config.state.value,
            "permeability": f"{self.current_config.permeability:.0%}",
            "direction": self.current_config.direction,
            "risk_level": f"{self.current_config.risk_level:.0%}",
            "quarter": self.last_transition.value if self.last_transition else None,
            "transitions": self.transition_count
        }


# =============================================================================
# TREE CALENDAR (BETH-LUIS-NION)
# =============================================================================

@dataclass
class TreeMonth:
    """
    A month in the Tree Calendar.
    
    Each month is 28 days (lunar cycle) with a Tree Operator
    defining the System Environment Variable.
    """
    
    name: str                      # Irish name
    tree: str                      # Associated tree
    ogham: str                     # Ogham letter
    start_day: int                 # Day of year (1-365)
    
    # Properties
    element: str = "earth"
    function: str = ""             # System function
    keywords: List[str] = field(default_factory=list)


# The 13-Month Tree Calendar
TREE_CALENDAR = [
    TreeMonth("Beth", "Birch", "ᚁ", 1,
              element="earth", function="Initialization",
              keywords=["cleansing", "new_beginnings", "birth"]),
    
    TreeMonth("Luis", "Rowan", "ᚂ", 29,
              element="fire", function="Protection",
              keywords=["quickening", "warding", "vision"]),
    
    TreeMonth("Nion", "Ash", "ᚅ", 57,
              element="air", function="Connection",
              keywords=["world_tree", "linking", "rebirth"]),
    
    TreeMonth("Fearn", "Alder", "ᚃ", 85,
              element="water", function="Foundation",
              keywords=["shield", "foundation", "oracle"]),
    
    TreeMonth("Saille", "Willow", "ᚄ", 113,
              element="water", function="Intuition",
              keywords=["moon", "flexibility", "emotion"]),
    
    TreeMonth("Huath", "Hawthorn", "ᚆ", 141,
              element="fire", function="Cleansing",
              keywords=["fear", "restraint", "purification"]),
    
    TreeMonth("Duir", "Oak", "ᚇ", 169,
              element="earth", function="Sovereignty",
              keywords=["strength", "doorway", "endurance"]),
    
    TreeMonth("Tinne", "Holly", "ᚈ", 197,
              element="fire", function="Balance",
              keywords=["challenge", "justice", "exchange"]),
    
    TreeMonth("Coll", "Hazel", "ᚉ", 225,
              element="air", function="Wisdom",
              keywords=["inspiration", "poetry", "knowledge"]),
    
    TreeMonth("Muin", "Vine", "ᚋ", 253,
              element="water", function="Prophecy",
              keywords=["harvest", "release", "truth"]),
    
    TreeMonth("Gort", "Ivy", "ᚌ", 281,
              element="earth", function="Persistence",
              keywords=["search", "growth", "spiral"]),
    
    TreeMonth("Ngetal", "Reed", "ᚍ", 309,
              element="air", function="Direct_Action",
              keywords=["threshold", "healing", "transformation"]),
    
    TreeMonth("Ruis", "Elder", "ᚏ", 337,
              element="water", function="Endings",
              keywords=["death", "regeneration", "completion"]),
]


class ArborealClock:
    """
    The Arboreal Clock - Bio-morphic Timing Lattice.
    
    Rejects abstract numeric time for Biological Time.
    Time measured by Phenological State of vegetation.
    
    Structure:
    - 13 months of 28 days = 364 days
    - Plus 1 intercalary day = 365 days
    - Each month governed by Tree Operator
    """
    
    def __init__(self, start_date: datetime = None):
        self.start_date = start_date or datetime(datetime.now().year, 1, 1)
        self.months = {m.name: m for m in TREE_CALENDAR}
        
        # Current state
        self.current_month: Optional[TreeMonth] = None
        self.day_in_month: int = 0
        self.year_day: int = 0
    
    def update(self, date: datetime = None) -> TreeMonth:
        """Update clock to given date."""
        if date is None:
            date = datetime.now()
        
        # Calculate day of year
        year_start = datetime(date.year, 1, 1)
        self.year_day = (date - year_start).days + 1
        
        # Find current month
        for month in TREE_CALENDAR:
            if month.start_day <= self.year_day < month.start_day + 28:
                self.current_month = month
                self.day_in_month = self.year_day - month.start_day + 1
                break
        
        # Handle intercalary (day 365)
        if self.year_day == 365:
            self.current_month = TREE_CALENDAR[-1]  # Elder (transition)
            self.day_in_month = 29  # Extra day
        
        return self.current_month
    
    def get_tree_operator(self) -> Dict[str, Any]:
        """Get current Tree Operator (system environment variable)."""
        if self.current_month is None:
            self.update()
        
        return {
            "tree": self.current_month.tree,
            "ogham": self.current_month.ogham,
            "element": self.current_month.element,
            "function": self.current_month.function,
            "keywords": self.current_month.keywords,
            "day": self.day_in_month,
            "month": self.current_month.name
        }
    
    def get_month_by_name(self, name: str) -> Optional[TreeMonth]:
        """Get month by Irish name."""
        return self.months.get(name)
    
    def get_month_by_tree(self, tree: str) -> Optional[TreeMonth]:
        """Get month by tree name."""
        tree_lower = tree.lower()
        for month in TREE_CALENDAR:
            if month.tree.lower() == tree_lower:
                return month
        return None
    
    def get_cycle_position(self) -> float:
        """Get position in annual cycle (0.0 - 1.0)."""
        return self.year_day / 365.0
    
    def get_phase(self) -> str:
        """Get current phenological phase."""
        position = self.get_cycle_position()
        
        if position < 0.25:
            return "dormant"      # Winter
        elif position < 0.5:
            return "growing"      # Spring
        elif position < 0.75:
            return "flowering"    # Summer
        else:
            return "harvest"      # Autumn


# =============================================================================
# WHEEL OF THE YEAR
# =============================================================================

class WheelOfTheYear:
    """
    The Complete Wheel of the Year.
    
    Integrates:
    - Seasonal Firewall (Quarter Days)
    - Arboreal Clock (Tree Calendar)
    - Cross-Quarter solar festivals
    """
    
    def __init__(self):
        self.firewall = SeasonalFirewall()
        self.clock = ArborealClock()
        
        # Festival dates (approximate day of year)
        self.festivals = {
            # Fire Festivals (Quarter Days)
            QuarterDay.SAMHAIN: 305,       # Nov 1
            QuarterDay.IMBOLC: 32,         # Feb 1
            QuarterDay.BELTANE: 121,       # May 1
            QuarterDay.LUGHNASADH: 213,    # Aug 1
            
            # Solar Festivals (Cross-Quarters)
            CrossQuarter.WINTER_SOLSTICE: 355,  # Dec 21
            CrossQuarter.SPRING_EQUINOX: 80,    # Mar 21
            CrossQuarter.SUMMER_SOLSTICE: 172,  # Jun 21
            CrossQuarter.AUTUMN_EQUINOX: 264,   # Sep 21
        }
    
    def update(self, date: datetime = None) -> Dict[str, Any]:
        """Update wheel to current date."""
        if date is None:
            date = datetime.now()
        
        # Update components
        self.firewall.update_for_date(date)
        self.clock.update(date)
        
        # Check for nearby festivals
        upcoming = self._get_upcoming_festivals(date)
        
        return {
            "date": date.isoformat(),
            "tree_month": self.clock.current_month.name if self.clock.current_month else None,
            "tree_operator": self.clock.get_tree_operator(),
            "firewall": self.firewall.get_status(),
            "phase": self.clock.get_phase(),
            "upcoming_festivals": upcoming
        }
    
    def _get_upcoming_festivals(self, date: datetime, 
                                days_ahead: int = 30) -> List[str]:
        """Get festivals coming up in next N days."""
        year_day = (date - datetime(date.year, 1, 1)).days + 1
        upcoming = []
        
        for festival, day in self.festivals.items():
            days_until = day - year_day
            if days_until < 0:
                days_until += 365
            
            if days_until <= days_ahead:
                upcoming.append({
                    "festival": festival.value,
                    "days_until": days_until
                })
        
        return sorted(upcoming, key=lambda x: x["days_until"])
    
    def get_ritual_window(self, date: datetime = None) -> Dict[str, Any]:
        """
        Get current ritual/operational window.
        
        Indicates optimal times for various operations.
        """
        if date is None:
            date = datetime.now()
        
        self.update(date)
        
        firewall_state = self.firewall.current_config.state
        tree_op = self.clock.get_tree_operator()
        
        # Determine optimal operations
        operations = []
        
        if firewall_state in [FirewallState.OPEN, FirewallState.PERMEABLE]:
            operations.append("realm_transfer")
            operations.append("divination")
        
        if tree_op["function"] == "Initialization":
            operations.append("new_projects")
        elif tree_op["function"] == "Protection":
            operations.append("warding")
        elif tree_op["function"] == "Wisdom":
            operations.append("learning")
        elif tree_op["function"] == "Endings":
            operations.append("completion")
            operations.append("release")
        
        return {
            "optimal_operations": operations,
            "tree_influence": tree_op["tree"],
            "element": tree_op["element"],
            "firewall_state": firewall_state.value,
            "risk_level": self.firewall.current_config.risk_level
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_temporal() -> bool:
    """Validate temporal module."""
    
    # Test Seasonal Firewall
    firewall = SeasonalFirewall()
    
    # Test different dates
    samhain = datetime(2025, 11, 1)
    config = firewall.update_for_date(samhain)
    assert config.permeability == 1.0  # Samhain is fully open
    assert config.direction == "inbound"
    
    beltane = datetime(2025, 5, 1)
    config = firewall.update_for_date(beltane)
    assert config.permeability == 1.0  # Beltane is fully open
    assert config.direction == "outbound"
    
    # Test access check
    firewall.update_for_date(samhain)
    allowed, reason = firewall.check_access("otherworld", "physical")
    # Should mostly pass at Samhain
    
    # Test Arboreal Clock
    clock = ArborealClock()
    
    jan_15 = datetime(2025, 1, 15)
    month = clock.update(jan_15)
    assert month.tree == "Birch"  # First month
    
    jul_15 = datetime(2025, 7, 15)
    month = clock.update(jul_15)
    # Should be around Holly or Oak
    
    # Test Tree Operator
    operator = clock.get_tree_operator()
    assert "tree" in operator
    assert "function" in operator
    
    # Test Wheel of the Year
    wheel = WheelOfTheYear()
    status = wheel.update()
    assert "tree_month" in status
    assert "firewall" in status
    
    # Test ritual window
    window = wheel.get_ritual_window()
    assert "optimal_operations" in window
    
    return True


if __name__ == "__main__":
    print("Validating Temporal Module...")
    assert validate_temporal()
    print("✓ Temporal Module validated")
    
    # Demo
    print("\n--- Wheel of the Year Demo ---")
    wheel = WheelOfTheYear()
    
    # Current status
    status = wheel.update()
    print(f"\nCurrent Status:")
    print(f"  Tree Month: {status['tree_month']}")
    print(f"  Phase: {status['phase']}")
    print(f"  Firewall: {status['firewall']['state']} ({status['firewall']['permeability']})")
    
    # Tree operator
    op = status['tree_operator']
    print(f"\nTree Operator:")
    print(f"  Tree: {op['tree']} ({op['ogham']})")
    print(f"  Element: {op['element']}")
    print(f"  Function: {op['function']}")
    
    # Upcoming festivals
    print(f"\nUpcoming Festivals:")
    for fest in status['upcoming_festivals'][:3]:
        print(f"  {fest['festival']}: {fest['days_until']} days")
    
    # Ritual window
    window = wheel.get_ritual_window()
    print(f"\nRitual Window:")
    print(f"  Optimal Operations: {window['optimal_operations']}")
    print(f"  Risk Level: {window['risk_level']:.0%}")
