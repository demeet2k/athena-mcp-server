from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import csv
import hashlib
import importlib.metadata
import json
import math
import time

import numpy as np

from .jpl_sbdb import fetch_extreme_tnos_from_jpl
from .lenses import (
    DetectabilityLens,
    LensReport,
    OrbitPlausibilityLens,
    PerihelionClusteringLens,
    PoleAlignmentLens,
    PrecessionDominanceLens,
)
from .orbits import (
    OrbitalElements,
    ecliptic_to_radec_deg,
    mean_angle_deg,
    pole_to_i_Omega_deg,
    pole_unit_vector,
    wrap_angle_deg,
    xyz_to_lonlat_deg,
)
from .theta import PlanetNineTheta
from .tno_data import TNO, demo_extreme_tnos, load_tno_csv, select_extreme, tno_set_digest

# Optional integration with the AQM kernel artifacts.
try:
    from aqm.ledger import Ledger
    from aqm.certs import CertificateBundle
    from aqm.kernel import Tile
    from aqm.addressing import TileAddress
    from aqm.store import MerkleStore
except Exception:  # pragma: no cover
    Ledger = None  # type: ignore
    CertificateBundle = None  # type: ignore
    Tile = None  # type: ignore
    TileAddress = None  # type: ignore
    MerkleStore = None  # type: ignore


@dataclass(frozen=True)
class QPHIConfig:
    """
    Q-PHI run configuration.

    This pack is intentionally "audit-first":
      - deterministic under a fixed seed
      - input dataset digested (SHA-256)
      - every stage logged to an AQM-style ledger
    """
    seed: int = 42

    # Sampling / refinement
    n_initial: int = 30_000
    elite_keep: int = 200
    refine_rounds: int = 2
    offspring_per_elite: int = 30

    # Priors / proposal ranges (tune these if you have stronger constraints)
    a_range_au: Tuple[float, float] = (300.0, 1200.0)
    q_range_au: Tuple[float, float] = (200.0, 500.0)  # perihelion distance
    i_range_deg: Tuple[float, float] = (0.0, 60.0)
    mass_range_earth: Tuple[float, float] = (3.0, 15.0)
    albedo_range: Tuple[float, float] = (0.05, 0.7)
    density_range_g_cm3: Tuple[float, float] = (1.0, 3.0)

    # Proposal strategy
    # "data_guided" uses the TNO sample's mean perihelion direction + mean pole
    # to propose i/Omega/varpi9 more efficiently (still fully Bayesian once lenses apply).
    proposal_mode: str = "data_guided"  # or "broad"
    proposal_varpi_sigma_deg: float = 50.0
    proposal_i_sigma_deg: float = 12.0
    proposal_Omega_sigma_deg: float = 35.0

    # Lens hyperparameters
    kappa_perihelion: float = 4.0
    pole_sigma_deg: float = 20.0
    precession_ratio_target: float = 1.0
    precession_sigma_log: float = 0.6

    # Lens weights (can be learned in a later Q-LEARN phase)
    w_perihelion: float = 1.0
    w_pole: float = 0.6
    w_precession: float = 0.8
    w_detectability: float = 0.5
    w_plausibility: float = 1.0

    # Detectability toy model
    mlim: float = 22.0
    sky_coverage_fraction: float = 0.35
    detect_width_mag: float = 0.6
    earth_lon_deg: float = 0.0

    # Posterior softmax temperature (larger = less-peaky sky map)
    posterior_temperature: float = 8.0

    # Output
    out_dir: str = "qphi_out"
    store_dir: Optional[str] = ".aqm_store_qphi"  # Merkle store for replay artifacts (optional)

    # Input selection (extreme-TNO cut)
    tno_a_min_au: float = 250.0
    tno_q_min_au: float = 30.0

    # Refinement jitter scales
    jitter_log_a: float = 0.12
    jitter_q_au: float = 30.0
    jitter_i_deg: float = 8.0
    jitter_angle_deg: float = 25.0
    jitter_mass_log: float = 0.25
    jitter_albedo: float = 0.08
    jitter_density: float = 0.25


