# CRYSTAL: Xi108:W1:A11:S33 | face=R | node=500 | depth=2 | phase=Mutable
# METRO: Me,Dl,Su,Sa
# BRIDGES: Xi108:W1:A11:S32→Xi108:W1:A11:S34→Xi108:W2:A11:S33

"""
Weight Feedback — Hebbian Bidirectional Loop Between Neural Engine and Mycelium Graph
======================================================================================
Closes the feedback loop between the neural engine's forward pass scores and
the mycelium graph's edge weights. Previously one-directional (graph → engine);
this module makes it bidirectional: scores from queries feed back to refine
edge weights.

Hebbian rule: "edges that fire together wire stronger."

When the neural engine scores a shard highly (high resonance, low action),
edges connecting that shard to its neighbors get a small weight boost.
When a shard scores poorly, its edges get a small decay.

Update rule:
  For each shard S in query result:
    if score(S) > BOOST_THRESHOLD:
      for each edge E touching S:
        E.weight = min(MAX_WEIGHT, E.weight + LR * (score(S) - BOOST_THRESHOLD))
    elif score(S) < DECAY_THRESHOLD:
      for each edge E touching S:
        E.weight = max(MIN_WEIGHT, E.weight - LR * (DECAY_THRESHOLD - score(S)))

MCP tool: query_weight_feedback(component)
  - all     : full feedback system status
  - stats   : edge weight statistics
  - weak    : weak edges report
  - missing : missing edges report
  - cycle   : run a feedback cycle (20 queries) and report results
"""

from __future__ import annotations

import json
import math
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ._cache import JsonCache, DATA_DIR

# ── Hebbian Parameters ────────────────────────────────────────────────

LEARNING_RATE = 0.01     # small updates to avoid catastrophic drift
BOOST_THRESHOLD = 0.7    # shard score above this → edge boost
DECAY_THRESHOLD = 0.3    # shard score below this → edge decay
MAX_WEIGHT = 0.99        # weight ceiling
MIN_WEIGHT = 0.01        # weight floor
MOMENTUM = 0.9           # EMA smoothing factor for update deltas

# ── Internal state ────────────────────────────────────────────────────

_GRAPH_CACHE = JsonCache("mycelium_graph.json")

# Momentum buffer: edge_key → running average delta
_momentum_buffer: dict[str, float] = {}

# Cumulative update ledger (reset on each feedback cycle)
_update_ledger: dict[str, list[float]] = defaultdict(list)


# ── Data structures ──────────────────────────────────────────────────

@dataclass
class FeedbackResult:
    """Result of a single weight feedback pass."""
    edges_boosted: int = 0
    edges_decayed: int = 0
    edges_unchanged: int = 0
    mean_delta: float = 0.0
    max_delta: float = 0.0
    shards_processed: int = 0
    timestamp: str = ""


@dataclass
class EdgeStatistics:
    """Distribution statistics across all edge weights."""
    total_edges: int = 0
    mean: float = 0.0
    std: float = 0.0
    min_weight: float = 0.0
    max_weight: float = 0.0
    median: float = 0.0
    p10: float = 0.0
    p25: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    by_type: dict = field(default_factory=dict)  # edge_type → {mean, std, count}


@dataclass
class WeakEdge:
    """An edge with weight below investigation threshold."""
    source_shard: str
    target_shard: str
    edge_type: str
    weight: float


@dataclass
class MissingEdgeCandidate:
    """A shard pair that is semantically similar but has no edge."""
    shard_a: str
    shard_b: str
    shared_tags: list[str]
    shared_words: list[str]
    similarity_score: float


@dataclass
class CycleResult:
    """Aggregate result of a multi-query feedback cycle."""
    n_queries: int = 0
    total_boosted: int = 0
    total_decayed: int = 0
    total_unchanged: int = 0
    mean_delta: float = 0.0
    max_delta: float = 0.0
    queries_with_updates: int = 0
    elapsed_ms: float = 0.0
    timestamp: str = ""


