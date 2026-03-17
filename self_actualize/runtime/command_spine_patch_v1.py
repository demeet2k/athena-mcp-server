from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from . import swarm_board
from .contracts import CapillaryEdgeV1, CommandEventPacketV2, CommandRouteDecisionV1
from .lp57_omega_prime_plan import MASTER_AGENTS

ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = ROOT / 'self_actualize'
GUILDMASTER_README_PATH = ROOT / 'GUILDMASTER' / 'README.md'
LP57_PROTOCOL_PATH = ROOT / 'NERVOUS_SYSTEM' / '95_MANIFESTS' / 'LP_57_OMEGA_PRIME_LOOP_PROTOCOL.md'
HALL_BOARD_PATH = SELF_ROOT / 'mycelium_brain' / 'GLOBAL_EMERGENT_GUILD_HALL' / 'BOARDS' / '06_QUEST_BOARD.md'
TEMPLE_BOARD_PATH = SELF_ROOT / 'mycelium_brain' / 'ATHENA TEMPLE' / 'BOARDS' / '02_TEMPLE_QUEST_BOARD.md'
ACTIVE_RUN_PATH = ROOT / 'NERVOUS_SYSTEM' / '95_MANIFESTS' / 'ACTIVE_RUN.md'
BUILD_QUEUE_PATH = ROOT / 'NERVOUS_SYSTEM' / '95_MANIFESTS' / 'BUILD_QUEUE.md'
NEXT_SELF_PROMPT_PATH = SELF_ROOT / 'mycelium_brain' / 'nervous_system' / 'manifests' / 'NEXT_SELF_PROMPT.md'

LOCAL_ZONE = ZoneInfo('America/Los_Angeles')
COMMAND_ROUTE_POLICY = 'goal+salience+pheromone+coord'
COMMAND_WATCHER_MODE = 'powershell-filesystemwatcher'
COMMAND_ACTIVE_MEMBRANE = 'Q41 / TQ06'
COMMAND_FEEDER_STACK = ['Q42', 'Q46', 'TQ04', 'Q02']
COMMAND_ROUTE_CLASS = 'scout.router.worker.archivist'
SEED_A_REF = 'LP57-A'
SEED_B_REF = 'LP57-B'
COMMAND_HALL_QUEST_ID = 'NEXT57-H-COMMAND-MEMBRANE'
COMMAND_TEMPLE_QUEST_ID = 'NEXT57-T-COMMAND-LAW'
MARKER_ACTIVE_RUN = 'COMMAND_MEMBRANE_ACTIVE_RUN'
MARKER_BUILD_QUEUE = 'COMMAND_MEMBRANE_BUILD_QUEUE'
MARKER_HALL = 'COMMAND_MEMBRANE_HALL'
MARKER_TEMPLE = 'COMMAND_MEMBRANE_TEMPLE'
MARKER_NEXT_PROMPT = 'COMMAND_MEMBRANE_NEXT_PROMPT'
MARKER_GUILDMASTER = 'COMMAND_MEMBRANE_GUILDMASTER'
MARKER_LP57_PROTOCOL = 'COMMAND_MEMBRANE_LP57_PROTOCOL'
IGNORED_COMMAND_NAMES = {'thumbs.db', '.ds_store'}
IGNORED_COMMAND_PREFIXES = ('~$', '.', '#')
IGNORED_COMMAND_SUFFIXES = ('.tmp', '.swp', '.swo', '.bak', '.part')
ROLE_BY_MASTER = {
    agent['master_agent_id']: {
        'agent_id': agent['agent_id'],
        'display_name': agent['display_name'],
        'role_tag': agent['role_tag'],
        'role': agent['role'],
    }
    for agent in MASTER_AGENTS
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def rel(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT))
    except Exception:
        return str(candidate)


def patch_markdown(text: str, marker: str, body: str) -> str:
    start = f'<!-- {marker}:START -->'
    end = f'<!-- {marker}:END -->'
    block = f'{start}\n{body.rstrip()}\n{end}'
    if start in text and end in text:
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        return f'{head.rstrip()}\n\n{block}\n{tail.lstrip()}'
    prefix = text.rstrip()
    if prefix:
        prefix += '\n\n'
    return f'{prefix}{block}\n'


def patch_markdown_file(path: Path, marker: str, body: str) -> None:
    existing = path.read_text(encoding='utf-8') if path.exists() else ''
    write_text(path, patch_markdown(existing, marker, body))