@dataclass(frozen=True)
class CandidateResult:
    theta: PlanetNineTheta
    log_score: float
    reports: Dict[str, LensReport]

    def to_row(self) -> Dict[str, Any]:
        e = self.theta.elements
        r_vec = e.position_vector()
        r = float(np.linalg.norm(r_vec))
        ra, dec = ecliptic_to_radec_deg(r_vec)
        lon, lat = xyz_to_lonlat_deg(r_vec)

        row: Dict[str, Any] = {
            "log_score": float(self.log_score),
            "a_au": float(e.a_au),
            "e": float(e.e),
            "i_deg": float(e.i_deg),
            "Omega_deg": float(e.Omega_deg),
            "omega_deg": float(e.omega_deg),
            "M_deg": float(e.M_deg),
            "varpi_deg": float(e.perihelion_longitude_deg()),
            "q_au": float(e.perihelion_distance_au()),
            "Q_au": float(e.aphelion_distance_au()),
            "mass_earth": float(self.theta.mass_earth),
            "albedo": float(self.theta.albedo),
            "density_g_cm3": float(self.theta.density_g_cm3),
            "radius_km": float(self.theta.radius_km()),
            "H": float(self.theta.absolute_magnitude_H()),
            "r_au": r,
            "ecl_lon_deg": float(lon),
            "ecl_lat_deg": float(lat),
            "ra_deg": float(ra),
            "dec_deg": float(dec),
        }
        for k, rep in self.reports.items():
            row[f"{k}_log"] = float(rep.log_score)
        return row


def config_digest(cfg: QPHIConfig) -> str:
    """Deterministic digest of the *model-relevant* run config.

    This is part of the 'audit-first' contract: a run is uniquely identified by
    (code version, cfg_digest, tno_digest, seed).

    Implementation note:
      We intentionally exclude fields that do not change the math of the
      inference (e.g., output directories). This keeps caching/run IDs stable
      across deployments.
    """
    d = asdict(cfg)
    # These affect *where* artifacts are written/stored, not the posterior.
    d.pop("out_dir", None)
    d.pop("store_dir", None)

    payload = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def package_version() -> str:
    """Return installed package version (best-effort)."""
    try:
        return str(importlib.metadata.version("aqm-kernel"))
    except Exception:
        return "unknown"


def _log_uniform(rng: np.random.Generator, lo: float, hi: float) -> float:
    lo = float(lo); hi = float(hi)
    x = rng.uniform(math.log(lo), math.log(hi))
    return float(math.exp(x))


def _wrap360(x: float) -> float:
    return float(x % 360.0)


def _trunc_norm(rng: np.random.Generator, mu: float, sigma: float, lo: float, hi: float, max_tries: int = 50) -> float:
    """Sample a truncated normal in [lo,hi] (deterministic fallback).

    We keep this intentionally simple (no SciPy dependency in the core loop).
    """
    mu = float(mu); sigma = max(1e-9, float(sigma))
    lo = float(lo); hi = float(hi)
    for _ in range(int(max_tries)):
        x = float(rng.normal(mu, sigma))
        if lo <= x <= hi:
            return x
    # deterministic fallback if the truncation is too tight
    return float(np.clip(mu, lo, hi))


@dataclass(frozen=True)
class ProposalHints:
    """Data-derived proposal hints.

    These do *not* change the target distribution by themselves; they're only
    used to propose candidates more efficiently during Q-SEARCH.
    """

    tno_mean_varpi_deg: float
    varpi9_mu_deg: float
    tno_mean_i_deg: float
    tno_mean_Omega_deg: float

    @staticmethod
    def from_tnos(tnos: List[TNO]) -> "ProposalHints":
        if not tnos:
            return ProposalHints(
                tno_mean_varpi_deg=0.0,
                varpi9_mu_deg=180.0,
                tno_mean_i_deg=0.0,
                tno_mean_Omega_deg=0.0,
            )

        varpi = np.array([t.elements.perihelion_longitude_deg() for t in tnos], dtype=float)
        mean_varpi = float(mean_angle_deg(varpi))
        # Per PerihelionClusteringLens: TNO varpi ~ (varpi9 + 180°)
        varpi9_mu = float(wrap_angle_deg(mean_varpi - 180.0))

        poles = np.array([pole_unit_vector(t.elements.i_deg, t.elements.Omega_deg) for t in tnos], dtype=float)
        mean_pole = poles.mean(axis=0)
        norm = float(np.linalg.norm(mean_pole))
        if norm > 0:
            mean_pole = mean_pole / norm
        i_mu, Om_mu = pole_to_i_Omega_deg(mean_pole)

        return ProposalHints(
            tno_mean_varpi_deg=mean_varpi,
            varpi9_mu_deg=float(varpi9_mu),
            tno_mean_i_deg=float(i_mu),
            tno_mean_Omega_deg=float(Om_mu),
        )


