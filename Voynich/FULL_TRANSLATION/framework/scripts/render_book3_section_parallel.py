from __future__ import annotations

import re
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

SECTION_DOC = next(p for p in (WS / "NEW").iterdir() if p.name.startswith("SECTION III") and p.suffix == ".md")
MAIN = WS / "NEW" / "working" / "VML BALNEOLOGICAL SECTION f75r through f84v.md"
COMPLETE = WS / "NEW" / "working" / "VML_BALNEOLOGICAL_SECTION_COMPLETE.md"

BOOK3_DIRECT_SOURCES = [
    "NEW/SECTION III - BOOK III - THE BATH PURIFICATION SECTION.md",
    "NEW/working/VML BALNEOLOGICAL SECTION f75r through f84v.md",
    "NEW/working/VML_BALNEOLOGICAL_SECTION_COMPLETE.md",
    "eva/EVA TRANSCRIPTION ORIGIONAL.txt",
]

BOOK3_DERIVED_SOURCES = [
    "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md",
    "FULL_TRANSLATION/framework/registry/lenses.json",
    "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
    "FULL_TRANSLATION/crystals/MASTER_PLANT_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_ASTROLOGY_CRYSTAL.md",
]

TARGETS = [f"F{n:03d}{side}" for n in range(75, 85) for side in ("R", "V")]

GROUP_TITLES = {
    "P": "Protocol corridor",
    "K": "Pipe and channel labels",
    "L": "Pool and node labels",
    "R": "Route corridor",
    "X": "Channel key register",
    "W": "Witness ledger",
}

SIG = [
    ("qokeee", "triple-essence spike"),
    ("qoeee", "triple-essence spike"),
    ("qokee", "circulation command"),
    ("qoked", "circulation command"),
    ("qok", "circulation command"),
    ("qol", "circulation return"),
    ("qor", "circulation return"),
    ("shedy", "settle phase"),
    ("sheedy", "settle phase"),
    ("sheol", "settle phase"),
    ("shckhy", "valve clamp"),
    ("sheckhy", "valve clamp"),
    ("checkhy", "valve clamp"),
    ("chckhy", "valve clamp"),
    ("ckhy", "valve clamp"),
    ("kch", "valve clamp"),
    ("daiin", "commit checkpoint"),
    ("daiii", "commit checkpoint"),
    ("dain", "commit checkpoint"),
    ("deiin", "extended commit"),
    ("saiin", "salt completion"),
    ("sar", "salt test"),
    ("sal", "salt test"),
    ("otol", "return gate"),
    ("oteey", "return gate"),
    ("otedy", "return gate"),
    ("oteol", "return gate"),
    ("ol", "fluid conduit"),
    ("dam", "sealed union"),
    ("am", "vessel union"),
    ("qokal", "governance matrix"),
    ("dar", "root fixation"),
    ("dal", "structural fixation"),
    ("rar", "rotation return"),
    ("rol", "rotation return"),
    ("chor", "volatile outlet"),
    ("cho", "volatile outlet"),
]


def disp(fid: str) -> str:
    match = re.match(r"F0*(\d+)([RV])", fid)
    return f"f{match.group(1)}{match.group(2).lower()}"


def split_folio_blocks(text: str) -> dict[str, str]:
    pattern = re.compile(r"(?ms)^# \*\*FOLIO (F\d+[RV]) [^\n]*\*\*\n(.*?)(?=^# \*\*FOLIO F\d+[RV] [^\n]*\*\*|\Z)")
    out: dict[str, str] = {}
    for match in pattern.finditer(text):
        raw = match.group(1).upper()
        fid = f"F{int(raw[1:-1]):03d}{raw[-1]}"
        out[fid] = match.group(0).strip()
    return out


