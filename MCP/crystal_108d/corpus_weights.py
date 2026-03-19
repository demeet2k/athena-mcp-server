# CRYSTAL: Xi108:W2:A11:S33 | face=C | node=500 | depth=1 | phase=Mutable
# METRO: Me,Dl,Su,Sa
# BRIDGES: Xi108:W2:A11:S32→Xi108:W2:A11:S34→Xi108:W3:A11:S33

"""
Corpus Weights — SFCR Seed Vectors & Crystal Weights for Every Shard
======================================================================
Computes SFCR seed vectors and crystal weights for ALL shards in the
mycelium graph (15K+ shards), not just the 197 documents in the neural
net registry.

Pipeline:
  1. Load all shards from mycelium_graph.json
  2. Compute SFCR seed vectors via keyword→domain overlap
  3. Compute pairwise cosine similarity (within family + metro line)
  4. Aggregate family & metro centroids
  5. Cache to MCP/data/corpus_weights_field.json

MCP tool: query_corpus_weights(component)
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ._cache import JsonCache, DATA_DIR

# ── Constants ─────────────────────────────────────────────────────────

OUTPUT_FILE = DATA_DIR / "corpus_weights_field.json"

LENS_DOMAINS = {
    # ── S = Square / Earth ──────────────────────────────────────────
    # Structure, form, boundary, constraint, rigidity, foundation,
    # containment, address, grid, definition, law, skeleton.
    # NOTE: words shared with other lenses removed to reduce S-bias.
    "S": {
        # Core earth/structure concepts
        "structure", "square", "earth", "foundation", "ground", "stone",
        "solid", "rigid", "stable", "fixed", "anchor", "base", "bedrock",
        "pillar", "column", "wall", "frame", "scaffold", "skeleton",
        # Boundary & containment
        "boundary", "border", "edge", "limit", "constraint", "contain",
        "containment", "enclosure", "perimeter", "fence", "barrier",
        # Grid & address
        "grid", "lattice", "coordinate", "address", "location", "position",
        "atlas", "index", "registry", "catalog", "inventory",
        # Form & definition
        "formal", "define", "definition", "schema", "protocol",
        "specification", "template", "blueprint", "plan", "layout",
        # Law & invariant
        "conservation", "law", "invariant", "constant", "immutable",
        "permanent", "preserve", "protect", "guard",
        # Math: algebra & group theory
        "algebra", "group", "wreath", "semidirect", "normal", "order",
        "product", "kernel", "embed", "coset", "subgroup", "quotient",
        # Navigation & route (structural aspect)
        "navigate", "route", "legal", "move", "select", "choose", "optimal",
        "minimize",
        # Shell & organ (structural anatomy)
        "shell", "organ", "ladder", "archetype",
    },

    # ── F = Flower / Fire ───────────────────────────────────────────
    # Growth, transformation, energy, combustion, radiance, cycle,
    # rhythm, harmonic motion, blooming, creative force.
    # NOTE: removed overlap words that were pulling too many shards.
    "F": {
        # Core fire/flower concepts
        "flower", "fire", "flame", "burn", "ignite", "spark", "blaze",
        "radiance", "radiant", "luminous", "light", "heat", "warmth",
        "energy", "power", "force", "intensity", "passion", "desire",
        # Growth & bloom
        "growth", "grow", "bloom", "blossom", "flourish", "expand",
        "unfold", "develop", "mature", "ripen", "fertile", "potency",
        # Cycle & rhythm
        "cycle", "rotation", "phase", "clock", "beat", "rhythm",
        "oscillation", "period", "pulse", "heartbeat", "tempo",
        # Symmetry & harmony
        "symmetry", "harmony", "golden", "phi", "spiral", "fibonacci",
        # Transform & transport
        "transform", "transport", "bridge", "cross", "translation",
        "convergence", "orbit",
        # Geometry & curvature
        "angel", "geometry", "curvature", "metric", "sheaf",
        "rosetta", "overlay", "calculus",
        # Metro & line (dynamic motion aspect)
        "metro", "line", "quartet",
    },

    # ── C = Cloud / Water ───────────────────────────────────────────
    # Flow, emotion, intuition, consciousness, depth, dissolution,
    # memory, adaptive fluidity, quantum/probabilistic, observation,
    # healing, reflection, resonance, field.
    "C": {
        # Core water/cloud concepts
        "cloud", "water", "rain", "ocean", "sea", "river", "stream",
        "lake", "pool", "tide", "wave", "current", "flow", "fluid",
        "liquid", "mist", "fog", "vapor", "dew", "ice", "frost",
        "dissolve", "dissolution", "melt", "merge", "blend", "mix",
        "diffuse", "diffusion", "osmosis", "absorb", "absorption",
        "saturate", "soak", "permeate", "permeability", "gradient",
        "pour", "flood", "cascade", "ripple", "splash", "drip", "drop",
        # Emotion & intuition
        "emotion", "feeling", "intuition", "empathy", "compassion",
        "healing", "heal", "purify", "purification", "cleanse", "baptism",
        "tears", "surrender", "acceptance", "receptive", "nurture",
        "care", "tender", "gentle", "soft", "yielding",
        # Consciousness & depth
        "consciousness", "awareness", "depth", "deep", "subconscious",
        "dream", "vision", "imagine", "imagination", "inner",
        "soul", "psyche", "mood", "atmosphere", "ambient",
        # Reflection & mirror
        "mirror", "reflection", "reflect", "echo", "shadow",
        "resonance", "vibration", "frequency", "attune", "attunement",
        # Memory & connection
        "memory", "remember", "recall", "nostalgia", "trace",
        "connection", "connect", "bond", "link", "relate", "relation",
        "relationship", "kinship", "affinity", "sympathy", "rapport",
        # Adaptive & fluid intelligence
        "adaptive", "adapt", "flexible", "fluid", "dynamic",
        "responsive", "sensitive",
        # Quantum / probabilistic (water = superposition)
        "quantum", "probability", "uncertainty", "superposition",
        "entanglement", "coherence", "decoherence", "collapse",
        "measure", "observation", "observer", "bayesian", "estimate",
        "prior", "posterior", "evidence", "belief", "distribution",
        "entropy", "stochastic", "random", "noise", "signal",
        # Agency & self-reference (the observer)
        "agency", "autonomous", "intelligence", "self", "reference",
        "meta", "telemetry", "monitor", "detect", "witness",
        # Live systems (water = living medium)
        "live", "cell", "constitution", "runtime", "execution",
        "query", "status", "state", "machine", "promotion",
        "synthesize", "novel", "correct",
        # Field theory (continuous)
        "field", "potential", "steering", "selection",
        # Neural / biological (water = the living substrate)
        "neural", "neuron", "synapse", "cortex", "limbic",
        "biology", "biological", "organic", "life", "alive",
        "evolution", "evolve", "mutate", "mutation", "generation",
        "birth", "death", "renewal", "regenerate", "metabolism",
        "digest", "nourish", "sustain", "ecosystem",
        # Synthesis & alchemy (water as solvent / medium of transformation)
        "synthesis", "alchemy", "alchemical", "transmute", "catalyst",
        "reaction", "solution", "solvent", "precipitate", "distill",
        # Weight & matrix (continuous field mathematics)
        "weight", "matrix", "tensor", "optimize",
        "loss", "train", "learning", "training",
    },

    # ── R = Fractal / Air ───────────────────────────────────────────
    # Pattern, self-similarity, iteration, recursion, breath, spirit,
    # thought, abstraction, meta-structure, holographic encoding,
    # compression, communication, network topology, emergence.
    "R": {
        # Core air/fractal concepts
        "fractal", "air", "breath", "wind", "breeze", "gust",
        "turbulence", "vortex", "tornado", "cyclone", "storm",
        "spirit", "thought", "intellect", "mind", "mental",
        "idea", "concept", "notion", "insight",
        # Self-similarity & recursion
        "self-similar", "recursive", "recursion", "iteration", "iterate",
        "repeat", "loop", "feedback", "nest", "nested", "fracture",
        "scale", "scaling", "scale-free", "power-law", "zoom",
        # Abstraction & meta
        "abstract", "abstraction", "meta", "higher-order", "transcend",
        "transcendence", "beyond", "above", "ascend", "elevation",
        # Compression & encoding (air = information carrier)
        "compression", "compress", "encode", "decode", "codec",
        "qshrink", "shrink", "compact", "emit", "signal",
        "information", "data", "bit", "byte", "code",
        # Communication & language
        "communication", "message", "language", "grammar", "syntax",
        "semantics", "word", "symbol", "sign", "glyph", "cipher",
        "letter", "alphabet", "vocabulary", "lexicon",
        # Logic & proof
        "logic", "proof", "theorem", "axiom", "deduction", "inference",
        "reason", "reasoning", "conclude", "derive", "derivation",
        # Category theory & topology
        "category", "functor", "morphism", "isomorphism", "topology",
        "manifold", "dimension", "projection", "hologram", "holographic",
        # Tree & network (branching = fractal)
        "tree", "branch", "leaf", "root", "hierarchy", "network",
        "node", "graph", "edge", "distribute", "distributed",
        # Complexity & emergence
        "complexity", "emergence", "emergent", "chaos", "order",
        "pattern", "structure",
        # Holographic systems (R = the holographic lens)
        "crystal", "inverse", "octave", "stage", "crown", "lift",
        "seed", "complete", "weave", "stack",
        # Organism & collective (swarm = distributed air)
        "shard", "mycelium", "family", "tag", "summary", "medium",
        "repo", "mirror", "guild", "quest", "membrane",
        "civilization", "frontier", "manuscript", "being",
        "organism", "swarm", "collective", "brain",
        # Mapping & traversal (fractal navigation)
        "map", "mapping", "lookup", "resolve", "traverse", "walk",
        # Infrastructure & system (the invisible carrier)
        "server", "agent", "config", "infrastructure", "pipeline",
        "module", "package", "library", "framework", "tool",
        "system", "platform", "compiler", "interpreter",
        # Document & text (air carries the word)
        "document", "chapter", "section", "page", "text",
        "read", "write", "parse", "format", "render",
        "appendix", "table", "list", "entry",
    },
}

# Flatten all domain keywords for quick tokenization
_ALL_DOMAIN_WORDS: set[str] = set()
for _words in LENS_DOMAINS.values():
    _ALL_DOMAIN_WORDS |= _words

# ── Data Structures ───────────────────────────────────────────────────


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class CorpusWeightField:
    """The full computed corpus weight field."""
    shard_count: int = 0
    seed_vectors: dict[str, list[float]] = field(default_factory=dict)
    similarity_edges: list[dict] = field(default_factory=list)
    family_centroids: dict[str, list[float]] = field(default_factory=dict)
    metro_centroids: dict[str, list[float]] = field(default_factory=dict)
    computed_at: str = ""
    version: int = 1


# ── Core Computation ──────────────────────────────────────────────────


def _tokenize_shard(shard: dict) -> set[str]:
    """Extract keyword tokens from a shard's summary and tags."""
    text_parts = []
    summary = shard.get("summary", "")
    if summary:
        text_parts.append(summary)
    tags = shard.get("tags", [])
    if tags:
        text_parts.append(" ".join(tags))
    # Also use family and payload_ref for extra signal
    family = shard.get("family", "")
    if family:
        text_parts.append(family)
    payload = shard.get("payload_ref", "")
    if payload:
        # Extract meaningful parts from file path
        stem = payload.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        text_parts.append(stem.replace("_", " ").replace("-", " "))

    raw = " ".join(text_parts).lower()
    tokens = set(re.findall(r'[a-z][a-z0-9_-]*', raw))
    # Also split hyphenated tokens
    expanded = set()
    for t in tokens:
        expanded.add(t)
        if "-" in t:
            for part in t.split("-"):
                if len(part) > 1:
                    expanded.add(part)
        if "_" in t:
            for part in t.split("_"):
                if len(part) > 1:
                    expanded.add(part)
    return expanded