def _sample_theta(rng: np.random.Generator, cfg: QPHIConfig, hints: Optional[ProposalHints] = None) -> PlanetNineTheta:
    # a is log-uniform
    a = _log_uniform(rng, cfg.a_range_au[0], cfg.a_range_au[1])

    # q uniform, must be < a
    q_lo, q_hi = cfg.q_range_au
    q_hi_eff = min(q_hi, 0.95 * a)
    q = float(rng.uniform(q_lo, q_hi_eff))
    e = 1.0 - q / a
    e = float(np.clip(e, 0.05, 0.98))

    # angles
    if cfg.proposal_mode == "data_guided" and hints is not None:
        # Guide the *proposal* using TNO mean pole and mean perihelion direction.
        # The lenses still compute the final likelihood.
        i = _trunc_norm(rng, hints.tno_mean_i_deg, cfg.proposal_i_sigma_deg, cfg.i_range_deg[0], cfg.i_range_deg[1])
        Omega = _wrap360(hints.tno_mean_Omega_deg + rng.normal(0.0, cfg.proposal_Omega_sigma_deg))

        varpi9 = _wrap360(hints.varpi9_mu_deg + rng.normal(0.0, cfg.proposal_varpi_sigma_deg))
        omega = _wrap360(varpi9 - Omega)
    else:
        i = float(rng.uniform(cfg.i_range_deg[0], cfg.i_range_deg[1]))
        Omega = float(rng.uniform(0.0, 360.0))
        omega = float(rng.uniform(0.0, 360.0))

    # Time-uniform position along the orbit: mean anomaly ~ Uniform(0, 360)
    # (This naturally spends more time near aphelion in true-anomaly space.)
    M = float(rng.uniform(0.0, 360.0))

    # physical
    mass = _log_uniform(rng, cfg.mass_range_earth[0], cfg.mass_range_earth[1])
    albedo = float(rng.uniform(cfg.albedo_range[0], cfg.albedo_range[1]))
    density = float(rng.uniform(cfg.density_range_g_cm3[0], cfg.density_range_g_cm3[1]))

    return PlanetNineTheta(
        elements=OrbitalElements(a_au=a, e=e, i_deg=i, Omega_deg=Omega, omega_deg=omega, M_deg=M),
        mass_earth=mass,
        albedo=albedo,
        density_g_cm3=density,
    )


def _jitter_theta(rng: np.random.Generator, base: PlanetNineTheta, cfg: QPHIConfig) -> PlanetNineTheta:
    e0 = base.elements

    # log-a jitter
    a = float(e0.a_au * math.exp(rng.normal(0.0, cfg.jitter_log_a)))
    a = float(np.clip(a, cfg.a_range_au[0], cfg.a_range_au[1]))

    # jitter q directly, then recompute e
    q0 = e0.perihelion_distance_au()
    q = float(q0 + rng.normal(0.0, cfg.jitter_q_au))
    q = float(np.clip(q, cfg.q_range_au[0], min(cfg.q_range_au[1], 0.95 * a)))
    e = float(np.clip(1.0 - q / a, 0.05, 0.98))

    i = float(np.clip(e0.i_deg + rng.normal(0.0, cfg.jitter_i_deg), cfg.i_range_deg[0], cfg.i_range_deg[1]))
    Omega = _wrap360(e0.Omega_deg + rng.normal(0.0, cfg.jitter_angle_deg))
    # Jitter varpi directly (Omega+omega) to preserve the geometry of the perihelion direction.
    varpi0 = e0.perihelion_longitude_deg()
    varpi = _wrap360(varpi0 + rng.normal(0.0, cfg.jitter_angle_deg))
    omega = _wrap360(varpi - Omega)
    M = _wrap360(e0.M_deg + rng.normal(0.0, cfg.jitter_angle_deg))

    # phys: log-mass jitter, linear for albedo/density
    mass = float(base.mass_earth * math.exp(rng.normal(0.0, cfg.jitter_mass_log)))
    mass = float(np.clip(mass, cfg.mass_range_earth[0], cfg.mass_range_earth[1]))
    albedo = float(np.clip(base.albedo + rng.normal(0.0, cfg.jitter_albedo), cfg.albedo_range[0], cfg.albedo_range[1]))
    density = float(np.clip(base.density_g_cm3 + rng.normal(0.0, cfg.jitter_density), cfg.density_range_g_cm3[0], cfg.density_range_g_cm3[1]))

    return PlanetNineTheta(
        elements=OrbitalElements(a_au=a, e=e, i_deg=i, Omega_deg=Omega, omega_deg=omega, M_deg=M),
        mass_earth=mass,
        albedo=albedo,
        density_g_cm3=density,
    )


