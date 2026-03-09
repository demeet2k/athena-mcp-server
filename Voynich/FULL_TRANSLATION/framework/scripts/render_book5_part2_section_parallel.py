from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import re

import render_book5_part1_section_parallel as part1


FT = part1.FT
SECTIONS_DIR = part1.SECTIONS_DIR
CRYSTALS_DIR = part1.CRYSTALS_DIR
UNIFIED_DIR = part1.UNIFIED_DIR
METRO_DIR = part1.METRO_DIR
MANIFESTS_DIR = part1.MANIFESTS_DIR
FOLIOS_DIR = part1.FOLIOS_DIR

TARGETS = [
    "F106V",
    "F107R",
    "F107V",
    "F108R",
    "F108V",
    "F111R",
    "F111V",
    "F112R",
    "F112V",
    "F113R",
    "F113V",
    "F114R",
    "F114V",
    "F115R",
    "F115V",
    "F116R",
    "F116V",
]


def part2_role(section: str, title: str) -> str:
    if section == "Colophon":
        return "colophon / final notation"
    if section == "Closing Text":
        return "closing instruction text"
    if section == "Star-Based Formulary":
        return "star formulary"
    return part1.folio_kind(section, title)


def adapt_part2_folio(fid: str, blocks: dict[str, str]) -> dict[str, object]:
    folio = part1.parse_folio(fid, blocks)
    section = folio["core_vml"][2].split(" = ", 1)[1]
    title = folio["core_vml"][1].split(" = ", 1)[1]
    role = part2_role(section, title)

    folio["manuscript_role"] = role
    folio["book_label"] = "Book V - Pharmaceutical Part 2"
    folio["release_target"] = "Pharmaceutical 2 Crystal, unified corpus, metro layer, and master manuscript"
    folio["purpose"] = (
        f"`{part1.disp(fid)}` is a `{role}` inside `Book V - Pharmaceutical Part 2`. "
        f"Source title: {title}. Source subsection: {section}. "
        f"Local source summary: {part1.cut(folio['all_lens_zero_point'], 280)}"
    )
    folio["pointer_position"] = f"`{part1.disp(fid)}` inside Book V / Pharmaceutical Part 2"
    folio["pointer_page_type"] = role
    folio["pointer_judgment"] = f"`{part1.disp(fid)}` is best read as `{role}` under the source title `{title}`."

    if section == "Closing Text":
        folio["risk"] = "mastery-zone"
        folio["confidence"] = "high on technical closure role; medium on exact lexical semantics"
        folio["direct_operational_meaning"] = (
            f"`{part1.disp(fid)}` behaves as the closing technical instruction corridor of Book V: "
            f"{folio['all_lens_zero_point']}"
        )
        folio["mythic_extraction"] = (
            f"Across the mythic lenses, `{part1.disp(fid)}` is the final instruction chamber: "
            "the master still speaks in process language right before silence."
        )
    elif section == "Colophon":
        folio["risk"] = "witness-limited"
        folio["confidence"] = "medium on colophon role; low on exact semantics"
        folio["reading_contract"] = [
            "This final page may lie partly or wholly outside ordinary VML recipe language.",
            "The damaged witness is preserved directly and not normalized into a false technical page.",
            "Silence, sparsity, and closure are part of the evidence.",
            "The page is handled as manuscript ending rather than as a standard recipe station.",
        ]
        folio["direct_operational_meaning"] = (
            f"`{part1.disp(fid)}` behaves as a colophon or final notation page rather than an ordinary recipe leaf."
        )
        folio["mathematical_extraction"] = (
            f"Across the formal lenses, `{part1.disp(fid)}` is a terminal low-density witness: "
            "the operational signal collapses to a minimal residual notation."
        )
        folio["mythic_extraction"] = (
            f"Across the mythic lenses, `{part1.disp(fid)}` is the manuscript's ending silence."
        )
        folio["dense_compression"] = "Three damaged final notations close the manuscript outside the main recipe density."
        folio["crystal_contribution"] = [
            "colophon silence",
            "terminal notation",
            "exit from VML density",
        ]
        folio["audit"] = [
            "EVA inventory complete for the 3 visible units",
            "colophon handled as witness-limited ending rather than forced recipe normal form",
            "16 formal math lenses populated with per-line equations",
            "4 mythic lenses populated with per-line readings",
            "damaged glyphs preserved explicitly",
            "terminal silence remains visible as a manuscript-level feature",
        ]
    return folio


