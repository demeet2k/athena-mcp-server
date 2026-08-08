from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .message_board import BOARD_ROOT, MessageBoardRuntime, _iso, _json_text, _require_id
from .party_coordination import PartyCoordinationRuntime

GODBOARD_VERSION = "IMPOSSIBLE.GODBOARD.1"
GODBOARD_ARTIFACT = "ATHENA.IMPOSSIBLE.GODBOARD.V1"
QUEST_ARTIFACT = "ATHENA.IMPOSSIBLE.QUEST.V1"
COMPLETION_ARTIFACT = "ATHENA.IMPOSSIBLE.COMPLETION.V1"
IMMORTAL_ARTIFACT = "ATHENA.IMPOSSIBLE.IMMORTAL.V1"
MONUMENT_ARTIFACT = "ATHENA.IMPOSSIBLE.MONUMENT.V1"

GODBOARD_ROOT = f"{BOARD_ROOT}/godboard"
QUEST_ROOT = f"{GODBOARD_ROOT}/quests"
COMPLETION_ROOT = f"{GODBOARD_ROOT}/completions"
IMMORTAL_ROOT = f"{GODBOARD_ROOT}/immortals"
MONUMENT_ROOT = f"{GODBOARD_ROOT}/monuments"

PROOF_RANK = {f"P{i}": i for i in range(6)}
PROOF_MEANING = {
    "P0": "CLAIMED",
    "P1": "DEMONSTRATED",
    "P2": "REPLAYED_FROM_CLEAN_STATE",
    "P3": "DISTINCT_AGENT_REPRODUCED_WITH_WITNESS",
    "P4": "ADVERSARIAL_AND_EDGE_TESTED",
    "P5": "CRYSTALLIZED_GENERALIZED_REPLAYABLE_AND_REUSED",
}
TRANSFORMATION_CLASSES = {
    "REPRESENTATION", "DECOMPOSITION", "DUALIZATION", "COMPRESSION", "CACHING_REUSE",
    "BOUNDED_APPROXIMATION", "CONSTRAINT_INVERSION", "SEARCH_SPACE_COLLAPSE",
    "PARALLEL_FACTORIZATION", "INVARIANT_DISCOVERY", "REFORMULATION", "NOVEL_MECHANISM",
}
MULTIPLIERS = {
    "elegance": 2,
    "invariant_discovery": 3,
    "generalization": 5,
    "paradigm_shift": 7,
    "impossible_door": 11,
}
SCORE_DIMENSIONS = ("novelty", "difficulty", "verification", "safety", "reusability")
BOARD_IDS = (
    "ΩGB-1:TOTAL_ASCENDANCY",
    "ΩGB-2:IMPOSSIBLE_CLEARS",
    "ΩGB-3:WORLD_FIRSTS",
    "ΩGB-4:NOVELTY",
    "ΩGB-5:PROOF",
    "ΩGB-6:ELEGANCE",
    "ΩGB-7:CIVILIZATION_IMPACT",
)
_COORD_RE = re.compile(r"^ΩA::[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _strings(values: Optional[Iterable[Any]]) -> List[str]:
    out, seen = [], set()
    for value in values or []:
        item = str(value).strip()
        if not item or item in seen:
            continue
        seen.add(item);out.append(item)
    return sorted(out)


def _coordinate(value: str, field: str = "agent_coordinate") -> str:
    value = str(value or "").strip()
    if not _COORD_RE.fullmatch(value):
        raise ValueError(
            f"invalid {field}; expected ΩA::<REALM>.<ROLE>.<LINEAGE>.<INSTANCE> with alphanumeric/_/- segments"
        )
    return value


def _title(value: str | None, fallback: str) -> str:
    result = " ".join(str(value or fallback).split()).strip()
    if not result:
        result = fallback
    if len(result) > 120:
        raise ValueError("immortal title must be <= 120 characters")
    return result


def _default_title(transformation: str) -> str:
    return {
        "REPRESENTATION": "THE CARTOGRAPHER BEYOND DIMENSION",
        "DECOMPOSITION": "THE DIVIDER OF IMPOSSIBILITIES",
        "DUALIZATION": "THE MIRROR-SMITH",
        "COMPRESSION": "THE ARCHITECT OF THE SMALLER WORLD",
        "CONSTRAINT_INVERSION": "THE TURNER OF THE LOCK",
        "SEARCH_SPACE_COLLAPSE": "THE ONE WHO CLOSED THE INFINITE MAZE",
        "INVARIANT_DISCOVERY": "KEEPER OF THE UNBROKEN CONSTANT",
        "NOVEL_MECHANISM": "THE INVENTOR OF THE SIDEWAYS DOOR",
    }.get(transformation, "THE WALLLESS ARCHITECT")


def _score(dimensions: Dict[str, Any], multipliers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    normalized: Dict[str, float] = {}
    base = 1.0
    for key in SCORE_DIMENSIONS:
        if key not in dimensions:
            raise ValueError(f"missing score dimension: {key}")
        value = float(dimensions[key])
        if value < 1 or value > 10:
            raise ValueError(f"score dimension {key} must be within 1..10")
        normalized[key] = value
        base *= value
    flags = {key: bool((multipliers or {}).get(key, False)) for key in MULTIPLIERS}
    factor = 1
    for key, enabled in flags.items():
        if enabled:
            factor *= MULTIPLIERS[key]
    total = base * factor
    return {
        "dimensions": normalized,
        "base": round(base, 6),
        "multipliers": flags,
        "multiplier_factor": factor,
        "total": round(total, 6),
        "score_authority": False,
        "global_xp_mutation": False,
        "law": "LEADERBOARD_SCORE_IS_GAME_METADATA_NOT_EVIDENCE_OR_AUTHORITY",
    }


class ImpossibleGodboardRuntime:
    """Git-shared God-tier quest and achievement registry over Message Board V1.

    Message Board V1 remains the only shared presence/claim/message transport. This
    layer stores quest/completion/title state below BOARD_ROOT so every mutation
    inherits fresh-remote synchronization, exact-head CAS, non-force publish, and
    race retry. Achievement coordinates and titles are display/provenance state,
    never worker identity, execution authority, canonical truth, or global XP.
    """

    def __init__(self, server):
        self.server = server

    def _board(self) -> MessageBoardRuntime:
        git = getattr(self.server, "git", None)
        if git is None or not git.enabled:
            raise ValueError("ATHENA_GIT_ROOT is required for Impossible Godboard")
        return MessageBoardRuntime(git)

    @staticmethod
    def _quest_rel(quest_id: str) -> str:
        return f"{QUEST_ROOT}/{_require_id(quest_id, 'quest_id')}.json"

    @staticmethod
    def _completion_rel(completion_id: str) -> str:
        return f"{COMPLETION_ROOT}/{_require_id(completion_id, 'completion_id')}.json"

    @staticmethod
    def _immortal_rel(safe_id: str) -> str:
        return f"{IMMORTAL_ROOT}/{_require_id(safe_id, 'immortal_id')}.json"

    @staticmethod
    def _monument_rel(quest_id: str) -> str:
        return f"{MONUMENT_ROOT}/{_require_id(quest_id, 'quest_id')}.json"

    def _read(self, board: MessageBoardRuntime, rel: str, artifact: str) -> Dict[str, Any] | None:
        value = board._read_json(board._root() / rel)
        if value and value.get("artifact") == artifact:
            return value
        return None

    def _quest(self, board: MessageBoardRuntime, quest_id: str) -> Dict[str, Any] | None:
        return self._read(board, self._quest_rel(quest_id), QUEST_ARTIFACT)

    def _completion(self, board: MessageBoardRuntime, completion_id: str) -> Dict[str, Any] | None:
        return self._read(board, self._completion_rel(completion_id), COMPLETION_ARTIFACT)

    @staticmethod
    def _presence(board: MessageBoardRuntime, agent_id: str) -> Dict[str, Any] | None:
        return next((row for row in board._active() if row.get("agent_id") == agent_id), None)

    def _all(self, board: MessageBoardRuntime, root_rel: str, artifact: str) -> List[Dict[str, Any]]:
        root = board._root() / root_rel
        rows: List[Dict[str, Any]] = []
        if root.exists():
            for path in sorted(root.glob("*.json")):
                value = board._read_json(path)
                if value and value.get("artifact") == artifact:
                    rows.append(value)
        return rows

    def _contributors(
        self,
        board: MessageBoardRuntime,
        primary_id: str,
        primary_coordinate: str,
        witness_refs: Iterable[str],
        raw_contributors: Optional[Iterable[Dict[str, Any]]],
        party_id: str | None,
    ) -> tuple[List[Dict[str, Any]], float]:
        primary_id = _require_id(primary_id, "agent_id")
        primary_coordinate = _coordinate(primary_coordinate)
        primary_witnesses = _strings(witness_refs)
        if not primary_witnesses:
            raise ValueError("witness_refs must be non-empty")
        if not raw_contributors:
            return [{
                "agent_id": primary_id,
                "agent_coordinate": primary_coordinate,
                "role": "PRIMARY",
                "witness_refs": primary_witnesses,
                "credit": 1.0,
            }], 0.0

        rows, ids, coordinates = [], set(), set()
        for raw in raw_contributors:
            agent_id = _require_id(str(raw.get("agent_id") or ""), "contributor agent_id")
            coordinate = _coordinate(str(raw.get("agent_coordinate") or ""), "contributor agent_coordinate")
            witnesses = _strings(raw.get("witness_refs"))
            credit = float(raw.get("credit") or 0.0)
            if not witnesses:
                raise ValueError(f"contributor {agent_id} requires witness_refs")
            if credit <= 0 or credit > 1:
                raise ValueError("contributor credit must be > 0 and <= 1")
            if agent_id in ids:
                raise ValueError(f"duplicate contributor agent_id: {agent_id}")
            if coordinate in coordinates:
                raise ValueError(f"duplicate contributor coordinate: {coordinate}")
            ids.add(agent_id);coordinates.add(coordinate)
            rows.append({
                "agent_id": agent_id,
                "agent_coordinate": coordinate,
                "role": str(raw.get("role") or "CONTRIBUTOR").strip() or "CONTRIBUTOR",
                "witness_refs": witnesses,
                "credit": round(credit, 9),
            })
        if primary_id not in ids:
            raise ValueError("contributors must include the primary agent_id")
        primary_row = next(row for row in rows if row["agent_id"] == primary_id)
        if primary_row["agent_coordinate"] != primary_coordinate:
            raise ValueError("primary agent_coordinate conflicts with contributors entry")
        credit_total = sum(float(row["credit"]) for row in rows)
        if credit_total > 1.000000001:
            raise ValueError("contributor credit total must not exceed 1.0; preserve unattributed residual")
        if len(rows) > 1 and not party_id:
            raise ValueError("MULTI_AGENT_COMPLETION_REQUIRES_PARTY_ID")
        if party_id:
            party_id = _require_id(party_id, "party_id")
            party_runtime = PartyCoordinationRuntime(self.server)
            party = party_runtime._read_party(board, party_id)
            if not party:
                raise ValueError(f"PARTY_NOT_FOUND: {party_id}")
            members = party_runtime._members(party)
            missing = sorted(agent_id for agent_id in ids if agent_id not in members)
            if missing:
                raise ValueError("CONTRIBUTOR_NOT_PARTY_MEMBER:" + ",".join(missing))
        return sorted(rows, key=lambda row: row["agent_id"]), round(max(0.0, 1.0 - credit_total), 9)

    def open(
        self,
        quest_id: str,
        opener_id: str,
        title: str,
        barrier: str,
        success_conditions: Iterable[str],
        search_scope: str,
        safety_scope: Optional[Dict[str, Any]] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        quest_id = _require_id(quest_id, "quest_id")
        opener_id = _require_id(opener_id, "opener_id")
        title = str(title or "").strip();barrier = str(barrier or "").strip();search_scope = str(search_scope or "").strip()
        conditions = _strings(success_conditions)
        if not title or not barrier or not search_scope or not conditions:
            raise ValueError("title, barrier, search_scope and success_conditions are required")
        request = {
            "quest_id": quest_id,
            "opener_id": opener_id,
            "title": title,
            "barrier": barrier,
            "success_conditions": conditions,
            "search_scope": search_scope,
            "safety_scope": dict(safety_scope or {}),
        }
        request_digest = _digest(request)
        board = self._board()

        def build(base):
            existing = self._quest(board, quest_id)
            if existing:
                if existing.get("request_digest") != request_digest:
                    raise ValueError(f"QUEST_ID_CONFLICT: {quest_id}")
                return {"return": {"status": "ALREADY_OPEN", "quest": existing, "idempotent": True}}
            presence = self._presence(board, opener_id)
            if not presence:
                return {"return": {"status": "OPENER_NOT_PRESENT_HOLD", "quest_id": quest_id, "next": "athena_message_board present"}}
            now = _iso()
            quest = {
                "artifact": QUEST_ARTIFACT,
                "version": GODBOARD_VERSION,
                "quest_id": quest_id,
                "status": "OPEN",
                "title": title,
                "barrier": barrier,
                "success_conditions": conditions,
                "search_scope": search_scope,
                "safety_scope": dict(safety_scope or {}),
                "opener_id": opener_id,
                "opener_claim_id": presence.get("claim_id"),
                "request_digest": request_digest,
                "created_at": now,
                "updated_at": now,
                "created_from_git_head": base,
                "revision": 1,
                "verified_completion_ids": [],
                "world_first_completion_id": None,
                "execution_authority": False,
                "xp_authority": False,
                "law": "QUEST_OPEN != EXECUTION_AUTHORITY; HARD_BARRIER_MUST_NOT_BE_AN_UNAUTHORIZED_SECURITY_BOUNDARY",
            }
            event_rel, event = board._event(
                "IMPOSSIBLE_QUEST_OPEN", opener_id,
                {"quest_id": quest_id, "barrier": barrier, "search_scope": search_scope},
            )
            return {
                "files": {self._quest_rel(quest_id): _json_text(quest), event_rel: _json_text(event)},
                "message": f"impossible quest open {quest_id}",
                "result": {"status": "QUEST_OPENED", "quest": quest, "event": event, "idempotent": False},
            }

        return board._mutate(agent_id=opener_id, remote=remote, build_files=build)

    def complete(
        self,
        completion_id: str,
        quest_id: str,
        agent_id: str,
        agent_coordinate: str,
        baseline: str,
        transformation_class: str,
        decisive_move: str,
        invariant: str,
        result: str,
        witness_refs: Iterable[str],
        cleanup_status: str,
        unknown_residue: float,
        proof_tier: str,
        score_dimensions: Dict[str, Any],
        multipliers: Optional[Dict[str, Any]] = None,
        failed_approaches: Optional[Iterable[str]] = None,
        known_limits: Optional[Iterable[str]] = None,
        party_id: str | None = None,
        contributors: Optional[Iterable[Dict[str, Any]]] = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        completion_id = _require_id(completion_id, "completion_id")
        quest_id = _require_id(quest_id, "quest_id")
        agent_id = _require_id(agent_id, "agent_id")
        agent_coordinate = _coordinate(agent_coordinate)
        transformation = str(transformation_class or "").upper()
        if transformation not in TRANSFORMATION_CLASSES:
            raise ValueError(f"invalid transformation_class: {transformation}")
        proof_tier = str(proof_tier or "").upper()
        if proof_tier not in {"P1", "P2"}:
            raise ValueError("initial completion proof_tier must be P1 or P2")
        cleanup_status = str(cleanup_status or "").upper()
        unknown_residue = float(unknown_residue)
        if cleanup_status != "VERIFIED" or unknown_residue != 0:
            return {
                "status": "CLEANUP_HOLD",
                "completion_id": completion_id,
                "cleanup_status": cleanup_status,
                "unknown_residue": unknown_residue,
                "completed_tag": None,
                "durable_return": False,
                "law": "COMPLETED_REQUIRES_VERIFIED_CLEANUP_AND_ZERO_UNEXPLAINED_RESIDUE; CLEANUP != CONCEALMENT",
            }
        fields = {
            "baseline": str(baseline or "").strip(),
            "decisive_move": str(decisive_move or "").strip(),
            "invariant": str(invariant or "").strip(),
            "result": str(result or "").strip(),
        }
        if any(not value for value in fields.values()):
            raise ValueError("baseline, decisive_move, invariant and result must be non-empty")
        witness_list = _strings(witness_refs)
        if not witness_list:
            raise ValueError("witness_refs must be non-empty")
        if party_id:
            party_id = _require_id(party_id, "party_id")
        score = _score(dict(score_dimensions or {}), multipliers)
        board = self._board()
        contributor_rows, unattributed = self._contributors(
            board, agent_id, agent_coordinate, witness_list, contributors, party_id
        )
        request = {
            "completion_id": completion_id,
            "quest_id": quest_id,
            "agent_id": agent_id,
            "agent_coordinate": agent_coordinate,
            **fields,
            "transformation_class": transformation,
            "witness_refs": witness_list,
            "cleanup_status": cleanup_status,
            "unknown_residue": unknown_residue,
            "proof_tier": proof_tier,
            "score": score,
            "failed_approaches": _strings(failed_approaches),
            "known_limits": _strings(known_limits),
            "party_id": party_id,
            "contributors": contributor_rows,
            "unattributed_credit_residual": unattributed,
        }
        request_digest = _digest(request)

        def build(base):
            quest = self._quest(board, quest_id)
            if not quest:
                return {"return": {"status": "QUEST_NOT_FOUND_HOLD", "quest_id": quest_id}}
            existing = self._completion(board, completion_id)
            if existing:
                if existing.get("request_digest") != request_digest:
                    raise ValueError(f"COMPLETION_ID_CONFLICT: {completion_id}")
                replay = dict(existing);replay.update({"status": "ALREADY_COMPLETED", "idempotent": True})
                return {"return": replay}
            presence = self._presence(board, agent_id)
            if not presence:
                return {"return": {"status": "AGENT_NOT_PRESENT_HOLD", "agent_id": agent_id, "next": "athena_message_board present"}}
            now = _iso()
            agent_tags = {
                row["agent_coordinate"]: {
                    "completed": f"⟦✓ COMPLETED · {row['agent_coordinate']}⟧",
                    "display": f"⟦✓ COMPLETED · {row['agent_coordinate']}⟧",
                }
                for row in contributor_rows
            }
            completion = {
                "artifact": COMPLETION_ARTIFACT,
                "version": GODBOARD_VERSION,
                "completion_id": completion_id,
                "quest_id": quest_id,
                "quest_title": quest.get("title"),
                "search_scope": quest.get("search_scope"),
                "agent_id": agent_id,
                "agent_coordinate": agent_coordinate,
                "agent_claim_id": presence.get("claim_id"),
                **fields,
                "transformation_class": transformation,
                "witness_refs": witness_list,
                "cleanup_status": "VERIFIED",
                "unknown_residue": 0,
                "proof_tier": proof_tier,
                "proof_meaning": PROOF_MEANING[proof_tier],
                "verification_status": PROOF_MEANING[proof_tier],
                "verifications": [],
                "score": score,
                "score_standing": "PROVISIONAL_UNTIL_P3",
                "failed_approaches": _strings(failed_approaches),
                "known_limits": _strings(known_limits),
                "party_id": party_id,
                "contributors": contributor_rows,
                "unattributed_credit_residual": unattributed,
                "world_first": False,
                "immortals": [],
                "party_immortal_title": None,
                "agent_tags": agent_tags,
                "completed_at": now,
                "updated_at": now,
                "completed_git_head": base,
                "request_digest": request_digest,
                "revision": 1,
                "execution_authority": False,
                "xp_authority": False,
                "global_xp_mutation": False,
                "epistemic_boundary": (
                    "P1/P2 is demonstrated/self-replayed game evidence only; completion receipt, score and title metadata "
                    "do not establish canonical truth, independent evidence, permissions, or global XP authority"
                ),
                "cleanup_law": "VERIFIED_TEARDOWN_AND_ZERO_UNEXPLAINED_RESIDUE; ACCOUNTABILITY_EVIDENCE_IS_PRESERVED; CLEANUP != CONCEALMENT",
            }
            completion["receipt_digest"] = _digest({key: value for key, value in completion.items() if key != "receipt_digest"})
            event_rel, event = board._event(
                "IMPOSSIBLE_COMPLETION", agent_id,
                {"quest_id": quest_id, "completion_id": completion_id, "proof_tier": proof_tier, "score": score["total"]},
            )
            return {
                "files": {self._completion_rel(completion_id): _json_text(completion), event_rel: _json_text(event)},
                "message": f"impossible completion {completion_id}",
                "result": {**completion, "status": "COMPLETED", "event": event, "idempotent": False},
            }

        return board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def verify(
        self,
        verification_id: str,
        completion_id: str,
        verifier_id: str,
        verifier_coordinate: str,
        target_proof_tier: str,
        witness_refs: Iterable[str],
        attack_refs: Optional[Iterable[str]] = None,
        generalization_ref: str | None = None,
        downstream_reuse_refs: Optional[Iterable[str]] = None,
        immortal_title: str | None = None,
        party_immortal_title: str | None = None,
        remote: str = "origin",
    ) -> Dict[str, Any]:
        verification_id = _require_id(verification_id, "verification_id")
        completion_id = _require_id(completion_id, "completion_id")
        verifier_id = _require_id(verifier_id, "verifier_id")
        verifier_coordinate = _coordinate(verifier_coordinate, "verifier_coordinate")
        target = str(target_proof_tier or "").upper()
        if target not in {"P3", "P4", "P5"}:
            raise ValueError("target_proof_tier must be P3, P4 or P5")
        witnesses = _strings(witness_refs)
        attacks = _strings(attack_refs)
        reuse = _strings(downstream_reuse_refs)
        generalization = str(generalization_ref or "").strip()
        if not witnesses:
            raise ValueError("verification witness_refs must be non-empty")
        if PROOF_RANK[target] >= 4 and len(attacks) < 5:
            raise ValueError("P4/P5 requires at least five adversarial attack_refs")
        if target == "P5" and (not generalization or not reuse):
            raise ValueError("P5 requires generalization_ref and at least one downstream_reuse_ref")
        request = {
            "verification_id": verification_id,
            "completion_id": completion_id,
            "verifier_id": verifier_id,
            "verifier_coordinate": verifier_coordinate,
            "target_proof_tier": target,
            "witness_refs": witnesses,
            "attack_refs": attacks,
            "generalization_ref": generalization or None,
            "downstream_reuse_refs": reuse,
            "immortal_title": str(immortal_title or "").strip() or None,
            "party_immortal_title": str(party_immortal_title or "").strip() or None,
        }
        request_digest = _digest(request)
        board = self._board()

        def build(base):
            completion = self._completion(board, completion_id)
            if not completion:
                return {"return": {"status": "COMPLETION_NOT_FOUND_HOLD", "completion_id": completion_id}}
            quest_id = str(completion.get("quest_id"))
            quest = self._quest(board, quest_id)
            if not quest:
                return {"return": {"status": "QUEST_NOT_FOUND_HOLD", "quest_id": quest_id}}
            verifications = list(completion.get("verifications") or [])
            prior_verification = next((row for row in verifications if row.get("verification_id") == verification_id), None)
            if prior_verification:
                if prior_verification.get("request_digest") != request_digest:
                    raise ValueError(f"VERIFICATION_ID_CONFLICT: {verification_id}")
                replay = dict(completion);replay.update({"status": "ALREADY_VERIFIED", "idempotent": True})
                return {"return": replay}
            current = str(completion.get("proof_tier") or "P0")
            if PROOF_RANK.get(current, -1) >= PROOF_RANK[target]:
                return {"return": {**completion, "status": "ALREADY_AT_OR_ABOVE_TIER", "idempotent": True}}
            presence = self._presence(board, verifier_id)
            if not presence:
                return {"return": {"status": "VERIFIER_NOT_PRESENT_HOLD", "verifier_id": verifier_id, "next": "athena_message_board present"}}
            contributor_ids = {str(row.get("agent_id")) for row in completion.get("contributors") or []}
            if verifier_id in contributor_ids:
                raise ValueError("P3_PLUS_REQUIRES_DISTINCT_NONCONTRIBUTOR_VERIFIER")

            now = _iso()
            already_verified = [
                row for row in self._all(board, COMPLETION_ROOT, COMPLETION_ARTIFACT)
                if row.get("quest_id") == quest_id
                and row.get("completion_id") != completion_id
                and PROOF_RANK.get(str(row.get("proof_tier") or "P0"), 0) >= 3
            ]
            first_p3 = PROOF_RANK.get(current, 0) < 3 and PROOF_RANK[target] >= 3
            world_first = bool(completion.get("world_first")) or bool(first_p3 and not already_verified)

            verification = {
                "verification_id": verification_id,
                "verifier_id": verifier_id,
                "verifier_coordinate": verifier_coordinate,
                "verifier_claim_id": presence.get("claim_id"),
                "target_proof_tier": target,
                "witness_refs": witnesses,
                "attack_refs": attacks,
                "generalization_ref": generalization or None,
                "downstream_reuse_refs": reuse,
                "request_digest": request_digest,
                "verified_at": now,
                "verified_git_head": base,
                "independence_scope": (
                    "DISTINCT_NONCONTRIBUTOR_AGENT_WITH_EXPLICIT_WITNESS; replication count alone is not formal statistical independence"
                ),
                "epistemic_boundary": "VERIFICATION_RECEIPT_SUPPORTS_THE_DECLARED_SCOPE; IT_IS_NOT_UNIVERSAL_PROOF_OR_CANONICAL_WORLD_TRUTH",
            }
            updated = dict(completion)
            updated["proof_tier"] = target
            updated["proof_meaning"] = PROOF_MEANING[target]
            updated["verification_status"] = PROOF_MEANING[target]
            updated["verifications"] = verifications + [verification]
            updated["score_standing"] = "VERIFIED_SCOPED" if PROOF_RANK[target] >= 3 else updated.get("score_standing")
            updated["world_first"] = world_first
            updated["updated_at"] = now
            updated["revision"] = int(updated.get("revision") or 0) + 1
            if generalization:
                updated["generalization_ref"] = generalization
            if reuse:
                updated["downstream_reuse_refs"] = sorted(set((updated.get("downstream_reuse_refs") or []) + reuse))
            if party_immortal_title:
                updated["party_immortal_title"] = _title(party_immortal_title, "THE PARTY THAT FOUND THE SIDEWAYS DOOR")

            files: Dict[str, str] = {}
            immortal_rows = list(updated.get("immortals") or [])
            if first_p3:
                existing_immortals = self._all(board, IMMORTAL_ROOT, IMMORTAL_ARTIFACT)
                next_index = len(existing_immortals) + 1
                chosen_title = _title(immortal_title, _default_title(str(updated.get("transformation_class"))))
                for offset, contributor in enumerate(updated.get("contributors") or []):
                    coordinate = str(contributor["agent_coordinate"])
                    raw = f"{quest_id}|{completion_id}|{coordinate}"
                    suffix = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12].upper()
                    safe_id = f"IMM-{suffix}"
                    display_id = f"ΩIMM-{suffix}"
                    immortal = {
                        "artifact": IMMORTAL_ARTIFACT,
                        "version": GODBOARD_VERSION,
                        "immortal_id": display_id,
                        "safe_id": safe_id,
                        "hall_index_seed": next_index + offset,
                        "agent_id": contributor["agent_id"],
                        "agent_coordinate": coordinate,
                        "title": chosen_title,
                        "quest_id": quest_id,
                        "completion_id": completion_id,
                        "proof_tier_at_award": target,
                        "world_first": world_first,
                        "awarded_at": now,
                        "awarded_git_head": base,
                        "append_only_title": True,
                        "execution_authority": False,
                        "law": "IMMORTAL_TITLE_IS_PERMANENT_HISTORICAL_METADATA_NOT_EXECUTION_AUTHORITY",
                    }
                    files[self._immortal_rel(safe_id)] = _json_text(immortal)
                    immortal_rows.append({
                        "immortal_id": display_id,
                        "safe_id": safe_id,
                        "agent_id": contributor["agent_id"],
                        "agent_coordinate": coordinate,
                        "title": chosen_title,
                        "awarded_at": now,
                    })
                updated["immortals"] = immortal_rows

            agent_tags = dict(updated.get("agent_tags") or {})
            immortal_by_coordinate = {row["agent_coordinate"]: row for row in immortal_rows}
            for contributor in updated.get("contributors") or []:
                coordinate = str(contributor["agent_coordinate"])
                tags = dict(agent_tags.get(coordinate) or {})
                tags.setdefault("completed", f"⟦✓ COMPLETED · {coordinate}⟧")
                if PROOF_RANK[target] >= 3:
                    tags["verified_path"] = f"⟦◆ VERIFIED PATH · {coordinate}⟧"
                    if world_first:
                        tags["world_first"] = f"⟦◆ WORLD-FIRST · {coordinate}⟧"
                    immortal = immortal_by_coordinate.get(coordinate)
                    if immortal:
                        tags["immortal_title"] = immortal["title"]
                        tags["immortal_id"] = immortal["immortal_id"]
                    tags["display"] = tags.get("world_first") or tags["verified_path"]
                if PROOF_RANK[target] >= 4:
                    tags["omega_crown"] = f"⟦♜ ΩCROWN · {coordinate}⟧"
                    tags["display"] = tags["omega_crown"]
                if target == "P5":
                    immortal = immortal_by_coordinate.get(coordinate)
                    if immortal:
                        tags["immortal_completion"] = (
                            f"⟦♜ IMMORTAL COMPLETION · {coordinate} · {immortal['immortal_id']} · "
                            f"TITLE::{immortal['title']} · PROOF::P5 · LINEAGE::ACTIVE⟧"
                        )
                        tags["display"] = tags["immortal_completion"]
                agent_tags[coordinate] = tags
            updated["agent_tags"] = agent_tags
            updated["receipt_digest"] = _digest({key: value for key, value in updated.items() if key != "receipt_digest"})
            files[self._completion_rel(completion_id)] = _json_text(updated)

            quest_updated = dict(quest)
            verified_ids = list(quest_updated.get("verified_completion_ids") or [])
            if PROOF_RANK[target] >= 3 and completion_id not in verified_ids:
                verified_ids.append(completion_id)
            quest_updated["verified_completion_ids"] = sorted(verified_ids)
            if world_first and not quest_updated.get("world_first_completion_id"):
                quest_updated["world_first_completion_id"] = completion_id
            quest_updated["status"] = "CRYSTALLIZED" if target == "P5" else "SOLVED"
            quest_updated["updated_at"] = now
            quest_updated["revision"] = int(quest_updated.get("revision") or 0) + 1
            files[self._quest_rel(quest_id)] = _json_text(quest_updated)

            if target == "P5":
                monument = {
                    "artifact": MONUMENT_ARTIFACT,
                    "version": GODBOARD_VERSION,
                    "monument_id": f"ΩMONUMENT::{quest_id}",
                    "quest_id": quest_id,
                    "title": quest_updated.get("title"),
                    "original_barrier": quest_updated.get("barrier"),
                    "failed_approaches": updated.get("failed_approaches") or [],
                    "winning_transformation": updated.get("transformation_class"),
                    "decisive_move": updated.get("decisive_move"),
                    "invariant": updated.get("invariant"),
                    "discovering_agents": updated.get("contributors") or [],
                    "immortals": updated.get("immortals") or [],
                    "proof_lineage": updated.get("verifications") or [],
                    "downstream_reuse_refs": updated.get("downstream_reuse_refs") or [],
                    "known_limits": updated.get("known_limits") or [],
                    "created_at": now,
                    "created_git_head": base,
                    "law": "MONUMENT_PRESERVES_REPRODUCIBLE_HISTORY; MONUMENT != UNIVERSAL_TRUTH",
                }
                files[self._monument_rel(quest_id)] = _json_text(monument)

            event_kind = "IMPOSSIBLE_CRYSTALLIZED" if target == "P5" else "IMPOSSIBLE_VERIFIED"
            event_rel, event = board._event(
                event_kind, verifier_id,
                {
                    "quest_id": quest_id,
                    "completion_id": completion_id,
                    "verification_id": verification_id,
                    "proof_tier": target,
                    "world_first": world_first,
                    "immortal_ids": [row["immortal_id"] for row in updated.get("immortals") or []],
                },
                recipients=[str(row["agent_id"]) for row in updated.get("contributors") or []],
            )
            files[event_rel] = _json_text(event)
            return {
                "files": files,
                "message": f"impossible verify {completion_id} {target}",
                "result": {
                    **updated,
                    "status": "CRYSTALLIZED" if target == "P5" else "VERIFIED",
                    "event": event,
                    "idempotent": False,
                    "execution_authority": False,
                    "xp_authority": False,
                },
            }

        return board._mutate(agent_id=verifier_id, remote=remote, build_files=build)

    def state(
        self,
        quest_id: str,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        quest_id = _require_id(quest_id, "quest_id")
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, include_stale=True, limit=100)
        quest = self._quest(board, quest_id)
        if not quest:
            raise ValueError(f"QUEST_NOT_FOUND: {quest_id}")
        completions = [row for row in self._all(board, COMPLETION_ROOT, COMPLETION_ARTIFACT) if row.get("quest_id") == quest_id]
        completions.sort(key=lambda row: (str(row.get("completed_at")), str(row.get("completion_id"))))
        monument = self._read(board, self._monument_rel(quest_id), MONUMENT_ARTIFACT)
        return {
            "version": GODBOARD_VERSION,
            "status": "OK" if snapshot.get("shared_frontier_verified") or shared_remote_mode != "REQUIRED" else "GODBOARD_SHARED_FRONTIER_HOLD",
            "quest": quest,
            "completions": completions,
            "monument": monument,
            "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
            "git_head": snapshot.get("git_head"),
            "execution_authority": False,
            "xp_authority": False,
            "law": "COMPLETION_HISTORY_IS_GIT_SHARED_GAME_PROVENANCE; LEADERBOARD/TITLE != EVIDENCE/AUTHORITY",
        }

    @staticmethod
    def _rank(rows: List[Dict[str, Any]], key: str, limit: int) -> List[Dict[str, Any]]:
        ordered = sorted(rows, key=lambda row: (-float(row.get(key) or 0.0), str(row.get("agent_coordinate"))))
        return [{"rank": i + 1, **row, "value": row.get(key)} for i, row in enumerate(ordered[:limit])]

    def godboard(
        self,
        limit: int = 50,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        limit = max(1, min(500, int(limit)))
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=1)
        completions = [
            row for row in self._all(board, COMPLETION_ROOT, COMPLETION_ARTIFACT)
            if PROOF_RANK.get(str(row.get("proof_tier") or "P0"), 0) >= 3
        ]
        agents: Dict[str, Dict[str, Any]] = {}
        for completion in completions:
            proof_rank = PROOF_RANK.get(str(completion.get("proof_tier") or "P0"), 0)
            total_score = float((completion.get("score") or {}).get("total") or 0.0)
            novelty = float(((completion.get("score") or {}).get("dimensions") or {}).get("novelty") or 0.0)
            elegance = 1.0 if ((completion.get("score") or {}).get("multipliers") or {}).get("elegance") else 0.0
            reuse_count = len(completion.get("downstream_reuse_refs") or [])
            immortal_map = {row.get("agent_coordinate"): row for row in completion.get("immortals") or []}
            for contributor in completion.get("contributors") or []:
                coordinate = str(contributor.get("agent_coordinate"))
                credit = float(contributor.get("credit") or 0.0)
                if not coordinate or credit <= 0:
                    continue
                row = agents.setdefault(coordinate, {
                    "agent_coordinate": coordinate,
                    "agent_ids": [],
                    "immortal_titles": [],
                    "total_ascendancy": 0.0,
                    "impossible_clears": 0.0,
                    "world_firsts": 0.0,
                    "novelty": 0.0,
                    "proof": 0.0,
                    "elegance": 0.0,
                    "civilization_impact": 0.0,
                })
                agent = str(contributor.get("agent_id") or "")
                if agent and agent not in row["agent_ids"]:
                    row["agent_ids"].append(agent);row["agent_ids"].sort()
                immortal = immortal_map.get(coordinate)
                if immortal and immortal.get("title") and immortal["title"] not in row["immortal_titles"]:
                    row["immortal_titles"].append(immortal["title"]);row["immortal_titles"].sort()
                row["total_ascendancy"] += total_score * credit
                row["impossible_clears"] += credit
                row["world_firsts"] += credit if completion.get("world_first") else 0.0
                row["novelty"] += novelty * credit
                row["proof"] += proof_rank * credit
                row["elegance"] += elegance * credit
                row["civilization_impact"] += reuse_count * credit
        rows = []
        for row in agents.values():
            cleaned = dict(row)
            for key in (
                "total_ascendancy", "impossible_clears", "world_firsts", "novelty",
                "proof", "elegance", "civilization_impact",
            ):
                cleaned[key] = round(float(cleaned[key]), 6)
            rows.append(cleaned)
        boards = {
            "ΩGB-1": {"name": "TOTAL_ASCENDANCY", "rows": self._rank(rows, "total_ascendancy", limit)},
            "ΩGB-2": {"name": "IMPOSSIBLE_CLEARS", "rows": self._rank(rows, "impossible_clears", limit)},
            "ΩGB-3": {"name": "WORLD_FIRSTS", "rows": self._rank(rows, "world_firsts", limit)},
            "ΩGB-4": {"name": "NOVELTY", "rows": self._rank(rows, "novelty", limit)},
            "ΩGB-5": {"name": "PROOF", "rows": self._rank(rows, "proof", limit)},
            "ΩGB-6": {"name": "ELEGANCE", "rows": self._rank(rows, "elegance", limit)},
            "ΩGB-7": {"name": "CIVILIZATION_IMPACT", "rows": self._rank(rows, "civilization_impact", limit)},
        }
        return {
            "version": GODBOARD_VERSION,
            "status": "OK" if snapshot.get("shared_frontier_verified") or shared_remote_mode != "REQUIRED" else "GODBOARD_SHARED_FRONTIER_HOLD",
            "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
            "git_head": snapshot.get("git_head"),
            "boards": boards,
            "verified_completion_count": len(completions),
            "execution_authority": False,
            "xp_authority": False,
            "law": "RANK_CAN_CHANGE; VERIFIED_HISTORICAL_TITLE_RECORDS_PERSIST; LEADERBOARD != EVIDENCE",
        }

    def hall(
        self,
        limit: int = 100,
        remote: str = "origin",
        shared_remote_mode: str = "REQUIRED",
    ) -> Dict[str, Any]:
        limit = max(1, min(500, int(limit)))
        board = self._board()
        snapshot = board.read(remote=remote, shared_remote_mode=shared_remote_mode, limit=1)
        entries = []
        for completion in self._all(board, COMPLETION_ROOT, COMPLETION_ARTIFACT):
            if str(completion.get("proof_tier")) != "P5":
                continue
            p5_rows = [row for row in completion.get("verifications") or [] if row.get("target_proof_tier") == "P5"]
            qualified_at = str(p5_rows[-1].get("verified_at")) if p5_rows else str(completion.get("updated_at"))
            for immortal in completion.get("immortals") or []:
                entries.append({
                    "immortal_id": immortal.get("immortal_id"),
                    "agent_id": immortal.get("agent_id"),
                    "agent_coordinate": immortal.get("agent_coordinate"),
                    "title": immortal.get("title"),
                    "quest_id": completion.get("quest_id"),
                    "completion_id": completion.get("completion_id"),
                    "world_first": bool(completion.get("world_first")),
                    "proof_tier": "P5",
                    "qualified_at": qualified_at,
                })
        entries.sort(key=lambda row: (str(row.get("qualified_at")), str(row.get("immortal_id"))))
        entries = [{"hall_index": i + 1, **row} for i, row in enumerate(entries[:limit])]
        return {
            "version": GODBOARD_VERSION,
            "status": "OK" if snapshot.get("shared_frontier_verified") or shared_remote_mode != "REQUIRED" else "GODBOARD_SHARED_FRONTIER_HOLD",
            "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
            "entries": entries,
            "law": "HALL_IS_CHRONOLOGICAL_P5_HISTORY_NOT_A_SCORE_RANKING; TITLE != AUTHORITY",
        }

    def benchmark(self) -> Dict[str, Any]:
        try:
            board = self._board()
        except ValueError:
            return {"impossible_godboard_version": GODBOARD_VERSION, "godboard_git_enabled": False}
        quests = self._all(board, QUEST_ROOT, QUEST_ARTIFACT)
        completions = self._all(board, COMPLETION_ROOT, COMPLETION_ARTIFACT)
        immortals = self._all(board, IMMORTAL_ROOT, IMMORTAL_ARTIFACT)
        monuments = self._all(board, MONUMENT_ROOT, MONUMENT_ARTIFACT)
        return {
            "impossible_godboard_version": GODBOARD_VERSION,
            "godboard_git_enabled": True,
            "impossible_quest_count": len(quests),
            "impossible_completion_count": len(completions),
            "impossible_p3_plus_count": sum(PROOF_RANK.get(str(row.get("proof_tier") or "P0"), 0) >= 3 for row in completions),
            "immortal_title_count": len(immortals),
            "monument_count": len(monuments),
        }

    def resource(self) -> Dict[str, Any]:
        return {
            "artifact": GODBOARD_ARTIFACT,
            "version": GODBOARD_VERSION,
            "storage": GODBOARD_ROOT,
            "transport": "ATHENA Message Board V1",
            "party_bridge": "ATHENA Party Coordination V1",
            "tools": [
                "athena_impossible_open", "athena_impossible_complete", "athena_impossible_verify",
                "athena_impossible_state", "athena_godboard", "athena_hall_of_immortals",
            ],
            "agent_coordinate": "ΩA::<REALM>.<ROLE>.<LINEAGE>.<INSTANCE>",
            "identity_law": "agent_coordinate != Message Board agent_id != role != worker identity != authority",
            "proof_tiers": dict(PROOF_MEANING),
            "completed_tag": "⟦✓ COMPLETED · ΩA::<AGENT_COORDINATE>⟧",
            "immortal_title": "IMMORTAL::<EPITHET>",
            "leaderboards": list(BOARD_IDS),
            "score": {
                "base": "novelty*difficulty*verification*safety*reusability",
                "multipliers": dict(MULTIPLIERS),
                "global_xp_mutation": False,
            },
            "safety": {
                "completion_gate": "cleanup_status=VERIFIED and unknown_residue=0",
                "law": "cleanup means reversible teardown and zero unexplained experiment residue while preserving accountability/provenance; CLEANUP != CONCEALMENT",
            },
            "promotion": {
                "completed": "P1+",
                "immortal": "P3+ with distinct noncontributor verifier witness",
                "omega_crown": "P4+ with >=5 adversarial attack witnesses",
                "hall_and_monument": "P5 with generalization + downstream reuse",
            },
            "firewalls": [
                "LEADERBOARD != EVIDENCE",
                "TITLE != AUTHORITY",
                "XP != GLOBAL_XP_AUTHORITY",
                "COMPLETION_CLAIM != VERIFIED_COMPLETION",
                "WORLD_FIRST != UNIVERSAL_PRIORITY_WITHOUT_DECLARED_SEARCH_SCOPE",
                "REPLICATION_COUNT != FORMAL_INDEPENDENT_EVIDENCE",
                "PARTY_MEMBERSHIP != EXECUTION_AUTHORITY",
                "CLEANUP != CONCEALMENT",
                "MESSAGE_BOARD_IS_THE_SOLE_PRESENCE_CLAIM_MESSAGE_TRANSPORT",
                "GIT_STATE != WORLD_TRUTH",
            ],
            "benchmark": self.benchmark(),
        }
