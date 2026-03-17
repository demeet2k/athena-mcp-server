"""`Atlas`: a single object that *runs the kernel* and *stores the meaning*.

AtlasForge has two layers:

1) the operational kernel: Blueprint → Plan → Recipe → ProofPack
2) the memory/atlas layer: structured notes + retrieval + linkage

The `Atlas` class is a convenience façade that turns the framework into a
practical mathematics memory bank:

```python
from atlasforge import Atlas, RootConstraint, Interval

atlas = Atlas.from_env()  # uses ATLASFORGE_MEMORY_DIR if set

bp = atlas.blueprint(
    name="sqrt(2)",
    constraint=RootConstraint(lambda x: x*x - 2, domain=Interval.closed(1,2)),
)

recipe = atlas.solve(bp, verified=True)
atlas.remember("Why Brent works", "...", tags=["root", "brent"])

hits = atlas.recall("interference", tags=["qcm"])
```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence
import os

from atlasforge.recipes.recipe import Blueprint, SolvePlan, Recipe, RecipeExecutor
from atlasforge.memory.store import MemoryStore
from atlasforge.core.enums import TruthProfile


@dataclass
class AtlasConfig:
    """Configuration for an :class:`~atlasforge.atlas.atlas.Atlas`."""

    memory_dir: Optional[str] = None
    auto_bootstrap: bool = True


class Atlas:
    """High-level orchestrator for *math as memory*.

    Atlas is intentionally thin. It delegates real work to:
    - :class:`~atlasforge.recipes.recipe.RecipeExecutor`
    - :class:`~atlasforge.memory.store.MemoryStore`
    """

    def __init__(self, config: Optional[AtlasConfig] = None):
        self.config = config or AtlasConfig()
        self.executor = RecipeExecutor()
        self.memory: Optional[MemoryStore] = None

        if self.config.memory_dir:
            self.memory = MemoryStore(self.config.memory_dir)

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "Atlas":
        """Construct an Atlas using environment variables.

        - ATLASFORGE_MEMORY_DIR: directory for memory bank.
        """
        mem = os.environ.get("ATLASFORGE_MEMORY_DIR")
        return cls(AtlasConfig(memory_dir=mem))

    # ------------------------------------------------------------------
    # Blueprint helpers
    # ------------------------------------------------------------------

    def blueprint(
        self,
        constraint: Any,
        name: str = "",
        description: str = "",
        truth_profile: TruthProfile = TruthProfile.EXPLORE,
        chart: Any = None,
        search_domain: Any = None,
        hints: Optional[Dict[str, Any]] = None,
    ) -> Blueprint:
        """Convenience constructor for a :class:`~atlasforge.recipes.recipe.Blueprint`."""
        return Blueprint(
            constraint=constraint,
            chart=chart,
            truth_profile=truth_profile,
            search_domain=search_domain,
            hints=dict(hints or {}),
            name=name,
            description=description,
        )

    # ------------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------------

    def solve(
        self,
        blueprint: Blueprint,
        plan: Optional[SolvePlan] = None,
        verified: bool = False,
        remember: bool = True,
        note: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> Recipe:
        """Execute a blueprint and optionally remember the result.

        Parameters
        ----------
        verified:
            If True and no explicit plan is passed, uses `SolvePlan.verified()`.
        remember:
            If True and a memory bank is configured, log the recipe.
        note:
            Optional additional note stored as a MemoryEntry linked to the recipe.
        tags:
            Extra tags for the recipe log / note.
        """

        if plan is None:
            plan = SolvePlan.verified() if verified else SolvePlan.default()

        recipe = self.executor.execute(blueprint, plan)

        if remember and self.memory is not None:
            # Store the standard recipe log entry.
            entry_hash = self.memory.log_recipe(recipe, title=blueprint.name or None, tags=list(tags or []))
            try:
                if recipe.output is not None:
                    recipe.output.metadata["memory_entry"] = entry_hash
            except Exception:
                pass

            # Optionally store an additional free-form note.
            if note:
                note_hash = self.memory.remember(
                    title=f"Note: {blueprint.name or 'Recipe'}",
                    content=str(note).rstrip() + "\n",
                    tags=list(tags or []) + ["note"],
                    links={"recipe": recipe.content_hash(), "blueprint": blueprint.content_hash()},
                    extra={"kind": "note"},
                )
                # Link the note to the recipe-log entry.
                try:
                    self.memory.link(note_hash, entry_hash, relation="annotates")
                except Exception:
                    pass

        return recipe

    # ------------------------------------------------------------------
    # Memory façade
    # ------------------------------------------------------------------

    def remember(
        self,
        title: str,
        content: str,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, Any]] = None,
        address: Optional[Any] = None,
    ) -> Optional[str]:
        """Store a memory entry (if a memory bank is configured)."""
        if self.memory is None:
            return None
        return self.memory.remember(
            title=title,
            content=content,
            tags=tags,
            links=links,
            extra=extra,
            address=address,
        )


    # ------------------------------------------------------------------
    # Structured knowledge helpers (Definitions/Lemmas/Theorems/...)
    # ------------------------------------------------------------------

    def define(self, title: str, statement: str, **kwargs) -> Optional[str]:
        """Convenience: store a *Definition* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.define(title=title, statement=statement, **kwargs)

    def lemma(self, title: str, statement: str, **kwargs) -> Optional[str]:
        """Convenience: store a *Lemma* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.lemma(title=title, statement=statement, **kwargs)

    def theorem(self, title: str, statement: str, **kwargs) -> Optional[str]:
        """Convenience: store a *Theorem* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.theorem(title=title, statement=statement, **kwargs)

    def identity(self, title: str, statement: str, **kwargs) -> Optional[str]:
        """Convenience: store an *Identity* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.identity(title=title, statement=statement, **kwargs)

    def operator(self, title: str, statement: str, **kwargs) -> Optional[str]:
        """Convenience: store an *Operator* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.operator(title=title, statement=statement, **kwargs)

    def proof_entry(self, title: str, proof: str, **kwargs) -> Optional[str]:
        """Convenience: store a standalone *Proof* knowledge item."""
        if self.memory is None:
            return None
        return self.memory.proof_entry(title=title, proof=proof, **kwargs)

    # ------------------------------------------------------------------
    # Book compiler
    # ------------------------------------------------------------------


    def export_book(
        self,
        output_path: str,
        *,
        title: str = "AtlasForge Memory Atlas",
        subtitle: str = "",
        query: str = "",
        tags: Optional[Sequence[str]] = None,
        kinds: Optional[Sequence[str]] = None,
        session_id: Optional[str] = None,
        roots: Optional[Sequence[str]] = None,
        include_dependencies: bool = False,
        dependency_relations: Optional[Sequence[str]] = None,
        dependency_direction: str = "out",
        dependency_max_depth: int = 25,
        sort_by: str = "crystal",
        include_crystal_map: bool = True,
        include_full_crystal_map: bool = False,
        max_entries_per_cell: int = 25,
        include_graph_edges: bool = True,
        include_toc: bool = True,
        include_tag_index: bool = True,
        max_entries: Optional[int] = None,
        fmt: str = "md",
    ) -> Optional[str]:
        """Compile the memory bank into a book-like artifact.

        Parameters
        ----------
        fmt:
            "md" (Markdown), "pdf", "docx", or "tex".

        roots + include_dependencies:
            If ``roots`` is provided and ``include_dependencies`` is True, the
            export will include the dependency closure following graph edges
            (by default: ``depends_on``).
        """
        if self.memory is None:
            return None

        from atlasforge.atlas.book import AtlasBookBuilder, AtlasBookConfig

        dep_rels = list(dependency_relations or ["depends_on"])

        cfg = AtlasBookConfig(
            title=title,
            subtitle=subtitle,
            query=query,
            tags=list(tags or []),
            kinds=list(kinds or []),
            session_id=session_id,
            root_hashes=list(roots or []),
            include_dependencies=include_dependencies,
            dependency_relations=dep_rels,
            dependency_direction=dependency_direction,
            dependency_max_depth=int(dependency_max_depth or 25),
            sort_by=sort_by,
            include_crystal_map=include_crystal_map,
            include_full_crystal_map=include_full_crystal_map,
            max_entries_per_cell=int(max_entries_per_cell or 25),
            include_toc=include_toc,
            include_tag_index=include_tag_index,
            include_graph_edges=include_graph_edges,
            max_entries=max_entries,
        )
        builder = AtlasBookBuilder(self.memory)

        fmt_norm = (fmt or "md").strip().lower()
        if fmt_norm in ("pdf",):
            return builder.export_pdf(output_path, cfg)
        if fmt_norm in ("docx", "word"):
            return builder.export_docx(output_path, cfg)
        if fmt_norm in ("tex", "latex"):
            return builder.export_tex(output_path, cfg)
        return builder.export_markdown(output_path, cfg)


    def recall(
        self,
        query: str = "",
        tags: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        kinds: Optional[Sequence[Any]] = None,
        kind: Optional[Any] = None,
        limit: int = 20,
    ) -> List[Any]:
        """Search the memory bank (returns MemoryEntry list)."""
        if self.memory is None:
            return []
        return self.memory.search(query=query, tags=tags, address=address, kinds=kinds, kind=kind, limit=limit)

    def link(self, src: str, dst: str, relation: str, note: str = "", meta: Optional[Dict[str, Any]] = None) -> bool:
        """Create a knowledge-graph edge."""
        if self.memory is None:
            return False
        self.memory.link(src=src, dst=dst, relation=relation, note=note, meta=meta)
        return True

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def start_session(self, name: str, description: str = "", tags: Optional[Sequence[str]] = None):
        if self.memory is None:
            return None
        return self.memory.start_session(name=name, description=description, tags=tags)

    def end_session(self) -> Optional[str]:
        if self.memory is None:
            return None
        return self.memory.end_session()
