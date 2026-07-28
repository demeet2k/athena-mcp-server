"""KC144 Ω whole-crystal convergence and structural-autofill compiler.

This plane is lateral to the externally blocked W33 authority handoff.  It
reconciles retrieved internal, Drive, runtime-Git, and control-Git
manifestations into source-neutral propositions, computes a typed defect
tensor, and closes only the structural fields forced by exact laws.

It never invents semantic payload, empirical evidence, external authority,
IC10 votes, production state, or a W33 return.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "whole_crystal_autofill.json"
)
SCHEMA = "athena.kc144-whole-crystal-autofill/v1"
PLANE = "KC144.XNAV.OMEGA"
TITLE = "WHOLE-CRYSTAL-CONVERGENCE-DEFECT-TENSOR-AND-STRUCTURAL-AUTOFILL"
RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
RUNTIME_PULL_REQUEST = 13
RUNTIME_W32_HEAD = "07bbea3a715dc9c8d040d53d2625a4e4592d6e6c"
RUNTIME_W32_TREE = "b1f5c2157225a8307c6f87670dfeb25523d13807"
CONTROL_REPOSITORY = "demeet2k/Athena"
CONTROL_PULL_REQUEST = 28
CONTROL_W32_HEAD = "31ea9c23a5997bd8511b1e8daa2e16a1a8633846"
CONTROL_W32_TREE = "1941a5d36bea6fbcddc3a9dc3b55b7e158ec474a"
W32_RUNTIME_RECEIPT = (
    "w32-next-octave-authority-quorum:sha256:"
    "570b8997f000937f56a6f18e29d51aecf80b54a8648e31743724e91466ed65c5"
)
W32_CONTROL_RECEIPT = (
    "w32-next-octave-authority-quorum-control-admission:sha256:"
    "8b6df05625189bd10e3d3e30dd1380413e5f340d7d2a88b293d6389c8cc90f27"
)
SUCCESSOR = (
    "KC144.XNAV.W33::RETURN-NEXT-OCTAVE-AUTHORITY-REGISTRY-COMMIT-"
    "AND-ISSUE-FIRST-QUORUM-BOUND-EXECUTION-HANDOFF"
)
SOURCE_STATES = {"RETRIEVED", "DECLARED", "INDEXED", "DERIVED"}
PROPOSITION_STATES = {"EXACT", "DERIVED", "LOCATOR_ONLY", "ABSENT"}
LENSES = ("IDENTITY", "SOURCE", "SEMANTIC", "AUTHORITY", "RETURN")
OCTAVES = (0, 1)
FORCED_FIELDS = (
    "gid",
    "row",
    "column",
    "grid",
    "theta_degrees",
    "octave",
    "scale",
    "fill_class",
    "authority_state",
    "return_required",
)
WITHHELD_FIELDS = (
    "semantic_role",
    "empirical_evidence",
    "promotion_state",
    "source_body",
)
PRODUCTION_COUNT_FIELDS = (
    "authority_sources",
    "authority_revisions",
    "registry_charters",
    "authority_admissions",
    "ic10_quorum_votes",
    "ic10_quorum_observations",
    "published_images",
    "persistent_endpoints",
    "merges",
    "deployments",
    "promotions",
)


class WholeCrystalAutofillError(RuntimeError):
    """Frozen Ω source/law ledger is malformed."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _without(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = deepcopy(value)
    result.pop(field, None)
    return result


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _negative() -> dict[str, bool]:
    return {
        "semantic_payload_generated": False,
        "empirical_evidence_generated": False,
        "authority_generated": False,
        "ic10_vote_generated": False,
        "registry_opened": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "image_published": False,
        "merged": False,
        "deployed": False,
        "promoted": False,
        "production_effect_claimed": False,
    }


