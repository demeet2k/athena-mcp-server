from __future__ import annotations

import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio
from render_remaining_plant_section_parallel import clean, cut, phr, tarot


FT = Path(__file__).resolve().parents[2]
WS = FT.parent
SECTIONS_DIR = FT / "sections"
CRYSTALS_DIR = FT / "crystals"
UNIFIED_DIR = FT / "unified"
METRO_DIR = FT / "metro"
MANIFESTS_DIR = FT / "manifests"
MAIN = WS / "NEW" / "working" / "VML PHARMACEUTICAL SECTION f87r through f116v.md"

DIRECT_SOURCES = [
    "NEW/working/VML PHARMACEUTICAL SECTION f87r through f116v.md",
    "NEW/working/VML_PHARMACEUTICAL_SECTION_ANALYSIS.md",
    "NEW/working/VML_DEEP_RECIPE_CALLBACK_ANALYSIS.md",
    "NEW/working/VML_RECIPE_CROSSREF.md",
    "NEW/working/VML_RECIPE_RECONSTRUCTION_PT2.md",
    "eva/EVA TRANSCRIPTION ORIGIONAL.txt",
]

DERIVED_SOURCES = [
    "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md",
    "FULL_TRANSLATION/framework/registry/lenses.json",
    "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
    "FULL_TRANSLATION/crystals/MASTER_PLANT_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_ASTROLOGY_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_BATH_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_COSMOLOGY_CRYSTAL.md",
]

TARGETS = [
    "F087R",
    "F087V",
    "F088R",
    "F088V",
    "F089R1",
    "F089R2",
    "F089V1",
    "F089V2",
    "F090R1",
    "F090R2",
    "F090V1",
    "F090V2",
    "F093R",
    "F093V",
    "F094R",
    "F094V",
    "F095R1",
    "F095R2",
    "F095V1",
    "F095V2",
    "F096R",
    "F096V",
    "F099R",
    "F099V",
    "F100R",
    "F100V",
    "F101R1",
    "F101V1",
    "F101V2",
    "F102R1",
    "F102R2",
    "F102V1",
    "F102V2",
    "F103R",
    "F103V",
    "F104R",
    "F104V",
    "F105R",
    "F105V",
    "F106R",
]

SIG = [
    ("qotor", "retort turn"),
    ("qot", "timed transmutation"),
    ("qok", "extraction circuit"),
    ("qo", "circulation circuit"),
    ("daiiin", "extended verification"),
    ("daiin", "verification checkpoint"),
    ("daiim", "vessel completion"),
    ("aiim", "vessel completion"),
    ("aiin", "cycle completion"),
    ("dam", "sealed union"),
    ("am", "vessel union"),
    ("dar", "root fixation"),
    ("dal", "structural fixation"),
    ("dor", "outlet fixation"),
    ("rod", "root fixation"),
    ("cth", "conduit binding"),
    ("ckh", "valve control"),
    ("chekal", "essence crystallization"),
    ("chokal", "heat crystallization"),
    ("cph", "cph-cluster"),
    ("cfh", "fire seal"),
    ("ol", "fluid carriage"),
    ("chor", "volatile outlet"),
    ("cho", "volatile heat"),
    ("saiin", "salt completion"),
    ("sar", "salt root"),
    ("sal", "salt matrix"),
    ("eee", "triple essence"),
    ("ee", "essence load"),
    ("otol", "timed fluid return"),
    ("ote", "timed drive"),
]


def asciiish(text: str) -> str:
    swaps = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2192": "->",
        "â€”": "-",
        "â€“": "-",
        "â†’": "->",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€�": '"',
    }
    for old, new in swaps.items():
        text = text.replace(old, new)
    return clean(text)


def disp(fid: str) -> str:
    match = re.match(r"F0*(\d+)([RV])(\d)?", fid)
    return f"f{match.group(1)}{match.group(2).lower()}{match.group(3) or ''}"


def canon(raw: str) -> str:
    match = re.match(r"F0*(\d+)([RV])(\d)?", raw.upper())
    return f"F{int(match.group(1)):03d}{match.group(2)}{match.group(3) or ''}"