def architecture_map(text: str) -> tuple[dict[str, dict[str, object]], str]:
    table_match = re.search(r"## Complete Folio Architecture \(20 Folios\)(.*?)(?:\n## |\Z)", text, re.S)
    if not table_match:
        raise ValueError("Could not find bath architecture table.")
    section = table_match.group(1)
    out: dict[str, dict[str, object]] = {}
    total_line = ""
    for raw in section.splitlines():
        line = raw.strip()
        if line.startswith("|") and re.search(r"\|\s*\d+\s*\|", line):
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) < 8:
                continue
            fid = cols[1].upper()
            fid = f"F{int(fid[1:-1]):03d}{fid[-1]}"
            out[fid] = {
                "folio": fid,
                "title": clean(cols[2]),
                "paragraphs": int(cols[3]),
                "qo": int(cols[4]),
                "valves": int(cols[5]),
                "seals": int(cols[6]),
                "feature": clean(cols[7]),
            }
        elif line.startswith("**SECTION TOTALS:"):
            total_line = clean(line)
    return out, total_line


def teaching_map(text: str) -> dict[str, list[str]]:
    pattern = re.compile(r"(?ms)^## (F\d+[RrVv])[^\\n]*What It Teaches[^\n]*\n(.*?)(?=^---$|^# |\Z)")
    out: dict[str, list[str]] = {}
    for match in pattern.finditer(text):
        fid = match.group(1).upper()
        fid = f"F{int(fid[1:-1]):03d}{fid[-1]}"
        body = match.group(2)
        items: list[str] = []
        for raw in body.splitlines():
            line = clean(raw)
            line = re.sub(r"^\d+\.\s*", "", line)
            line = re.sub(r"^-+\s*", "", line)
            if not line:
                continue
            items.append(line)
        out[fid] = items
    return out


def extract_title_and_function(block: str, fallback_title: str) -> tuple[str, str]:
    match = re.search(r"\*\*Title:\*\*\s*(.*?)\s*\*\*Function:\*\*\s*(.*?)(?:\n|$)", block, re.S)
    if not match:
        return fallback_title, "Bath purification control page."
    return clean(match.group(1)), clean(match.group(2))


def normalize_eva(raw: str) -> str:
    text = raw.replace("\\=", "=").replace("\\-", "-").replace("\\*", "*")
    text = re.sub(r"\{[^}]+\}", "", text)
    text = re.sub(r"\s+", "", text)
    return text.rstrip("-")


