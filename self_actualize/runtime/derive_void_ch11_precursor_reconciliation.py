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

CANONICAL_ROOT_PATH = FAMILIES_ROOT / "VOID_CH11_CANONICAL_ROOT.md"
CANONICAL_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_void_ch11.md"
PRIMARY_SOURCE_PATH = FAMILIES_ROOT / "FAMILY_void_ch11_primary_source.md"
WITNESS_LEDGER_PATH = NERVOUS_SYSTEM_ROOT / "ledgers" / "WITNESS_void_ch11_family.md"
ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_void_ch11_route_map.md"
OK_THEOREM_PATH = FAMILIES_ROOT / "VOID_CH11_OK_THEOREM.md"

MIRROR_FAMILY_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "_build"
    / "nervous_system"
    / "families"
    / "VOID_CH11_FAMILY.md"
)
MIRROR_NODE_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "_build"
    / "nervous_system"
    / "families"
    / "VOID_INFORMATION_FROM_THE_VOID_NODE.md"
)
MIRROR_CHAPTER_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "04_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)
LIVE_CHAPTER_PATH = (
    WORKSPACE_ROOT
    / "NERVOUS_SYSTEM"
    / "30_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "void_ch11_precursor_reconciliation.json"
OUTPUT_MARKDOWN_PATH = FAMILIES_ROOT / "VOID_CH11_PRECURSOR_MIRROR_RECONCILIATION.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_void_ch11_precursor_reconciliation"

ATOM_PATTERN = re.compile(r"^\s*- `Ch11<0022>\.[SFCR][1-4]\.[a-d]`")
EMPTY_ATOM_PATTERN = re.compile(r":\s*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_backtick_value(text: str, label: str) -> str | None:
    pattern = re.compile(re.escape(label) + r"\s*`([^`]+)`")
    match = pattern.search(text)
    return match.group(1) if match else None


def extract_bullet_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf"-\s*{re.escape(label)}:\s*`?([^\r\n`]+)`?")
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def extract_inline_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf"{re.escape(label)}\s*`([^`]+)`")
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def extract_imported_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    pattern = re.compile(r"- `?([A-Za-z_]+)\s*=\s*(\d+)`?")
    for name, value in pattern.findall(text):
        counts[name] = int(value)
    return counts


def chapter_atoms(path: Path) -> dict[str, int | float]:
    lines = read_text(path).splitlines()
    atoms = [line for line in lines if ATOM_PATTERN.match(line)]
    filled = [line for line in atoms if not EMPTY_ATOM_PATTERN.search(line)]
    atom_count = len(atoms)
    filled_count = len(filled)
    return {
        "atom_count": atom_count,
        "filled_count": filled_count,
        "completion_percent": round((filled_count / atom_count) * 100, 1) if atom_count else 0.0,
    }


