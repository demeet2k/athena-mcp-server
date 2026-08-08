from __future__ import annotations

"""Deterministic KC144 topological crystal.

This module is intentionally source-neutral and standard-library only. It turns
KC144's constitutional laws into executable finite objects without promoting
source documents, branch popularity, or graph adjacency into evidence or
authority.
"""

from collections import deque
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any, Iterable

HUB_VERSION = "KC144.TOPOLOGICAL.COMMAND.HUB.1.0.0"
PARENT_RUNTIME_SHA = "6b643134ee26ce117c2b548b5a89edf5cec55934"
FULL_AOR_SOURCE_SHA = "1ef1c992318897b581bf9740fa3cf50b9d5ea0e8"
GIT_BRAIN_SOURCE_SHA = "98499d9af914aac2664c237391b49805050bceb5"

BANDS: tuple[tuple[str, int, int, str], ...] = (
    ("H6", 1, 6, "constitutional root"),
    ("X16", 7, 22, "observation tensor: four poles x four faces"),
    ("BR21", 23, 43, "seven-stage / three-rail metabolism"),
    ("F37", 44, 80, "carrier atlas"),
    ("IC10", 81, 90, "conjunctive admission kernel"),
    ("KC15", 91, 105, "nonempty four-bit support lattice"),
    ("KC27", 106, 132, "three-trit semantic state register"),
    ("SSN12", 133, 144, "observation, audit, replay, and return"),
)

C4 = ("I", "R", "O", "T")
P3 = ("10", "00", "01")
P4 = ("11", "10", "00", "01")
S3 = ("OBJECT", "RELATION", "PROOF")
M12 = tuple(f"{axis}{phase}" for axis in C4 for phase in P3)

UNIVERSAL_COLUMNS = (
    "Objects and constructors",
    "Relations, interfaces, and order",
    "Coordinates and representations",
    "Symmetry, duality, and conjugation",
    "Local change, derivatives, and sensitivity",
    "Global accumulation, integration, and synthesis",
    "Recurrence, iteration, and generation",
    "Transforms, spectral views, and translation",
    "Invariants, sectors, and conserved structure",
    "Boundaries, singularities, and exceptions",
    "Search, proof, and optimization",
    "Return, inversion, and reconstruction",
)

COORDINATE_SYSTEMS: tuple[dict[str, Any], ...] = (
    {"id": "COORD.GID", "name": "Immutable GID", "cardinality": 144, "invertible": True},
    {"id": "COORD.GRID12", "name": "12x12 grid", "cardinality": 144, "invertible": True},
    {"id": "COORD.BAND", "name": "Eight-band constitution", "cardinality": 8, "invertible": False},
    {"id": "COORD.BAND_LOCAL", "name": "Band-local station", "cardinality": 144, "invertible": True},
    {"id": "COORD.LEGACY_S3", "name": "Legacy surface", "cardinality": 3, "invertible": False},
    {"id": "COORD.LEGACY_P4", "name": "Legacy pole", "cardinality": 4, "invertible": False},
    {"id": "COORD.UNIVERSAL_C12", "name": "Universal operation column", "cardinality": 12, "invertible": False},
    {"id": "COORD.LEGACY_FACTOR", "name": "S3 x P4 x C12", "cardinality": 144, "invertible": True},
    {"id": "COORD.M12_ROW", "name": "M12 row", "cardinality": 12, "invertible": False},
    {"id": "COORD.M12_COLUMN", "name": "M12 column", "cardinality": 12, "invertible": False},
    {"id": "COORD.M12_SQUARE", "name": "M12 x M12", "cardinality": 144, "invertible": True},
    {"id": "COORD.WHEEL", "name": "C144 wheel", "cardinality": 144, "invertible": True},
    {"id": "COORD.MIRROR", "name": "GID involution g -> 145-g", "cardinality": 72, "invertible": True},
    {"id": "COORD.D4_VIEW", "name": "Eight square symmetries", "cardinality": 8, "invertible": True},
    {"id": "COORD.NATIVE_SUBCRYSTAL", "name": "Band-native local coordinate", "cardinality": 144, "invertible": True},
    {"id": "COORD.POLYATLAS_FIBRE", "name": "Open coordinate fibre registry", "cardinality": "OPEN", "invertible": "DECLARED_PER_TRANSFORM"},
)

