#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import math
import re
import zipfile
import hashlib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PureWindowsPath
from typing import Iterable
from xml.etree import ElementTree

from nervous_system_core import (
    APPENDICES,
    CHAPTERS,
    clean_display_name,
    infer_appendix_links,
    infer_chapter_links,
    infer_family,
    normalize_lookup_text,
    presentation_name,
)

PROFILE_VERSION = "mycelium-metro-v4.3"

ALLOWED_SOURCE_EXTENSIONS = {".md", ".docx", ".pdf", ".txt", ".html", ".zip"}
DERIVATIVE_DENYLIST = (
    "_build/",
    "DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/",
    "Trading Bot/MANUSCRIPT_ELEMENTAL_NET_4X4/",
    "Athena FLEET/FLEET_MYCELIUM_NETWORK/CAPSULES/",
    "Athena FLEET/FLEET_MYCELIUM_NETWORK/MIRRORS/",
    "NERVOUS_SYSTEM/50_CORPUS_CAPSULES/",
    "QSHRINK - ATHENA (internal use)/05_MANUSCRIPT_SPACE/root_cells/",
    "QSHRINK - ATHENA (internal use)/09_REPAIR_256X256/steps/",
    "QSHRINK - ATHENA (internal use)/10_CH11_256X256/cells/",
)

LENS_BASE = {"S": "AppC", "F": "AppE", "C": "AppI", "R": "AppM"}
FACET_BASE = {"1": "AppA", "2": "AppB", "3": "AppH", "4": "AppM"}
ARC_HUB = {0: "AppA", 1: "AppC", 2: "AppE", 3: "AppF", 4: "AppG", 5: "AppN", 6: "AppP"}
MANDATORY_SIGNATURE = ("AppA", "AppI", "AppM")
TRUTH_OVERLAY = {"NEAR": "AppJ", "AMBIG": "AppL", "FAIL": "AppK"}
HCRL_ORDER = ("S", "F", "C", "R")

LENS_LABELS = {"S": "Square", "F": "Flower", "C": "Cloud", "R": "Fractal"}
FACET_LABELS = {"1": "Objects", "2": "Laws", "3": "Constructions", "4": "Certificates"}

LENS_KEYWORDS = {
    "S": ("address", "grid", "index", "object", "registry", "kernel", "lattice", "station"),
    "F": ("phase", "orbit", "rotation", "transform", "cycle", "symmetry", "wave", "gear"),
    "C": ("truth", "corridor", "candidate", "ambigu", "uncertain", "evidence", "admiss", "cloud"),
    "R": ("replay", "recur", "fractal", "seed", "compress", "regener", "memory", "self-similar"),
}

FACET_KEYWORDS = {
    "1": ("object", "entity", "node", "document", "manuscript", "atom", "record", "shell"),
    "2": ("law", "axiom", "rule", "invariant", "equivalence", "contract", "discipline", "theorem"),
    "3": ("build", "construct", "compose", "route", "synthes", "implementation", "transport", "assembly"),
    "4": ("proof", "verify", "witness", "certificate", "receipt", "test", "closure", "replay"),
}

ZIP_PREFERRED_EXTENSIONS = (".md", ".txt", ".html", ".docx", ".pdf")


@dataclass(frozen=True)
class SelectedRecord:
    record_id: str
    relative_path: str
    absolute_path: str
    extension: str
    sha256: str
    title: str
    excerpt: str
    headings: tuple[str, ...]
    role_tags: tuple[str, ...]


@dataclass(frozen=True)
class ExcludedRecord:
    relative_path: str
    reason: str


@dataclass
class SourceEnvelope:
    source_sha256: str
    title: str
    full_text: str
    headings: list[str]
    read_mode: str
    truth_state: str
    notes: list[str] = field(default_factory=list)
    chosen_archive_member: str | None = None
    archive_candidates: list[dict[str, object]] = field(default_factory=list)


@dataclass
class RoutePlan:
    tesseract_header: str
    hubs_seq: list[str]
    tunnel_plan: dict[str, object]
    truth_intent: str
    hcrl_pass: dict[str, object]
    obligations: list[str]
    header: str
    primary_hubs: list[str]
    tunnel: str
    truth_state: str
    dominant_view: str
    drop_log: list[str]


@dataclass
class RewriteArtifact:
    ms_code: str
    record: SelectedRecord
    docs_gate_status: str
    duplicate_group: str | None
    source: SourceEnvelope
    family: str
    z_point: str
    home_chapter: dict
    secondary_chapters: list[dict]
    appendices: list[dict]
    dominant_lens: str
    dominant_facet: str
    route_plan: RoutePlan
    hcrl: dict[str, list[str]]
    crystal_tile: list[dict[str, object]]


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return "\n".join(self.parts)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_relative_path(raw_path: str) -> str:
    return PureWindowsPath(raw_path).as_posix()