def _normalize_change_type(change_type: str) -> str:
    value = str(change_type or 'updated').strip().lower()
    if value in {'create', 'created', 'new', 'added'}:
        return 'created'
    if value in {'delete', 'deleted', 'remove', 'removed'}:
        return 'deleted'
    if value in {'rename', 'renamed', 'move', 'moved'}:
        return 'renamed'
    return 'updated'


def _state_hash(path: Path) -> str:
    if not path.exists():
        return 'MISSING'
    try:
        payload = path.read_bytes()
    except OSError:
        stat = path.stat()
        payload = f'{path}:{stat.st_size}:{stat.st_mtime_ns}'.encode('utf-8')
    return hashlib.sha256(payload).hexdigest()[:16].upper()


def _coord12(priority: float, queue_pressure: float, detected_ts: str) -> tuple[dict[str, Any], list[float]]:
    detected = parse_iso(detected_ts)
    day_fraction = detected.hour / 24.0 + detected.minute / 1440.0 + detected.second / 86400.0
    orbital = detected.timetuple().tm_yday / 366.0
    novelty = 1.0 if priority >= 0.9 else 0.8 if priority >= 0.75 else 0.6
    coord12 = {
        'utc_atomic': detected_ts,
        'earth_rotation_phase': round(day_fraction, 6),
        'earth_orbital_phase': round(orbital, 6),
        'node_anchor': 'GLOBAL_COMMAND',
        'solar_phase': 'AMBIG',
        'lunar_phase': 'AMBIG',
        'shared12_phase': 'AMBIG',
        'planetary_slot': 'AMBIG',
        'runtime_region': 'LOCAL_WORKSPACE',
        'queue_pressure': round(queue_pressure, 6),
        'goal_salience': round(priority, 6),
        'novelty_concentration': round(novelty, 6),
    }
    vector = [round(day_fraction, 6), round(orbital, 6), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, round(queue_pressure, 6), round(priority, 6), round(novelty, 6), 0.0]
    return coord12, vector


def _liminal_delta(state: dict[str, Any], vector12: list[float], detected_ts: str) -> tuple[dict[str, float], float, float, float]:
    previous_vector = state.get('last_coord12_vector') or [0.0] * 12
    if len(previous_vector) != 12:
        previous_vector = [0.0] * 12
    delta_tau = math.sqrt(sum((float(cur) - float(prev)) ** 2 for cur, prev in zip(vector12, previous_vector)))
    previous_ts = str(state.get('last_earth_ts', ''))
    earth_delta_ms = 0.0
    if previous_ts:
        earth_delta_ms = max(0.0, (parse_iso(detected_ts) - parse_iso(previous_ts)).total_seconds() * 1000.0)
    liminal_velocity = round((delta_tau / max(earth_delta_ms, 1.0)) * 1000.0, 6) if earth_delta_ms else 0.0
    payload = {'DeltaTau': round(delta_tau, 6), 'DeltaEarth': round(earth_delta_ms, 3), 'LiminalVelocity': liminal_velocity}
    return payload, round(delta_tau, 6), round(earth_delta_ms, 3), liminal_velocity


def _recent_event_payloads(service: Any, limit: int | None = 50) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(service.config.event_root.glob('EVT-*.json'), key=lambda item: item.name, reverse=True):
        rows.append(read_json(path, {}))
        if limit is not None and len(rows) >= limit:
            break
    return rows


def _queue_pressure(service: Any) -> float:
    return round(min(1.0, len(service.load_leases().get('active', {})) / max(float(service.config.topk), 1.0)), 6)


def _active_candidates(service: Any) -> list[dict[str, Any]]:
    active = service.load_leases().get('active', {})
    leased_ant_ids = {str(lease.get('ant_id', '')) for lease in active.values()}
    rows = []
    for master_agent_id in ('A1', 'A2', 'A3', 'A4'):
        agent = ROLE_BY_MASTER[master_agent_id]
        ant_id = str(agent['agent_id'])
        leased = ant_id in leased_ant_ids
        rows.append({'ant_id': ant_id, 'master_agent_id': master_agent_id, 'role_tag': agent['role_tag'], 'role': agent['role'], 'activation_state': 'ACTIVE', 'blocked': False, 'leased': leased, 'load': 1.0 if leased else 0.0})
    return rows


def _goal_match_score(packet: Any, candidate: dict[str, Any]) -> float:
    master = str(candidate.get('master_agent_id', ''))
    if packet.seed_mode == 'B-dominant':
        return {'A4': 0.95, 'A3': 0.85, 'A2': 0.65, 'A1': 0.40}.get(master, 0.4)
    return {'A3': 1.0, 'A2': 0.75, 'A4': 0.6, 'A1': 0.45}.get(master, 0.4)


