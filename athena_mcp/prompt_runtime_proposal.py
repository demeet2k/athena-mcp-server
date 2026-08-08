from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Mapping, Sequence

from .prompt_runtime_types import (
    AUTHORITY_LAW, EXPERIMENT_STATUSES, OBSERVED_EXPERIMENT_STATUSES,
    PROMPT_RUNTIME_VERSION, PromptRuntimeError, compact_timestamp,
    json_copy as _json_copy, nonempty as _nonempty, safe_actor as _safe_actor,
    sha256_json, sha256_text, slug as _slug, string_list as _string_list, utc_now,
)


class PromptRuntimeProposalMixin:
    def propose(
        self,
        *,
        expected_git_head: str,
        module_id: str,
        version: str,
        scope: Sequence[str],
        content: str,
        defect: str,
        expected_effect: str,
        metrics: Sequence[str],
        tests: Sequence[str],
        rollback: str,
        depends_on: Sequence[str] | None = None,
        triggers: Sequence[str] | None = None,
        actor: str = "agent",
    ) -> Dict[str, Any]:
        self._cas(expected_git_head)
        self._require_clean()
        manifest, _ = self._manifest()
        module = _slug(module_id, "module_id")
        candidate_scope = _string_list(list(scope), "scope", allow_empty=False)
        body = _nonempty(content, "content").rstrip() + "\n"
        dependencies = _string_list(list(depends_on or []), "depends_on")
        unknown_dependencies = sorted(set(dependencies) - set(manifest["modules"]))
        if unknown_dependencies:
            raise PromptRuntimeError(f"candidate depends_on unknown modules: {unknown_dependencies}")
        candidate_version = _nonempty(version, "version")
        creator = _safe_actor(actor)
        created_at = utc_now()
        target = manifest["modules"].get(module)
        base_digest = None
        if isinstance(target, dict) and target.get("path"):
            base_digest = self._read_text(str(target["path"]), role="candidate_base")["digest"]
        digest_seed = {
            "module": module,
            "version": candidate_version,
            "scope": candidate_scope,
            "content_digest": sha256_text(body),
            "actor": creator,
            "created_at": created_at,
            "nonce": uuid.uuid4().hex,
        }
        suffix = sha256_json(digest_seed).split(":", 1)[1][:12]
        path = f"prompts/candidates/{module}/{compact_timestamp()}-{_slug(creator, 'actor')}-{suffix}.md"
        metadata: Dict[str, Any] = {
            "schema": "ATHENA.PROMPT.CANDIDATE.V1",
            "module_id": module,
            "version": candidate_version,
            "status": "CANDIDATE",
            "scope": candidate_scope,
            "authority_ceiling": manifest["authority_ceiling"],
            "depends_on": dependencies,
            "triggers": _string_list(list(triggers or []), "triggers"),
            "path": path,
            "defect": _nonempty(defect, "defect"),
            "expected_effect": _nonempty(expected_effect, "expected_effect"),
            "metrics": _string_list(list(metrics), "metrics", allow_empty=False),
            "tests": _string_list(list(tests), "tests", allow_empty=False),
            "rollback": _nonempty(rollback, "rollback"),
            "base_digest": base_digest,
            "expected_git_head": expected_git_head,
            "created_by": creator,
            "created_at": created_at,
            "content_digest": sha256_text(body),
        }
        event = {
            "schema": "ATHENA.PROMPT.EVENT.V1",
            "kind": "PROMPT_PROPOSAL",
            "time": created_at,
            "actor": creator,
            "expected_git_head": expected_git_head,
            "candidate_path": path,
            "candidate_digest": sha256_json(metadata),
            "module_id": module,
            "status": "CANDIDATE",
            "authority_law": AUTHORITY_LAW,
        }
        event_path = self._event_path("PROMPT_PROPOSAL", event)
        commit = self._commit_writes(
            expected_head=expected_git_head,
            writes={
                path: self._candidate_document(metadata, body),
                event_path: json.dumps(event, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            },
            actor=creator,
            message=f"prompt: propose {module} {candidate_version}",
        )
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": "CANDIDATE",
            "candidate_path": path,
            "candidate_metadata": metadata,
            "event_path": event_path,
            "commit": commit,
            "authority_law": AUTHORITY_LAW,
        }

    def experiment(
        self,
        *,
        expected_git_head: str,
        experiment_id: str,
        candidate_path: str,
        hypothesis: str,
        protocol: Mapping[str, Any],
        result_status: str,
        observations: Sequence[Mapping[str, Any]] | None = None,
        witness: Mapping[str, Any] | None = None,
        actor: str = "agent",
    ) -> Dict[str, Any]:
        self._cas(expected_git_head)
        self._require_clean()
        candidate_meta, _, candidate_body = self._load_candidate(candidate_path)
        status = _nonempty(result_status, "result_status").upper()
        if status not in EXPERIMENT_STATUSES:
            raise PromptRuntimeError(f"unknown experiment result_status {status!r}")
        observation_rows = list(observations or [])
        if any(not isinstance(row, Mapping) for row in observation_rows):
            raise PromptRuntimeError("observations must be an array of objects")
        witness_payload = dict(witness or {})
        if status in OBSERVED_EXPERIMENT_STATUSES:
            if not observation_rows:
                raise PromptRuntimeError(f"{status} experiment requires observed rows")
            if not witness_payload:
                raise PromptRuntimeError(f"{status} experiment requires an execution witness")
        elif observation_rows or witness_payload:
            raise PromptRuntimeError(
                f"{status} experiment may not carry observations/witness as though it had executed"
            )
        if not isinstance(protocol, Mapping) or not protocol:
            raise PromptRuntimeError("protocol must be a non-empty object")
        experiment_slug = _slug(experiment_id, "experiment_id")
        path = f"prompts/experiments/{experiment_slug}.json"
        if self._resolve(path, must_exist=False).exists():
            raise PromptRuntimeError(f"experiment_id already exists and is append-only: {experiment_slug!r}")
        record = {
            "schema": "ATHENA.PROMPT.EXPERIMENT.V1",
            "experiment_id": experiment_slug,
            "candidate_path": candidate_body["path"],
            "candidate_digest": candidate_body["digest"],
            "candidate_content_digest": candidate_meta["content_digest"],
            "hypothesis": _nonempty(hypothesis, "hypothesis"),
            "protocol": _json_copy(dict(protocol)),
            "result_status": status,
            "observations": [_json_copy(dict(row)) for row in observation_rows],
            "witness": _json_copy(witness_payload) if witness_payload else None,
            "recorded_by": _safe_actor(actor),
            "recorded_at": utc_now(),
            "expected_git_head": expected_git_head,
            "epistemic_law": (
                "PLANNED/RUNNING is not observation; PASSED/FAILED/INCONCLUSIVE requires explicit observed rows and witness"
            ),
        }
        record["record_digest"] = sha256_json(record)
        event = {
            "schema": "ATHENA.PROMPT.EVENT.V1",
            "kind": "PROMPT_TEST",
            "time": record["recorded_at"],
            "actor": record["recorded_by"],
            "expected_git_head": expected_git_head,
            "experiment_path": path,
            "experiment_digest": record["record_digest"],
            "candidate_path": candidate_body["path"],
            "result_status": status,
        }
        event_path = self._event_path("PROMPT_TEST", event)
        commit = self._commit_writes(
            expected_head=expected_git_head,
            writes={
                path: json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                event_path: json.dumps(event, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            },
            actor=record["recorded_by"],
            message=f"prompt: record experiment {experiment_slug} {status.lower()}",
        )
        return {
            "version": PROMPT_RUNTIME_VERSION,
            "status": status,
            "experiment_path": path,
            "record": record,
            "event_path": event_path,
            "commit": commit,
        }
