from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any, Dict, Iterable, Mapping, Optional

from .cohesion_mesh import COALITION_EVENT
from .message_board import _norm_target
from .party_coordination import PARTY_ARTIFACT, PARTY_ROOT

DEPENDENCY_CONE_VERSION = "COHESION.DEPENDENCY.CONE.1"
CHANGE_KINDS = {
    "GIT_RANGE", "GIT_PATHS", "CLAIM", "MESSAGE", "WORK_KEY",
    "TARGET", "DEPENDENCY", "COHESION_ENTRY", "DECISION",
}
NODE_PREFIXES = {
    "change", "agent", "claim", "work", "target", "goal", "dep",
    "request", "party", "message", "campaign", "decision",
}
SEED_RELATIONS = {
    "CHANGE_GIT_TARGET", "CHANGE_GIT_DEPENDENCY", "CHANGE_CLAIM",
    "CHANGE_AGENT", "CHANGE_WORK_KEY", "CHANGE_TARGET", "CHANGE_MESSAGE",
    "CHANGE_DEPENDENCY", "CHANGE_COHESION_ENTRY", "CHANGE_GOAL_REF",
    "CHANGE_DECISION", "CHANGE_CALLER_REF",
}
LAWS = [
    "DEPENDENCY_CONE != GLOBAL_RESET",
    "DEPENDENCY_CONE != REFRESH_EXECUTION",
    "DEPENDENCY_CONE != CLAIM_MUTATION",
    "DEPENDENCY_CONE != ACK_EXECUTION",
    "DEPENDENCY_CONE != ASSIGNMENT",
    "DEPENDENCY_CONE != FRESHNESS_TRAIN",
    "OBSERVED_EDGE != INFERRED_SEMANTIC_EDGE",
    "PARTY_MEMBERSHIP != UNIVERSAL_DEPENDENCY",
    "TASK_SIMILARITY != DEPENDENCY",
    "CHANGED_PATH_DISJOINT != SEMANTIC_INDEPENDENCE_PROOF",
    "TARGETED_INVALIDATION_REQUIRES_PROVEN_PATH",
    "UNKNOWN_IMPACT != NO_IMPACT",
    "MATA_UNAVAILABLE != INFERRED_FROM_PROSE",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm_text(value: Any) -> str:
    return " ".join(_text(value).casefold().split())


def _targets(values: Optional[Iterable[Any]]) -> list[str]:
    return sorted({_norm_target(_text(value)) for value in (values or []) if _norm_target(_text(value))})


def _refs(values: Optional[Iterable[Any]]) -> list[str]:
    return sorted({_text(value) for value in (values or []) if _text(value)})


def _node(prefix: str, value: Any) -> str:
    prefix = _text(prefix)
    raw = _text(value)
    if prefix == "work":
        raw = _norm_text(raw)
    elif prefix == "target":
        raw = _norm_target(raw)
    if prefix not in NODE_PREFIXES or not raw:
        raise ValueError(f"invalid node ref {prefix}:{raw}")
    return f"{prefix}:{raw}"


def _parse_node_ref(value: Any) -> str:
    raw = _text(value)
    if ":" not in raw:
        raise ValueError("caller node ref must use <type>:<value>")
    prefix, rest = raw.split(":", 1)
    return _node(prefix, rest)


def _edge_key(edge: Mapping[str, Any]) -> tuple:
    return (
        edge.get("src"), edge.get("relation"), edge.get("dst"),
        edge.get("standing"), tuple(edge.get("evidence_refs") or []),
        json.dumps(edge.get("metadata") or {}, sort_keys=True, separators=(",", ":")),
    )


def _add_edge(
    adjacency: Dict[str, list[dict]], edge_keys: set[tuple], src: str, relation: str, dst: str,
    *, standing: str = "OBSERVED_RUNTIME", evidence_refs: Optional[Iterable[Any]] = None,
    propagate: bool = True, metadata: Optional[Mapping[str, Any]] = None,
) -> None:
    edge = {
        "src": src, "relation": str(relation), "dst": dst, "standing": standing,
        "evidence_refs": _refs(evidence_refs), "propagate": bool(propagate),
        "metadata": dict(metadata or {}),
    }
    key = _edge_key(edge)
    if key in edge_keys:
        return
    edge_keys.add(key)
    adjacency[src].append(edge)


def _party_rows(board) -> list[dict]:
    root = board._root() / PARTY_ROOT
    if not root.exists():
        return []
    rows = []
    for path in sorted(root.glob("*.json")):
        value = board._read_json(path)
        if isinstance(value, dict) and value.get("artifact") == PARTY_ARTIFACT:
            rows.append(value)
    return rows


def _active_by_agent(snapshot: Mapping[str, Any]) -> Dict[str, dict]:
    return {str(row.get("agent_id")): dict(row) for row in (snapshot.get("active") or []) if row.get("agent_id")}


def _presence_public(row: Mapping[str, Any], parties: Iterable[str] = ()) -> dict:
    return {
        "agent_id": row.get("agent_id"), "claim_id": row.get("claim_id"), "mode": row.get("mode"),
        "task": row.get("task"), "work_key": row.get("work_key"), "targets": _targets(row.get("targets")),
        "join_of": row.get("join_of"), "party_ids": sorted(set(parties)),
    }


def _safe_git_ref(value: Any, field: str) -> str:
    ref = _text(value)
    if not ref or len(ref) > 200 or ref.startswith("-") or any(ch.isspace() for ch in ref):
        raise ValueError(f"{field} is not a safe Git ref")
    return ref


def _git_range(board, change: Mapping[str, Any]) -> tuple[dict, list[dict]]:
    base_ref = _safe_git_ref(change.get("base_ref"), "base_ref")
    head_ref = _safe_git_ref(change.get("head_ref"), "head_ref")
    unresolved: list[dict] = []
    try:
        base_sha = board.git._git("rev-parse", "--verify", f"{base_ref}^{{commit}}")
        head_sha = board.git._git("rev-parse", "--verify", f"{head_ref}^{{commit}}")
        output = board.git._git("diff", "--name-only", f"{base_sha}..{head_sha}")
    except Exception as exc:
        return {"status": "GIT_REF_HOLD", "base_ref": base_ref, "head_ref": head_ref, "error": str(exc), "changed_paths": []}, [{"code": "GIT_REF_UNAVAILABLE", "detail": str(exc)}]
    observed = _targets(output.splitlines())
    supplied = _targets(change.get("changed_paths"))
    if supplied and supplied != observed:
        unresolved.append({"code": "CALLER_CHANGED_PATHS_MISMATCH", "caller_supplied": supplied, "observed_git_diff": observed, "standing": "OBSERVED_GIT_DIFF_WINS"})
    return {"status": "OK", "base_ref": base_ref, "head_ref": head_ref, "base_sha": base_sha, "head_sha": head_sha, "changed_paths": observed}, unresolved


def _decode_party_message(party_runtime, event: Mapping[str, Any]) -> Optional[dict]:
    decoder = getattr(party_runtime, "_decode_party_message", None)
    if decoder is None:
        return None
    try:
        value = decoder(dict(event))
    except Exception:
        return None
    return dict(value) if isinstance(value, Mapping) else None


def _acked_by(events: Iterable[Mapping[str, Any]]) -> Dict[str, set[str]]:
    result: Dict[str, set[str]] = defaultdict(set)
    for event in events:
        if event.get("kind") != "ACK":
            continue
        message_id = _text((event.get("payload") or {}).get("message_id"))
        agent_id = _text(event.get("agent_id"))
        if message_id and agent_id:
            result[message_id].add(agent_id)
    return result


def _build_graph(cohesion_runtime, party_runtime, board, snapshot: Mapping[str, Any]) -> dict:
    adjacency: Dict[str, list[dict]] = defaultdict(list)
    edge_keys: set[tuple] = set()
    active = _active_by_agent(snapshot)
    party_memberships: Dict[str, set[str]] = defaultdict(set)
    party_goal_refs: Dict[tuple[str, str], list[str]] = {}
    entries: Dict[str, dict] = {}
    campaigns: Dict[str, dict] = {}
    messages: Dict[str, dict] = {}
    events = board._events()
    acked = _acked_by(events)

    for agent_id, row in sorted(active.items()):
        agent = _node("agent", agent_id)
        claim_id = _text(row.get("claim_id"))
        if claim_id:
            claim = _node("claim", claim_id)
            _add_edge(adjacency, edge_keys, claim, "CLAIM_ID", agent, evidence_refs=[claim_id])
        work_key = _text(row.get("work_key"))
        if work_key:
            _add_edge(adjacency, edge_keys, _node("work", work_key), "EXACT_WORK_KEY", agent, evidence_refs=[claim_id or agent_id], metadata={"work_key": work_key})
        for target in _targets(row.get("targets")):
            _add_edge(adjacency, edge_keys, _node("target", target), "TARGET_PATH", agent, evidence_refs=[claim_id or agent_id], metadata={"target": target})
        join_of = _text(row.get("join_of"))
        if join_of:
            _add_edge(adjacency, edge_keys, _node("claim", join_of), "JOIN_RELATION", agent, evidence_refs=[claim_id or agent_id], metadata={"join_of": join_of})

    for row in cohesion_runtime._active_requests(board):
        payload = dict(row.get("payload") or {})
        request_id = _text(payload.get("request_id")); agent_id = _text(payload.get("agent_id"))
        if not request_id or not agent_id:
            continue
        entries[request_id] = payload
        request = _node("request", request_id); agent = _node("agent", agent_id)
        event_id = _text((row.get("event") or {}).get("event_id"))
        _add_edge(adjacency, edge_keys, request, "COHESION_ENTRY_OWNER", agent, evidence_refs=[event_id or request_id])
        goal_ref = _text(payload.get("goal_ref"))
        if goal_ref:
            _add_edge(adjacency, edge_keys, _node("goal", goal_ref), "GOAL_REF", request, evidence_refs=[request_id])
        work_key = _text(payload.get("work_key"))
        if work_key:
            _add_edge(adjacency, edge_keys, _node("work", work_key), "EXACT_WORK_KEY", request, evidence_refs=[request_id])
        for target in _targets(payload.get("targets")):
            _add_edge(adjacency, edge_keys, _node("target", target), "TARGET_PATH", request, evidence_refs=[request_id], metadata={"target": target})
        for dependency in _refs(payload.get("dependencies")):
            _add_edge(adjacency, edge_keys, _node("dep", dependency), "DEPENDENCY_REF", request, evidence_refs=[request_id], metadata={"dependency_ref": dependency})
        if _text(payload.get("request_kind")).upper() == "OFFER":
            for provided in _refs(payload.get("provides")):
                dep = _node("dep", provided)
                _add_edge(adjacency, edge_keys, request, "PROVIDES_REF", dep, evidence_refs=[request_id], metadata={"provides_ref": provided})
                _add_edge(adjacency, edge_keys, agent, "PROVIDES_REF", dep, evidence_refs=[request_id], metadata={"provides_ref": provided})

    for party in _party_rows(board):
        party_id = _text(party.get("party_id"))
        if not party_id:
            continue
        party_node = _node("party", party_id)
        members = party.get("members") or {}
        if not isinstance(members, Mapping):
            continue
        for agent_id, member_raw in sorted(members.items()):
            member = dict(member_raw or {}); agent_id = _text(agent_id)
            if not agent_id:
                continue
            party_memberships[agent_id].add(party_id)
            goal_refs = _refs(member.get("goal_refs")); party_goal_refs[(party_id, agent_id)] = goal_refs
            _add_edge(adjacency, edge_keys, party_node, "PARTY_MEMBER", _node("agent", agent_id), evidence_refs=[party_id], propagate=False)
            for goal_ref in goal_refs:
                _add_edge(adjacency, edge_keys, _node("goal", goal_ref), "PARTY_GOAL_REF", _node("agent", agent_id), evidence_refs=[party_id], metadata={"party_id": party_id, "goal_ref": goal_ref})

    for event in cohesion_runtime._cohesion_events(board, COALITION_EVENT):
        payload = dict(cohesion_runtime._payload(event)); campaign_id = _text(payload.get("campaign_id"))
        if not campaign_id:
            continue
        campaigns[campaign_id] = payload; campaign = _node("campaign", campaign_id); event_id = _text(event.get("event_id"))
        for need_id in _refs(payload.get("need_ids")):
            _add_edge(adjacency, edge_keys, campaign, "COALITION_NEED", _node("request", need_id), evidence_refs=[event_id or campaign_id])
        for assignment in payload.get("assignments") or []:
            if not isinstance(assignment, Mapping):
                continue
            need_id = _text(assignment.get("need_id")); candidate = _text(assignment.get("assigned_candidate"))
            if need_id and candidate:
                _add_edge(adjacency, edge_keys, _node("request", need_id), "COALITION_ASSIGNMENT", _node("agent", candidate), evidence_refs=[event_id or campaign_id], metadata={"campaign_id": campaign_id})

    for event in events:
        if event.get("kind") != "MESSAGE":
            continue
        event_id = _text(event.get("event_id"))
        if not event_id:
            continue
        messages[event_id] = dict(event); message = _node("message", event_id)
        packet = _decode_party_message(party_runtime, event); party_message = bool(packet)
        for recipient in _refs(event.get("recipients")):
            _add_edge(adjacency, edge_keys, message, "MESSAGE_RECIPIENT", _node("agent", recipient), evidence_refs=[event_id], metadata={"message_id": event_id, "party_message": party_message, "ack_required": bool(party_message and recipient not in acked.get(event_id, set())), "already_acked": bool(recipient in acked.get(event_id, set()))})
        if packet:
            party_id = _text(packet.get("party_id"))
            if party_id:
                _add_edge(adjacency, edge_keys, _node("party", party_id), "PARTY_MESSAGE", message, evidence_refs=[event_id], propagate=False)
            for goal_ref in _refs(packet.get("goal_refs")):
                _add_edge(adjacency, edge_keys, _node("goal", goal_ref), "MESSAGE_GOAL_REF", message, evidence_refs=[event_id], metadata={"party_id": party_id})

    return {"adjacency": adjacency, "edge_keys": edge_keys, "active": active, "party_memberships": party_memberships, "party_goal_refs": party_goal_refs, "entries": entries, "campaigns": campaigns, "messages": messages, "events": events}


def _add_caller_edges(graph: dict, caller_edges: Optional[Iterable[Mapping[str, Any]]]) -> list[dict]:
    unresolved = []
    for index, raw in enumerate(caller_edges or []):
        if not isinstance(raw, Mapping):
            raise ValueError("caller_edges entries must be objects")
        src = _parse_node_ref(raw.get("src")); dst = _parse_node_ref(raw.get("dst")); relation = _text(raw.get("relation")); evidence = _refs(raw.get("evidence_refs"))
        if not relation:
            raise ValueError("caller edge relation is required")
        if not evidence:
            unresolved.append({"code": "CALLER_EDGE_WITHOUT_EVIDENCE", "index": index, "src": src, "relation": relation, "dst": dst, "standing": "CALLER_SUPPLIED_UNWITNESSED"})
        _add_edge(graph["adjacency"], graph["edge_keys"], src, relation, dst, standing="CALLER_SUPPLIED", evidence_refs=evidence, metadata={"caller_supplied": True})
    return unresolved


def _change_seed(board, graph: dict, change: Mapping[str, Any]) -> tuple[str, dict, list[dict], bool]:
    kind = _text(change.get("kind")).upper()
    if kind not in CHANGE_KINDS:
        raise ValueError("unsupported change.kind")
    normalized = {"kind": kind}; unresolved: list[dict] = []; git_change = kind in {"GIT_RANGE", "GIT_PATHS"}; change_node = _node("change", _digest(dict(change))[:20])

    def connect(node: str, relation: str, *, metadata: Optional[dict] = None):
        _add_edge(graph["adjacency"], graph["edge_keys"], change_node, relation, node, evidence_refs=[f"change:{kind}"], metadata=metadata or {})

    if kind == "GIT_RANGE":
        git_result, git_unresolved = _git_range(board, change); normalized.update(git_result); unresolved.extend(git_unresolved)
        for path in git_result.get("changed_paths") or []:
            connect(_node("target", path), "CHANGE_GIT_TARGET", metadata={"path": path}); connect(_node("dep", path), "CHANGE_GIT_DEPENDENCY", metadata={"path": path})
    elif kind == "GIT_PATHS":
        paths = _targets(change.get("changed_paths"))
        if not paths:
            raise ValueError("GIT_PATHS requires changed_paths")
        normalized["changed_paths"] = paths; normalized["standing"] = "CALLER_SUPPLIED_PATH_LIST"
        for path in paths:
            connect(_node("target", path), "CHANGE_GIT_TARGET", metadata={"path": path}); connect(_node("dep", path), "CHANGE_GIT_DEPENDENCY", metadata={"path": path})
    elif kind == "CLAIM":
        claim_id = _text(change.get("claim_id")); agent_id = _text(change.get("agent_id")); work_key = _text(change.get("work_key")); targets = _targets(change.get("targets")); status = _text(change.get("status_change"))
        if not claim_id:
            raise ValueError("CLAIM change requires claim_id")
        normalized.update({"claim_id": claim_id, "agent_id": agent_id or None, "work_key": work_key or None, "targets": targets, "status_change": status or None}); connect(_node("claim", claim_id), "CHANGE_CLAIM")
        if agent_id: connect(_node("agent", agent_id), "CHANGE_AGENT")
        if work_key: connect(_node("work", work_key), "CHANGE_WORK_KEY", metadata={"work_key": work_key})
        for target in targets: connect(_node("target", target), "CHANGE_TARGET", metadata={"target": target})
    elif kind == "MESSAGE":
        event_id = _text(change.get("event_id")); sender = _text(change.get("sender")); recipients = _refs(change.get("recipients"))
        if not event_id:
            raise ValueError("MESSAGE change requires event_id")
        normalized.update({"event_id": event_id, "sender": sender or None, "recipients": recipients, "requires_ack": bool(change.get("requires_ack"))}); connect(_node("message", event_id), "CHANGE_MESSAGE")
    elif kind == "WORK_KEY":
        work_key = _text(change.get("work_key"))
        if not work_key: raise ValueError("WORK_KEY change requires work_key")
        normalized["work_key"] = work_key; connect(_node("work", work_key), "CHANGE_WORK_KEY", metadata={"work_key": work_key})
    elif kind == "TARGET":
        targets = _targets(change.get("targets"))
        if not targets: raise ValueError("TARGET change requires targets")
        normalized["targets"] = targets
        for target in targets: connect(_node("target", target), "CHANGE_TARGET", metadata={"target": target})
    elif kind == "DEPENDENCY":
        refs = _refs(change.get("dependency_refs"))
        if not refs: raise ValueError("DEPENDENCY change requires dependency_refs")
        normalized["dependency_refs"] = refs
        for ref in refs: connect(_node("dep", ref), "CHANGE_DEPENDENCY", metadata={"dependency_ref": ref})
    elif kind == "COHESION_ENTRY":
        entry_id = _text(change.get("entry_id")); goal_ref = _text(change.get("goal_ref"))
        if not entry_id: raise ValueError("COHESION_ENTRY change requires entry_id")
        normalized.update({"entry_id": entry_id, "goal_ref": goal_ref or None}); connect(_node("request", entry_id), "CHANGE_COHESION_ENTRY")
        if goal_ref: connect(_node("goal", goal_ref), "CHANGE_GOAL_REF")
    else:
        decision_ref = _text(change.get("decision_ref")); refs = _refs(change.get("refs"))
        if not decision_ref: raise ValueError("DECISION change requires decision_ref")
        normalized.update({"decision_ref": decision_ref, "refs": refs, "standing": "CALLER_SUPPLIED_DECISION_REF"}); connect(_node("decision", decision_ref), "CHANGE_DECISION")
        for ref in refs:
            node = _parse_node_ref(ref); connect(node, "CHANGE_CALLER_REF", metadata={"source": decision_ref})
    return change_node, normalized, unresolved, git_change


def _enumerate_paths(adjacency: Mapping[str, list[dict]], root: str, max_depth: int) -> tuple[Dict[str, list[list[dict]]], set[str], bool, list[str]]:
    paths: Dict[str, list[list[dict]]] = defaultdict(list); visited_nodes = {root}; truncated = False; cutoff: set[str] = set(); queue: list[tuple[str, list[dict], int]] = [(root, [], 0)]; seen = {(root, tuple())}; expansions = 0
    while queue:
        node, path, semantic_depth = queue.pop(0); edges = sorted(adjacency.get(node, []), key=lambda edge: (edge["relation"], edge["dst"], edge["standing"], tuple(edge.get("evidence_refs") or [])))
        for edge in edges:
            next_path = path + [edge]; next_semantic = semantic_depth + (0 if edge["relation"] in SEED_RELATIONS else 1)
            if next_semantic > max_depth:
                truncated = True; cutoff.add(node); continue
            dst = str(edge["dst"]); visited_nodes.add(dst)
            if dst.startswith("agent:"):
                agent_id = dst.split(":", 1)[1]; paths[agent_id].append(next_path)
                if len(paths[agent_id]) >= 16: continue
            if not edge.get("propagate", True): continue
            signature = (dst, tuple((item["src"], item["relation"], item["dst"], item["standing"]) for item in next_path))
            if signature in seen: continue
            seen.add(signature); queue.append((dst, next_path, next_semantic)); expansions += 1
            if expansions >= 10000:
                truncated = True; cutoff.add(dst); queue.clear(); break
    return paths, visited_nodes, truncated, sorted(cutoff)


def _semantic_edges(path: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [edge for edge in path if str(edge.get("relation")) not in SEED_RELATIONS]


def _reason(edge: Mapping[str, Any]) -> str:
    relation = str(edge.get("relation") or ""); metadata = edge.get("metadata") or {}
    if relation in {"TARGET_PATH", "CHANGE_TARGET"}:
        path = _text(metadata.get("target") or metadata.get("path")); return f"TARGET_PATH:{path}" if path else relation
    if relation == "CHANGE_GIT_TARGET":
        path = _text(metadata.get("path")); return f"GIT_TARGET_PATH:{path}" if path else relation
    if relation in {"DEPENDENCY_REF", "CHANGE_DEPENDENCY", "CHANGE_GIT_DEPENDENCY"}:
        ref = _text(metadata.get("dependency_ref") or metadata.get("path")); return f"DEPENDENCY_REF:{ref}" if ref else relation
    if relation == "PROVIDES_REF":
        ref = _text(metadata.get("provides_ref")); return f"PROVIDES_REF:{ref}" if ref else relation
    return relation


def _actions(paths: list[list[dict]], *, git_change: bool) -> list[str]:
    relations = {str(edge.get("relation")) for path in paths for edge in path}; metadata = [edge.get("metadata") or {} for path in paths for edge in path]; actions: set[str] = set(); state_relations = relations - {"MESSAGE_RECIPIENT", "CHANGE_MESSAGE"}
    if state_relations:
        actions.update({"REHYDRATE", "HOLD_UNTIL_RECHECK"})
    if git_change:
        actions.add("RECHECK_GIT_HEAD")
    if relations & {"CLAIM_ID", "CHANGE_CLAIM", "CHANGE_AGENT", "EXACT_WORK_KEY", "JOIN_RELATION", "CHANGE_WORK_KEY"}:
        actions.add("RECHECK_CLAIM")
    if relations & {"TARGET_PATH", "CHANGE_TARGET", "CHANGE_GIT_TARGET"}:
        actions.add("RECHECK_TARGET")
    if relations & {"DEPENDENCY_REF", "PROVIDES_REF", "CHANGE_DEPENDENCY", "CHANGE_GIT_DEPENDENCY", "CALLER_SUPPLIED_EDGE"}:
        actions.add("RECHECK_DEPENDENCY")
    if relations & {"COHESION_ENTRY_OWNER", "COALITION_ASSIGNMENT", "COALITION_NEED", "CHANGE_COHESION_ENTRY", "DEPENDENCY_REF", "PROVIDES_REF"}:
        actions.add("RECHECK_COHESION_ENTRY")
    if relations & {"PARTY_GOAL_REF", "MESSAGE_GOAL_REF", "CHANGE_GOAL_REF"}:
        actions.add("RECHECK_PARTY")
    if "MESSAGE_RECIPIENT" in relations:
        actions.add("READ_MESSAGE")
        if any(bool(meta.get("ack_required")) for meta in metadata): actions.add("ACK_MESSAGE")
    return sorted(actions)


def _path_public(path: list[dict]) -> dict:
    semantic_depth = len(_semantic_edges(path)); return {"nodes": [path[0]["src"]] + [edge["dst"] for edge in path] if path else [], "relations": [edge["relation"] for edge in path], "reasons": sorted({_reason(edge) for edge in path}), "standing": sorted({str(edge.get("standing")) for edge in path}), "evidence_refs": sorted({ref for edge in path for ref in (edge.get("evidence_refs") or [])}), "semantic_depth": semantic_depth, "direct": semantic_depth <= 1}


def _lane_rows(graph: dict, agent_paths: Mapping[str, list[list[dict]]], *, git_change: bool):
    direct, transitive, all_rows = [], [], []
    for agent_id in sorted(agent_paths):
        presence = graph["active"].get(agent_id)
        if not presence: continue
        unique = {}
        for path in [_path_public(path) for path in agent_paths[agent_id]]: unique[json.dumps(path, sort_keys=True, separators=(",", ":"))] = path
        paths = sorted(unique.values(), key=lambda row: (row["semantic_depth"], row["relations"], row["nodes"])); is_direct = any(path["direct"] for path in paths); reasons = sorted({reason for path in paths for reason in path["reasons"]}); actions = _actions(agent_paths[agent_id], git_change=git_change)
        row = {**_presence_public(presence, graph["party_memberships"].get(agent_id, set())), "impact": "DIRECT" if is_direct else "TRANSITIVE", "reason_codes": reasons, "required_actions": actions, "propagation_paths": paths, "action_authority": False}
        all_rows.append(row); (direct if is_direct else transitive).append(row)
    return direct, transitive, all_rows


def _party_impacts(graph: dict, affected_agents: set[str]) -> list[dict]:
    parties: Dict[str, dict] = {}
    for agent_id in sorted(affected_agents):
        for party_id in sorted(graph["party_memberships"].get(agent_id, set())):
            row = parties.setdefault(party_id, {"party_id": party_id, "affected_member_ids": [], "affected_member_goal_refs": {}, "other_members_auto_invalidated": False, "law": "PARTY_MEMBERSHIP != UNIVERSAL_DEPENDENCY"}); row["affected_member_ids"].append(agent_id); row["affected_member_goal_refs"][agent_id] = list(graph["party_goal_refs"].get((party_id, agent_id), []))
    return [parties[key] for key in sorted(parties)]


def _visited_entries(graph: dict, visited_nodes: set[str]) -> list[dict]:
    rows = []
    for request_id, payload in sorted(graph["entries"].items()):
        if _node("request", request_id) not in visited_nodes: continue
        rows.append({"request_id": request_id, "request_kind": payload.get("request_kind"), "agent_id": payload.get("agent_id"), "goal_ref": payload.get("goal_ref"), "work_key": payload.get("work_key"), "targets": _targets(payload.get("targets")), "dependencies": _refs(payload.get("dependencies")), "provides": _refs(payload.get("provides")), "party_id": payload.get("party_id")})
    return rows


def _graph_digest(adjacency: Mapping[str, list[dict]]) -> str:
    edges = []
    for src in sorted(adjacency):
        for edge in adjacency[src]: edges.append({"src": edge["src"], "relation": edge["relation"], "dst": edge["dst"], "standing": edge["standing"], "evidence_refs": edge.get("evidence_refs") or [], "propagate": bool(edge.get("propagate")), "metadata": edge.get("metadata") or {}})
    edges.sort(key=lambda row: (row["src"], row["relation"], row["dst"], row["standing"], json.dumps(row["metadata"], sort_keys=True, separators=(",", ":")))); return _digest(edges)


def augment_dependency_cone_resource(resource: Mapping[str, Any]) -> dict:
    value = dict(resource or {}); tools = list(value.get("tools") or [])
    if "athena_cohesion_dependency_cone" not in tools: tools.append("athena_cohesion_dependency_cone")
    value["tools"] = tools; residual = []
    for item in value.get("residual") or []: residual.append("remaining C3 steering tools 13-15" if str(item) in {"remaining C3 steering tools 12-15", "C3 steering tools 12-15"} else item)
    value["residual"] = residual; laws = list(value.get("laws") or [])
    for law in LAWS:
        if law not in laws: laws.append(law)
    value["laws"] = laws; value["dependency_cone_version"] = DEPENDENCY_CONE_VERSION; value["targeted_invalidation"] = {"global_reset": False, "transitivity": "explicit observed/caller-supplied edges only", "mata_dependency_runtime": "UNAVAILABLE_NOT_IN_RUNTIME", "freshness_train_authority": False}
    return value


def dependency_cone(cohesion_runtime: Any, party_runtime: Any, *, change: Mapping[str, Any], caller_edges: Optional[Iterable[Mapping[str, Any]]] = None, max_depth: int = 4, remote: str = "origin", shared_remote_mode: str = "REQUIRED") -> dict:
    if not isinstance(change, Mapping): raise ValueError("change must be an object")
    max_depth = int(max_depth)
    if max_depth < 1 or max_depth > 8: raise ValueError("max_depth must be between 1 and 8")
    board = cohesion_runtime._board(); head_before_sync = board.git.head(); snapshot = board.read(limit=500, include_stale=False, remote=remote, shared_remote_mode=shared_remote_mode); head_after_sync = board.git.head(); shared_fresh = bool(snapshot.get("shared_frontier_verified"))
    if str(shared_remote_mode or "REQUIRED").upper() == "REQUIRED" and not shared_fresh:
        value = {"artifact": "ATHENA.COHESION.DEPENDENCY.CONE.V1", "version": DEPENDENCY_CONE_VERSION, "status": "COHESION_DEPENDENCY_CONE_SHARED_FRONTIER_HOLD", "classification": "SHARED_FRONTIER_HOLD", "change": dict(change), "directly_affected": [], "transitively_affected": [], "affected_entries": [], "parties": [], "required_actions": [], "unaffected_observed_lanes": [], "unresolved": [{"code": "SHARED_FRONTIER_UNVERIFIED"}], "propagation_paths": [], "max_depth": max_depth, "truncated": False, "shared_frontier_verified": False, "head_before_sync": head_before_sync, "head_after_sync": head_after_sync, "read_only": True, "mutation_performed": False, "execution_authority": False, "claim_authority": False, "ack_authority": False, "assignment_authority": False, "freshness_train_authority": False, "mata": {"runtime_available": False, "dependency_relation": "UNAVAILABLE_NOT_IN_RUNTIME", "law": "OBSERVED_RUNTIME_EDGE != MATA_CANONICAL_DEPENDENCY"}, "remote_sync": snapshot.get("remote_sync"), "laws": list(LAWS)}; value["decision_digest"] = _digest({"classification": value["classification"], "change": value["change"], "unresolved": value["unresolved"]}); return value
    graph = _build_graph(cohesion_runtime, party_runtime, board, snapshot); unresolved = _add_caller_edges(graph, caller_edges); root, normalized_change, change_unresolved, git_change = _change_seed(board, graph, change); unresolved.extend(change_unresolved)
    if normalized_change.get("status") == "GIT_REF_HOLD": classification = "GIT_REF_HOLD"; agent_paths = {}; visited_nodes = {root}; truncated = False; cutoff_nodes = []
    else: agent_paths, visited_nodes, truncated, cutoff_nodes = _enumerate_paths(graph["adjacency"], root, max_depth); classification = "TARGETED_CONE" if agent_paths else "NO_OBSERVED_AFFECTED_LANES"
    if truncated:
        unresolved.append({"code": "MAX_DEPTH_OR_PATH_LIMIT_REACHED", "max_depth": max_depth, "cutoff_nodes": cutoff_nodes}); classification = "TARGETED_CONE_TRUNCATED" if agent_paths else "UNKNOWN_IMPACT_TRUNCATED"
    direct, transitive, affected = _lane_rows(graph, agent_paths, git_change=git_change); affected_ids = {str(row["agent_id"]) for row in affected}; unaffected = [_presence_public(row, graph["party_memberships"].get(agent_id, set())) for agent_id, row in sorted(graph["active"].items()) if agent_id not in affected_ids]; parties = _party_impacts(graph, affected_ids); entries = _visited_entries(graph, visited_nodes); required_actions = [{"agent_id": row["agent_id"], "actions": row["required_actions"], "reason_codes": row["reason_codes"], "action_authority": False} for row in affected]
    if git_change and not affected:
        unresolved.append({"code": "UNOBSERVED_SEMANTIC_DEPENDENCY_POSSIBLE", "detail": "changed paths hit no observed exact target/dependency edge; disjoint paths are not semantic independence proof"})
        if classification == "NO_OBSERVED_AFFECTED_LANES": classification = "NO_OBSERVED_LANE_HIT_WITH_UNKNOWN_SEMANTIC_RESIDUE"
    propagation_paths = []
    for row in affected:
        for path in row["propagation_paths"]: propagation_paths.append({"agent_id": row["agent_id"], **path})
    propagation_paths.sort(key=lambda row: (row["semantic_depth"], row["agent_id"], row["relations"], row["nodes"])); graph_digest = _graph_digest(graph["adjacency"]); status = "COHESION_DEPENDENCY_CONE_HOLD" if classification in {"GIT_REF_HOLD", "SHARED_FRONTIER_HOLD"} else "COHESION_DEPENDENCY_CONE_OK"
    value = {"artifact": "ATHENA.COHESION.DEPENDENCY.CONE.V1", "version": DEPENDENCY_CONE_VERSION, "status": status, "classification": classification, "change": normalized_change, "directly_affected": direct, "transitively_affected": transitive, "affected_entries": entries, "parties": parties, "required_actions": required_actions, "unaffected_observed_lanes": unaffected, "unresolved": unresolved, "propagation_paths": propagation_paths, "max_depth": max_depth, "truncated": bool(truncated), "graph_digest": graph_digest, "shared_frontier_verified": shared_fresh, "git_head": head_after_sync, "head_before_sync": head_before_sync, "head_after_sync": head_after_sync, "read_sync_may_fast_forward": True, "read_only": True, "mutation_performed": False, "execution_authority": False, "claim_authority": False, "ack_authority": False, "assignment_authority": False, "freshness_train_authority": False, "mata": {"runtime_available": False, "dependency_relation": "UNAVAILABLE_NOT_IN_RUNTIME", "semantic_issue_ref": "demeet2k/Athena#233", "law": "OBSERVED_RUNTIME_EDGE != MATA_CANONICAL_DEPENDENCY"}, "remote_sync": snapshot.get("remote_sync"), "laws": list(LAWS)}; value["decision_digest"] = _digest({"classification": classification, "change": normalized_change, "directly_affected": direct, "transitively_affected": transitive, "affected_entries": entries, "parties": parties, "required_actions": required_actions, "unaffected_observed_lanes": unaffected, "unresolved": unresolved, "propagation_paths": propagation_paths, "max_depth": max_depth, "truncated": bool(truncated), "graph_digest": graph_digest, "mata": value["mata"]}); return value
