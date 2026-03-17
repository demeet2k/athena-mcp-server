from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import math
import numpy as np

from .orbits import OrbitalElements

@dataclass(frozen=True)
class PlanetNineTheta:
    """
    Domain parameter record (ThetaRec) for Planet Nine inference.

    theta_dyn: orbital elements (a,e,i,Omega,omega,M)
    theta_phys: mass, albedo, bulk density (used for brightness constraints)
    """
    elements: OrbitalElements
    mass_earth: float = 5.0
    albedo: float = 0.2
    density_g_cm3: float = 2.0

    def to_record(self) -> Dict[str, Any]:
        e = self.elements
        return {
            "elements": {
                "a_au": e.a_au,
                "e": e.e,
                "i_deg": e.i_deg,
                "Omega_deg": e.Omega_deg,
                "omega_deg": e.omega_deg,
                "M_deg": e.M_deg,
            },
            "mass_earth": self.mass_earth,
            "albedo": self.albedo,
            "density_g_cm3": self.density_g_cm3,
        }

    def radius_km(self) -> float:
        """
        Crude mass->radius mapping using constant bulk density.

        R = (3M / 4πρ)^(1/3)
        - M in kg
        - ρ in kg/m^3
        """
        M_EARTH_KG = 5.9722e24
        mass_kg = self.mass_earth * M_EARTH_KG
        rho = self.density_g_cm3 * 1000.0  # g/cm^3 -> kg/m^3
        R_m = (3.0 * mass_kg / (4.0 * math.pi * rho)) ** (1.0 / 3.0)
        return R_m / 1000.0

    def absolute_magnitude_H(self) -> float:
        """
        Approximate H from diameter and albedo:
            D(km) = 1329 / sqrt(p) * 10^{-H/5}
        => H = 5 log10(1329/(D*sqrt(p)))
        """
        p = max(1e-6, float(self.albedo))
        D_km = 2.0 * self.radius_km()
        return 5.0 * math.log10(1329.0 / (D_km * math.sqrt(p)))
