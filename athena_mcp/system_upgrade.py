from __future__ import annotations

import json
import time
from typing import Any, Iterable, Mapping

from .identity import digest, event_id
from .kc144_polyatlas import validate as validate_polyatlas
from .kc144_registry_pack import (
    PACK_SHA256,
    completion_frontier,
    query_registry,
    verify_pack,
)
from .runtime_truth import overlay_summary, transport_overlay_summary

SYSTEM_UPGRADE_VERSION = "ATHENA.SYSTEM.UPGRADE.1"
SYSTEM_RELEASE_VERSION = "ATHENA.SYSTEM.RELEASE.1"

SYSTEM_UPGRADE_SCHEMA = """
CREATE TABLE IF NOT EXISTS system_upgrade_runs(
 run_id TEXT PRIMARY KEY,
 objective TEXT NOT NULL,
 target_version TEXT NOT NULL,
 expected_git_head TEXT,
 actor TEXT NOT NULL,
 status TEXT NOT NULL,
 input_json TEXT NOT NULL,
 state_json TEXT NOT NULL,
 state_digest TEXT NOT NULL,
 plan_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_system_upgrade_runs_updated
 ON system_upgrade_runs(updated_at);
CREATE TABLE IF NOT EXISTS system_upgrade_events(
 upgrade_event_id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL,
 seq INTEGER NOT NULL,
 operation TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 previous_state_digest TEXT,
 state_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL,
 UNIQUE(run_id,seq)
);
CREATE INDEX IF NOT EXISTS idx_system_upgrade_events_run
 ON system_upgrade_events(run_id,seq);
CREATE TABLE IF NOT EXISTS system_release_certificates(
 certificate_id TEXT PRIMARY KEY,
 run_id TEXT NOT NULL,
 git_head TEXT NOT NULL,
 status TEXT NOT NULL,
 input_json TEXT NOT NULL,
 certificate_json TEXT NOT NULL,
 certificate_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_system_release_created
 ON system_release_certificates(created_at);
CREATE INDEX IF NOT EXISTS idx_system_release_head
 ON system_release_certificates(git_head);
"""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _state_digest(state: Mapping[str, Any]) -> str:
    body = {key: value for key, value in dict(state).items() if key != "state_digest"}
    return digest(body, 64)