def _base4(value: int, width: int) -> str:
    digits = "0123"
    if value == 0:
        return "0" * width
    parts: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, 4)
        parts.append(digits[remainder])
    return "".join(reversed(parts)).rjust(width, "0")


def _derive_title(record: dict) -> str:
    headings = record.get("heading_candidates") or []
    if headings:
        return presentation_name(headings[0])
    return presentation_name(Path(record["relative_path"]).name)


def chapter_station_label(chapter) -> str:
    return f"{chapter.code}<{chapter.station}>"


def load_atlas(atlas_path: Path) -> dict:
    return json.loads(atlas_path.read_text(encoding="utf-8"))


def select_source_records(
    atlas_path: Path,
    path_prefix: str | None = None,
    limit: int | None = None,
) -> tuple[list[SelectedRecord], list[ExcludedRecord]]:
    atlas = load_atlas(atlas_path)
    selected: list[SelectedRecord] = []
    excluded: list[ExcludedRecord] = []
    normalized_prefix = normalize_relative_path(path_prefix).rstrip("/") if path_prefix else None

    for record in atlas["records"]:
        relative_path = normalize_relative_path(record["relative_path"])
        extension = Path(relative_path).suffix.lower()
        role_tags = tuple(record.get("role_tags") or ())

        if "manuscript" not in role_tags:
            excluded.append(ExcludedRecord(relative_path=relative_path, reason="missing-manuscript-tag"))
            continue
        if extension not in ALLOWED_SOURCE_EXTENSIONS:
            excluded.append(ExcludedRecord(relative_path=relative_path, reason="unsupported-extension"))
            continue
        if relative_path.lower().endswith(".4d.md"):
            excluded.append(ExcludedRecord(relative_path=relative_path, reason="existing-4d-derivative"))
            continue
        if any(relative_path.startswith(prefix) for prefix in DERIVATIVE_DENYLIST):
            excluded.append(ExcludedRecord(relative_path=relative_path, reason="denylisted-derivative-tree"))
            continue
        if normalized_prefix and not relative_path.startswith(normalized_prefix):
            excluded.append(ExcludedRecord(relative_path=relative_path, reason="path-prefix-filter"))
            continue

        selected.append(
            SelectedRecord(
                record_id=record["record_id"],
                relative_path=relative_path,
                absolute_path=record["path"],
                extension=extension,
                sha256=record["sha256"],
                title=_derive_title(record),
                excerpt=record.get("excerpt", ""),
                headings=tuple(record.get("heading_candidates") or ()),
                role_tags=role_tags,
            )
        )

    selected.sort(key=lambda item: item.relative_path.lower())
    if limit is not None:
        selected = selected[:limit]
    return selected, excluded


def assign_ms_codes(records: list[SelectedRecord]) -> dict[str, str]:
    if not records:
        return {}
    width = max(5, math.ceil(math.log(len(records), 4)) if len(records) > 1 else 1)
    return {
        record.relative_path: f"Ms<{_base4(index, width)}>"
        for index, record in enumerate(records)
    }


def build_duplicate_groups(
    records: list[SelectedRecord],
    sha_by_path: dict[str, str] | None = None,
) -> tuple[dict[str, str | None], list[dict[str, object]]]:
    by_sha: dict[str, list[SelectedRecord]] = defaultdict(list)
    for record in records:
        by_sha[(sha_by_path or {}).get(record.relative_path, record.sha256)].append(record)

    path_to_group: dict[str, str | None] = {}
    manifest_groups: list[dict[str, object]] = []
    for group_index, (sha256, group_records) in enumerate(sorted(by_sha.items()), start=1):
        if len(group_records) < 2:
            path_to_group[group_records[0].relative_path] = None
            continue
        group_id = f"DG{group_index:04d}"
        members = sorted(record.relative_path for record in group_records)
        for member in members:
            path_to_group[member] = group_id
        manifest_groups.append({"group_id": group_id, "sha256": sha256, "members": members})
    return path_to_group, manifest_groups


def docs_gate_status(gate_path: Path) -> str:
    if not gate_path.exists():
        return "UNKNOWN"
    text = gate_path.read_text(encoding="utf-8")
    if "BLOCKED" in text:
        return "BLOCKED"
    if "PASS" in text:
        return "PASS"
    return "UNKNOWN"


def sha256_for_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_sha256(record: SelectedRecord) -> str:
    path = Path(record.absolute_path)
    if not path.exists():
        return record.sha256
    return sha256_for_path(path)