def derive_payload() -> dict:
    canonical_root_text = read_text(CANONICAL_ROOT_PATH)
    mirror_family_text = read_text(MIRROR_FAMILY_PATH)
    mirror_node_text = read_text(MIRROR_NODE_PATH)
    theorem_text = read_text(OK_THEOREM_PATH)

    live_truth = extract_bullet_value(canonical_root_text, "Current Truth")
    theorem_truth = extract_inline_value(theorem_text, "Truth:")
    imported_family_name = extract_bullet_value(mirror_family_text, "imported family name")
    imported_document_count = extract_bullet_value(mirror_family_text, "imported document count")
    imported_signal_totals = extract_imported_counts(mirror_family_text)
    imported_hub_spine = extract_bullet_value(mirror_family_text, "Imported chapter-hub spine from the older lineage")

    live_atoms = chapter_atoms(LIVE_CHAPTER_PATH)
    mirror_atoms = chapter_atoms(MIRROR_CHAPTER_PATH)

    mirror_uses_master = "VOID_MANUSCRIPT_MASTER.md" in mirror_family_text
    mirror_next_promotion_is_docx = "Promote `INFORMATION FROM THE VOID MANI.docx`" in mirror_family_text
    mirror_node_has_duplicate_pressure = "Current duplicate requiring reconciliation" in mirror_node_text
    mirror_node_truth_is_ambig = "`AMBIG`" in mirror_node_text

    conditions = {
        "canonical_root_exists": CANONICAL_ROOT_PATH.exists(),
        "q26_theorem_exists": OK_THEOREM_PATH.exists(),
        "mirror_family_exists": MIRROR_FAMILY_PATH.exists(),
        "live_chapter_is_content_authority": live_atoms["atom_count"] == 64 and live_atoms["filled_count"] == 64,
        "mirror_chapter_is_topology_shell": mirror_atoms["atom_count"] == 64 and mirror_atoms["filled_count"] == 0,
        "mirror_preserves_lineage_mass": bool(imported_family_name) and bool(imported_document_count),
        "mirror_preserves_duplicate_branch_signal": mirror_node_has_duplicate_pressure,
        "live_truth_is_ok": live_truth == "OK",
    }
    truth = "OK" if all(conditions.values()) else "NEAR"

    preserved = [
        {
            "facet": "older family lineage",
            "mirror_witness": imported_family_name or "unknown",
            "canonical_decision": "preserve as precursor lineage",
            "reason": "the older family widens Chapter 11 reach beyond the local node and preserves prior routing/runtime context",
        },
        {
            "facet": "signal totals",
            "mirror_witness": imported_signal_totals,
            "canonical_decision": "preserve as historical pressure field",
            "reason": "the precursor counts still witness earlier routing, runtime, verification, identity, and void mass",
        },
        {
            "facet": "duplicate branch pressure",
            "mirror_witness": "INFORMATION FROM THE VOID MANI primary/(1) duplicate divergence",
            "canonical_decision": "preserve as unresolved source-branch witness",
            "reason": "the mirror node still names a real duplicate split that remains meaningful lineage evidence",
        },
        {
            "facet": "hub spine",
            "mirror_witness": imported_hub_spine or "AppA -> AppF -> AppM -> AppL -> AppI",
            "canonical_decision": "retain as precursor spine",
            "reason": "the precursor hub ordering still explains why the live family crosses address, transport, replay, evidence promotion, and corridor truth",
        },
    ]

    deprecated = [
        {
            "claim": "mirror family as truth-bearing primary surface",
            "old_state": "mirror family implied current live family state",
            "new_state": "mirror family is lineage witness only",
        },
        {
            "claim": "next promotion should be the first bronze docx node",
            "old_state": "promote INFORMATION FROM THE VOID MANI docx",
            "new_state": "docx node remains historical branch evidence; live canonical root and theorem now outrank it",
        },
        {
            "claim": "mirror chapter as active content witness",
            "old_state": f"{mirror_atoms['filled_count']}/{mirror_atoms['atom_count']} active mirror atoms treated implicitly as chapter witness",
            "new_state": "mirror chapter is a topology shell and not a competing content authority",
        },
        {
            "claim": "NEAR family truth",
            "old_state": "family truth remained NEAR before theorem closure",
            "new_state": "family truth is locally OK after Q26 and this precursor reconciliation",
        },
    ]

    canonical = [
        {
            "surface": str(CANONICAL_ROOT_PATH),
            "role": "family-owned canonical root",
        },
        {
            "surface": str(OK_THEOREM_PATH),
            "role": "local OK theorem for sibling reconciliation",
        },
        {
            "surface": str(LIVE_CHAPTER_PATH),
            "role": "content authority for Chapter 11 atoms",
        },
        {
            "surface": str(MIRROR_FAMILY_PATH),
            "role": "precursor lineage witness",
        },
        {
            "surface": str(MIRROR_CHAPTER_PATH),
            "role": "topology-only mirror shell",
        },
        {
            "surface": str(MIRROR_NODE_PATH),
            "role": "duplicate-branch historical witness",
        },
    ]

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "reconciliation_id": "VOID_CH11.PRECURSOR.RECONCILED.2026-03-10",
        "conditions": conditions,
        "live_truth": live_truth,
        "q26_theorem_truth": theorem_truth,
        "imported_family_name": imported_family_name,
        "imported_document_count": imported_document_count,
        "imported_signal_totals": imported_signal_totals,
        "imported_hub_spine": imported_hub_spine or "AppA -> AppF -> AppM -> AppL -> AppI",
        "live_atoms": live_atoms,
        "mirror_atoms": mirror_atoms,
        "mirror_flags": {
            "uses_void_manuscript_master": mirror_uses_master,
            "next_promotion_is_docx": mirror_next_promotion_is_docx,
            "node_has_duplicate_pressure": mirror_node_has_duplicate_pressure,
            "node_truth_mentions_ambig": mirror_node_truth_is_ambig,
        },
        "preserved_lineage": preserved,
        "deprecated_or_demoted": deprecated,
        "canonical_assignment": canonical,
        "writeback_targets": [
            str(CANONICAL_FAMILY_PATH),
            str(PRIMARY_SOURCE_PATH),
            str(WITNESS_LEDGER_PATH),
            str(ROUTE_MAP_PATH),
            str(NERVOUS_SYSTEM_ROOT / "manifests" / "VOID_CH11_ACTIVE_FRONT.md"),
        ],
        "next_seed": "Q08",
    }


