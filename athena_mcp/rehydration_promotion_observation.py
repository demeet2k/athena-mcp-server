from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .github_promotion_verifier import GithubPromotionVerifier
from .promotion import PromotionLedger
from .rehydration_loop import RehydrationLoopRuntime

ARTIFACT = "ATHENA.REHYDRATION.PROMOTION.OBSERVATION.V1_2"
TOOL_NAME = "athena_rehydration_promotion_observe"
TARGET_MODES = {"CURRENT_GIT", "CYCLE_WORK", "LOOP_CHECKPOINT", "EXPLICIT"}


def _row_dict(row: Any) -> dict:
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except Exception:
        return {}


@dataclass(frozen=True)
class PromotionTarget:
    mode: str
    head: str
    current_git_head: str | None
    cycle_work_head: str | None
    loop_checkpoint_head: str | None

    def body(self) -> dict:
        return {
            "mode": self.mode,
            "head": self.head,
            "current_git_head": self.current_git_head,
            "cycle_work_head": self.cycle_work_head,
            "loop_checkpoint_head": self.loop_checkpoint_head,
        }


class RehydrationPromotionObserver:
    """Read-only exact-head promotion observation for one rehydration loop.

    This membrane may read PromotionLedger receipts and independently observe the
    host GitHub check-suite verifier. It intentionally has no call path to
    PromotionLedger.evaluate, merge, release, or deployment authority.
    """

    def __init__(
        self,
        *,
        git,
        loop: RehydrationLoopRuntime,
        promotion: PromotionLedger,
        verifier: GithubPromotionVerifier,
    ):
        self.git = git
        self.loop = loop
        self.promotion = promotion
        self.verifier = verifier

    def _verify_loop_local(self, loop_id: str) -> dict:
        # Public verify may be wrapped by the shared-fresh membrane. This observer
        # already reports current Git coordinates and never upgrades authority, so
        # use DISABLED only to replay the local persisted causal chain.
        try:
            return self.loop.verify(loop_id, shared_remote_mode="DISABLED")
        except TypeError:
            return self.loop.verify(loop_id)

    def _loop_snapshot(self, loop_id: str) -> dict:
        state, paths = self.loop._read_state(loop_id)
        checkpoint = self.loop._path_last_commit(paths["state"])
        current = self.git.head() if getattr(self.git, "enabled", False) else None
        receipt = None
        receipt_path = None
        if state.get("receipt_paths"):
            receipt_path = state["receipt_paths"][-1]
            try:
                receipt = self.loop._read_json(receipt_path)
            except Exception as exc:
                receipt = {"_read_error": f"{type(exc).__name__}:{exc}"}
        completion = (receipt or {}).get("completion") if isinstance(receipt, dict) else None
        completion = completion if isinstance(completion, dict) else {}
        control = completion.get("_rehydration_control")
        control = control if isinstance(control, dict) else {}
        cycle_gate = control.get("cycle_gate") if isinstance(control.get("cycle_gate"), dict) else None
        routing = completion.get("successor_baton") if isinstance(completion.get("successor_baton"), dict) else None
        return {
            "loop_id": loop_id,
            "loop_status": state.get("status"),
            "step_index": state.get("step_index"),
            "state_digest": state.get("state_digest"),
            "chain_digest": state.get("chain_digest"),
            "current_git_head": current,
            "loop_checkpoint_head": checkpoint,
            "cycle_work_head": (receipt or {}).get("work_head") if isinstance(receipt, dict) else None,
            "receipt_path": receipt_path,
            "receipt_digest": (receipt or {}).get("receipt_digest") if isinstance(receipt, dict) else None,
            "cycle_gate": cycle_gate,
            "routing_successor": routing,
            "loop_verification": self._verify_loop_local(loop_id),
        }

    @staticmethod
    def _resolve_target(snapshot: dict, mode: str, explicit_head: str | None) -> PromotionTarget:
        mode = str(mode or "CURRENT_GIT").upper()
        if mode not in TARGET_MODES:
            raise ValueError(f"target_head_mode must be one of {sorted(TARGET_MODES)}")
        if mode == "CURRENT_GIT":
            head = snapshot.get("current_git_head")
        elif mode == "CYCLE_WORK":
            head = snapshot.get("cycle_work_head")
        elif mode == "LOOP_CHECKPOINT":
            head = snapshot.get("loop_checkpoint_head")
        else:
            head = str(explicit_head or "").strip() or None
        if not head:
            raise ValueError(f"target head unavailable for mode {mode}")
        return PromotionTarget(
            mode=mode,
            head=str(head),
            current_git_head=snapshot.get("current_git_head"),
            cycle_work_head=snapshot.get("cycle_work_head"),
            loop_checkpoint_head=snapshot.get("loop_checkpoint_head"),
        )

    def _runs_for_head(self, git_head: str, limit: int) -> list[dict]:
        limit = max(1, min(int(limit), 100))
        rows = self.promotion.s.rows(
            "SELECT run_id,candidate_server,git_head,status,decision_digest,eid,created_at "
            "FROM promotion_runs WHERE git_head=? ORDER BY created_at DESC LIMIT ?",
            (git_head, limit),
        )
        result = []
        for raw in rows:
            row = _row_dict(raw)
            run_id = row.get("run_id")
            try:
                replay = self.promotion.replay(run_id)
            except Exception as exc:
                replay = {
                    "run_id": run_id,
                    "status": "REPLAY_ERROR",
                    "match": False,
                    "detail": f"{type(exc).__name__}:{exc}",
                }
            result.append({**row, "replay": replay})
        return result

    @staticmethod
    def _persisted_standing(runs: list[dict]) -> dict:
        if not runs:
            return {
                "status": "UNOBSERVED",
                "latest_status": None,
                "valid_statuses": [],
                "qualified_run_ids": [],
                "contested": False,
            }
        valid = [row for row in runs if (row.get("replay") or {}).get("match") is True]
        if not valid:
            return {
                "status": "REPLAY_HOLD",
                "latest_status": runs[0].get("status"),
                "valid_statuses": [],
                "qualified_run_ids": [],
                "contested": False,
            }
        statuses = sorted({str(row.get("status")) for row in valid})
        contested = len(statuses) > 1
        return {
            "status": "CONTESTED" if contested else statuses[0],
            "latest_status": valid[0].get("status"),
            "valid_statuses": statuses,
            "qualified_run_ids": [row.get("run_id") for row in valid if row.get("status") == "QUALIFIED"],
            "contested": contested,
        }

    @staticmethod
    def _observation_status(loop_verification: dict, standing: dict, external: dict) -> str:
        if str(loop_verification.get("status")) not in {"PASS", "PASS_UNVERIFIED"}:
            return "LOOP_INTEGRITY_HOLD"
        if standing.get("status") == "CONTESTED":
            return "PROMOTION_CONTESTED"
        if standing.get("status") == "QUALIFIED":
            return "PERSISTED_QUALIFIED_OBSERVED"
        if standing.get("status") == "ATTESTED_READY":
            return "ATTESTED_READY_OBSERVED"
        if standing.get("status") == "BLOCKED":
            return "PROMOTION_BLOCKED_OBSERVED"
        if external.get("verified") is True:
            return "CHECKS_VERIFIED_PROMOTION_UNQUALIFIED"
        if standing.get("status") == "REPLAY_HOLD":
            return "PROMOTION_REPLAY_HOLD"
        return "PROMOTION_UNOBSERVED"

    def observe(
        self,
        *,
        loop_id: str,
        target_head_mode: str = "CURRENT_GIT",
        explicit_head: str | None = None,
        check_external: bool = True,
        run_limit: int = 20,
        timeout_s: float = 12.0,
    ) -> dict:
        snapshot = self._loop_snapshot(loop_id)
        target = self._resolve_target(snapshot, target_head_mode, explicit_head)
        runs = self._runs_for_head(target.head, run_limit)
        standing = self._persisted_standing(runs)
        if check_external:
            external = self.verifier.verify(target.head, timeout_s)
        else:
            external = {
                "version": "ATHENA.GITHUB.PROMOTION.VERIFIER.1",
                "status": "DISABLED",
                "verified": False,
                "head_sha": target.head,
            }
        status = self._observation_status(snapshot["loop_verification"], standing, external)
        return {
            "artifact": ARTIFACT,
            "status": status,
            "loop": snapshot,
            "promotion_target": target.body(),
            "persisted_promotion": {
                "standing": standing,
                "runs": runs,
                "count": len(runs),
                "source": "PROMOTION.2_LEDGER_READ_ONLY",
            },
            "external_checks": external,
            "authority": {
                "mode": "OBSERVATION_ONLY",
                "may_evaluate_promotion": False,
                "may_persist_promrun": False,
                "may_merge": False,
                "may_release": False,
                "may_deploy": False,
            },
            "laws": [
                "REHYDRATION_MAY_OBSERVE_PROMOTION_BUT_MAY_NOT_GRANT_PROMOTION",
                "CHECKS_VERIFIED != PROMOTION_QUALIFIED",
                "PROMOTION_RUN != MERGE_AUTHORITY",
                "EXACT_HEAD_IDENTITY_IS_EXPLICIT_NOT_INFERRED",
                "CONTESTED_PROMRUNS_REMAIN_CONTESTED",
                "REPLAY_MATCH != EXTERNAL_REVERIFICATION",
            ],
        }

    def call_tool(self, name: str, args: dict):
        if name != TOOL_NAME:
            return False, None
        return True, self.observe(
            loop_id=args["loop_id"],
            target_head_mode=args.get("target_head_mode", "CURRENT_GIT"),
            explicit_head=args.get("explicit_head"),
            check_external=args.get("check_external", True),
            run_limit=args.get("run_limit", 20),
            timeout_s=args.get("timeout_s", 12.0),
        )


REHYDRATION_PROMOTION_OBSERVATION_TOOLS = [
    {
        "name": TOOL_NAME,
        "description": (
            "Read-only promotion observation for a rehydration loop. Binds loop/cycle coordinates to an explicit target Git head, "
            "reads persisted PROMOTION.2 runs for that exact head, replays their frozen predicates, and optionally asks the host-bound "
            "GitHub verifier whether one coherent required check-suite is currently verified. Never evaluates/persists promotion and never merges/releases."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["loop_id"],
            "properties": {
                "loop_id": {"type": "string"},
                "target_head_mode": {"type": "string", "enum": sorted(TARGET_MODES)},
                "explicit_head": {"type": ["string", "null"]},
                "check_external": {"type": "boolean"},
                "run_limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "timeout_s": {"type": "number", "minimum": 1, "maximum": 60},
            },
            "additionalProperties": False,
        },
    }
]
REHYDRATION_PROMOTION_OBSERVATION_TOOL_NAMES = {TOOL_NAME}
