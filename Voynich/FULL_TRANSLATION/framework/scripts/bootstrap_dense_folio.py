from __future__ import annotations

import argparse
import json
from pathlib import Path


FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = FRAMEWORK_ROOT / "registry" / "lenses.json"
TEMPLATE_PATH = FRAMEWORK_ROOT / "templates" / "FOLIO_DENSE_TEMPLATE.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a dense multilens Voynich folio markdown file."
    )
    parser.add_argument("--folio", required=True, help="Display folio id, e.g. F002R")
    parser.add_argument("--book", required=True, help="Book label, e.g. Book I")
    parser.add_argument("--section-role", default="Fill in the folio role.", help="Section role")
    parser.add_argument(
        "--zero-claim",
        default="Fill in the core folio claim once direct evidence and the full line program are clear.",
        help="Initial folio zero claim",
    )
    parser.add_argument("--line-ids-file", help="Optional path with one line id per line")
    parser.add_argument("--eva-file", help="Optional path containing EVA transcription text")
    parser.add_argument(
        "--direct-source",
        action="append",
        default=[],
        help="Direct source path or note. May be repeated.",
    )
    parser.add_argument(
        "--derived-source",
        action="append",
        default=[],
        help="Derived source path or note. May be repeated.",
    )
    parser.add_argument("--output", required=True, help="Output markdown path")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    return parser.parse_args()


def load_registry() -> dict:
    with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_optional_text(path_str: str | None, default: str) -> str:
    if not path_str:
        return default
    return Path(path_str).read_text(encoding="utf-8-sig").strip() or default


def read_line_ids(path_str: str | None) -> list[str]:
    if not path_str:
        return []
    values = []
    for raw in Path(path_str).read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        values.append(line)
    return values


def format_bullets(items: list[str], empty_line: str) -> str:
    if not items:
        return empty_line
    return "\n".join(f"- `{item}`" for item in items)


def paragraph_heading(line_id: str) -> str:
    prefix = line_id.split(".", 1)[0]
    return f"### {prefix} - fill label"


def build_direct_ledger(line_ids: list[str]) -> str:
    if not line_ids:
        return (
            "### P? - fill label\n\n"
            "- `P?.?`\n"
            "  EVA: ``\n"
            "  Literal chain: ``\n"
            "  Operational English: \n"
        )

    blocks: list[str] = []
    current_prefix = None
    for line_id in line_ids:
        prefix = line_id.split(".", 1)[0]
        if prefix != current_prefix:
            if blocks:
                blocks.append("")
            blocks.append(paragraph_heading(line_id))
            blocks.append("")
            current_prefix = prefix
        blocks.append(f"- `{line_id}`")
        blocks.append("  EVA: ``")
        blocks.append("  Literal chain: ``")
        blocks.append("  Operational English: ")
        blocks.append("")
    return "\n".join(blocks).rstrip()


def build_lens_sections(lenses: list[dict], line_ids: list[str]) -> str:
    sections: list[str] = []
    if not line_ids:
        line_ids = ["P?.?"]

    for lens in lenses:
        sections.append(f"### {lens['display_name']}")
        sections.append("")
        for line_id in line_ids:
            sections.append(f"- `{line_id}`")
            for field in lens["entry_fields"]:
                sections.append(f"  {field}: ")
            sections.append("")
        sections.append("")
    return "\n".join(sections).rstrip()


def replace_token(template: str, token: str, value: str) -> str:
    return template.replace("{{" + token + "}}", value)


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {output_path}")

    registry = load_registry()
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    line_ids = read_line_ids(args.line_ids_file)
    eva_text = read_optional_text(args.eva_file, "Add full EVA transcription here.")

    direct_sources = format_bullets(
        args.direct_source,
        "- `Add direct folio-specific sources here.`",
    )
    derived_sources = format_bullets(
        args.derived_source,
        "- `Add derived framework and math sources here.`",
    )

    replacements = {
        "FOLIO_TITLE": args.folio,
        "SHORT_PURPOSE": (
            f"This file is the dense working standard for {args.folio}. "
            "It should contain direct evidence, line-by-line literal parsing, "
            "full multilens renderers, and a formal folio theorem."
        ),
        "SOURCE_STACK_DIRECT": direct_sources,
        "SOURCE_STACK_DERIVED": derived_sources,
        "FOLIO_ZERO_CLAIM": args.zero_claim,
        "FULL_EVA": eva_text,
        "FOLIO_SHORT": args.folio,
        "CORE_VML_MACHINERY": (
            f"- Book: `{args.book}`\n"
            f"- Section role: `{args.section_role}`\n"
            "- Add the active VML token families for this folio here.\n"
            "- Reuse operator families from `framework/registry/vml_operator_registry.md`.\n"
        ),
        "DIRECT_LEDGER": build_direct_ledger(line_ids),
        "LENS_SECTIONS": build_lens_sections(registry["lenses"], line_ids),
        "DIRECT_OPERATIONAL_MEANING": "State the direct operational meaning of the full folio here.",
        "MATHEMATICAL_EXTRACTION": (
            "State what the folio means when all formal mathematical lenses are observed together."
        ),
        "MYTHIC_EXTRACTION": (
            "State what the folio means when the mythic and narrative lenses are observed together."
        ),
        "ALL_LENS_ZERO_POINT": (
            "State the simultaneous all-lens zero point here."
        ),
        "DENSE_ONE_SENTENCE_COMPRESSION": (
            "Compress the full folio into one sentence without losing the operational backbone."
        ),
        "IMPORTED_KERNEL_EQUATIONS": (
            "Import the specific kernels used from `framework/registry/math_kernel_registry.md`."
        ),
        "TYPED_STATE_MACHINE": (
            "Define the regime states, liminal edges, fail space, and initial state for this folio."
        ),
        "LINE_OPERATORS": (
            "Write explicit operator compositions for the decisive lines and paragraph compositions."
        ),
        "FORMAL_SAFETY_INVARIANTS": (
            "State trace, fail, flux, coherence, and checkpoint invariants for this folio."
        ),
        "CONJUGACY_LAW": (
            "Specify how the non-AQM mathematical lenses are transported from the AQM source lens."
        ),
        "CONCRETE_TRANSPORT_TARGETS": (
            "Specialize the chemistry, physics, quantum, wave, music, light, geometry, number, compression, hacking, and game carriers for this folio."
        ),
        "FORMAL_FOLIO_THEOREM": (
            "Compose the full folio operator chain and state the terminal condition."
        ),
    }

    for token, value in replacements.items():
        template = replace_token(template, token, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")


if __name__ == "__main__":
    main()