def _status(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("status") or value.get("conclusion") or value.get("result")
    return str(value or "").strip().upper()


def _validate_witness(
    packet: Mapping[str, Any] | None,
    *,
    expected_head: str | None = None,
    require_exact_head: bool = False,
) -> dict[str, Any]:
    witness = dict(packet or {})
    defects: list[str] = []
    if witness.get("observed") is not True:
        defects.append("not_observed")
    if not str(witness.get("ref") or "").strip():
        defects.append("missing_ref")
    if witness.get("procedure") in (None, "", {}, []):
        defects.append("missing_procedure")
    if witness.get("observation") in (None, "", {}, []):
        defects.append("missing_observation")
    result = _status(witness.get("result") or witness.get("conclusion"))
    if result not in {"PASS", "SUCCESS", "SUCCEEDED"}:
        defects.append("result_not_pass")
    observed_head = str(witness.get("head_sha") or "").strip()
    if require_exact_head:
        if not expected_head:
            defects.append("run_has_no_expected_git_head")
        elif observed_head != expected_head:
            defects.append("head_mismatch")
    elif observed_head and expected_head and observed_head != expected_head:
        defects.append("head_mismatch")
    normalized = {
        "observed": witness.get("observed") is True,
        "ref": str(witness.get("ref") or "").strip() or None,
        "procedure": witness.get("procedure"),
        "observation": witness.get("observation"),
        "result": result or None,
        "head_sha": observed_head or None,
        "independence_key": witness.get("independence_key"),
        "metadata": witness.get("metadata") or {},
    }
    normalized["witness_digest"] = digest(normalized, 64)
    return {
        "status": "PASS" if not defects else "FAIL",
        "defects": defects,
        "witness": normalized,
        "boundary": (
            "A witness records supplied procedure, observation, result and provenance. "
            "Receipt integrity does not independently reproduce the external observation."
        ),
    }


def _gate(status: bool, evidence: Any, boundary: str) -> dict[str, Any]:
    return {
        "status": "PASS" if status else "FAIL",
        "evidence": evidence,
        "boundary": boundary,
    }


class SystemUpgradeRuntime:
    """Persistent whole-system upgrade, readiness and release-control plane."""

    def __init__(self, server: Any, integrity: Any | None = None) -> None:
        self.server = server
        self.integrity = integrity or server.aor_development.integrity
        self.s = server.store
        with self.s.db:
            self.s.db.executescript(SYSTEM_UPGRADE_SCHEMA)
        self.server.core.register(
            "TOOL",
            "SYSTEM",
            "UPGRADE",
            "COMPLETE_RUNTIME",
            "WITNESSED_CAS_LEDGER",
            {
                "objective": "string",
                "completion_witnesses": "procedure+observation+result+ref",
                "expected_state_digest": "sha256",
            },
            {
                "run_id": "UPGRUN",
                "state_digest": "sha256",
                "gate_matrix": "C/I/E/P/R/V/O/M/S/X",
                "frontier": "source-bound tasks",
                "release_certificate": "RELCERT",
            },
            constraints={
                "unknown_not_zero": True,
                "planning_not_execution": True,
                "witness_required_for_completion": True,
                "release_requires_exact_head_attestations": True,
            },
            actor="GENESIS.SYSTEM.UPGRADE.1",
            status="CANONICAL",
        )

    def describe(self) -> dict[str, Any]:
        return {
            "version": SYSTEM_UPGRADE_VERSION,
            "release_version": SYSTEM_RELEASE_VERSION,
            "mode": "PERSISTENT_WITNESSED_CAS",
            "source_task_pack": PACK_SHA256,
            "terminal_equation": "ATHENA_READY iff C&I&E&P&R&V&O&M&S&X all PASS",
            "authority_boundary": (
                "The upgrade ledger observes local runtime gates and supplied witnesses. "
                "It never converts plans, graph reachability, source repetition or CI metadata into semantic truth."
            ),
        }

    @staticmethod
    def _source_tasks() -> list[dict[str, Any]]:
        result = query_registry("completion", offset=0, limit=500)
        tasks = list(result.get("items") or [])
        tasks.sort(key=lambda item: (item.get("task_number", 10**9), str(item.get("task_id"))))
        return tasks

    @classmethod
    def _source_task_map(cls) -> dict[str, dict[str, Any]]:
        return {str(item["task_id"]): item for item in cls._source_tasks()}

    def _observed_surface(self) -> tuple[list[str], list[str]]:
        tools_response = self.server.handle(
            {"jsonrpc": "2.0", "id": "upgrade:tools", "method": "tools/list"}
        )
        resources_response = self.server.handle(
            {"jsonrpc": "2.0", "id": "upgrade:resources", "method": "resources/list"}
        )
        tools = [item["name"] for item in tools_response["result"]["tools"]]
        resources = [item["uri"] for item in resources_response["result"]["resources"]]
        return tools, resources

    def _sqlite_integrity(self) -> dict[str, Any]:
        try:
            rows = self.s.rows("PRAGMA integrity_check")
            values = [next(iter(row.values())) for row in rows]
            passed = values == ["ok"]
            return {"status": "PASS" if passed else "FAIL", "observed": values}
        except Exception as exc:
            return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}

    def local_snapshot(self, run_replay_samples: bool = True) -> dict[str, Any]:
        surface = self.integrity.surface_audit(True)
        foundation = self.integrity.state_foundation
        schema = foundation.schema.verify(
            foundation.CRITICAL_REQUIRED_TABLES, foundation.CRITICAL_REQUIRED_COLUMNS
        )
        self_test = self.integrity.self_test.run(
            10 if run_replay_samples else 1, True
        )
        startup = self.integrity.startup.evaluate(run_replay_samples)
        omega = self.integrity.state_foundation.call_tool("athena_omega_state", {})[1]
        registry = verify_pack(deep=True)
        polyatlas = validate_polyatlas(include_details=False)
        sqlite_integrity = self._sqlite_integrity()
        upgrade_tables = {
            "system_upgrade_runs",
            "system_upgrade_events",
            "system_release_certificates",
        }
        actual_tables = {
            str(row["name"])
            for row in self.s.rows(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        upgrade_schema = {
            "status": "PASS" if upgrade_tables.issubset(actual_tables) else "FAIL",
            "required_tables": sorted(upgrade_tables),
            "missing_tables": sorted(upgrade_tables - actual_tables),
        }
        tool_names, resource_uris = self._observed_surface()
        overlay = overlay_summary(tool_names, resource_uris)
        transports = transport_overlay_summary(tool_names, resource_uris)
        command_hub = getattr(self.server, "command_hub", None)
        if command_hub is None:
            hub_validation: dict[str, Any] = {
                "status": "N/A",
                "overall_status": "N/A",
                "reason": "base runtime has no KC144 command-hub overlay",
            }
        else:
            hub_validation = command_hub.validate()
        git = self.server.git.status()
        transport_benchmark = self.integrity.development.transport.benchmark()

        surface_groups = surface.get("groups") or {}
        live_required_organs = all(
            value.get("surface_pass") for value in overlay.get("organs", {}).values()
        )
        live_required_transports = all(
            value.get("surface_pass") for value in transports.get("transports", {}).values()
        )
        hub_ok = hub_validation.get("overall_status") in {"PASS", "N/A"}
        replay_ok = (self_test.get("gates") or {}).get("replay") == "PASS"
        omega_ok = bool(omega.get("omega_id") and omega.get("state_digest"))
        schema_ok = schema.get("status") == "PASS"
        surface_ok = surface.get("surface_status") == "PASS"
        composition_ok = (surface.get("composition") or {}).get("status") == "PASS"
        self_test_ok = self_test.get("status") == "PASS"
        startup_ok = startup.get("status") == "READY_LOCAL"
        registry_ok = registry.get("status") == "PASS"
        polyatlas_ok = polyatlas.get("status") == "PASS"
        sqlite_ok = sqlite_integrity.get("status") == "PASS"
        cycle_ok = (surface_groups.get("cycle") or {}).get("status") == "PASS"
        upgrade_surface_ok = (
            ((overlay.get("organs") or {}).get("ORGAN.SYSTEM_UPGRADE1") or {}).get("surface_pass")
            is True
        )
        transport_surface_ok = (surface_groups.get("transport") or {}).get("status") == "PASS"

        gates = {
            "C": _gate(
                surface_ok and upgrade_surface_ok,
                {
                    "surface": surface.get("surface_status"),
                    "system_upgrade_surface": "PASS" if upgrade_surface_ok else "FAIL",
                    "observed_tools": surface.get("observed_tool_count"),
                    "observed_resources": surface.get("observed_resource_count"),
                },
                "C certifies required capability discovery, not semantic correctness.",
            ),
            "I": _gate(
                composition_ok and live_required_organs,
                {
                    "composition": (surface.get("composition") or {}).get("status"),
                    "live_organs": overlay.get("live"),
                    "not_live_organs": overlay.get("not_live"),
                },
                "I certifies one composed runtime and live declared organs.",
            ),
            "E": _gate(
                cycle_ok and upgrade_surface_ok,
                {
                    "cycle_surface": (surface_groups.get("cycle") or {}).get("status"),
                    "upgrade_surface": "PASS" if upgrade_surface_ok else "FAIL",
                },
                "E certifies executable fail-closed control surfaces; planning remains distinct from execution.",
            ),
            "P": _gate(
                sqlite_ok and schema_ok and upgrade_schema.get("status") == "PASS",
                {
                    "sqlite": sqlite_integrity,
                    "schema": schema.get("status"),
                    "upgrade_schema": upgrade_schema,
                },
                "P certifies local ledger integrity and required persisted schema.",
            ),
            "R": _gate(
                replay_ok,
                {
                    "replay_gate": (self_test.get("gates") or {}).get("replay"),
                    "failures": self_test.get("replay_failures"),
                },
                "R certifies deterministic stored-receipt replay samples, not external-world repetition.",
            ),
            "V": _gate(
                self_test_ok and registry_ok and polyatlas_ok and hub_ok,
                {
                    "self_test": self_test.get("status"),
                    "registry": registry.get("status"),
                    "polyatlas": polyatlas.get("status"),
                    "hub": hub_validation.get("overall_status"),
                },
                "V certifies implemented local validation procedures and their observed results.",
            ),
            "O": _gate(
                omega_ok and startup_ok,
                {
                    "omega_id": omega.get("omega_id"),
                    "startup": startup.get("status"),
                },
                "O certifies observable accessible state; unseen external state remains UNKNOWN.",
            ),
            "M": _gate(
                schema_ok,
                {
                    "schema_version": schema.get("version"),
                    "up_to_date": schema.get("up_to_date"),
                    "missing_tables": schema.get("missing_required_tables"),
                    "missing_columns": schema.get("missing_required_columns"),
                },
                "M certifies additive migration currency and critical schema preservation.",
            ),
            "S": _gate(
                surface_ok
                and composition_ok
                and schema_ok
                and sqlite_ok
                and upgrade_schema.get("status") == "PASS",
                {
                    "surface": surface.get("surface_status"),
                    "composition": (surface.get("composition") or {}).get("status"),
                    "schema": schema.get("status"),
                    "sqlite": sqlite_integrity.get("status"),
                    "upgrade_schema": upgrade_schema.get("status"),
                },
                "S is the conjunctive structural/surface/composition/schema integrity gate.",
            ),
            "X": _gate(
                transport_surface_ok and live_required_transports,
                {
                    "transport_surface": (surface_groups.get("transport") or {}).get("status"),
                    "live_transports": transports.get("live"),
                    "not_live_transports": transports.get("not_live"),
                    "benchmark": transport_benchmark,
                },
                "X certifies explicit typed transport availability; transport output retains source authority ceilings.",
            ),
        }
        ready = all(value["status"] == "PASS" for value in gates.values())
        snapshot = {
            "version": SYSTEM_UPGRADE_VERSION,
            "captured_at": time.time(),
            "gate_matrix": gates,
            "gate_states": {key: value["status"] for key, value in gates.items()},
            "athena_ready_local": ready,
            "status": "READY_LOCAL" if ready else "HOLD_LOCAL",
            "surface": surface,
            "schema": schema,
            "self_test": self_test,
            "startup": startup,
            "omega": {
                "omega_id": omega.get("omega_id"),
                "state_digest": omega.get("state_digest"),
                "boundary": omega.get("boundary"),
            },
            "registry": registry,
            "polyatlas": polyatlas,
            "hub_validation": hub_validation,
            "runtime_organ_overlay": overlay,
            "runtime_transport_overlay": transports,
            "sqlite_integrity": sqlite_integrity,
            "upgrade_schema": upgrade_schema,
            "git": git,
            "boundary": (
                "READY_LOCAL is a measured local runtime condition. It is necessary but not sufficient "
                "for release, deployment, empirical truth, or exact-head external promotion."
            ),
        }
        snapshot["snapshot_digest"] = digest(
            {key: value for key, value in snapshot.items() if key not in {"captured_at", "snapshot_digest"}},
            64,
        )
        return snapshot

    def _frontier(self, completed: Iterable[str]) -> dict[str, Any]:
        return completion_frontier(completed_task_ids=sorted(set(completed)), limit=500)

    def _compose_state(
        self,
        *,
        run_id: str,
        objective: str,
        target_version: str,
        expected_git_head: str | None,
        completed: Mapping[str, Any],
        rejected: list[dict[str, Any]],
        local: Mapping[str, Any],
        seq: int,
    ) -> dict[str, Any]:
        frontier = self._frontier(completed)
        task_total = int(frontier.get("snapshot_task_count") or 0)
        completed_count = len(completed)
        local_ready = bool(local.get("athena_ready_local"))
        state = {
            "version": SYSTEM_UPGRADE_VERSION,
            "run_id": run_id,
            "objective": objective,
            "target_version": target_version,
            "expected_git_head": expected_git_head,
            "seq": seq,
            "status": "READY_LOCAL" if local_ready else "ACTIVE",
            "local": dict(local),
            "gate_matrix": dict(local.get("gate_matrix") or {}),
            "gate_states": dict(local.get("gate_states") or {}),
            "athena_ready_local": local_ready,
            "source_completion": {
                "completed": completed_count,
                "total": task_total,
                "fraction": (completed_count / task_total) if task_total else None,
                "complete": bool(task_total and completed_count == task_total),
                "completed_tasks": dict(completed),
                "rejected_observations": list(rejected),
            },
            "frontier": frontier,
            "return": {
                "coordinate": "KC144.V1::GID144::SSN12.M12",
                "successor": frontier.get("frontier", [None])[0] if frontier.get("frontier") else None,
            },
            "boundary": (
                "Source-task completion changes only through witnessed observations. "
                "Local readiness and source-snapshot completion are reported separately."
            ),
        }
        state["state_digest"] = _state_digest(state)
        return state

    def _emit(
        self,
        *,
        run_id: str,
        seq: int,
        operation: str,
        state: Mapping[str, Any],
        previous_state_digest: str | None,
        actor: str,
        extra: Mapping[str, Any] | None = None,
    ) -> str:
        payload = {
            "operation": operation,
            "run_id": run_id,
            "seq": seq,
            "previous_state_digest": previous_state_digest,
            "state": dict(state),
            "extra": dict(extra or {}),
        }
        parent = self.s.head("global")
        parent_eid = parent["eid"] if parent else None
        eid = event_id("SYSTEM_UPGRADE", actor, parent_eid, payload)
        event_digest = digest(payload, 32)
        upgrade_event_id = "UPGEV." + digest(
            {"run_id": run_id, "seq": seq, "operation": operation, "eid": eid}, 24
        )
        now = time.time()
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO system_upgrade_events VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    upgrade_event_id,
                    run_id,
                    seq,
                    operation,
                    _canonical(payload),
                    previous_state_digest,
                    state["state_digest"],
                    eid,
                    now,
                ),
            )
        self.s.put_event(eid, "SYSTEM_UPGRADE", actor, parent_eid, payload, event_digest)
        self.s.set_head("global", None, None, eid, event_digest)
        return eid

    def plan(
        self,
        objective: str,
        *,
        target_version: str = "2.6.0",
        expected_git_head: str | None = None,
        completion_witnesses: Iterable[Mapping[str, Any]] | None = None,
        actor: str = "agent",
        persist: bool = True,
    ) -> dict[str, Any]:
        objective = str(objective).strip()
        if not objective:
            raise ValueError("objective must be non-empty")
        target_version = str(target_version).strip()
        if not target_version:
            raise ValueError("target_version must be non-empty")
        expected_git_head = str(expected_git_head).strip() if expected_git_head else None
        task_map = self._source_task_map()
        completed: dict[str, Any] = {}
        rejected: list[dict[str, Any]] = []
        for item in completion_witnesses or []:
            item = dict(item)
            task_id = str(item.get("task_id") or "").strip()
            if task_id not in task_map:
                rejected.append({"task_id": task_id or None, "reason": "unknown_task_id"})
                continue
            witness = _validate_witness(
                item.get("witness"),
                expected_head=expected_git_head,
                require_exact_head=bool(item.get("require_exact_head", False)),
            )
            if witness["status"] != "PASS":
                rejected.append(
                    {"task_id": task_id, "reason": "invalid_witness", "witness": witness}
                )
                continue
            dependencies = set(task_map[task_id].get("dependencies") or [])
            if not dependencies.issubset(completed):
                rejected.append(
                    {
                        "task_id": task_id,
                        "reason": "dependencies_not_completed_in_import_order",
                        "missing_dependencies": sorted(dependencies - set(completed)),
                    }
                )
                continue
            completed[task_id] = {
                "task": task_map[task_id],
                "witness": witness["witness"],
                "observed_at": time.time(),
            }
        local = self.local_snapshot(run_replay_samples=True)
        parent = self.s.head("global")
        run_id = "UPGRUN." + digest(
            {
                "objective": objective,
                "target_version": target_version,
                "expected_git_head": expected_git_head,
                "parent_eid": parent["eid"] if parent else None,
                "created_ns": time.time_ns(),
            },
            24,
        )
        state = self._compose_state(
            run_id=run_id,
            objective=objective,
            target_version=target_version,
            expected_git_head=expected_git_head,
            completed=completed,
            rejected=rejected,
            local=local,
            seq=0,
        )
        inputs = {
            "objective": objective,
            "target_version": target_version,
            "expected_git_head": expected_git_head,
            "completion_witnesses": list(completion_witnesses or []),
            "source_pack_sha256": PACK_SHA256,
        }
        plan_digest = digest(
            {
                "objective": objective,
                "target_version": target_version,
                "expected_git_head": expected_git_head,
                "source_pack_sha256": PACK_SHA256,
                "accepted_task_ids": sorted(completed),
                "rejected": rejected,
            },
            64,
        )
        if not persist:
            return {
                **state,
                "persisted": False,
                "plan_digest": plan_digest,
                "input": inputs,
            }
        now = time.time()
        eid = self._emit(
            run_id=run_id,
            seq=0,
            operation="PLAN",
            state=state,
            previous_state_digest=None,
            actor=actor,
            extra={"plan_digest": plan_digest},
        )
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO system_upgrade_runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    objective,
                    target_version,
                    expected_git_head,
                    actor,
                    state["status"],
                    _canonical(inputs),
                    _canonical(state),
                    state["state_digest"],
                    plan_digest,
                    eid,
                    now,
                    now,
                ),
            )
        return {
            **state,
            "persisted": True,
            "plan_digest": plan_digest,
            "eid": eid,
        }

    def get(self, run_id: str) -> dict[str, Any]:
        row = self.s.one("SELECT * FROM system_upgrade_runs WHERE run_id=?", (run_id,))
        if not row:
            raise KeyError("unknown system upgrade run")
        result = dict(row)
        result["input"] = json.loads(result.pop("input_json"))
        result["state"] = json.loads(result.pop("state_json"))
        result["events"] = self.s.rows(
            "SELECT upgrade_event_id,seq,operation,previous_state_digest,state_digest,eid,created_at "
            "FROM system_upgrade_events WHERE run_id=? ORDER BY seq",
            (run_id,),
        )
        return result

    def state(self, run_id: str) -> dict[str, Any]:
        stored = self.get(run_id)
        return {
            **stored["state"],
            "plan_digest": stored["plan_digest"],
            "actor": stored["actor"],
            "created_at": stored["created_at"],
            "updated_at": stored["updated_at"],
            "events": stored["events"],
        }

    def _update_state(
        self,
        stored: Mapping[str, Any],
        state: Mapping[str, Any],
        *,
        operation: str,
        actor: str,
        extra: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        previous = str(stored["state_digest"])
        seq = int(state["seq"])
        eid = self._emit(
            run_id=str(stored["run_id"]),
            seq=seq,
            operation=operation,
            state=state,
            previous_state_digest=previous,
            actor=actor,
            extra=extra,
        )
        now = time.time()
        with self.s.db:
            self.s.db.execute(
                "UPDATE system_upgrade_runs SET status=?,state_json=?,state_digest=?,eid=?,updated_at=? "
                "WHERE run_id=? AND state_digest=?",
                (
                    state["status"],
                    _canonical(state),
                    state["state_digest"],
                    eid,
                    now,
                    stored["run_id"],
                    previous,
                ),
            )
            changed = self.s.db.execute("SELECT changes() n").fetchone()[0]
        if changed != 1:
            raise ValueError("STALE_UPGRADE_STATE")
        return {**state, "eid": eid, "updated_at": now}

    def observe(
        self,
        run_id: str,
        task_id: str,
        witness: Mapping[str, Any],
        expected_state_digest: str,
        *,
        require_exact_head: bool = False,
        refresh_local: bool = True,
        actor: str = "agent",
    ) -> dict[str, Any]:
        stored = self.get(run_id)
        if stored["state_digest"] != expected_state_digest:
            raise ValueError(
                f"STALE_UPGRADE_STATE expected={expected_state_digest} current={stored['state_digest']}"
            )
        task_map = self._source_task_map()
        task_id = str(task_id)
        if task_id not in task_map:
            raise KeyError("unknown completion task")
        current = dict(stored["state"])
        source = dict(current["source_completion"])
        completed = dict(source.get("completed_tasks") or {})
        if task_id in completed:
            return {
                **current,
                "idempotent": True,
                "observation": completed[task_id],
            }
        dependencies = set(task_map[task_id].get("dependencies") or [])
        missing = sorted(dependencies - set(completed))
        if missing:
            raise ValueError(f"TASK_BLOCKED missing_dependencies={missing}")
        checked = _validate_witness(
            witness,
            expected_head=current.get("expected_git_head"),
            require_exact_head=require_exact_head,
        )
        if checked["status"] != "PASS":
            raise ValueError(f"INVALID_WITNESS defects={checked['defects']}")
        completed[task_id] = {
            "task": task_map[task_id],
            "witness": checked["witness"],
            "observed_at": time.time(),
        }
        local = (
            self.local_snapshot(run_replay_samples=True)
            if refresh_local
            else dict(current["local"])
        )
        next_state = self._compose_state(
            run_id=run_id,
            objective=current["objective"],
            target_version=current["target_version"],
            expected_git_head=current.get("expected_git_head"),
            completed=completed,
            rejected=list(source.get("rejected_observations") or []),
            local=local,
            seq=int(current["seq"]) + 1,
        )
        return self._update_state(
            stored,
            next_state,
            operation="OBSERVE_TASK",
            actor=actor,
            extra={"task_id": task_id, "witness_digest": checked["witness"]["witness_digest"]},
        )

    def refresh(
        self,
        run_id: str,
        expected_state_digest: str,
        *,
        run_replay_samples: bool = True,
        actor: str = "agent",
    ) -> dict[str, Any]:
        stored = self.get(run_id)
        if stored["state_digest"] != expected_state_digest:
            raise ValueError(
                f"STALE_UPGRADE_STATE expected={expected_state_digest} current={stored['state_digest']}"
            )
        current = dict(stored["state"])
        source = dict(current["source_completion"])
        local = self.local_snapshot(run_replay_samples=run_replay_samples)
        next_state = self._compose_state(
            run_id=run_id,
            objective=current["objective"],
            target_version=current["target_version"],
            expected_git_head=current.get("expected_git_head"),
            completed=dict(source.get("completed_tasks") or {}),
            rejected=list(source.get("rejected_observations") or []),
            local=local,
            seq=int(current["seq"]) + 1,
        )
        return self._update_state(
            stored,
            next_state,
            operation="REFRESH_LOCAL_GATES",
            actor=actor,
            extra={"snapshot_digest": local.get("snapshot_digest")},
        )

    def replay(self, run_id: str) -> dict[str, Any]:
        stored = self.get(run_id)
        events = self.s.rows(
            "SELECT * FROM system_upgrade_events WHERE run_id=? ORDER BY seq",
            (run_id,),
        )
        defects: list[dict[str, Any]] = []
        previous: str | None = None
        final_digest: str | None = None
        for expected_seq, row in enumerate(events):
            payload = json.loads(row["payload_json"])
            state = payload.get("state") or {}
            recomputed = _state_digest(state)
            if int(row["seq"]) != expected_seq:
                defects.append(
                    {"seq": row["seq"], "defect": "non_contiguous_sequence", "expected": expected_seq}
                )
            if row["previous_state_digest"] != previous:
                defects.append(
                    {
                        "seq": row["seq"],
                        "defect": "previous_digest_mismatch",
                        "expected": previous,
                        "observed": row["previous_state_digest"],
                    }
                )
            if row["state_digest"] != recomputed:
                defects.append(
                    {
                        "seq": row["seq"],
                        "defect": "event_state_digest_mismatch",
                        "expected": row["state_digest"],
                        "observed": recomputed,
                    }
                )
            previous = row["state_digest"]
            final_digest = recomputed
        current_recomputed = _state_digest(stored["state"])
        if current_recomputed != stored["state_digest"]:
            defects.append(
                {
                    "defect": "current_state_digest_mismatch",
                    "expected": stored["state_digest"],
                    "observed": current_recomputed,
                }
            )
        if final_digest != stored["state_digest"]:
            defects.append(
                {
                    "defect": "event_chain_not_at_current_state",
                    "expected": stored["state_digest"],
                    "observed": final_digest,
                }
            )
        return {
            "version": SYSTEM_UPGRADE_VERSION,
            "run_id": run_id,
            "status": "REPLAY_MATCH" if not defects else "REPLAY_DIVERGED",
            "match": not defects,
            "event_count": len(events),
            "stored_state_digest": stored["state_digest"],
            "recomputed_state_digest": current_recomputed,
            "defects": defects,
            "boundary": (
                "Replay verifies frozen upgrade state and event-chain integrity. "
                "It does not re-perform external tests or observations."
            ),
        }

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        return self.s.rows(
            "SELECT run_id,objective,target_version,expected_git_head,actor,status,"
            "state_digest,plan_digest,eid,created_at,updated_at "
            "FROM system_upgrade_runs ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )

    def release_certificate(
        self,
        run_id: str,
        git_head: str,
        ci_witness: Mapping[str, Any],
        smoke_witness: Mapping[str, Any],
        *,
        require_source_completion: bool = False,
        actor: str = "agent",
        persist: bool = True,
    ) -> dict[str, Any]:
        stored = self.get(run_id)
        state = dict(stored["state"])
        git_head = str(git_head).strip()
        if not git_head:
            raise ValueError("git_head must be non-empty")
        expected = state.get("expected_git_head")
        expected_gate = {
            "status": "PASS" if not expected or expected == git_head else "FAIL",
            "expected": expected,
            "observed": git_head,
        }
        local = self.local_snapshot(run_replay_samples=True)
        promotion = self.integrity.promotion.evaluate(
            "Server",
            git_head,
            local["surface"],
            ci_witness,
            smoke_witness,
            self.server.git.status(),
            actor,
            persist,
        )
        source = state.get("source_completion") or {}
        source_gate = {
            "status": (
                "PASS"
                if not require_source_completion or source.get("complete") is True
                else "FAIL"
            ),
            "required": require_source_completion,
            "completed": source.get("completed"),
            "total": source.get("total"),
            "complete": source.get("complete"),
        }
        gates = {
            "local_runtime": {
                "status": "PASS" if local.get("athena_ready_local") else "FAIL",
                "gate_states": local.get("gate_states"),
                "snapshot_digest": local.get("snapshot_digest"),
            },
            "upgrade_replay": {
                "status": "PASS" if self.replay(run_id)["match"] else "FAIL",
            },
            "expected_head": expected_gate,
            "source_completion": source_gate,
            "promotion": {
                "status": "PASS" if promotion.get("status") == "QUALIFIED" else "FAIL",
                "promotion_status": promotion.get("status"),
                "promotion_run_id": promotion.get("run_id"),
                "decision_digest": promotion.get("decision_digest"),
            },
        }
        qualified = all(value["status"] == "PASS" for value in gates.values())
        certificate = {
            "version": SYSTEM_RELEASE_VERSION,
            "run_id": run_id,
            "git_head": git_head,
            "target_version": state.get("target_version"),
            "status": "QUALIFIED" if qualified else "BLOCKED",
            "release_allowed": qualified,
            "gates": gates,
            "local_snapshot": local,
            "source_task_pack": PACK_SHA256,
            "law": (
                "QUALIFIED iff local C/I/E/P/R/V/O/M/S/X all PASS, upgrade replay matches, "
                "expected head matches, optional source completion passes, and exact-head "
                "PROMOTION.1 CI+smoke witnesses qualify."
            ),
            "boundary": (
                "Release qualification is an exact-head integration certificate. "
                "It is not deployment, merge authority, empirical proof, or a claim that unresolved algorithms are true."
            ),
        }
        certificate_digest = digest(certificate, 64)
        if not persist:
            return {
                **certificate,
                "persisted": False,
                "certificate_digest": certificate_digest,
                "promotion": promotion,
            }
        parent = self.s.head("global")
        parent_eid = parent["eid"] if parent else None
        event_payload = {
            "operation": "SYSTEM_RELEASE_CERTIFICATE",
            "run_id": run_id,
            "git_head": git_head,
            "status": certificate["status"],
            "certificate_digest": certificate_digest,
        }
        eid = event_id("SYSTEM_RELEASE_CERTIFICATE", actor, parent_eid, event_payload)
        event_digest = digest(event_payload, 32)
        certificate_id = "RELCERT." + digest(
            {"run_id": run_id, "git_head": git_head, "certificate": certificate_digest}, 24
        )
        inputs = {
            "run_id": run_id,
            "git_head": git_head,
            "ci_witness": dict(ci_witness),
            "smoke_witness": dict(smoke_witness),
            "require_source_completion": require_source_completion,
        }
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO system_release_certificates VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    certificate_id,
                    run_id,
                    git_head,
                    certificate["status"],
                    _canonical(inputs),
                    _canonical(certificate),
                    certificate_digest,
                    eid,
                    time.time(),
                ),
            )
        self.s.put_event(
            eid,
            "SYSTEM_RELEASE_CERTIFICATE",
            actor,
            parent_eid,
            event_payload,
            event_digest,
        )
        self.s.set_head("global", None, None, eid, event_digest)
        return {
            **certificate,
            "persisted": True,
            "certificate_id": certificate_id,
            "certificate_digest": certificate_digest,
            "eid": eid,
            "promotion": promotion,
        }

    def release_get(self, certificate_id: str) -> dict[str, Any]:
        row = self.s.one(
            "SELECT * FROM system_release_certificates WHERE certificate_id=?",
            (certificate_id,),
        )
        if not row:
            raise KeyError("unknown system release certificate")
        result = dict(row)
        result["input"] = json.loads(result.pop("input_json"))
        result["certificate"] = json.loads(result.pop("certificate_json"))
        return result

    def release_replay(self, certificate_id: str) -> dict[str, Any]:
        stored = self.release_get(certificate_id)
        recomputed = digest(stored["certificate"], 64)
        upgrade_replay = self.replay(stored["run_id"])
        promotion_run_id = (
            ((stored["certificate"].get("gates") or {}).get("promotion") or {}).get(
                "promotion_run_id"
            )
        )
        promotion_replay = None
        if promotion_run_id:
            promotion_replay = self.integrity.promotion.replay(promotion_run_id)
        match = (
            recomputed == stored["certificate_digest"]
            and upgrade_replay["match"]
            and (promotion_replay is None or promotion_replay["match"])
        )
        return {
            "version": SYSTEM_RELEASE_VERSION,
            "certificate_id": certificate_id,
            "run_id": stored["run_id"],
            "git_head": stored["git_head"],
            "status": "REPLAY_MATCH" if match else "REPLAY_DIVERGED",
            "match": match,
            "stored_certificate_digest": stored["certificate_digest"],
            "recomputed_certificate_digest": recomputed,
            "upgrade_replay": upgrade_replay,
            "promotion_replay": promotion_replay,
            "boundary": (
                "Release replay verifies frozen certificate, upgrade and promotion receipt integrity; "
                "it does not independently contact GitHub Actions or reproduce smoke execution."
            ),
        }

    def release_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        return self.s.rows(
            "SELECT certificate_id,run_id,git_head,status,certificate_digest,eid,created_at "
            "FROM system_release_certificates ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

    def manifest(self) -> dict[str, Any]:
        tasks = self._source_tasks()
        result = {
            **self.describe(),
            "source_tasks": {
                "count": len(tasks),
                "first": tasks[0].get("task_id") if tasks else None,
                "last": tasks[-1].get("task_id") if tasks else None,
                "pack_sha256": PACK_SHA256,
            },
            "tables": [
                "system_upgrade_runs",
                "system_upgrade_events",
                "system_release_certificates",
            ],
            "tools": [
                "athena_system_upgrade_manifest",
                "athena_system_upgrade_plan",
                "athena_system_upgrade_state",
                "athena_system_upgrade_observe",
                "athena_system_upgrade_refresh",
                "athena_system_upgrade_replay",
                "athena_system_upgrade_recent",
                "athena_system_release_certificate",
                "athena_system_release_get",
                "athena_system_release_replay",
                "athena_system_release_recent",
            ],
            "resources": [
                "athena://system/upgrade",
                "athena://system/upgrade/frontier",
                "athena://system/release",
            ],
            "recent": self.recent(10),
            "release_recent": self.release_recent(10),
        }
        result["manifest_digest"] = digest(
            {key: value for key, value in result.items() if key != "manifest_digest"}, 64
        )
        return result

    def benchmark(self) -> dict[str, Any]:
        upgrade_runs = self.s.one("SELECT COUNT(*) n FROM system_upgrade_runs")["n"]
        upgrade_events = self.s.one("SELECT COUNT(*) n FROM system_upgrade_events")["n"]
        releases = self.s.one("SELECT COUNT(*) n FROM system_release_certificates")["n"]
        qualified = self.s.one(
            "SELECT COUNT(*) n FROM system_release_certificates WHERE status='QUALIFIED'"
        )["n"]
        return {
            "system_upgrade_version": SYSTEM_UPGRADE_VERSION,
            "system_release_version": SYSTEM_RELEASE_VERSION,
            "system_upgrade_runs": upgrade_runs,
            "system_upgrade_events": upgrade_events,
            "system_release_certificates": releases,
            "system_release_qualified": qualified,
            "system_release_blocked": releases - qualified,
        }
