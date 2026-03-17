from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import math
import numpy as np

from .constants import DEFAULT_OPTICAL_MLIM, DEFAULT_SKY_COVERAGE_FRACTION, GIANT_PLANETS
from .orbits import ang_diff_deg, mean_angle_deg, pole_unit_vector, pole_to_i_Omega_deg, wrap_angle_deg
from .theta import PlanetNineTheta
from .tno_data import TNO


def _von_mises_logpdf(angle_rad: float, mu_rad: float, kappa: float) -> float:
    """
    Log of von Mises density on the circle:
        f(x) = exp(kappa cos(x-mu)) / (2π I0(kappa))
    """
    # For numerical stability, use approximation for log(I0) if needed.
    # Here kappa is modest, so numpy's i0 is fine.
    return (kappa * math.cos(angle_rad - mu_rad)) - math.log(2.0 * math.pi) - math.log(float(np.i0(kappa)))

def von_mises_loglik_deg(angles_deg: np.ndarray, mu_deg: float, kappa: float) -> float:
    mu_rad = math.radians(mu_deg)
    ang_rad = np.deg2rad(angles_deg.astype(float))
    return float(sum(_von_mises_logpdf(float(a), mu_rad, kappa) for a in ang_rad))


@dataclass(frozen=True)
class LensReport:
    lens_id: str
    log_score: float
    details: Dict[str, float]


class PerihelionClusteringLens:
    """
    Likelihood model for extreme-TNO perihelion clustering.

    Simplification: assumes TNO longitudes of perihelion (varpi = Omega+omega)
    are drawn from a von Mises distribution centered at (varpi9 + 180°), i.e.
    anti-aligned with Planet Nine's perihelion direction.

    This is a *proxy* for the much richer dynamical story, but it gives a
    concrete, data-driven constraint.
    """

    def __init__(self, tnos: List[TNO], kappa: float = 4.0) -> None:
        self.tnos = list(tnos)
        self.kappa = float(kappa)
        self.varpi_deg = np.array([t.elements.perihelion_longitude_deg() for t in self.tnos], dtype=float)
        self.mean_varpi = mean_angle_deg(self.varpi_deg)

    def score(self, theta: PlanetNineTheta) -> LensReport:
        varpi9 = theta.elements.perihelion_longitude_deg()
        mu = wrap_angle_deg(varpi9 + 180.0)
        ll = von_mises_loglik_deg(self.varpi_deg, mu_deg=mu, kappa=self.kappa)
        return LensReport(
            lens_id="perihelion_clustering",
            log_score=float(ll),
            details={
                "kappa": self.kappa,
                "tno_mean_varpi_deg": float(self.mean_varpi),
                "theta_varpi9_deg": float(varpi9),
                "model_mu_deg": float(mu),
            },
        )


class PoleAlignmentLens:
    """
    Proxy constraint from orbital-pole clustering.

    We compute a mean pole direction from the TNO sample, then encourage
    Planet Nine's orbital pole to be within some angular distance.
    """

    def __init__(self, tnos: List[TNO], sigma_deg: float = 20.0) -> None:
        self.tnos = list(tnos)
        self.sigma_deg = float(sigma_deg)

        poles = np.array([pole_unit_vector(t.elements.i_deg, t.elements.Omega_deg) for t in self.tnos], dtype=float)
        mean = poles.mean(axis=0)
        norm = float(np.linalg.norm(mean))
        self.mean_pole = mean / norm if norm > 0 else np.array([0.0, 0.0, 1.0], dtype=float)
        self.mean_i_deg, self.mean_Omega_deg = pole_to_i_Omega_deg(self.mean_pole)

    @staticmethod
    def _angle_between(u: np.ndarray, v: np.ndarray) -> float:
        dot = float(np.dot(u, v))
        dot = max(-1.0, min(1.0, dot))
        return math.degrees(math.acos(dot))

    def score(self, theta: PlanetNineTheta) -> LensReport:
        pole9 = pole_unit_vector(theta.elements.i_deg, theta.elements.Omega_deg)
        ang = self._angle_between(self.mean_pole, pole9)

        # Gaussian penalty in angle
        ll = -0.5 * (ang / self.sigma_deg) ** 2 - math.log(self.sigma_deg * math.sqrt(2.0 * math.pi))
        return LensReport(
            lens_id="pole_alignment",
            log_score=float(ll),
            details={
                "tno_mean_i_deg": float(self.mean_i_deg),
                "tno_mean_Omega_deg": float(self.mean_Omega_deg),
                "pole_angle_deg": float(ang),
                "sigma_deg": float(self.sigma_deg),
            },
        )