def build_lens_suite(tnos: List[TNO], cfg: QPHIConfig) -> List[Tuple[str, float, Any]]:
    """
    Return list of (lens_id, weight, lens_obj) in deterministic order.
    """
    return [
        (
            "orbit_plausibility",
            cfg.w_plausibility,
            OrbitPlausibilityLens(
                q_min_au=cfg.q_range_au[0],
                q_max_au=cfg.q_range_au[1],
                a_min_au=cfg.a_range_au[0],
                a_max_au=cfg.a_range_au[1],
                i_max_deg=cfg.i_range_deg[1],
            ),
        ),
        ("perihelion_clustering", cfg.w_perihelion, PerihelionClusteringLens(tnos, kappa=cfg.kappa_perihelion)),
        ("pole_alignment", cfg.w_pole, PoleAlignmentLens(tnos, sigma_deg=cfg.pole_sigma_deg)),
        ("precession_dominance", cfg.w_precession, PrecessionDominanceLens(tnos, ratio_target=cfg.precession_ratio_target, sigma_log=cfg.precession_sigma_log)),
        (
            "detectability",
            cfg.w_detectability,
            DetectabilityLens(
                mlim=cfg.mlim,
                sky_coverage_fraction=cfg.sky_coverage_fraction,
                width_mag=cfg.detect_width_mag,
                earth_lon_deg=cfg.earth_lon_deg,
            ),
        ),
    ]


def score_theta(theta: PlanetNineTheta, lens_suite: Sequence[Tuple[str, float, Any]]) -> CandidateResult:
    reports: Dict[str, LensReport] = {}
    total = 0.0
    for lens_id, w, lens in lens_suite:
        rep: LensReport = lens.score(theta)
        reports[lens_id] = rep
        total += float(w) * float(rep.log_score)

        # hard reject short-circuit
        if lens_id == "orbit_plausibility" and rep.details.get("ok", 1.0) < 0.5:
            total = -1e12
            break

    return CandidateResult(theta=theta, log_score=float(total), reports=reports)


def _softmax_weights(log_scores: np.ndarray, temperature: float) -> np.ndarray:
    m = float(np.max(log_scores))
    w = np.exp((log_scores - m) / max(1e-6, float(temperature)))
    w = w / np.sum(w)
    return w


def _weighted_mean_direction_radec(results: Sequence[CandidateResult], temperature: float) -> Tuple[float, float, np.ndarray]:
    logw = np.array([r.log_score for r in results], dtype=float)
    w = _softmax_weights(logw, temperature=temperature)

    dirs = []
    for r in results:
        vec = r.theta.elements.position_vector()
        u = vec / (np.linalg.norm(vec) + 1e-30)
        dirs.append(u)
    U = np.vstack(dirs)  # (N,3)
    mean_vec = (w[:, None] * U).sum(axis=0)
    mean_vec = mean_vec / (np.linalg.norm(mean_vec) + 1e-30)

    ra, dec = ecliptic_to_radec_deg(mean_vec)
    return ra, dec, mean_vec