def extract_eva_lines(block: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(r"\*\*([A-Za-z0-9.]+)\*\*\s*\\?\[[^\]]+\\?\]:\s*`([^`]+)`")
    out: list[tuple[str, str, str]] = []
    for match in pattern.finditer(block):
        lid = match.group(1).upper().replace(" ", "")
        raw = match.group(2).replace("\\=", "=").replace("\\-", "-").replace("\\*", "*").strip()
        out.append((lid, raw.rstrip("-"), normalize_eva(raw)))
    return out


def extract_plain_language(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for label in ["Description", "VML Structural Decode", "What you're looking at", "What the text says", "Process statistics"]:
        match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.*?)(?=\n\*\*|\n## |\n---|\Z)", block, re.S)
        out[label] = clean(match.group(1)) if match else ""
    return out


def prefix_key(line_id: str) -> str:
    match = re.match(r"([A-Z]+)", line_id)
    return match.group(1)[0] if match else "W"


def build_groups(lines: list[tuple[str, str, str]]) -> list[dict[str, object]]:
    order: list[str] = []
    grouped: dict[str, list[str]] = {}
    for lid, _raw, _eva in lines:
        key = prefix_key(lid)
        if key not in grouped:
            order.append(key)
            grouped[key] = []
        grouped[key].append(lid)
    return [{"label": key, "title": GROUP_TITLES.get(key, f"{key} corridor"), "line_ids": grouped[key]} for key in order]


def bath_signatures(token: str) -> list[str]:
    low = token.lower()
    out: list[str] = []
    if "*" in low:
        out.append("damaged witness")
    for needle, label in SIG:
        if needle in low and label not in out:
            out.append(label)
    return out or ["opaque operator"]


def tokens(eva: str) -> list[str]:
    return [tok for tok in re.split(r"[.\-=,\s]+", eva) if tok]


def literal(eva: str) -> str:
    return " | ".join(f"`{tok}` = {' / '.join(bath_signatures(tok)[:3])}" for tok in tokens(eva)[:6])


def optext(eva: str, hint: str) -> str:
    seen: list[str] = []
    for token in tokens(eva):
        for feat in bath_signatures(token):
            if feat not in seen and feat != "opaque operator":
                seen.append(feat)
    acts: list[str] = []
    if "circulation command" in seen:
        acts.append("circulate the charge")
    if "valve clamp" in seen:
        acts.append("clamp and test the flow")
    if "settle phase" in seen:
        acts.append("let the fraction settle")
    if "salt test" in seen or "salt completion" in seen:
        acts.append("read the salt purity signal")
    if "commit checkpoint" in seen or "extended commit" in seen:
        acts.append("commit the stable state")
    if "return gate" in seen:
        acts.append("route through the return gate")
    if "root fixation" in seen:
        acts.append("anchor the route at the root")
    if "structural fixation" in seen:
        acts.append("lock the structure")
    if "sealed union" in seen or "vessel union" in seen:
        acts.append("seal the purified union")
    if "triple-essence spike" in seen:
        acts.append("raise the essence load")
    if not acts:
        acts = ["carry the local bath operator chain"]
    return f"{', then '.join(acts[:3]).capitalize()}, keeping the line aligned with {phr(hint, 10)}."


def summary(eva: str) -> str:
    seen: list[str] = []
    for token in tokens(eva):
        for feat in bath_signatures(token):
            if feat not in seen and feat != "opaque operator":
                seen.append(feat)
    return (" / ".join(seen[:3]) if seen else "opaque operator") + " line"


def confidence(eva: str) -> str:
    return "mixed" if "*" in eva or "skippedtext" in eva.lower() else "strong"


def finalize_book3_folio(folio: dict[str, object]) -> dict[str, object]:
    folio["book_label"] = "Book III - Bath / balneological"
    folio["release_target"] = "Bath Crystal, unified corpus, metro layer, and master manuscript"
    folio["direct_sources"] = BOOK3_DIRECT_SOURCES
    folio["derived_sources"] = BOOK3_DERIVED_SOURCES
    return folio


def risk_level(arch: dict[str, object]) -> str:
    if arch["valves"] >= 12 or arch["seals"] >= 4:
        return "high"
    if arch["valves"] >= 7 or arch["seals"] >= 2:
        return "moderate"
    return "controlled"


def build(fid: str, block: str, arch: dict[str, dict[str, object]], teaches: dict[str, list[str]]) -> dict[str, object]:
    section_stats = arch[fid]
    plain = extract_plain_language(block)
    title, function = extract_title_and_function(block, section_stats["title"])
    eva_lines = extract_eva_lines(block)
    if not eva_lines:
        raise ValueError(f"No EVA lines parsed for {fid}.")
    rows = [
        (lid, eva, literal(eva), optext(eva, function or plain["What the text says"]), summary(eva), confidence(eva))
        for lid, _raw, eva in eva_lines
    ]
    full_eva = "\n".join(f"{lid}: {raw}" for lid, raw, _eva in eva_lines)
    title_line = plain["What you're looking at"] or title
    direct = plain["What the text says"] or function
    teach_lines = teaches.get(fid, [])
    contribution = [
        f"{title} station",
        f"key feature: {section_stats['feature']}",
        f"load: {section_stats['qo']} circulation / {section_stats['valves']} valves / {section_stats['seals']} seals",
    ]
    for item in teach_lines[:3]:
        contribution.append(item)
    math = (
        f"Across the formal lenses, `{disp(fid)}` behaves as a fixed-point purification page with "
        f"N_qo={section_stats['qo']}, N_valve={section_stats['valves']}, and N_seal={section_stats['seals']}. "
        f"The governing update is x_(n+1) = V(C(x_n)); stop when ||x_(n+1)-x_n|| <= eps, then publish y = S(x_*)."
    )
    mythic = (
        f"`{disp(fid)}` is a bathhouse-laboratory chamber: descend through linked pools, purify by circulation, "
        f"prove stability at the clamps, and only then carry the living fluid onward."
    )
    typed_state_machine = f"""
\\[
\\mathcal R_{{{disp(fid)}}} = \\{{r_{{charge}}, r_{{circulate}}, r_{{clamp}}, r_{{commit}}, r_{{seal}}\\}}
\\]
\\[
\\delta(r_{{charge}})=r_{{circulate}}, \\qquad
\\delta(r_{{circulate}})=r_{{clamp}}, \\qquad
\\delta(r_{{clamp}})=
\\begin{{cases}}
r_{{circulate}} & \\text{{if }} \\Delta_n > 0 \\\\
r_{{commit}} & \\text{{if }} \\Delta_n = 0
\\end{{cases}}
\\]
\\[
\\delta(r_{{commit}})=
\\begin{{cases}}
r_{{seal}} & \\text{{if }} P_{{salt}} = 1 \\\\
r_{{circulate}} & \\text{{otherwise}}
\\end{{cases}}
\\]
""".strip()
    invariants = f"""
\\[
N_{{\\mathrm{{qo}}}}({disp(fid)}) = {section_stats['qo']}, \\qquad
N_{{\\mathrm{{valve}}}}({disp(fid)}) = {section_stats['valves']}, \\qquad
N_{{\\mathrm{{seal}}}}({disp(fid)}) = {section_stats['seals']}
\\]
\\[
\\forall n,\\; x_n \\in \\mathcal P_{{bath}} \\Rightarrow C(x_n) \\in \\mathcal P_{{bath}}, \\qquad
S(x_*) = 1 \\Rightarrow \\text{{release}}(x_*)
\\]
""".strip()
    theorem = f"""
\\[
x_* = \\operatorname{{Fix}}(V \\circ C), \\qquad y = S(x_*)
\\]

The formal theorem of `{disp(fid)}` is:

1. the page is a purification controller, not an ornamental bath,
2. circulation and clamp logic dominate the visible route,
3. the stable state is published only after salt/commit evidence is satisfied,
4. the folio's distinctive role is `{section_stats['feature']}`.
""".strip()
    purpose = (
        f"`{disp(fid)}` is a Book III bath page. {function} "
        f"{cut(plain['Description'], 220)} {cut(direct, 220)}"
    )
    return finalize_book3_folio(make_folio(
        folio_id=fid,
        quire="Book III purification band",
        bifolio=disp(fid),
        manuscript_role=function.lower(),
        purpose=purpose,
        zero_claim=cut(direct, 220),
        botanical="Bath / purification infrastructure page",
        risk=risk_level(section_stats),
        confidence="high on bath control law and page role",
        visual_grammar=[
            cut(title_line, 180),
            cut(plain["Description"], 180),
            "proximity = scope, vertical = temporal, cascade = gravity flow",
            cut(plain["VML Structural Decode"], 180),
        ],
        full_eva=full_eva,
        core_vml=[
            f"`qo-` = {section_stats['qo']} circulation commands",
            f"`valves` = {section_stats['valves']} clamp checkpoints",
            f"`seals` = {section_stats['seals']} terminal seals",
            f"`paragraphs` = {section_stats['paragraphs']} visible units",
            f"`key feature` = {section_stats['feature']}",
        ],
        groups=build_groups(eva_lines),
        lines=rows,
        tarot_cards=tarot(len(rows)),
        movements=[row[3] for row in rows],
        direct=f"{direct} Process statistics: {plain['Process statistics']}".strip(),
        math=math,
        mythic=mythic,
        compression=cut(direct, 160),
        typed_state_machine=typed_state_machine,
        invariants=invariants,
        theorem=theorem,
        crystal_contribution=contribution,
        pointer_title=title,
        pointer_position=f"the {disp(fid)} bath station inside Book III",
        pointer_page_type=f"balneological protocol page with {len(eva_lines)} visible units",
        pointer_conclusion=cut(direct, 140),
        pointer_judgment=f"{title_line} {cut(direct, 180)}",
        currier_language="unknown",
        currier_hand="unknown",
    ))


def append_if_missing(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + addition.strip() + "\n", encoding="utf-8")


def ensure_status_row(status: str, old: str, new: str) -> str:
    return status.replace(old, new) if old in status else status


def write_rollups(folios: list[dict[str, object]], arch: dict[str, dict[str, object]], teaches: dict[str, list[str]], totals: str) -> None:
    atlas = "\n".join(f"- `{disp(f['folio_id'])}`: {cut(f['direct_operational_meaning'], 180)}" for f in folios)
    phases = {
        "initializer": ["F075R", "F075V", "F076R", "F076V"],
        "routing": ["F077R", "F077V", "F078R", "F078V"],
        "lattice": ["F079R", "F079V", "F080R", "F080V"],
        "graded": ["F081R", "F081V", "F082R", "F082V"],
        "terminal": ["F083R", "F083V", "F084R", "F084V"],
    }
    folio_entries: list[str] = []
    for folio in folios:
        fid = folio["folio_id"]
        meta = arch[fid]
        teach = teaches.get(fid, [])
        teach_block = "\n".join(f"- {line}" for line in teach[:4]) if teach else "- teaching summary not isolated"
        folio_entries.append(
            f"""### `{disp(fid)}`
- Title: {meta['title']}
- Role: {folio['manuscript_role']}
- Load: `{meta['paragraphs']}` paragraphs, `{meta['qo']}` circulation commands, `{meta['valves']}` valves, `{meta['seals']}` seals
- Key feature: `{meta['feature']}`
- Operational meaning: {cut(folio['direct_operational_meaning'], 220)}
- Local teachings:
{teach_block}
"""
        )
    master = f"""# MASTER BATH CRYSTAL

## Scope

- Corpus: `Book III - Bath / balneological`
- Authoritative outputs synthesized: `{len(folios)}`
- Canonical folio sides covered: `20`
- Source stack: `SECTION III`, `VML BALNEOLOGICAL SECTION f75r through f84v`, `VML_BALNEOLOGICAL_SECTION_COMPLETE`, `MASTER_PLANT_CRYSTAL`, `MASTER_ASTROLOGY_CRYSTAL`
- Section totals: {totals or 'totals unavailable'}

## Purpose

This file is the master analysis document for the completed bath corpus. It does five jobs at once:

1. it re-reads every Book III folio as one purification factory,
2. it compresses the full bath section into a folio-by-folio atlas,
3. it extracts the stable Bath Crystal from repeated circulation, clamp, settle, and seal behavior,
4. it maps the explicit metro and deeper emergent metro that structure Book III internally,
5. it prepares the handoff from timing into purification and from purification into formulation.

## Zero Point

Book III says raw matter and correct timing are still not enough. Material must be circulated, tested, settled, recommitted, and only then released. The bath section is the manuscript's purification law made spatial.

Stated compactly:

`Book I = what to gather.`

`Book II = when to act.`

`Book III = how to purify until the route stops changing.`

## Governing Thesis

The strongest claim supported by the local bath corpus is this:

- the pools are operational vessels, not merely decorative baths,
- the nymphs are process-state markers positioned at live nodes,
- text placement is grammar: inside-pool text is local, overhead text is global, vertical text is temporal,
- the section is governed by one fixed-point convergence law:
  circulate -> clamp -> repeat or commit -> route or seal,
- Book III is the purification bridge between the gathered plant world of Book I and the recipe world of Book V.

## Section Architecture

### Arc I - Initializer and scale bridge

- {", ".join(f'`{disp(fid)}`' for fid in phases['initializer'])}
- Establishes the universal control law, scale transitions, convergence doctrine, and endurance cycling.

### Arc II - Routing and shared infrastructure

- {", ".join(f'`{disp(fid)}`' for fid in phases['routing'])}
- Turns pool diagrams into executable plumbing, state-machine logic, and dual-batch routing.

### Arc III - Modular lattice and queen-node expansion

- {", ".join(f'`{disp(fid)}`' for fid in phases['lattice'])}
- Builds distributed subroutines, maintenance cadence, and stacked multi-module purification.

### Arc IV - Gentle entry, naming, and chromatic publication

- {", ".join(f'`{disp(fid)}`' for fid in phases['graded'])}
- Shows graded entry for sensitive material, stabilization ladders, naming only after proof, and full-spectrum pipeline publication.

### Arc V - Double-commit closure

- {", ".join(f'`{disp(fid)}`' for fid in phases['terminal'])}
- Deepens QA, expands to four-port distribution, seals covered-pool processing, and locks the section with final crystallization.

## Full Folio-By-Folio Atlas

{chr(10).join(folio_entries)}

## Bath Crystal

### Stable invariants

- `qo-` is no longer occasional: it is the dominant circulation operator of the whole section.
- `shedy` is the settle rhythm that alternates with active circulation.
- `chckhy / ckhy / kch-` are not decorative tokens; they are clamp and checkpoint logic.
- `daiin / dain / deiin` mark the moment the page is willing to commit the present state.
- `sal / sar / saiin` behave as purity evidence, especially when crystallization or salt completion becomes explicit.
- `ol` and its compounds mark fluid carriage, conduit contents, and transfer state rather than generic water.

### Section theorem

- purification is iterative,
- stability is empirical rather than assumed,
- release is conditional on convergence,
- the diagram space itself is executable.

## Cross Synthesis

### Book I -> Book III

Book I teaches substance-specific transformations. Book III strips those substances of local plant identity and subjects them to universal purification law. Matter becomes vessel-work.

### Book II -> Book III

Book II schedules the work. Book III executes the scheduled purification. The astronomical calendar becomes live plumbing.

### Book III -> Book V

Book III creates purified fractions. Book V can only exist if Book III succeeds. Formula presupposes purification.

## Metro Map

- Line A: distributed circulation -> stability doctrine -> endurance convergence
- Line B: routing controller -> full state-machine -> dual-batch shared infrastructure
- Line C: modular lattice -> maintenance log -> queen-node circulation -> stacked bathhouse
- Line D: gentle carrier -> stabilization ladder -> naming after proof -> chromatic publication
- Line E: double-commit QA -> four-port convergence -> covered pool control -> polish and lock
- Transfer hubs: `f75r`, `f76r`, `f77v`, `f79r`, `f80v`, `f82r`, `f83r`, `f84v`

## Emergent Metro Map

- Hidden line 1: the bath section turns chemistry into control theory; its real concern is convergence, not ornament.
- Hidden line 2: the body/laboratory dual reading is not optional rhetoric but the section's operating multivalence.
- Hidden line 3: Book III repeatedly teaches that naming or releasing a state before proof is bad practice.
- Hidden line 4: the section keeps widening from one bath to a whole distributed network, then narrows back into a final locked closer.
- Hidden line 5: the most important output of Book III is not just purified fluid, but repeatable purification infrastructure.

## Handoff

- backward handoff: `MASTER_ASTROLOGY_CRYSTAL.md`
- forward handoff: `BATH_CRYSTAL.md` -> future `PHARMACEUTICAL_1_CRYSTAL.md`
- manuscript role: purification infrastructure between timing and recipes
"""
    section_doc = f"""# FULL BATH

## Scope

- Section: `Book III - Bath / balneological`
- Completed outputs: `{len(folios)}`
- Canonical folio sides: `20`
- Section totals: {totals or 'totals unavailable'}

## Section Synthesis

Book III is now complete as a translated purification corpus. The section establishes the manuscript's circulation, clamp, settle, and seal infrastructure. The authoritative section-level master analysis is in `crystals/MASTER_BATH_CRYSTAL.md`.

## Folio Atlas

{atlas}
"""
    crystal_doc = f"""# BATH CRYSTAL

## Section Identity

- Book: `Book III - Bath / balneological`
- Role: `purification infrastructure of the manuscript`
- Completed outputs: `{len(folios)}`

## Crystal Summary

- initializer ring: distributed network, scale bridge, stability doctrine, endurance cycle
- routing ring: bathhouse controller, state-machine, shared infrastructure
- lattice ring: modular cells, maintenance, queen nodes, stacked modules
- closure ring: graded entry, naming, chromatic publication, double-commit, four-port distribution, final crystallization

## Metro Summary

- explicit line: circulate -> clamp -> settle -> commit -> route/seal
- emergent line: timing becomes purification infrastructure and purified fractions become future formula inputs

## Master Analysis

See `crystals/MASTER_BATH_CRYSTAL.md`.
"""
    (CRYSTALS_DIR / "MASTER_BATH_CRYSTAL.md").write_text(master, encoding="utf-8")
    (SECTIONS_DIR / "FULL_BATH.md").write_text(section_doc, encoding="utf-8")
    (CRYSTALS_DIR / "BATH_CRYSTAL.md").write_text(crystal_doc, encoding="utf-8")

    append_if_missing(
        UNIFIED_DIR / "VOYNICH_FULL_TRANSLATION.md",
        "## Book III - Bath / Balneological Parallel Completion",
        "## Book III - Bath / Balneological Parallel Completion\n\n- canonical Book III bath folios complete\n- master analysis: `crystals/MASTER_BATH_CRYSTAL.md`\n- section synthesis: `sections/FULL_BATH.md`",
    )
    append_if_missing(
        UNIFIED_DIR / "VOYNICH_MASTER_MANUSCRIPT.md",
        "## Book III Parallel Batch",
        "## Book III Parallel Batch\n\nBook III now exists as a completed parallel bath batch with full section and crystal rollups.",
    )
    append_if_missing(
        CRYSTALS_DIR / "VOYNICH_FULL_CRYSTAL.md",
        "## Book III Delta - Bath Completion",
        "## Book III Delta - Bath Completion\n\n- the full-manuscript crystal now includes the purification infrastructure\n- fixed-point convergence, bath routing, and purification QA now sit between Book II timing and Book V formula logic",
    )
    append_if_missing(
        METRO_DIR / "VOYNICH_METRO_MAP_WORKING.md",
        "## Book III Expansion Delta",
        "## Book III Expansion Delta\n\n- distributed purification network\n- fixed-point convergence law\n- bathhouse routing and state-machine logic\n- naming after proof and final crystallization",
    )

    status_path = MANIFESTS_DIR / "CORPUS_BUILD_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    status = ensure_status_row(status, "| `crystals/BATH_CRYSTAL.md` | initialized |", "| `crystals/BATH_CRYSTAL.md` | authoritative completed Book III bath crystal |")
    if "| `crystals/MASTER_BATH_CRYSTAL.md` | complete master Book III bath analysis, full Bath Crystal, metro map, and emergent metro map |" not in status:
        status = status.replace(
            "| `crystals/BATH_CRYSTAL.md` | authoritative completed Book III bath crystal |",
            "| `crystals/BATH_CRYSTAL.md` | authoritative completed Book III bath crystal |\n| `crystals/MASTER_BATH_CRYSTAL.md` | complete master Book III bath analysis, full Bath Crystal, metro map, and emergent metro map |",
        )
    status = ensure_status_row(status, "| `sections/FULL_BATH.md` | initialized |", "| `sections/FULL_BATH.md` | authoritative completed Book III bath synthesis |")
    if "| `framework/scripts/render_book3_section_parallel.py` | complete |" not in status:
        anchor = "| `framework/scripts/render_book2_section_parallel.py` | complete |"
        if anchor in status:
            status = status.replace(anchor, anchor + "\n| `framework/scripts/render_book3_section_parallel.py` | complete |")
    if "## Book III Parallel Completion" not in status:
        status += "\n\n## Book III Parallel Completion\n\n- canonical Book III bath folios rendered in parallel\n- section synthesis completed in `sections/FULL_BATH.md`\n- master bath analysis completed in `crystals/MASTER_BATH_CRYSTAL.md`\n"
    status_path.write_text(status, encoding="utf-8")


def main() -> None:
    main_text = MAIN.read_text(encoding="utf-8-sig")
    complete_text = COMPLETE.read_text(encoding="utf-8-sig")
    folio_blocks = split_folio_blocks(main_text)
    arch, totals = architecture_map(complete_text)
    teaches = teaching_map(complete_text)

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(build, fid, folio_blocks[fid], arch, teaches) for fid in TARGETS]
        folios = [future.result() for future in futures]

    order = {fid: i for i, fid in enumerate(TARGETS)}
    folios.sort(key=lambda folio: order[folio["folio_id"]])

    for folio in folios:
        (FOLIOS_DIR / f"{folio['folio_id']}_FINAL_DRAFT.md").write_text(render_folio(folio), encoding="utf-8")
        (FOLIOS_DIR / f"{folio['folio_id']}.md").write_text(render_pointer(folio), encoding="utf-8")

    write_rollups(folios, arch, teaches, totals)
    print(f"Rendered {len(folios)} Book III bath outputs in parallel.")


if __name__ == "__main__":
    main()
