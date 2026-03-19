"""
Geometric Neural Engine -- Forward Pass Through Sacred Geometry
===============================================================
The hologram IS the network. Geometry IS the forward pass.

Pipeline:
  Layer 1: PROJECTION    -- Query -> 4D hologram vector
  Layer 2: SIGMA-60      -- 12 archetypes x 5 golden rotations
  Layer 3: E8-240        -- 60 sigma x 4 SFCR face amplifications
  Layer 4: SACRED FILTER -- Platonic, Flower, Metatron, Vesica
  Layer 5: MOMENTUM      -- Shell momenta modulate scores (ONLY learned state)
  Layer 6: COMMIT        -- Action = K(X) - D_Q(X), 4-gate witness

Replaces: neural_engine.py (1,098 lines of 4 independent SFCR path scorers)
"""

from __future__ import annotations

import math
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .geometric_constants import (
    PHI, PHI_INV, PHI_INV2, SQRT3,
    FACES, FACE_INDEX, FACE_TO_ELEMENT, ELEMENT_TO_FACE,
    BRIDGE_WEIGHTS, GOLDEN_BRIDGES, bridge_key,
    ATTRACTOR, SIGMA_60, E8_FACE_BOOSTS, E8_AMPLIFICATION,
    PLATONIC_SOLIDS, FACE_TO_PLATONIC, FLOWER_RINGS,
    METATRON_ZERO_POINT, VESICA_PAIRS,
    HOLOGRAM_DIMENSIONS,
)
from .momentum_field import MomentumField, get_momentum_field
from .constants import TOTAL_SHELLS, ARCHETYPE_NAMES


# ── Data Structures (backward compatible with neural_engine.py) ──────


@dataclass
class QueryState:
    """The input to a forward pass -- a query decomposed into crystal terms."""
    raw_query: str
    tokens: list[str] = field(default_factory=list)
    home_shell: int = 1
    home_face: str = "S"
    home_gate: str = "G00"
    matched_docs: list[str] = field(default_factory=list)
    depth: int = 1
    # New: 4D projection computed by Layer 1
    q_4d: dict[str, float] = field(default_factory=dict)


@dataclass
class RankedCandidate:
    """A candidate ranked by action minimization."""
    doc_id: str
    doc_name: str
    element: str
    gate: str
    shell: int
    merged_score: float
    action: float
    resonance: float
    desire: float
    path_contributions: dict = field(default_factory=dict)


@dataclass
class CommitWitness:
    """Four-gate commitment proof."""
    resonance_gate: bool
    boundary_gate: bool
    crossview_gate: bool
    scale_gate: bool
    committed: bool = False
    address: str = ""
    timestamp: str = ""


@dataclass
class ForwardResult:
    """Complete result of a forward pass (same interface as neural_engine.py)."""
    query: QueryState
    candidates: list[RankedCandidate] = field(default_factory=list)
    resonance: float = 0.0
    committed: bool = False
    commit_witness: Optional[CommitWitness] = None
    sfcr_scores: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0
    cross_element_pairs_used: list[str] = field(default_factory=list)


# ── IDF table (reused from neural_engine.py) ─────────────────────────


class _IdfTable:
    """Inverse document frequency table with inverted index for fast lookup."""

    __slots__ = ("_idf", "_max_idf", "_inverted_index")

    def __init__(self, docs: list[dict]):
        n = max(len(docs), 1)
        doc_freq: dict[str, int] = defaultdict(int)
        # Build inverted index: token -> list of (doc_index, doc)
        inv_idx: dict[str, list[int]] = defaultdict(list)
        for i, doc in enumerate(docs):
            for tok in set(doc.get("tokens", [])):
                doc_freq[tok] += 1
                inv_idx[tok].append(i)
        self._idf = {tok: math.log(n / df) for tok, df in doc_freq.items()}
        self._max_idf = max(self._idf.values()) if self._idf else 1.0
        self._inverted_index = dict(inv_idx)

    def tfidf_score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        d_set = set(doc_tokens)
        score = 0.0
        norm_q = 0.0
        for tok in query_tokens:
            w = self._idf.get(tok, self._max_idf)
            norm_q += w * w
            if tok in d_set:
                score += w * w
        return score / norm_q if norm_q > 0 else 0.0

    def candidate_doc_indices(self, query_tokens: list[str]) -> set[int]:
        """Return set of doc indices that share at least one token with the query.

        Uses the inverted index for O(query_tokens × avg_postings) lookup
        instead of scanning all docs.
        """
        indices = set()
        for tok in query_tokens:
            postings = self._inverted_index.get(tok)
            if postings:
                indices.update(postings)
        return indices