def _weighted_containment_radii_deg(results: Sequence[CandidateResult], mean_vec: np.ndarray, qs: Sequence[float], temperature: float) -> List[float]:
    logw = np.array([r.log_score for r in results], dtype=float)
    w = _softmax_weights(logw, temperature=temperature)

    angs = []
    for r in results:
        vec = r.theta.elements.position_vector()
        u = vec / (np.linalg.norm(vec) + 1e-30)
        dot = float(np.dot(u, mean_vec))
        dot = max(-1.0, min(1.0, dot))
        angs.append(math.degrees(math.acos(dot)))
    angs = np.array(angs, dtype=float)

    # weighted quantile
    order = np.argsort(angs)
    angs_s = angs[order]
    w_s = w[order]
    cdf = np.cumsum(w_s)
    out = []
    for q in qs:
        idx = int(np.searchsorted(cdf, q, side="left"))
        idx = min(max(idx, 0), len(angs_s) - 1)
        out.append(float(angs_s[idx]))
    return out


def run_qphi(tnos: List[TNO], cfg: QPHIConfig) -> Dict[str, Any]:
    """
    Run the Q-PHI pipeline and write outputs.

    Returns a dict summary (also written to out_dir/summary.json).
    """
    rng = np.random.default_rng(cfg.seed)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- AQM-style ledger (optional) ----
    ledger = Ledger() if Ledger is not None else None
    if ledger is not None:
        ledger.append("StartRun", {"seed": cfg.seed})

    # ---- Build lenses ----
    lens_suite = build_lens_suite(tnos, cfg)
    if ledger is not None:
        ledger.append("BuildLenses", {"lenses": [lid for lid, _, _ in lens_suite]})

    # ---- Q-SEARCH: initial Monte Carlo ----
    t0 = time.time()
    initial: List[CandidateResult] = []
    hints = ProposalHints.from_tnos(tnos) if cfg.proposal_mode == "data_guided" else None
    if ledger is not None and hints is not None:
        ledger.append(
            "ProposalHints",
            {
                "tno_mean_varpi_deg": float(hints.tno_mean_varpi_deg),
                "varpi9_mu_deg": float(hints.varpi9_mu_deg),
                "tno_mean_i_deg": float(hints.tno_mean_i_deg),
                "tno_mean_Omega_deg": float(hints.tno_mean_Omega_deg),
                "proposal_varpi_sigma_deg": float(cfg.proposal_varpi_sigma_deg),
                "proposal_i_sigma_deg": float(cfg.proposal_i_sigma_deg),
                "proposal_Omega_sigma_deg": float(cfg.proposal_Omega_sigma_deg),
            },
        )
    for _ in range(int(cfg.n_initial)):
        theta = _sample_theta(rng, cfg, hints=hints)
        initial.append(score_theta(theta, lens_suite))
    if ledger is not None:
        ledger.append("Q_SEARCH_Done", {"n_initial": cfg.n_initial, "elapsed_s": float(time.time() - t0)})

    # ---- Keep elites ----
    initial.sort(key=lambda r: r.log_score, reverse=True)
    elites = initial[: int(cfg.elite_keep)]
    if ledger is not None:
        ledger.append("EliteSelect", {"elite_keep": cfg.elite_keep, "best_log_score": float(elites[0].log_score)})

    # ---- Q-REFINE: deterministic elite jitter rounds ----
    for rr in range(int(cfg.refine_rounds)):
        pool = list(elites)
        for base in elites:
            for _ in range(int(cfg.offspring_per_elite)):
                th = _jitter_theta(rng, base.theta, cfg)
                pool.append(score_theta(th, lens_suite))
        pool.sort(key=lambda r: r.log_score, reverse=True)
        elites = pool[: int(cfg.elite_keep)]
        if ledger is not None:
            ledger.append("RefineRound", {"round": rr + 1, "pool_size": len(pool), "best_log_score": float(elites[0].log_score)})

    posterior = elites

    # ---- Summaries ----
    ra_c, dec_c, mean_vec = _weighted_mean_direction_radec(posterior, temperature=cfg.posterior_temperature)
    r50, r90 = _weighted_containment_radii_deg(posterior, mean_vec, qs=[0.5, 0.9], temperature=cfg.posterior_temperature)

    summary = {
        "code_version": package_version(),
        "seed": cfg.seed,
        "n_tnos": len(tnos),
        "tno_digest": tno_set_digest(tnos),
        "cfg_digest": config_digest(cfg),
        "n_initial": cfg.n_initial,
        "elite_keep": cfg.elite_keep,
        "refine_rounds": cfg.refine_rounds,
        "offspring_per_elite": cfg.offspring_per_elite,
        "best_log_score": float(posterior[0].log_score),
        "posterior_temperature": float(cfg.posterior_temperature),
        "sky_center_ra_deg": float(ra_c),
        "sky_center_dec_deg": float(dec_c),
        "containment_radius_50_deg": float(r50),
        "containment_radius_90_deg": float(r90),
    }

    _write_candidates_csv(out_dir / "candidates.csv", posterior)
    _write_sky_samples_csv(out_dir / "sky_samples.csv", posterior, temperature=cfg.posterior_temperature)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    if ledger is not None:
        ledger.append("WriteOutputs", {"out_dir": str(out_dir)})
        (out_dir / "ledger.json").write_text(json.dumps(ledger.to_canonical_dict(), indent=2, sort_keys=True), encoding="utf-8")

    # ---- Store Tile in MerkleStore (optional) ----
    tile_hash = None
    if cfg.store_dir and MerkleStore is not None and Tile is not None and TileAddress is not None and CertificateBundle is not None:
        store = MerkleStore(cfg.store_dir)

        certs = CertificateBundle()
        certs.add_obligation("Determinism", "Run is deterministic under pinned config + seed + input dataset digest.")
        certs.add_obligation("DataProvenance", "TNO dataset digest is recorded; use JPL SBDB/MPC data for serious inference.")
        certs_hash = store.put(certs)

        ledger_hash = store.put(ledger) if ledger is not None else None

        addr = TileAddress.for_chapter(16, "S", 1)
        tile = Tile(
            kind="Tile",
            address=addr,
            seed={"title": "Planet Nine Q-PHI run", "cfg_seed": cfg.seed},
            payload={
                "config": cfg.__dict__,
                "summary": summary,
                "out_files": ["candidates.csv", "sky_samples.csv", "summary.json", "ledger.json"],
                "tno_digest": summary["tno_digest"],
            },
            deps=[h for h in [certs_hash, ledger_hash] if h],
            cert_hooks=[certs_hash],
            ledger_hooks=[ledger_hash] if ledger_hash else [],
        )
        tile_hash = store.put(tile)
        summary["tile_hash"] = tile_hash
        summary["store_dir"] = cfg.store_dir

    return summary


