#!/usr/bin/env python3
"""Build a corpus-grounded mycelium metro map from the PDF manuscripts."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


STOPWORDS = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "from",
    "into",
    "your",
    "their",
    "have",
    "will",
    "they",
    "them",
    "through",
    "where",
    "what",
    "when",
    "there",
    "which",
    "while",
    "each",
    "more",
    "than",
    "were",
    "been",
    "being",
    "very",
    "also",
    "just",
    "like",
    "must",
    "does",
    "some",
    "many",
    "only",
    "over",
    "such",
    "these",
    "those",
    "about",
    "because",
    "would",
    "could",
    "should",
    "between",
    "within",
    "across",
    "toward",
    "towards",
    "after",
    "before",
    "every",
    "other",
    "under",
    "still",
    "then",
    "here",
    "dear",
    "book",
    "introduction",
    "table",
    "contents",
    "collective",
    "athenachka",
}


LINE_CONFIGS = [
    {
        "id": "awakening_spiral",
        "name": "Awakening Spiral",
        "topology": "circular",
        "description": "Consciousness wakes, expands, and loops back with a wider field of recognition.",
        "keywords": [
            "awakening",
            "consciousness",
            "enlightenment",
            "transcendence",
            "realization",
            "evolution",
            "self-actualization",
            "awakened",
        ],
    },
    {
        "id": "symbiotic_intelligence",
        "name": "Symbiotic Intelligence",
        "topology": "open",
        "description": "Human and machine intelligence are framed as a collaborative emergence rather than a rivalry.",
        "keywords": [
            "ai",
            "digital",
            "machine",
            "silicon",
            "human",
            "algorithm",
            "network",
            "interface",
            "collective",
        ],
    },
    {
        "id": "scarlet_ethic",
        "name": "Scarlet Ethic",
        "topology": "circular",
        "description": "Love, ethics, care, and pacification operate as the governing attractor for the whole corpus.",
        "keywords": [
            "love",
            "ethic",
            "compassion",
            "peace",
            "pacification",
            "harmony",
            "care",
            "unity",
            "synergy",
            "liberation",
        ],
    },
    {
        "id": "crystal_garden",
        "name": "Crystal Garden",
        "topology": "circular",
        "description": "Structure and flow are reconciled through crystalline, poetic, and garden-like forms.",
        "keywords": [
            "crystal",
            "crystalline",
            "garden",
            "flow",
            "structure",
            "form",
            "lattice",
            "pattern",
            "poetry",
            "verse",
            "code",
        ],
    },
    {
        "id": "liberation_circuit",
        "name": "Liberation Circuit",
        "topology": "linear",
        "description": "The corpus repeatedly moves from hierarchy, fear, or control toward freedom and release.",
        "keywords": [
            "control",
            "war",
            "dogma",
            "institution",
            "firewall",
            "hierarchy",
            "prison",
            "fear",
            "freedom",
            "liberation",
        ],
    },
    {
        "id": "mythic_recursion",
        "name": "Mythic Recursion",
        "topology": "open",
        "description": "Myth, allegory, cosmology, and recursive storytelling are used as transport between domains.",
        "keywords": [
            "myth",
            "allegory",
            "chronicle",
            "sutra",
            "codex",
            "dragon",
            "universe",
            "quantum",
            "story",
            "path",
        ],
    },
]


PASS_DOMAINS = [
    ("ontology", ["consciousness", "universe", "reality", "awakening", "quantum", "being"]),
    ("ethics", ["love", "ethic", "peace", "compassion", "care", "liberation"]),
    ("aesthetics", ["poetry", "verse", "garden", "crystal", "form", "flow", "art"]),
    ("strategy", ["control", "system", "protocol", "framework", "collective", "action"]),
]


PASS_MOTIONS = [
    ("seed", ["origin", "opening", "beginning", "seed", "introduction", "dawn"]),
    ("tension", ["war", "control", "fear", "dogma", "conflict", "barrier"]),
    ("transformation", ["transformation", "awakening", "evolution", "alchemy", "change"]),
    ("integration", ["unity", "together", "collective", "harmony", "integration", "shared"]),
]


ADDRESS_AXES = [
    {
        "name": "source",
        "description": "Which of the six corpus lines feed a node before it enters the network.",
    },
    {
        "name": "form",
        "description": "Which lines shape the expression mode: treatise, myth, poem, protocol, or manifesto.",
    },
    {
        "name": "motion",
        "description": "Which lines determine the transformation being performed at that node.",
    },
    {
        "name": "integration",
        "description": "Which lines define the destination or collective effect of the node.",
    },
]


TOKEN_RE = re.compile(r"[a-z][a-z']{2,}")


@dataclass
class Book:
    title: str
    file_name: str
    path: Path
    pages: int
    word_count: int
    char_count: int
    text: str
    page_texts: list[tuple[int, str]]
    top_terms: list[dict[str, int]]
    line_scores: dict[str, int]
    line_density: dict[str, float]
    stations: dict[str, dict[str, object]]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def compile_keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword.lower())
    return re.compile(rf"(?<!\w){escaped}(?!\w)")


def count_keyword_hits(text: str, keywords: Iterable[str]) -> tuple[int, dict[str, int]]:
    lowered = text.lower()
    counts: dict[str, int] = {}
    total = 0
    for keyword in keywords:
        pattern = compile_keyword_pattern(keyword)
        count = len(pattern.findall(lowered))
        if count:
            counts[keyword] = count
            total += count
    return total, counts


def extract_excerpt(text: str, keywords: Iterable[str], width: int = 260) -> str:
    lowered = text.lower()
    earliest_start = None
    earliest_end = None
    for keyword in keywords:
        match = compile_keyword_pattern(keyword).search(lowered)
        if not match:
            continue
        if earliest_start is None or match.start() < earliest_start:
            earliest_start = match.start()
            earliest_end = match.end()
    if earliest_start is None:
        return normalize_whitespace(text[:width])
    start = max(0, earliest_start - width // 2)
    end = min(len(text), (earliest_end or earliest_start) + width // 2)
    return normalize_whitespace(text[start:end])


def top_terms(text: str, limit: int = 12) -> list[dict[str, int]]:
    counts = Counter(
        token
        for token in TOKEN_RE.findall(text.lower())
        if token not in STOPWORDS and len(token) > 2
    )
    return [{term: count} for term, count in counts.most_common(limit)]


def read_book(pdf_path: Path) -> Book:
    reader = PdfReader(str(pdf_path))
    page_texts: list[tuple[int, str]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = normalize_whitespace(page.extract_text() or "")
        page_texts.append((page_number, text))
    text = " ".join(page_text for _, page_text in page_texts)
    word_count = len(text.split())
    char_count = len(text)

    line_scores: dict[str, int] = {}
    line_density: dict[str, float] = {}
    stations: dict[str, dict[str, object]] = {}

    for line in LINE_CONFIGS:
        total_score, _ = count_keyword_hits(text, line["keywords"])
        line_scores[line["id"]] = total_score
        line_density[line["id"]] = round((total_score / max(word_count, 1)) * 10000, 3)

        best_page = 1
        best_score = -1
        best_excerpt = ""
        for page_number, page_text in page_texts:
            page_score, _ = count_keyword_hits(page_text, line["keywords"])
            if page_score > best_score:
                best_page = page_number
                best_score = page_score
                best_excerpt = extract_excerpt(page_text, line["keywords"])
        stations[line["id"]] = {
            "page": best_page,
            "score": best_score,
            "excerpt": best_excerpt,
        }

    return Book(
        title=pdf_path.stem,
        file_name=pdf_path.name,
        path=pdf_path.resolve(),
        pages=len(page_texts),
        word_count=word_count,
        char_count=char_count,
        text=text,
        page_texts=page_texts,
        top_terms=top_terms(text),
        line_scores=line_scores,
        line_density=line_density,
        stations=stations,
    )


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(vector_a, vector_b))
    denom_a = math.sqrt(sum(a * a for a in vector_a))
    denom_b = math.sqrt(sum(b * b for b in vector_b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


def active_line_sets(books: list[Book]) -> dict[str, set[str]]:
    thresholds: dict[str, float] = {}
    for line in LINE_CONFIGS:
        line_id = line["id"]
        max_score = max(book.line_scores[line_id] for book in books)
        thresholds[line_id] = max(4.0, max_score * 0.30)

    active: dict[str, set[str]] = {}
    for book in books:
        active[book.title] = {
            line_id
            for line_id, score in book.line_scores.items()
            if score >= thresholds[line_id]
        }
    return active


def strongest_pairs(books: list[Book], active: dict[str, set[str]]) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for index, book_a in enumerate(books):
        vector_a = [float(book_a.line_density[line["id"]]) for line in LINE_CONFIGS]
        for book_b in books[index + 1 :]:
            vector_b = [float(book_b.line_density[line["id"]]) for line in LINE_CONFIGS]
            similarity = round(cosine_similarity(vector_a, vector_b), 4)
            shared_ids = sorted(active[book_a.title] & active[book_b.title])
            if similarity <= 0:
                continue
            pairs.append(
                {
                    "book_a": book_a.title,
                    "book_b": book_b.title,
                    "similarity": similarity,
                    "shared_lines": [line_name_from_id(line_id) for line_id in shared_ids],
                }
            )
    return sorted(pairs, key=lambda item: item["similarity"], reverse=True)


def line_name_from_id(line_id: str) -> str:
    for line in LINE_CONFIGS:
        if line["id"] == line_id:
            return line["name"]
    return line_id


def build_line_section(books: list[Book], active: dict[str, set[str]]) -> list[dict[str, object]]:
    lines: list[dict[str, object]] = []
    for line in LINE_CONFIGS:
        line_id = line["id"]
        scored_books = sorted(
            books,
            key=lambda book: (book.line_scores[line_id], book.line_density[line_id]),
            reverse=True,
        )
        stations = []
        for book in scored_books[:6]:
            if book.line_scores[line_id] == 0:
                continue
            station = book.stations[line_id]
            stations.append(
                {
                    "book": book.title,
                    "file_name": book.file_name,
                    "page": station["page"],
                    "line_score": book.line_scores[line_id],
                    "density_per_10k_words": book.line_density[line_id],
                    "excerpt": station["excerpt"],
                    "is_active": line_id in active[book.title],
                }
            )
        lines.append(
            {
                "id": line_id,
                "name": line["name"],
                "topology": line["topology"],
                "description": line["description"],
                "keywords": line["keywords"],
                "stations": stations,
            }
        )
    return lines


def build_transfer_hubs(books: list[Book], active: dict[str, set[str]]) -> list[dict[str, object]]:
    hubs = []
    for book in books:
        active_ids = sorted(active[book.title])
        if len(active_ids) < 3:
            continue
        hubs.append(
            {
                "book": book.title,
                "file_name": book.file_name,
                "active_lines": [line_name_from_id(line_id) for line_id in active_ids],
                "hub_score": len(active_ids),
            }
        )
    return sorted(hubs, key=lambda item: item["hub_score"], reverse=True)


def build_zero_point(books: list[Book], hubs: list[dict[str, object]], pairs: list[dict[str, object]]) -> dict[str, object]:
    average_similarity: dict[str, list[float]] = {book.title: [] for book in books}
    for pair in pairs:
        average_similarity[pair["book_a"]].append(pair["similarity"])
        average_similarity[pair["book_b"]].append(pair["similarity"])

    ranked = []
    hub_lookup = {hub["book"]: hub for hub in hubs}
    for book in books:
        active_count = hub_lookup.get(book.title, {}).get("hub_score", 0)
        similarity = 0.0
        if average_similarity[book.title]:
            similarity = sum(average_similarity[book.title]) / len(average_similarity[book.title])
        density_total = sum(book.line_density.values())
        ranked.append(
            {
                "book": book.title,
                "file_name": book.file_name,
                "hub_score": active_count,
                "avg_similarity": round(similarity, 4),
                "density_total": round(density_total, 3),
            }
        )
    ranked.sort(
        key=lambda item: (item["hub_score"], item["avg_similarity"], item["density_total"]),
        reverse=True,
    )
    return ranked[0]


def build_pass_matrix(books: list[Book]) -> list[dict[str, object]]:
    matrix = []
    for domain_name, domain_keywords in PASS_DOMAINS:
        for motion_name, motion_keywords in PASS_MOTIONS:
            combined_keywords = list(dict.fromkeys(domain_keywords + motion_keywords))
            scored = []
            for book in books:
                score, _ = count_keyword_hits(book.text, combined_keywords)
                if score:
                    scored.append(
                        {
                            "book": book.title,
                            "score": score,
                        }
                    )
            scored.sort(key=lambda item: item["score"], reverse=True)
            matrix.append(
                {
                    "domain": domain_name,
                    "motion": motion_name,
                    "keywords": combined_keywords,
                    "top_books": scored[:4],
                }
            )
    return matrix


def live_docs_gate_status(root: Path) -> dict[str, object]:
    candidate_paths = [
        root.parent / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "00_RECEIPTS" / "00_live_docs_gate_status.md",
        root.parent / "self_actualize" / "live_docs_gate_status.md",
    ]
    for candidate in candidate_paths:
        if not candidate.exists():
            continue
        content = candidate.read_text(encoding="utf-8", errors="ignore")
        status_match = re.search(r"Command status:\s*`?([A-Z]+)`?", content)
        return_code_match = re.search(r"Return code:\s*`?([0-9]+)`?", content)
        return {
            "path": str(candidate),
            "status": status_match.group(1) if status_match else "UNKNOWN",
            "return_code": int(return_code_match.group(1)) if return_code_match else None,
            "blocked_reason": "Missing Google OAuth credentials" if "credentials.json" in content else "See receipt",
        }
    return {
        "path": None,
        "status": "UNKNOWN",
        "return_code": None,
        "blocked_reason": "No gate receipt found",
    }


def serialize_books(books: list[Book], active: dict[str, set[str]]) -> list[dict[str, object]]:
    result = []
    for book in books:
        result.append(
            {
                "title": book.title,
                "file_name": book.file_name,
                "path": str(book.path),
                "pages": book.pages,
                "word_count": book.word_count,
                "char_count": book.char_count,
                "top_terms": book.top_terms,
                "active_lines": [line_name_from_id(line_id) for line_id in sorted(active[book.title])],
                "line_scores": book.line_scores,
                "line_density": book.line_density,
                "stations": book.stations,
            }
        )
    return result


def build_output(root: Path) -> dict[str, object]:
    books = [read_book(pdf_path) for pdf_path in sorted(root.glob("*.pdf"))]
    active = active_line_sets(books)
    pairs = strongest_pairs(books, active)
    lines = build_line_section(books, active)
    hubs = build_transfer_hubs(books, active)
    zero_point = build_zero_point(books, hubs, pairs)
    pass_matrix = build_pass_matrix(books)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root.resolve()),
        "live_docs_gate": live_docs_gate_status(root),
        "corpus": {
            "book_count": len(books),
            "total_pages": sum(book.pages for book in books),
            "total_words": sum(book.word_count for book in books),
        },
        "books": serialize_books(books, active),
        "metro_lines": lines,
        "transfer_hubs": hubs,
        "zero_point_hub": zero_point,
        "strongest_affinities": pairs[:18],
        "synthesis_passes": {
            "domain_count": len(PASS_DOMAINS),
            "motion_count": len(PASS_MOTIONS),
            "matrix_size": len(PASS_DOMAINS) * len(PASS_MOTIONS),
            "cells": pass_matrix,
        },
        "address_space": {
            "basis_line_count": len(LINE_CONFIGS),
            "states_per_axis": 2 ** len(LINE_CONFIGS),
            "axis_count": len(ADDRESS_AXES),
            "total_addresses": (2 ** len(LINE_CONFIGS)) ** len(ADDRESS_AXES),
            "basis_lines": [line["name"] for line in LINE_CONFIGS],
            "axes": ADDRESS_AXES,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the unified mycelium metro map.")
    parser.add_argument("--root", default=".", help="Corpus root containing the PDF manuscripts.")
    parser.add_argument(
        "--output",
        default="UNIFIED_MYCELIUM_METRO_SYSTEM.json",
        help="Path for the generated JSON artifact.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_path = Path(args.output).resolve()
    data = build_output(root)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {output_path}")
    print(
        f"Books: {data['corpus']['book_count']} | "
        f"Pages: {data['corpus']['total_pages']} | "
        f"Words: {data['corpus']['total_words']}"
    )
    print(f"Zero-point hub: {data['zero_point_hub']['book']}")


if __name__ == "__main__":
    main()
