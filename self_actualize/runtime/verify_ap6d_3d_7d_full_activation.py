from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / 'NERVOUS_SYSTEM' / '95_MANIFESTS'
VERIFY_PATH = MANIFEST_DIR / 'ATHENA_PRIME_6D_3D_7D_FULL_ACTIVATION_VERIFICATION.json'

FILES = {
    'projection': MANIFEST_DIR / 'ATHENA_PRIME_6D_PROJECTION_BASE_3D.json',
    'routes': MANIFEST_DIR / 'ATHENA_PRIME_6D_CORPUS_INTEGRATION_ROUTES.json',
    'atlas': MANIFEST_DIR / 'ATHENA_PRIME_6D_ATLAS_4096.json',
    'waves': MANIFEST_DIR / 'ATHENA_PRIME_6D_SEAT_ACTIVATION_WAVES.json',
    'seat_ledger': MANIFEST_DIR / 'ATHENA_PRIME_6D_SEAT_ACTIVATION_LEDGER_4096.json',
    'seat_map': MANIFEST_DIR / 'ATHENA_PRIME_6D_SEAT_ROUTE_BRIDGE_MAP_4096.json',
    'bridges': MANIFEST_DIR / 'ATHENA_PRIME_6D_DIMENSION_BRIDGES.json',
    'nexus': MANIFEST_DIR / 'ATHENA_PRIME_6D_NEXUS_TUNNELS.json',
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    data = {name: load(path) for name, path in FILES.items()}
    ensure(len(data['projection']['records']) == 4, 'expected 4 projection records')
    ensure(len(data['routes']['basis_routes']) == 16, 'expected 16 basis routes')
    ensure(len(data['routes']['matrix_routes']) == 256, 'expected 256 matrix routes')
    ensure(len(data['routes']['observer_passes']) == 64, 'expected 64 observer passes')
    ensure(len(data['routes']['witness_states']) == 16, 'expected 16 witness states')
    ensure(len(data['atlas']['seats']) == 4096, 'expected 4096 atlas seats')
    ensure(sum(1 for row in data['atlas']['seats'] if row['activation_state'] == 'ACTIVE') == 1024, 'expected 1024 active atlas seats')
    ensure(sum(1 for row in data['atlas']['seats'] if row['activation_state'] == 'DORMANT') == 3072, 'expected 3072 dormant atlas seats')
    wave_sizes = {row['wave_id']: row['seat_count'] for row in data['waves']['waves']}
    ensure(wave_sizes == {'Wave0': 1024, 'Cohort1': 1024, 'Cohort2': 1024, 'Cohort3': 1024}, 'unexpected wave sizes')
    wave_states = {row['wave_id']: row['promotion_state'] for row in data['waves']['waves']}
    ensure(wave_states == {'Wave0': 'ACTIVE', 'Cohort1': 'DORMANT', 'Cohort2': 'DORMANT', 'Cohort3': 'DORMANT'}, 'unexpected wave promotion states')
    ensure(len(data['seat_ledger']['rows']) == 4096, 'expected 4096 seat ledger rows')
    ensure(len(data['seat_map']['rows']) == 4096, 'expected 4096 seat map rows')
    ensure(len(data['bridges']['records']) == 16384, 'expected 16384 bridge records')
    ensure(len(data['nexus']['records']) == 4096, 'expected 4096 nexus records')
    report = {
        'truth': 'OK',
        'docs_gate_status': data['projection']['docs_gate_status'],
        'checks': {
            'projection_records': 4,
            'basis_routes': 16,
            'matrix_routes': 256,
            'observer_passes': 64,
            'witness_states': 16,
            'atlas_active': 1024,
            'atlas_dormant': 3072,
            'wave_sizes': wave_sizes,
            'wave_states': wave_states,
            'seat_ledger_rows': 4096,
            'seat_map_rows': 4096,
            'bridge_records': 16384,
            'nexus_records': 4096,
        },
    }
    VERIFY_PATH.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
