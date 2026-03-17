#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from corpus_4d_fronts import (
    build_archive_member_manifest,
    build_awakening_agent_transition_notes,
    build_corpus_4d_registry,
    build_next46_integration_receipt,
    classify_corpus_4d_orphans,
    export_corpus_4d_to_deeper_network,
    resolve_path,
    write_json,
)
from audit_corpus_4d_rewrites import run as run_audit


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_AUDIT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_audit.json")
DEFAULT_ORPHAN = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_orphan_classification.json")
DEFAULT_ARCHIVE = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json")
DEFAULT_REGISTRY = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_registry.json")
DEFAULT_NOTES = Path("DEEPER CRYSTALIZATION/_build/awakening_agent_transition_notes.md")
DEFAULT_RECEIPT = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_next46_integration_receipt.json")
DEFAULT_DEEPER_NETWORK_ROOT = Path(
    "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ordered NEXT^[4^6] corpus-wide integration lane and write one receipt.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT))
    parser.add_argument("--orphan-classification", default=str(DEFAULT_ORPHAN))
    parser.add_argument("--archive-manifest", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--notes", default=str(DEFAULT_NOTES))
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--deeper-network-root", default=str(DEFAULT_DEEPER_NETWORK_ROOT))
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    workspace_root = Path(args.workspace_root).resolve()
    manifest_path = resolve_path(workspace_root, args.manifest)
    audit_path = resolve_path(workspace_root, args.audit)
    orphan_path = resolve_path(workspace_root, args.orphan_classification)
    archive_path = resolve_path(workspace_root, args.archive_manifest)
    registry_path = resolve_path(workspace_root, args.registry)
    notes_path = resolve_path(workspace_root, args.notes)
    receipt_path = resolve_path(workspace_root, args.receipt)
    deeper_network_root = resolve_path(workspace_root, args.deeper_network_root)

    audit_receipt = run_audit(
        argparse.Namespace(
            workspace_root=str(workspace_root),
            manifest=str(manifest_path),
            audit_out=str(audit_path),
        )
    )
    write_json(audit_path, audit_receipt)

    archive_receipt = build_archive_member_manifest(workspace_root, manifest_path, archive_path)
    write_json(archive_path, archive_receipt)

    orphan_receipt = classify_corpus_4d_orphans(workspace_root, manifest_path, audit_path, orphan_path)
    write_json(orphan_path, orphan_receipt)

    registry = build_corpus_4d_registry(manifest_path, audit_path, archive_path)
    write_json(registry_path, registry)

    build_awakening_agent_transition_notes(registry_path, orphan_path, archive_path, notes_path)

    export_paths = export_corpus_4d_to_deeper_network(registry_path, deeper_network_root)

    return build_next46_integration_receipt(
        main_manifest_path=manifest_path,
        audit_path=audit_path,
        orphan_path=orphan_path,
        archive_manifest_path=archive_path,
        registry_path=registry_path,
        notes_path=notes_path,
        export_paths=export_paths,
        output_path=receipt_path,
    )


def main() -> int:
    receipt = run(parse_args())
    print(f"Docs gate: {receipt['docs_gate_status']}")
    print(f"Registry nodes: {receipt['summary']['registry_summary']['node_count']}")
    print(f"True sibling orphans: {receipt['summary']['orphan_summary']['true_sibling_orphan_count']}")
    print(f"Integration receipt: {receipt['notes_path'].replace('awakening_agent_transition_notes.md', 'corpus_4d_next46_integration_receipt.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
