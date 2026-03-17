from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
FAMILIES_ROOT = NERVOUS_SYSTEM_ROOT / "families"

B12_JSON_PATH = SELF_ACTUALIZE_ROOT / "bruno_b12_operator_table.json"
ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_bruno_route_map.md"
PRIMARY_SOURCE_PATH = FAMILIES_ROOT / "FAMILY_bruno_primary_sources.md"
ACTIVE_FRONT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "BRUNO_ACTIVE_FRONT.md"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "bruno_address_c_leaf_promotion.json"
OUTPUT_MARKDOWN_PATH = FAMILIES_ROOT / "BRUNO_ADDRESS_C_LEAF_PROMOTION.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_bruno_address_c_leaf_promotion"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def derive_payload() -> dict:
    b12_payload = json.loads(B12_JSON_PATH.read_text(encoding="utf-8"))
    route_map_text = read_text(ROUTE_MAP_PATH)
    primary_text = read_text(PRIMARY_SOURCE_PATH)
    active_front_text = read_text(ACTIVE_FRONT_PATH)

    address_c_match = re.search(
        r"<Bruno_Archetype_Compression,\s*BrunoAthenaMasterTome,\s*Ch06,\s*R,\s*4,\s*a,\s*EAFW,\s*Arc1,\s*Me,\s*AppM,\s*([A-Z]+),\s*classical>",
        route_map_text,
    )
    address_c_truth = address_c_match.group(1) if address_c_match else "AMBIG"

    conditions = {
        "b12_table_exists": B12_JSON_PATH.exists(),
        "b12_truth_is_ok": b12_payload.get("truth") == "OK",
        "primary_source_truth_is_ok": "`OK`" in primary_text,
        "address_c_truth_is_ok": address_c_truth == "OK",
        "active_front_requests_leaf_promotion": "downstream `AMBIG` Bruno leaf" in active_front_text,
    }
    truth = "OK" if all(conditions.values()) else "NEAR"

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "promotion_id": "BRUNO.ADDRESS_C.LEAF.OK.2026-03-10",
        "leaf": {
            "name": "Address C",
            "node": "<Bruno_Archetype_Compression, BrunoAthenaMasterTome, Ch06, R, 4, a, EAFW, Arc1, Me, AppM, OK, classical>",
            "old_truth": "AMBIG",
            "new_truth": address_c_truth,
        },
        "conditions": conditions,
        "supporting_artifacts": [
            str(B12_JSON_PATH),
            str(ROUTE_MAP_PATH),
            str(PRIMARY_SOURCE_PATH),
            str(ACTIVE_FRONT_PATH),
        ],
        "why": [
            "The Bruno B12 table now source-pins the replay-side Bronze wheel.",
            "The family primary-source surface now classifies Bruno locally as OK.",
            "Address C no longer floats as a replay shell without source-pinned bronze support.",
        ],
        "next_seed": "Q35",
    }


def render_markdown(payload: dict) -> str:
    conditions = "\n".join(
        f"- `{key}`: `{('PASS' if value else 'FAIL')}`" for key, value in payload["conditions"].items()
    )
    supports = "\n".join(f"- `{artifact}`" for artifact in payload["supporting_artifacts"])
    why = "\n".join(f"- {item}" for item in payload["why"])
    return f"""# BRUNO Address C Leaf Promotion

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
PromotionID: `{payload['promotion_id']}`

## Leaf

- Name:
  `{payload['leaf']['name']}`
- Old truth:
  `{payload['leaf']['old_truth']}`
- New truth:
  `{payload['leaf']['new_truth']}`
- Node:
  `{payload['leaf']['node']}`

## Conditions

{conditions}

## Supporting Artifacts

{supports}

## Why The Promotion Holds

{why}

## Restart Seed

`Q35 Mirror ORGIN Into A Routed Seed Corpus`
"""


def main() -> int:
    payload = derive_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON_PATH}")
    print(f"Wrote {OUTPUT_MARKDOWN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