def block_map(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in re.finditer(r"(?ms)^# \*\*FOLIO (F\d+[RV](?:\d)?) .*?(?=^# \*\*FOLIO |\Z)", text):
        out[canon(match.group(1))] = match.group(0).strip()
    return out


def section_map(block: str) -> dict[str, str]:
    out: dict[str, list[str]] = {"__head__": []}
    current = "__head__"
    for raw in block.splitlines():
        line = raw.rstrip()
        if line.startswith("## **"):
            current = asciiish(line)
            out[current] = []
        else:
            out[current].append(line)
    return {key: "\n".join(value).strip() for key, value in out.items()}


def pick_section(parts: dict[str, str], needle: str) -> str:
    for head, body in parts.items():
        if needle.lower() in head.lower():
            return body
    return ""


def heading_meta(block: str) -> tuple[str, str]:
    match = re.search(r"\*\*Title:\*\*\s*(.*?)\s+\*\*Sub-section:\*\*\s*(.*?)(?:\n|$)", block, re.S)
    if not match:
        return ("Untitled pharmaceutical page", "Pharmaceutical Part 1")
    return asciiish(match.group(1)), asciiish(match.group(2))


def line_id(raw: str) -> str:
    return raw.replace(" ", "").upper()


def parse_eva(section: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for key, eva in re.findall(r"\*\*([A-Za-z][A-Za-z0-9.]*)\*\*:\s*`([^`]+)`", section):
        out.append((line_id(key), eva.strip().replace("\\=", "=").replace("\\-", "-").rstrip("-")))
    return out


def parse_keyed(section: str, operational: bool = False) -> dict[str, str]:
    out: dict[str, str] = {}
    cur = None
    buf: list[str] = []
    for raw in section.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("---"):
            continue
        if operational:
            match = re.match(r"^\*\*Line\s+\d+\s+\(([A-Za-z][A-Za-z0-9.]*)\)\*\*:\s*(.*)$", stripped)
        else:
            match = re.match(r"^\*\*([A-Za-z][A-Za-z0-9.]*)\*\*:\s*(.*)$", stripped)
        if match:
            if cur:
                out[cur] = asciiish(" ".join(buf))
            cur = line_id(match.group(1))
            buf = [match.group(2).strip()]
        elif cur:
            buf.append(stripped)
    if cur:
        out[cur] = asciiish(" ".join(buf))
    return out


def token_features(token: str) -> list[str]:
    low = token.lower()
    out = ["damaged witness"] if "*" in low else []
    for needle, label in SIG:
        if needle in low and label not in out:
            out.append(label)
    return out or ["opaque operator"]


def tokens(eva: str) -> list[str]:
    return [tok for tok in re.split(r"[.\-=,\s]+", eva) if tok]


def literal(eva: str, explicit: str) -> str:
    if explicit:
        return cut(explicit, 360)
    return " | ".join(f"`{tok}` = {' / '.join(token_features(tok)[:3])}" for tok in tokens(eva)[:6])


def optext(eva: str, explicit: str, hint: str) -> str:
    if explicit:
        return cut(explicit, 360)
    seen: list[str] = []
    for tok in tokens(eva):
        for feat in token_features(tok):
            if feat != "opaque operator" and feat not in seen:
                seen.append(feat)
    acts: list[str] = []
    if "retort turn" in seen or "timed transmutation" in seen:
        acts.append("retort the route")
    if "circulation circuit" in seen or "extraction circuit" in seen:
        acts.append("circulate and refine the batch")
    if "conduit binding" in seen or "valve control" in seen:
        acts.append("stabilize the conduit and valve state")
    if "essence crystallization" in seen or "heat crystallization" in seen:
        acts.append("drive the product into crystal form")
    if "sealed union" in seen or "vessel union" in seen:
        acts.append("seal the compounded product")
    if "verification checkpoint" in seen or "extended verification" in seen:
        acts.append("verify before promotion")
    if not acts:
        acts = ["carry the local pharmaceutical operator chain"]
    return f"{', then '.join(acts[:3]).capitalize()}, keeping the line aligned with {phr(hint, 10)}."


def summary(eva: str, explicit: str) -> str:
    if explicit:
        return phr(explicit, 6) + " line"
    seen: list[str] = []
    for tok in tokens(eva):
        for feat in token_features(tok):
            if feat != "opaque operator" and feat not in seen:
                seen.append(feat)
    return (" / ".join(seen[:3]) if seen else "opaque operator") + " line"


def confidence(eva: str, explicit_token: str, explicit_op: str) -> str:
    if "*" in eva:
        return "mixed"
    if explicit_token and explicit_op:
        return "strong"
    return "mixed"


def build_groups(lines: list[tuple[str, str]]) -> list[dict[str, object]]:
    if any("." in lid for lid, _ in lines):
        grouped: dict[str, list[str]] = defaultdict(list)
        order: list[str] = []
        for lid, _ in lines:
            key = "TITLE" if lid.startswith("T") else lid.split(".", 1)[0]
            if key not in grouped:
                order.append(key)
            grouped[key].append(lid)
        out = []
        for key in order:
            title = "Title line" if key == "TITLE" else f"{key} corridor"
            out.append({"label": key, "title": title, "line_ids": grouped[key]})
        return out

    out: list[dict[str, object]] = []
    cur: list[str] = []
    idx = 1
    for lid, eva in lines:
        if lid.startswith("T"):
            if cur:
                out.append({"label": f"P{idx}", "title": f"Paragraph {idx} span", "line_ids": cur[:]})
                idx += 1
                cur = []
            out.append({"label": lid, "title": "Title line", "line_ids": [lid]})
            continue
        cur.append(lid)
        if eva.endswith("="):
            out.append({"label": f"P{idx}", "title": f"Paragraph {idx} span", "line_ids": cur[:]})
            idx += 1
            cur = []
    if cur:
        out.append({"label": f"P{idx}", "title": f"Paragraph {idx} span", "line_ids": cur[:]})
    if len(out) == 1 and len(lines) > 18:
        ids = [lid for lid, _ in lines]
        out = []
        for n, start in enumerate(range(0, len(ids), 8), start=1):
            out.append({"label": f"B{n}", "title": f"Block {n}", "line_ids": ids[start : start + 8]})
    return out


def count_features(lines: list[tuple[str, str]]) -> Counter:
    counts: Counter = Counter()
    for _lid, eva in lines:
        low = eva.lower()
        counts["units"] += 1
        counts["retort"] += low.count("qotor") + low.count("qot")
        counts["circulation"] += low.count("qok") + low.count("qo")
        counts["verification"] += low.count("daiin") + low.count("daiii") + low.count("dain") + low.count("aiin")
        counts["union"] += low.count("dam") + low.count("am")
        counts["salt"] += low.count("saiin") + low.count("sar") + low.count("sal")
        counts["damage"] += 1 if "*" in low else 0
    return counts


def folio_kind(subsection: str, title: str) -> str:
    text = f"{subsection} {title}".lower()
    if "star" in text:
        return "star formulary"
    if "foldout" in text:
        return "foldout recipe"
    if "intermediate" in text or "ingredient bank" in text or "pipeline" in text or "rectification" in text:
        return "intermediate formulary"
    return "jar and container recipe"


def risk_level(title: str, plain: str) -> str:
    text = f"{title} {plain}".lower()
    if any(word in text for word in ["volatile", "fire", "danger", "lock", "crystallization"]):
        return "elevated"
    if "star" in text:
        return "systemic"
    return "moderate"


def theorem(fid: str, title: str, subsection: str, counts: Counter) -> str:
    return (
        "\\[\\rho_* = (\\Psi_{\\mathrm{final}} \\circ \\Psi_{\\mathrm{body}} \\circ \\Psi_{\\mathrm{entry}})(\\rho_0)\\]\n\n"
        f"The formal theorem of `{disp(fid)}` is:\n\n"
        f"1. it belongs to `{asciiish(subsection)}` and executes `{asciiish(title).lower()}`\n"
        f"2. it carries `{counts['retort']}` retort/transmutation signals, `{counts['circulation']}` circulation or extraction signals, and `{counts['verification']}` completion markers across `{counts['units']}` visible lines\n"
        f"3. it preserves `{counts['union']}` union signals and `{counts['salt']}` salt signals as the local closure budget\n"
        f"4. it contributes one station to the Pharmaceutical Part 1 crystal and the Book V training arc\n"
    )


def parse_folio(fid: str, blocks: dict[str, str]) -> dict[str, object]:
    block = blocks[fid]
    title, subsection = heading_meta(block)
    parts = section_map(block)
    eva_section = pick_section(parts, "EVA Transcription")
    token_section = pick_section(parts, "VML Token Translation")
    operational_section = pick_section(parts, "Operational Translation")
    visual_section = pick_section(parts, "Visual Description")
    plain_section = pick_section(parts, "Plain-Language")

    eva_rows = parse_eva(eva_section)
    token_rows = parse_keyed(token_section, operational=False)
    op_rows = parse_keyed(operational_section, operational=True)
    visual = asciiish(visual_section)
    plain = asciiish(plain_section)
    lines = [
        (
            lid,
            eva,
            literal(eva, token_rows.get(lid, "")),
            optext(eva, op_rows.get(lid, ""), plain or title),
            summary(eva, op_rows.get(lid, "") or token_rows.get(lid, "")),
            confidence(eva, token_rows.get(lid, ""), op_rows.get(lid, "")),
        )
        for lid, eva in eva_rows
    ]
    groups = build_groups([(lid, eva) for lid, eva in eva_rows])
    counts = count_features(eva_rows)
    kind = folio_kind(subsection, title)
    purpose = (
        f"`{disp(fid)}` is a `{kind}` inside `Book V - Pharmaceutical Part 1`. "
        f"Source title: {title}. Source subsection: {subsection}. "
        f"Local source summary: {cut(plain or visual or title, 280)}"
    )
    zero_claim = cut(plain or visual or title, 300)
    crystal_tags = [
        asciiish(subsection),
        asciiish(title),
        f"{counts['retort']} retort/circulation signals",
        f"{counts['verification']} completion markers",
    ]

    folio = make_folio(
        folio_id=fid,
        quire="Book V",
        bifolio=f"Pharmaceutical Part 1 station {disp(fid)}",
        manuscript_role=kind,
        purpose=purpose,
        zero_claim=zero_claim,
        botanical=f"Pharmaceutical subtype: {asciiish(subsection)}",
        risk=risk_level(title, plain),
        confidence="high on local process role; medium on exact token semantics",
        visual_grammar=[
            f"Book V Part 1 pharmaceutical folio `{disp(fid)}`",
            f"title: {title}",
            f"subsection: {subsection}",
            f"visible unit count: {counts['units']}",
            cut(visual or "visual witness preserved through the local source transcription", 140),
        ],
        full_eva="\n".join(f"{lid}: {eva}" for lid, eva in eva_rows),
        core_vml=[
            f"`{disp(fid)}` = {kind}",
            f"`{disp(fid)}` title = {title}",
            f"`{disp(fid)}` section = {subsection}",
            f"`{disp(fid)}` counts = retort {counts['retort']} / circulation {counts['circulation']} / verification {counts['verification']}",
        ],
        groups=groups,
        lines=lines,
        tarot_cards=tarot(len(lines)),
        movements=[line[4] for line in lines],
        direct=zero_claim,
        math=(
            f"Across the formal lenses, `{disp(fid)}` behaves as a `{kind}` with "
            f"{counts['retort']} retort/transmutation events and {counts['verification']} completion markers "
            f"distributed across {counts['units']} visible lines."
        ),
        mythic=(
            f"Across the mythic lenses, `{disp(fid)}` is one training station in the Book V fire curriculum: "
            f"{asciiish(title).lower()}."
        ),
        compression=cut(zero_claim, 180),
        typed_state_machine=(
            f"\\[\\mathcal R_{{{disp(fid)}}} = \\{{r_{{\\mathrm{{entry}}}}, r_{{\\mathrm{{body}}}}, r_{{\\mathrm{{terminal}}}}\\}}\\]\n"
            f"\\[\\delta(e_{{\\mathrm{{{disp(fid)}}}}}): r_{{\\mathrm{{entry}}}} \\to r_{{\\mathrm{{body}}}} \\to r_{{\\mathrm{{terminal}}}}\\]"
        ),
        invariants=(
            f"\\[N_{{\\mathrm{{retort}}}}({disp(fid)})={counts['retort']}, \\qquad "
            f"N_{{\\mathrm{{circulation}}}}({disp(fid)})={counts['circulation']}, \\qquad "
            f"N_{{\\mathrm{{verify}}}}({disp(fid)})={counts['verification']}\\]\n"
            f"\\[N_{{\\mathrm{{union}}}}({disp(fid)})={counts['union']}, \\qquad "
            f"N_{{\\mathrm{{salt}}}}({disp(fid)})={counts['salt']}, \\qquad "
            f"N_{{\\mathrm{{damage}}}}({disp(fid)})={counts['damage']}\\]"
        ),
        theorem=theorem(fid, title, subsection, counts),
        crystal_contribution=crystal_tags,
        pointer_title=asciiish(title).title(),
        pointer_position=f"`{disp(fid)}` inside Book V / Pharmaceutical Part 1",
        pointer_page_type=kind,
        pointer_conclusion=zero_claim,
        pointer_judgment=f"`{disp(fid)}` is best read as `{kind}` under the source title `{title}`.",
        currier_language="Pharmaceutical",
        currier_hand="Pharmaceutical",
        reading_contract=[
            "Book V pages are recipes and recipe infrastructure, not botanical monographs.",
            "The local source translation is preserved explicitly and not collapsed into hidden paraphrase.",
            "Subpage foldouts remain independent stations.",
            "Visible uncertainty and damaged witness markers remain explicit.",
        ],
    )
    folio["book_label"] = "Book V - Pharmaceutical Part 1"
    folio["release_target"] = "Pharmaceutical 1 Crystal, unified corpus, metro layer, and master manuscript"
    folio["direct_sources"] = DIRECT_SOURCES
    folio["derived_sources"] = DERIVED_SOURCES
    return folio


def write_one(folio: dict[str, object]) -> None:
    fid = folio["folio_id"]
    (FOLIOS_DIR / f"{fid}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
    (FOLIOS_DIR / f"{fid}.md").write_text(render_pointer(folio), encoding="utf-8")


def subsection_summary(folios: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for folio in folios:
        key = folio["core_vml"][2].split(" = ", 1)[1]
        out[key].append(folio)
    return out


def put_block(path: Path, start: str, end: str, body: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    rx = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.S)
    if rx.search(current):
        current = rx.sub(block, current)
    else:
        current = current.rstrip() + "\n\n" + block if current else block
    path.write_text(current, encoding="utf-8")


def full_section_doc(folios: list[dict[str, object]]) -> str:
    grouped = subsection_summary(folios)
    atlas = []
    for folio in folios:
        atlas.append(
            f"- `{disp(folio['folio_id'])}` - {folio['core_vml'][1].split(' = ', 1)[1]} - {folio['manuscript_role']} - {cut(folio['all_lens_zero_point'], 140)}"
        )
    subsection_rows = [f"- `{name}` - {len(group)} translated units" for name, group in grouped.items()]
    return (
        "# Pharmaceutical 1 Full\n\n"
        "## Scope\n\n"
        "- Book: `Book V - Pharmaceutical Part 1`\n"
        "- Range: `f87r-f106r`\n"
        f"- Completed translated units: `{len(folios)}`\n"
        "- Coverage: jar recipes, foldout recipe core, intermediate formulary, and first star-based formularies\n\n"
        "## Section Architecture\n\n"
        + "\n".join(subsection_rows)
        + "\n\n## Section Synthesis\n\n"
        "Pharmaceutical Part 1 is the manuscript's first full recipe curriculum. It turns the earlier books into executable medicine grammar: Plant supplies matter, Astrology supplies timing, Bath supplies purification infrastructure, and Cosmology supplies routing. Book V Part 1 then teaches the operator how to seal volatile matter, stage iterative SOPs, scale foldout machines into repeatable jar recipes, and finally cross into star-governed formulation.\n\n"
        "## Folio-By-Folio Atlas\n\n"
        + "\n".join(atlas)
        + "\n\n## Current Zero Point\n\n"
        "Book V Part 1 means: build the pharmaceutical machine, run it in repeatable loops, introduce ingredient banks and rectification, then cross the threshold into star-structured compounding.\n"
    )


def crystal_doc(folios: list[dict[str, object]]) -> str:
    grouped = subsection_summary(folios)
    lines = []
    for name, group in grouped.items():
        short = ", ".join(disp(f["folio_id"]) for f in group[:6])
        if len(group) > 6:
            short += ", ..."
        lines.append(f"- `{name}`: {len(group)} units anchored by {short}")
    return (
        "# Pharmaceutical 1 Crystal\n\n"
        "## Scope\n\n"
        "- Book: `Book V - Pharmaceutical Part 1`\n"
        "- Range: `f87r-f106r`\n"
        f"- Current translated stations: `{len(folios)}` authoritative final-draft units\n\n"
        "## Synthesis\n\n"
        "This crystal gathers the first half of the Voynich pharmaceutical fire curriculum. The section begins with infrastructure and vessel law, expands into foldout machine logic, stabilizes into jar and intermediate formulary technique, and then enters star-governed recipe sequencing. Its repeating invariants are circulation, verification, vessel closure, and progressive crystallization.\n\n"
        "## Internal Districts\n\n"
        + "\n".join(lines)
        + "\n\n## Metro Map\n\n"
        "- `Recipe Primer Line`: `f87r-f88v` define what a pharmaceutical page is\n"
        "- `Foldout Machine Line`: `f89r1-f90v2` scale the universal machine into local recipe loops\n"
        "- `Ingredient Bank and Rectification Line`: `f99r-f102v2` turn recipes into labeled and correctable pipelines\n"
        "- `Star Threshold Line`: `f103r-f106r` convert recipe flow into checkpointed star sequencing\n\n"
        "## Emergent Metro Map\n\n"
        "- `Vessel Before Product`: the book insists on lawful containment before aggressive product claims\n"
        "- `Verification Before Union`: completion markers govern promotion into sealed medicine\n"
        "- `From Continuous Loop To Discrete Stage`: the section gradually teaches stage-based compounding without losing flow grammar\n\n"
        "## Current Zero Point\n\n"
        "Part 1 is the training arc that turns preparation into executable formulation.\n"
    )


def synthesis_doc() -> str:
    return (
        "# Pharmaceutical 1 Synthesis\n\n"
        "## Core Claim\n\n"
        "Book V Part 1 is the manuscript's executable first-half recipe school: payload definition, volatile sealing, iterative SOP discipline, foldout machine logic, intermediate formulary standardization, rectification, and the first rise into star-based compounding.\n\n"
        "## Stable Invariants\n\n"
        "- containment before intensity\n"
        "- verification before union\n"
        "- repetition before scale\n"
        "- labeled ingredients before advanced formulation\n"
        "- progressive crystallization rather than single-step fixation\n\n"
        "## Cross-Book Bridges\n\n"
        "- Plant supplies raw matter and bridge tokens\n"
        "- Astrology supplies timing and stage rhythm\n"
        "- Bath supplies circulation and rectification infrastructure\n"
        "- Cosmology supplies network routing intuition\n"
    )


def master_crystal_doc(folios: list[dict[str, object]]) -> str:
    atlas = []
    for folio in folios:
        atlas.append(
            f"- `{disp(folio['folio_id'])}` - {folio['core_vml'][1].split(' = ', 1)[1]} - {cut(folio['all_lens_zero_point'], 120)}"
        )
    return (
        "# MASTER PHARMACEUTICAL 1 CRYSTAL\n\n"
        "## Scope\n\n"
        "- Section: `Book V - Pharmaceutical Part 1`\n"
        "- Range: `f87r-f106r`\n"
        f"- Authoritative translated units: `{len(folios)}`\n\n"
        "## Governing Thesis\n\n"
        "The first pharmaceutical half is the manuscript's executable recipe school. It teaches how to define payloads, seal volatile outputs, iterate SOPs, operate foldout machines, formalize ingredient banks, rectify circulation, and finally rise into star-governed formulation.\n\n"
        "## Full Folio Atlas\n\n"
        + "\n".join(atlas)
        + "\n\n## Wave One - Deep Cross-Section Analysis\n\n"
        "Plant contributes source identity and rare bridge tokens. Astrology contributes timing law and checkpoint rhythm. Bath contributes circulation, return gates, and purification infrastructure. Cosmology contributes the network-scale intuition that local jars and stars are stations in a larger route system. Pharmaceutical Part 1 recombines all four prior books into directly executable formulation grammar.\n\n"
        "## Wave Two - Emergent Reading\n\n"
        "The emergent shape of Part 1 is pedagogical. The operator is first taught how to hold volatile matter, then how to repeat lawful loops, then how to standardize and label ingredients, and only then how to move into stage-marked star compounding. The section is less a list of recipes than a graduated fire curriculum.\n\n"
        "## Metro Map I - Deep Cross-Section Pharmaceutical Metro Map\n\n"
        "- `Payload and Sealing Line`: `f87r-f87v`\n"
        "- `Iterative SOP Line`: `f88r-f88v`\n"
        "- `Foldout Universal Machine Line`: `f89r1-f90v2`\n"
        "- `Plant-Reentry and Controlled Oscillation Line`: `f93r-f96v`\n"
        "- `Intermediate Formulary and Rectification Line`: `f99r-f102v2`\n"
        "- `Star Threshold and Progressive Crystallization Line`: `f103r-f106r`\n\n"
        "## Metro Map II - Emergent Pharmaceutical Metro Map\n\n"
        "- `Contain Before Intensify`\n"
        "- `Repeat Before Scale`\n"
        "- `Label Before Compound`\n"
        "- `Checkpoint Before Promotion`\n"
        "- `Crystallize By Stages, Not By Leap`\n\n"
        "## Metro Map III - Plant + Astrology + Bath + Cosmology + Pharmaceutical 1 Synthesized Metro Map\n\n"
        "- `Source Supply -> Timing Gate -> Purification Route -> Network Placement -> Recipe Execution`\n"
        "- `Salt and Spirit Supply Chains` from Book I now terminate in explicit jar and star formulary stations\n"
        "- `Bath return-gate logic` becomes pharmaceutical rectification discipline\n"
        "- `Astrological stage logic` becomes star checkpoint sequencing\n"
        "- `Cosmological routing` becomes distributed pharmaceutical machine design\n\n"
        "## Section Theorem\n\n"
        "Book V Part 1 means: define the pharmaceutical machine, prove it by repetition, formalize it by labels and gates, and cross it into star-ordered compounding.\n"
    )


def sync_rollups(folios: list[dict[str, object]]) -> None:
    (SECTIONS_DIR / "PHARMACEUTICAL_1_FULL.md").write_text(full_section_doc(folios), encoding="utf-8")
    (SECTIONS_DIR / "PHARMACEUTICAL_1_SYNTHESIS.md").write_text(synthesis_doc(), encoding="utf-8")
    (CRYSTALS_DIR / "PHARMACEUTICAL_1_CRYSTAL.md").write_text(crystal_doc(folios), encoding="utf-8")
    (CRYSTALS_DIR / "MASTER_PHARMACEUTICAL_1_CRYSTAL.md").write_text(master_crystal_doc(folios), encoding="utf-8")

    units = ", ".join(disp(f["folio_id"]) for f in folios[:12]) + ", ..."
    put_block(
        UNIFIED_DIR / "VOYNICH_FULL_TRANSLATION.md",
        "<!-- AUTO_BOOK5_PART1_UNIFIED_START -->",
        "<!-- AUTO_BOOK5_PART1_UNIFIED_END -->",
        (
            "## Book V - Pharmaceutical Part 1\n\n"
            f"- completed authoritative units: `{len(folios)}`\n"
            f"- range: `f87r-f106r`\n"
            f"- opening stations: `{units}`\n"
            "- status: the first pharmaceutical half is now built as a parallel dense-folio section\n"
        ),
    )
    put_block(
        UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT.md",
        "<!-- AUTO_BOOK5_PART1_MASTER_START -->",
        "<!-- AUTO_BOOK5_PART1_MASTER_END -->",
        (
            "## Book V Part 1 Completion Delta\n\n"
            f"- authoritative pharmaceutical units now on disk: `{len(folios)}`\n"
            "- the manuscript now includes the payload/sealing preface, iterative SOP corridor, foldout universal machine, intermediate formulary, rectification engine, and first star formulary rise through `f106r`\n"
            "- current Book V theorem: define, seal, iterate, label, rectify, and crystallize in stages\n"
        ),
    )
    put_block(
        METRO_DIR / "VOYNICH_METRO_MAP_WORKING.md",
        "<!-- AUTO_BOOK5_PART1_METRO_START -->",
        "<!-- AUTO_BOOK5_PART1_METRO_END -->",
        (
            "## Book V Part 1 Metro Delta\n\n"
            "- `Payload and Sealing Line` activates at `f87r-f87v`\n"
            "- `Universal Machine Line` activates across `f89r1-f90v2`\n"
            "- `Ingredient Bank and Rectification Line` activates across `f99r-f102v2`\n"
            "- `Star Threshold Line` activates across `f103r-f106r`\n"
            "- Book V now upgrades the earlier books from supply and routing into executable formulation curriculum\n"
        ),
    )
    put_block(
        CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md",
        "<!-- AUTO_BOOK5_PART1_FULL_CRYSTAL_START -->",
        "<!-- AUTO_BOOK5_PART1_FULL_CRYSTAL_END -->",
        (
            "## Book V Part 1 Delta\n\n"
            "- completed section: `f87r-f106r`\n"
            "- new whole-manuscript contribution: the manuscript now contains its first full pharmaceutical training arc rather than only a Book V horizon\n"
            "- active cross-book theorem: supply, time, purification, and routing now terminate in explicit recipe execution\n"
        ),
    )

    status_path = MANIFESTS_DIR / "CORPUS_BUILD_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    status = status.replace(
        "| `crystals/PHARMACEUTICAL_1_CRYSTAL.md` | initialized |",
        "| `crystals/PHARMACEUTICAL_1_CRYSTAL.md` | authoritative completed Book V Part 1 crystal |",
    )
    status = status.replace(
        "| `sections/PHARMACEUTICAL_1_FULL.md` | initialized |",
        "| `sections/PHARMACEUTICAL_1_FULL.md` | authoritative completed Book V Part 1 synthesis |",
    )
    status = status.replace(
        "| `sections/PHARMACEUTICAL_1_SYNTHESIS.md` | initialized |",
        "| `sections/PHARMACEUTICAL_1_SYNTHESIS.md` | completed concise Book V Part 1 synthesis |",
    )
    if "MASTER_PHARMACEUTICAL_1_CRYSTAL.md" not in status:
        status = status.replace(
            "| `crystals/PHARMACEUTICAL_2_CRYSTAL.md` | initialized |",
            "| `crystals/PHARMACEUTICAL_2_CRYSTAL.md` | initialized |\n| `crystals/MASTER_PHARMACEUTICAL_1_CRYSTAL.md` | complete master Book V Part 1 analysis, metro map, and emergent metro map |",
        )
    status = status.replace(
        "1. `f087r`\n2. `f087v`\n3. `f088r`\n4. `f088v`\n5. `f093r`\n6. `f093v`\n7. `f094r`\n8. `f094v`",
        "1. `f106v`\n2. `f107r`\n3. `f107v`\n4. `f108r`\n5. `f108v`\n6. `pharmaceutical 1 synthesis refinement`\n7. `pharmaceutical 2 full section`\n8. `full pharmaceutical crystal`",
    )
    status_path.write_text(status, encoding="utf-8")
    put_block(
        status_path,
        "<!-- AUTO_BOOK5_PART1_STATUS_START -->",
        "<!-- AUTO_BOOK5_PART1_STATUS_END -->",
        (
            "## Book V Part 1 Parallel Completion\n\n"
            f"- authoritative pharmaceutical units rendered in parallel: `{len(folios)}`\n"
            "- completed range: `f87r-f106r`\n"
            "- section synthesis completed in `sections/PHARMACEUTICAL_1_FULL.md`\n"
            "- crystal completed in `crystals/PHARMACEUTICAL_1_CRYSTAL.md`\n"
            "- master crystal completed in `crystals/MASTER_PHARMACEUTICAL_1_CRYSTAL.md`\n"
        ),
    )


def main() -> None:
    blocks = block_map(MAIN.read_text(encoding="utf-8"))
    missing = [fid for fid in TARGETS if fid not in blocks]
    if missing:
        raise SystemExit(f"Missing pharmaceutical blocks: {missing}")
    folios = [parse_folio(fid, blocks) for fid in TARGETS]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(write_one, folios))
    sync_rollups(folios)
    print(f"Rendered {len(folios)} Pharmaceutical Part 1 folios.")


if __name__ == "__main__":
    main()
