from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import math
import numpy as np

from .constants import OBLIQUITY_DEG, MU_SUN_AU3_YR2

def wrap_angle_rad(x: float) -> float:
    """Wrap to [0, 2pi)."""
    twopi = 2.0 * math.pi
    x = x % twopi
    if x < 0:
        x += twopi
    return x

def wrap_angle_deg(x: float) -> float:
    return math.degrees(wrap_angle_rad(math.radians(x)))

def mean_angle_deg(deg_values: np.ndarray) -> float:
    """Circular mean of angles in degrees. Returns value in [0, 360)."""
    ang = np.deg2rad(deg_values.astype(float))
    c = np.cos(ang).mean()
    s = np.sin(ang).mean()
    return wrap_angle_deg(math.degrees(math.atan2(s, c)))

def ang_diff_deg(a: float, b: float) -> float:
    """Smallest signed difference a-b in degrees in (-180, 180]."""
    d = (a - b + 180.0) % 360.0 - 180.0
    return d

def rot_z(angle_rad: float) -> np.ndarray:
    c = math.cos(angle_rad); s = math.sin(angle_rad)
    return np.array([[c, -s, 0.0],
                     [s,  c, 0.0],
                     [0.0,0.0,1.0]], dtype=float)

def rot_x(angle_rad: float) -> np.ndarray:
    c = math.cos(angle_rad); s = math.sin(angle_rad)
    return np.array([[1.0,0.0,0.0],
                     [0.0, c,-s],
                     [0.0, s, c]], dtype=float)

def solve_kepler_E(M: float, e: float, tol: float = 1e-12, max_iter: int = 50) -> float:
    """
    Solve Kepler's equation for eccentric anomaly E (radians):
        E - e*sin(E) = M, for 0<=e<1.
    """
    M = wrap_angle_rad(M)
    if e < 0.8:
        E = M
    else:
        # Good starter near pi for high e
        E = math.pi

    for _ in range(max_iter):
        f = E - e * math.sin(E) - M
        fp = 1.0 - e * math.cos(E)
        dE = -f / fp
        E = E + dE
        if abs(dE) < tol:
            break
    return wrap_angle_rad(E)

@dataclass(frozen=True)
class OrbitalElements:
    """
    Keplerian elements, heliocentric, referred to the ecliptic plane.

    a_au: semimajor axis [AU]
    e: eccentricity [0,1)
    i_deg: inclination [deg]
    Omega_deg: longitude of ascending node [deg]
    omega_deg: argument of perihelion [deg]
    M_deg: mean anomaly at epoch [deg]
    """
    a_au: float
    e: float
    i_deg: float
    Omega_deg: float
    omega_deg: float
    M_deg: float = 0.0

    def perihelion_longitude_deg(self) -> float:
        return wrap_angle_deg(self.Omega_deg + self.omega_deg)

    def perihelion_distance_au(self) -> float:
        return self.a_au * (1.0 - self.e)

    def aphelion_distance_au(self) -> float:
        return self.a_au * (1.0 + self.e)

    def to_state_vectors(self, mu: float = MU_SUN_AU3_YR2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert to heliocentric position/velocity vectors in AU and AU/yr.
        """
        a = float(self.a_au); e = float(self.e)
        i = math.radians(float(self.i_deg))
        Om = math.radians(float(self.Omega_deg))
        om = math.radians(float(self.omega_deg))
        M = math.radians(float(self.M_deg))

        E = solve_kepler_E(M, e)
        cosE = math.cos(E); sinE = math.sin(E)
        r = a * (1.0 - e * cosE)

        # Perifocal frame
        x_p = a * (cosE - e)
        y_p = a * math.sqrt(1.0 - e*e) * sinE
        r_p = np.array([x_p, y_p, 0.0], dtype=float)

        # Velocity in perifocal (AU/yr)
        # dE/dt = n / (1 - e*cosE), with n = sqrt(mu/a^3)
        n = math.sqrt(mu / (a**3))
        dE_dt = n / (1.0 - e*cosE)
        vx_p = -a * sinE * dE_dt
        vy_p =  a * math.sqrt(1.0 - e*e) * cosE * dE_dt
        v_p = np.array([vx_p, vy_p, 0.0], dtype=float)

        # Rotation to ecliptic: Rz(Omega) * Rx(i) * Rz(omega)
        R = rot_z(Om) @ rot_x(i) @ rot_z(om)
        r_vec = R @ r_p
        v_vec = R @ v_p
        return r_vec, v_vec

    def position_vector(self) -> np.ndarray:
        r, _ = self.to_state_vectors()
        return r

def ecliptic_to_radec_deg(r_ecl: np.ndarray) -> Tuple[float, float]:
    """
    Convert heliocentric ecliptic xyz vector to equatorial RA/Dec (degrees).
    (Assumes Earth at origin; for distant objects the parallax error is small.)
    """
    eps = math.radians(OBLIQUITY_DEG)
    x, y, z = float(r_ecl[0]), float(r_ecl[1]), float(r_ecl[2])

    xeq = x
    yeq = y * math.cos(eps) - z * math.sin(eps)
    zeq = y * math.sin(eps) + z * math.cos(eps)

    r = math.sqrt(xeq*xeq + yeq*yeq + zeq*zeq)
    ra = math.degrees(math.atan2(yeq, xeq)) % 360.0
    dec = math.degrees(math.asin(zeq / r))
    return ra, dec

def xyz_to_lonlat_deg(r_ecl: np.ndarray) -> Tuple[float, float]:
    x, y, z = float(r_ecl[0]), float(r_ecl[1]), float(r_ecl[2])
    r = math.sqrt(x*x + y*y + z*z)
    lon = math.degrees(math.atan2(y, x)) % 360.0
    lat = math.degrees(math.asin(z / r))
    return lon, lat

def pole_unit_vector(i_deg: float, Omega_deg: float) -> np.ndarray:
    """
    Angular momentum unit vector ("orbital pole") in ecliptic coordinates.
    Convention:
      h_x = sin(i) * sin(Omega)
      h_y = -sin(i) * cos(Omega)
      h_z = cos(i)
    """
    i = math.radians(float(i_deg))
    Om = math.radians(float(Omega_deg))
    return np.array([
        math.sin(i) * math.sin(Om),
        -math.sin(i) * math.cos(Om),
        math.cos(i),
    ], dtype=float)

def pole_to_i_Omega_deg(h: np.ndarray) -> Tuple[float, float]:
    """
    Invert pole_unit_vector approximately.
    Returns (i_deg, Omega_deg) with Omega in [0,360).
    """
    hx, hy, hz = float(h[0]), float(h[1]), float(h[2])
    # ensure unit
    norm = math.sqrt(hx*hx + hy*hy + hz*hz)
    if norm == 0:
        return 0.0, 0.0
    hx, hy, hz = hx/norm, hy/norm, hz/norm
    i = math.degrees(math.acos(max(-1.0, min(1.0, hz))))
    Omega = math.degrees(math.atan2(hx, -hy)) % 360.0
    return i, Omega
