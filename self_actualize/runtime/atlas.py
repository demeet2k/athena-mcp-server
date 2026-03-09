from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from .contracts import EvidenceRef


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "for",
    "in",
    "on",
    "with",
    "my",
    "full",
    "build",
    "your",
    "from",
    "into",
    "this",
}

SIGNIFICANT_SHORT_TOKENS = {
    "ai",
    "ml",
    "nn",
    "os",
    "ui",
    "ux",
    "qa",
    "js",
    "ts",
    "py",
    "cpu",
    "gpu",
}


@dataclass
class AtlasRecord:
    raw: dict[str, Any]

    @property
    def record_id(self) -> str:
        return self.raw["record_id"]

    @property
    def relative_path(self) -> str:
        return self.raw["relative_path"]

    @property
    def top_level(self) -> str:
        return self.raw.get("top_level", "")

    @property
    def kind(self) -> str:
        return self.raw["kind"]

    @property
    def sha256(self) -> str:
        return self.raw["sha256"]

    @property
    def excerpt(self) -> str:
        return self.raw.get("excerpt", "")

    @property
    def headings(self) -> list[str]:
        return self.raw.get("heading_candidates", [])

    @property
    def role_tags(self) -> list[str]:
        return self.raw.get("role_tags", [])

    @property
    def evidence(self) -> dict[str, Any]:
        return self.raw.get("evidence", {})

    @property
    def locator(self) -> str:
        return self.evidence.get("locator", self.raw.get("path", ""))


@dataclass
class RegimeProfile:
    name: str
    keywords: list[str]
    preferred_top_levels: list[str]
    penalized_top_levels: list[str]
    preferred_role_tags: list[str]
    preferred_path_keywords: list[str]
    penalized_path_keywords: list[str]
    preferred_kinds: list[str]
    lens_mix: dict[str, float]


