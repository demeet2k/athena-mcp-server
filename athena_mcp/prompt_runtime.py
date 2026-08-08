from __future__ import annotations

from typing import Any, Dict, Mapping

from .prompt_runtime_compile import PromptRuntimeCompileMixin
from .prompt_runtime_git import PromptRuntimeGit
from .prompt_runtime_promotion import PromptRuntimePromotionMixin
from .prompt_runtime_proposal import PromptRuntimeProposalMixin
from .prompt_runtime_records import PromptRuntimeRecordsMixin
from .prompt_runtime_selection import PromptRuntimeSelectionMixin
from .prompt_runtime_types import AUTHORITY_LAW, PROMPT_RESOURCE_URI, PROMPT_RUNTIME_VERSION


class PromptRuntimeSurface(
    PromptRuntimePromotionMixin,
    PromptRuntimeProposalMixin,
    PromptRuntimeSelectionMixin,
    PromptRuntimeCompileMixin,
    PromptRuntimeRecordsMixin,
    PromptRuntimeGit,
):
    """Executable Git-brain prompt runtime under an explicit authority ceiling."""

    def status(self) -> Dict[str, Any]:
        if not self.configured:
            return {
                "version": PROMPT_RUNTIME_VERSION,
                "configured": False,
                "status": "UNAVAILABLE",
                "required_configuration": "ATHENA_GIT_ROOT",
                "authority_law": AUTHORITY_LAW,
            }
        try:
            snapshot = self.hydrate()
        except Exception as exc:
            return {
                "version": PROMPT_RUNTIME_VERSION,
                "configured": True,
                "status": "DEGRADED",
                "error": str(exc),
                "git": self.server.git.status(),
                "authority_law": AUTHORITY_LAW,
            }
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "configured": True,
            "status": "READY",
            "git": snapshot["git"],
            "profile": snapshot["profile"],
            "stack_digest": snapshot["stack_digest"],
            "source_capsule_digest": snapshot["source_capsule"]["capsule_digest"],
            "frontier_refs": snapshot.get("frontier_refs"),
            "tool_contract": [
                "athena_prompt_hydrate",
                "athena_prompt_compile",
                "athena_prompt_freshness",
                "athena_prompt_propose",
                "athena_prompt_experiment",
                "athena_prompt_activate",
                "athena_prompt_promote",
            ],
            "authority_law": AUTHORITY_LAW,
            "non_goals": [
                "remote repository fetch",
                "automatic self-promotion",
                "host instruction mutation",
                "automatic push/deploy",
                "experiment-to-observation fabrication",
                "filename-inferred goal or pressure authority",
            ],
        }

    def call_tool(self, name: str, args: Mapping[str, Any]):
        if name == "athena_prompt_hydrate":
            return True, self.hydrate(
                profile=args.get("profile"),
                scope=args.get("scope"),
                include_text=bool(args.get("include_text", False)),
                since_git_head=args.get("since_git_head"),
                task=args.get("task"),
            )
        if name == "athena_prompt_compile":
            return True, self.compile(
                profile=args.get("profile"),
                scope=args.get("scope"),
                task_overlay=args.get("task_overlay"),
                since_git_head=args.get("since_git_head"),
                task=args.get("task"),
            )
        if name == "athena_prompt_freshness":
            return True, self.freshness(last_git_head=args["last_git_head"])
        if name == "athena_prompt_propose":
            return True, self.propose(
                expected_git_head=args["expected_git_head"],
                module_id=args["module_id"],
                version=args["version"],
                scope=args["scope"],
                content=args["content"],
                defect=args["defect"],
                expected_effect=args["expected_effect"],
                metrics=args["metrics"],
                tests=args["tests"],
                rollback=args["rollback"],
                depends_on=args.get("depends_on"),
                triggers=args.get("triggers"),
                actor=args.get("actor", "agent"),
            )
        if name == "athena_prompt_experiment":
            return True, self.experiment(
                expected_git_head=args["expected_git_head"],
                experiment_id=args["experiment_id"],
                candidate_path=args["candidate_path"],
                hypothesis=args["hypothesis"],
                protocol=args["protocol"],
                result_status=args["result_status"],
                observations=args.get("observations"),
                witness=args.get("witness"),
                actor=args.get("actor", "agent"),
            )
        if name == "athena_prompt_activate":
            return True, self.activate(
                expected_git_head=args["expected_git_head"],
                candidate_path=args["candidate_path"],
                scope=args["scope"],
                experiment_refs=args["experiment_refs"],
                witness=args["witness"],
                expires_at=args.get("expires_at"),
                actor=args.get("actor", "agent"),
            )
        if name == "athena_prompt_promote":
            return True, self.promote(
                expected_git_head=args["expected_git_head"],
                candidate_path=args["candidate_path"],
                target_module_id=args["target_module_id"],
                experiment_refs=args["experiment_refs"],
                evidence_refs=args["evidence_refs"],
                witness=args["witness"],
                actor=args.get("actor", "agent"),
            )
        return False, None

    def read_resource(self, uri: str) -> Dict[str, Any]:
        if uri != PROMPT_RESOURCE_URI:
            raise KeyError(uri)
        payload = self.status()
        payload["laws"] = {
            "freshness": (
                "expected_git_head == current_git_head for mutation; last_git_head != current or material prompt/frontier diff -> rehydrate before consequential action"
            ),
            "composition": (
                "manifest profile/active modules + mandatory modules + task-selector matches + dependency closure -> strict unique order -> policy/modules -> matching ACTIVE_SCOPED overlays -> ephemeral task overlay"
            ),
            "source_binding": (
                "every compiled Git body carries exact HEAD + digest; snippets are not accepted as bodies"
            ),
            "frontier_refs": (
                "goal/pressure/work references are returned only when explicitly declared by active state; absent declarations remain UNDECLARED"
            ),
            "promotion": (
                "candidate + passed witnessed experiments + evidence + explicit authority witness; history remains"
            ),
            "authority": AUTHORITY_LAW,
        }
        return payload

    def benchmark(self) -> Dict[str, Any]:
        status = self.status()
        return {
            "prompt_runtime_configured": bool(status.get("configured")),
            "prompt_runtime_status": status.get("status"),
            "prompt_runtime_stack_digest": status.get("stack_digest"),
            "prompt_runtime_head": (status.get("git") or {}).get("head"),
            "prompt_runtime_frontier_status": (status.get("frontier_refs") or {}).get("status"),
        }