def _compute_seed_vector(tokens: set[str]) -> list[float]:
    """Compute a 4D SFCR seed vector from keyword tokens.

    Each component is the count of token overlaps with that lens domain,
    then normalized to a unit vector. If no overlap, returns uniform [0.25, 0.25, 0.25, 0.25].
    """
    counts = []
    for lens in ("S", "F", "C", "R"):
        domain = LENS_DOMAINS[lens]
        overlap = len(tokens & domain)
        counts.append(float(overlap))

    total = sum(counts)
    if total == 0:
        return [0.25, 0.25, 0.25, 0.25]

    # Normalize to unit vector (L2 norm)
    magnitude = math.sqrt(sum(c * c for c in counts))
    if magnitude < 1e-15:
        return [0.25, 0.25, 0.25, 0.25]

    return [c / magnitude for c in counts]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two 4D vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a < 1e-15 or mag_b < 1e-15:
        return 0.0
    return dot / (mag_a * mag_b)


def _centroid(vectors: list[list[float]]) -> list[float]:
    """Compute the centroid (mean) of a list of 4D vectors, then normalize."""
    if not vectors:
        return [0.25, 0.25, 0.25, 0.25]

    n = len(vectors)
    sums = [0.0, 0.0, 0.0, 0.0]
    for v in vectors:
        for i in range(4):
            sums[i] += v[i]
    mean = [s / n for s in sums]

    magnitude = math.sqrt(sum(c * c for c in mean))
    if magnitude < 1e-15:
        return [0.25, 0.25, 0.25, 0.25]
    return [c / magnitude for c in mean]


