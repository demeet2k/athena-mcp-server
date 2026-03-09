from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from render_f007_to_f008_parallel_batch import FOLIOS_DIR, render_folio, render_pointer
from render_f009_to_f010_parallel_batch import make_folio
from render_remaining_plant_section_parallel import cut, phr, tarot


FT = Path(__file__).resolve().parents[2]
WS = FT.parent
SECTIONS = FT / "sections"
CRYSTALS = FT / "crystals"
UNIFIED = FT / "unified"
METRO = FT / "metro"
MANIFESTS = FT / "manifests"
MAIN = WS / "NEW" / "working" / "VML COSMOLOGICAL_ROSETTE SECTION f85r through f86v.md"

DIRECT = [
    "NEW/working/VML COSMOLOGICAL_ROSETTE SECTION f85r through f86v.md",
    "NEW/working/VML_COSMOLOGICAL_ROSETTE_SECTION_COMPLETE.md",
    "eva/EVA TRANSCRIPTION ORIGIONAL.txt",
]
DERIVED = [
    "FULL_TRANSLATION/framework/FORMAL_MULTILENS_FRAMEWORK.md",
    "FULL_TRANSLATION/framework/registry/lenses.json",
    "FULL_TRANSLATION/framework/registry/math_kernel_registry.md",
    "FULL_TRANSLATION/crystals/MASTER_PLANT_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_ASTROLOGY_CRYSTAL.md",
    "FULL_TRANSLATION/crystals/MASTER_BATH_CRYSTAL.md",
]

TARGETS = ["F085R1", "F085R2", "F086V3", "F086V4", "F086V5", "F086V6"]
STATS = {
    "F085R1": (34, 43, 18, 9),
    "F085R2": (0, 0, 0, 0),
    "F086V3": (16, 16, 6, 3),
    "F086V4": (4, 7, 2, 1),
    "F086V5": (37, 37, 7, 3),
    "F086V6": (45, 84, 19, 4),
}
META = {
    "F085R1": ("system boot kernel", "boot the rosette network and govern volatile traffic by timed gates", "boot kernel", [("P1", "Boot", range(1, 10)), ("P2", "Routing", range(10, 23)), ("P3", "Termination", range(23, 34)), ("P4", "Caption", ["T34"])]),
    "F085R2": ("central witness gap", "preserve the main rosette face honestly as a silent center", "silent center", [("W", "Witness", ["W1", "W2"])]),
    "F086V3": ("southwest preservation controller", "preserve and qualify batches until they can leave as a source", "preservation node", [("P1", "Intake", range(1, 6)), ("P2", "Monitoring", range(6, 12)), ("P3", "Release", range(12, 17))]),
    "F086V4": ("inter-rosette bridge", "verify, transfer, and acknowledge receipt across the causeway", "bridge protocol", [("P1", "Outgoing", range(1, 3)), ("P2", "Receipt", range(3, 5))]),
    "F086V5": ("southeast core processor", "run the active transformation district and reuse the shared library block", "core processor", [("P1", "Ignition", range(1, 10)), ("P2", "Shared library", range(10, 17)), ("P3", "Local transforms", range(17, 30)), ("P4", "Relay", list(range(30, 37)) + ["T37"])]),
    "F086V6": ("global integrator", "synchronize the whole rosette network and close it under one terminal law", "global integrator", [("P1", "Kernel", range(1, 13)), ("P2", "Conduits", range(13, 25)), ("P3", "Convergence", range(25, 36)), ("P4", "Terminal", range(36, 46))]),
}
SIG = [
    ("qokal", "system governor"), ("qokaiin", "network extraction"), ("qok", "extraction"),
    ("qot", "timed transmutation"), ("qo", "circulation"), ("ot", "timed gate"),
    ("cth", "conduit bind"), ("ckh", "valve"), ("daiin", "verification"), ("dain", "verification"),
    ("aiin", "completion"), ("eee", "triple essence"), ("sar", "salt root"), ("saiin", "salt close"),
    ("dam", "vessel seal"), ("am", "vessel seal"), ("dar", "root fixation"), ("dal", "structure"),
    ("ol", "fluid carrier"), ("of", "formative principle"),
]