def render_markdown(payload: dict) -> str:
    preserved_rows = "\n".join(
        f"| {row['facet']} | {row['mirror_witness']} | {row['canonical_decision']} | {row['reason']} |"
        for row in payload["preserved_lineage"]
    )
    deprecated_rows = "\n".join(
        f"| {row['claim']} | {row['old_state']} | {row['new_state']} |"
        for row in payload["deprecated_or_demoted"]
    )
    conditions = "\n".join(
        f"- `{key}`: `{('PASS' if value else 'FAIL')}`"
        for key, value in payload["conditions"].items()
    )
    canonical_rows = "\n".join(
        f"| `{row['surface']}` | {row['role']} |"
        for row in payload["canonical_assignment"]
    )

    return f"""# VOID_CH11 Precursor Mirror Reconciliation

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
ReconciliationID: `{payload['reconciliation_id']}`

## Decision

The precursor `_build` `VOID_CH11` family is now reconciled with the live branch as a
preserved lineage witness rather than as a competing canonical truth surface.

The live branch keeps:

- `VOID_CH11_CANONICAL_ROOT.md` as family-owned root
- `VOID_CH11_OK_THEOREM.md` as local theorem closure
- `NERVOUS_SYSTEM/30_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md` as content authority

The precursor branch keeps:

- older `void-and-collapse` lineage identity
- duplicate-branch pressure from `INFORMATION FROM THE VOID MANI`
- historical routing/runtime/verification signal totals
- precursor hub-spine memory

## Conditions

{conditions}

## Coverage Split

- live chapter atoms:
  `{payload['live_atoms']['filled_count']}/{payload['live_atoms']['atom_count']}` filled
- mirror chapter atoms:
  `{payload['mirror_atoms']['filled_count']}/{payload['mirror_atoms']['atom_count']}` filled
- imported family:
  `{payload['imported_family_name']}`
- imported document count:
  `{payload['imported_document_count']}`
- live root truth:
  `{payload['live_truth']}`
- Q26 theorem truth:
  `{payload['q26_theorem_truth']}`

## Preserved Lineage

| Facet | Mirror Witness | Canonical Decision | Reason |
| --- | --- | --- | --- |
{preserved_rows}

## Deprecated Or Demoted Mirror Claims

| Claim | Old State | New State |
| --- | --- | --- |
{deprecated_rows}

## Canonical Assignment

| Surface | Role |
| --- | --- |
{canonical_rows}

## Mirror Flags

- uses `VOID_MANUSCRIPT_MASTER.md`:
  `{payload['mirror_flags']['uses_void_manuscript_master']}`
- still names docx-node next promotion:
  `{payload['mirror_flags']['next_promotion_is_docx']}`
- preserves duplicate-branch pressure:
  `{payload['mirror_flags']['node_has_duplicate_pressure']}`
- mirror node still carries `AMBIG` language:
  `{payload['mirror_flags']['node_truth_mentions_ambig']}`

## Result

`Q11` is satisfied by one explicit precursor-to-live foldback:

`_build/VOID_CH11_FAMILY -> VOID_CH11_PRECURSOR_MIRROR_RECONCILIATION -> live family surfaces`

This preserves historical witness while tightening search mass around the live theorem.

## Next Seed

`{payload['next_seed']}`
"""


def main() -> int:
    payload = derive_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote precursor reconciliation json: {OUTPUT_JSON_PATH}")
    print(f"Wrote precursor reconciliation markdown: {OUTPUT_MARKDOWN_PATH}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