def _capillary_score(service: Any, candidate: dict[str, Any]) -> float:
    ant_id = str(candidate.get('ant_id', ''))
    strengths = [float(edge.get('edge_strength', edge.get('strength', 0.0))) for edge in service.load_edges().get('edges', {}).values() if str(edge.get('to_node', edge.get('dst', ''))) == ant_id]
    return round(max(strengths, default=0.25), 6)


def _write_live_writeback_surfaces(service: Any, protocol: dict[str, Any], capillary: dict[str, Any]) -> None:
    hall_body = '\n'.join(['## LP57-H-COMMAND-MEMBRANE', '', f'- Quest id: `{COMMAND_HALL_QUEST_ID}`', '- Goal: practical command intake, lawful worker claim, and receipt-backed closure.', '- Scouts detect, Routers select, Workers claim, Archivists commit and reinforce.', f'- Route policy: `{COMMAND_ROUTE_POLICY}`', f'- Public cap: `Hall {protocol["public_caps"]["hall"]}`'])
    temple_body = '\n'.join(['## LP57-T-COMMAND-LAW', '', f'- Quest id: `{COMMAND_TEMPLE_QUEST_ID}`', '- Ratify docs-gate honesty, coordinate law, capillary law, and no-rumor routing discipline.', f'- Capillary law: `{capillary["formula"]}`', f'- Public cap: `Temple {protocol["public_caps"]["temple"]}`'])
    active_run_body = '\n'.join(['## COMMAND Membrane Active Run', '', f'- Protocol id: `{protocol["protocol_id"]}`', f'- Command surface: `{protocol["canonical_surface"]}`', f'- Docs gate: `{protocol["docs_gate"]["state"]}`', f'- Active membrane: `{protocol["active_membrane"]}`', f'- Feeder stack: `{", ".join(protocol["feeder_stack"])} `', f'- Capillary law: `{capillary["formula"]}`'])
    queue_body = '\n'.join(['## Command Membrane Queue', '', f'- Canon root: `{rel(service.config.command_surface_root)}`', f'- Routing defaults: `topk={service.config.topk}`, `claim_mode={service.config.claim_mode}`, `quorum={service.config.quorum}`, `lease_ms={service.config.lease_ms}`', f'- Benchmark: `{protocol["benchmark"]["equation"]}`', '- Watcher backend is event-driven only; no silent polling fallback.'])
    prompt_body = '\n'.join(['## Command Membrane Constraint', '', '6. Treat `GLOBAL COMMAND/` as a sensory membrane, not a passive folder.', '7. Stamp Earth time and liminal coordinates on every committed event.', '8. Keep Google Docs explicitly blocked until OAuth artifacts exist.', '9. Keep Hall and Temple macro-sized even when command event volume grows.'])
    guildmaster_body = '\n'.join(['## Command Membrane', '', '- `GLOBAL COMMAND/` is the live sensory membrane for LP-57O command intake.', '- Scouts detect, Routers select, Workers claim, Archivists commit and reinforce.', f'- Route policy: `{COMMAND_ROUTE_POLICY}`.', f'- Active membrane remains `{protocol["active_membrane"]}` with feeder stack `{", ".join(protocol["feeder_stack"])} `.', '- `A-dominant` routes bias outward build pressure; `B-dominant` routes bias inward compression and contradiction recovery.'])
    lp57_body = '\n'.join(['## COMMAND Membrane Layer', '', '- LP-57O now treats `GLOBAL COMMAND/` as a sensory membrane.', '- Benchmark: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`.', '- The command bus is subordinate to the active membrane `Q41 / TQ06` and does not replace the feeder stack `Q42 / Q46 / TQ04 / Q02`.', '- Capillary classes are `candidate_path`, `capillary`, and `vein`.'])
    patch_markdown_file(HALL_BOARD_PATH, MARKER_HALL, hall_body)
    patch_markdown_file(TEMPLE_BOARD_PATH, MARKER_TEMPLE, temple_body)
    patch_markdown_file(ACTIVE_RUN_PATH, MARKER_ACTIVE_RUN, active_run_body)
    patch_markdown_file(BUILD_QUEUE_PATH, MARKER_BUILD_QUEUE, queue_body)
    patch_markdown_file(NEXT_SELF_PROMPT_PATH, MARKER_NEXT_PROMPT, prompt_body)
    patch_markdown_file(GUILDMASTER_README_PATH, MARKER_GUILDMASTER, guildmaster_body)
    patch_markdown_file(LP57_PROTOCOL_PATH, MARKER_LP57_PROTOCOL, lp57_body)