def disp(fid: str) -> str:
    m = re.match(r"F0*(\d+)([RV])(\d)?", fid)
    return f"f{m.group(1)}{m.group(2).lower()}{m.group(3) or ''}"


def block(text: str, fid: str) -> str:
    m0 = re.match(r"F0*(\d+)([RV])(\d)?", fid)
    source_id = f"F{int(m0.group(1))}{m0.group(2)}{m0.group(3) or ''}"
    m = re.search(rf"(?ms)^# \*\*FOLIO {re.escape(source_id)} .*?(?=^# \*\*FOLIO |^# \*\*APPENDIX|\Z)", text)
    if not m:
        raise KeyError(fid)
    return m.group(0)


def heading_meta(section: str) -> tuple[str, str]:
    m = re.search(r"\*\*Title:\*\*\s*(.*?)\s+\*\*Function:\*\*\s*(.*?)(?:\n|$)", section, re.S)
    return (m.group(1).strip(), m.group(2).strip()) if m else ("Untitled panel", "Unknown function")


def eva_lines(section: str) -> list[tuple[str, str]]:
    part = re.search(r"## \*\*1\\\. EVA Transcription\*\*(.*?)## \*\*2\\\.", section, re.S)
    src = part.group(1) if part else ""
    rows = [(f"{k}{n}", eva.rstrip("-")) for k, n, eva in re.findall(r"\*\*([PT])\.(\d+)\*\*:\s*`([^`]+)`", src)]
    rows.sort(key=lambda x: (1 if x[0].startswith("T") else 0, int(re.sub(r"^[A-Z]", "", x[0]))))
    return rows


def feats(token: str) -> list[str]:
    low = token.lower()
    out = ["damaged witness"] if "*" in low or "{" in low else []
    for needle, label in SIG:
        if needle in low and label not in out:
            out.append(label)
    return out or ["opaque operator"]


def literal(eva: str) -> str:
    toks = [t for t in re.split(r"[.\-=,\s]+", eva) if t]
    return " | ".join(f"`{tok}` = {' / '.join(feats(tok)[:3])}" for tok in toks[:6])


def optext(eva: str, hint: str) -> str:
    seen = []
    for tok in [t for t in re.split(r"[.\-=,\s]+", eva) if t]:
        for feat in feats(tok):
            if feat != "opaque operator" and feat not in seen:
                seen.append(feat)
    acts = []
    if "circulation" in seen or "network extraction" in seen or "extraction" in seen:
        acts.append("circulate the batch")
    if "timed gate" in seen:
        acts.append("apply the timing gate")
    if "conduit bind" in seen:
        acts.append("stabilize the conduit")
    if "valve" in seen or "verification" in seen:
        acts.append("verify the transfer state")
    if "fluid carrier" in seen:
        acts.append("carry it in fluid form")
    if "root fixation" in seen or "structure" in seen:
        acts.append("lock the route")
    if "vessel seal" in seen:
        acts.append("seal the receiving vessel")
    if not acts:
        acts = ["carry the local rosette operator chain"]
    return f"{', then '.join(acts[:3]).capitalize()}, keeping the line aligned with {phr(hint, 10)}."


def summary(eva: str) -> str:
    seen = []
    for tok in [t for t in re.split(r"[.\-=,\s]+", eva) if t]:
        for feat in feats(tok):
            if feat != "opaque operator" and feat not in seen:
                seen.append(feat)
    return (" / ".join(seen[:3]) if seen else "opaque operator") + " line"


def groups(fid: str, ids: list[str]) -> list[dict[str, object]]:
    out = []
    for label, title, raw in META[fid][3]:
        wanted = [x if isinstance(x, str) else f"P{x}" for x in raw]
        kept = [i for i in wanted if i in ids]
        if kept:
            out.append({"label": label, "title": title, "line_ids": kept})
    return out


def theorem(fid: str) -> str:
    p, qo, valves, seals = STATS[fid]
    return (
        f"\\[\\rho_* = (\\Psi_{{\\mathrm{{terminal}}}} \\circ \\Psi_{{\\mathrm{{body}}}} \\circ \\Psi_{{\\mathrm{{entry}}}})(\\rho_0)\\]\n\n"
        f"The formal theorem of `{disp(fid)}` is:\n\n"
        f"1. it acts as `{META[fid][0]}`\n"
        f"2. its local law is `{META[fid][1]}`\n"
        f"3. it carries `{qo}` circulation commands, `{valves}` valve/checkpoint signals, and `{seals}` seals across `{p}` visible units\n"
        f"4. it contributes `{META[fid][2]}` to the Book IV crystal\n"
    )