MATH_OBJECTS: tuple[dict[str, Any], ...] = (
    {"id": "MATH.CENSUS", "law": "6+16+21+37+10+15+27+12=144", "state": "EXECUTABLE"},
    {"id": "MATH.GRID", "law": "g=12(r-1)+c", "inverse": "r=1+floor((g-1)/12); c=1+((g-1) mod 12)", "state": "EXECUTABLE"},
    {"id": "MATH.WHEEL", "law": "theta(g)=2.5*(g-1) degrees", "state": "EXECUTABLE"},
    {"id": "MATH.MIRROR", "law": "M(g)=145-g; M^2=I", "state": "EXECUTABLE"},
    {"id": "MATH.LEGACY_FACTOR", "law": "g=1+48s+12p+q", "state": "EXECUTABLE"},
    {"id": "MATH.M12", "law": "M12=C4xP3", "state": "EXECUTABLE"},
    {"id": "MATH.M12_SQUARE", "law": "KC144=M12xM12=(C4xP3)^2", "state": "EXECUTABLE"},
    {"id": "MATH.M12_TO_GID", "law": "g=12[3i(a)+j(p)]+[3i(b)+j(q)]+1", "state": "EXECUTABLE"},
    {"id": "MATH.GRID_GRAPH", "law": "P12 square P12", "expected_edges": 264, "state": "EXECUTABLE"},
    {"id": "MATH.RADIAL_GRAPH", "law": "C144", "expected_edges": 144, "state": "EXECUTABLE"},
    {"id": "MATH.MIRROR_GRAPH", "law": "72 disjoint involution pairs", "expected_edges": 72, "state": "EXECUTABLE"},
    {"id": "MATH.BR21_GRAPH", "law": "P7 square C3", "expected_edges": 39, "state": "EXECUTABLE"},
    {"id": "MATH.KC15_GRAPH", "law": "nonempty B4 one-bit cover", "expected_edges": 28, "state": "EXECUTABLE"},
    {"id": "MATH.KC27_GRAPH", "law": "P3 square P3 square P3", "expected_edges": 54, "state": "EXECUTABLE"},
    {"id": "MATH.READINESS", "law": "ATHENA_READY iff C&I&E&P&R&V&O&M&S&X all PASS", "state": "EXECUTABLE"},
    {"id": "MATH.AOR_RESIDUAL", "law": "severity*leverage*information_gain/cost", "state": "LIVE_SOURCE_RUNTIME"},
    {"id": "MATH.AOR_FRONTIER", "law": "readiness*gain*independence*bridge/cost", "state": "LIVE_SOURCE_RUNTIME"},
    {"id": "MATH.AOR_SUCCESSOR", "law": "DeltaJ*information_gain*bridge*option_value/cost", "state": "LIVE_SOURCE_RUNTIME"},
    {"id": "MATH.AOR_ROBUSTNESS", "law": "epsilon*=(q^(1/5)-1)/(q^(1/5)+1)", "state": "LIVE_SOURCE_RUNTIME"},
)

SOURCE_DATASETS: tuple[dict[str, Any], ...] = (
    {"id": "DATA.DRIVE.COORD_MATH_GRAPH", "kind": "GOOGLE_DOC", "title": "ATHENA KC144 COMPLETE COORDINATE / MATHEMATICS / GRAPH SPECIFICATION", "locator": "gdrive:1RmZAkqwe796Pe_XWez6-0CLuY4MBpuldGLhXVuoAcwE", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.FULL_SEATING", "kind": "GOOGLE_DOC", "title": "Omega KC144 FULL-SEATING CRYSTALLINE-MYCELIUM JSON", "locator": "gdrive:1SNaq8MUcv4C8Nlm662knUmmk9-9Rob9gn7k8L2CgYak", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.MASTER_GIT_TASK", "kind": "GOOGLE_DOC", "title": "MASTER TASK LIST GIT", "locator": "gdrive:1gSzMzjK7XwjofwRVnnQYVGFKrCjoosw6dyJcRLIr52E", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.META24_CBG2", "kind": "GOOGLE_DOC", "title": "META24 CBG-2 LIVE TOPOLOGY INGESTION + BRIDGE TEST RUNNER", "locator": "gdrive:1QCWdPxKyOVFBi2cVWqAKFQJmLRPeZ2-Z2eyo0XTVi0o", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.GRAPH_SYSTEM", "kind": "GOOGLE_DOC", "title": "ATHENA GRAPH SYSTEM V2", "locator": "gdrive:1xw9i7sFz9Ae0wRK794Q16UeEG9fj9JU2dKymgM0RxAc", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.GRAPH_FOUNDRY", "kind": "GOOGLE_DOC", "title": "ATHENA GRAPH-COORDINATE-VECTOR NAVIGATIONAL FOUNDRY", "locator": "gdrive:1F07Q1t0Uvx6QriN3wfLXihJpmQZGs9qQ1wOB8juo_Ig", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.MATH_COORD", "kind": "GOOGLE_DOC", "title": "KC144 RDX MATH-COORD", "locator": "gdrive:1k0Z5Fv3ZYU4HXohdmr5Sj-i8VtFNvgMJ-LyRHhMtPyw", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.HARNESS_SYNTHESIS", "kind": "GOOGLE_DOC", "title": "HARNESS - DEEP GOOGLE DOCS SYNTHESIS", "locator": "gdrive:1w5fjzD3DAO2GIS5l3Mv44AcG3sSRuaeN-PekGLBGuSw", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.META_OBSERVER", "kind": "GOOGLE_DOC", "title": "META-OBSERVER KC144 CAUSAL-DELTA HARNESS", "locator": "gdrive:16wwbSGJxpjbAdNiIjw_cmuohoi3WuMoVMKgZKVMz-as", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.REAL_WORK_SKILL", "kind": "GOOGLE_DOC", "title": "ATHENA REAL WORK - GLOBAL ANTI-SANDBAGGING SKILL", "locator": "gdrive:1P96vV0vaPlFLqeK8XKUhwvFK4M-EPfReZXIN7rJI1m8", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.HUG", "kind": "GOOGLE_DOC", "title": "HUG work", "locator": "gdrive:1nHLzQAAgk3Ik-_SyXF0YPrCFNiNlrM_fCE-2eGpyfWo", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.MMLG2", "kind": "GOOGLE_DOC", "title": "ATHENA META MACHINE LEARNING GAME v2", "locator": "gdrive:1ISdrZ0ycWYXMP-kUA85uyJetuxlbBTnEwxnD9krMZ7g", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.OMNICOORD", "kind": "GOOGLE_DOC", "title": "KC144 OMNICOORDINATE HYPER-CRYSTAL", "locator": "gdrive:1LoJBGBzpKh1i6laS6wyKybLuWe2tJliWrNMk0x6w_44", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.POLYCARTOGRAPHIC", "kind": "GOOGLE_DOC", "title": "KC144.V3 Unified Polycartographic Reality-Contact Architecture", "locator": "gdrive:1HuwujBfsHNoXy0tOSZH2P98L-Gw3rdFbg_fgcuIJKkE", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.CONTROL_PLANE", "kind": "GOOGLE_SHEET", "title": "ATHENA DRIVE BRAIN - OMEGA1 CONTROL PLANE", "locator": "gdrive:18zrrNB01aH8SDPxuiEzEPZ9v7aZkecorv_DW41KbdqQ", "state": "SOURCE_INDEXED"},
    {"id": "DATA.DRIVE.LOCAL_BRAIN_PORT", "kind": "GOOGLE_DOC", "title": "ATHENA LOCAL BRAIN PORT OMEGA2", "locator": "gdrive:1Wk5251fbxpCOc5bHp6t_lHtp9Weoq3sFswY-dSA-bXs", "state": "SOURCE_INDEXED"},
    {"id": "DATA.GIT.RUNTIME_UNIFIED", "kind": "GIT_COMMIT", "title": "AOR x Collective early braid", "locator": f"github:demeet2k/athena-mcp-server@{PARENT_RUNTIME_SHA}", "state": "LIVE_PARENT"},
    {"id": "DATA.GIT.RUNTIME_AOR_FULL", "kind": "GIT_COMMIT", "title": "Full staged AOR modular runtime", "locator": f"github:demeet2k/athena-mcp-server@{FULL_AOR_SOURCE_SHA}", "state": "STAGED_SOURCE"},
    {"id": "DATA.GIT.GIT_BRAIN_AOR", "kind": "GIT_COMMIT", "title": "AOR Git-brain policies and schemas", "locator": f"github:demeet2k/Athena@{GIT_BRAIN_SOURCE_SHA}", "state": "STAGED_SOURCE"},
)

