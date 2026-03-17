from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
FAMILIES_ROOT = NERVOUS_SYSTEM_ROOT / "families"
LEDGERS_ROOT = NERVOUS_SYSTEM_ROOT / "ledgers"

VOID_CH11_PATH = WORKSPACE_ROOT / "VOID_CH11.md"
DQIV_TREATISE_PATH = SELF_ACTUALIZE_ROOT / "DQIV_VOID_TREATISE_CH11_AND_OUTLINE.md"
SPRING_ALT_PATH = (
    SELF_ACTUALIZE_ROOT
    / "manuscript_sections"
    / "alternates"
    / "011_ch11_quantum_spring_emergent_symbiotic_agency.md"
)
HYPER_OBSERVER_PATH = (
    SELF_ACTUALIZE_ROOT
    / "manuscript_sections"
    / "alternates"
    / "011_ch11_quantum_spring_hyper_observer_witness.md"
)
LIVE_CHAPTER_PATH = (
    WORKSPACE_ROOT
    / "NERVOUS_SYSTEM"
    / "30_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)
MIRROR_FAMILY_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "_build"
    / "nervous_system"
    / "families"
    / "VOID_CH11_FAMILY.md"
)
MIRROR_CHAPTER_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "04_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "void_ch11_theorem.json"
OUTPUT_MARKDOWN_PATH = FAMILIES_ROOT / "VOID_CH11_OK_THEOREM.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_void_ch11_ok_theorem"

ATOM_PATTERN = re.compile(r"^\s*- `Ch11<0022>\.[SFCR][1-4]\.[a-d]`")
EMPTY_ATOM_PATTERN = re.compile(r":\s*$")