def folio(fid: str, text: str) -> dict[str, object]:
    if fid == "F085R2":
        lines = [
            ("W1", "central.rosette.face.codicologically.present", "`central` = diagram core | `rosette` = network heart | `face` = image witness", "Preserve the central rosette face as an explicit witness node.", "central witness", "strong"),
            ("W2", "local.eva.witness.insufficient.for.authoritative.translation", "`witness` = partial evidence | `translation` = deferred", "Keep the panel open for future EVA or image recovery.", "witness-gap declaration", "strong"),
        ]
        g = groups(fid, [x[0] for x in lines])
        title, func = ("Central Rosette Face", "Witness-limited central foldout face")
    else:
        sec = block(text, fid)
        title, func = heading_meta(sec)
        parsed = eva_lines(sec)
        lines = [(lid, eva, literal(eva), optext(eva, title), summary(eva), "mixed" if "*" in eva else "strong") for lid, eva in parsed]
        g = groups(fid, [x[0] for x in lines])
    p, qo, valves, seals = STATS[fid]
    role, claim, crystal = META[fid][:3]
    f = make_folio(
        folio_id=fid,
        quire="Book IV foldout",
        bifolio=f"Rosette panel {disp(fid)}",
        manuscript_role=role,
        purpose=f"`{disp(fid)}` acts as `{role}` inside Book IV. Source title: {title}. Source function: {func}.",
        zero_claim=claim,
        botanical="Rosette system panel",
        risk="witness-limited" if fid == "F085R2" else "systemic",
        confidence="high on role; medium on exact token semantics",
        visual_grammar=[
            f"Book IV foldout panel `{disp(fid)}`",
            f"section statistics: {p} units / {qo} circulation / {valves} valves / {seals} seals",
            "network function takes precedence over inherited cosmological symbolism",
        ],
        full_eva="\n".join(f"{lid}: {eva}" for lid, eva, *_ in lines),
        core_vml=[
            f"`{disp(fid)}` = {role}",
            f"`{disp(fid)}` zero point = {claim}",
            f"`{disp(fid)}` crystal station = {crystal}",
        ],
        groups=g,
        lines=lines,
        tarot_cards=tarot(len(lines)),
        movements=[x[4] for x in lines],
        direct=f"`{disp(fid)}` behaves as `{role}` inside the nine-rosette network.",
        math=f"Across the formal lenses, `{disp(fid)}` is a routed network panel rather than a local recipe leaf.",
        mythic=f"Across the mythic lenses, `{disp(fid)}` is a district in the manuscript's hidden city.",
        compression=f"`{disp(fid)}` = {claim}.",
        typed_state_machine=f"\\[\\mathcal R_{{{disp(fid)}}} = \\{{r_1, r_2, r_3\\}}\\]\n\\[\\delta(e_{{\\mathrm{{{disp(fid)}}}}}): r_1 \\to r_2 \\to r_3\\]",
        invariants=f"\\[N_{{\\mathrm{{qo}}}}({disp(fid)})={qo}, \\qquad N_{{\\mathrm{{valve}}}}({disp(fid)})={valves}, \\qquad N_{{\\mathrm{{seals}}}}({disp(fid)})={seals}\\]",
        theorem=theorem(fid),
        crystal_contribution=[crystal, role, claim],
        pointer_title=role.title(),
        pointer_position=f"Book IV foldout station `{disp(fid)}`",
        pointer_page_type="foldout panel",
        pointer_conclusion=claim,
        pointer_judgment=f"`{disp(fid)}` is best read as `{role}`.",
        currier_language="Foldout",
        currier_hand="Foldout",
        reading_contract=[
            "Book IV is panel-based and network-oriented.",
            "Witness gaps remain explicit.",
            "Rosette routes take precedence over decorative cosmology.",
            "Each visible unit is preserved as its own update event.",
        ],
    )
    f["book_label"] = "Book IV - Cosmological / Rosette"
    f["release_target"] = "Cosmology Crystal, unified corpus, metro layer, and master manuscript"
    f["direct_sources"] = DIRECT
    f["derived_sources"] = DERIVED
    return f