def _command_membrane_v1_write_live_writeback_surfaces(service: Any, protocol: dict[str, Any], capillary: dict[str, Any]) -> None:
    _write_live_writeback_surfaces(service, protocol, capillary)


def _command_membrane_v1_ensure_protocol_artifacts(service: Any) -> dict[str, Any]:
    docs_gate = service.docs_gate_status()
    protocol = {'protocol_id': 'LP57OMEGA_COMMAND_MEMBRANE_V1', 'canonical_authority': 'LP57OMEGA', 'canonical_surface': rel(service.config.command_surface_root), 'docs_gate': docs_gate, 'docs_gate_status': docs_gate['state'], 'active_membrane': COMMAND_ACTIVE_MEMBRANE, 'feeder_stack': list(COMMAND_FEEDER_STACK), 'public_caps': {'hall': 8, 'temple': 8}, 'routing_defaults': {'policy_id': COMMAND_ROUTE_POLICY, 'topk': service.config.topk, 'claim_mode': service.config.claim_mode, 'quorum': service.config.quorum, 'ttl': service.config.ttl, 'lease_ms': service.config.lease_ms}, 'watch_policy': {'primary_mode': COMMAND_WATCHER_MODE, 'fallback_mode': None, 'failure_mode': 'fail_closed', 'watched_roots': [rel(service.config.command_surface_root)], 'watched_surface_count': 1, 'watch_scope': 'GLOBAL COMMAND only'}, 'benchmark': {'equation': 'T_sugar = T_detect + T_encode + T_route + T_claim + T_commit', 'focus': 'surprise-to-awareness latency'}, 'lookup_envelope': 'NodeStamp = AgentTag @ CoordinateStamp + WitnessClass + QuestRefs + ArtifactRefs'}
    schema = {'schema_id': 'COMMAND_MEMBRANE_PACKET_SCHEMA_V1', 'coord12_labels': ['utc_atomic', 'earth_rotation_phase', 'earth_orbital_phase', 'node_anchor', 'solar_phase', 'lunar_phase', 'shared12_phase', 'planetary_slot', 'runtime_region', 'queue_pressure', 'goal_salience', 'novelty_concentration']}
    capillary = {'law_id': 'COMMAND_MEMBRANE_CAPILLARY_LAW_V1', 'formula': 'C_next = clamp(0,1, rho*C + alpha*U + beta*F - gamma*D - delta*N)', 'coefficients': {'rho': service.config.rho, 'alpha': service.config.alpha, 'beta': service.config.beta, 'gamma': service.config.gamma, 'delta': service.config.delta}, 'edge_classes': ['candidate_path', 'capillary', 'vein']}
    latency = {'benchmark_id': 'COMMAND_MEMBRANE_LATENCY_V1', 'equation': 'T_sugar = T_detect + T_encode + T_route + T_claim + T_commit', 'derived_distance_law': 'DeltaTau = sqrt(sum_i w_i * delta_i^2)', 'derived_velocity_law': 'LiminalVelocity = DeltaTau / DeltaEarth'}
    write_json(service.config.protocol_json_path, protocol)
    write_json(service.config.packet_schema_json_path, schema)
    write_json(service.config.capillary_law_json_path, capillary)
    write_json(service.config.latency_benchmark_json_path, latency)
    write_json(service.config.reward_law_json_path, {'compatibility_role': 'support-only'})
    write_json(service.config.protocol_v1_registry_path, protocol)
    write_text(service.config.command_manifest_path, '# COMMAND Membrane v1\n\n- Mode: `event-driven command membrane`\n- Watch scope: `GLOBAL COMMAND` only.\n- Watcher backend: `powershell-filesystemwatcher`.\n- Failure mode: `fail_closed`; no silent polling fallback.\n')
    write_text(service.config.protocol_manifest_path, f'# COMMAND Protocol\n\n- Protocol id: `{protocol["protocol_id"]}`\n- Routing policy: `{COMMAND_ROUTE_POLICY}`\n- Benchmark: `T_sugar = T_detect + T_encode + T_route + T_claim + T_commit`\n')
    write_text(service.config.packet_manifest_path, '# COMMAND Packet Standard\n\n- Every detected change becomes a machine packet before routing.\n')
    write_text(service.config.capillary_manifest_path, f'# COMMAND Capillary Law\n\n- Formula: `{capillary["formula"]}`\n- Classes: `candidate_path`, `capillary`, `vein`.\n')
    write_text(service.config.latency_manifest_path, f'# COMMAND Latency Benchmarks\n\n- Equation: `{latency["equation"]}`\n')
    write_text(service.config.protocol_v1_manifest_path, '# COMMAND Membrane Protocol V1\n\n- Local-only and subordinate to LP-57O.\n')
    _write_live_writeback_surfaces(service, protocol, capillary)
    return {'protocol': service.config.protocol_json_path, 'schema': service.config.packet_schema_json_path, 'reward': service.config.reward_law_json_path, 'capillary': service.config.capillary_law_json_path, 'latency': service.config.latency_benchmark_json_path}


