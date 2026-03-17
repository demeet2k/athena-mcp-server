from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.lp57omega_b_prime_support import (
    B_PRIME_DOC_MIRROR,
    B_PRIME_DOC_PATH,
    B_PRIME_MANIFEST_REPORT_PATH,
    B_PRIME_REGISTRY_MIRROR,
    B_PRIME_REGISTRY_PATH,
    LP57OMEGA_DEEP_CONTROL_MIRROR,
    LP57OMEGA_DEEP_CONTROL_PATH,
    LP57OMEGA_INDEX_MIRROR,
    LP57OMEGA_INDEX_PATH,
    LP57OMEGA_MANIFEST_FLEET_MIRROR,
    LP57OMEGA_MANIFEST_MIRROR,
    LP57OMEGA_MANIFEST_PATH,
    apply_marker_block,
    build_b_prime_registry,
    load_json,
    render_b_prime_markdown,
    verify_b_prime_registry,
    write_json,
    write_text,
)


INDEX_MARKER = "LP57OMEGA_B_PRIME_WITNESS"
DEEP_CONTROL_MARKER = "LP57OMEGA_B_PRIME_REGISTRY"


def update_manifest(registry: dict) -> dict:
    manifest = (
        load_json(LP57OMEGA_MANIFEST_PATH)
        if LP57OMEGA_MANIFEST_PATH.exists()
        else {"protocol_id": "LP-57OMEGA", "counts": {}, "outputs": {}, "notes": []}
    )
    manifest.setdefault("counts", {})
    manifest.setdefault("outputs", {})
    manifest.setdefault("notes", [])
    manifest["counts"]["b_prime_dense_shell_rows"] = registry["counts"]["dense_shell_rows"]
    manifest["counts"]["b_prime_witness_rows"] = registry["counts"]["witnessed_rows"]
    manifest["counts"]["b_prime_pointer_expanded_rows"] = registry["payload_counts"]["pointer_expanded_rows"]
    manifest["counts"]["b_prime_witness_seed_payloads"] = registry["payload_counts"]["witness_seed_payloads"]
    manifest["counts"]["b_prime_replay_seed_payloads"] = registry["payload_counts"]["replay_seed_payloads"]
    manifest["outputs"]["b_prime_witness_registry"] = str(B_PRIME_REGISTRY_PATH)
    manifest["outputs"]["b_prime_witness_doc"] = str(B_PRIME_DOC_PATH)
    manifest["outputs"]["b_prime_witness_verification"] = str(B_PRIME_MANIFEST_REPORT_PATH)
    note = (
        "B' installs the explicit Flower-lens AETHER coordinate shell over the sealed "
        "2/65 -> 65/65 dense shell, materializing symbolic Tick_2B/V_2B/E_2B witness "
        "and replay seed payloads without modifying P or S records."
    )
    if note not in manifest["notes"]:
        manifest["notes"].append(note)
    return manifest


def update_index(index_text: str, registry: dict) -> str:
    body = "\n".join(
        [
            "## B' Witnessed Inversion Shell",
            "",
            "- dense shell: `1/65 header; 2/65 -> 65/65 sealed`",
            f"- dense shell rows: `{registry['counts']['dense_shell_rows']}`",
            f"- witnessed rows: `{registry['counts']['witnessed_rows']}`",
            (
                "- pointer-expanded rows / seed payloads: "
                f"`{registry['payload_counts']['pointer_expanded_rows']}` / "
                f"`{registry['payload_counts']['witness_seed_payloads']}` / "
                f"`{registry['payload_counts']['replay_seed_payloads']}`"
            ),
            "- parent chain: `Rxx <- Sxx`, `Qxx <- Rxx`, `Txx <- Qxx`",
            "- shell ABI: `AE=(L,Phi,B;sigma)` pinned to the Flower lens",
            "- route pins: `rtL = Sigma-F-N-21`, `rtZ = Sigma-F-G-21`",
            "- seed payloads: `WS / RS` with symbolic hash locks and explicit AETHER coordinates",
            f"- registry: `{B_PRIME_REGISTRY_PATH}`",
            f"- surface: `{B_PRIME_DOC_PATH}`",
            f"- verification: `{B_PRIME_MANIFEST_REPORT_PATH}`",
        ]
    )
    return apply_marker_block(index_text, INDEX_MARKER, body)


def update_deep_control(deep_control_text: str) -> str:
    body = "\n".join(
        [
            "## B' Witnessed Inversion Shell",
            "",
            f"- witness registry: `{B_PRIME_REGISTRY_PATH}`",
            f"- witness surface: `{B_PRIME_DOC_PATH}`",
            f"- verification: `{B_PRIME_MANIFEST_REPORT_PATH}`",
            "- shell law: `A -> B -> B'`",
            "- explicit AETHER shell: `R -> Phi0/Phi1`, `Q -> Phi2`, `T -> Phi3:h`",
            "- registry pins: `Tick_2B`, `V_2B`, `E_2B`",
            "- witness scope: `Immediate lawful parent only` with symbolic WS/RS payload objects",
        ]
    )
    return apply_marker_block(deep_control_text, DEEP_CONTROL_MARKER, body)


def main() -> int:
    registry = build_b_prime_registry()
    markdown = render_b_prime_markdown(registry)
    verification = verify_b_prime_registry(registry, markdown)
    manifest = update_manifest(registry)

    index_source = (
        LP57OMEGA_INDEX_PATH.read_text(encoding="utf-8")
        if LP57OMEGA_INDEX_PATH.exists()
        else "# LP57Omega Protocol Index\n"
    )
    deep_control_source = (
        LP57OMEGA_DEEP_CONTROL_PATH.read_text(encoding="utf-8")
        if LP57OMEGA_DEEP_CONTROL_PATH.exists()
        else "# LP57Omega Deep Control\n"
    )

    write_json(B_PRIME_REGISTRY_PATH, registry)
    write_json(B_PRIME_REGISTRY_MIRROR, registry)
    write_json(B_PRIME_MANIFEST_REPORT_PATH, verification)
    write_json(LP57OMEGA_MANIFEST_PATH, manifest)
    write_json(LP57OMEGA_MANIFEST_MIRROR, manifest)
    write_json(LP57OMEGA_MANIFEST_FLEET_MIRROR, manifest)

    write_text(B_PRIME_DOC_PATH, markdown)
    write_text(B_PRIME_DOC_MIRROR, markdown)
    write_text(LP57OMEGA_INDEX_PATH, update_index(index_source, registry))
    write_text(LP57OMEGA_INDEX_MIRROR, update_index(index_source, registry))
    write_text(
        LP57OMEGA_DEEP_CONTROL_PATH, update_deep_control(deep_control_source)
    )
    write_text(
        LP57OMEGA_DEEP_CONTROL_MIRROR, update_deep_control(deep_control_source)
    )

    print(
        json.dumps(
            {
                "truth": verification["truth"],
                "registry": str(B_PRIME_REGISTRY_PATH),
                "surface": str(B_PRIME_DOC_PATH),
                "verification": str(B_PRIME_MANIFEST_REPORT_PATH),
                "witnessed_rows": registry["counts"]["witnessed_rows"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