def _write_candidates_csv(path: Path, results: Sequence[CandidateResult]) -> None:
    rows = [r.to_row() for r in results]
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _write_sky_samples_csv(path: Path, results: Sequence[CandidateResult], temperature: float) -> None:
    logw = np.array([r.log_score for r in results], dtype=float)
    w = _softmax_weights(logw, temperature=temperature)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ra_deg", "dec_deg", "weight", "r_au", "m_est"])
        writer.writeheader()
        for wi, r in zip(w, results):
            r_vec = r.theta.elements.position_vector()
            r_au = float(np.linalg.norm(r_vec))
            ra, dec = ecliptic_to_radec_deg(r_vec)
            m_est = float(r.reports.get("detectability", LensReport("detectability", 0.0, {})).details.get("m_est", float("nan")))
            writer.writerow({"ra_deg": float(ra), "dec_deg": float(dec), "weight": float(wi), "r_au": r_au, "m_est": m_est})


def load_tnos_for_run(tno_csv: Optional[str], cfg: QPHIConfig, *, fetch_jpl: bool = False, jpl_limit: int = 200) -> List[TNO]:
    """
    Load the extreme-TNO dataset for the run.

    Priority:
      1) If fetch_jpl=True: query JPL SBDB Query API (requires internet)
      2) Else if tno_csv is provided: load from local CSV
      3) Else: built-in demo dataset (synthetic)

    The returned list is then filtered by cfg.tno_a_min_au and cfg.tno_q_min_au.
    """
    if fetch_jpl:
        try:
            tnos = fetch_extreme_tnos_from_jpl(
                a_min_au=cfg.tno_a_min_au,
                q_min_au=cfg.tno_q_min_au,
                limit=int(jpl_limit),
                sort="-a",
            )
        except Exception:
            # Deterministic fallback
            tnos = demo_extreme_tnos(seed=9)
    elif tno_csv is not None:
        tnos = load_tno_csv(tno_csv)
    else:
        tnos = demo_extreme_tnos(seed=9)

    # Apply "extreme" filter (idempotent for the JPL query)
    tnos = select_extreme(tnos, a_min_au=cfg.tno_a_min_au, q_min_au=cfg.tno_q_min_au)
    return tnos
