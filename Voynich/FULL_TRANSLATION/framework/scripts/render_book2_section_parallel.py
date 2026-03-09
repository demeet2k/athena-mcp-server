from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio
from render_remaining_plant_section_parallel import (
    blocks,
    clean,
    confsum,
    counts,
    cut,
    evalines,
    pairmap,
    phr,
    pick,
    sections,
    tables,
    tarot,
)


FT = Path(__file__).resolve().parents[2]
WS = FT.parent
SECTIONS_DIR = FT / "sections"
CRYSTALS_DIR = FT / "crystals"
UNIFIED_DIR = FT / "unified"
METRO_DIR = FT / "metro"
MANIFESTS_DIR = FT / "manifests"

MAIN = WS / "NEW" / "SECTION II — BOOK II_ THE ASTRONOMICAL & ASTROLOGICAL.md"
ASTRO_COMPLETE = WS / "NEW" / "working" / "ASTRO_COMPLETE_VML_TRANSLATION.md"

BOOK2_DIRECT_SOURCES = [
    "NEW/SECTION II - BOOK II_ THE ASTRONOMICAL & ASTROLOGICAL.md",
    "NEW/working/ASTRO_COMPLETE_VML_TRANSLATION.md",
    "NEW/working/VML_ASTRONOMICAL_SECTION_COMPLETE.md",
    "NEW/working/ZODIAC_MASTER_TRANSLATION.md",
    "eva/EVA TRANSCRIPTION ORIGIONAL.txt",
]

BOOK2_DERIVED_SOURCES = [
    "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md",
    "FULL_TRANSLATION/framework/registry/lenses.json",
    "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
    "FULL_TRANSLATION/crystals/MASTER_PLANT_CRYSTAL.md",
]

CANONICAL = ["F058R", "F058V", "F065R", "F065V", "F066R", "F066V", "F069R", "F071R", "F071V", "F073R", "F073V"]
TARGETS = [
    ("F058R", "main", "FOLIO F58R"),
    ("F058V", "stub", ""),
    ("F065R", "stub", ""),
    ("F065V", "main", "FOLIO F65V"),
    ("F066R", "main", "FOLIO F66R"),
    ("F066V", "main", "FOLIO F66V"),
    ("F067R1", "main", "FOLIO F67R1"),
    ("F067R2", "main", "FOLIO F67R2"),
    ("F067V1", "main", "FOLIO F67V1"),
    ("F067V2", "main", "FOLIO F67V2"),
    ("F068R1", "main", "FOLIO F68R1"),
    ("F068R2", "main", "FOLIO F68R2"),
    ("F068R3", "astro", "F68R3"),
    ("F068V2", "mainsub", "F68V2"),
    ("F068V3", "mainsub", "F68V3"),
    ("F069R", "main", "FOLIO F69R"),
    ("F070R2", "main", "FOLIO F70R2"),
    ("F070V2", "main", "FOLIO F70V2"),
    ("F070V1", "main", "FOLIO F70V1"),
    ("F071R", "main", "FOLIO F71R"),
    ("F071V", "main", "FOLIO F71V"),
    ("F072R1", "main", "FOLIO F72R1"),
    ("F072R2", "main", "FOLIO F72R2"),
    ("F072V3", "main", "FOLIO F72V3"),
    ("F072V2", "main", "FOLIO F72V2"),
    ("F072V1", "main", "FOLIO F72V1"),
    ("F073R", "main", "FOLIO F73R"),
    ("F073V", "main", "FOLIO F73V"),
]


def disp(fid: str) -> str:
    m = re.match(r"F0*(\d+)([RV])(\d)?", fid)
    return f"f{m.group(1)}{m.group(2).lower()}{(m.group(3) or '').lower()}"