class CorpusAtlas:
    def __init__(self, atlas_sources: list[Path], records: list[AtlasRecord], regime_profiles: dict[str, RegimeProfile]) -> None:
        self.atlas_sources = atlas_sources
        self.atlas_path = atlas_sources[0]
        self.records = records
        self.regime_profiles = regime_profiles

    @property
    def source_label(self) -> str:
        return " + ".join(str(path) for path in self.atlas_sources)

    @classmethod
    def load_default(cls) -> "CorpusAtlas | None":
        atlas_dir = Path(__file__).resolve().parents[1]
        atlas_sources = [
            atlas_dir / "corpus_atlas.json",
            atlas_dir / "archive_atlas.json",
        ]
        existing_sources = [path for path in atlas_sources if path.exists()]
        if not existing_sources:
            return None

        records: list[AtlasRecord] = []
        for atlas_path in existing_sources:
            payload = json.loads(atlas_path.read_text(encoding="utf-8"))
            records.extend(AtlasRecord(raw=record) for record in payload.get("records", []))
        regime_profiles = cls._load_regime_profiles()
        return cls(atlas_sources=existing_sources, records=records, regime_profiles=regime_profiles)

    @classmethod
    def _load_regime_profiles(cls) -> dict[str, RegimeProfile]:
        profiles_path = Path(__file__).resolve().parents[1] / "regime_profiles.json"
        if not profiles_path.exists():
            return {"default": cls._default_profile()}

        raw_profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        profiles: dict[str, RegimeProfile] = {}
        for name, payload in raw_profiles.items():
            profiles[name] = RegimeProfile(
                name=name,
                keywords=payload.get("keywords", []),
                preferred_top_levels=payload.get("preferred_top_levels", []),
                penalized_top_levels=payload.get("penalized_top_levels", []),
                preferred_role_tags=payload.get("preferred_role_tags", []),
                preferred_path_keywords=payload.get("preferred_path_keywords", []),
                penalized_path_keywords=payload.get("penalized_path_keywords", []),
                preferred_kinds=payload.get("preferred_kinds", []),
                lens_mix=payload.get(
                    "lens_mix",
                    {"square": 0.3, "flower": 0.2, "cloud": 0.25, "fractal": 0.25},
                ),
            )

        if "default" not in profiles:
            profiles["default"] = cls._default_profile()
        return profiles

    @staticmethod
    def _default_profile() -> RegimeProfile:
        return RegimeProfile(
            name="default",
            keywords=[],
            preferred_top_levels=[],
            penalized_top_levels=[],
            preferred_role_tags=[],
            preferred_path_keywords=[],
            penalized_path_keywords=[],
            preferred_kinds=["document", "text", "code", "data"],
            lens_mix={"square": 0.3, "flower": 0.2, "cloud": 0.25, "fractal": 0.25},
        )

    @staticmethod
    def _keywords(text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        return [
            token
            for token in tokens
            if token not in STOPWORDS and (len(token) > 2 or token in SIGNIFICANT_SHORT_TOKENS)
        ]

    @staticmethod
    def _field_overlap(keywords: list[str], text: str) -> int:
        return sum(1 for keyword in set(keywords) if keyword in text)

    @staticmethod
    def _phrase_bonus(keywords: list[str], text: str) -> float:
        normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
        bonus = 0.0
        for size, weight in ((3, 1.6), (2, 1.0)):
            if len(keywords) < size:
                continue
            for index in range(len(keywords) - size + 1):
                phrase = " ".join(keywords[index : index + size])
                if phrase in normalized:
                    bonus += weight
        return bonus

    def infer_regime(self, query: str) -> RegimeProfile:
        query_keywords = set(self._keywords(query))
        best_profile = self.regime_profiles["default"]
        best_score = 0

        for name, profile in self.regime_profiles.items():
            if name == "default":
                continue
            score = len(query_keywords.intersection(profile.keywords))
            if score > best_score:
                best_score = score
                best_profile = profile

        return best_profile

    @staticmethod
    def _lens_bonus(record: AtlasRecord, route_lens: str | None) -> float:
        if not route_lens:
            return 0.0

        tags = set(record.role_tags)
        bonus = 0.0
        if route_lens == "square_structure":
            if record.kind in {"code", "data"}:
                bonus += 0.7
            if tags.intersection({"formal-framework", "atlas", "orchestration", "executable"}):
                bonus += 0.5
        elif route_lens == "cloud_ambiguity":
            if record.kind in {"document", "text"}:
                bonus += 0.5
            if tags.intersection({"manuscript", "external-retrieval", "readable"}):
                bonus += 0.5
        elif route_lens == "fractal_scaling":
            if record.kind in {"document", "text", "code"}:
                bonus += 0.4
            if tags.intersection({"formal-framework", "manuscript", "runtime-learning", "orchestration"}):
                bonus += 0.4
        return bonus

    def search(
        self,
        query: str,
        limit: int = 6,
        preferred_kinds: set[str] | None = None,
        regime_name: str = "default",
        route_lens: str | None = None,
    ) -> list[EvidenceRef]:
        keywords = self._keywords(query)
        profile = self.regime_profiles.get(regime_name, self.regime_profiles["default"])
        preferred_top_levels = {item.lower() for item in profile.preferred_top_levels}
        penalized_top_levels = {item.lower() for item in profile.penalized_top_levels}
        preferred_role_tags = {item.lower() for item in profile.preferred_role_tags}
        preferred_path_keywords = {item.lower() for item in profile.preferred_path_keywords}
        penalized_path_keywords = {item.lower() for item in profile.penalized_path_keywords}

        scored: list[tuple[float, AtlasRecord]] = []

        for record in self.records:
            if preferred_kinds and record.kind not in preferred_kinds:
                continue
            if profile.preferred_kinds and record.kind not in set(profile.preferred_kinds) and record.kind not in {"document", "text", "code", "data"}:
                continue

            path_text = record.relative_path.lower()
            role_text = " ".join(record.role_tags).lower()
            heading_text = " ".join(record.headings).lower()
            excerpt_text = record.excerpt.lower()
            top_level = record.top_level.lower()
            basename_text = re.sub(
                r"[^a-z0-9]+",
                " ",
                PurePosixPath(path_text.replace("\\", "/").replace("::", "/")).name.lower(),
            )

            path_overlap = self._field_overlap(keywords, path_text)
            role_overlap = self._field_overlap(keywords, role_text)
            heading_overlap = self._field_overlap(keywords, heading_text)
            excerpt_overlap = self._field_overlap(keywords, excerpt_text)
            basename_overlap = self._field_overlap(keywords, basename_text)

            lexical_score = (
                path_overlap * 2.2
                + basename_overlap * 2.0
                + role_overlap * 1.8
                + heading_overlap * 1.4
                + excerpt_overlap * 0.35
            )
            lexical_score += self._phrase_bonus(keywords, f"{record.relative_path} {' '.join(record.headings)}")
            if lexical_score == 0:
                continue

            score = lexical_score
            if record.kind in {"document", "text", "code"}:
                score += 0.3
            if preferred_kinds and record.kind in preferred_kinds:
                score += 0.4
            if top_level in preferred_top_levels:
                score += 1.5
            if top_level in penalized_top_levels:
                score -= 2.0

            matching_role_tags = preferred_role_tags.intersection({tag.lower() for tag in record.role_tags})
            score += 0.7 * len(matching_role_tags)

            score += 0.45 * sum(1 for token in preferred_path_keywords if token in path_text)
            score -= 0.6 * sum(1 for token in penalized_path_keywords if token in path_text)

            if top_level == "self_actualize":
                if regime_name in {"atlas-build", "orchestration"}:
                    score += 0.4
                else:
                    score -= 1.0

            if "_extracted\\" in path_text:
                score += 0.25
            if not record.excerpt:
                score -= 0.25
            if record.evidence.get("source_type") == "zip_entry" and record.kind in {"code", "text", "data", "document"}:
                score += 0.35

            score += self._lens_bonus(record, route_lens)
            scored.append((score, record))

        scored.sort(key=lambda item: (-item[0], item[1].relative_path.lower()))
        results: list[EvidenceRef] = []
        seen_content_keys: set[str] = set()

        for score, record in scored:
            dedupe_key = record.evidence.get("text_hash") or record.sha256
            if dedupe_key and dedupe_key in seen_content_keys:
                continue
            if dedupe_key:
                seen_content_keys.add(dedupe_key)

            results.append(
                EvidenceRef(
                    record_id=record.record_id,
                    relative_path=record.relative_path,
                    kind=record.kind,
                    score=round(score, 3),
                    locator=record.locator,
                    excerpt=record.excerpt,
                    heading=(record.headings[0] if record.headings else ""),
                    sha256=record.sha256,
                    text_hash=record.evidence.get("text_hash", ""),
                )
            )
            if len(results) >= limit:
                break

        return results