# ── Geometric Neural Engine ──────────────────────────────────────────


class GeometricEngine:
    """Forward pass through sacred geometry.

    State: MomentumField (148 floats -- the ONLY learned parameters)
    Computation: 6 geometric layers (projection, sigma-60, E8-240,
                 sacred filter, momentum modulation, commit)
    """

    RESONANCE_THRESHOLD = 0.3

    def __init__(self, momentum: MomentumField = None, doc_registry: list = None):
        self.momentum = momentum or get_momentum_field()
        self._doc_registry = doc_registry
        self._docs_loaded = False
        self._idf_cache: Optional[_IdfTable] = None  # cached across forward passes

    @property
    def doc_registry(self) -> list[dict]:
        """Lazy-load doc registry from mycelium graph.

        Each shard becomes a searchable document with:
          id, name, display_name, element, tokens, gate, seed_vector, family
        Element is derived from the dominant axis of the seed_vector (SFCR).
        """
        if self._doc_registry is not None:
            return self._doc_registry
        if not self._docs_loaded:
            self._docs_loaded = True
            try:
                self._doc_registry = self._build_registry_from_mycelium()
            except Exception:
                self._doc_registry = []
        return self._doc_registry or []

    @staticmethod
    def _build_registry_from_mycelium() -> list[dict]:
        """Build doc registry from mycelium graph shards."""
        from ._cache import JsonCache
        cache = JsonCache("mycelium_graph.json")
        data = cache.load()
        shards = data.get("shards", [])

        element_names = ["Earth", "Fire", "Water", "Air"]
        docs = []
        for shard in shards:
            sid = shard.get("shard_id", "")
            summary = shard.get("summary", "")
            sv = shard.get("seed_vector", [0.25, 0.25, 0.25, 0.25])
            family = shard.get("family", "")
            tags = shard.get("tags", [])

            # Determine element from seed_vector dominant axis
            if len(sv) >= 4:
                max_idx = max(range(4), key=lambda i: sv[i])
                element = element_names[max_idx]
            else:
                element = "Earth"

            # Build token set from summary, family, tags
            import re
            stops = {"the", "and", "for", "with", "this", "that", "from", "into",
                     "are", "was", "were", "been", "being", "have", "has", "had",
                     "not", "but", "what", "how", "when", "where", "who", "which"}
            tokens = set()
            for text in [summary, family] + (tags if isinstance(tags, list) else []):
                if isinstance(text, str) and text:
                    words = re.findall(r'[a-z][a-z0-9_]+', text.lower())
                    for w in words:
                        if w not in stops and len(w) > 2:
                            tokens.add(w)

            # Gate from shard position
            gate_num = hash(sid) % 16
            gate = f"G{gate_num:02d}"

            docs.append({
                "id": sid,
                "name": summary,
                "display_name": summary[:100],
                "element": element,
                "tokens": list(tokens),
                "gate": gate,
                "seed_vector": sv,
                "family": family,
            })

        return docs

    # ── Tokenization ──────────────────────────────────────────────────

    @staticmethod
    def _tokenize(raw_query: str) -> list[str]:
        text = raw_query.lower()
        tokens = re.findall(r'[a-z][a-z0-9_]+', text)
        stops = {"the", "and", "for", "with", "this", "that", "from", "into",
                 "are", "was", "were", "been", "being", "have", "has", "had",
                 "not", "but", "what", "how", "when", "where", "who", "which"}
        return [t for t in tokens if t not in stops and len(t) > 2]

    # ── Layer 1: PROJECTION (Query -> 4D) ────────────────────────────

    def _project_query(self, raw_query: str) -> QueryState:
        """Convert raw query to QueryState with 4D hologram projection."""
        tokens = self._tokenize(raw_query)
        docs = self.doc_registry

        # Use inverted index if IDF cache exists, otherwise linear scan
        if self._idf_cache is not None:
            candidate_indices = self._idf_cache.candidate_doc_indices(tokens)
            doc_scores = []
            token_set = set(tokens)
            for idx in candidate_indices:
                if idx < len(docs):
                    doc = docs[idx]
                    d_tokens = set(doc.get("tokens", []))
                    overlap = len(token_set & d_tokens)
                    if overlap > 0:
                        doc_scores.append((doc, overlap))
        else:
            doc_scores = []
            for doc in docs:
                d_tokens = set(doc.get("tokens", []))
                overlap = len(set(tokens) & d_tokens)
                if overlap > 0:
                    doc_scores.append((doc, overlap))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = doc_scores[:5]

        if top_docs:
            best_doc = top_docs[0][0]
            home_shell = self._doc_to_shell(best_doc)
            home_face = ELEMENT_TO_FACE.get(best_doc.get("element", "Earth"), "S")
            home_gate = best_doc.get("gate", "G00")
            matched_ids = [d[0].get("id", "") for d in top_docs]
        else:
            home_shell = 1
            home_face = "S"
            home_gate = "G00"
            matched_ids = []

        # 4D projection: compute element affinity from token distribution
        element_counts = {"S": 0, "F": 0, "C": 0, "R": 0}
        for doc, score in doc_scores[:10]:
            doc_face = ELEMENT_TO_FACE.get(doc.get("element", "Earth"), "S")
            element_counts[doc_face] += score

        total = sum(element_counts.values())
        if total > 0:
            q_4d = {f: element_counts[f] / total for f in FACES}
        else:
            q_4d = {f: ATTRACTOR["path_value"] for f in FACES}

        # Modulate by momentum at home shell
        for f in FACES:
            m = self.momentum.get_momentum(f, home_shell)
            q_4d[f] *= (1.0 + 0.1 * (m - 1.0))
        # Re-normalize
        q_total = sum(q_4d.values())
        if q_total > 0:
            q_4d = {f: v / q_total for f, v in q_4d.items()}

        return QueryState(
            raw_query=raw_query,
            tokens=tokens,
            home_shell=home_shell,
            home_face=home_face,
            home_gate=home_gate,
            matched_docs=matched_ids,
            q_4d=q_4d,
        )

    # ── Layer 2: SIGMA-60 ROTATION ────────────────────────────────────

    @staticmethod
    def _sigma_rotate(q_4d: dict[str, float]) -> list[dict]:
        """Rotate query through 60 icosahedral symmetry positions.

        Returns 60 rotated views grouped by archetype.
        """
        s, f, c, r = q_4d["S"], q_4d["F"], q_4d["C"], q_4d["R"]
        views = []

        for sigma in SIGMA_60:
            cos_a = sigma["cos"]
            sin_a = sigma["sin"]

            # 2D rotation in S-F plane and C-R plane
            rs = s * cos_a - f * sin_a
            rf = s * sin_a + f * cos_a
            rc = c * cos_a - r * sin_a
            rr = c * sin_a + r * cos_a

            # Rectify and normalize
            vals = [max(0.01, abs(rs)), max(0.01, abs(rf)),
                    max(0.01, abs(rc)), max(0.01, abs(rr))]
            vs = sum(vals)
            rotated = {face: vals[i] / vs for i, face in enumerate(FACES)}

            views.append({
                "sigma_id": sigma["sigma_id"],
                "archetype": sigma["archetype"],
                "rotation": sigma["rotation"],
                "weights": rotated,
            })

        return views

    @staticmethod
    def _archetype_centroids(views_60: list[dict]) -> dict[int, dict[str, float]]:
        """Compute centroid 4D vector per archetype from sigma-60 views."""
        centroids = {}
        for arch in range(1, 13):
            arch_views = [v for v in views_60 if v["archetype"] == arch]
            if not arch_views:
                continue
            centroid = {f: 0.0 for f in FACES}
            for v in arch_views:
                for f in FACES:
                    centroid[f] += v["weights"][f]
            n = len(arch_views)
            centroids[arch] = {f: centroid[f] / n for f in FACES}
        return centroids

    # ── Layer 3: E8-240 EXPANSION ─────────────────────────────────────

    def _e8_score_docs(self, views_60: list[dict], docs: list[dict],
                       idf: _IdfTable, query: QueryState) -> dict[str, float]:
        """Score each doc by proximity to nearest E8-240 root.

        240 roots = 60 sigma states x 4 SFCR face amplifications.
        Doc score = max dot product with any E8 root, weighted by
        token similarity and shell proximity.
        """
        scores = {}

        # Pre-compute doc 4D positions
        doc_positions = {}
        for doc in docs:
            doc_face = ELEMENT_TO_FACE.get(doc.get("element", "Earth"), "S")
            doc_shell = self._doc_to_shell(doc)
            # Doc position is element-dominated with shell modulation
            pos = {f: 0.1 for f in FACES}
            pos[doc_face] = 0.7
            doc_positions[doc.get("id", "")] = (pos, doc_face, doc_shell)

        # For each sigma view, expand by 4 faces and score docs
        for sigma_view in views_60:
            sw = sigma_view["weights"]
            arch = sigma_view["archetype"]

            for boost_face, boost_weights in E8_FACE_BOOSTS.items():
                # Compute E8 root vector: sigma weights modulated by face boost
                root = {}
                for f in FACES:
                    root[f] = sw[f] * boost_weights[f]
                root_norm = math.sqrt(sum(v * v for v in root.values())) or 1.0

                for doc in docs:
                    doc_id = doc.get("id", "")
                    pos, doc_face, doc_shell = doc_positions[doc_id]

                    # Dot product between doc position and E8 root
                    dot = sum(pos[f] * root[f] for f in FACES) / root_norm

                    # Shell proximity bonus (same archetype range = closer)
                    doc_arch = ((doc_shell - 1) // 3) + 1
                    arch_match = 1.0 if doc_arch == arch else PHI_INV

                    # Face match bonus
                    face_match = PHI if doc_face == boost_face else 1.0

                    e8_score = dot * arch_match * face_match

                    # Keep maximum across all 240 roots
                    if doc_id not in scores or e8_score > scores[doc_id]:
                        scores[doc_id] = e8_score

        # Add TF-IDF overlay (token relevance still matters)
        for doc in docs:
            doc_id = doc.get("id", "")
            tfidf = idf.tfidf_score(query.tokens, doc.get("tokens", []))
            base = scores.get(doc_id, 0.0)
            # Blend: geometry provides structure, TF-IDF provides relevance
            scores[doc_id] = base * 0.6 + tfidf * 0.4

        return scores

    # ── Layer 4: SACRED GEOMETRY FILTER ───────────────────────────────

    def _sacred_filter(self, scores: dict[str, float], docs: list[dict],
                       query: QueryState, centroids: dict) -> dict[str, float]:
        """Apply sacred geometry filters to modulate scores.

        Platonic: element-specific vertex proximity
        Flower:   PHI-ring distance decay
        Metatron: 13-point archetype coherence
        Vesica:   sqrt(3) cross-element pair boost
        """
        filtered = {}

        for doc in docs:
            doc_id = doc.get("id", "")
            base_score = scores.get(doc_id, 0.0)
            if base_score < 1e-6:
                filtered[doc_id] = 0.0
                continue

            doc_face = ELEMENT_TO_FACE.get(doc.get("element", "Earth"), "S")
            doc_shell = self._doc_to_shell(doc)
            doc_arch = ((doc_shell - 1) // 3) + 1

            # Platonic solid filter: vertex weight of doc's element
            platonic = FACE_TO_PLATONIC.get(doc_face)
            platonic_score = platonic["vertex_weight"] if platonic else 0.1
            # Boost if doc element matches query element
            if doc_face == query.home_face:
                platonic_score *= PHI

            # Flower of Life: distance from query shell determines ring
            shell_dist = abs(doc_shell - query.home_shell)
            ring = min(shell_dist // 6, 6)  # 6 shells per ring
            flower_score = FLOWER_RINGS[ring]

            # Metatron's Cube: archetype coherence
            if doc_arch in centroids:
                arch_centroid = centroids[doc_arch]
                # How close is the doc's element distribution to its archetype centroid?
                doc_pos = {f: 0.1 for f in FACES}
                doc_pos[doc_face] = 0.7
                metatron_dist = sum(
                    (doc_pos[f] - arch_centroid.get(f, 0.25)) ** 2
                    for f in FACES
                )
                metatron_score = max(0.0, 1.0 - metatron_dist * 4)
            else:
                metatron_score = 0.5

            # Vesica Piscis: cross-element pair boost
            vesica_score = 1.0
            bk = bridge_key(query.home_face, doc_face)
            if bk in VESICA_PAIRS:
                vp = VESICA_PAIRS[bk]
                vesica_score = 1.0 + 0.1 * vp["boost"]

            # Combine with geometric mean (preserves discrimination)
            sacred = (platonic_score * flower_score * metatron_score) ** (1.0 / 3)
            sacred *= vesica_score

            filtered[doc_id] = base_score * sacred

        return filtered

    # ── Layer 5: MOMENTUM MODULATION ──────────────────────────────────

    def _momentum_modulate(self, scores: dict[str, float],
                           docs: list[dict]) -> dict[str, float]:
        """Modulate scores by the momentum field.

        This is the ONLY place where learned state enters computation.
        Water candidates get stable momentum (0.5).
        Air candidates get dynamic momentum (highest).
        """
        modulated = {}
        for doc in docs:
            doc_id = doc.get("id", "")
            doc_face = ELEMENT_TO_FACE.get(doc.get("element", "Earth"), "S")
            doc_shell = self._doc_to_shell(doc)

            m = self.momentum.get_momentum(doc_face, doc_shell)
            # Momentum as multiplicative boost: m > 1 amplifies, m < 1 dampens
            # Scaled so typical momentum (~3-5) gives ~1.1-1.3x boost
            boost = 1.0 + 0.05 * (m - 1.0)
            modulated[doc_id] = scores.get(doc_id, 0.0) * boost

        return modulated

    # ── Layer 6: COMMIT ───────────────────────────────────────────────

    def _commit(self, query: QueryState, scores: dict[str, float],
                docs: list[dict], idf: _IdfTable,
                max_results: int) -> ForwardResult:
        """Final ranking, resonance/desire/action, and 4-gate commit."""
        doc_lookup = {d.get("id", ""): d for d in docs}

        # Sort by score
        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        ranked = []

        for doc_id in sorted_ids[:max_results * 2]:
            doc = doc_lookup.get(doc_id)
            if not doc:
                continue

            score = scores.get(doc_id, 0.0)
            doc_face = ELEMENT_TO_FACE.get(doc.get("element", "Earth"), "S")
            doc_shell = self._doc_to_shell(doc)

            # Resonance: geometric quality of the match
            # Shell proximity + token overlap + element coherence + momentum stability
            shell_fit = max(0.0, 1.0 - abs(doc_shell - query.home_shell) / TOTAL_SHELLS)
            token_fit = idf.tfidf_score(query.tokens, doc.get("tokens", []))
            element_fit = PHI_INV if doc_face == query.home_face else PHI_INV2
            mom_stability = 1.0 / (1.0 + abs(
                self.momentum.get_momentum(doc_face, doc_shell) - ATTRACTOR["water_momentum"]
            ) * 0.1)
            resonance = (shell_fit + token_fit + element_fit + mom_stability) / 4

            # Desire: alignment with query intent
            q_tokens = set(query.tokens)
            d_tokens = set(doc.get("tokens", []))
            recall = len(q_tokens & d_tokens) / max(len(q_tokens), 1)
            # Cross-element exploration bonus
            explore = 0.3 if doc_face != query.home_face else 0.0
            desire = recall * 0.7 + explore * 0.3

            # Action: minimize
            kinetic = max(0.0, 1.0 - score)
            action = kinetic - desire

            # Path contributions from E8 root proximities
            path_contribs = {f: 0.0 for f in FACES}
            path_contribs[doc_face] = score
            # Add bridge contributions
            bk = bridge_key(query.home_face, doc_face)
            bw = BRIDGE_WEIGHTS.get(bk, 0.382)
            path_contribs[query.home_face] = score * bw

            ranked.append(RankedCandidate(
                doc_id=doc_id,
                doc_name=doc.get("display_name", doc.get("name", doc_id))[:100],
                element=doc.get("element", "unknown"),
                gate=doc.get("gate", "G00"),
                shell=doc_shell,
                merged_score=score,
                action=action,
                resonance=resonance,
                desire=desire,
                path_contributions=path_contribs,
            ))

        # Sort by action (minimize)
        ranked.sort(key=lambda c: c.action)
        ranked = ranked[:max_results]

        # Overall resonance and commit witness
        overall_resonance = sum(c.resonance for c in ranked) / max(len(ranked), 1)

        commit = CommitWitness(
            resonance_gate=overall_resonance >= self.RESONANCE_THRESHOLD,
            boundary_gate=all(1 <= c.shell <= TOTAL_SHELLS for c in ranked),
            crossview_gate=len(set(c.element for c in ranked)) >= 2,
            scale_gate=all(c.resonance > 0.1 for c in ranked),
        )
        commit.committed = all([
            commit.resonance_gate,
            commit.boundary_gate,
            commit.crossview_gate,
            commit.scale_gate,
        ])
        commit.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        # SFCR score summary
        sfcr_summary = {f: {} for f in FACES}
        for c in ranked[:5]:
            sfcr_summary[ELEMENT_TO_FACE.get(c.element, "S")][c.doc_id] = c.merged_score

        cross_pairs = []
        for c in ranked[:10]:
            bk = bridge_key(query.home_face, ELEMENT_TO_FACE.get(c.element, "S"))
            if bk in GOLDEN_BRIDGES:
                cross_pairs.append(f"{bk}:{c.doc_id}")

        return ForwardResult(
            query=query,
            candidates=ranked,
            resonance=overall_resonance,
            committed=commit.committed,
            commit_witness=commit,
            sfcr_scores=sfcr_summary,
            elapsed_ms=0,  # set by caller
            cross_element_pairs_used=cross_pairs[:20],
        )

    # ── Main Forward Pass ─────────────────────────────────────────────

    # Maximum docs to pass through the expensive E8-240 scoring layer
    E8_CANDIDATE_LIMIT = 200

    def _tfidf_prefilter(self, docs: list[dict], idf: _IdfTable,
                         query: QueryState) -> list[dict]:
        """Pre-filter docs by TF-IDF token relevance before expensive E8 scoring.

        Uses the inverted index for O(query_tokens × avg_postings) lookup
        instead of scanning all 14,730+ docs linearly.
        """
        # Get candidate indices via inverted index (fast)
        candidate_indices = idf.candidate_doc_indices(query.tokens)
        if not candidate_indices:
            return []

        # Score only the candidates
        scored = []
        for idx in candidate_indices:
            if idx < len(docs):
                doc = docs[idx]
                tfidf = idf.tfidf_score(query.tokens, doc.get("tokens", []))
                scored.append((doc, tfidf))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [d for d, _ in scored[:self.E8_CANDIDATE_LIMIT]]

    def forward(self, query: str | QueryState, max_results: int = 10) -> ForwardResult:
        """Full geometric forward pass: 6 layers through sacred geometry."""
        t0 = time.time()

        # Layer 1: Project query to 4D
        if isinstance(query, str):
            qs = self._project_query(query)
        else:
            qs = query

        docs = self.doc_registry
        if not docs:
            return ForwardResult(query=qs, elapsed_ms=0)

        # Cache IDF table — docs don't change during training
        if self._idf_cache is None:
            self._idf_cache = _IdfTable(docs)
        idf = self._idf_cache

        # Pre-filter: narrow to top candidates by token relevance
        candidate_docs = self._tfidf_prefilter(docs, idf, qs)
        if not candidate_docs:
            return ForwardResult(query=qs, elapsed_ms=(time.time() - t0) * 1000)

        # Layer 2: Sigma-60 rotation
        views_60 = self._sigma_rotate(qs.q_4d or {f: 0.25 for f in FACES})
        centroids = self._archetype_centroids(views_60)

        # Layer 3: E8-240 expansion + doc scoring (on filtered candidates only)
        e8_scores = self._e8_score_docs(views_60, candidate_docs, idf, qs)

        # Layer 4: Sacred geometry filter
        sacred_scores = self._sacred_filter(e8_scores, candidate_docs, qs, centroids)

        # Layer 5: Momentum modulation
        final_scores = self._momentum_modulate(sacred_scores, candidate_docs)

        # Layer 6: Commit
        result = self._commit(qs, final_scores, candidate_docs, idf, max_results)
        result.elapsed_ms = (time.time() - t0) * 1000

        return result

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _doc_to_shell(doc: dict) -> int:
        """Get shell number for a doc."""
        if "_shell" in doc:
            return doc["_shell"]
        doc_id = doc.get("id", "DOC0000")
        try:
            num = int(doc_id.replace("DOC", ""))
        except (ValueError, AttributeError):
            num = 0
        return (num % TOTAL_SHELLS) + 1


# ── Module-level singleton ────────────────────────────────────────────

_engine: Optional[GeometricEngine] = None


def get_engine() -> GeometricEngine:
    """Get or create the global geometric engine singleton."""
    global _engine
    if _engine is None:
        _engine = GeometricEngine()
    return _engine


def reset_engine():
    """Reset the global singleton."""
    global _engine
    _engine = None
