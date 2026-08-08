from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Sequence

from .prompt_runtime_types import (
    AUTHORITY_LAW, PROMPT_RUNTIME_VERSION, PromptRuntimeError, canonical_json,
    nonempty as _nonempty, safe_actor as _safe_actor, sha256_json,
    string_list as _string_list, utc_now,
)


class PromptRuntimePromotionMixin:
    def activate(
        self,
        *,
        expected_git_head: str,
        candidate_path: str,
        scope: Sequence[str],
        experiment_refs: Sequence[str],
        witness: Mapping[str, Any],
        expires_at: str | None = None,
        actor: str = "agent",
    ) -> Dict[str, Any]:
        self._cas(expected_git_head)
        self._require_clean()
        manifest, _ = self._manifest()
        active, active_body = self._active_state(manifest)
        candidate_meta, _, candidate_body = self._load_candidate(candidate_path)
        requested_scope = _string_list(list(scope), "scope", allow_empty=False)
        declared_scope = _string_list(candidate_meta.get("scope"), "candidate.scope", allow_empty=False)
        if not self._scope_is_subset(requested_scope, declared_scope):
            raise PromptRuntimeError(
                f"activation scope {requested_scope!r} exceeds candidate scope {declared_scope!r}"
            )
        verified = self._verified_experiments(
            experiment_refs,
            candidate_body["path"],
            candidate_digest=candidate_body["digest"],
            candidate_content_digest=candidate_meta["content_digest"],
        )
        witness_payload = self._validate_decision_witness(witness, "ACTIVATE_SCOPED")
        if expires_at:
            parsed = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise PromptRuntimeError("expires_at must be timezone-aware")
            if parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc):
                raise PromptRuntimeError("expires_at must be in the future")
        overlay_seed = {
            "candidate_path": candidate_body["path"],
            "scope": requested_scope,
            "experiments": list(experiment_refs),
            "witness": witness_payload,
        }
        overlay_id = "PROMPT.OVERLAY." + sha256_json(overlay_seed).split(":", 1)[1][:16]
        existing = list(active.get("active_scoped_overlays", []))
        if any(isinstance(row, dict) and row.get("overlay_id") == overlay_id for row in existing):
            raise PromptRuntimeError(f"overlay {overlay_id} is already active")
        overlay = {
            "overlay_id": overlay_id,
            "event_kind": "PROMPT_ACTIVATE",
            "candidate_path": candidate_body["path"],
            "candidate_digest": candidate_body["digest"],
            "module_id": candidate_meta["module_id"],
            "scope": requested_scope,
            "order": 1000 + int(manifest["modules"].get(candidate_meta["module_id"], {}).get("order", 0)),
            "experiment_refs": list(experiment_refs),
            "experiment_digests": [record["record_digest"] for record in verified],
            "witness": witness_payload,
            "activated_by": _safe_actor(actor),
            "activated_at": utc_now(),
            "expires_at": expires_at,
            "expected_git_head": expected_git_head,
            "status": "ACTIVE_SCOPED",
            "authority": "REPOSITORY_SCOPE_ONLY",
        }
        updated = copy.deepcopy(active)
        updated["active_scoped_overlays"] = existing + [overlay]
        updated["revision"] = int(active.get("revision", 0)) + 1
        updated["last_event"] = overlay
        commit = self._commit_writes(
            expected_head=expected_git_head,
            writes={
                active_body["path"]: json.dumps(updated, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            },
            actor=overlay["activated_by"],
            message=f"prompt: activate scoped overlay {overlay_id}",
        )
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": "ACTIVE_SCOPED",
            "overlay": overlay,
            "active_state_path": active_body["path"],
            "commit": commit,
            "firewall": "ACTIVE_SCOPED != CANONICAL",
        }

    def promote(
        self,
        *,
        expected_git_head: str,
        candidate_path: str,
        target_module_id: str,
        experiment_refs: Sequence[str],
        evidence_refs: Sequence[str],
        witness: Mapping[str, Any],
        actor: str = "agent",
    ) -> Dict[str, Any]:
        self._cas(expected_git_head)
        self._require_clean()
        manifest, _ = self._manifest()
        active, active_body = self._active_state(manifest)
        candidate_meta, candidate_text, candidate_body = self._load_candidate(candidate_path)
        target_id = _nonempty(target_module_id, "target_module_id")
        if target_id not in manifest["modules"]:
            raise PromptRuntimeError(
                "Prompt Runtime V1 promotes only existing manifest modules; propose manifest expansion separately"
            )
        if candidate_meta.get("module_id") != target_id:
            raise PromptRuntimeError(
                f"candidate module_id {candidate_meta.get('module_id')!r} does not match target {target_id!r}"
            )
        target_path = str(manifest["modules"][target_id]["path"])
        current_target = self._read_text(target_path, role="canonical_target")
        if not candidate_meta.get("base_digest"):
            raise PromptRuntimeError("candidate lacks base_digest and cannot be canonically promoted")
        if current_target["digest"] != candidate_meta["base_digest"]:
            raise PromptRuntimeError(
                canonical_json(
                    {
                        "status": "STALE_PROMPT_BASE",
                        "candidate_base_digest": candidate_meta["base_digest"],
                        "current_target_digest": current_target["digest"],
                        "target_path": target_path,
                    }
                )
            )
        verified_experiments = self._verified_experiments(
            experiment_refs,
            candidate_body["path"],
            candidate_digest=candidate_body["digest"],
            candidate_content_digest=candidate_meta["content_digest"],
        )
        evidence = self._verify_evidence_refs(evidence_refs)
        witness_payload = self._validate_decision_witness(witness, "PROMOTE")
        if not candidate_meta.get("rollback"):
            raise PromptRuntimeError("canonical promotion requires a candidate rollback plan")
        promoted_at = utc_now()
        event = {
            "schema": "ATHENA.PROMPT.EVENT.V1",
            "kind": "PROMPT_PROMOTE",
            "time": promoted_at,
            "actor": _safe_actor(actor),
            "expected_git_head": expected_git_head,
            "candidate_path": candidate_body["path"],
            "candidate_digest": candidate_body["digest"],
            "target_module_id": target_id,
            "target_path": current_target["path"],
            "previous_target_digest": current_target["digest"],
            "promoted_content_digest": candidate_meta["content_digest"],
            "experiment_refs": list(experiment_refs),
            "experiment_digests": [row["record_digest"] for row in verified_experiments],
            "evidence": evidence,
            "witness": witness_payload,
            "rollback": candidate_meta["rollback"],
            "authority": "REPOSITORY_OPERATING_POLICY_ONLY",
            "firewall": "PROMPT_RUNTIME != HOST_SYSTEM_PROMPT",
        }
        event["event_digest"] = sha256_json(event)
        event_path = self._event_path("PROMPT_PROMOTE", event)

        overlays_before = list(active.get("active_scoped_overlays", []))
        overlays_after = [
            row
            for row in overlays_before
            if not (isinstance(row, dict) and row.get("candidate_path") == candidate_body["path"])
        ]
        writes: Dict[str, str] = {
            current_target["path"]: candidate_text,
            event_path: json.dumps(event, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        }
        if overlays_after != overlays_before:
            updated = copy.deepcopy(active)
            updated["active_scoped_overlays"] = overlays_after
            updated["revision"] = int(active.get("revision", 0)) + 1
            updated["last_event"] = {
                "kind": "PROMPT_PROMOTE",
                "candidate_path": candidate_body["path"],
                "event_path": event_path,
                "time": promoted_at,
            }
            writes[active_body["path"]] = json.dumps(
                updated, ensure_ascii=False, sort_keys=True, indent=2
            ) + "\n"
        commit = self._commit_writes(
            expected_head=expected_git_head,
            writes=writes,
            actor=event["actor"],
            message=f"prompt: promote {target_id} from candidate",
        )
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": "CANONICAL_REPOSITORY_POLICY",
            "target_module_id": target_id,
            "target_path": current_target["path"],
            "candidate_path": candidate_body["path"],
            "candidate_preserved": self._resolve(candidate_body["path"]).is_file(),
            "event_path": event_path,
            "event": event,
            "removed_scoped_overlays": len(overlays_before) - len(overlays_after),
            "commit": commit,
            "authority_law": AUTHORITY_LAW,
        }