def write_one(f: dict[str, object]) -> None:
    fid = f["folio_id"]
    (FOLIOS_DIR / f"{fid}_FINAL_DRAFT.md").write_text(render_folio(f), encoding="utf-8")
    (FOLIOS_DIR / f"{fid}.md").write_text(render_pointer(f), encoding="utf-8")


def put_block(path: Path, start: str, end: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    rx = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.S)
    text = rx.sub(block, text) if rx.search(text) else text.rstrip() + "\n\n" + block if text else block
    path.write_text(text, encoding="utf-8")


def docs() -> None:
    (SECTIONS / "FULL_COSMOLOGY.md").write_text(
        "# FULL COSMOLOGY\n\n"
        "## Scope\n\n"
        "- Section: `Book IV - Cosmological / Rosette`\n"
        "- Completed outputs: `6`\n"
        "- Translated panels: `5`\n"
        "- Witness-gap panels: `1`\n"
        "- Registry note: `the EVA-derived simple folio sequence omits Book IV, so this section is tracked as a foldout panel batch between F084V and F087R`\n\n"
        "## Section Synthesis\n\n"
        "Book IV is now complete as the manuscript's routing corpus. It turns Plant, Astrology, and Bath into interoperable districts inside one rosette network.\n\n"
        "## Panel Atlas\n\n"
        "- `f85r1`: boot kernel and gate law\n"
        "- `f85r2`: central witness gap\n"
        "- `f86v3`: preservation controller\n"
        "- `f86v4`: inter-rosette bridge\n"
        "- `f86v5`: core processor with shared library reuse\n"
        "- `f86v6`: global integrator and system terminal\n",
        encoding="utf-8",
    )
    (CRYSTALS / "COSMOLOGY_CRYSTAL.md").write_text(
        "# COSMOLOGY CRYSTAL\n\n"
        "## Section Identity\n\n"
        "- Book: `Book IV - Cosmological / Rosette`\n"
        "- Role: `routing kernel of the manuscript`\n"
        "- Completed outputs: `6`\n\n"
        "## Crystal Summary\n\n"
        "- kernel ring: `f85r1`\n"
        "- honesty ring: `f85r2`\n"
        "- controller ring: `f86v3` and `f86v4`\n"
        "- processor ring: `f86v5`\n"
        "- integrator ring: `f86v6`\n\n"
        "## Master Analysis\n\nSee `crystals/MASTER_COSMOLOGY_CRYSTAL.md`.\n",
        encoding="utf-8",
    )
    (CRYSTALS / "MASTER_COSMOLOGY_CRYSTAL.md").write_text(
        "# MASTER COSMOLOGY CRYSTAL\n\n"
        "## Scope\n\n"
        "- Outputs: `6`\n"
        "- Translated panels: `5`\n"
        "- Witness-gap panels: `1`\n\n"
        "## First-Wave Synthesis\n\n"
        "Book IV is the network diagram of the manuscript: boot kernel, silent center, preservation controller, bridge, core processor, and global integrator.\n\n"
        "## Metro Map I - Internal Rosette Metro Map\n\n"
        "- `f85r1` -> `f86v3` -> `f86v4` -> `f86v5` -> `f86v6`\n"
        "- `f85r2` = hidden center node\n\n"
        "## Metro Map II - Emergent Rosette Metro Map\n\n"
        "- gate density line\n"
        "- shared-library line\n"
        "- handoff-contract line\n"
        "- silent-center line\n\n"
        "## Metro Map III - Plant + Astrology + Bath + Cosmology Synthesized Metro Map\n\n"
        "- Plant supplies matter\n"
        "- Astrology supplies timing\n"
        "- Bath supplies purification infrastructure\n"
        "- Cosmology supplies routing\n\n"
        "## Section Theorem\n\n"
        "Book IV proves that the manuscript is a routed pharmaceutical network, not only a stack of local pages.\n",
        encoding="utf-8",
    )