class PrecessionDominanceLens:
    """
    Secular precession-rate proxy.

    We compute a quadrupole-order perihelion precession rate for each TNO due to:
      - inner giant planets (J,S,U,N)
      - Planet Nine (as an outer perturber)

    Then we reward candidates where Planet Nine's precession contribution is
    comparable to or dominates the inner-planet contribution for the TNO sample.
    """

    def __init__(self, tnos: List[TNO], ratio_target: float = 1.0, sigma_log: float = 0.6) -> None:
        self.tnos = list(tnos)
        self.ratio_target = float(ratio_target)
        self.sigma_log = float(sigma_log)

    @staticmethod
    def _mean_motion(a_au: float) -> float:
        # In AU,yr,Msun units: n = sqrt(mu/a^3), mu = 4π^2
        return math.sqrt(39.47841760435743 / (a_au ** 3))

    @staticmethod
    def _g_inner(a_tno: float) -> float:
        """
        Sum of inner-planet contributions using a simple (3/4) n (m/M) (a_p/a)^3 formula.
        """
        n = PrecessionDominanceLens._mean_motion(a_tno)
        g = 0.0
        for p in GIANT_PLANETS.values():
            if p.a_au < a_tno:
                g += (3.0 / 4.0) * n * p.mass_solar * (p.a_au / a_tno) ** 3
        return g

    @staticmethod
    def _g_outer(a_tno: float, a_p9: float, e_p9: float, m_p9_solar: float) -> float:
        """
        Outer-perturber quadrupole approximation:
          g ≈ (3/4) n (m_p/M) (a/a_p)^3 / (1-e_p^2)^{3/2}
        """
        if a_p9 <= a_tno:
            return 0.0
        n = PrecessionDominanceLens._mean_motion(a_tno)
        denom = (1.0 - e_p9 * e_p9) ** 1.5
        return (3.0 / 4.0) * n * m_p9_solar * (a_tno / a_p9) ** 3 / max(1e-8, denom)

    def score(self, theta: PlanetNineTheta) -> LensReport:
        # Convert mass to solar masses
        M_EARTH_KG = 5.9722e24
        M_SUN_KG = 1.98847e30
        m_solar = theta.mass_earth * M_EARTH_KG / M_SUN_KG

        ratios: List[float] = []
        for t in self.tnos:
            g_in = self._g_inner(t.elements.a_au)
            g_out = self._g_outer(t.elements.a_au, theta.elements.a_au, theta.elements.e, m_solar)
            ratio = g_out / (g_in + 1e-30)
            ratios.append(ratio)

        ratios = np.array(ratios, dtype=float)
        # Work in log space; reward around log(ratio_target)
        log_r = np.log(np.clip(ratios, 1e-12, 1e12))
        mu = math.log(max(1e-12, self.ratio_target))
        ll = float(np.sum(-0.5 * ((log_r - mu) / self.sigma_log) ** 2 - math.log(self.sigma_log * math.sqrt(2.0 * math.pi))))
        return LensReport(
            lens_id="precession_dominance",
            log_score=ll,
            details={
                "ratio_target": self.ratio_target,
                "sigma_log": self.sigma_log,
                "ratio_median": float(np.median(ratios)),
                "ratio_min": float(np.min(ratios)),
                "ratio_max": float(np.max(ratios)),
            },
        )