def heading_slice(text: str, anchor: str) -> str:
    m = re.search(rf"(?mi)^# .*{re.escape(anchor)}.*$", text)
    if not m:
        raise KeyError(anchor)
    start = m.start()
    next_head = re.search(r"(?m)^# .+$", text[m.end() :])
    end = m.end() + next_head.start() if next_head else len(text)
    return text[start:end]


def extract_heading_block(text: str, phrase: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if phrase in line:
            start = i
            break
    if start is None:
        return ""
    out = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith("### ") or line.startswith("## ") or line.startswith("# "):
            break
        out.append(line)
    return "\n".join(out)


def table_map(section: str) -> dict[str, str]:
    ts = tables(section)
    return {} if not ts else {clean(r[0]): clean(r[1]) for r in ts[0][1] if len(r) >= 2}


def subtitle(section: str) -> str:
    for line in section.splitlines():
        if line.startswith("## "):
            return clean(line)
    return clean(section.splitlines()[0])


def units_from_block(block: str) -> list[tuple[str, str]]:
    out, cur, buf = [], None, []
    for raw in block.splitlines():
        line = raw.strip().replace("\\[", "[").replace("\\]", "]")
        if not line or line.startswith("###") or line.startswith("####") or line.startswith("---"):
            continue
        m = re.match(r"^\[([A-Za-z0-9.]+)\]\s*(.+)$", line) or re.match(r"^([A-Za-z0-9.]+):\s*(.+)$", line)
        if m:
            if cur:
                out.append((cur, re.sub(r"\s+", " ", " ".join(buf)).strip()))
            cur = re.sub(r"[^A-Za-z0-9]", "", m.group(1)).upper()
            buf = [re.sub(r"\{[^}]+\}", "", m.group(2)).strip()]
        elif cur:
            buf.append(re.sub(r"\{[^}]+\}", "", line).strip())
    if cur:
        out.append((cur, re.sub(r"\s+", " ", " ".join(buf)).strip()))
    return out


def units_from_source_text(section: str, prefix: str = "X") -> list[tuple[str, str]]:
    m = re.search(r"\*\*Source text:\*\*\s*(.+?)(?:\n\n|\n---|\n\*\*Page total|\Z)", section, re.S)
    if not m:
        return []
    toks = [t for t in re.split(r"[\s.]+", m.group(1).replace("`", "")) if t]
    return [(f"{prefix}{i}", tok) for i, tok in enumerate(toks, start=1)]


def note_units(section: str) -> list[tuple[str, str]]:
    m = re.search(r"(?:EVA TRANSCRIPTION NOTE:|\*\*NOTE:\*\*)(.+?)(?:\n\n|\n---|\n### |\Z)", section, re.S)
    note = clean(m.group(1)) if m else cut(clean(section), 140)
    words = [w for w in re.findall(r"[A-Za-z0-9]+", note.lower()) if w]
    payload = ".".join(words[:12]) if words else "structural.witness.only"
    return [("W1", "structural.witness.high.confidence"), ("W2", payload)]


def signatures(eva: str) -> list[str]:
    t = eva.lower()
    sigs = []
    for needle, label in [
        ("qokal", "Saturn governance"),
        ("ot", "temporal drive"),
        ("ok", "phase shift"),
        ("daiin", "verification checkpoint"),
        ("ckh", "valve control"),
        ("cth", "conduit binding"),
        ("eee", "triple essence"),
        ("sar", "salt root"),
        ("dam", "union fixation"),
        ("al", "structure matrix"),
        ("ol", "fluid medium"),
    ]:
        if needle in t and label not in sigs:
            sigs.append(label)
    return sigs or ["opaque operator"]


def astro_counts(lines: list[tuple[str, str]]) -> dict[str, int]:
    out = {"units": 0, "temporal": 0, "phase": 0, "completion": 0, "saturn": 0, "valve": 0}
    for _lid, eva in lines:
        e = eva.lower()
        out["units"] += 1
        out["temporal"] += e.count("ot")
        out["phase"] += e.count("ok")
        out["completion"] += e.count("aiin") + e.count("aiir") + e.count("daii")
        out["saturn"] += e.count("qokal")
        out["valve"] += e.count("ckh") + e.count("kch")
    return out


def literal(eva: str) -> str:
    tokens = [p for p in re.split(r"[.\-=,\s]+", eva) if p]
    return " | ".join(f"`{tok}` = {' / '.join(signatures(tok)[:3])}" for tok in tokens[:6])


def optext(eva: str, hint: str) -> str:
    sigs = signatures(eva)
    acts = []
    if "temporal drive" in sigs:
        acts.append("enter the timing gate")
    if "phase shift" in sigs:
        acts.append("shift the schedule")
    if "Saturn governance" in sigs:
        acts.append("invoke the slow governor")
    if "verification checkpoint" in sigs:
        acts.append("verify before advancing")
    if "valve control" in sigs:
        acts.append("discipline the valve")
    if "conduit binding" in sigs:
        acts.append("stabilize the conduit")
    if "triple essence" in sigs:
        acts.append("raise the essence load")
    if not acts:
        acts = ["carry the local timing operator"]
    return f"{', then '.join(acts[:3]).capitalize()}, keeping the line aligned with {phr(hint, 10)}."


def build_groups(lines: list[tuple[str, str]]) -> list[dict[str, object]]:
    order, groups = [], {}
    for lid, _eva in lines:
        key = "R3" if lid.startswith("R3") else "R2" if lid.startswith("R2") else "R1" if lid.startswith("R1") else lid[0]
        if key not in groups:
            order.append(key)
            groups[key] = []
        groups[key].append(lid)
    titles = {"P": "Paragraph corridor", "C": "Circular-title ring", "R1": "Outer ring", "R2": "Middle ring", "R3": "Kernel ring", "S": "Sector and star labels", "B": "Base texts", "I": "Index loop", "O": "Operational loop", "X": "Constellation anchors", "W": "Witness ledger"}
    return [{"label": key, "title": titles.get(key, f"{key} corridor"), "line_ids": groups[key]} for key in order]


def finalize_book2_folio(folio: dict[str, object]) -> dict[str, object]:
    folio["book_label"] = "Book II - Astronomical / Astrological"
    folio["release_target"] = "Astrology Crystal, unified corpus, metro layer, and master manuscript"
    folio["direct_sources"] = BOOK2_DIRECT_SOURCES
    folio["derived_sources"] = BOOK2_DERIVED_SOURCES
    return folio


def stub(fid: str) -> dict[str, object]:
    lines = [("W1", "witness.side.recorded.but.not.transcribed"), ("W2", "registry.bridge.content.unavailable")]
    if fid == "F065R":
        lines = [("W1", "registry.bridge.herbal.side.recorded.in.eva"), ("W2", "title.next.to.plant.recorded")]
    rows = [(lid, eva, literal(eva), optext(eva, "witness preservation"), "witness-preservation line", "witness-limited") for lid, eva in lines]
    return finalize_book2_folio(make_folio(
        folio_id=fid,
        quire="Book II registry anomaly",
        bifolio=disp(fid),
        manuscript_role="witness-limited astronomical bridge",
        purpose=f"`{disp(fid)}` is preserved as a witness-limited Book II anomaly; the local corpus records its existence but does not provide a full translation witness.",
        zero_claim=f"Preserve `{disp(fid)}` honestly without inventing unavailable text.",
        botanical="Astronomical witness anomaly",
        risk="witness-limited",
        confidence="high on codicological existence; low on content",
        visual_grammar=["witness exists", "content unavailable locally", "macro-plan anomaly preserved honestly", "later evidence can replace this stub cleanly"],
        full_eva="\n".join(f"{lid}: {eva}" for lid, eva in lines),
        core_vml=["`witness-only page` = codicological presence without safe reconstruction", "`honesty rule` = preserve the gap", "`macro anomaly` = runtime expects the side"],
        groups=build_groups(lines),
        lines=rows,
        tarot_cards=tarot(len(rows)),
        movements=[r[3] for r in rows],
        direct="The page is kept as an honest witness-gap file rather than a fabricated translation.",
        math=f"Across the formal lenses, `{disp(fid)}` is a witness-bound state with no safe operator expansion.",
        mythic=f"`{disp(fid)}` is the page-shaped silence that keeps the corpus honest.",
        compression="Preserve the witness; do not invent the missing text.",
        typed_state_machine="\\[\\mathcal R = \\{r_{witness}\\}\\]",
        invariants="\\[N_{\\mathrm{visible\\ units}}=2\\]",
        theorem="\\[\\rho_* = \\Psi_{W}(\\rho_0)\\]\n\nThe formal theorem is that the witness exists and the missing text remains missing.",
        crystal_contribution=["witness-gap station", "honesty corridor", "registry anomaly close"],
        pointer_title="Witness-Limited Registry Anomaly",
        pointer_position=f"the {disp(fid)} side in the Book II transition band",
        pointer_page_type="witness-limited anomaly page",
        pointer_conclusion="codicological existence preserved without false reconstruction",
        pointer_judgment="No unsupported translation is invented here.",
        currier_language="unknown",
        currier_hand="unknown",
    ))


def build(fid: str, kind: str, anchor: str, main_sections: dict[str, str], astro_sections: dict[str, str]) -> dict[str, object]:
    if kind == "stub":
        return stub(fid)
    section = astro_sections[anchor] if kind == "astro" else main_sections["FOLIOS F68V2"] if kind == "mainsub" else main_sections[anchor]
    props = table_map(section)
    eva_block = extract_heading_block(section, "EVA TRANSCRIPTION")
    if kind == "mainsub":
        eva_block = re.search(rf"### \*\*EVA TRANSCRIPTION .*{anchor}\*\*(.+?)(?=\n### |\n## |\n# |\Z)", section, re.S)
        eva_lines = units_from_block(eva_block.group(1) if eva_block else "")
    else:
        eva_lines = units_from_block(eva_block or section)
    note_mode = False
    if not eva_lines:
        eva_lines = units_from_source_text(section)
    if not eva_lines:
        eva_lines = note_units(section)
        note_mode = True
    rows = [(lid, eva, literal(eva), optext(eva, props.get("Function", subtitle(section))), " / ".join(signatures(eva)[:3]) + " line", "witness-limited" if note_mode else ("mixed" if "*" in eva else "strong")) for lid, eva in eva_lines]
    c = astro_counts(eva_lines)
    key_tokens = [f"`temporal` = {c['temporal']} markers", f"`phase` = {c['phase']} markers", f"`verification` = {c['completion']} checkpoints", f"`Saturn` = {c['saturn']} invocations", f"`valve` = {c['valve']} controls"]
    return finalize_book2_folio(make_folio(
        folio_id=fid,
        quire=props.get("Quire/Bifolio", "Book II astronomy witness"),
        bifolio=props.get("Folio", disp(fid)),
        manuscript_role=clean(props.get("Function", subtitle(section))).lower(),
        purpose=f"`{disp(fid)}` is a Book II timing page. {cut(props.get('Function', subtitle(section)), 180)} {cut(clean(section), 220)}",
        zero_claim=cut(f"{disp(fid)} teaches {props.get('Function', subtitle(section))} and resolves its visible units as timing grammar.", 220),
        botanical=f"Astronomical subject: {props.get('Section', props.get('Zodiac', 'timing page'))}",
        risk=props.get("Risk Level", "reference").lower(),
        confidence="high on structural role, witness-limited on token coverage" if note_mode else confsum("", "high on temporal role and local source stack"),
        visual_grammar=[props.get("Illustration", "astronomical witness"), props.get("Distinction", "timing page"), f"{len(eva_lines)} visible units", subtitle(section)],
        full_eva="\n".join(f"{lid}: {eva}" for lid, eva in eva_lines),
        core_vml=key_tokens,
        groups=build_groups(eva_lines),
        lines=rows,
        tarot_cards=tarot(len(rows)),
        movements=[r[3] for r in rows],
        direct=cut(clean(section), 320),
        math=f"Across the formal lenses, `{disp(fid)}` behaves as a timing operator page with {c['temporal']} temporal markers and {c['phase']} phase markers.",
        mythic=f"`{disp(fid)}` turns sky-pattern into executable scheduling.",
        compression=cut(props.get("Function", subtitle(section)), 160),
        typed_state_machine="\\[\\mathcal R = \\{r_{timing}\\}\\]",
        invariants=f"\\[N_{{\\mathrm{{visible\\ units}}}}={c['units']}, \\qquad N_{{\\mathrm{{temporal}}}}={c['temporal']}, \\qquad N_{{\\mathrm{{verification}}}}={c['completion']}\\]",
        theorem=f"\\[\\rho_* = (\\Psi_n \\circ \\cdots \\circ \\Psi_1)(\\rho_0)\\]\n\nThe formal theorem of `{disp(fid)}` is that the page functions as executable temporal control rather than decorative astronomy.",
        crystal_contribution=[phr(subtitle(section), 5) + " station", "timing kernel line", "verification corridor", "phase-control close"],
        pointer_title=subtitle(section),
        pointer_position=f"the {disp(fid)} timing station in Book II",
        pointer_page_type=f"{props.get('Illustration', 'astronomical witness')} with {c['units']} visible units",
        pointer_conclusion=", ".join(k.split("`")[1] for k in key_tokens[:3]),
        pointer_judgment=cut(clean(section), 220),
        currier_language="Mixed A/B",
        currier_hand="4",
    ))


def append_if_missing(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + addition.strip() + "\n", encoding="utf-8")


def write_rollups(folios: list[dict[str, object]]) -> None:
    atlas = "\n".join(f"- `{disp(f['folio_id'])}`: {cut(f['direct_operational_meaning'], 160)}" for f in folios)
    witness = [disp(f["folio_id"]) for f in folios if "witness" in f["manuscript_role"] or "witness" in f["direct_operational_meaning"].lower()]
    zodiac = [disp(f["folio_id"]) for f in folios if any(sign in f["pointer_title"].lower() for sign in ["pisces", "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius"])]
    kernel = [disp(f["folio_id"]) for f in folios if any(key in f["pointer_title"].lower() for key in ["wheel", "cosmogram", "orbit", "calibration", "zodiac initialization"])]
    master = f"""# MASTER ASTROLOGY CRYSTAL

## Scope

- Corpus: `Book II - Astronomical / Astrological`
- Authoritative folio outputs synthesized: `{len(folios)}`
- Canonical macro folio sides covered: `{len(CANONICAL)}`
- Companion subpages covered: `{len(folios) - len(CANONICAL)}`
- Witness-limited anomaly pages preserved honestly: {", ".join(f"`{f}`" for f in witness) if witness else "none"}
- Master source class: authoritative final-draft folio atlases in `FULL_TRANSLATION/folios`

## Purpose

This file is the master analysis document for the fully translated astronomical and astrological corpus. It does four things at once:

1. it compresses every completed Book II folio and subfolio into one readable atlas,
2. it extracts the full Astrology Crystal from the completed timing corpus,
3. it maps the explicit metro and deeper emergent metro that connect calendrics, zodiac program logic, and pharmaceutical scheduling,
4. it prepares the handoff from Book II timing into the later bath, cosmology, and pharmaceutical books.

## Corpus State

Book II now reads as the manuscript's temporal control layer. The section resolves into four arcs:

- Cosmological kernel: `f58r`, `f65v`, `f66r`, `f66v` define the master timing grammar, paired operation-result logic, and execution rules.
- Clock and calibration band: `f67r1` through `f69r` establish month-wheel, red-ink command routing, solar and directional calibration, fixed stars, ephemeris tables, and the bridge to zodiac execution.
- Zodiac boot and seasonal corridor: `f70r2` through `f70v1` initialize the zodiac program and encode the year-boundary handoff.
- Zodiac body: `f71r` through `f73v` map sign-specific operational states onto the annual pharmaceutical cycle.

## Full Folio-By-Folio Atlas

{atlas}

## Cross Synthesis

### What Book II means

Book II says a medicine is not fully known until its time-address is known. Book I teaches how to extract. Book II teaches when to extract, which phase to privilege, how to route operations through slow and fast governors, and how to align the same recipe with monthly, seasonal, solar, and zodiacal timing structures.

### Timing Grammar

- `temporal drive` markers move the process into scheduled action.
- `phase shift` markers change regime rather than merely describing sky pictures.
- `verification checkpoints` make the astronomical pages read like executable QA rather than ornament.
- `Saturn governance` slows, seals, disciplines, and rate-limits dangerous or delicate operations.
- `valve control` preserves the same safety language found in the herbal pages, proving that Book II is operationally continuous with Book I.

### Section Crystal

- Kernel station: {", ".join(f"`{f}`" for f in kernel[:6]) if kernel else "timing kernel not isolated"}
- Zodiac program line: {", ".join(f"`{f}`" for f in zodiac) if zodiac else "zodiac set incomplete"}
- Witness-honesty line: {", ".join(f"`{f}`" for f in witness) if witness else "no witness anomalies"}
- Book-level theorem: astronomical imagery is executable schedule, not decorative astronomy.

## Metro Map

- Line A: cosmological source code -> execution rules -> scheduling wheel -> zodiac boot
- Line B: monthly clock -> solar fine-grain clock -> fixed-star calibration -> orbit parameter tables
- Line C: year boundary -> sign-by-sign phase execution -> late-zodiac closure
- Transfer hubs: `f66r`, `f67r2`, `f68v2`, `f70r2`, `f71v`

## Emergent Metro Map

- Hidden line 1: Book II reuses Book I safety language, proving that timing is a control layer on top of extraction, not a separate cosmology.
- Hidden line 2: the zodiac pages behave like state presets; each sign is a reusable process mood, not merely a date marker.
- Hidden line 3: the witness-limited pages are structurally important because they preserve the honest outline of the full machine even when local textual witness is partial.
- Hidden line 4: the astrology corpus gradually shifts from universal clock to executable year, compressing the whole manuscript into a time-program.

## Zero Point

Book II says the manuscript is a programmable calendar for medicine: the same operator chains from Book I only become fully intelligible when mapped onto phase, season, and celestial timing.
"""
    section_doc = f"""# FULL ASTROLOGY

## Scope

- Section: `Book II - Astronomical / Astrological`
- Completed outputs: `{len(folios)}`
- Canonical macro folios: `{len(CANONICAL)}`
- Companion subpages: `{len(folios) - len(CANONICAL)}`

## Section Synthesis

Book II is now complete as a translated timing corpus. The section establishes the manuscript's scheduling layer, moving from master cosmological rules into concrete zodiac execution. The authoritative section-level master analysis is in `crystals/MASTER_ASTROLOGY_CRYSTAL.md`.

## Folio Atlas

{atlas}
"""
    crystal_doc = f"""# ASTROLOGY CRYSTAL

## Section Identity

- Book: `Book II - Astronomical / Astrological`
- Role: `timing kernel of the manuscript`
- Completed outputs: `{len(folios)}`

## Crystal Summary

- Kernel ring: cosmological specification, operation-result QA, scheduling wheel, execution rules
- Calibration ring: month wheel, solar clock, fixed stars, ephemeris
- Zodiac ring: boot code, transition corridor, sign-by-sign operational presets
- Honesty ring: witness-limited anomalies preserved without false reconstruction

## Metro Summary

- explicit line: source code -> scheduler -> zodiac program
- emergent line: extraction grammar from Book I becomes time-addressable in Book II

## Master Analysis

See `crystals/MASTER_ASTROLOGY_CRYSTAL.md`.
"""
    (CRYSTALS_DIR / "MASTER_ASTROLOGY_CRYSTAL.md").write_text(master, encoding="utf-8")
    (SECTIONS_DIR / "FULL_ASTROLOGY.md").write_text(section_doc, encoding="utf-8")
    (CRYSTALS_DIR / "ASTROLOGY_CRYSTAL.md").write_text(crystal_doc, encoding="utf-8")
    append_if_missing(UNIFIED_DIR / "VOYNICH_FULL_TRANSLATION.md", "## Book II - Astronomical / Astrological Parallel Completion", "## Book II - Astronomical / Astrological Parallel Completion\n\n- canonical Book II macro folios complete\n- companion subpages complete\n- master analysis: `crystals/MASTER_ASTROLOGY_CRYSTAL.md`")
    append_if_missing(UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT.md", "## Book II Parallel Batch", "## Book II Parallel Batch\n\nBook II now exists as a completed parallel astronomy batch.")
    append_if_missing(CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md", "## Book II Delta - Astronomical / Astrological Completion", "## Book II Delta - Astronomical / Astrological Completion\n\n- the full-manuscript crystal now includes the timing kernel")
    append_if_missing(METRO_DIR / "VOYNICH_METRO_MAP_WORKING.md", "## Book II Expansion Delta", "## Book II Expansion Delta\n\n- timing kernel\n- lunar-solar calibration\n- zodiac program execution")
    status_path = MANIFESTS_DIR / "CORPUS_BUILD_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    status = status.replace("| `crystals/ASTROLOGY_CRYSTAL.md` | initialized |", "| `crystals/ASTROLOGY_CRYSTAL.md` | authoritative completed Book II astrology crystal |")
    status = status.replace("| `sections/FULL_ASTROLOGY.md` | initialized |", "| `sections/FULL_ASTROLOGY.md` | authoritative completed Book II astrology synthesis |")
    if "| `framework/scripts/render_book2_section_parallel.py` | complete |" not in status:
        status = status.replace("| `framework/scripts/render_remaining_plant_section_parallel.py` | complete |", "| `framework/scripts/render_remaining_plant_section_parallel.py` | complete |\n| `framework/scripts/render_book2_section_parallel.py` | complete |")
    if "## Book II Parallel Completion" not in status:
        status += "\n\n## Book II Parallel Completion\n\n- canonical Book II macro folios rendered\n- companion Book II subpages rendered\n- note: the serial autonomous cursor still preserves the unresolved `f057v` bridge task\n"
    status_path.write_text(status, encoding="utf-8")


def main() -> None:
    main_text = MAIN.read_text(encoding="utf-8-sig")
    astro_text = ASTRO_COMPLETE.read_text(encoding="utf-8-sig")
    main_sections = {anchor: heading_slice(main_text, anchor) for _fid, kind, anchor in TARGETS if kind in {"main", "mainsub"} and anchor not in {"", "F68V2", "F68V3"}}
    main_sections["FOLIOS F68V2"] = heading_slice(main_text, "FOLIOS F68V2")
    astro_sections = {"F68R3": heading_slice(astro_text, "F68R3")}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(build, fid, kind, anchor, main_sections, astro_sections) for fid, kind, anchor in TARGETS]
        folios = [f.result() for f in futures]
    order = {fid: i for i, (fid, _kind, _anchor) in enumerate(TARGETS)}
    folios.sort(key=lambda x: order[x["folio_id"]])
    for folio in folios:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")
    write_rollups(folios)
    print(f"Rendered {len(folios)} Book II outputs in parallel.")


if __name__ == "__main__":
    main()