ORGANS: tuple[dict[str, Any], ...] = (
    {"id": "ORGAN.GIT_LEDGER", "kind": "HARNESS", "gid": 1, "state": "LIVE_UNIFIED", "depends_on": []},
    {"id": "ORGAN.CCR", "kind": "HARNESS", "gid": 2, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.GIT_LEDGER"]},
    {"id": "ORGAN.IDENTITY_FIREWALL", "kind": "SKILL", "gid": 3, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.CCR"]},
    {"id": "ORGAN.SCHEMA_VALIDATION", "kind": "TOOL_SURFACE", "gid": 4, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.CCR"]},
    {"id": "ORGAN.TIME_PROVENANCE", "kind": "DATASET", "gid": 5, "state": "LIVE_UNIFIED", "depends_on": []},
    {"id": "ORGAN.SOURCE_RETURN", "kind": "HARNESS", "gid": 6, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.GIT_LEDGER"]},
    {"id": "ORGAN.JSPACE", "kind": "GRAPH", "gid": 7, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.CCR"]},
    {"id": "ORGAN.SCALE", "kind": "COORDINATE", "gid": 8, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.JSPACE"]},
    {"id": "ORGAN.KC144_CORE", "kind": "COORDINATE", "gid": 9, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.CCR"]},
    {"id": "ORGAN.POLYCOORDINATE", "kind": "COORDINATE", "gid": 10, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.KC144_CORE"]},
    {"id": "ORGAN.TRANSFORM_RUNTIME", "kind": "TOOL_SURFACE", "gid": 11, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.POLYCOORDINATE"]},
    {"id": "ORGAN.HOLONOMY", "kind": "MATH", "gid": 12, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.TRANSFORM_RUNTIME"]},
    {"id": "ORGAN.CRYSTAL_RUNTIME", "kind": "HARNESS", "gid": 13, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.KC144_CORE", "ORGAN.JSPACE"]},
    {"id": "ORGAN.EMISSION_GATEWAY", "kind": "TOOL_SURFACE", "gid": 14, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.CRYSTAL_RUNTIME"]},
    {"id": "ORGAN.SESSION_RUNTIME", "kind": "HARNESS", "gid": 15, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.GIT_LEDGER"]},
    {"id": "ORGAN.GIT_CAS", "kind": "TOOL_SURFACE", "gid": 16, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.GIT_LEDGER"]},
    {"id": "ORGAN.COLLECTIVE_RUNTIME", "kind": "HARNESS", "gid": 23, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.JSPACE"]},
    {"id": "ORGAN.COLLECTIVE_GROWTH", "kind": "HARNESS", "gid": 24, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.COLLECTIVE_RUNTIME"]},
    {"id": "ORGAN.COLLECTIVE_MEMORY_V2", "kind": "HARNESS", "gid": 25, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.COLLECTIVE_RUNTIME", "ORGAN.COLLECTIVE_GROWTH"]},
    {"id": "ORGAN.AOR_CORE", "kind": "HARNESS", "gid": 26, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.JSPACE", "ORGAN.SCALE"]},
    {"id": "ORGAN.AOR_BRANCH", "kind": "HARNESS", "gid": 27, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.AOR_CORE"]},
    {"id": "ORGAN.AOR_ROBUSTNESS", "kind": "MATH", "gid": 28, "state": "LIVE_UNIFIED", "depends_on": ["ORGAN.AOR_CORE"]},
    {"id": "ORGAN.AUTHORITY_Y1", "kind": "HARNESS", "gid": 29, "state": "LIVE_UNIFIED", "source": PARENT_RUNTIME_SHA, "depends_on": ["ORGAN.AOR_CORE"]},
    {"id": "ORGAN.EQ1", "kind": "HARNESS", "gid": 30, "state": "PARTIALLY_BRAIDED_NOT_SURFACED", "source": PARENT_RUNTIME_SHA, "depends_on": ["ORGAN.AUTHORITY_Y1"]},
    {"id": "ORGAN.SX1", "kind": "HARNESS", "gid": 31, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.EQ1"]},
    {"id": "ORGAN.RAG1", "kind": "HARNESS", "gid": 32, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.SX1", "ORGAN.EQ1"]},
    {"id": "ORGAN.HUG_ABI1", "kind": "HARNESS", "gid": 33, "state": "STAGED_SOURCE_FAIL_CLOSED", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.RAG1"]},
    {"id": "ORGAN.GAP1", "kind": "GRAPH", "gid": 34, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.RAG1", "ORGAN.HUG_ABI1"]},
    {"id": "ORGAN.FIELD1", "kind": "HARNESS", "gid": 35, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.GAP1", "ORGAN.SX1"]},
    {"id": "ORGAN.SURFACE1", "kind": "VALIDATOR", "gid": 36, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.FIELD1"]},
    {"id": "ORGAN.COMPOSITION1", "kind": "VALIDATOR", "gid": 37, "state": "STAGED_SOURCE", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.SURFACE1"]},
    {"id": "ORGAN.PROMOTION1", "kind": "HARNESS", "gid": 38, "state": "STAGED_SOURCE_NOT_WIRED", "source": FULL_AOR_SOURCE_SHA, "depends_on": ["ORGAN.SURFACE1", "ORGAN.COMPOSITION1"]},
    {"id": "ORGAN.TOPOLOGICAL_COMMAND_HUB", "kind": "COMMAND_CENTER", "gid": 39, "state": "THIS_CANDIDATE", "depends_on": ["ORGAN.KC144_CORE", "ORGAN.JSPACE", "ORGAN.AOR_CORE", "ORGAN.COLLECTIVE_MEMORY_V2"]},
)

SOURCE_FIBRES: tuple[dict[str, Any], ...] = (
    {"id": "HARNESS.DRIVE.DEEP_SYNTHESIS", "kind": "HARNESS", "dataset": "DATA.DRIVE.HARNESS_SYNTHESIS", "state": "SOURCE_INDEXED"},
    {"id": "HARNESS.META_OBSERVER_CAUSAL_DELTA", "kind": "HARNESS", "dataset": "DATA.DRIVE.META_OBSERVER", "state": "SOURCE_INDEXED"},
    {"id": "SKILL.REAL_WORK_ANTI_SANDBAGGING", "kind": "SKILL", "dataset": "DATA.DRIVE.REAL_WORK_SKILL", "state": "SOURCE_INDEXED"},
    {"id": "HARNESS.MMLG2", "kind": "HARNESS", "dataset": "DATA.DRIVE.MMLG2", "state": "SOURCE_INDEXED"},
    {"id": "HARNESS.HUG", "kind": "HARNESS", "dataset": "DATA.DRIVE.HUG", "state": "SOURCE_INDEXED_ALGORITHM_UNRESOLVED"},
    {"id": "HARNESS.POLYCARTOGRAPHIC_REALITY_CONTACT", "kind": "HARNESS", "dataset": "DATA.DRIVE.POLYCARTOGRAPHIC", "state": "SOURCE_INDEXED"},
    {"id": "HARNESS.FULL_SEATING_CRYSTALLINE_MYCELIUM", "kind": "HARNESS", "dataset": "DATA.DRIVE.FULL_SEATING", "state": "SOURCE_INDEXED"},
    {"id": "HARNESS.GRAPH_COORD_VECTOR_FOUNDRY", "kind": "HARNESS", "dataset": "DATA.DRIVE.GRAPH_FOUNDRY", "state": "SOURCE_INDEXED"},
    {"id": "SKILL.LOCAL_BRAIN_PORT", "kind": "SKILL", "dataset": "DATA.DRIVE.LOCAL_BRAIN_PORT", "state": "SOURCE_INDEXED"},
    {"id": "SKILL.DRIVE_CONTROL_PLANE", "kind": "SKILL", "dataset": "DATA.DRIVE.CONTROL_PLANE", "state": "SOURCE_INDEXED"},
)

TRANSPORTS: tuple[dict[str, Any], ...] = (
    {"id": "TRANSPORT.PHEROMONE_TO_RAG", "src": "ORGAN.COLLECTIVE_MEMORY_V2", "relation": "ROUTING_PRIOR_NOT_EVIDENCE", "dst": "ORGAN.RAG1", "state": "REQUIRED_NOT_MECHANIZED"},
    {"id": "TRANSPORT.ALARM_TO_GAP", "src": "ORGAN.JSPACE", "relation": "TYPED_INVALIDATION", "dst": "ORGAN.GAP1", "state": "REQUIRED_NOT_MECHANIZED"},
    {"id": "TRANSPORT.RGO_TO_REWARD", "src": "ORGAN.COLLECTIVE_MEMORY_V2", "relation": "WITNESSED_OUTCOME_NOT_PREDICTION", "dst": "ORGAN.AOR_CORE", "state": "REQUIRED_NOT_MECHANIZED"},
    {"id": "TRANSPORT.AOR_TO_COLLECTIVE", "src": "ORGAN.AOR_CORE", "relation": "WHAT_TO_RESOURCE", "dst": "ORGAN.COLLECTIVE_RUNTIME", "state": "DECLARED_MANUAL_SEAM"},
    {"id": "TRANSPORT.FIELD_TO_PROMOTION", "src": "ORGAN.FIELD1", "relation": "CANDIDATE_TO_GATE", "dst": "ORGAN.PROMOTION1", "state": "STAGED_SOURCE"},
    {"id": "TRANSPORT.PROMOTION_TO_RETURN", "src": "ORGAN.PROMOTION1", "relation": "QUALIFIED_RECEIPT_TO_SOURCE_RETURN", "dst": "ORGAN.SOURCE_RETURN", "state": "HOLD_UNTIL_EXACT_HEAD_WITNESS"},
)

READINESS_GATES: tuple[dict[str, Any], ...] = (
    {"id": "IC01.CAPABILITY", "symbol": "C", "gid": 81, "state": "PARTIAL", "reason": "full staged organ set is not yet active on the unified branch"},
    {"id": "IC02.INTEGRATION", "symbol": "I", "gid": 82, "state": "HOLD", "reason": "Collective and full AOR stacks remain divergent"},
    {"id": "IC03.EXECUTABLE_LOOP", "symbol": "E", "gid": 83, "state": "PARTIAL", "reason": "core loops execute; EQ/SX/RAG/HUG/GAP/FIELD/PROMOTION are not all mounted"},
    {"id": "IC04.PERSISTENCE", "symbol": "P", "gid": 84, "state": "PARTIAL", "reason": "semantic, Git, collective, authority, and AOR receipts exist; promotion receipt wiring is incomplete"},
    {"id": "IC05.REPLAY", "symbol": "R", "gid": 85, "state": "PARTIAL", "reason": "existing ledgers replay; whole-organism replay has no terminal receipt"},
    {"id": "IC06.VERIFICATION", "symbol": "V", "gid": 86, "state": "HOLD", "reason": "this candidate requires exact-head unit and smoke witnesses"},
    {"id": "IC07.OBSERVABILITY", "symbol": "O", "gid": 87, "state": "PASS_STRUCTURAL", "reason": "hub exposes topology, inventory, communication, datasets, graphs, and blockers"},
    {"id": "IC08.MIGRATION", "symbol": "M", "gid": 88, "state": "HOLD", "reason": "divergent AOR and Collective state migrations are not certified"},
    {"id": "IC09.SURFACE_SECURITY", "symbol": "S", "gid": 89, "state": "HOLD", "reason": "full surface/composition/security certificate must run on exact head"},
    {"id": "IC10.CROSS_ORGAN", "symbol": "X", "gid": 90, "state": "HOLD", "reason": "required Collective-to-AOR transports are indexed but not mechanized"},
)

BASE_RESOURCE_URIS = (
    "athena://manifest", "athena://kc144/stations", "athena://state/head", "athena://registry",
    "athena://jspace", "athena://scale", "athena://coordinate/charts", "athena://crystals",
    "athena://math", "athena://time/provenance", "athena://transforms", "athena://emissions",
    "athena://collective/runtime", "athena://collective/growth", "athena://collective/v2",
    "athena://orchestration/law", "athena://orchestration/recent", "athena://orchestration/robustness",
    "athena://branches", "athena://authority",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _band(gid: int) -> tuple[str, int, int, str]:
    for item in BANDS:
        if item[1] <= gid <= item[2]:
            return item
    raise ValueError("gid must be in 1..144")


def gid_from_grid(row: int, col: int) -> int:
    if not (1 <= row <= 12 and 1 <= col <= 12):
        raise ValueError("row and col must be in 1..12")
    return 12 * (row - 1) + col


def grid_from_gid(gid: int) -> tuple[int, int]:
    if not 1 <= gid <= 144:
        raise ValueError("gid must be in 1..144")
    return 1 + (gid - 1) // 12, 1 + (gid - 1) % 12


def legacy_factor(gid: int) -> dict[str, Any]:
    if not 1 <= gid <= 144:
        raise ValueError("gid must be in 1..144")
    n = gid - 1
    s = n // 48
    p = (n % 48) // 12
    q = n % 12
    return {"s": s, "surface": S3[s], "p": p, "pole": P4[p], "q": q, "column": q + 1}


def gid_from_legacy(s: int, p: int, q: int) -> int:
    if not (0 <= s < 3 and 0 <= p < 4 and 0 <= q < 12):
        raise ValueError("legacy factors outside S3 x P4 x C12")
    return 1 + 48 * s + 12 * p + q


def m12_factor(gid: int) -> dict[str, Any]:
    row, col = grid_from_gid(gid)
    return {
        "row_index": row,
        "row": M12[row - 1],
        "row_axis": C4[(row - 1) // 3],
        "row_phase": P3[(row - 1) % 3],
        "column_index": col,
        "column": M12[col - 1],
        "column_axis": C4[(col - 1) // 3],
        "column_phase": P3[(col - 1) % 3],
    }


def gid_from_m12(row_axis: str, row_phase: str, col_axis: str, col_phase: str) -> int:
    try:
        r = 3 * C4.index(row_axis) + P3.index(row_phase) + 1
        c = 3 * C4.index(col_axis) + P3.index(col_phase) + 1
    except ValueError as exc:
        raise ValueError("invalid C4/P3 coordinate") from exc
    return gid_from_grid(r, c)


def d4_image(gid: int, operation: str) -> int:
    r, c = grid_from_gid(gid)
    transforms = {
        "I": (r, c),
        "R90": (c, 13 - r),
        "R180": (13 - r, 13 - c),
        "R270": (13 - c, r),
        "REF_H": (13 - r, c),
        "REF_V": (r, 13 - c),
        "REF_D": (c, r),
        "REF_A": (13 - c, 13 - r),
    }
    if operation not in transforms:
        raise ValueError(f"unknown D4 operation: {operation}")
    return gid_from_grid(*transforms[operation])


def native_coordinate(gid: int) -> dict[str, Any]:
    band, lo, _hi, _role = _band(gid)
    i = gid - lo
    if band == "X16":
        return {"system": "X16", "pole": P4[i // 4], "face": C4[i % 4], "index": i + 1}
    if band == "BR21":
        return {"system": "BR21", "stage": i // 3 + 1, "rail": P3[i % 3], "index": i + 1}
    if band == "KC15":
        mask = i + 1
        return {"system": "KC15", "mask": format(mask, "04b"), "mask_value": mask, "support_size": mask.bit_count()}
    if band == "KC27":
        return {"system": "KC27", "trits": f"{i // 9}{(i // 3) % 3}{i % 3}", "index": i}
    if band == "SSN12":
        return {"system": "SSN12", "m12": M12[i], "index": i + 1}
    return {"system": band, "index": i + 1}


@dataclass(frozen=True)
class Seat:
    gid: int
    sid: str
    grid: str
    row: int
    column: int
    band: str
    band_local_index: int
    band_role: str
    universal_operation: str
    wheel_degrees: float
    mirror_gid: int
    legacy: dict[str, Any]
    m12: dict[str, Any]
    d4: dict[str, int]
    native: dict[str, Any]


def seat(gid: int) -> dict[str, Any]:
    row, col = grid_from_gid(gid)
    band, lo, _hi, role = _band(gid)
    item = Seat(
        gid=gid,
        sid=f"KC144.SID.{gid:03d}",
        grid=f"R{row:02d}C{col:02d}",
        row=row,
        column=col,
        band=band,
        band_local_index=gid - lo + 1,
        band_role=role,
        universal_operation=UNIVERSAL_COLUMNS[col - 1],
        wheel_degrees=2.5 * (gid - 1),
        mirror_gid=145 - gid,
        legacy=legacy_factor(gid),
        m12=m12_factor(gid),
        d4={op: d4_image(gid, op) for op in ("I", "R90", "R180", "R270", "REF_H", "REF_V", "REF_D", "REF_A")},
        native=native_coordinate(gid),
    )
    return asdict(item)


def seats() -> list[dict[str, Any]]:
    return [seat(g) for g in range(1, 145)]


def _edge(src: int, dst: int, relation: str, directed: bool = False, graph_name: str = "") -> dict[str, Any]:
    return {"src": src, "dst": dst, "relation": relation, "directed": directed, "graph": graph_name}


def physical_grid_edges() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in range(1, 13):
        for c in range(1, 13):
            g = gid_from_grid(r, c)
            if c < 12:
                out.append(_edge(g, gid_from_grid(r, c + 1), "GRID_ADJACENT", graph_name="physical_grid"))
            if r < 12:
                out.append(_edge(g, gid_from_grid(r + 1, c), "GRID_ADJACENT", graph_name="physical_grid"))
    return out


def radial_ring_edges() -> list[dict[str, Any]]:
    return [_edge(g, 1 if g == 144 else g + 1, "RADIAL_SUCCESSOR", directed=True, graph_name="radial_ring") for g in range(1, 145)]


def mirror_edges() -> list[dict[str, Any]]:
    return [_edge(g, 145 - g, "MIRROR", graph_name="mirror") for g in range(1, 73)]


def br21_edges() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    base = 23
    for stage in range(7):
        for rail in range(3):
            g = base + 3 * stage + rail
            if stage < 6:
                out.append(_edge(g, g + 3, "BR21_STAGE_SUCCESSOR", graph_name="br21_native"))
        nodes = [base + 3 * stage + rail for rail in range(3)]
        out.extend((_edge(nodes[0], nodes[1], "BR21_RAIL", graph_name="br21_native"),
                    _edge(nodes[1], nodes[2], "BR21_RAIL", graph_name="br21_native"),
                    _edge(nodes[2], nodes[0], "BR21_RAIL", graph_name="br21_native")))
    return out


def kc15_edges() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for mask in range(1, 16):
        for bit in range(4):
            if not mask & (1 << bit):
                sup = mask | (1 << bit)
                out.append(_edge(90 + mask, 90 + sup, "KC15_ONE_BIT_COVER", directed=True, graph_name="kc15_native"))
    return out


def _trits(index: int) -> tuple[int, int, int]:
    return index // 9, (index // 3) % 3, index % 3


def _trit_index(a: int, b: int, c: int) -> int:
    return 9 * a + 3 * b + c


def kc27_edges() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index in range(27):
        coord = list(_trits(index))
        for dim in range(3):
            if coord[dim] < 2:
                nxt = coord.copy()
                nxt[dim] += 1
                out.append(_edge(106 + index, 106 + _trit_index(*nxt), f"KC27_TRIT_{dim+1}", graph_name="kc27_native"))
    return out


GRAPH_BUILDERS = {
    "physical_grid": physical_grid_edges,
    "radial_ring": radial_ring_edges,
    "mirror": mirror_edges,
    "br21_native": br21_edges,
    "kc15_native": kc15_edges,
    "kc27_native": kc27_edges,
}

GRAPH_EXPECTED_COUNTS = {
    "physical_grid": 264,
    "radial_ring": 144,
    "mirror": 72,
    "br21_native": 39,
    "kc15_native": 28,
    "kc27_native": 54,
}


def graph(name: str, include_edges: bool = True) -> dict[str, Any]:
    if name == "combined":
        edges = [edge for graph_name in GRAPH_BUILDERS for edge in GRAPH_BUILDERS[graph_name]()]
        nodes = sorted({n for edge in edges for n in (edge["src"], edge["dst"])})
        body: dict[str, Any] = {"id": "GRAPH.COMBINED", "name": name, "nodes": len(nodes), "edge_records": len(edges), "typed_multigraph": True}
    elif name == "compiler_declared":
        body = {
            "id": "GRAPH.COMPILER.DECLARED",
            "name": name,
            "nodes": 144,
            "edge_records": 690,
            "state": "SOURCE_DECLARED_NOT_RECONSTRUCTED_HERE",
            "boundary": "cardinality is indexed from source; records are not fabricated",
        }
        edges = []
    else:
        if name not in GRAPH_BUILDERS:
            raise ValueError(f"unknown graph: {name}")
        edges = GRAPH_BUILDERS[name]()
        nodes = sorted({n for edge in edges for n in (edge["src"], edge["dst"])})
        body = {"id": f"GRAPH.{name.upper()}", "name": name, "nodes": len(nodes), "edge_records": len(edges), "typed_multigraph": False}
    body["edge_digest"] = digest(edges)
    if include_edges:
        body["edges"] = edges
    return body


def graph_summaries() -> list[dict[str, Any]]:
    return [graph(name, include_edges=False) for name in (*GRAPH_BUILDERS.keys(), "compiler_declared", "combined")]


def _adjacency(graph_names: Iterable[str]) -> dict[int, list[tuple[int, str]]]:
    out: dict[int, list[tuple[int, str]]] = {g: [] for g in range(1, 145)}
    for name in graph_names:
        if name not in GRAPH_BUILDERS:
            raise ValueError(f"graph cannot be routed: {name}")
        for edge in GRAPH_BUILDERS[name]():
            out[edge["src"]].append((edge["dst"], edge["relation"]))
            if not edge["directed"]:
                out[edge["dst"]].append((edge["src"], edge["relation"]))
    for node in out:
        out[node].sort(key=lambda pair: (pair[0], pair[1]))
    return out


def route(src: int, dst: int, graphs: Iterable[str] = ("physical_grid",)) -> dict[str, Any]:
    grid_from_gid(src)
    grid_from_gid(dst)
    names = tuple(dict.fromkeys(graphs))
    adjacency = _adjacency(names)
    queue: deque[int] = deque([src])
    parent: dict[int, tuple[int, str] | None] = {src: None}
    while queue:
        node = queue.popleft()
        if node == dst:
            break
        for nxt, relation in adjacency[node]:
            if nxt not in parent:
                parent[nxt] = (node, relation)
                queue.append(nxt)
    if dst not in parent:
        return {"state": "UNREACHABLE", "src": src, "dst": dst, "graphs": names, "path": [], "relations": []}
    path = [dst]
    relations: list[str] = []
    cursor = dst
    while parent[cursor] is not None:
        prev, relation = parent[cursor]  # type: ignore[misc]
        path.append(prev)
        relations.append(relation)
        cursor = prev
    path.reverse()
    relations.reverse()
    return {"state": "ROUTE_FOUND", "src": src, "dst": dst, "graphs": names, "hops": len(path) - 1, "path": path, "relations": relations}


def stable_carrier_gid(identifier: str, lo: int = 44, hi: int = 80) -> int:
    if lo > hi:
        raise ValueError("invalid carrier range")
    value = int.from_bytes(hashlib.sha256(identifier.encode("utf-8")).digest()[:8], "big")
    return lo + value % (hi - lo + 1)


def static_inventory() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = [dict(item) for item in ORGANS]
    for item in COORDINATE_SYSTEMS:
        items.append({"id": item["id"], "kind": "COORDINATE", "state": "STRUCTURAL", "gid": stable_carrier_gid(item["id"]), "payload": dict(item)})
    for item in MATH_OBJECTS:
        items.append({"id": item["id"], "kind": "MATH", "state": item["state"], "gid": stable_carrier_gid(item["id"]), "payload": dict(item)})
    for name in (*GRAPH_BUILDERS.keys(), "compiler_declared", "combined"):
        summary = graph(name, include_edges=False)
        items.append({"id": summary["id"], "kind": "GRAPH", "state": summary.get("state", "STRUCTURAL"), "gid": stable_carrier_gid(summary["id"]), "payload": summary})
    for item in SOURCE_DATASETS:
        items.append({"id": item["id"], "kind": "DATASET", "state": item["state"], "gid": stable_carrier_gid(item["id"]), "payload": dict(item)})
    for item in SOURCE_FIBRES:
        items.append({"id": item["id"], "kind": item["kind"], "state": item["state"], "gid": stable_carrier_gid(item["id"]), "payload": dict(item)})
    for item in READINESS_GATES:
        items.append({"id": item["id"], "kind": "GATE", "state": item["state"], "gid": item["gid"], "payload": dict(item)})
    return sorted(items, key=lambda item: (item["gid"], item["kind"], item["id"]))


def readiness() -> dict[str, Any]:
    gate_states = {item["symbol"]: item["state"] for item in READINESS_GATES}
    ready = all(state == "PASS" for state in gate_states.values())
    return {
        "equation": "ATHENA_READY iff C&I&E&P&R&V&O&M&S&X all PASS",
        "gates": [dict(item) for item in READINESS_GATES],
        "gate_states": gate_states,
        "athena_ready": ready,
        "verdict": "PASS" if ready else "HOLD",
        "structural_topology": "PASS",
        "organism_integration": "PARTIAL",
        "promotion": "HOLD",
    }


def communication_graph() -> dict[str, Any]:
    edges: list[dict[str, Any]] = []
    for organ in ORGANS:
        for dep in organ.get("depends_on", []):
            edges.append({"src": dep, "relation": "DEPENDS", "dst": organ["id"], "state": organ["state"]})
    edges.extend({k: v for k, v in item.items() if k != "id"} | {"transport_id": item["id"]} for item in TRANSPORTS)
    nodes = sorted({organ["id"] for organ in ORGANS})
    body = {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
    body["digest"] = digest(body)
    return body


def validate_topology() -> dict[str, Any]:
    all_seats = seats()
    graphs = {name: GRAPH_BUILDERS[name]() for name in GRAPH_BUILDERS}
    checks: list[dict[str, Any]] = []

    def check(identifier: str, observed: Any, expected: Any) -> None:
        checks.append({"id": identifier, "pass": observed == expected, "observed": observed, "expected": expected})

    check("SEAT_COUNT", len(all_seats), 144)
    check("UNIQUE_GID", len({s["gid"] for s in all_seats}), 144)
    check("UNIQUE_GRID", len({s["grid"] for s in all_seats}), 144)
    check("BAND_CENSUS", [sum(1 for s in all_seats if s["band"] == b[0]) for b in BANDS], [b[2] - b[1] + 1 for b in BANDS])
    check("GRID_ROUNDTRIP", all(gid_from_grid(*grid_from_gid(g)) == g for g in range(1, 145)), True)
    check("LEGACY_ROUNDTRIP", all(gid_from_legacy(legacy_factor(g)["s"], legacy_factor(g)["p"], legacy_factor(g)["q"]) == g for g in range(1, 145)), True)
    check("M12_ROUNDTRIP", all(gid_from_m12(m12_factor(g)["row_axis"], m12_factor(g)["row_phase"], m12_factor(g)["column_axis"], m12_factor(g)["column_phase"]) == g for g in range(1, 145)), True)
    check("MIRROR_INVOLUTION", all(145 - (145 - g) == g for g in range(1, 145)), True)
    check("MIRROR_FIXED_POINTS", sum(1 for g in range(1, 145) if 145 - g == g), 0)
    cursor = 1
    for _ in range(144):
        cursor = 1 if cursor == 144 else cursor + 1
    check("WHEEL_CLOSURE", cursor, 1)
    check("D4_R90_R270", all(d4_image(d4_image(g, "R90"), "R270") == g for g in range(1, 145)), True)
    for name, expected in GRAPH_EXPECTED_COUNTS.items():
        check(f"GRAPH_{name.upper()}_EDGE_COUNT", len(graphs[name]), expected)
    check("INVENTORY_GID_RANGE", all(1 <= item["gid"] <= 144 for item in static_inventory()), True)
    check("DATASET_IDS_UNIQUE", len({item["id"] for item in SOURCE_DATASETS}), len(SOURCE_DATASETS))
    check("ORGAN_IDS_UNIQUE", len({item["id"] for item in ORGANS}), len(ORGANS))
    passed = all(item["pass"] for item in checks)
    body = {
        "id": "KC144.TOPOLOGY.VALIDATION.1",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "passed": sum(1 for item in checks if item["pass"]),
        "total": len(checks),
        "boundary": "structural validation; not evidence, authority, integration, or promotion",
    }
    body["receipt_digest"] = digest(body)
    return body


def manifest(include_edges: bool = False) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": HUB_VERSION,
        "version": "1.0.0",
        "parent_runtime_sha": PARENT_RUNTIME_SHA,
        "full_aor_source_sha": FULL_AOR_SOURCE_SHA,
        "git_brain_source_sha": GIT_BRAIN_SOURCE_SHA,
        "authority": "SOURCE_BOUND_STRUCTURAL_READ_ONLY",
        "noncollapse_law": "GID!=object!=coordinate!=claim!=evidence!=authority; adjacency!=bridge; execution!=promotion",
        "census": {band: hi - lo + 1 for band, lo, hi, _role in BANDS},
        "census_equation": "6+16+21+37+10+15+27+12=144",
        "coordinates": [dict(item) for item in COORDINATE_SYSTEMS],
        "math": [dict(item) for item in MATH_OBJECTS],
        "seats": seats(),
        "graphs": [graph(name, include_edges=include_edges) for name in (*GRAPH_BUILDERS.keys(), "compiler_declared")],
        "organs": [dict(item) for item in ORGANS],
        "source_fibres": [dict(item) for item in SOURCE_FIBRES],
        "transports": [dict(item) for item in TRANSPORTS],
        "datasets": [dict(item) for item in SOURCE_DATASETS],
        "readiness": readiness(),
        "communication": communication_graph(),
        "return": {"from": "GID144", "to": "H01_PRIME", "state": "SUCCESSOR_SEED_ONLY_NOT_PRODUCTION_AUTHORITY"},
    }
    body["manifest_digest"] = digest(body)
    return body