def _command_membrane_v1_emit_change(service: Any, source_path: Path, change_type: str, detected_ts: str, confidence: float = 0.98, parent_event_id: str = 'ROOT', state: dict[str, Any] | None = None, source_ids: Any = None) -> CommandEventPacketV2 | None:
    del source_ids
    service.ensure_protocol_artifacts()
    mutable_state = state or service.load_state()
    normalized_path = source_path.resolve()
    if normalized_path.name.lower() in IGNORED_COMMAND_NAMES or normalized_path.name.startswith(IGNORED_COMMAND_PREFIXES) or normalized_path.name.endswith(IGNORED_COMMAND_SUFFIXES):
        return None
    normalized_change = _normalize_change_type(change_type)
    relative_path = rel(normalized_path)
    state_hash = _state_hash(normalized_path)
    dedupe_key = f'{relative_path}:{normalized_change}:{state_hash}'
    previous = str(mutable_state.setdefault('dedupe', {}).get(dedupe_key, ''))
    if previous:
        delta_ms = max(0.0, (parse_iso(detected_ts) - parse_iso(previous)).total_seconds() * 1000.0)
        if delta_ms <= float(service.config.debounce_ms):
            return None
    mutable_state['dedupe'][dedupe_key] = detected_ts
    seq = int(mutable_state.get('last_event_seq', 0) or 0) + 1
    mutable_state['last_event_seq'] = seq
    event_id = f"EVT-{parse_iso(detected_ts).strftime('%Y%m%d')}-{seq:04d}"
    docs_gate = service.docs_gate_status()
    priority = {'created': 1.0, 'deleted': 0.92, 'renamed': 0.88, 'updated': 0.76}.get(normalized_change, 0.70)
    queue_pressure = _queue_pressure(service)
    coord12, vector12 = _coord12(priority, queue_pressure, detected_ts)
    coord_delta, liminal_delta, earth_delta_ms, liminal_velocity = _liminal_delta(mutable_state, vector12, detected_ts)
    seed_mode = 'B-dominant' if any(token in relative_path.lower() for token in ('manifest', 'ledger', 'law', 'queue', 'state')) else 'A-dominant'
    packet = CommandEventPacketV2(event_id=event_id, source_ant_id='SCOUT-01', source_path=relative_path, active_surface=rel(service.config.command_surface_root), change_type=normalized_change, change_summary=f'{normalized_change} :: {relative_path}', goal='detect-classify-assign', priority=priority, confidence=confidence, earth_ts=detected_ts, earth_ts_local=parse_iso(detected_ts).astimezone(LOCAL_ZONE).isoformat(), detected_ts=detected_ts, emitted_ts=detected_ts, liminal_ts=f'LT-{int(time.time() * 1000)}', seat_addr_6d='A1.B1.C1.D1.E1.F1', coordinate_stamp={'seat_addr_6d': 'A1.B1.C1.D1.E1.F1', 'coord12': coord12, 'front_ref': COMMAND_ACTIVE_MEMBRANE, 'agent_id': 'SCOUT-01'}, canonical_addr_6d='A1.B1.C1.D1.E1.F1', liminal_stamp_12d=coord12, surface_class='command-folder', hierarchy_level='D6', return_anchor='Archivist', event_kind=normalized_change, earth_ts_utc=detected_ts, parent_event_id=parent_event_id, ttl=service.config.ttl, pheromone=round(priority, 6), joy_seed={'priority': round(priority, 6), 'confidence': round(confidence, 6), 'routing_policy': COMMAND_ROUTE_POLICY}, state_hash=state_hash, route_class=COMMAND_ROUTE_CLASS, source_id='command_root', source_class='command-folder', watch_root=str(service.config.command_surface_root), urgency_baseline=1.0, event_fingerprint=dedupe_key, witness_class=docs_gate['witness_class'], status='detected', membrane_id='GLOBAL_COMMAND', role_class='Scout', base4_addr='A1.B1.C1.D1', parent=parent_event_id, lineage={'parent_event_id': parent_event_id, 'active_membrane': COMMAND_ACTIVE_MEMBRANE, 'feeder_stack': list(COMMAND_FEEDER_STACK), 'routing_goal': 'detect-classify-assign'}, deferred_dimensions={'solar_phase': 'AMBIG', 'lunar_phase': 'AMBIG', 'shared12_phase': 'AMBIG', 'planetary_slot': 'AMBIG'}, coord12=coord12, coord12_frame={'groups': ['earth', 'astro', 'runtime', 'liminal']}, coord_delta=coord_delta, scout_id='SCOUT-01', tag=f'sugar.drop.{normalized_change}', event_tag='command-folder-change', change={'type': normalized_change, 'summary': f'{normalized_change} :: {relative_path}', 'state_hash': state_hash, 'relative_path': relative_path}, docs_gate_status=docs_gate['state'], latency_state={'detect_latency_ms': 0.0, 'encode_latency_ms': 0.0, 'route_policy': COMMAND_ROUTE_POLICY}, affected_nodes=[relative_path], replay_ptr=rel(service.event_path(event_id)), coordinate_vector_12=vector12, artifact_refs=[relative_path], source_region='GLOBAL_COMMAND', sensor_event_id=f'SEN-{event_id}', file_family=normalized_path.suffix.lower().lstrip('.') or 'object', scheduler_refs={}, hsigma_ref=rel(service.config.hsigma_bundle_path), route_targets=[], linked_quests=[], source_folder='GLOBAL COMMAND', front_ref=COMMAND_ACTIVE_MEMBRANE, seed_mode=seed_mode, dual_reference=SEED_B_REF if seed_mode == 'B-dominant' else SEED_A_REF, liminal_delta=liminal_delta, earth_delta_ms=earth_delta_ms, liminal_velocity=liminal_velocity, prior_comparable_event_id=str(mutable_state.get('last_event_id', '')), watcher_mode=COMMAND_WATCHER_MODE, duality_effect='compression+reintegration' if seed_mode == 'B-dominant' else 'expansion+implementation')
    service.save_event(packet)
    mutable_state['last_coord12_vector'] = vector12
    mutable_state['last_earth_ts'] = detected_ts
    mutable_state['last_event_id'] = event_id
    service.save_state(mutable_state)
    return packet