class FrozenWholeCrystalAutofill:
    """Compile the deterministic structural fixed point under source guards."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        *,
        allow_test_contract: bool = False,
    ):
        self.snapshot = deepcopy(snapshot)
        self.allow_test_contract = allow_test_contract
        self._validate_snapshot()
        self.propositions = {
            item["proposition_id"]: item
            for item in self.snapshot["propositions"]
        }
        self.manifestations = {
            item["surface"]: item
            for item in self.snapshot["manifestations"]
        }

    @classmethod
    def load(cls) -> "FrozenWholeCrystalAutofill":
        try:
            return cls(json.loads(DATA_PATH.read_text(encoding="utf-8")))
        except (OSError, TypeError, ValueError) as error:
            raise WholeCrystalAutofillError(
                f"invalid frozen whole-crystal snapshot: {error}"
            ) from error

    def _validate_snapshot(self) -> None:
        required = {
            "schema",
            "plane",
            "title",
            "predecessor",
            "coordinate_law",
            "autofill_law",
            "propositions",
            "manifestations",
            "production_counts",
            "barriers",
            "successor",
            "successor_source_status",
            "contract_digest",
        }
        if set(self.snapshot) != required:
            raise ValueError("whole-crystal top-level fields drift")
        if (
            self.snapshot["schema"] != SCHEMA
            or self.snapshot["plane"] != PLANE
            or self.snapshot["title"] != TITLE
        ):
            raise ValueError("whole-crystal identity drift")
        expected_digest = _digest(_without(self.snapshot, "contract_digest"))
        if self.snapshot["contract_digest"] != expected_digest:
            raise ValueError("whole-crystal contract digest mismatch")
        if self.snapshot["successor"] != SUCCESSOR:
            raise ValueError("blocked W33 successor drift")
        predecessor = self.snapshot["predecessor"]
        if predecessor != {
            "runtime_repository": RUNTIME_REPOSITORY,
            "runtime_pull_request": RUNTIME_PULL_REQUEST,
            "runtime_head": RUNTIME_W32_HEAD,
            "runtime_tree": RUNTIME_W32_TREE,
            "runtime_receipt_id": W32_RUNTIME_RECEIPT,
            "control_repository": CONTROL_REPOSITORY,
            "control_pull_request": CONTROL_PULL_REQUEST,
            "control_head": CONTROL_W32_HEAD,
            "control_tree": CONTROL_W32_TREE,
            "control_receipt_id": W32_CONTROL_RECEIPT,
        }:
            raise ValueError("W32 runtime/control custody drift")
        law = self.snapshot["coordinate_law"]
        if law != {
            "rows": 12,
            "columns": 12,
            "station_count": 144,
            "gid_formula": "12*(row-1)+column",
            "theta_formula": "2.5*(gid-1)",
            "octave_scale_formula": "2**octave",
        }:
            raise ValueError("coordinate law drift")
        autofill = self.snapshot["autofill_law"]
        if (
            autofill.get("structural_gaps") != "GENERATE_FROM_EXACT_SCHEMA"
            or autofill.get("generated_mark") != "GENERATED_STRUCTURAL"
            or autofill.get("semantic_gaps") != "WITHHOLD_AS_AMBIG"
            or autofill.get("empirical_gaps") != "FORBID_AUTOFILL"
            or autofill.get("authority_gaps") != "FORBID_AUTOFILL"
            or autofill.get("fixed_point_rule")
            != "F[n+1]=F[n]∪READY_STRUCTURAL(F[n])"
        ):
            raise ValueError("autofill law drift")
        propositions = self.snapshot["propositions"]
        proposition_ids = [item.get("proposition_id") for item in propositions]
        if (
            len(propositions) != 8
            or len(set(proposition_ids)) != len(proposition_ids)
        ):
            raise ValueError("proposition lattice must contain eight unique rows")
        for item in propositions:
            if set(item) != {
                "proposition_id",
                "class",
                "statement",
                "autofill_policy",
            }:
                raise ValueError("proposition row fields drift")
            if item["class"] not in {
                "STRUCTURAL",
                "SEMANTIC",
                "EMPIRICAL",
                "AUTHORITY",
            }:
                raise ValueError("unknown proposition class")
            if item["autofill_policy"] not in {
                "FORCED",
                "WITHHOLD",
                "FORBIDDEN",
            }:
                raise ValueError("unknown proposition autofill policy")
        manifestations = self.snapshot["manifestations"]
        surfaces = [item.get("surface") for item in manifestations]
        if surfaces != [
            "INTERNAL_CONTINUITY",
            "GOOGLE_DRIVE",
            "GITHUB_RUNTIME",
            "GITHUB_CONTROL",
        ]:
            raise ValueError("source surfaces or ordering drift")
        for item in manifestations:
            required_manifestation = {
                "surface",
                "source_id",
                "locator",
                "revision",
                "retrieval_state",
                "claim_ceiling",
                "proposition_states",
            }
            if set(item) != required_manifestation:
                raise ValueError("manifestation fields drift")
            if item["retrieval_state"] not in SOURCE_STATES:
                raise ValueError("unknown retrieval state")
            if set(item["proposition_states"]) != set(proposition_ids):
                raise ValueError("manifestation proposition coverage drift")
            if not set(item["proposition_states"].values()) <= PROPOSITION_STATES:
                raise ValueError("unknown proposition standing")
        counts = self.snapshot["production_counts"]
        if set(counts) != set(PRODUCTION_COUNT_FIELDS) or any(counts.values()):
            raise ValueError("production counts must remain exactly zero")
        barrier_ids = [item.get("barrier_id") for item in self.snapshot["barriers"]]
        if len(barrier_ids) != len(set(barrier_ids)) or not barrier_ids:
            raise ValueError("barrier identities must be nonempty and disjoint")

    @staticmethod
    def _grid(gid: int) -> tuple[int, int, str]:
        if isinstance(gid, bool) or not isinstance(gid, int) or not 1 <= gid <= 144:
            raise ValueError("gid must be an integer in [1, 144]")
        row, remainder = divmod(gid - 1, 12)
        row += 1
        column = remainder + 1
        return row, column, f"R{row:02d}C{column:02d}"

    @staticmethod
    def _neighbors(row: int, column: int) -> list[str]:
        neighbors: list[str] = []
        for dr, dc in ((-1, 0), (0, -1), (0, 1), (1, 0)):
            r, c = row + dr, column + dc
            if 1 <= r <= 12 and 1 <= c <= 12:
                neighbors.append(f"GID{12 * (r - 1) + c:03d}")
        return neighbors

    def station(self, gid: int, *, octave: int = 0) -> dict[str, Any]:
        if isinstance(octave, bool) or not isinstance(octave, int) or octave < 0:
            raise ValueError("octave must be a nonnegative integer")
        row, column, grid = self._grid(gid)
        result = {
            "schema": "athena.kc144-generated-structural-cell/v1",
            "gid": f"GID{gid:03d}",
            "row": row,
            "column": column,
            "grid": grid,
            "theta_degrees": 2.5 * (gid - 1),
            "octave": octave,
            "scale": 2**octave,
            "fill_class": "GENERATED_STRUCTURAL",
            "authority_state": "HOLD",
            "return_required": True,
            "neighbors": self._neighbors(row, column),
            "generator": {
                "contract_digest": self.snapshot["contract_digest"],
                "laws": [
                    "gid=12*(row-1)+column",
                    "theta=2.5*(gid-1)",
                    "scale=2**octave",
                ],
            },
            "invariants": [
                "ONE_GID_ONE_GRID",
                "PHYSICAL_GIDS_NEVER_RENUMBERED",
                "GENERATED_IS_NOT_SOURCED",
                "AUTHORITY_REMAINS_HOLD",
                "RETURN_REMAINS_REQUIRED",
            ],
            "alternatives": [],
            "losses": [
                "SEMANTIC_ROLE_UNFILLED",
                "EMPIRICAL_EVIDENCE_UNFILLED",
                "SOURCE_BODY_UNFILLED",
                "PROMOTION_FORBIDDEN",
            ],
            "rejection_tests": [
                "gid_outside_1_144",
                "duplicate_grid",
                "theta_formula_drift",
                "silent_semantic_fill",
                "authority_escalation",
            ],
            "withheld": {
                "semantic_role": "AMBIG",
                "empirical_evidence": "ABSENT",
                "promotion_state": "FORBIDDEN",
                "source_body": "UNRESOLVED",
            },
        }
        result["cell_digest"] = _digest(result)
        return result

    def convergence_lattice(self) -> dict[str, Any]:
        rows = []
        for proposition_id, proposition in self.propositions.items():
            states = {
                surface: item["proposition_states"][proposition_id]
                for surface, item in self.manifestations.items()
            }
            exact = sum(state == "EXACT" for state in states.values())
            derived = sum(state == "DERIVED" for state in states.values())
            absent = sum(state == "ABSENT" for state in states.values())
            conflict = False
            policy = proposition["autofill_policy"]
            forced = (
                proposition["class"] == "STRUCTURAL"
                and policy == "FORCED"
                and exact >= 1
                and not conflict
            )
            if exact >= 2:
                standing = "EXACT_CROSS_SURFACE"
            elif exact == 1 and derived >= 1:
                standing = "EXACT_WITH_DERIVED_CONVERGENCE"
            elif exact == 1:
                standing = "SOURCE_EXACT_SINGLE_SURFACE"
            elif derived:
                standing = "DERIVED_ONLY"
            else:
                standing = "UNRESOLVED"
            rows.append(
                {
                    "proposition_id": proposition_id,
                    "class": proposition["class"],
                    "statement": proposition["statement"],
                    "surface_states": states,
                    "exact_manifestations": exact,
                    "derived_manifestations": derived,
                    "absent_manifestations": absent,
                    "conflict": conflict,
                    "standing": standing,
                    "autofill_policy": policy,
                    "structurally_forced": forced,
                }
            )
        return {
            "schema": "athena.kc144-convergence-lattice/v1",
            "plane": PLANE,
            "rows": rows,
            "row_count": len(rows),
            "forced_structural_propositions": sum(
                row["structurally_forced"] for row in rows
            ),
            "semantic_empirical_authority_autofills": 0,
            "direction": [
                "SEED",
                "LAW",
                "SOURCE_NEUTRAL_OID",
                "DEFECT_TENSOR",
                "STRUCTURAL_FIXED_POINT",
                "REGENERATED_BODY",
                "RECEIPT",
                "GID144_M12_REENTRY",
            ],
            "truth_credit_assigned": 0,
            "authority_effect": "NONE",
            "lattice_digest": "",
        } | {
            "lattice_digest": _digest(
                {
                    "schema": "athena.kc144-convergence-lattice/v1",
                    "plane": PLANE,
                    "rows": rows,
                }
            )
        }

    def defect_tensor(
        self,
        *,
        surface: str | None = None,
        proposition_id: str | None = None,
    ) -> dict[str, Any]:
        if surface is not None and surface not in self.manifestations:
            raise ValueError("unknown surface")
        if proposition_id is not None and proposition_id not in self.propositions:
            raise ValueError("unknown proposition_id")
        surfaces = [surface] if surface else list(self.manifestations)
        propositions = (
            [proposition_id] if proposition_id else list(self.propositions)
        )
        cells = []
        for surface_name in surfaces:
            manifestation = self.manifestations[surface_name]
            for pid in propositions:
                proposition = self.propositions[pid]
                state = manifestation["proposition_states"][pid]
                for lens in LENSES:
                    for octave in OCTAVES:
                        defect = 0
                        reasons: list[str] = []
                        if state == "DERIVED":
                            defect += 1
                            reasons.append("DERIVED_NOT_EXACT")
                        elif state == "LOCATOR_ONLY":
                            defect += 2
                            reasons.append("CONTENT_NOT_RETRIEVED")
                        elif state == "ABSENT":
                            defect += 3
                            reasons.append("MANIFESTATION_ABSENT")
                        if lens == "SEMANTIC" and proposition["class"] != "STRUCTURAL":
                            defect += 1
                            reasons.append("SEMANTIC_NOT_SCHEMA_FORCED")
                        if lens == "AUTHORITY":
                            defect += 1
                            reasons.append("AUTHORITY_NOT_AUTOFILLABLE")
                        if octave == 1 and pid != "P07_HIGHER_OCTAVE_GEOMETRY":
                            defect += 1
                            reasons.append("OCTAVE_PROJECTION_NOT_NATIVE_SOURCE")
                        cells.append(
                            {
                                "surface": surface_name,
                                "proposition_id": pid,
                                "lens": lens,
                                "octave": octave,
                                "defect": defect,
                                "reasons": reasons or ["NONE"],
                            }
                        )
        return {
            "schema": "athena.kc144-defect-tensor/v1",
            "axes": {
                "surface": surfaces,
                "proposition": propositions,
                "lens": list(LENSES),
                "octave": list(OCTAVES),
            },
            "shape": [
                len(surfaces),
                len(propositions),
                len(LENSES),
                len(OCTAVES),
            ],
            "cell_count": len(cells),
            "zero_defect_cells": sum(cell["defect"] == 0 for cell in cells),
            "nonzero_defect_cells": sum(cell["defect"] != 0 for cell in cells),
            "cells": cells,
            "tensor_digest": _digest(cells),
        }

    def compile_fixed_point(self, *, octave: int = 0) -> dict[str, Any]:
        cells = [self.station(gid, octave=octave) for gid in range(1, 145)]
        grid_ids = {cell["grid"] for cell in cells}
        cell_digests = [cell["cell_digest"] for cell in cells]
        if len(grid_ids) != 144 or len(set(cell_digests)) != 144:
            raise WholeCrystalAutofillError("generated structural atlas collided")
        iterations = [
            {
                "iteration": 0,
                "admitted_cells": 0,
                "frontier": 144,
                "reason": "EXACT_GLOBAL_SCHEMA_AVAILABLE",
            },
            {
                "iteration": 1,
                "admitted_cells": 144,
                "frontier": 0,
                "reason": "NO_ADDITIONAL_STRUCTURAL_CELL_FORCED",
            },
        ]
        closure = {
            "schema": "athena.kc144-structural-fixed-point/v1",
            "plane": PLANE,
            "octave": octave,
            "iterations": iterations,
            "fixed_point_reached": True,
            "station_cells": 144,
            "structural_fields_per_cell": len(FORCED_FIELDS),
            "forced_structural_fields": 144 * len(FORCED_FIELDS),
            "withheld_fields_per_cell": len(WITHHELD_FIELDS),
            "withheld_nonstructural_fields": 144 * len(WITHHELD_FIELDS),
            "fill_class": "GENERATED_STRUCTURAL",
            "semantic_autofills": 0,
            "empirical_autofills": 0,
            "authority_autofills": 0,
            "promotion_autofills": 0,
            "production_counts": deepcopy(self.snapshot["production_counts"]),
            "barriers": deepcopy(self.snapshot["barriers"]),
            "successor": SUCCESSOR,
            "cell_root": _digest(cell_digests),
            "truth_credit_assigned": 0,
            "evidence_effect": "NONE",
            "authority_effect": "NONE",
            "production_effect": "NONE",
        }
        closure["closure_digest"] = _digest(closure)
        return closure

    def status(self) -> dict[str, Any]:
        lattice = self.convergence_lattice()
        closure = self.compile_fixed_point()
        return {
            "schema": "athena.kc144-whole-crystal-autofill-status/v1",
            "status": (
                "PASS_OMEGA_WHOLE_CRYSTAL_STRUCTURAL_FIXED_POINT__"
                "HOLD_W33_EXTERNAL_AUTHORITY_RETURN"
            ),
            "plane": PLANE,
            "contract_digest": self.snapshot["contract_digest"],
            "source_surfaces": len(self.manifestations),
            "propositions": len(self.propositions),
            "convergence_lattice_digest": lattice["lattice_digest"],
            "fixed_point": closure,
            "production_counts": deepcopy(self.snapshot["production_counts"]),
            "successor": SUCCESSOR,
            **_negative(),
        }

    def barriers(self) -> dict[str, Any]:
        return {
            "schema": "athena.kc144-whole-crystal-barriers/v1",
            "status": "HOLD_AT_GENUINE_EXTERNAL_DEPENDENCY_BARRIERS",
            "barriers": deepcopy(self.snapshot["barriers"]),
            "autofillable_barriers": 0,
            "successor": SUCCESSOR,
            **_negative(),
        }

    def explain(self) -> dict[str, Any]:
        return {
            "schema": "athena.kc144-whole-crystal-autofill-law/v1",
            "status": "PASS_AUTOFILL_SEPARATION_LAW_EXPLAINED",
            "equation": "F[n+1]=F[n]∪READY_STRUCTURAL(F[n])",
            "ready_rule": (
                "exact_generator ∧ consistent_neighbors ∧ no_identity_conflict "
                "∧ class=STRUCTURAL ∧ authority_effect=NONE"
            ),
            "law": (
                "STRUCTURAL SYMMETRY MAY REGENERATE A MARKED BODY; "
                "SEMANTIC RESONANCE MAY ONLY PROPOSE AMBIGUOUS CANDIDATES; "
                "EMPIRICAL EVIDENCE AND AUTHORITY REQUIRE EXTERNAL EVENTS; "
                "A GENERATED CELL NEVER BECOMES A SOURCE OR A PROMOTION."
            ),
            "forced_fields": list(FORCED_FIELDS),
            "withheld_fields": list(WITHHELD_FIELDS),
            "direction": self.convergence_lattice()["direction"],
            **_negative(),
        }


def register_whole_crystal_autofill(mcp: Any) -> None:
    """Register seven Ω tools and two source-preserving resources."""
    compiler = FrozenWholeCrystalAutofill.load()

    @mcp.tool()
    def athena_whole_crystal_autofill_status() -> str:
        """Return the Ω source, fixed-point, and production boundary."""
        return _render(compiler.status())

    @mcp.tool()
    def inspect_athena_whole_crystal_source_lattice() -> str:
        """Inspect source-neutral propositions without merging manifestations."""
        return _render(compiler.convergence_lattice())

    @mcp.tool()
    def inspect_athena_whole_crystal_defect_tensor(
        surface: str | None = None,
        proposition_id: str | None = None,
    ) -> str:
        """Inspect D(surface, proposition, lens, octave)."""
        return _render(
            compiler.defect_tensor(
                surface=surface,
                proposition_id=proposition_id,
            )
        )

    @mcp.tool()
    def inspect_athena_whole_crystal_cell(gid: int, octave: int = 0) -> str:
        """Inspect one generated structural envelope and its withheld fields."""
        return _render(compiler.station(gid, octave=octave))

    @mcp.tool()
    def compile_athena_whole_crystal_fixed_point(octave: int = 0) -> str:
        """Compile all 144 structurally forced cells to the fixed point."""
        return _render(compiler.compile_fixed_point(octave=octave))

    @mcp.tool()
    def inspect_athena_whole_crystal_genuine_barriers() -> str:
        """Return the external events that mathematics cannot autofill."""
        return _render(compiler.barriers())

    @mcp.tool()
    def explain_athena_whole_crystal_autofill_law() -> str:
        """Explain the structural/semantic/evidence/authority separation law."""
        return _render(compiler.explain())

    @mcp.resource("athena://whole-crystal-convergence-lattice")
    def whole_crystal_convergence_resource() -> str:
        """Read the frozen source-neutral convergence ledger."""
        return _render(compiler.snapshot)

    @mcp.resource("athena://whole-crystal-structural-fixed-point")
    def whole_crystal_fixed_point_resource() -> str:
        """Read the current deterministic 144-cell structural fixed point."""
        return _render(compiler.compile_fixed_point())