class DetectabilityLens:
    """
    Very coarse "non-detection" lens.

    Compute an apparent magnitude proxy:
        m ~ H + 10 log10(r_AU)
    where we approximate r≈Δ and phase effects negligible at large r.

    If m is *bright* compared to a survey depth, penalize unless we assume the
    object fell into an unsearched fraction of the sky.

    This is a placeholder for real survey modeling.
    """

    def __init__(
        self,
        mlim: float = DEFAULT_OPTICAL_MLIM,
        sky_coverage_fraction: float = DEFAULT_SKY_COVERAGE_FRACTION,
        width_mag: float = 0.6,
        earth_lon_deg: float = 0.0,
    ) -> None:
        self.mlim = float(mlim)
        self.sky_cov = float(sky_coverage_fraction)
        self.width_mag = float(width_mag)
        self.earth_lon_deg = float(earth_lon_deg)

    def score(self, theta: PlanetNineTheta) -> LensReport:
        H = theta.absolute_magnitude_H()
        r_vec = theta.elements.position_vector()
        r_au = float(np.linalg.norm(r_vec))

        # Approximate geocentric distance using a circular 1 AU Earth orbit in the ecliptic.
        # For r >> 1 AU this is a small correction, but it gives the right form:
        #   m = H + 5 log10(r * Δ)
        lam = math.radians(self.earth_lon_deg)
        r_earth = np.array([math.cos(lam), math.sin(lam), 0.0], dtype=float)
        delta_au = float(np.linalg.norm(r_vec - r_earth))
        m = H + 5.0 * math.log10(max(1e-12, r_au * delta_au))

        # Smooth detection efficiency curve (logistic) rather than a hard threshold.
        # eff ~ 1 when bright, ~ 0 when faint.
        w = max(0.05, abs(self.width_mag))
        eff = 1.0 / (1.0 + math.exp((m - self.mlim) / w))
        eff = max(0.0, min(1.0, eff))

        # Covered fraction of sky times efficiency.
        p_detect = max(0.0, min(1.0, self.sky_cov * eff))
        p_not = max(1e-12, 1.0 - p_detect)
        ll = float(math.log(p_not))
        return LensReport(
            lens_id="detectability",
            log_score=float(ll),
            details={
                "H": float(H),
                "r_au": float(r_au),
                "delta_au": float(delta_au),
                "m_est": float(m),
                "mlim": float(self.mlim),
                "sky_cov": float(self.sky_cov),
                "width_mag": float(self.width_mag),
                "earth_lon_deg": float(self.earth_lon_deg),
                "p_not_detected": float(p_not),
            },
        )


class OrbitPlausibilityLens:
    """
    Hard-ish constraints encoded as a log-score.

    This does not try to be a full dynamical stability check; it just enforces
    broad plausibility cuts so the sampler doesn't waste all of its budget.
    """

    def __init__(self,
                 q_min_au: float = 150.0,
                 q_max_au: float = 600.0,
                 a_min_au: float = 200.0,
                 a_max_au: float = 2000.0,
                 i_max_deg: float = 80.0) -> None:
        self.q_min = float(q_min_au)
        self.q_max = float(q_max_au)
        self.a_min = float(a_min_au)
        self.a_max = float(a_max_au)
        self.i_max = float(i_max_deg)

    def score(self, theta: PlanetNineTheta) -> LensReport:
        e = theta.elements
        q = e.perihelion_distance_au()
        a = e.a_au
        i = e.i_deg

        ok = (self.a_min <= a <= self.a_max) and (self.q_min <= q <= self.q_max) and (0.0 <= i <= self.i_max) and (0.0 <= e.e < 1.0)
        ll = 0.0 if ok else -1e6  # effectively reject

        return LensReport(
            lens_id="orbit_plausibility",
            log_score=float(ll),
            details={
                "q_au": float(q),
                "a_au": float(a),
                "i_deg": float(i),
                "ok": 1.0 if ok else 0.0,
            },
        )
