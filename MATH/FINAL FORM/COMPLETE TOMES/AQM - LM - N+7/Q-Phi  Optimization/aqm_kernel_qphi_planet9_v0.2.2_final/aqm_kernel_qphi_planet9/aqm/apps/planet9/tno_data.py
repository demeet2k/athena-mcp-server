from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .orbits import OrbitalElements


@dataclass(frozen=True)
class TNO:
    """
    A trans-Neptunian object with (heliocentric) osculating orbital elements.

    Notes:
      - Elements are treated as a snapshot at some epoch. For distant TNOs and
        for the coarse inference we do here, the exact epoch is often less
        important than the angular clustering statistics.
    """
    name: str
    elements: OrbitalElements


def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def tno_set_digest(tnos: Sequence[TNO]) -> str:
    payload = [
        {
            "name": t.name,
            "a_au": t.elements.a_au,
            "e": t.elements.e,
            "i_deg": t.elements.i_deg,
            "Omega_deg": t.elements.Omega_deg,
            "omega_deg": t.elements.omega_deg,
            "M_deg": t.elements.M_deg,
        }
        for t in tnos
    ]
    b = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_hex(b)


def _find_column(fieldnames: Sequence[str], candidates: Sequence[str]) -> str:
    """
    Find a header column name in `fieldnames` matching any candidate, using
    case-insensitive comparison.
    Returns the *original* column spelling.
    """
    norm = {fn.strip().lower(): fn for fn in fieldnames}
    for cand in candidates:
        key = cand.strip().lower()
        if key in norm:
            return norm[key]
    raise ValueError(f"CSV missing any of columns: {candidates}")


def load_tno_csv(path: str | Path) -> List[TNO]:
    """
    Load a CSV of orbital elements.

    Expected columns (some aliases accepted):
      - name
      - a_au (or a)
      - e
      - i_deg (or incl_deg)
      - Omega_deg  (longitude of ascending node)
      - omega_deg  (argument of perihelion)
      - M_deg (optional)

    IMPORTANT: Node and argument are distinct. If your CSV uses ambiguous names
    (e.g., both are called 'omega'), rename the node column to Omega_deg.
    """
    path = Path(path)
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        fns = [fn.strip() for fn in reader.fieldnames if fn is not None]

        name_k = _find_column(fns, ["name", "designation", "object"])
        a_k = _find_column(fns, ["a_au", "a", "semimajor_axis_au"])
        e_k = _find_column(fns, ["e", "ecc", "eccentricity"])
        i_k = _find_column(fns, ["i_deg", "i", "incl_deg", "inclination_deg"])

        # For the node/argument columns, prefer the standard explicit spellings.
        # Case matters in the canonical "Omega_deg" vs "omega_deg" convention,
        # so we check exact spellings first.
        Omega_k = None
        omega_k = None

        for fn in fns:
            if fn.strip() == "Omega_deg":
                Omega_k = fn
            if fn.strip() == "omega_deg":
                omega_k = fn

        # Fall back to aliases if needed
        if Omega_k is None:
            try:
                Omega_k = _find_column(fns, ["lan_deg", "node_deg", "long_asc_node_deg", "Omega", "LAN"])
            except ValueError:
                Omega_k = None

        if omega_k is None:
            try:
                omega_k = _find_column(fns, ["argp_deg", "peri_arg_deg", "argument_of_perihelion_deg", "omega"])
            except ValueError:
                omega_k = None

        if Omega_k is None or omega_k is None:
            raise ValueError(
                "CSV must include both the ascending node and argument of perihelion. "
                "Preferred headers: 'Omega_deg' and 'omega_deg'."
            )

        M_k = None
        try:
            M_k = _find_column(fns, ["M_deg", "M", "mean_anomaly_deg"])
        except ValueError:
            M_k = None

        out: List[TNO] = []
        for row in reader:
            name = str(row[name_k]).strip()
            a_au = float(row[a_k])
            e = float(row[e_k])
            i_deg = float(row[i_k])
            Omega_deg = float(row[Omega_k])
            omega_deg = float(row[omega_k])
            M_deg = float(row[M_k]) if M_k is not None and str(row.get(M_k, "")).strip() != "" else 0.0

            out.append(
                TNO(
                    name=name,
                    elements=OrbitalElements(
                        a_au=a_au,
                        e=e,
                        i_deg=i_deg,
                        Omega_deg=Omega_deg,
                        omega_deg=omega_deg,
                        M_deg=M_deg,
                    ),
                )
            )
        return out


def select_extreme(tnos: Iterable[TNO], a_min_au: float = 250.0, q_min_au: float = 30.0) -> List[TNO]:
    """
    Filter to "extreme" TNOs often used in Planet Nine analyses.

    Defaults are broad and should be tuned for your specific study.
    """
    out: List[TNO] = []
    for t in tnos:
        if t.elements.a_au >= a_min_au and t.elements.perihelion_distance_au() >= q_min_au:
            out.append(t)
    return out


def demo_extreme_tnos(seed: int = 9) -> List[TNO]:
    """
    Built-in *synthetic* extreme-TNO sample.

    This exists so the pipeline runs end-to-end without external data.
    For real inference, replace with a curated dataset from MPC/JPL.

    The angles are intentionally clustered to mimic the empirical "perihelion
    clustering" signal discussed in Planet Nine literature.
    """
    rng = np.random.default_rng(seed)

    names = [
        "Sedna_demo",
        "2012_VP113_demo",
        "2015_TG387_demo",
        "2010_GB174_demo",
        "2004_VN112_demo",
        "2013_SY99_demo",
        "2014_SR349_demo",
        "2013_FT28_demo",
        "2015_RX245_demo",
        "2015_BP519_demo",
        "2013_RF98_demo",
        "2014_FZ71_demo",
    ]

    # Cluster longitudes of perihelion around ~60° with ~20° dispersion
    varpi = (60.0 + rng.normal(0.0, 20.0, size=len(names))) % 360.0

    # Sample node longitudes, then set argument so that varpi = Omega + omega
    Omega = rng.uniform(0, 360, size=len(names)) % 360.0
    omega = (varpi - Omega) % 360.0

    # a,e,i roughly in the "extreme" regime
    a = rng.uniform(250, 700, size=len(names))
    e = rng.uniform(0.65, 0.9, size=len(names))
    i = np.clip(rng.normal(20.0, 8.0, size=len(names)), 0.0, 60.0)

    # Mean anomaly is not critical for the angular clustering metrics used here.
    M = rng.uniform(0, 360, size=len(names))

    return [
        TNO(
            name=names[k],
            elements=OrbitalElements(
                a_au=float(a[k]),
                e=float(e[k]),
                i_deg=float(i[k]),
                Omega_deg=float(Omega[k]),
                omega_deg=float(omega[k]),
                M_deg=float(M[k]),
            ),
        )
        for k in range(len(names))
    ]