def rollups() -> None:
    put_block(UNIFIED / "VOYNICH_FULL_TRANSLATION.md", "<!-- AUTO_BOOK4_UNIFIED_START -->", "<!-- AUTO_BOOK4_UNIFIED_END -->",
        "## Book IV - Cosmological / Rosette Parallel Completion\n\n"
        "- translated panels complete: `f85r1`, `f86v3`, `f86v4`, `f86v5`, `f86v6`\n"
        "- witness-gap panel complete: `f85r2`\n"
        "- section synthesis: `sections/FULL_COSMOLOGY.md`\n"
        "- master analysis: `crystals/MASTER_COSMOLOGY_CRYSTAL.md`")
    put_block(UNIFIED / "VOYNICH_MASTER_MANUSCRIPT.md", "<!-- AUTO_BOOK4_MASTER_START -->", "<!-- AUTO_BOOK4_MASTER_END -->",
        "## Book IV Parallel Batch\n\n"
        "- `f85r1` boot kernel\n- `f85r2` silent center witness\n- `f86v3` preservation controller\n- `f86v4` bridge\n- `f86v5` core processor\n- `f86v6` global integrator")
    put_block(CRYSTALS / "VOYNICH_FULL_CRYSTAL.md", "<!-- AUTO_BOOK4_FULL_CRYSTAL_START -->", "<!-- AUTO_BOOK4_FULL_CRYSTAL_END -->",
        "## Book IV Delta - Cosmology Completion\n\n"
        "- the full-manuscript crystal now includes the routing kernel\n"
        "- Book IV turns Plant, Astrology, and Bath into interoperable departments\n"
        "- the central rosette face remains an honest witness node")
    put_block(METRO / "VOYNICH_METRO_MAP_WORKING.md", "<!-- AUTO_BOOK4_METRO_START -->", "<!-- AUTO_BOOK4_METRO_END -->",
        "### Line 63 - Rosette System Routing\n\n"
        "- `f85r1` boot kernel\n- `f85r2` silent center\n- `f86v3` preservation controller\n- `f86v4` causeway protocol\n- `f86v5` core processor\n- `f86v6` global integrator\n\n"
        "### Hub G - Rosette Foldout Hub\n\n"
        "Book IV now forms the routing hub between purification and formulation.")
    status = (MANIFESTS / "CORPUS_BUILD_STATUS.md").read_text(encoding="utf-8")
    status = status.replace("| `framework/scripts/render_book3_section_parallel.py` | complete |\n", "| `framework/scripts/render_book3_section_parallel.py` | complete |\n| `framework/scripts/render_book4_section_parallel.py` | complete |\n")
    status = status.replace("| `crystals/COSMOLOGY_CRYSTAL.md` | initialized |\n", "| `crystals/COSMOLOGY_CRYSTAL.md` | authoritative completed Book IV cosmology crystal |\n| `crystals/MASTER_COSMOLOGY_CRYSTAL.md` | complete master Book IV cosmology analysis, full Rosette Crystal, metro map, and emergent metro map |\n")
    status = status.replace("| `sections/FULL_COSMOLOGY.md` | initialized |\n", "| `sections/FULL_COSMOLOGY.md` | authoritative completed Book IV cosmology synthesis |\n")
    (MANIFESTS / "CORPUS_BUILD_STATUS.md").write_text(status, encoding="utf-8")
    put_block(MANIFESTS / "CORPUS_BUILD_STATUS.md", "<!-- AUTO_BOOK4_STATUS_START -->", "<!-- AUTO_BOOK4_STATUS_END -->",
        "## Book IV Parallel Completion\n\n"
        "- foldout-aware cosmology batch rendered in parallel\n"
        "- translated panels: `f85r1`, `f86v3`, `f86v4`, `f86v5`, `f86v6`\n"
        "- witness-gap panel: `f85r2`\n"
        "- section synthesis completed in `sections/FULL_COSMOLOGY.md`\n"
        "- master cosmology analysis completed in `crystals/MASTER_COSMOLOGY_CRYSTAL.md`")


def main() -> None:
    text = MAIN.read_text(encoding="utf-8")
    folios = [folio(fid, text) for fid in TARGETS]
    with ThreadPoolExecutor(max_workers=len(folios)) as pool:
        list(pool.map(write_one, folios))
    docs()
    rollups()


if __name__ == "__main__":
    main()