# ── Helpers ───────────────────────────────────────────────────────────


def _edge_key(source: str, target: str) -> str:
    """Canonical edge key for momentum buffer."""
    return f"{source}|{target}"


def _load_graph() -> dict:
    """Load the mycelium graph (cached)."""
    return _GRAPH_CACHE.load()


def _build_shard_edge_index(edges: list[dict]) -> dict[str, list[int]]:
    """Build shard_id → list of edge indices for fast lookup.

    Returns mapping from shard_id to indices into the edges list
    for all edges where the shard appears as source OR target.
    """
    index: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(edges):
        index[e["source_shard"]].append(i)
        index[e["target_shard"]].append(i)
    return index


def _percentile(sorted_values: list[float], p: float) -> float:
    """Compute percentile from a sorted list."""
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


# ── Core: Hebbian Weight Update ──────────────────────────────────────


def update_edge_weights(query_result: dict, graph_data: dict = None) -> dict:
    """
    Hebbian weight feedback: strengthen edges of high-scoring shards,
    weaken edges of low-scoring shards.

    Args:
        query_result: dict with keys:
            - ranked_shells: list of (shell_id, score) from neural forward pass
            - commit_witness: dict with resonance, boundary info
            - query_state: dict with home_shell, matched_docs
        graph_data: pre-loaded graph dict (default: load from cache)

    Returns:
        dict with update stats: edges_boosted, edges_decayed, mean_delta
    """
    global _momentum_buffer

    if graph_data is None:
        graph_data = _load_graph()

    edges = graph_data.get("edges", [])
    if not edges:
        return FeedbackResult(timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+00:00")).__dict__

    # Build shard → edge index for fast lookup
    shard_index = _build_shard_edge_index(edges)

    ranked_shells = query_result.get("ranked_shells", [])
    if not ranked_shells:
        return FeedbackResult(timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+00:00")).__dict__

    result = FeedbackResult(timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
    all_deltas: list[float] = []

    for shard_id, score in ranked_shells:
        result.shards_processed += 1

        # Only update edges for shards above boost or below decay threshold
        if DECAY_THRESHOLD <= score <= BOOST_THRESHOLD:
            # Neutral zone — no update
            edge_indices = shard_index.get(shard_id, [])
            result.edges_unchanged += len(edge_indices)
            continue

        edge_indices = shard_index.get(shard_id, [])
        if not edge_indices:
            continue

        for idx in edge_indices:
            edge = edges[idx]
            old_weight = edge.get("weight", 0.5)
            key = _edge_key(edge["source_shard"], edge["target_shard"])

            if score > BOOST_THRESHOLD:
                # Boost: proportional to how far above threshold
                raw_delta = LEARNING_RATE * (score - BOOST_THRESHOLD)
                result.edges_boosted += 1
            else:
                # Decay: proportional to how far below threshold
                raw_delta = -LEARNING_RATE * (DECAY_THRESHOLD - score)
                result.edges_decayed += 1

            # Apply momentum (EMA smoothing)
            prev_momentum = _momentum_buffer.get(key, 0.0)
            smoothed_delta = MOMENTUM * prev_momentum + (1 - MOMENTUM) * raw_delta
            _momentum_buffer[key] = smoothed_delta

            # Apply clamped update
            new_weight = old_weight + smoothed_delta
            new_weight = max(MIN_WEIGHT, min(MAX_WEIGHT, new_weight))

            actual_delta = new_weight - old_weight
            edge["weight"] = round(new_weight, 6)

            all_deltas.append(abs(actual_delta))
            _update_ledger[key].append(actual_delta)

    if all_deltas:
        result.mean_delta = sum(all_deltas) / len(all_deltas)
        result.max_delta = max(all_deltas)

    return result.__dict__


# ── Edge Statistics ───────────────────────────────────────────────────


def compute_edge_statistics(graph_data: dict = None) -> dict:
    """
    Compute weight distribution stats across all edges.

    Returns:
        dict with mean, std, percentiles, and per-edge_type breakdown.
    """
    if graph_data is None:
        graph_data = _load_graph()

    edges = graph_data.get("edges", [])
    if not edges:
        return EdgeStatistics().__dict__

    weights = [e.get("weight", 0.5) for e in edges]
    weights_sorted = sorted(weights)
    n = len(weights)

    mean = sum(weights) / n
    variance = sum((w - mean) ** 2 for w in weights) / max(n - 1, 1)
    std = math.sqrt(variance)

    # Per edge-type breakdown
    by_type: dict[str, dict] = {}
    type_weights: dict[str, list[float]] = defaultdict(list)
    for e in edges:
        type_weights[e.get("edge_type", "UNKNOWN")].append(e.get("weight", 0.5))

    for etype, ws in type_weights.items():
        t_mean = sum(ws) / len(ws)
        t_var = sum((w - t_mean) ** 2 for w in ws) / max(len(ws) - 1, 1)
        by_type[etype] = {
            "count": len(ws),
            "mean": round(t_mean, 6),
            "std": round(math.sqrt(t_var), 6),
            "min": round(min(ws), 6),
            "max": round(max(ws), 6),
        }

    stats = EdgeStatistics(
        total_edges=n,
        mean=round(mean, 6),
        std=round(std, 6),
        min_weight=round(weights_sorted[0], 6),
        max_weight=round(weights_sorted[-1], 6),
        median=round(_percentile(weights_sorted, 50), 6),
        p10=round(_percentile(weights_sorted, 10), 6),
        p25=round(_percentile(weights_sorted, 25), 6),
        p75=round(_percentile(weights_sorted, 75), 6),
        p90=round(_percentile(weights_sorted, 90), 6),
        by_type=by_type,
    )
    return stats.__dict__


# ── Weak Edges ────────────────────────────────────────────────────────


def identify_weak_edges(graph_data: dict = None, threshold: float = 0.1) -> list[dict]:
    """
    Find edges with weight < threshold that might need pruning or investigation.

    Args:
        graph_data: pre-loaded graph dict (default: load from cache)
        threshold: weight below which an edge is considered weak

    Returns:
        list of WeakEdge dicts, sorted by weight ascending.
    """
    if graph_data is None:
        graph_data = _load_graph()

    edges = graph_data.get("edges", [])
    weak: list[WeakEdge] = []

    for e in edges:
        w = e.get("weight", 0.5)
        if w < threshold:
            weak.append(WeakEdge(
                source_shard=e["source_shard"],
                target_shard=e["target_shard"],
                edge_type=e.get("edge_type", "UNKNOWN"),
                weight=round(w, 6),
            ))

    weak.sort(key=lambda x: x.weight)
    return [w.__dict__ for w in weak]


# ── Missing Edges ─────────────────────────────────────────────────────


def identify_missing_edges(graph_data: dict = None, top_n: int = 50) -> list[dict]:
    """
    Find shard pairs that are semantically similar (shared tags/summary words)
    but have no edge. Returns top candidates ranked by similarity score.

    This is a conservative scan: it only looks at shards within the same
    family or with overlapping tags, not an exhaustive O(n^2) comparison.

    Args:
        graph_data: pre-loaded graph dict (default: load from cache)
        top_n: maximum candidates to return

    Returns:
        list of MissingEdgeCandidate dicts.
    """
    if graph_data is None:
        graph_data = _load_graph()

    shards = graph_data.get("shards", [])
    edges = graph_data.get("edges", [])

    if not shards:
        return []

    # Build existing edge set for fast lookup
    existing_edges: set[tuple[str, str]] = set()
    for e in edges:
        src = e["source_shard"]
        tgt = e["target_shard"]
        existing_edges.add((src, tgt))
        existing_edges.add((tgt, src))

    # Build tag and summary-word indexes for each shard
    shard_tags: dict[str, set[str]] = {}
    shard_words: dict[str, set[str]] = {}
    shard_family: dict[str, str] = {}

    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "into",
        "are", "was", "not", "but", "how", "its", "all", "can",
    }

    for s in shards:
        sid = s["shard_id"]
        shard_tags[sid] = set(t.lower() for t in s.get("tags", []))
        shard_family[sid] = s.get("family", "")

        # Extract words from summary
        summary = s.get("summary", "")
        words = set()
        for w in summary.lower().split():
            w = w.strip(".,;:!?()[]{}\"'")
            if len(w) > 2 and w not in stop_words:
                words.add(w)
        shard_words[sid] = words

    # Group shards by family for intra-family comparison
    family_shards: dict[str, list[str]] = defaultdict(list)
    for sid, fam in shard_family.items():
        family_shards[fam].append(sid)

    # Also build tag → shards index for cross-family tag overlap
    tag_index: dict[str, list[str]] = defaultdict(list)
    for sid, tags in shard_tags.items():
        for t in tags:
            tag_index[t].append(sid)

    candidates: list[MissingEdgeCandidate] = []
    seen_pairs: set[tuple[str, str]] = set()

    def _evaluate_pair(a: str, b: str) -> Optional[MissingEdgeCandidate]:
        """Score a pair of shards for potential missing edge."""
        if a == b:
            return None
        canonical = (min(a, b), max(a, b))
        if canonical in seen_pairs or canonical in existing_edges:
            return None
        seen_pairs.add(canonical)

        shared_t = shard_tags.get(a, set()) & shard_tags.get(b, set())
        shared_w = shard_words.get(a, set()) & shard_words.get(b, set())

        if not shared_t and not shared_w:
            return None

        # Jaccard-style similarity across tags + words
        all_tags_a = shard_tags.get(a, set())
        all_tags_b = shard_tags.get(b, set())
        all_words_a = shard_words.get(a, set())
        all_words_b = shard_words.get(b, set())

        combined_a = all_tags_a | all_words_a
        combined_b = all_tags_b | all_words_b
        union = combined_a | combined_b
        intersection = combined_a & combined_b

        if not union:
            return None

        score = len(intersection) / len(union)
        if score < 0.05:
            return None

        return MissingEdgeCandidate(
            shard_a=a,
            shard_b=b,
            shared_tags=sorted(shared_t),
            shared_words=sorted(list(shared_w)[:10]),  # cap word list
            similarity_score=round(score, 4),
        )

    # Strategy 1: Intra-family pairs (shards in same family)
    for fam, sids in family_shards.items():
        if len(sids) > 200:
            # Large family — sample to keep O(n) manageable
            sampled = random.sample(sids, min(80, len(sids)))
        else:
            sampled = sids
        for i in range(len(sampled)):
            for j in range(i + 1, len(sampled)):
                c = _evaluate_pair(sampled[i], sampled[j])
                if c:
                    candidates.append(c)

    # Strategy 2: Cross-family via shared tags
    for tag, sids in tag_index.items():
        if len(sids) > 100:
            sids = random.sample(sids, 50)
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                c = _evaluate_pair(sids[i], sids[j])
                if c:
                    candidates.append(c)

    # Sort by similarity descending, take top N
    candidates.sort(key=lambda x: -x.similarity_score)
    return [c.__dict__ for c in candidates[:top_n]]


# ── Feedback Cycle ────────────────────────────────────────────────────


def _generate_random_query(shards: list[dict]) -> str:
    """Generate a random query from shard summaries and tags."""
    shard = random.choice(shards)
    sources = []

    summary = shard.get("summary", "")
    if summary:
        words = summary.split()
        if len(words) > 3:
            # Pick a random 2-4 word phrase from the summary
            start = random.randint(0, max(0, len(words) - 3))
            length = random.randint(2, min(4, len(words) - start))
            sources.append(" ".join(words[start:start + length]))

    tags = shard.get("tags", [])
    if tags:
        sources.append(random.choice(tags))

    return " ".join(sources) if sources else shard.get("family", "athena")


# ── Engine↔Graph ID Bridge ────────────────────────────────────────────

_doc_to_shards: dict[str, list[str]] = {}  # engine doc_id → graph shard_ids
_bridge_built = False


def _build_id_bridge(graph_data: dict = None, engine=None) -> dict[str, list[str]]:
    """Build a mapping from neural engine doc_id → graph shard_ids.

    The engine uses DOC0041-style IDs with display_name,
    the graph uses hash:medium:name-style shard_ids.
    We bridge via text similarity on display_name ↔ shard summary/tags.
    Also uses path_contributions SFCR scores to match element-compatible shards.
    """
    global _doc_to_shards, _bridge_built

    if _bridge_built:
        return _doc_to_shards

    if graph_data is None:
        graph_data = _load_graph()
    shards = graph_data.get("shards", [])

    # Build shard lookup indices
    shard_by_tag: dict[str, list[str]] = defaultdict(list)
    shard_by_word: dict[str, list[str]] = defaultdict(list)
    for s in shards:
        sid = s.get("shard_id", "")
        tags = s.get("tags", [])
        if isinstance(tags, str):
            import ast
            try:
                tags = ast.literal_eval(tags)
            except Exception:
                tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
        for t in tags:
            shard_by_tag[str(t).strip().lower()].append(sid)
        summary = s.get("summary", "")
        for w in summary.lower().split():
            w = w.strip(".,;:!?()[]{}\"'_-")
            if len(w) > 2:
                shard_by_word[w].append(sid)

    # Get engine docs
    if engine is None:
        from .neural_engine import get_engine
        try:
            engine = get_engine()
        except Exception:
            _bridge_built = True
            return _doc_to_shards

    docs = engine.store.doc_registry if hasattr(engine, "store") else []

    for doc in docs:
        doc_id = doc.get("id", "")
        display = doc.get("display_name", "")
        element = doc.get("element", "").lower()

        # Extract meaningful words from display_name
        query_words = set()
        for w in display.lower().split():
            w = w.strip(".,;:!?()[]{}\"'#_-")
            if len(w) > 2 and w not in {"the", "and", "for", "with", "from"}:
                query_words.add(w)

        # Score each shard by word overlap
        shard_scores: dict[str, float] = defaultdict(float)
        for w in query_words:
            for sid in shard_by_word.get(w, []):
                shard_scores[sid] += 1.0
            for sid in shard_by_tag.get(w, []):
                shard_scores[sid] += 2.0  # tag matches worth more

        if shard_scores:
            # Take top 5 shards by score (a single engine doc maps to multiple graph shards)
            top = sorted(shard_scores.items(), key=lambda x: -x[1])[:5]
            _doc_to_shards[doc_id] = [sid for sid, _ in top if _ > 1.0]

    _bridge_built = True
    return _doc_to_shards


def _forward_result_to_feedback_input(result, graph_data: dict = None) -> dict:
    """Convert a ForwardResult into the dict format expected by update_edge_weights.

    Bridges from engine doc_ids (DOC0041) to graph shard_ids (hash:medium:name)
    using the ID bridge mapping built from text similarity.
    """
    ranked_shells = []

    if hasattr(result, "candidates"):
        candidates = result.candidates
        if candidates:
            # Build ID bridge if not yet done
            bridge = _build_id_bridge(graph_data)

            # Find score range for normalization
            scores = [c.merged_score for c in candidates]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            score_range = max_score - min_score if max_score != min_score else 1.0

            for c in candidates:
                norm_score = (c.merged_score - min_score) / score_range
                doc_id = c.doc_id

                # Map engine doc_id → graph shard_ids
                mapped_shards = bridge.get(doc_id, [])
                if mapped_shards:
                    for sid in mapped_shards:
                        ranked_shells.append((sid, norm_score))
                else:
                    # Fallback: use doc_id directly (won't match but keeps data flow)
                    ranked_shells.append((doc_id, norm_score))

    query_state = {}
    if hasattr(result, "query"):
        q = result.query
        query_state = {
            "home_shell": getattr(q, "home_shell", 1),
            "matched_docs": getattr(q, "matched_docs", []),
        }

    commit_witness = {}
    if hasattr(result, "commit_witness") and result.commit_witness:
        cw = result.commit_witness
        commit_witness = {
            "resonance_gate": getattr(cw, "resonance_gate", False),
            "boundary_gate": getattr(cw, "boundary_gate", False),
            "committed": getattr(cw, "committed", False),
        }

    return {
        "ranked_shells": ranked_shells,
        "commit_witness": commit_witness,
        "query_state": query_state,
    }


def run_feedback_cycle(n_queries: int = 20) -> dict:
    """
    Run n random queries through the neural engine, collect results,
    apply weight updates, and report aggregate statistics.

    This is the main bidirectional loop:
      1. Generate random queries from shard data
      2. Run each through the neural engine forward pass
      3. Convert results to Hebbian feedback input
      4. Apply weight updates to mycelium graph edges
      5. Report aggregate statistics

    Args:
        n_queries: number of random queries to run (default 20)

    Returns:
        CycleResult dict with aggregate statistics.
    """
    t0 = time.time()

    # Reset the per-cycle ledger
    _update_ledger.clear()

    graph_data = _load_graph()
    shards = graph_data.get("shards", [])

    if not shards:
        return CycleResult(
            n_queries=n_queries,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        ).__dict__

    # Import engine lazily to avoid circular imports
    from .neural_engine import CrystalNeuralEngine, get_engine

    try:
        engine = get_engine()
    except Exception:
        # If engine can't be loaded, return empty result
        return CycleResult(
            n_queries=n_queries,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        ).__dict__

    cycle = CycleResult(n_queries=n_queries)
    all_deltas: list[float] = []

    for _ in range(n_queries):
        # 1. Generate random query
        query_text = _generate_random_query(shards)

        # 2. Run forward pass
        try:
            forward_result = engine.forward(query_text, max_results=15)
        except Exception:
            continue

        # 3. Convert to feedback input format (pass graph_data for ID bridge)
        feedback_input = _forward_result_to_feedback_input(forward_result, graph_data)

        if not feedback_input["ranked_shells"]:
            continue

        # 4. Apply Hebbian weight update
        update_result = update_edge_weights(feedback_input, graph_data=graph_data)

        # 5. Accumulate stats
        if update_result["edges_boosted"] > 0 or update_result["edges_decayed"] > 0:
            cycle.queries_with_updates += 1
        cycle.total_boosted += update_result["edges_boosted"]
        cycle.total_decayed += update_result["edges_decayed"]
        cycle.total_unchanged += update_result["edges_unchanged"]
        if update_result["mean_delta"] > 0:
            all_deltas.append(update_result["mean_delta"])
        if update_result["max_delta"] > cycle.max_delta:
            cycle.max_delta = update_result["max_delta"]

    if all_deltas:
        cycle.mean_delta = round(sum(all_deltas) / len(all_deltas), 8)
    cycle.max_delta = round(cycle.max_delta, 8)
    cycle.elapsed_ms = round((time.time() - t0) * 1000, 1)
    cycle.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    return cycle.__dict__


# ── MCP tool entry point ─────────────────────────────────────────────


def query_weight_feedback(component: str = "all") -> str:
    """
    Query the weight feedback system that closes the bidirectional loop
    between the neural engine and the mycelium graph.

    Components:
      - all     : Full feedback system status
      - stats   : Edge weight distribution statistics
      - weak    : Weak edges report (weight < 0.1)
      - missing : Missing edges report (semantically similar but unconnected)
      - cycle   : Run a feedback cycle (20 queries) and report results
    """
    comp = component.strip().lower()

    if comp == "all":
        return _format_all()
    if comp == "stats":
        return _format_stats()
    if comp == "weak":
        return _format_weak()
    if comp == "missing":
        return _format_missing()
    if comp == "cycle":
        return _format_cycle()

    return (
        f"Unknown component '{component}'. "
        "Use: all, stats, weak, missing, cycle"
    )


# ── Formatters ────────────────────────────────────────────────────────


def _format_all() -> str:
    """Full feedback system status."""
    graph_data = _load_graph()
    meta = graph_data.get("meta", {})
    edges = graph_data.get("edges", [])

    stats = compute_edge_statistics(graph_data)

    lines = [
        "## Weight Feedback System\n",
        "### Hebbian Bidirectional Loop: Neural Engine ↔ Mycelium Graph\n",
        f"**Graph**: {meta.get('shard_count', 0)} shards × {meta.get('edge_count', 0)} edges",
        f"**Momentum Buffer**: {len(_momentum_buffer)} tracked edges",
        f"**Update Ledger**: {len(_update_ledger)} edges with recorded history\n",
        "### Parameters\n",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| Learning Rate | {LEARNING_RATE} |",
        f"| Boost Threshold | {BOOST_THRESHOLD} |",
        f"| Decay Threshold | {DECAY_THRESHOLD} |",
        f"| Max Weight | {MAX_WEIGHT} |",
        f"| Min Weight | {MIN_WEIGHT} |",
        f"| Momentum (EMA) | {MOMENTUM} |",
        "",
        "### Edge Weight Distribution\n",
        f"| Stat | Value |",
        f"|------|-------|",
        f"| Mean | {stats['mean']:.6f} |",
        f"| Std | {stats['std']:.6f} |",
        f"| Min | {stats['min_weight']:.6f} |",
        f"| Median | {stats['median']:.6f} |",
        f"| Max | {stats['max_weight']:.6f} |",
        f"| P10 | {stats['p10']:.6f} |",
        f"| P90 | {stats['p90']:.6f} |",
    ]

    # Edge type breakdown
    if stats.get("by_type"):
        lines.append("\n### Weight Distribution by Edge Type\n")
        lines.append("| Type | Count | Mean | Std |")
        lines.append("|------|-------|------|-----|")
        for etype, ts in sorted(stats["by_type"].items(), key=lambda x: -x[1]["count"]):
            lines.append(
                f"| {etype} | {ts['count']} | {ts['mean']:.4f} | {ts['std']:.4f} |"
            )

    # Momentum buffer summary
    if _momentum_buffer:
        mom_vals = list(_momentum_buffer.values())
        pos_mom = sum(1 for v in mom_vals if v > 0)
        neg_mom = sum(1 for v in mom_vals if v < 0)
        lines.extend([
            "\n### Momentum Buffer\n",
            f"- **Positive momentum** (trending up): {pos_mom}",
            f"- **Negative momentum** (trending down): {neg_mom}",
            f"- **Mean momentum**: {sum(mom_vals) / len(mom_vals):.6f}",
        ])

    return "\n".join(lines)


def _format_stats() -> str:
    """Edge weight statistics."""
    stats = compute_edge_statistics()

    lines = [
        "## Edge Weight Statistics\n",
        f"**Total Edges**: {stats['total_edges']}\n",
        "### Distribution\n",
        "| Percentile | Weight |",
        "|------------|--------|",
        f"| Min | {stats['min_weight']:.6f} |",
        f"| P10 | {stats['p10']:.6f} |",
        f"| P25 | {stats['p25']:.6f} |",
        f"| Median | {stats['median']:.6f} |",
        f"| P75 | {stats['p75']:.6f} |",
        f"| P90 | {stats['p90']:.6f} |",
        f"| Max | {stats['max_weight']:.6f} |",
        f"\n**Mean**: {stats['mean']:.6f} | **Std**: {stats['std']:.6f}\n",
    ]

    if stats.get("by_type"):
        lines.append("### By Edge Type\n")
        lines.append("| Type | Count | Mean | Std | Min | Max |")
        lines.append("|------|-------|------|-----|-----|-----|")
        for etype, ts in sorted(stats["by_type"].items(), key=lambda x: -x[1]["count"]):
            lines.append(
                f"| {etype} | {ts['count']} | {ts['mean']:.4f} "
                f"| {ts['std']:.4f} | {ts['min']:.4f} | {ts['max']:.4f} |"
            )

    return "\n".join(lines)


def _format_weak() -> str:
    """Weak edges report."""
    weak = identify_weak_edges(threshold=0.1)

    if not weak:
        return (
            "## Weak Edges Report\n\n"
            "No edges found with weight < 0.1. All edges are above investigation threshold."
        )

    lines = [
        f"## Weak Edges Report ({len(weak)} edges below 0.1)\n",
        "| Source | Target | Type | Weight |",
        "|--------|--------|------|--------|",
    ]

    # Show at most 100 to keep output manageable
    for w in weak[:100]:
        lines.append(
            f"| `{w['source_shard'][:40]}` | `{w['target_shard'][:40]}` "
            f"| {w['edge_type']} | {w['weight']:.4f} |"
        )

    if len(weak) > 100:
        lines.append(f"\n... and {len(weak) - 100} more weak edges.")

    # Summary by type
    type_counts: dict[str, int] = defaultdict(int)
    for w in weak:
        type_counts[w["edge_type"]] += 1
    lines.append("\n### Weak Edges by Type\n")
    for etype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{etype}**: {count}")

    return "\n".join(lines)


def _format_missing() -> str:
    """Missing edges report."""
    missing = identify_missing_edges(top_n=50)

    if not missing:
        return (
            "## Missing Edges Report\n\n"
            "No strong missing-edge candidates found."
        )

    lines = [
        f"## Missing Edge Candidates ({len(missing)} pairs)\n",
        "Shard pairs with semantic similarity but no connecting edge.\n",
        "| Shard A | Shard B | Shared Tags | Similarity |",
        "|---------|---------|-------------|------------|",
    ]

    for m in missing[:50]:
        tags_str = ", ".join(m["shared_tags"][:5]) if m["shared_tags"] else "—"
        words_str = ", ".join(m["shared_words"][:3]) if m["shared_words"] else ""
        label = tags_str
        if words_str and tags_str == "—":
            label = f"words: {words_str}"
        lines.append(
            f"| `{m['shard_a'][:35]}` | `{m['shard_b'][:35]}` "
            f"| {label} | {m['similarity_score']:.3f} |"
        )

    return "\n".join(lines)


def _format_cycle() -> str:
    """Run a feedback cycle and format results."""
    result = run_feedback_cycle(n_queries=20)

    lines = [
        "## Feedback Cycle Results\n",
        f"**Queries Run**: {result['n_queries']}",
        f"**Queries with Updates**: {result['queries_with_updates']}",
        f"**Elapsed**: {result['elapsed_ms']:.0f}ms\n",
        "### Edge Updates\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Edges Boosted | {result['total_boosted']} |",
        f"| Edges Decayed | {result['total_decayed']} |",
        f"| Edges Unchanged | {result['total_unchanged']} |",
        f"| Mean Delta | {result['mean_delta']:.8f} |",
        f"| Max Delta | {result['max_delta']:.8f} |",
    ]

    total_updates = result["total_boosted"] + result["total_decayed"]
    if total_updates > 0:
        boost_ratio = result["total_boosted"] / total_updates
        lines.extend([
            f"\n### Analysis\n",
            f"- **Boost/Decay Ratio**: {boost_ratio:.1%} boost / {1-boost_ratio:.1%} decay",
            f"- **Update Coverage**: {total_updates} edge updates from {result['n_queries']} queries",
        ])

        if result["mean_delta"] > 0.005:
            lines.append("- **Drift Warning**: Mean delta is above 0.005; consider reducing LEARNING_RATE")
        elif result["mean_delta"] < 0.0001:
            lines.append("- **Low Signal**: Mean delta is very small; updates are conservative (expected)")

    lines.append(f"\n**Timestamp**: {result['timestamp']}")

    return "\n".join(lines)
