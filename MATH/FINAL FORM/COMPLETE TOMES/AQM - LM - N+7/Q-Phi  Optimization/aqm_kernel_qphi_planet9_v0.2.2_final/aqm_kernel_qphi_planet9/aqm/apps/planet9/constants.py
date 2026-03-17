from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# -----------------------------
# Physical constants (approx.)
# -----------------------------

AU_M: float = 149_597_870_700.0           # meters
G_SI: float = 6.67430e-11                # m^3 kg^-1 s^-2
DAY_S: float = 86_400.0                  # seconds

M_SUN_KG: float = 1.98847e30
M_EARTH_KG: float = 5.9722e24

# In canonical astronomical units (AU, year, solar mass): mu_sun = 4*pi^2 AU^3/yr^2.
MU_SUN_AU3_YR2: float = 39.47841760435743  # 4*pi^2

OBLIQUITY_DEG: float = 23.439281  # mean obliquity ~ J2000

# -----------------------------
# Giant planet data (approx.)
# -----------------------------

@dataclass(frozen=True)
class Planet:
    name: str
    mass_solar: float
    a_au: float  # semimajor axis (AU), used in secular precession approximations

GIANT_PLANETS: Dict[str, Planet] = {
    # Masses: kg / M_sun. a_au are mean semimajor axes.
    "Jupiter": Planet("Jupiter", 1.89813e27 / M_SUN_KG, 5.2044),
    "Saturn":  Planet("Saturn",  5.68340e26 / M_SUN_KG, 9.5826),
    "Uranus":  Planet("Uranus",  8.68100e25 / M_SUN_KG, 19.2184),
    "Neptune": Planet("Neptune", 1.02413e26 / M_SUN_KG, 30.1104),
}

# -----------------------------
# "Survey" defaults (very rough)
# -----------------------------
# These are deliberately coarse; for a serious search you should use a real survey
# footprint + depth model per field.
DEFAULT_OPTICAL_MLIM: float = 22.0  # typical wide-field survey depth in V-like band
DEFAULT_SKY_COVERAGE_FRACTION: float = 0.35  # fraction of sky covered to that depth (crude)