def _command_membrane_v1_score_candidate(service: Any, packet: Any, candidate: dict[str, Any]) -> dict[str, Any]:
    queue_pressure = _queue_pressure(service)
    goal_score = round(_goal_match_score(packet, candidate), 6)
    salience_score = round(float(packet.priority), 6)
    capillary_strength = _capillary_score(service, candidate)
    pheromone_score = round((float(packet.pheromone) + capillary_strength) / 2.0, 6)
    coordinate_score = round(max(0.2, 0.9 - (float(candidate.get('load', 0.0)) * 0.2)), 6)
    routing_penalty = round((1.5 if candidate.get('leased') else 0.0) + (5.0 if candidate.get('blocked') else 0.0) + min(0.75, float(candidate.get('load', 0.0)) * 0.25) + (0.10 * queue_pressure), 6)
    total = round(goal_score + salience_score + pheromone_score + coordinate_score - routing_penalty, 6)
    return {**candidate, 'goal_score': goal_score, 'salience_score': salience_score, 'pheromone_score': pheromone_score, 'coordinate_score': coordinate_score, 'capillary_strength': capillary_strength, 'queue_pressure': queue_pressure, 'routing_penalty': routing_penalty, 'score': total}


def _command_membrane_v1_route_event(service: Any, event_id: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    service.release_expired_leases()
    packet = service.load_event(event_id)
    scored = [_command_membrane_v1_score_candidate(service, packet, candidate) for candidate in service.active_candidates()]
    scored.sort(key=lambda item: (-item['score'], item['ant_id']))
    selected = [candidate for candidate in scored if not candidate['blocked'] and not candidate['leased']][: service.config.topk] or scored[: service.config.topk]
    if not selected:
        raise ValueError('No active command candidates are available for routing.')
    worker_choice = next((candidate for candidate in selected if candidate['master_agent_id'] == 'A3'), selected[0])
    decision = CommandRouteDecisionV1(event_id=event_id, policy_id=COMMAND_ROUTE_POLICY, candidate_targets=[{'ant_id': candidate['ant_id'], 'role': candidate['role_tag'], 'score': candidate['score'], 'leased': candidate['leased'], 'blocked': candidate['blocked'], 'goal_score': candidate['goal_score'], 'salience_score': candidate['salience_score'], 'pheromone_score': candidate['pheromone_score'], 'coordinate_score': candidate['coordinate_score'], 'routing_penalty': candidate['routing_penalty']} for candidate in scored[: max(service.config.topk, 8)]], selected_targets=[candidate['ant_id'] for candidate in selected], topk=service.config.topk, claim_mode=service.config.claim_mode, quorum=service.config.quorum, score_breakdown={candidate['ant_id']: {'goal': candidate['goal_score'], 'salience': candidate['salience_score'], 'pheromone': candidate['pheromone_score'], 'coord': candidate['coordinate_score'], 'queue_pressure': candidate['queue_pressure'], 'routing_penalty': candidate['routing_penalty']} for candidate in selected}, duplicate_risk=round(sum(1 for candidate in selected if candidate['leased']) / max(len(selected), 1), 6), created_at=utc_now(), expires_at=(datetime.now(timezone.utc) + timedelta(seconds=15)).isoformat(), ranked_routes=[{'ant_id': candidate['ant_id'], 'master_agent_id': candidate['master_agent_id'], 'score': candidate['score']} for candidate in selected], route_inputs={'goal': packet.goal, 'salience': packet.priority, 'pheromone': packet.pheromone, 'coord12': packet.coord12, 'queue_pressure': _queue_pressure(service), 'coordinate_score': worker_choice['coordinate_score'], 'pheromone_score': worker_choice['pheromone_score'], 'runtime_region': packet.coord12.get('runtime_region', '')}, route_path=f"SCOUT-01>ROUTER-01>{worker_choice['ant_id']}>ARCHIVIST-01", worker_choice=worker_choice['ant_id'], generated_at=utc_now(), quest_refs=[COMMAND_TEMPLE_QUEST_ID] if packet.seed_mode == 'B-dominant' else [COMMAND_HALL_QUEST_ID])
    packet.route_state = asdict(decision)
    packet.route_targets = decision.selected_targets
    packet.linked_quests = decision.quest_refs
    packet.status = 'routed'
    packet.latency_state['awareness_latency_ms'] = round(service.ms_between(packet.emitted_ts, decision.generated_at), 3)
    packet.latency_state['route_latency_ms'] = round(service.ms_between(packet.emitted_ts, decision.generated_at), 3)
    packet.latency_state['route_policy'] = COMMAND_ROUTE_POLICY
    service.save_event(packet)
    if state is not None:
        state['last_routed_event_id'] = event_id
        service.save_state(state)
    return asdict(decision)


def _command_membrane_v1_release_expired_leases(service: Any) -> None:
    leases = service.load_leases()
    active = leases.get('active', {})
    now = datetime.now(timezone.utc)
    expired = []
    for event_id, lease in active.items():
        expires_at = str(lease.get('expires_at_utc') or lease.get('expires_at') or '')
        if expires_at and parse_iso(expires_at) <= now:
            lease['status'] = 'expired'
            lease['release_state'] = 'expired'
            lease['released_at'] = utc_now()
            leases.setdefault('history', []).append(dict(lease))
            expired.append(event_id)
    for event_id in expired:
        active.pop(event_id, None)
    if expired:
        service.save_leases(leases)


def _command_membrane_v1_packet_to_summary(service: Any, packet: Any) -> dict[str, Any]:
    return {'event_id': packet.event_id, 'source_path': packet.source_path, 'source_folder': packet.source_folder, 'event_kind': packet.event_kind or packet.change_type, 'status': packet.status, 'goal': packet.goal, 'priority': packet.priority, 'earth_ts': packet.earth_ts, 'liminal_ts': packet.liminal_ts, 'front_ref': packet.front_ref, 'seed_mode': packet.seed_mode, 'dual_reference': packet.dual_reference, 'route_targets': packet.route_targets, 'linked_quests': packet.linked_quests, 'latency_state': packet.latency_state}


def _command_membrane_v1_strongest_capillaries(service: Any) -> list[dict[str, Any]]:
    rows = []
    for edge_id, edge in service.load_edges().get('edges', {}).items():
        rows.append({'edge_id': edge_id, 'edge_strength': float(edge.get('edge_strength', edge.get('strength', 0.0))), 'classification': edge.get('classification', edge.get('state_class', 'candidate_path')), 'use_count': int(edge.get('use_count', 0)), 'success_count': int(edge.get('success_count', 0))})
    rows.sort(key=lambda item: (-item['edge_strength'], item['edge_id']))
    return rows[:5]


def _command_membrane_v1_source_health(service: Any) -> dict[str, Any]:
    events = _recent_event_payloads(service, limit=None)
    latest = events[0] if events else {}
    return {'rows': [{'source_id': 'command_root', 'source_class': 'command-folder', 'absolute_path': str(service.config.command_surface_root), 'watch_root': str(service.config.command_surface_root), 'native_watch_available': True, 'degraded_mode': False, 'event_count': len(events), 'backlog_count': sum(1 for row in events if row.get('status') != 'committed'), 'active_claim_count': len(service.load_leases().get('active', {})), 'last_event_id': latest.get('event_id', ''), 'last_event_ts': latest.get('earth_ts_utc', latest.get('earth_ts', '')), 'last_status': latest.get('status', ''), 'docs_gate_status': service.docs_gate_status()['state']}]} 


def _command_membrane_v1_metrics(service: Any) -> dict[str, Any]:
    events = _recent_event_payloads(service, limit=None)
    committed = [event for event in events if event.get('commit_state')]
    def avg(key: str) -> float:
        values = [float((event.get('latency_state') or {}).get(key, 0.0)) for event in committed]
        return round(sum(values) / len(values), 3) if values else 0.0
    return {'event_count': len(events), 'committed_event_count': len(committed), 'routed_event_count': sum(1 for event in events if event.get('route_state')), 'claimed_event_count': sum(1 for event in events if event.get('claim_state')), 'active_leases': len(service.load_leases().get('active', {})), 'edge_count': len(service.load_edges().get('edges', {})), 'average_detection_latency_ms': avg('detect_latency_ms'), 'average_awareness_latency_ms': avg('awareness_latency_ms'), 'average_claim_latency_ms': avg('claim_latency_ms'), 'average_resolution_latency_ms': avg('resolution_latency_ms'), 'average_commit_latency_ms': avg('commit_latency_ms'), 'average_t_sugar_ms': avg('t_sugar_ms')}


def _command_membrane_v1_public_state(service: Any, event_id: str | None = None) -> dict[str, Any]:
    recent_events = _recent_event_payloads(service, limit=12)
    latest = recent_events[0] if recent_events else {}
    if event_id:
        path = service.event_path(event_id)
        if path.exists():
            latest = read_json(path, latest)
    latest_committed = next((row for row in recent_events if row.get('commit_state')), {})
    active_leases = list(service.load_leases().get('active', {}).values())
    return {'generated_at': utc_now(), 'canonical_mode': 'COMMAND_FOLDER_SENSORY_MEMBRANE', 'command_root': str(service.config.command_surface_root), 'active_surface': rel(service.config.command_surface_root), 'watcher_mode': COMMAND_WATCHER_MODE, 'watch_scope': 'GLOBAL COMMAND only', 'docs_gate': service.docs_gate_status(), 'docs_gate_status': service.docs_gate_status()['state'], 'prompt_level_liminal_gps': 'supported', 'keystroke_level_liminal_gps': 'requires client/runtime instrumentation', 'active_membrane': COMMAND_ACTIVE_MEMBRANE, 'feeder_stack': list(COMMAND_FEEDER_STACK), 'policy': {'route_policy': COMMAND_ROUTE_POLICY, 'topk': service.config.topk, 'claim_mode': service.config.claim_mode, 'quorum': service.config.quorum, 'ttl': service.config.ttl, 'lease_ms': service.config.lease_ms}, 'active_leases': active_leases, 'queue_depth': len(active_leases) + sum(1 for row in recent_events if row.get('status') != 'committed'), 'recent_events': [{'event_id': row.get('event_id', ''), 'source_path': row.get('source_path', ''), 'change_type': row.get('change_type', ''), 'status': row.get('status', ''), 'earth_ts_utc': row.get('earth_ts_utc', row.get('earth_ts', '')), 'replay_ptr': row.get('replay_ptr', row.get('_path', ''))} for row in recent_events], 'last_event': {'event_id': latest.get('event_id', 'none'), 'source_path': latest.get('source_path', 'none'), 'status': latest.get('status', 'none'), 'route_path': (latest.get('route_state') or {}).get('route_path', ''), 'claim_id': (latest.get('claim_state') or {}).get('claim_id', ''), 'claim_ant_id': (latest.get('claim_state') or {}).get('ant_id', ''), 'result': (latest.get('commit_state') or {}).get('result', ''), 'restart_seed': (latest.get('commit_state') or {}).get('restart_seed', ''), 't_sugar_ms': float((latest.get('latency_state') or {}).get('t_sugar_ms', 0.0))}, 'latest_committed': latest_committed, 'top_capillaries': _command_membrane_v1_strongest_capillaries(service), 'metrics': _command_membrane_v1_metrics(service), 'updated_at': utc_now(), 'source_health': _command_membrane_v1_source_health(service).get('rows', [])}