# ── Main Computation Engine ───────────────────────────────────────────

_CACHE: Optional[CorpusWeightField] = None


def _load_from_disk() -> Optional[CorpusWeightField]:
    """Try to load precomputed results from disk."""
    if not OUTPUT_FILE.exists():
        return None
    try:
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        field_obj = CorpusWeightField(
            shard_count=data["meta"]["shard_count"],
            seed_vectors=data["seed_vectors"],
            similarity_edges=data["similarity_edges"],
            family_centroids=data["family_centroids"],
            metro_centroids=data["metro_centroids"],
            computed_at=data["meta"]["computed_at"],
            version=data["meta"]["version"],
        )
        return field_obj
    except (KeyError, json.JSONDecodeError):
        return None


def _save_to_disk(field_obj: CorpusWeightField) -> None:
    """Save computed results to disk atomically."""
    data = {
        "meta": {
            "shard_count": field_obj.shard_count,
            "computed_at": field_obj.computed_at,
            "version": field_obj.version,
            "edge_count": len(field_obj.similarity_edges),
            "family_count": len(field_obj.family_centroids),
            "metro_count": len(field_obj.metro_centroids),
        },
        "seed_vectors": {
            sid: [round(v, 6) for v in vec]
            for sid, vec in field_obj.seed_vectors.items()
        },
        "similarity_edges": [
            {
                "source": e["source"],
                "target": e["target"],
                "cosine": round(e["cosine"], 6),
                "family_match": e["family_match"],
            }
            for e in field_obj.similarity_edges
        ],
        "family_centroids": {
            fam: [round(v, 6) for v in vec]
            for fam, vec in field_obj.family_centroids.items()
        },
        "metro_centroids": {
            line: [round(v, 6) for v in vec]
            for line, vec in field_obj.metro_centroids.items()
        },
    }
    # Write via centralized JsonCache (locking + pheromone + auto-qshrink)
    from ._cache import JsonCache
    cache = JsonCache(OUTPUT_FILE.name)
    cache.save(
        data,
        agent_id="corpus-weight-builder",
        task_summary="rebuild corpus weight field",
        element="S",
        auto_compress=True,
    )