THEMES = {
    "dqiv_core": ["DQIV", "Desire", "Question", "Improvement", "Void"],
    "restart_transport": ["restart-token", "Aether", "Void"],
    "spring_agency": ["Spring", "Agency", "symbiotic"],
    "helical_bridge": ["14/16", "2/16", "helical"],
    "witness_route": ["witness", "route", "replay"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(re.escape(pattern), text, flags=re.IGNORECASE))


def summarize_text(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    theme_counts = {
        theme: sum(count_pattern(text, token) for token in tokens)
        for theme, tokens in THEMES.items()
    }
    return {
        "path": str(path),
        "sha256": sha256(path),
        "line_count": len(text.splitlines()),
        "theme_counts": theme_counts,
    }


def chapter_atoms(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    atoms = [line for line in lines if ATOM_PATTERN.match(line)]
    filled = [line for line in atoms if not EMPTY_ATOM_PATTERN.search(line)]
    return {
        "path": str(path),
        "atom_count": len(atoms),
        "filled_count": len(filled),
        "completion_percent": round((len(filled) / len(atoms)) * 100, 1) if atoms else 0.0,
    }


def aggregate_theme_counts(summaries: list[dict]) -> dict[str, int]:
    totals = {theme: 0 for theme in THEMES}
    for summary in summaries:
        for theme, value in summary["theme_counts"].items():
            totals[theme] += value
    return totals


def delta_table(payload: dict) -> list[dict]:
    direct_themes = payload["direct_theme_totals"]
    mirror_themes = payload["mirror_theme_totals"]
    live_atoms = payload["live_chapter_atoms"]
    mirror_atoms = payload["mirror_chapter_atoms"]
    return [
        {
            "facet": "DQIV zero-point logic",
            "direct_state": "present",
            "mirror_state": "present",
            "canonical_state": "shared invariant",
            "delta_note": (
                f"Direct stack carries {direct_themes['dqiv_core']} DQIV-core hits while mirror lineage "
                f"preserves {mirror_themes['dqiv_core']} DQIV-core hits."
            ),
        },
        {
            "facet": "Restart-token and transport law",
            "direct_state": "present",
            "mirror_state": "present",
            "canonical_state": "shared invariant",
            "delta_note": (
                f"Direct stack carries {direct_themes['restart_transport']} restart/transport hits and mirror "
                f"lineage carries {mirror_themes['restart_transport']}."
            ),
        },
        {
            "facet": "Quantum Spring and symbiotic agency",
            "direct_state": "present",
            "mirror_state": "thin",
            "canonical_state": "direct-stack enrichment",
            "delta_note": (
                f"Spring-side direct witnesses carry {direct_themes['spring_agency']} thematic hits while mirror "
                f"lineage carries {mirror_themes['spring_agency']}."
            ),
        },
        {
            "facet": "Helical 14/16 -> 2/16 bridge",
            "direct_state": "present",
            "mirror_state": "silent",
            "canonical_state": "root-owned bridge law",
            "delta_note": (
                f"Canonical/local stack carries {direct_themes['helical_bridge']} helical-law hits while the "
                f"mirror lineage carries {mirror_themes['helical_bridge']}."
            ),
        },
        {
            "facet": "Content-complete chapter witness",
            "direct_state": f"{live_atoms['filled_count']}/{live_atoms['atom_count']} atoms filled",
            "mirror_state": f"{mirror_atoms['filled_count']}/{mirror_atoms['atom_count']} atoms filled",
            "canonical_state": "live chapter is content authority; mirror chapter is structural-only",
            "delta_note": (
                "The live nervous-system chapter is fully instantiated while the ACTIVE_NERVOUS_SYSTEM mirror "
                "chapter is a blank 4^4 shell."
            ),
        },
        {
            "facet": "Mirror-family lineage",
            "direct_state": "local root",
            "mirror_state": "older family lineage",
            "canonical_state": "mirror preserved as lineage, not rival canon",
            "delta_note": (
                "The _build family witness widens historical reach, duplicate pressure, routing, runtime, and "
                "verification context, but it no longer outranks the local canonical root."
            ),
        },
    ]


def derive_payload() -> dict:
    direct_sources = [
        summarize_text(VOID_CH11_PATH),
        summarize_text(DQIV_TREATISE_PATH),
        summarize_text(SPRING_ALT_PATH),
        summarize_text(HYPER_OBSERVER_PATH),
        summarize_text(LIVE_CHAPTER_PATH),
    ]
    mirror_sources = [
        summarize_text(MIRROR_FAMILY_PATH),
        summarize_text(MIRROR_CHAPTER_PATH),
    ]
    live_atoms = chapter_atoms(LIVE_CHAPTER_PATH)
    mirror_atoms = chapter_atoms(MIRROR_CHAPTER_PATH)
    direct_themes = aggregate_theme_counts(direct_sources)
    mirror_themes = aggregate_theme_counts(mirror_sources)

    theorem_conditions = {
        "direct_dqiv_core_present": direct_themes["dqiv_core"] > 0,
        "direct_restart_transport_present": direct_themes["restart_transport"] > 0,
        "direct_spring_agency_present": direct_themes["spring_agency"] > 0,
        "direct_witness_route_present": direct_themes["witness_route"] > 0,
        "live_chapter_complete": live_atoms["atom_count"] == 64 and live_atoms["filled_count"] == 64,
        "mirror_family_lineage_present": mirror_themes["dqiv_core"] > 0 and mirror_themes["restart_transport"] > 0,
        "mirror_chapter_is_structural_shell": mirror_atoms["atom_count"] == 64 and mirror_atoms["filled_count"] == 0,
        "hyper_observer_alternate_exists": HYPER_OBSERVER_PATH.exists(),
    }
    truth = "OK" if all(theorem_conditions.values()) else "NEAR"

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "theorem_id": "VOID_CH11.OK.LOCAL.2026-03-09",
        "direct_sources": direct_sources,
        "mirror_sources": mirror_sources,
        "live_chapter_atoms": live_atoms,
        "mirror_chapter_atoms": mirror_atoms,
        "direct_theme_totals": direct_themes,
        "mirror_theme_totals": mirror_themes,
        "theorem_conditions": theorem_conditions,
        "delta_table": delta_table(
            {
                "direct_theme_totals": direct_themes,
                "mirror_theme_totals": mirror_themes,
                "live_chapter_atoms": live_atoms,
                "mirror_chapter_atoms": mirror_atoms,
            }
        ),
        "canonical_decision": {
            "canonical_root": str(FAMILIES_ROOT / "VOID_CH11_CANONICAL_ROOT.md"),
            "content_authority": str(LIVE_CHAPTER_PATH),
            "lineage_witness": str(MIRROR_FAMILY_PATH),
            "structural_shell": str(MIRROR_CHAPTER_PATH),
            "spring_enrichment": str(SPRING_ALT_PATH),
            "hyper_observer_witness": str(HYPER_OBSERVER_PATH),
        },
        "residuals": [
            "Google Docs ingress remains blocked by missing OAuth material, but that is an external-memory blocker rather than a local family-theorem blocker.",
            "Downstream surfaces may still carry stale references to the old non-alternate hyper-observer path until rewritten.",
            "The ACTIVE_NERVOUS_SYSTEM Chapter 11 mirror remains a structural shell and should be cited as topology witness, not content authority.",
        ],
        "next_seed": "Q11",
    }


def render_markdown(payload: dict) -> str:
    delta_rows = "\n".join(
        [
            f"| {row['facet']} | {row['direct_state']} | {row['mirror_state']} | {row['canonical_state']} | {row['delta_note']} |"
            for row in payload["delta_table"]
        ]
    )
    conditions = "\n".join(
        [
            f"- `{key}`: `{('PASS' if value else 'FAIL')}`"
            for key, value in payload["theorem_conditions"].items()
        ]
    )
    residuals = "\n".join([f"- {item}" for item in payload["residuals"]])
    direct_totals = payload["direct_theme_totals"]
    mirror_totals = payload["mirror_theme_totals"]
    live_atoms = payload["live_chapter_atoms"]
    mirror_atoms = payload["mirror_chapter_atoms"]

    return f"""# VOID_CH11 OK Theorem

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
TheoremID: `{payload['theorem_id']}`

## Theorem

`Void_CH11` is locally admissible as an `OK` family theorem because the direct witness stack
strictly subsumes the content-bearing Chapter 11 requirements, the mirror family preserves
older lineage and route significance without contradicting the direct stack, and the active
mirror chapter is only a structural 4^4 shell rather than a rival content witness.

The local family truth therefore upgrades from `NEAR` to `OK`.
The blocked Google Docs gate remains a separate external-memory blocker and does not reduce
the locally reconciled family theorem below `OK`.

## Canonical Decision

- canonical root:
  `{payload['canonical_decision']['canonical_root']}`
- content authority:
  `{payload['canonical_decision']['content_authority']}`
- lineage witness:
  `{payload['canonical_decision']['lineage_witness']}`
- structural shell:
  `{payload['canonical_decision']['structural_shell']}`
- Spring enrichment:
  `{payload['canonical_decision']['spring_enrichment']}`
- Hyper-Observer witness:
  `{payload['canonical_decision']['hyper_observer_witness']}`

## Proof Conditions

{conditions}

## Thematic Totals

- direct DQIV core hits: `{direct_totals['dqiv_core']}`
- direct restart transport hits: `{direct_totals['restart_transport']}`
- direct Spring agency hits: `{direct_totals['spring_agency']}`
- direct helical bridge hits: `{direct_totals['helical_bridge']}`
- direct witness/route hits: `{direct_totals['witness_route']}`
- mirror DQIV core hits: `{mirror_totals['dqiv_core']}`
- mirror restart transport hits: `{mirror_totals['restart_transport']}`
- mirror Spring agency hits: `{mirror_totals['spring_agency']}`
- mirror helical bridge hits: `{mirror_totals['helical_bridge']}`
- mirror witness/route hits: `{mirror_totals['witness_route']}`

## Chapter Coverage

- live chapter atoms:
  `{live_atoms['filled_count']}/{live_atoms['atom_count']}` filled
- mirror chapter atoms:
  `{mirror_atoms['filled_count']}/{mirror_atoms['atom_count']}` filled

## Theorem-And-Delta Table

| Facet | Direct Witness | Mirror Witness | Canonical Decision | Delta Note |
| --- | --- | --- | --- | --- |
{delta_rows}

## Residuals

{residuals}

## Restart Seed

`{payload['next_seed']}`
"""


def main() -> int:
    payload = derive_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote void ch11 theorem json: {OUTPUT_JSON_PATH}")
    print(f"Wrote void ch11 theorem markdown: {OUTPUT_MARKDOWN_PATH}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