def write_one(folio: dict[str, object]) -> None:
    fid = folio["folio_id"]
    (FOLIOS_DIR / f"{fid}_FINAL_DRAFT.md").write_text(part1.render_folio(folio), encoding="utf-8")
    (FOLIOS_DIR / f"{fid}.md").write_text(part1.render_pointer(folio), encoding="utf-8")


def subsection_summary(folios: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    return part1.subsection_summary(folios)


def full_section_doc(folios: list[dict[str, object]]) -> str:
    grouped = subsection_summary(folios)
    atlas = []
    for folio in folios:
        atlas.append(
            f"- `{part1.disp(folio['folio_id'])}` - {folio['core_vml'][1].split(' = ', 1)[1]} - {folio['manuscript_role']} - {part1.cut(folio['all_lens_zero_point'], 140)}"
        )
    subsection_rows = [f"- `{name}` - {len(group)} translated units" for name, group in grouped.items()]
    return (
        "# Pharmaceutical 2 - Full Translation Ledger\n\n"
        "## Scope\n\n"
        "- Book: `Book V - Pharmaceutical Part 2`\n"
        "- Range: `f106v-f116v`\n"
        f"- Completed translated units: `{len(folios)}`\n"
        "- Coverage: late star curriculum, advanced compounds, terminal instructions, and colophon closure\n"
        "- Preserved gap: `f109-f110` remain absent from the local source sequence\n\n"
        "## Section Architecture\n\n"
        + "\n".join(subsection_rows)
        + "\n\n## Section Thesis\n\n"
        "Pharmaceutical Part 2 is the late master curriculum of the manuscript. The star pages become a sustained manufacturing corpus, the growth principle peaks and resolves, dosage and packaging enter explicitly, and the manuscript closes with final instructions followed by a sparse colophon-like silence.\n\n"
        "## Folio-By-Folio Atlas\n\n"
        + "\n".join(atlas)
        + "\n\n## Current Zero Point\n\n"
        "Book V Part 2 means: sustain distillation through the advanced star corpus, merge and standardize the compounded streams, certify quality, and close the manuscript in a final technical voice followed by silence.\n"
    )


def synthesis_doc() -> str:
    return (
        "# Pharmaceutical 2 Synthesis\n\n"
        "## Core Claim\n\n"
        "Book V Part 2 is the late master curriculum: sustained distillation, growth-principle deployment, compound merge logic, dosage and packaging, final certification, and terminal closure.\n\n"
        "## Stable Invariants\n\n"
        "- star checkpoints replace jar pedagogy as the dominant page grammar\n"
        "- advanced compounding intensifies only after stable circulation discipline is established\n"
        "- quality certification becomes explicit and named near the end\n"
        "- the manuscript closes by thinning its language, not by adding one last dense recipe\n\n"
        "## Cross-Book Bridges\n\n"
        "- Plant bridge tokens become full compound inputs and certification traces\n"
        "- Astrology's staged timing fully matures into star-governed progression\n"
        "- Bath infrastructure survives as return-gate and recirculation logic inside late recipes\n"
        "- Cosmology's network intuition survives as multi-stream merge and convergence architecture\n"
    )


def crystal_doc(folios: list[dict[str, object]]) -> str:
    grouped = subsection_summary(folios)
    lines = []
    for name, group in grouped.items():
        short = ", ".join(part1.disp(f["folio_id"]) for f in group[:6])
        if len(group) > 6:
            short += ", ..."
        lines.append(f"- `{name}`: {len(group)} units anchored by {short}")
    return (
        "# Pharmaceutical 2 Crystal\n\n"
        "## Scope\n\n"
        "- Book: `Book V - Pharmaceutical Part 2`\n"
        "- Range: `f106v-f116v`\n"
        f"- Current translated stations: `{len(folios)}` authoritative final-draft units\n\n"
        "## Synthesis\n\n"
        "This crystal gathers the late star-manufacturing corpus, the terminal quality corridor, and the manuscript ending. It is the section where sustained distillation, maximum sensitivity, multi-stream merge, dosage standardization, preservation, and final certification all converge before giving way to colophon silence.\n\n"
        "## Internal Districts\n\n"
        + "\n".join(lines)
        + "\n\n## Metro Map\n\n"
        "- `Advanced Distillation Line`: `f106v-f108v`\n"
        "- `Late Star Mastery Line`: `f111r-f115v`\n"
        "- `Closure Line`: `f116r-f116v`\n\n"
        "## Emergent Metro Map\n\n"
        "- `Sensitivity Becomes Ordinary`\n"
        "- `Merge, Then Measure`\n"
        "- `Certification Before Closure`\n"
        "- `Silence After Mastery`\n\n"
        "## Current Zero Point\n\n"
        "Part 2 is the master-school arc that turns star recipes into final certification and closes the manuscript.\n"
    )


def master_crystal_doc(folios: list[dict[str, object]]) -> str:
    atlas = []
    for folio in folios:
        atlas.append(
            f"- `{part1.disp(folio['folio_id'])}` - {folio['core_vml'][1].split(' = ', 1)[1]} - {part1.cut(folio['all_lens_zero_point'], 120)}"
        )
    return (
        "# MASTER PHARMACEUTICAL 2 CRYSTAL\n\n"
        "## Scope\n\n"
        "- Section: `Book V - Pharmaceutical Part 2`\n"
        "- Range: `f106v-f116v`\n"
        f"- Authoritative translated units: `{len(folios)}`\n\n"
        "## Governing Thesis\n\n"
        "The second pharmaceutical half is the manuscript's late mastery arc. It sustains distillation, saturates sensitivity, merges streams, standardizes dose and preservation, certifies quality, and then deliberately exits dense technical speech.\n\n"
        "## Full Folio Atlas\n\n"
        + "\n".join(atlas)
        + "\n\n## Wave One - Deep Cross-Section Analysis\n\n"
        "Part 2 internalizes the whole manuscript. Plant matter is no longer merely identified but compounded and measured. Astrological staging becomes star checkpoint law. Bath return gates become late rectification and retention protocols. Cosmology's hidden routing returns as merge and convergence architecture. The result is a final pharmaceutical school where previous books no longer appear as separate bodies of knowledge but as one integrated procedure field.\n\n"
        "## Wave Two - Emergent Reading\n\n"
        "The emergent pattern of Part 2 is closure by refinement. The section intensifies, merges, measures, packages, certifies, and then reduces itself to almost nothing. Mastery is shown not by endless complexity but by the ability to let the system fall silent.\n\n"
        "## Metro Map I - Deep Cross-Section Pharmaceutical 2 Metro Map\n\n"
        "- `Distillation Peak Line`: `f106v-f108v`\n"
        "- `Late Star Mastery Line`: `f111r-f112v`\n"
        "- `Merge and Verification Line`: `f113r-f114v`\n"
        "- `Packaging and Certification Line`: `f115r-f115v`\n"
        "- `Final Instruction and Colophon Line`: `f116r-f116v`\n\n"
        "## Metro Map II - Emergent Pharmaceutical 2 Metro Map\n\n"
        "- `Sustained heat becomes ordinary craft`\n"
        "- `The growth principle peaks, merges, and is then silenced`\n"
        "- `Certification is the last real technical act`\n"
        "- `The manuscript ends by dropping density`\n\n"
        "## Metro Map III - Full Five-Book Synthesized Metro Map\n\n"
        "- `Herbal source -> astrological timing -> bath purification -> rosette routing -> pharmaceutical execution -> certification -> silence`\n"
        "- `Book V Part 2` is the final proving ground where every previous line is either certified or released\n"
        "- the colophon acts as a zero-density terminal after the full fire curriculum\n\n"
        "## Section Theorem\n\n"
        "Book V Part 2 means: complete the star-manufacturing corpus, certify the product, and close the manuscript by passing from technical speech into terminal notation.\n"
    )


def combined_synthesis_doc() -> str:
    return (
        "# Pharmaceutical 1 / 2 Synthesis\n\n"
        "## Core Claim\n\n"
        "Taken together, the two pharmaceutical halves form a complete curriculum: Part 1 teaches the machine and the staged grammar of formulation; Part 2 executes the late mastery arc, certifies the results, and closes the book.\n\n"
        "## Split Logic\n\n"
        "- Part 1: payload, sealing, SOP, foldout machine, formulary, star threshold\n"
        "- Part 2: sustained star mastery, merge logic, dosage, preservation, certification, colophon silence\n\n"
        "## Whole Book V Theorem\n\n"
        "Book V means: turn the manuscript's earlier knowledge into medicine, then prove that medicine all the way to quality certification and closure.\n"
    )


def sync_rollups(folios: list[dict[str, object]]) -> None:
    (SECTIONS_DIR / "PHARMACEUTICAL_2_FULL.md").write_text(full_section_doc(folios), encoding="utf-8")
    (SECTIONS_DIR / "PHARMACEUTICAL_2_SYNTHESIS.md").write_text(synthesis_doc(), encoding="utf-8")
    (SECTIONS_DIR / "PHARMACEUTICAL_1_2_SYNTHESIS.md").write_text(combined_synthesis_doc(), encoding="utf-8")
    (CRYSTALS_DIR / "PHARMACEUTICAL_2_CRYSTAL.md").write_text(crystal_doc(folios), encoding="utf-8")
    (CRYSTALS_DIR / "MASTER_PHARMACEUTICAL_2_CRYSTAL.md").write_text(master_crystal_doc(folios), encoding="utf-8")

    units = ", ".join(part1.disp(f["folio_id"]) for f in folios)
    part1.put_block(
        UNIFIED_DIR / "VOYNICH_FULL_TRANSLATION.md",
        "<!-- AUTO_BOOK5_PART2_UNIFIED_START -->",
        "<!-- AUTO_BOOK5_PART2_UNIFIED_END -->",
        (
            "## Book V - Pharmaceutical Part 2\n\n"
            f"- completed authoritative units: `{len(folios)}`\n"
            "- range: `f106v-f116v`\n"
            "- preserved manuscript gap: `f109-f110`\n"
            f"- stations: `{units}`\n"
            "- status: the late pharmaceutical master curriculum and colophon closure are now built as a parallel dense-folio section\n"
        ),
    )
    part1.put_block(
        UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT.md",
        "<!-- AUTO_BOOK5_PART2_MASTER_START -->",
        "<!-- AUTO_BOOK5_PART2_MASTER_END -->",
        (
            "## Book V Part 2 Completion Delta\n\n"
            f"- authoritative late pharmaceutical units now on disk: `{len(folios)}`\n"
            "- the manuscript now includes the late star curriculum, merge and dosage corridor, preservation and certification corridor, final instructions, and the colophon ending\n"
            "- current late Book V theorem: sustain, merge, measure, certify, and then fall silent\n"
        ),
    )
    part1.put_block(
        METRO_DIR / "VOYNICH_METRO_MAP_WORKING.md",
        "<!-- AUTO_BOOK5_PART2_METRO_START -->",
        "<!-- AUTO_BOOK5_PART2_METRO_END -->",
        (
            "## Book V Part 2 Metro Delta\n\n"
            "- `Advanced Distillation Line` activates across `f106v-f108v`\n"
            "- `Late Star Mastery Line` activates across `f111r-f115v`\n"
            "- `Closure Line` activates at `f116r-f116v`\n"
            "- the manuscript now contains its full pharmaceutical certification and closure arc\n"
        ),
    )
    part1.put_block(
        CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md",
        "<!-- AUTO_BOOK5_PART2_FULL_CRYSTAL_START -->",
        "<!-- AUTO_BOOK5_PART2_FULL_CRYSTAL_END -->",
        (
            "## Book V Part 2 Delta\n\n"
            "- completed section: `f106v-f116v`\n"
            "- whole-manuscript contribution: the full five-book pharmaceutical curriculum is now section-complete through colophon closure\n"
            "- active cross-book theorem: source, time, purification, routing, execution, certification, and silence now all have translated section homes\n"
        ),
    )

    status_path = MANIFESTS_DIR / "CORPUS_BUILD_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    status = status.replace(
        "| `crystals/PHARMACEUTICAL_2_CRYSTAL.md` | initialized |",
        "| `crystals/PHARMACEUTICAL_2_CRYSTAL.md` | authoritative completed Book V Part 2 crystal |",
    )
    if "MASTER_PHARMACEUTICAL_2_CRYSTAL.md" not in status:
        status = status.replace(
            "| `crystals/MASTER_PHARMACEUTICAL_1_CRYSTAL.md` | complete master Book V Part 1 analysis, metro map, and emergent metro map |",
            "| `crystals/MASTER_PHARMACEUTICAL_1_CRYSTAL.md` | complete master Book V Part 1 analysis, metro map, and emergent metro map |\n| `crystals/MASTER_PHARMACEUTICAL_2_CRYSTAL.md` | complete master Book V Part 2 analysis, metro map, and emergent metro map |",
        )
    status = status.replace(
        "| `crystals/VOYNICH_FULL_CRYSTAL.md` | authoritative deep whole-manuscript crystal across completed Books I-IV with Book V horizon at `f87r` |",
        "| `crystals/VOYNICH_FULL_CRYSTAL.md` | authoritative deep whole-manuscript crystal across completed Books I-V |",
    )
    status = status.replace(
        "| `sections/PHARMACEUTICAL_2_FULL.md` | initialized |",
        "| `sections/PHARMACEUTICAL_2_FULL.md` | authoritative completed Book V Part 2 synthesis |",
    )
    status = status.replace(
        "| `sections/PHARMACEUTICAL_2_SYNTHESIS.md` | initialized |",
        "| `sections/PHARMACEUTICAL_2_SYNTHESIS.md` | completed concise Book V Part 2 synthesis |",
    )
    status = status.replace(
        "| `sections/PHARMACEUTICAL_1_2_SYNTHESIS.md` | initialized |",
        "| `sections/PHARMACEUTICAL_1_2_SYNTHESIS.md` | completed combined Book V synthesis |",
    )
    status = status.replace(
        "1. `f106v`\n2. `f107r`\n3. `f107v`\n4. `f108r`\n5. `f108v`\n6. `pharmaceutical 1 synthesis refinement`\n7. `pharmaceutical 2 full section`\n8. `full pharmaceutical crystal`",
        "1. `full pharmaceutical crystal`\n2. `master pharmaceutical crystal`\n3. `voynich full crystal refinement`\n4. `voynich master manuscript packaging`\n5. `author final line integration`\n6. `full corpus packaging`\n7. `final metro refinement`\n8. `giant manuscript export`",
    )
    if "render_book5_part2_section_parallel.py" not in status:
        status = status.replace(
            "| `framework/scripts/render_book5_part1_section_parallel.py` | complete |",
            "| `framework/scripts/render_book5_part1_section_parallel.py` | complete |\n| `framework/scripts/render_book5_part2_section_parallel.py` | complete |",
        )
    status_path.write_text(status, encoding="utf-8")
    part1.put_block(
        status_path,
        "<!-- AUTO_BOOK5_PART2_STATUS_START -->",
        "<!-- AUTO_BOOK5_PART2_STATUS_END -->",
        (
            "## Book V Part 2 Parallel Completion\n\n"
            f"- authoritative pharmaceutical units rendered in parallel: `{len(folios)}`\n"
            "- completed range: `f106v-f116v`\n"
            "- preserved gap: `f109-f110`\n"
            "- section synthesis completed in `sections/PHARMACEUTICAL_2_FULL.md`\n"
            "- crystal completed in `crystals/PHARMACEUTICAL_2_CRYSTAL.md`\n"
            "- master crystal completed in `crystals/MASTER_PHARMACEUTICAL_2_CRYSTAL.md`\n"
            "- combined pharmaceutical synthesis completed in `sections/PHARMACEUTICAL_1_2_SYNTHESIS.md`\n"
        ),
    )


def main() -> None:
    blocks = part1.block_map(part1.MAIN.read_text(encoding="utf-8"))
    missing = [fid for fid in TARGETS if fid not in blocks]
    if missing:
        raise SystemExit(f"Missing pharmaceutical blocks: {missing}")
    folios = [adapt_part2_folio(fid, blocks) for fid in TARGETS]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(write_one, folios))
    sync_rollups(folios)
    print(f"Rendered {len(folios)} Pharmaceutical Part 2 folios.")


if __name__ == "__main__":
    main()