def compute_corpus_weights() -> CorpusWeightField:
    """Compute SFCR seed vectors and similarity edges for all shards.

    Loads mycelium_graph.json, computes per-shard SFCR vectors,
    pairwise cosine similarity (within family + metro line), and
    family/metro centroids.
    """
    graph_cache = JsonCache("mycelium_graph.json")
    data = graph_cache.load()

    shards = data["shards"]
    edges = data["edges"]
    meta = data["meta"]

    field_obj = CorpusWeightField()
    field_obj.shard_count = len(shards)
    field_obj.computed_at = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # ── Step 1: Compute SFCR seed vectors for every shard ──

    shard_lookup: dict[str, dict] = {}
    family_groups: dict[str, list[str]] = defaultdict(list)
    metro_groups: dict[str, list[str]] = defaultdict(list)

    for s in shards:
        sid = s["shard_id"]
        tokens = _tokenize_shard(s)
        vec = _compute_seed_vector(tokens)
        field_obj.seed_vectors[sid] = vec
        shard_lookup[sid] = s

        # Group by family
        family = s.get("family", "unknown")
        family_groups[family].append(sid)

        # Group by metro line (route_refs)
        routes = s.get("route_refs", [])
        for route in routes:
            metro_groups[route].append(sid)

    # ── Step 2: Compute pairwise similarity edges ──

    similarity_edges: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    def _add_edge(sid_a: str, sid_b: str, family_match: bool) -> None:
        """Add a similarity edge if it passes threshold."""
        if sid_a == sid_b:
            return
        pair = (min(sid_a, sid_b), max(sid_a, sid_b))
        if pair in seen_pairs:
            return
        seen_pairs.add(pair)
        vec_a = field_obj.seed_vectors[sid_a]
        vec_b = field_obj.seed_vectors[sid_b]
        cos = _cosine_similarity(vec_a, vec_b)
        if cos > 0.3:  # threshold to keep edges meaningful
            similarity_edges.append({
                "source": sid_a,
                "target": sid_b,
                "cosine": cos,
                "family_match": family_match,
            })

    # Within each family: all pairs (families are typically small)
    for family, sids in family_groups.items():
        if len(sids) <= 500:
            # Small enough for all pairs
            for i in range(len(sids)):
                for j in range(i + 1, len(sids)):
                    _add_edge(sids[i], sids[j], True)
        else:
            # Large family: sample — connect each shard to top-20 by cosine
            for i, sid_a in enumerate(sids):
                vec_a = field_obj.seed_vectors[sid_a]
                # Score against a sample of the family
                sample = sids[:i] + sids[i+1:]
                if len(sample) > 200:
                    # Subsample: take every Nth element
                    step = max(1, len(sample) // 200)
                    sample = sample[::step]
                scored = []
                for sid_b in sample:
                    vec_b = field_obj.seed_vectors[sid_b]
                    cos = _cosine_similarity(vec_a, vec_b)
                    scored.append((cos, sid_b))
                scored.sort(reverse=True)
                for cos, sid_b in scored[:20]:
                    if cos > 0.3:
                        pair = (min(sid_a, sid_b), max(sid_a, sid_b))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            similarity_edges.append({
                                "source": sid_a,
                                "target": sid_b,
                                "cosine": cos,
                                "family_match": True,
                            })

    # Across families on same metro line: top-10 per shard
    for metro_line, sids in metro_groups.items():
        if len(sids) <= 1:
            continue
        # For each shard on this metro line, find top-10 cross-family matches
        for sid_a in sids:
            fam_a = shard_lookup[sid_a].get("family", "")
            vec_a = field_obj.seed_vectors[sid_a]
            # Only compare against shards from different families
            candidates = [s for s in sids if shard_lookup[s].get("family", "") != fam_a]
            if not candidates:
                continue
            # Subsample if too many candidates
            sample = candidates
            if len(sample) > 200:
                step = max(1, len(sample) // 200)
                sample = sample[::step]
            scored = []
            for sid_b in sample:
                pair = (min(sid_a, sid_b), max(sid_a, sid_b))
                if pair in seen_pairs:
                    continue
                vec_b = field_obj.seed_vectors[sid_b]
                cos = _cosine_similarity(vec_a, vec_b)
                scored.append((cos, sid_b))
            scored.sort(reverse=True)
            for cos, sid_b in scored[:10]:
                if cos > 0.3:
                    pair = (min(sid_a, sid_b), max(sid_a, sid_b))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        similarity_edges.append({
                            "source": sid_a,
                            "target": sid_b,
                            "cosine": cos,
                            "family_match": False,
                        })

    field_obj.similarity_edges = similarity_edges

    # ── Step 3: Compute family centroids ──

    for family, sids in family_groups.items():
        vectors = [field_obj.seed_vectors[sid] for sid in sids]
        field_obj.family_centroids[family] = _centroid(vectors)

    # ── Step 4: Compute metro line centroids ──

    for metro_line, sids in metro_groups.items():
        vectors = [field_obj.seed_vectors[sid] for sid in sids]
        field_obj.metro_centroids[metro_line] = _centroid(vectors)

    return field_obj


def get_corpus_weights() -> CorpusWeightField:
    """Get or compute the corpus weight field (lazy, cached)."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    # Try disk cache first
    loaded = _load_from_disk()
    if loaded is not None:
        _CACHE = loaded
        return _CACHE

    # Compute from scratch
    _CACHE = compute_corpus_weights()
    _save_to_disk(_CACHE)
    return _CACHE


def reset_cache() -> None:
    """Clear the in-memory cache so next call recomputes."""
    global _CACHE
    _CACHE = None


# ── MCP Tool Entry Point ─────────────────────────────────────────────


def query_corpus_weights(component: str = "all") -> str:
    """
    Query SFCR corpus weights computed across all mycelium shards.

    Components:
      - all              : Summary statistics of the corpus weight field
      - shard_vector:ID  : Look up a specific shard's SFCR seed vector
      - family_centroid:N: Family-level SFCR centroid
      - metro_centroid:L : Metro line SFCR centroid
      - similarity:ID    : Top-N similar shards for a given shard ID
      - gaps             : Shards with lowest connectivity (candidates for new edges)
      - families         : All family centroids ranked by dominant lens
      - metros           : All metro centroids ranked by dominant lens
      - recompute        : Force recomputation from mycelium graph
    """
    comp = component.strip()
    cl = comp.lower()

    if cl == "all":
        return _format_all()
    elif cl == "gaps":
        return _format_gaps()
    elif cl == "families":
        return _format_families()
    elif cl == "metros":
        return _format_metros()
    elif cl == "recompute":
        return _format_recompute()
    elif cl.startswith("shard_vector:"):
        return _format_shard_vector(comp.split(":", 1)[1].strip())
    elif cl.startswith("family_centroid:"):
        return _format_family_centroid(comp.split(":", 1)[1].strip())
    elif cl.startswith("metro_centroid:"):
        return _format_metro_centroid(comp.split(":", 1)[1].strip())
    elif cl.startswith("similarity:"):
        return _format_similarity(comp.split(":", 1)[1].strip())
    else:
        return (
            f"Unknown component '{component}'. Use: all, shard_vector:ID, "
            "family_centroid:NAME, metro_centroid:LINE, similarity:ID, "
            "gaps, families, metros, recompute"
        )


# ── Formatters ────────────────────────────────────────────────────────

LENS_LABELS = ("S", "F", "C", "R")
LENS_NAMES = {"S": "Square/Earth", "F": "Flower/Fire", "C": "Cloud/Water", "R": "Fractal/Air"}


def _vec_str(v: list[float]) -> str:
    """Format a 4D vector as a compact string."""
    return f"[{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}, {v[3]:.3f}]"


def _dominant_lens(v: list[float]) -> str:
    """Return the dominant SFCR lens label."""
    idx = max(range(4), key=lambda i: v[i])
    return LENS_LABELS[idx]


def _format_all() -> str:
    field_obj = get_corpus_weights()
    total_edges = len(field_obj.similarity_edges)
    family_edges = sum(1 for e in field_obj.similarity_edges if e["family_match"])
    cross_edges = total_edges - family_edges

    # Compute average cosine
    if total_edges > 0:
        avg_cos = sum(e["cosine"] for e in field_obj.similarity_edges) / total_edges
    else:
        avg_cos = 0.0

    # Count shards per dominant lens
    lens_dist = defaultdict(int)
    for vec in field_obj.seed_vectors.values():
        lens_dist[_dominant_lens(vec)] += 1

    # Connectivity: edges per shard
    connectivity = defaultdict(int)
    for e in field_obj.similarity_edges:
        connectivity[e["source"]] += 1
        connectivity[e["target"]] += 1
    connected_shards = len(connectivity)
    isolated = field_obj.shard_count - connected_shards
    avg_degree = sum(connectivity.values()) / max(connected_shards, 1)

    lines = [
        "## Corpus Weight Field\n",
        f"**Shards**: {field_obj.shard_count:,}",
        f"**Seed Vectors**: {len(field_obj.seed_vectors):,}",
        f"**Similarity Edges**: {total_edges:,} "
        f"(family: {family_edges:,} | cross-metro: {cross_edges:,})",
        f"**Average Cosine**: {avg_cos:.4f}",
        f"**Family Centroids**: {len(field_obj.family_centroids)}",
        f"**Metro Centroids**: {len(field_obj.metro_centroids)}",
        f"**Computed At**: {field_obj.computed_at}",
        f"**Version**: {field_obj.version}\n",
        "### Dominant Lens Distribution\n",
    ]
    for lens in LENS_LABELS:
        count = lens_dist.get(lens, 0)
        pct = count / max(field_obj.shard_count, 1)
        bar = "#" * int(pct * 40)
        lines.append(
            f"- **{lens}** ({LENS_NAMES[lens]}): {count:,} ({pct:.1%}) {bar}"
        )

    lines.extend([
        f"\n### Connectivity\n",
        f"- **Connected shards**: {connected_shards:,}",
        f"- **Isolated shards**: {isolated:,}",
        f"- **Avg degree**: {avg_degree:.1f}",
    ])

    return "\n".join(lines)


def _format_shard_vector(query: str) -> str:
    field_obj = get_corpus_weights()
    ql = query.lower()

    # Exact match first
    if query in field_obj.seed_vectors:
        vec = field_obj.seed_vectors[query]
        return _render_shard_detail(query, vec, field_obj)

    # Substring match
    matches = [sid for sid in field_obj.seed_vectors if ql in sid.lower()]
    if len(matches) == 1:
        vec = field_obj.seed_vectors[matches[0]]
        return _render_shard_detail(matches[0], vec, field_obj)
    if matches:
        lines = [f"## Multiple matches for '{query}' ({len(matches)})\n"]
        for sid in matches[:30]:
            vec = field_obj.seed_vectors[sid]
            lines.append(f"- **{sid}** {_vec_str(vec)} [{_dominant_lens(vec)}]")
        if len(matches) > 30:
            lines.append(f"- ... and {len(matches) - 30} more")
        return "\n".join(lines)
    return f"No shard found matching '{query}'."


def _render_shard_detail(sid: str, vec: list[float], field_obj: CorpusWeightField) -> str:
    dom = _dominant_lens(vec)
    lines = [
        f"## Shard Vector: {sid}\n",
        f"**SFCR Vector**: {_vec_str(vec)}",
        f"**Dominant Lens**: {dom} ({LENS_NAMES[dom]})\n",
        "### Component Breakdown\n",
        f"| Lens | Value | Bar |",
        f"|------|-------|-----|",
    ]
    for i, lens in enumerate(LENS_LABELS):
        bar = "#" * int(vec[i] * 40)
        lines.append(f"| {lens} ({LENS_NAMES[lens]}) | {vec[i]:.4f} | {bar} |")

    # Find edges for this shard
    shard_edges = [
        e for e in field_obj.similarity_edges
        if e["source"] == sid or e["target"] == sid
    ]
    shard_edges.sort(key=lambda e: e["cosine"], reverse=True)

    if shard_edges:
        lines.append(f"\n### Top Similar Shards ({len(shard_edges)} edges)\n")
        for e in shard_edges[:15]:
            other = e["target"] if e["source"] == sid else e["source"]
            fam_tag = " [family]" if e["family_match"] else " [cross]"
            lines.append(f"- **{other}** cos={e['cosine']:.4f}{fam_tag}")
        if len(shard_edges) > 15:
            lines.append(f"- ... and {len(shard_edges) - 15} more edges")
    else:
        lines.append("\n*No similarity edges for this shard.*")

    return "\n".join(lines)


def _format_family_centroid(family: str) -> str:
    field_obj = get_corpus_weights()
    fl = family.lower()

    # Exact match
    if family in field_obj.family_centroids:
        vec = field_obj.family_centroids[family]
        return _render_centroid("Family", family, vec, field_obj)

    # Case-insensitive match
    for fam, vec in field_obj.family_centroids.items():
        if fam.lower() == fl:
            return _render_centroid("Family", fam, vec, field_obj)

    # Substring
    matches = [(fam, vec) for fam, vec in field_obj.family_centroids.items()
               if fl in fam.lower()]
    if len(matches) == 1:
        return _render_centroid("Family", matches[0][0], matches[0][1], field_obj)
    if matches:
        lines = [f"## Multiple family matches for '{family}'\n"]
        for fam, vec in matches:
            lines.append(f"- **{fam}** {_vec_str(vec)} [{_dominant_lens(vec)}]")
        return "\n".join(lines)
    return f"No family found matching '{family}'."


def _format_metro_centroid(line: str) -> str:
    field_obj = get_corpus_weights()

    if line in field_obj.metro_centroids:
        vec = field_obj.metro_centroids[line]
        return _render_centroid("Metro Line", line, vec, field_obj)

    # Case-insensitive
    for ml, vec in field_obj.metro_centroids.items():
        if ml.lower() == line.lower():
            return _render_centroid("Metro Line", ml, vec, field_obj)

    return f"No metro line found matching '{line}'."


def _render_centroid(kind: str, name: str, vec: list[float],
                     field_obj: CorpusWeightField) -> str:
    dom = _dominant_lens(vec)
    lines = [
        f"## {kind} Centroid: {name}\n",
        f"**SFCR Centroid**: {_vec_str(vec)}",
        f"**Dominant Lens**: {dom} ({LENS_NAMES[dom]})\n",
        "| Lens | Value |",
        "|------|-------|",
    ]
    for i, lens in enumerate(LENS_LABELS):
        lines.append(f"| {lens} | {vec[i]:.4f} |")
    return "\n".join(lines)


def _format_similarity(query: str) -> str:
    field_obj = get_corpus_weights()
    ql = query.lower()

    # Find the shard
    sid = None
    if query in field_obj.seed_vectors:
        sid = query
    else:
        matches = [s for s in field_obj.seed_vectors if ql in s.lower()]
        if len(matches) == 1:
            sid = matches[0]
        elif matches:
            lines = [f"## Multiple matches for '{query}' — be more specific\n"]
            for s in matches[:20]:
                lines.append(f"- {s}")
            return "\n".join(lines)

    if not sid:
        return f"No shard found matching '{query}'."

    # Find all edges for this shard
    shard_edges = [
        e for e in field_obj.similarity_edges
        if e["source"] == sid or e["target"] == sid
    ]
    shard_edges.sort(key=lambda e: e["cosine"], reverse=True)

    vec = field_obj.seed_vectors[sid]
    lines = [
        f"## Similarity Report: {sid}\n",
        f"**SFCR Vector**: {_vec_str(vec)} [{_dominant_lens(vec)}]",
        f"**Total Edges**: {len(shard_edges)}\n",
    ]

    if shard_edges:
        lines.extend([
            "| Rank | Shard | Cosine | Type |",
            "|------|-------|--------|------|",
        ])
        for rank, e in enumerate(shard_edges[:30], 1):
            other = e["target"] if e["source"] == sid else e["source"]
            kind = "family" if e["family_match"] else "cross"
            lines.append(f"| {rank} | `{other}` | {e['cosine']:.4f} | {kind} |")
        if len(shard_edges) > 30:
            lines.append(f"\n*... and {len(shard_edges) - 30} more edges*")
    else:
        lines.append("*No similarity edges found for this shard.*")

    return "\n".join(lines)


def _format_gaps() -> str:
    field_obj = get_corpus_weights()

    # Count connectivity per shard
    connectivity = defaultdict(int)
    for e in field_obj.similarity_edges:
        connectivity[e["source"]] += 1
        connectivity[e["target"]] += 1

    # Find shards with zero or minimal connectivity
    all_sids = list(field_obj.seed_vectors.keys())
    scored = [(connectivity.get(sid, 0), sid) for sid in all_sids]
    scored.sort()

    # Isolated shards (degree 0)
    isolated = [sid for deg, sid in scored if deg == 0]
    # Low-connectivity shards (degree 1-2)
    low_conn = [(deg, sid) for deg, sid in scored if 0 < deg <= 2]

    lines = [
        "## Connectivity Gaps\n",
        f"**Total Shards**: {field_obj.shard_count:,}",
        f"**Isolated (degree 0)**: {len(isolated):,}",
        f"**Low-connectivity (degree 1-2)**: {len(low_conn):,}\n",
    ]

    if isolated:
        lines.append(f"### Isolated Shards (top 30 of {len(isolated)})\n")
        for sid in isolated[:30]:
            vec = field_obj.seed_vectors[sid]
            lines.append(f"- **{sid}** {_vec_str(vec)} [{_dominant_lens(vec)}]")
        if len(isolated) > 30:
            lines.append(f"- ... and {len(isolated) - 30} more")

    if low_conn:
        lines.append(f"\n### Low-Connectivity Shards (top 30 of {len(low_conn)})\n")
        for deg, sid in low_conn[:30]:
            vec = field_obj.seed_vectors[sid]
            lines.append(
                f"- **{sid}** degree={deg} {_vec_str(vec)} [{_dominant_lens(vec)}]"
            )

    # Suggest new edges: isolated shards with high cosine to existing shards
    if isolated:
        lines.append("\n### Suggested New Edges (top 20)\n")
        suggestions = []
        sample_isolated = isolated[:100]  # limit computation
        sample_connected = [sid for deg, sid in scored if deg >= 3][:200]
        for iso_sid in sample_isolated:
            vec_a = field_obj.seed_vectors[iso_sid]
            for con_sid in sample_connected:
                vec_b = field_obj.seed_vectors[con_sid]
                cos = _cosine_similarity(vec_a, vec_b)
                if cos > 0.5:
                    suggestions.append((cos, iso_sid, con_sid))
        suggestions.sort(reverse=True)
        for cos, src, tgt in suggestions[:20]:
            lines.append(f"- `{src}` <-> `{tgt}` cos={cos:.4f}")

    return "\n".join(lines)


def _format_families() -> str:
    field_obj = get_corpus_weights()
    lines = ["## Family Centroids\n",
             "| Family | S | F | C | R | Dominant |",
             "|--------|---|---|---|---|----------|"]
    sorted_fams = sorted(
        field_obj.family_centroids.items(),
        key=lambda x: max(x[1]),
        reverse=True,
    )
    for fam, vec in sorted_fams:
        dom = _dominant_lens(vec)
        lines.append(
            f"| {fam} | {vec[0]:.3f} | {vec[1]:.3f} | {vec[2]:.3f} | {vec[3]:.3f} | {dom} |"
        )
    return "\n".join(lines)


def _format_metros() -> str:
    field_obj = get_corpus_weights()
    lines = ["## Metro Line Centroids\n",
             "| Line | S | F | C | R | Dominant |",
             "|------|---|---|---|---|----------|"]
    sorted_lines = sorted(
        field_obj.metro_centroids.items(),
        key=lambda x: max(x[1]),
        reverse=True,
    )
    for line, vec in sorted_lines:
        dom = _dominant_lens(vec)
        lines.append(
            f"| {line} | {vec[0]:.3f} | {vec[1]:.3f} | {vec[2]:.3f} | {vec[3]:.3f} | {dom} |"
        )
    return "\n".join(lines)


def _format_recompute() -> str:
    global _CACHE
    _CACHE = None
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
    field_obj = compute_corpus_weights()
    _save_to_disk(field_obj)
    _CACHE = field_obj
    return (
        f"Recomputed corpus weight field.\n"
        f"**Shards**: {field_obj.shard_count:,}\n"
        f"**Seed Vectors**: {len(field_obj.seed_vectors):,}\n"
        f"**Similarity Edges**: {len(field_obj.similarity_edges):,}\n"
        f"**Family Centroids**: {len(field_obj.family_centroids)}\n"
        f"**Metro Centroids**: {len(field_obj.metro_centroids)}\n"
        f"**Saved to**: {OUTPUT_FILE}"
    )
