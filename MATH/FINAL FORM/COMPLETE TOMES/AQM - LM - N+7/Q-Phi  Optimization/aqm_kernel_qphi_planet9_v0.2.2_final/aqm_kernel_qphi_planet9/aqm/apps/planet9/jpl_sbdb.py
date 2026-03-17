from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import json
import time
from urllib.parse import urlencode

import requests

from .orbits import OrbitalElements
from .tno_data import TNO


@dataclass(frozen=True)
class JPLQuerySpec:
    """
    Minimal spec for an SBDB Query API call.
    """
    fields: Sequence[str]
    sb_class: str = "TNO"
    constraints: Optional[Dict[str, Any]] = None
    limit: int = 200
    sort: str = "-a"
    full_prec: bool = True
    timeout_s: float = 30.0


def _normalize_fields(fields: Any) -> List[str]:
    if fields is None:
        return []
    if isinstance(fields, list):
        return [str(x) for x in fields]
    if isinstance(fields, str):
        return [f.strip() for f in fields.split(",") if f.strip()]
    return [str(fields)]


def fetch_sbdb_query(spec: JPLQuerySpec) -> Dict[str, Any]:
    """
    Call the NASA/JPL SSD SBDB Query API (single request).

    Docs:
      - https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html

    Note:
      The API service asks clients to avoid concurrent requests.
    """
    base = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"

    params: Dict[str, Any] = {
        "fields": ",".join(spec.fields),
        "sb-class": spec.sb_class,
        "limit": int(spec.limit),
        "sort": spec.sort,
        "full-prec": "true" if spec.full_prec else "false",
    }
    if spec.constraints is not None:
        # JSON constraints must be URI-encoded; requests will handle encoding.
        params["sb-cdata"] = json.dumps(spec.constraints, separators=(",", ":"))

    # single request (no concurrency)
    resp = requests.get(base, params=params, timeout=float(spec.timeout_s))
    resp.raise_for_status()
    return resp.json()


def parse_sbdb_query_to_tnos(payload: Dict[str, Any]) -> List[TNO]:
    """
    Parse SBDB Query API response into our TNO records.

    Expected (typical) structure:
      - payload["fields"] : list of field names OR comma-separated string
      - payload["data"]   : list of rows, either lists (aligned with fields) or dicts
    """
    if "data" not in payload:
        # Some errors come back with "message" and/or "error"
        msg = payload.get("message") or payload.get("error") or "SBDB Query API returned no 'data' field."
        raise ValueError(str(msg))

    fields = _normalize_fields(payload.get("fields"))

    out: List[TNO] = []
    for row in payload["data"]:
        if isinstance(row, dict):
            rec = row
        else:
            # assume list/tuple aligned to fields
            rec = {fields[i]: row[i] for i in range(min(len(fields), len(row)))}

        name = str(rec.get("full_name") or rec.get("name") or rec.get("pdes") or "UNKNOWN")
        a = float(rec["a"])
        e = float(rec["e"])
        i_deg = float(rec["i"])
        Omega_deg = float(rec["om"])
        omega_deg = float(rec["w"])
        M_deg = float(rec.get("ma", 0.0))

        out.append(
            TNO(
                name=name,
                elements=OrbitalElements(
                    a_au=a,
                    e=e,
                    i_deg=i_deg,
                    Omega_deg=Omega_deg,
                    omega_deg=omega_deg,
                    M_deg=M_deg,
                ),
            )
        )
    return out


def fetch_extreme_tnos_from_jpl(a_min_au: float, q_min_au: float, limit: int = 200, sort: str = "-a") -> List[TNO]:
    """
    Convenience wrapper to query extreme TNOs from JPL SBDB Query API.

    Constraint syntax is documented here:
      - https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html

    We use:
      AND:
        a > a_min_au
        q > q_min_au
    """
    constraints = {"AND": [f"a|GT|{float(a_min_au)}", f"q|GT|{float(q_min_au)}"]}

    spec = JPLQuerySpec(
        fields=["full_name", "a", "e", "i", "om", "w", "ma", "q"],
        sb_class="TNO",
        constraints=constraints,
        limit=int(limit),
        sort=str(sort),
        full_prec=True,
    )
    payload = fetch_sbdb_query(spec)
    return parse_sbdb_query_to_tnos(payload)
