"""
ATHENA OS - QUMRAN KERNEL: TIME KERNEL MODULE
==============================================
364-Day Sabbatarian Calendar and Priestly Courses

THE TIME KERNEL (K_T):
    K_T = (Z_364, Q, W, F, M)
    
    where:
    - Z_364: 364-day year (52 complete weeks)
    - Q: Quarter structure (seasons, tekufot)
    - W: Weekly structure with Sabbaths as special nodes
    - F: Fixed festival schedule pinned to invariant weekdays
    - M: Mishmarot cycle of 24 priestly families

CALENDAR STRUCTURE:
    - 364 days = 52 weeks (exactly divisible by 7)
    - 4 quarters of 91 days (13 weeks each)
    - 12 months: 30-30-31 pattern per quarter
    - Festivals fall on SAME weekday every year
    
PRIESTLY COURSES (Mishmarot):
    24 divisions serving in rotation
    24 × 7 days × 6 years = 1008 weeks
    Full cycle synchronized with 364-day calendar

SABBATICAL CYCLES:
    - Week of years (7 years)
    - Jubilee (49 years)
    - Apocalyptic epochs (490 years = 10 jubilees)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, IntEnum
import numpy as np


# =============================================================================
# CALENDAR ENUMS
# =============================================================================

class Weekday(IntEnum):
    """Days of the week (Sunday = 1 as in ancient Hebrew)."""
    
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4      # Day of creation of luminaries
    THURSDAY = 5
    FRIDAY = 6
    SABBATH = 7        # Sacred rest day


class Quarter(IntEnum):
    """Four quarters (tekufot) of the year."""
    
    SPRING = 1         # Tekufat Nisan
    SUMMER = 2         # Tekufat Tammuz
    AUTUMN = 3         # Tekufat Tishri
    WINTER = 4         # Tekufat Tevet


class Month(IntEnum):
    """Twelve months of the Qumran calendar."""
    
    NISAN = 1
    IYYAR = 2
    SIVAN = 3
    TAMMUZ = 4
    AV = 5
    ELUL = 6
    TISHRI = 7
    MARCHESHVAN = 8
    KISLEV = 9
    TEVET = 10
    SHEVAT = 11
    ADAR = 12


# =============================================================================
# FESTIVAL DEFINITIONS
# =============================================================================

class Festival(Enum):
    """Fixed festivals of the Qumran calendar."""
    
    # Spring festivals
    PESACH = "pesach"                    # Passover (1/14)
    UNLEAVENED_BREAD = "matzot"          # 1/15-21
    WAVE_SHEAF = "omer"                  # First fruits of barley
    
    # Summer festivals
    SHAVUOT = "shavuot"                  # Pentecost (weeks)
    NEW_WINE = "new_wine"                # Festival of new wine
    NEW_OIL = "new_oil"                  # Festival of new oil
    WOOD_OFFERING = "wood_offering"      # Wood festival
    
    # Autumn festivals
    ROSH_HASHANAH = "rosh_hashanah"      # New year (7/1)
    YOM_KIPPUR = "yom_kippur"            # Day of Atonement (7/10)
    SUKKOT = "sukkot"                    # Tabernacles (7/15-21)
    SHEMINI_ATZERET = "shemini_atzeret"  # Eighth day assembly
    
    # Weekly
    SABBATH = "sabbath"                  # Every 7th day


@dataclass
class FestivalConfig:
    """Configuration for a festival."""
    
    festival: Festival
    month: int
    day: int
    duration: int = 1            # Days
    fixed_weekday: Optional[Weekday] = None
    description: str = ""


# Festival schedule (pinned to fixed weekdays in 364-day calendar)
FESTIVAL_SCHEDULE = [
    FestivalConfig(Festival.PESACH, 1, 14, 1, Weekday.TUESDAY, "Passover lamb slaughter"),
    FestivalConfig(Festival.UNLEAVENED_BREAD, 1, 15, 7, Weekday.WEDNESDAY, "Week of unleavened bread"),
    FestivalConfig(Festival.WAVE_SHEAF, 1, 26, 1, Weekday.SUNDAY, "First fruits of barley"),
    FestivalConfig(Festival.SHAVUOT, 3, 15, 1, Weekday.SUNDAY, "Pentecost - wheat harvest"),
    FestivalConfig(Festival.NEW_WINE, 5, 3, 1, Weekday.SUNDAY, "First fruits of wine"),
    FestivalConfig(Festival.NEW_OIL, 6, 22, 1, Weekday.SUNDAY, "First fruits of oil"),
    FestivalConfig(Festival.ROSH_HASHANAH, 7, 1, 1, Weekday.WEDNESDAY, "New Year"),
    FestivalConfig(Festival.YOM_KIPPUR, 7, 10, 1, Weekday.FRIDAY, "Day of Atonement"),
    FestivalConfig(Festival.SUKKOT, 7, 15, 7, Weekday.WEDNESDAY, "Feast of Tabernacles"),
    FestivalConfig(Festival.SHEMINI_ATZERET, 7, 22, 1, Weekday.WEDNESDAY, "Eighth day assembly"),
]


# =============================================================================
# PRIESTLY COURSE
# =============================================================================

@dataclass
class PriestlyCourse:
    """One of 24 priestly divisions (mishmarot)."""
    
    number: int              # 1-24
    name: str
    rotation_week: int       # Week in the 6-year cycle
    
    # Service schedule
    service_days: int = 7    # Days of service


# The 24 priestly courses (from 1 Chronicles 24)
PRIESTLY_COURSES = [
    PriestlyCourse(1, "Jehoiarib", 1),
    PriestlyCourse(2, "Jedaiah", 2),
    PriestlyCourse(3, "Harim", 3),
    PriestlyCourse(4, "Seorim", 4),
    PriestlyCourse(5, "Malchijah", 5),
    PriestlyCourse(6, "Mijamin", 6),
    PriestlyCourse(7, "Hakkoz", 7),
    PriestlyCourse(8, "Abijah", 8),
    PriestlyCourse(9, "Jeshua", 9),
    PriestlyCourse(10, "Shecaniah", 10),
    PriestlyCourse(11, "Eliashib", 11),
    PriestlyCourse(12, "Jakim", 12),
    PriestlyCourse(13, "Huppah", 13),
    PriestlyCourse(14, "Jeshebeab", 14),
    PriestlyCourse(15, "Bilgah", 15),
    PriestlyCourse(16, "Immer", 16),
    PriestlyCourse(17, "Hezir", 17),
    PriestlyCourse(18, "Happizzez", 18),
    PriestlyCourse(19, "Pethahiah", 19),
    PriestlyCourse(20, "Jehezkel", 20),
    PriestlyCourse(21, "Jachin", 21),
    PriestlyCourse(22, "Gamul", 22),
    PriestlyCourse(23, "Delaiah", 23),
    PriestlyCourse(24, "Maaziah", 24),
]


# =============================================================================
# QUMRAN DATE
# =============================================================================

@dataclass
class QumranDate:
    """
    A date in the 364-day Qumran calendar.
    
    Properties:
    - Year always begins on Wednesday (day luminaries were created)
    - 364 = 52 × 7 (perfect week alignment)
    - Festivals fall on same weekday every year
    """
    
    year: int
    month: int
    day: int
    
    def day_of_year(self) -> int:
        """Calculate day of year (1-364)."""
        # Month lengths: 30-30-31 per quarter
        month_lengths = [30, 30, 31, 30, 30, 31, 30, 30, 31, 30, 30, 31]
        
        total = 0
        for m in range(self.month - 1):
            total += month_lengths[m]
        total += self.day
        
        return total
    
    def weekday(self) -> Weekday:
        """Calculate weekday (year starts on Wednesday)."""
        doy = self.day_of_year()
        
        # Year starts on Wednesday (4)
        # Day 1 = Wednesday, Day 2 = Thursday, ...
        weekday_num = ((doy - 1 + 4 - 1) % 7) + 1
        return Weekday(weekday_num)
    
    def week_of_year(self) -> int:
        """Calculate week of year (1-52)."""
        return (self.day_of_year() - 1) // 7 + 1
    
    def quarter(self) -> Quarter:
        """Get quarter (season)."""
        if self.month <= 3:
            return Quarter.SPRING
        elif self.month <= 6:
            return Quarter.SUMMER
        elif self.month <= 9:
            return Quarter.AUTUMN
        else:
            return Quarter.WINTER
    
    def is_sabbath(self) -> bool:
        """Check if this date is a Sabbath."""
        return self.weekday() == Weekday.SABBATH
    
    def __str__(self) -> str:
        return f"{self.year}/{self.month}/{self.day}"


# =============================================================================
# TIME KERNEL
# =============================================================================

class TimeKernel:
    """
    The Qumran Time Kernel (K_T).
    
    K_T = (Z_364, Q, W, F, M)
    
    A complete calendrical lattice with:
    - 364-day year (52 perfect weeks)
    - Quarterly structure (tekufot)
    - Sabbath cycle
    - Fixed festivals
    - Priestly course rotation (mishmarot)
    """
    
    # Constants
    DAYS_PER_YEAR = 364
    WEEKS_PER_YEAR = 52
    DAYS_PER_WEEK = 7
    MONTHS_PER_YEAR = 12
    QUARTERS_PER_YEAR = 4
    
    # Sabbatical cycles
    YEARS_PER_SABBATICAL = 7
    SABBATICALS_PER_JUBILEE = 7
    YEARS_PER_JUBILEE = 49
    JUBILEES_PER_EPOCH = 10
    YEARS_PER_EPOCH = 490
    
    def __init__(self):
        self.courses = PRIESTLY_COURSES
        self.festivals = FESTIVAL_SCHEDULE
        
        # Month lengths
        self.month_lengths = [30, 30, 31, 30, 30, 31, 30, 30, 31, 30, 30, 31]
    
    def create_date(self, year: int, month: int, day: int) -> QumranDate:
        """Create a Qumran date with validation."""
        if month < 1 or month > 12:
            raise ValueError(f"Month must be 1-12, got {month}")
        
        max_day = self.month_lengths[month - 1]
        if day < 1 or day > max_day:
            raise ValueError(f"Day must be 1-{max_day} for month {month}, got {day}")
        
        return QumranDate(year, month, day)
    
    def get_priestly_course(self, date: QumranDate) -> PriestlyCourse:
        """
        Get the priestly course serving on a given date.
        
        24 courses rotate through 6-year cycle (1008 weeks).
        """
        # Calculate absolute week number in 6-year cycle
        year_in_cycle = (date.year - 1) % 6
        week_in_year = date.week_of_year()
        
        absolute_week = year_in_cycle * 52 + week_in_year
        
        # Map to course (24 courses, rotating)
        course_index = (absolute_week - 1) % 24
        return self.courses[course_index]
    
    def get_festivals_on_date(self, date: QumranDate) -> List[FestivalConfig]:
        """Get festivals occurring on a date."""
        result = []
        
        for fest in self.festivals:
            if fest.month == date.month:
                if fest.day <= date.day < fest.day + fest.duration:
                    result.append(fest)
        
        # Check Sabbath
        if date.is_sabbath():
            result.append(FestivalConfig(
                Festival.SABBATH, date.month, date.day, 1,
                Weekday.SABBATH, "Weekly Sabbath rest"
            ))
        
        return result
    
    def get_sabbatical_year(self, year: int) -> int:
        """Get position in 7-year sabbatical cycle (1-7)."""
        return ((year - 1) % self.YEARS_PER_SABBATICAL) + 1
    
    def is_sabbatical_year(self, year: int) -> bool:
        """Check if year is a sabbatical (7th) year."""
        return self.get_sabbatical_year(year) == 7
    
    def get_jubilee_year(self, year: int) -> int:
        """Get position in 49-year jubilee cycle (1-49)."""
        return ((year - 1) % self.YEARS_PER_JUBILEE) + 1
    
    def is_jubilee_year(self, year: int) -> bool:
        """Check if year is a jubilee (50th, but counted as 49th)."""
        return self.get_jubilee_year(year) == self.YEARS_PER_JUBILEE
    
    def get_epoch_year(self, year: int) -> int:
        """Get position in 490-year apocalyptic epoch (1-490)."""
        return ((year - 1) % self.YEARS_PER_EPOCH) + 1
    
    def calculate_days_between(self, d1: QumranDate, d2: QumranDate) -> int:
        """Calculate days between two dates."""
        days1 = (d1.year - 1) * self.DAYS_PER_YEAR + d1.day_of_year()
        days2 = (d2.year - 1) * self.DAYS_PER_YEAR + d2.day_of_year()
        return days2 - days1
    
    def add_days(self, date: QumranDate, days: int) -> QumranDate:
        """Add days to a date."""
        total_days = (date.year - 1) * self.DAYS_PER_YEAR + date.day_of_year() + days
        
        if total_days < 1:
            raise ValueError("Result date before year 1")
        
        new_year = (total_days - 1) // self.DAYS_PER_YEAR + 1
        day_in_year = (total_days - 1) % self.DAYS_PER_YEAR + 1
        
        # Convert day of year to month/day
        new_month = 1
        remaining = day_in_year
        
        for length in self.month_lengths:
            if remaining <= length:
                new_day = remaining
                break
            remaining -= length
            new_month += 1
        else:
            new_day = remaining
        
        return QumranDate(new_year, new_month, new_day)
    
    def get_calendar_summary(self, year: int) -> Dict[str, Any]:
        """Get summary of a calendar year."""
        return {
            "year": year,
            "days": self.DAYS_PER_YEAR,
            "weeks": self.WEEKS_PER_YEAR,
            "first_day_weekday": "Wednesday",
            "sabbatical_position": self.get_sabbatical_year(year),
            "is_sabbatical": self.is_sabbatical_year(year),
            "jubilee_position": self.get_jubilee_year(year),
            "is_jubilee": self.is_jubilee_year(year),
            "epoch_position": self.get_epoch_year(year)
        }


# =============================================================================
# SABBATARIAN LATTICE
# =============================================================================

class SabbatarianLattice:
    """
    The complete Sabbatarian time lattice.
    
    Nested cycles:
    - Day (1)
    - Week (7 days)
    - Month (30-31 days)
    - Quarter (91 days = 13 weeks)
    - Year (364 days = 52 weeks)
    - Sabbatical (7 years)
    - Jubilee (49 years = 7 sabbaticals)
    - Epoch (490 years = 10 jubilees)
    """
    
    def __init__(self):
        self.kernel = TimeKernel()
    
    def get_position_in_cycles(self, year: int, 
                                day_of_year: int = 1) -> Dict[str, int]:
        """Get position in all nested cycles."""
        return {
            "day_of_week": ((day_of_year - 1 + 3) % 7) + 1,  # Wed = 4 start
            "week_of_year": (day_of_year - 1) // 7 + 1,
            "day_of_year": day_of_year,
            "year": year,
            "year_in_sabbatical": self.kernel.get_sabbatical_year(year),
            "year_in_jubilee": self.kernel.get_jubilee_year(year),
            "year_in_epoch": self.kernel.get_epoch_year(year),
            "sabbatical_number": (year - 1) // 7 + 1,
            "jubilee_number": (year - 1) // 49 + 1,
            "epoch_number": (year - 1) // 490 + 1
        }
    
    def is_sacred_time(self, date: QumranDate) -> Dict[str, bool]:
        """Check various sacred time conditions."""
        return {
            "is_sabbath": date.is_sabbath(),
            "is_new_moon": date.day == 1,
            "is_quarter_start": date.month in [1, 4, 7, 10] and date.day == 1,
            "is_sabbatical_year": self.kernel.is_sabbatical_year(date.year),
            "is_jubilee_year": self.kernel.is_jubilee_year(date.year)
        }
    
    def get_year_map(self, year: int) -> Dict[str, Any]:
        """Generate complete map of a year's sacred times."""
        festivals = {}
        sabbaths = []
        
        # Iterate through year
        for doy in range(1, 365):
            date = self.kernel.add_days(
                QumranDate(year, 1, 1), 
                doy - 1
            )
            
            if date.is_sabbath():
                sabbaths.append(str(date))
            
            fests = self.kernel.get_festivals_on_date(date)
            for f in fests:
                if f.festival != Festival.SABBATH:
                    if f.festival.value not in festivals:
                        festivals[f.festival.value] = str(date)
        
        return {
            "year": year,
            "sabbath_count": len(sabbaths),
            "festivals": festivals,
            "summary": self.kernel.get_calendar_summary(year)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_time_kernel() -> bool:
    """Validate time kernel module."""
    
    # Test calendar basics
    kernel = TimeKernel()
    
    # Test date creation
    date = kernel.create_date(1, 1, 1)
    assert date.weekday() == Weekday.WEDNESDAY  # Year starts Wednesday
    assert date.day_of_year() == 1
    
    # Test year structure
    assert sum(kernel.month_lengths) == 364
    assert len(kernel.month_lengths) == 12
    
    # Test Sabbath detection
    sabbath = kernel.create_date(1, 1, 4)  # Day 4 = Sabbath
    assert sabbath.weekday() == Weekday.SABBATH
    assert sabbath.is_sabbath()
    
    # Test priestly courses
    for i, course in enumerate(PRIESTLY_COURSES):
        assert course.number == i + 1
    assert len(PRIESTLY_COURSES) == 24
    
    # Test sabbatical cycles
    assert kernel.is_sabbatical_year(7)
    assert not kernel.is_sabbatical_year(6)
    assert kernel.is_jubilee_year(49)
    
    # Test date arithmetic
    d1 = kernel.create_date(1, 1, 1)
    d2 = kernel.add_days(d1, 7)
    assert d2.day == 8
    assert kernel.calculate_days_between(d1, d2) == 7
    
    # Test lattice
    lattice = SabbatarianLattice()
    pos = lattice.get_position_in_cycles(49, 1)
    assert pos["year_in_jubilee"] == 49
    
    return True


if __name__ == "__main__":
    print("Validating Time Kernel Module...")
    assert validate_time_kernel()
    print("✓ Time Kernel Module validated")
    
    # Demo
    print("\n--- 364-Day Calendar Demo ---")
    kernel = TimeKernel()
    
    # Create a date
    date = kernel.create_date(1, 1, 1)
    print(f"Year 1, Month 1, Day 1:")
    print(f"  Weekday: {date.weekday().name}")
    print(f"  Day of Year: {date.day_of_year()}")
    print(f"  Week: {date.week_of_year()}")
    
    # Priestly course
    course = kernel.get_priestly_course(date)
    print(f"  Serving Course: {course.name}")
    
    # Year summary
    print("\n--- Year 7 (Sabbatical) Summary ---")
    summary = kernel.get_calendar_summary(7)
    for k, v in summary.items():
        print(f"  {k}: {v}")
    
    print("\n--- Festivals ---")
    for fest in FESTIVAL_SCHEDULE[:5]:
        print(f"  {fest.festival.value}: {fest.month}/{fest.day} ({fest.description})")
