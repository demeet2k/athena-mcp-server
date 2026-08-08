from __future__ import annotations

import json
from typing import Any, Dict, Mapping, Sequence

from .prompt_runtime_types import (
    CANDIDATE_META_CLOSE, CANDIDATE_META_OPEN, PromptRuntimeError,
    compact_timestamp, json_copy as _json_copy, nonempty as _nonempty,
    sha256_json, sha256_text, string_list as _string_list,
)


class PromptRuntimeRecordsMixin:
    def _candidate_document(self, metadata: Mapping[str, Any], body: str) -> str:
        return (
            CANDIDATE_META_OPEN
            + "\n"
            + json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)
            + "\n"
            + CANDIDATE_META_CLOSE
            + "\n"
            + body.rstrip()
            + "\n"
        )

    def _parse_candidate(self, text: str, path: str) -> tuple[Dict[str, Any], str]:
        if not text.startswith(CANDIDATE_META_OPEN + "\n"):
            raise PromptRuntimeError(f"candidate {path!r} lacks ATHENA_PROMPT_META_V1 header")
        close = "\n" + CANDIDATE_META_CLOSE + "\n"
        index = text.find(close)
        if index < 0:
            raise PromptRuntimeError(f"candidate {path!r} has an unterminated metadata header")
        metadata_text = text[len(CANDIDATE_META_OPEN) + 1 : index]
        try:
            metadata = json.loads(metadata_text)
        except json.JSONDecodeError as exc:
            raise PromptRuntimeError(f"candidate {path!r} has invalid metadata JSON") from exc
        if not isinstance(metadata, dict):
            raise PromptRuntimeError(f"candidate {path!r} metadata must be an object")
        body = text[index + len(close) :]
        expected = metadata.get("content_digest")
        observed = sha256_text(body.rstrip() + "\n")
        if expected != observed:
            raise PromptRuntimeError(
                f"candidate content digest mismatch path={path!r} expected={expected!r} observed={observed!r}"
            )
        return metadata, body.rstrip() + "\n"

    def _load_candidate(self, candidate_path: str) -> tuple[Dict[str, Any], str, Dict[str, Any]]:
        path = self._resolve(candidate_path, prefix="prompts/candidates")
        if path.suffix.lower() != ".md":
            raise PromptRuntimeError("prompt candidate path must end in .md")
        body = self._read_text(self._relative(path), role="candidate")
        metadata, candidate_text = self._parse_candidate(body["text"], body["path"])
        if metadata.get("path") != body["path"]:
            raise PromptRuntimeError("candidate metadata path does not match repository path")
        return metadata, candidate_text, body

    def _event_path(self, kind: str, seed: Any) -> str:
        digest = sha256_json(seed).split(":", 1)[1][:12]
        return f"prompts/events/{compact_timestamp()}-{kind}-{digest}.json"

    def _load_experiment(self, experiment_path: str) -> Dict[str, Any]:
        path = self._resolve(experiment_path, prefix="prompts/experiments")
        value, _ = self._read_json(self._relative(path), role="prompt_experiment")
        return value

    def _verified_experiments(
        self,
        refs: Sequence[str],
        candidate_path: str,
        *,
        candidate_digest: str,
        candidate_content_digest: str,
    ) -> list[Dict[str, Any]]:
        experiment_refs = _string_list(list(refs), "experiment_refs", allow_empty=False)
        verified = []
        for ref in experiment_refs:
            record = self._load_experiment(ref)
            if record.get("candidate_path") != candidate_path:
                raise PromptRuntimeError(
                    f"experiment {ref!r} is bound to {record.get('candidate_path')!r}, not {candidate_path!r}"
                )
            if record.get("candidate_digest") != candidate_digest:
                raise PromptRuntimeError(f"experiment {ref!r} is bound to a different candidate file digest")
            if record.get("candidate_content_digest") != candidate_content_digest:
                raise PromptRuntimeError(f"experiment {ref!r} is bound to different candidate content")
            if record.get("result_status") != "PASSED":
                raise PromptRuntimeError(f"experiment {ref!r} is not PASSED")
            if not record.get("witness") or not record.get("observations"):
                raise PromptRuntimeError(f"experiment {ref!r} lacks witnessed observations")
            expected_digest = record.get("record_digest")
            payload = dict(record)
            payload.pop("record_digest", None)
            if expected_digest != sha256_json(payload):
                raise PromptRuntimeError(f"experiment {ref!r} record digest mismatch")
            verified.append(record)
        return verified

    @staticmethod
    def _validate_decision_witness(witness: Mapping[str, Any], decision: str) -> Dict[str, Any]:
        if not isinstance(witness, Mapping) or not witness:
            raise PromptRuntimeError("decision witness must be a non-empty object")
        payload = _json_copy(dict(witness))
        for field in ("authority", "decision", "approved_by"):
            _nonempty(payload.get(field), f"witness.{field}")
        if str(payload["decision"]).upper() != decision:
            raise PromptRuntimeError(
                f"witness.decision must be {decision!r}, got {payload['decision']!r}"
            )
        return payload

    @staticmethod
    def _scope_is_subset(requested: Sequence[str], declared: Sequence[str]) -> bool:
        return "*" in declared or set(requested).issubset(set(declared))

    def _verify_evidence_refs(self, refs: Sequence[str]) -> list[Dict[str, Any]]:
        evidence_refs = _string_list(list(refs), "evidence_refs", allow_empty=False)
        result = []
        for ref in evidence_refs:
            if "://" in ref:
                result.append({"ref": ref, "kind": "EXTERNAL_REFERENCE", "body_bound": False})
                continue
            body = self._read_text(ref, role="promotion_evidence")
            result.append(
                {
                    "ref": body["path"],
                    "kind": "GIT_BODY",
                    "body_bound": True,
                    "digest": body["digest"],
                }
            )
        if not any(row["body_bound"] for row in result):
            raise PromptRuntimeError("canonical promotion requires at least one body-bound Git evidence ref")
        return result