def _normalize_block(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _heading_candidates(text: str, fallback: Iterable[str]) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
            continue
        if len(stripped) < 120 and stripped == stripped.title():
            headings.append(stripped)
    for candidate in fallback:
        if candidate and candidate not in headings:
            headings.append(candidate)
    return headings[:12]


def _read_text_path(path: Path) -> str:
    return _normalize_block(path.read_text(encoding="utf-8", errors="ignore"))


def _strip_html(raw_html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(raw_html)
    return _normalize_block(parser.text())


def _extract_docx_bytes(raw_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml_bytes)
    paragraphs: list[str] = []
    current: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t"):
            current.append(node.text or "")
        elif node.tag.endswith("}p"):
            text = "".join(current).strip()
            if text:
                paragraphs.append(text)
            current = []
    trailing = "".join(current).strip()
    if trailing:
        paragraphs.append(trailing)
    return _normalize_block("\n".join(paragraphs))


def _read_docx_path(path: Path) -> str:
    return _extract_docx_bytes(path.read_bytes())


def _read_pdf_path(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - exercised indirectly in tests
        raise RuntimeError("pypdf is required for PDF extraction") from exc

    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted.strip():
            chunks.append(extracted)
    return _normalize_block("\n\n".join(chunks))


def _extract_pdf_bytes(raw_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - exercised indirectly in tests
        raise RuntimeError("pypdf is required for PDF extraction") from exc

    reader = PdfReader(io.BytesIO(raw_bytes))
    chunks: list[str] = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted.strip():
            chunks.append(extracted)
    return _normalize_block("\n\n".join(chunks))


def _load_archive_member(archive: zipfile.ZipFile, member_name: str, extension: str) -> str:
    raw_bytes = archive.read(member_name)
    if extension in {".md", ".txt"}:
        return _normalize_block(raw_bytes.decode("utf-8", errors="ignore"))
    if extension == ".html":
        return _strip_html(raw_bytes.decode("utf-8", errors="ignore"))
    if extension == ".docx":
        return _extract_docx_bytes(raw_bytes)
    if extension == ".pdf":
        return _extract_pdf_bytes(raw_bytes)
    raise RuntimeError(f"Unsupported archive member type: {extension}")


def _archive_member_rank(member_name: str) -> tuple[int, str]:
    extension = Path(member_name).suffix.lower()
    try:
        extension_rank = ZIP_PREFERRED_EXTENSIONS.index(extension)
    except ValueError:
        extension_rank = len(ZIP_PREFERRED_EXTENSIONS)
    return extension_rank, member_name.lower()


def _hash_bytes(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def archive_candidate_summaries(path: Path) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            extension = Path(info.filename).suffix.lower()
            if extension not in ZIP_PREFERRED_EXTENSIONS:
                continue
            rank = _archive_member_rank(info.filename)
            candidates.append(
                {
                    "member_path": info.filename,
                    "extension": extension,
                    "read_mode": extension.lstrip("."),
                    "member_size_bytes": info.file_size,
                    "preference_rank": rank[0],
                }
            )
    candidates.sort(key=lambda item: (item["preference_rank"], -int(item["member_size_bytes"]), str(item["member_path"]).lower()))
    return candidates


def read_source(record: SelectedRecord) -> SourceEnvelope:
    path = Path(record.absolute_path)
    source_sha256 = current_sha256(record)
    headings = list(record.headings)
    notes: list[str] = []
    read_mode = record.extension.lstrip(".")
    truth_state = "NEAR"
    chosen_archive_member: str | None = None
    archive_candidates: list[dict[str, object]] = []

    try:
        if record.extension in {".md", ".txt"}:
            full_text = _read_text_path(path)
        elif record.extension == ".html":
            full_text = _strip_html(path.read_text(encoding="utf-8", errors="ignore"))
        elif record.extension == ".docx":
            full_text = _read_docx_path(path)
        elif record.extension == ".pdf":
            full_text = _read_pdf_path(path)
        elif record.extension == ".zip":
            read_mode = "zip"
            full_text, headings, truth_state, notes, chosen_archive_member, archive_candidates = _read_zip_source(path, headings)
        else:
            raise RuntimeError(f"Unsupported extension: {record.extension}")
    except Exception as exc:  # pragma: no cover - exercised by tests through failure cases
        full_text = ""
        truth_state = "FAIL"
        notes.append(f"read-error:{type(exc).__name__}:{exc}")

    if record.excerpt and record.excerpt not in full_text:
        full_text = _normalize_block(f"{record.excerpt}\n\n{full_text}" if full_text else record.excerpt)

    headings = _heading_candidates(full_text, [record.title, *headings])
    if not full_text.strip():
        truth_state = "FAIL"
        notes.append("empty-text")

    return SourceEnvelope(
        source_sha256=source_sha256,
        title=record.title,
        full_text=full_text,
        headings=headings,
        read_mode=read_mode,
        truth_state=truth_state,
        notes=notes,
        chosen_archive_member=chosen_archive_member,
        archive_candidates=archive_candidates,
    )


def _read_zip_source(
    path: Path,
    fallback_headings: list[str],
) -> tuple[str, list[str], str, list[str], str | None, list[dict[str, object]]]:
    notes: list[str] = []
    candidates = archive_candidate_summaries(path)
    if not candidates:
        return "", fallback_headings, "FAIL", ["zip:no-readable-manuscript-member"], None, []

    chosen = candidates[0]
    chosen_name = str(chosen["member_path"])
    chosen_extension = str(chosen["extension"])
    ambiguity_count = sum(1 for item in candidates if item["preference_rank"] == chosen["preference_rank"])
    truth_state = "AMBIG" if ambiguity_count > 1 else "NEAR"
    if ambiguity_count > 1:
        notes.append(f"zip:multiple-plausible-members:{ambiguity_count}")

    with zipfile.ZipFile(path) as archive:
        full_text = _load_archive_member(archive, chosen_name, chosen_extension)

    headings = _heading_candidates(full_text, [Path(chosen_name).stem, *fallback_headings])
    return full_text, headings, truth_state, notes, chosen_name, candidates


def read_archive_members(record: SelectedRecord) -> list[dict[str, object]]:
    path = Path(record.absolute_path)
    members: list[dict[str, object]] = []
    for candidate in archive_candidate_summaries(path):
        member_name = str(candidate["member_path"])
        extension = str(candidate["extension"])
        member_notes: list[str] = []
        with zipfile.ZipFile(path) as archive:
            raw_bytes = archive.read(member_name)
            member_sha256 = _hash_bytes(raw_bytes)
            try:
                full_text = _load_archive_member(archive, member_name, extension)
                truth_state = "NEAR" if full_text.strip() else "FAIL"
            except Exception as exc:
                full_text = ""
                truth_state = "FAIL"
                member_notes.append(f"read-error:{type(exc).__name__}:{exc}")

        headings = _heading_candidates(full_text, [presentation_name(Path(member_name).name), *record.headings])
        source = SourceEnvelope(
            source_sha256=member_sha256,
            title=presentation_name(Path(member_name).name),
            full_text=full_text,
            headings=headings,
            read_mode=str(candidate["read_mode"]),
            truth_state=truth_state,
            notes=member_notes,
            chosen_archive_member=member_name,
            archive_candidates=[dict(candidate)],
        )
        members.append(
            {
                "member_path": member_name,
                "member_sha256": member_sha256,
                "member_size_bytes": int(candidate["member_size_bytes"]),
                "read_mode": candidate["read_mode"],
                "extension": extension,
                "source": source,
            }
        )
    return members


def _weighted_counter(source: SourceEnvelope, record: SelectedRecord) -> Counter[str]:
    counter: Counter[str] = Counter()
    weighted_fields = (
        (record.title, 8),
        (" ".join(source.headings[:6]), 5),
        (record.excerpt, 3),
        (source.full_text[:24000], 1),
    )
    for text, weight in weighted_fields:
        for token in normalize_lookup_text(text).split():
            if len(token) >= 3:
                counter[token] += weight
    return counter


def _chapter_lookup() -> dict[str, object]:
    return {chapter.code: chapter for chapter in CHAPTERS}


def _appendix_lookup() -> dict[str, tuple[str, str, str]]:
    return {code: (code, title, description) for code, title, description in APPENDICES}


def _chapter_score(counter: Counter[str], chapter, seeded_codes: set[str], family: str) -> int:
    score = 0
    title_tokens = normalize_lookup_text(chapter.title).split()
    role_tokens = normalize_lookup_text(chapter.role).split()
    for token in title_tokens:
        score += counter[token] * 4
    for token in role_tokens:
        score += counter[token] * 2
    for token in chapter.lane.lower(), chapter.code.lower(), family.replace("-", " "):
        for subtoken in normalize_lookup_text(token).split():
            score += counter[subtoken]
    for hub in chapter.hubs:
        score += counter[hub.lower()] * 2
    if chapter.code in seeded_codes:
        score += 150
    if family in chapter.families:
        score += 50
    score += 21 - chapter.index
    return score


def _appendix_score(counter: Counter[str], appendix: tuple[str, str, str], seeded_codes: set[str]) -> int:
    code, title, description = appendix
    score = 0
    for token in normalize_lookup_text(title).split():
        score += counter[token] * 4
    for token in normalize_lookup_text(description).split():
        score += counter[token] * 2
    if code in seeded_codes:
        score += 90
    score += 16 - (ord(code[-1]) - ord("A") + 1)
    return score


def _score_dimension(counter: Counter[str], keywords: dict[str, tuple[str, ...]]) -> str:
    scores: dict[str, int] = {}
    for key, terms in keywords.items():
        scores[key] = sum(counter[term] for term in terms)
    return max(scores.items(), key=lambda item: (item[1], -ord(item[0][0])))[0]


def _derive_z_point(title: str, headings: list[str]) -> str:
    weighted: Counter[str] = Counter()
    candidates = [title, *headings[:8]]
    for index, candidate in enumerate(candidates):
        normalized = normalize_lookup_text(candidate)
        if not normalized:
            continue
        weighted[normalized] += max(1, 6 - index)
    if not weighted:
        return "Z_source_seed"
    cluster = max(weighted.items(), key=lambda item: (item[1], -len(item[0]), item[0]))[0]
    slug = re.sub(r"\s+", "_", cluster).strip("_")[:48]
    return f"Z_{slug or 'source_seed'}"


def _route_header(home_chapter, lane: str, dominant_view: str) -> str:
    return (
        f"**[Z_i <-> Z* | Arc {home_chapter.arc} | Rot {home_chapter.rot} | "
        f"Lane {lane} | View * | omega={home_chapter.omega}]**"
    )


def build_route_plan(home_chapter, dominant_lens: str, dominant_facet: str, truth_state: str, z_point: str) -> RoutePlan:
    overlay_hub = TRUTH_OVERLAY.get(truth_state)
    candidates = [
        "AppA",
        ARC_HUB[home_chapter.arc],
        LENS_BASE[dominant_lens],
        FACET_BASE[dominant_facet],
        overlay_hub,
        "AppI",
        "AppM",
    ]
    unique_hubs: list[str] = []
    for hub in candidates:
        if hub is None:
            continue
        if hub not in unique_hubs:
            unique_hubs.append(hub)

    drop_log: list[str] = []
    facet_hub = FACET_BASE[dominant_facet]
    lens_hub = LENS_BASE[dominant_lens]
    arc_hub = ARC_HUB[home_chapter.arc]

    while len(unique_hubs) > 6:
        if facet_hub in unique_hubs and facet_hub not in MANDATORY_SIGNATURE and facet_hub != overlay_hub:
            unique_hubs.remove(facet_hub)
            drop_log.append(f"dropped facet hub {facet_hub} to honor cap")
            continue
        if lens_hub in unique_hubs and lens_hub not in MANDATORY_SIGNATURE and lens_hub != overlay_hub:
            unique_hubs.remove(lens_hub)
            drop_log.append(f"dropped lens hub {lens_hub} to honor cap")
            continue
        if arc_hub in unique_hubs and arc_hub not in MANDATORY_SIGNATURE and arc_hub != overlay_hub:
            unique_hubs.remove(arc_hub)
            drop_log.append(f"dropped arc hub {arc_hub} to honor cap")
            continue
        break

    primary_hubs = []
    canonical_order = ["AppA", arc_hub, lens_hub, facet_hub, overlay_hub, "AppI", "AppM"]
    for hub in canonical_order:
        if hub is None:
            continue
        if hub in unique_hubs and hub not in primary_hubs:
            primary_hubs.append(hub)

    header = _route_header(home_chapter, home_chapter.lane, dominant_lens)
    tunnel = f"{z_point} -> Z* -> {chapter_station_label(home_chapter)}"
    tunnel_plan = {
        "via": "Z*",
        "mode": "BRIDGE",
        "from_z": z_point,
        "to_z": f"Z_{home_chapter.code.lower()}",
        "zoom": "chapter-home",
        "checkpoint": home_chapter.code,
        "invariants": [
            "local_addr",
            "truth_state",
            "mandatory_signature",
            "replay_path",
        ],
    }
    hcrl_pass = {
        "Square": f"home {home_chapter.code} with dominant facet {dominant_facet}",
        "Flower": f"arc {home_chapter.arc} rotation {home_chapter.rot} lane {home_chapter.lane}",
        "Cloud": f"truth corridor {truth_state}",
        "Fractal": f"replay from {z_point} through {home_chapter.code}",
        "Order": list(HCRL_ORDER),
        "Omitted": [],
    }
    obligations = [
        "verify source hash before promotion",
        "preserve docs gate status in output",
        "retain replay pointer to source path",
    ]
    if truth_state == "NEAR":
        obligations.append("record residual ledger before upgrading to OK")
    elif truth_state == "AMBIG":
        obligations.append("attach evidence plan before collapsing ambiguity")
    elif truth_state == "FAIL":
        obligations.append("quarantine route and emit conflict receipt")

    return RoutePlan(
        tesseract_header=header,
        hubs_seq=primary_hubs,
        tunnel_plan=tunnel_plan,
        truth_intent="VERIFY",
        hcrl_pass=hcrl_pass,
        obligations=obligations,
        header=header,
        primary_hubs=primary_hubs,
        tunnel=tunnel,
        truth_state=truth_state,
        dominant_view=dominant_lens,
        drop_log=drop_log,
    )


def analyze_record(record: SelectedRecord, source: SourceEnvelope) -> dict[str, object]:
    family = infer_family(record.title, f"{record.excerpt}\n{source.full_text[:4000]}")
    counter = _weighted_counter(source, record)
    chapter_lookup = _chapter_lookup()
    appendix_lookup = _appendix_lookup()
    seeded_chapters = set(infer_chapter_links(record.title, record.excerpt, family))
    seeded_appendices = set(infer_appendix_links(record.title, record.excerpt, family))

    ranked_chapters = sorted(
        (
            (_chapter_score(counter, chapter, seeded_chapters, family), chapter)
            for chapter in CHAPTERS
        ),
        key=lambda item: (-item[0], item[1].index),
    )
    home_chapter = ranked_chapters[0][1]
    secondary_chapters = [chapter for _, chapter in ranked_chapters[1:4]]

    ranked_appendices = sorted(
        (
            (_appendix_score(counter, appendix, seeded_appendices), appendix)
            for appendix in APPENDICES
        ),
        key=lambda item: (-item[0], item[1][0]),
    )
    appendices = [appendix for _, appendix in ranked_appendices[:4]]

    dominant_lens = _score_dimension(counter, LENS_KEYWORDS)
    dominant_facet = _score_dimension(counter, FACET_KEYWORDS)
    z_point = _derive_z_point(source.title, source.headings)
    route_plan = build_route_plan(home_chapter, dominant_lens, dominant_facet, source.truth_state, z_point)

    return {
        "family": family,
        "home_chapter": chapter_lookup[home_chapter.code],
        "secondary_chapters": [chapter_lookup[item.code] for item in secondary_chapters],
        "appendices": [appendix_lookup[item[0]] for item in appendices],
        "dominant_lens": dominant_lens,
        "dominant_facet": dominant_facet,
        "z_point": z_point,
        "route_plan": route_plan,
    }


def build_hcrl_block(
    record: SelectedRecord,
    source: SourceEnvelope,
    family: str,
    home_chapter,
    secondary_chapters: list[object],
    appendices: list[tuple[str, str, str]],
    dominant_lens: str,
    dominant_facet: str,
) -> dict[str, list[str]]:
    appendix_codes = ", ".join(code for code, _, _ in appendices)
    return {
        "Square": [
            f"Object seed: {record.title} routed as {chapter_station_label(home_chapter)} with {record.extension} source semantics.",
            f"Address lattice: dominant lens {LENS_LABELS[dominant_lens]} and dominant facet {FACET_LABELS[dominant_facet]}.",
            f"Anchor set: home {home_chapter.code}, secondary {', '.join(chapter.code for chapter in secondary_chapters)}.",
        ],
        "Flower": [
            f"Orbit phase: arc {home_chapter.arc}, rotation {home_chapter.rot}, lane {home_chapter.lane}.",
            f"Couplings: family `{family}` resonates with appendices {appendix_codes}.",
            f"HCRL motion: Square -> Flower -> Cloud -> Fractal preserved for replay.",
        ],
        "Cloud": [
            f"Truth corridor: {source.truth_state} via local-source rewrite from `{source.read_mode}` intake.",
            f"Ambiguity notes: {', '.join(source.notes) if source.notes else 'none beyond bounded local rewrite residuals'}.",
            f"Evidence plan: verify against source hash {source.source_sha256[:12]} and replay hooks before promotion.",
        ],
        "Fractal": [
            f"Seed compression: {record.title} regenerates from {record.relative_path}.",
            f"Replay loop: {source.source_sha256[:16]} -> {home_chapter.code} -> {appendix_codes} -> Z*.",
            f"Next tunnels: {home_chapter.code} to {', '.join(chapter.code for chapter in secondary_chapters)} under bounded hub cap.",
        ],
    }


def build_crystal_tile(
    ms_code: str,
    home_chapter,
    secondary_chapters: list[object],
    appendices: list[tuple[str, str, str]],
    route_plan: RoutePlan,
) -> list[dict[str, object]]:
    secondary_codes = [chapter.code for chapter in secondary_chapters]
    appendix_codes = [code for code, _, _ in appendices]
    tile: list[dict[str, object]] = []
    for lens in HCRL_ORDER:
        for facet in ("1", "2", "3", "4"):
            tile.append(
                {
                    "row": f"{lens}{facet}",
                    "a": f"{ms_code}::{home_chapter.code}.{lens}{facet}.a anchors {LENS_LABELS[lens]} {FACET_LABELS[facet].lower()}",
                    "b": f"{ms_code}::{home_chapter.code}.{lens}{facet}.b couples {secondary_codes[(int(facet) - 1) % len(secondary_codes)] if secondary_codes else home_chapter.code}",
                    "c": f"{ms_code}::{home_chapter.code}.{lens}{facet}.c binds {appendix_codes[(ord(lens) + int(facet)) % len(appendix_codes)] if appendix_codes else 'AppA'}",
                    "d": f"{ms_code}::{home_chapter.code}.{lens}{facet}.d certifies hubs {'/'.join(route_plan.primary_hubs[:3])}",
                }
            )
    return tile


def build_rewrite_artifact(
    ms_code: str,
    record: SelectedRecord,
    docs_gate_state: str,
    duplicate_group: str | None,
    source: SourceEnvelope,
    analysis: dict[str, object],
) -> RewriteArtifact:
    home_chapter = analysis["home_chapter"]
    secondary_chapters = analysis["secondary_chapters"]
    appendices = analysis["appendices"]
    dominant_lens = analysis["dominant_lens"]
    dominant_facet = analysis["dominant_facet"]
    route_plan = analysis["route_plan"]
    hcrl = build_hcrl_block(
        record,
        source,
        analysis["family"],
        home_chapter,
        secondary_chapters,
        appendices,
        dominant_lens,
        dominant_facet,
    )
    crystal_tile = build_crystal_tile(ms_code, home_chapter, secondary_chapters, appendices, route_plan)
    return RewriteArtifact(
        ms_code=ms_code,
        record=record,
        docs_gate_status=docs_gate_state,
        duplicate_group=duplicate_group,
        source=source,
        family=analysis["family"],
        z_point=analysis["z_point"],
        home_chapter=home_chapter,
        secondary_chapters=secondary_chapters,
        appendices=appendices,
        dominant_lens=dominant_lens,
        dominant_facet=dominant_facet,
        route_plan=route_plan,
        hcrl=hcrl,
        crystal_tile=crystal_tile,
    )


def _support_graph_lines(artifact: RewriteArtifact) -> list[str]:
    home = artifact.home_chapter
    secondary = artifact.secondary_chapters
    appendices = artifact.appendices
    conflict_target = TRUTH_OVERLAY[artifact.route_plan.truth_state]
    lines = [
        f"- REF | {artifact.ms_code} -> {home.code} | home anchor | NavRole=ORBIT_NEXT",
        f"- DUAL | {home.code}.S* <-> {home.code}.F* | invariant=home-station | budget={artifact.route_plan.truth_state}",
        f"- GEN | {artifact.ms_code} -> {secondary[0].code if secondary else home.code} | family={artifact.family}",
        f"- INST | {secondary[0].code if secondary else home.code} -> {artifact.ms_code} | instance={artifact.record.relative_path}",
        f"- IMPL | {artifact.ms_code} -> {appendices[0][0] if appendices else 'AppA'} | route={'/'.join(artifact.route_plan.primary_hubs)}",
        f"- PROOF | {artifact.ms_code} -> {appendices[-1][0] if appendices else 'AppM'} | source_sha={artifact.source.source_sha256[:16]}",
        f"- CONFLICT | {artifact.ms_code} -> {conflict_target} | truth={artifact.route_plan.truth_state} | notes={'; '.join(artifact.source.notes) if artifact.source.notes else 'bounded residual'}",
    ]
    for chapter in secondary[1:]:
        lines.append(f"- REF | {artifact.ms_code} -> {chapter.code} | secondary anchor")
    for code, title, _ in appendices[1:]:
        lines.append(f"- REF | {artifact.ms_code} -> {code} | appendix anchor {title}")
    return lines


def render_rewrite_markdown(
    artifact: RewriteArtifact,
    manifest_path: Path,
    archive_member_manifest_path: Path | None = None,
) -> str:
    lines = [
        artifact.route_plan.tesseract_header,
        f"Primary hubs: {' -> '.join(artifact.route_plan.hubs_seq)}",
        f"Tunnel: {artifact.route_plan.tunnel}",
        f"TunnelPlan: {json.dumps(artifact.route_plan.tunnel_plan, ensure_ascii=True, sort_keys=True)}",
        f"Truth intent: {artifact.route_plan.truth_intent}",
        f"Truth state: {artifact.route_plan.truth_state}",
        f"HCRL pass: {json.dumps(artifact.route_plan.hcrl_pass, ensure_ascii=True, sort_keys=True)}",
        f"Obligations: {'; '.join(artifact.route_plan.obligations)}",
        f"Drop log: {'; '.join(artifact.route_plan.drop_log) if artifact.route_plan.drop_log else 'none'}",
        "",
        f"## **{artifact.ms_code} - {artifact.source.title}**",
        f"## **{chapter_station_label(artifact.home_chapter)} - {artifact.home_chapter.title}**",
        "## **Square**",
        *[f"- {line}" for line in artifact.hcrl["Square"]],
        "## **Flower**",
        *[f"- {line}" for line in artifact.hcrl["Flower"]],
        "## **Cloud**",
        *[f"- {line}" for line in artifact.hcrl["Cloud"]],
        "## **Fractal**",
        *[f"- {line}" for line in artifact.hcrl["Fractal"]],
        "## **Crystal Tile**",
    ]
    for row in artifact.crystal_tile:
        lines.append(f"- {row['row']}: a={row['a']} | b={row['b']} | c={row['c']} | d={row['d']}")
    lines.extend(
        [
            "## **Support Graph**",
            *_support_graph_lines(artifact),
            "## **Replay Hooks**",
            f"- Source path: {artifact.record.relative_path}",
            f"- Source hash: {artifact.source.source_sha256}",
            f"- Docs gate state: {artifact.docs_gate_status}",
            f"- Duplicate group: {artifact.duplicate_group or 'unique'}",
            f"- Archive member: {artifact.source.chosen_archive_member or 'n/a'}",
            f"- Archive candidates: {len(artifact.source.archive_candidates)}",
            *(
                [f"- Archive member manifest: {normalize_relative_path(str(archive_member_manifest_path))}"]
                if archive_member_manifest_path is not None and len(artifact.source.archive_candidates) > 1
                else []
            ),
            f"- Manifest pointer: {normalize_relative_path(str(manifest_path))}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def manifest_entry(
    artifact: RewriteArtifact,
    output_path: Path,
    archive_member_manifest_path: Path | None = None,
) -> dict[str, object]:
    return {
        "ms_code": artifact.ms_code,
        "relative_path": artifact.record.relative_path,
        "output_path": normalize_relative_path(str(output_path)),
        "source_sha256": artifact.source.source_sha256,
        "docs_gate_status": artifact.docs_gate_status,
        "truth_state": artifact.route_plan.truth_state,
        "family": artifact.family,
        "z_point": artifact.z_point,
        "home_chapter": artifact.home_chapter.code,
        "secondary_chapters": [chapter.code for chapter in artifact.secondary_chapters],
        "appendices": [code for code, _, _ in artifact.appendices],
        "dominant_lens": artifact.dominant_lens,
        "dominant_facet": artifact.dominant_facet,
        "tesseract_header": artifact.route_plan.tesseract_header,
        "hubs_seq": artifact.route_plan.hubs_seq,
        "tunnel_plan": artifact.route_plan.tunnel_plan,
        "truth_intent": artifact.route_plan.truth_intent,
        "hcrl_pass": artifact.route_plan.hcrl_pass,
        "obligations": artifact.route_plan.obligations,
        "primary_hubs": artifact.route_plan.primary_hubs,
        "drop_log": artifact.route_plan.drop_log,
        "duplicate_group": artifact.duplicate_group,
        "archive_candidates": artifact.source.archive_candidates,
        "chosen_archive_member": artifact.source.chosen_archive_member,
        "archive_member_manifest_path": (
            normalize_relative_path(str(archive_member_manifest_path))
            if archive_member_manifest_path is not None and len(artifact.source.archive_candidates) > 1
            else None
        ),
        "audit_status": {
            "contract_ok": True,
            "missing_output": False,
            "stale_source": False,
            "issue_count": 0,
        },
        "profile_version": PROFILE_VERSION,
    }


def truth_totals(entries: Iterable[dict[str, object]]) -> dict[str, int]:
    counts = {"OK": 0, "NEAR": 0, "AMBIG": 0, "FAIL": 0}
    for entry in entries:
        truth_state = str(entry["truth_state"])
        counts[truth_state] = counts.get(truth_state, 0) + 1
    return counts


def sibling_output_path(record: SelectedRecord) -> Path:
    path = Path(record.absolute_path)
    return path.with_name(f"{path.stem}.4d.md")
