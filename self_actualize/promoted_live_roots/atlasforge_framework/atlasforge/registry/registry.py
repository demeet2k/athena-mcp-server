"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Registry System                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Content-Addressed Storage for Recipes and Artifacts.

The Registry implements:
1. RecipeStore - Content-addressed storage for recipes
2. DependencyDAG - Tracks dependencies between recipes
3. Cache - Memoization of solved constraints
4. Trust Chain - Propagation of verification status

Key Principle: Store by CONTENT HASH, not by name.
This enables deduplication, caching, and trust verification.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path

from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import CertificateLevel
from atlasforge.recipes.recipe import Recipe, Blueprint
from atlasforge.certificates.certificate import CertificateBundle


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT-ADDRESSED STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StorageEntry:
    """An entry in the content-addressed store."""
    
    content_hash: str
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    
    # Metadata
    entry_type: str = "unknown"
    tags: List[str] = field(default_factory=list)
    
    def touch(self):
        """Update access time and count."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class ContentStore:
    """
    Content-addressed key-value store.
    
    Objects are stored and retrieved by their content hash.
    This provides automatic deduplication.
    """
    
    def __init__(self):
        self._store: Dict[str, StorageEntry] = {}
        self._tags: Dict[str, Set[str]] = {}  # tag -> set of hashes
    
    def put(self, obj: ContentAddressed, tags: Optional[List[str]] = None) -> str:
        """
        Store an object by its content hash.
        
        Returns the content hash.
        """
        content_hash = obj.content_hash()
        
        if content_hash in self._store:
            # Already exists, just touch it
            self._store[content_hash].touch()
        else:
            # New entry
            entry = StorageEntry(
                content_hash=content_hash,
                data=obj.to_dict() if hasattr(obj, 'to_dict') else {'value': str(obj)},
                entry_type=type(obj).__name__,
                tags=tags or [],
            )
            self._store[content_hash] = entry
            
            # Update tag index
            for tag in entry.tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(content_hash)
        
        return content_hash
    
    def get(self, content_hash: str) -> Optional[StorageEntry]:
        """Retrieve an entry by content hash."""
        entry = self._store.get(content_hash)
        if entry:
            entry.touch()
        return entry
    
    def has(self, content_hash: str) -> bool:
        """Check if an entry exists."""
        return content_hash in self._store
    
    def delete(self, content_hash: str) -> bool:
        """Delete an entry."""
        if content_hash in self._store:
            entry = self._store[content_hash]
            for tag in entry.tags:
                if tag in self._tags:
                    self._tags[tag].discard(content_hash)
            del self._store[content_hash]
            return True
        return False
    
    def get_by_tag(self, tag: str) -> List[StorageEntry]:
        """Get all entries with a given tag."""
        hashes = self._tags.get(tag, set())
        return [self._store[h] for h in hashes if h in self._store]
    
    def __len__(self) -> int:
        return len(self._store)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._store)


# ═══════════════════════════════════════════════════════════════════════════════
# RECIPE STORE
# ═══════════════════════════════════════════════════════════════════════════════

class RecipeStore:
    """
    Specialized store for recipes.
    
    Provides:
    - Content-addressed storage
    - Lookup by blueprint hash
    - Cache of solved constraints
    - Verification status tracking
    """
    
    def __init__(self):
        self._recipes: ContentStore = ContentStore()
        self._blueprint_index: Dict[str, str] = {}  # blueprint_hash -> recipe_hash
        self._verified: Set[str] = set()  # Set of verified recipe hashes
    
    def store(self, recipe: Recipe) -> str:
        """
        Store a recipe.
        
        Returns the recipe's content hash.
        """
        recipe_hash = self._recipes.put(recipe, tags=["recipe"])
        
        # Index by blueprint
        blueprint_hash = recipe.blueprint.content_hash()
        self._blueprint_index[blueprint_hash] = recipe_hash
        
        # Track verification status
        if recipe.verified:
            self._verified.add(recipe_hash)
        
        return recipe_hash
    
    def get(self, recipe_hash: str) -> Optional[Recipe]:
        """Retrieve a recipe by hash."""
        entry = self._recipes.get(recipe_hash)
        if entry:
            # Reconstruct recipe from stored data
            # (In production, would deserialize properly)
            return entry.data.get('_recipe_obj')
        return None
    
    def lookup_by_blueprint(self, blueprint: Blueprint) -> Optional[Recipe]:
        """Look up a recipe by its blueprint."""
        blueprint_hash = blueprint.content_hash()
        recipe_hash = self._blueprint_index.get(blueprint_hash)
        if recipe_hash:
            return self.get(recipe_hash)
        return None
    
    def has_solution(self, blueprint: Blueprint) -> bool:
        """Check if a solution exists for a blueprint."""
        return blueprint.content_hash() in self._blueprint_index
    
    def is_verified(self, recipe_hash: str) -> bool:
        """Check if a recipe is verified."""
        return recipe_hash in self._verified
    
    def mark_verified(self, recipe_hash: str):
        """Mark a recipe as verified."""
        self._verified.add(recipe_hash)
    
    def get_verified_recipes(self) -> List[str]:
        """Get all verified recipe hashes."""
        return list(self._verified)
    
    def __len__(self) -> int:
        return len(self._recipes)


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY DAG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DependencyNode:
    """A node in the dependency DAG."""
    
    content_hash: str
    node_type: str  # "recipe", "certificate", "constraint", etc.
    
    # Dependencies
    depends_on: Set[str] = field(default_factory=set)  # Hashes this node depends on
    depended_by: Set[str] = field(default_factory=set)  # Hashes that depend on this node
    
    # Status
    valid: bool = True
    invalidation_reason: Optional[str] = None


class DependencyDAG:
    """
    Directed Acyclic Graph of dependencies between artifacts.
    
    Tracks:
    - What each artifact depends on
    - What depends on each artifact
    - Propagation of invalidation
    """
    
    def __init__(self):
        self._nodes: Dict[str, DependencyNode] = {}
    
    def add_node(self, content_hash: str, node_type: str) -> DependencyNode:
        """Add a node to the DAG."""
        if content_hash not in self._nodes:
            self._nodes[content_hash] = DependencyNode(content_hash, node_type)
        return self._nodes[content_hash]
    
    def add_dependency(self, from_hash: str, to_hash: str):
        """
        Add a dependency edge: from_hash depends on to_hash.
        """
        if from_hash not in self._nodes:
            self.add_node(from_hash, "unknown")
        if to_hash not in self._nodes:
            self.add_node(to_hash, "unknown")
        
        self._nodes[from_hash].depends_on.add(to_hash)
        self._nodes[to_hash].depended_by.add(from_hash)
    
    def get_dependencies(self, content_hash: str) -> Set[str]:
        """Get all direct dependencies of a node."""
        if content_hash in self._nodes:
            return self._nodes[content_hash].depends_on.copy()
        return set()
    
    def get_dependents(self, content_hash: str) -> Set[str]:
        """Get all nodes that directly depend on this node."""
        if content_hash in self._nodes:
            return self._nodes[content_hash].depended_by.copy()
        return set()
    
    def get_all_dependencies(self, content_hash: str) -> Set[str]:
        """Get all transitive dependencies (closure)."""
        visited = set()
        stack = [content_hash]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            if current in self._nodes:
                for dep in self._nodes[current].depends_on:
                    if dep not in visited:
                        stack.append(dep)
        
        visited.discard(content_hash)  # Don't include self
        return visited
    
    def get_all_dependents(self, content_hash: str) -> Set[str]:
        """Get all transitive dependents (reverse closure)."""
        visited = set()
        stack = [content_hash]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            if current in self._nodes:
                for dep in self._nodes[current].depended_by:
                    if dep not in visited:
                        stack.append(dep)
        
        visited.discard(content_hash)
        return visited
    
    def invalidate(self, content_hash: str, reason: str = "") -> Set[str]:
        """
        Invalidate a node and propagate to all dependents.
        
        Returns set of all invalidated hashes.
        """
        invalidated = set()
        
        if content_hash not in self._nodes:
            return invalidated
        
        stack = [content_hash]
        
        while stack:
            current = stack.pop()
            if current in invalidated:
                continue
            
            if current in self._nodes:
                node = self._nodes[current]
                node.valid = False
                node.invalidation_reason = reason
                invalidated.add(current)
                
                # Propagate to dependents
                for dep in node.depended_by:
                    if dep not in invalidated:
                        stack.append(dep)
        
        return invalidated
    
    def is_valid(self, content_hash: str) -> bool:
        """Check if a node and all its dependencies are valid."""
        if content_hash not in self._nodes:
            return False
        
        # Check self
        if not self._nodes[content_hash].valid:
            return False
        
        # Check all dependencies
        for dep in self.get_all_dependencies(content_hash):
            if dep in self._nodes and not self._nodes[dep].valid:
                return False
        
        return True
    
    def topological_sort(self) -> List[str]:
        """
        Return nodes in topological order.
        
        Nodes with no dependencies come first.
        """
        in_degree = {h: len(n.depends_on) for h, n in self._nodes.items()}
        queue = [h for h, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for dependent in self._nodes[node].depended_by:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# RECIPE CACHE
# ═══════════════════════════════════════════════════════════════════════════════

class RecipeCache:
    """
    Cache for recipe lookup by constraint.
    
    Enables fast lookup of previously solved constraints
    without re-computation.
    """
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[str, str] = {}  # constraint_hash -> recipe_hash
        self._access_order: List[str] = []  # LRU tracking
    
    def put(self, constraint_hash: str, recipe_hash: str):
        """Cache a constraint -> recipe mapping."""
        if constraint_hash in self._cache:
            # Update access order
            self._access_order.remove(constraint_hash)
        elif len(self._cache) >= self.max_size:
            # Evict LRU
            lru = self._access_order.pop(0)
            del self._cache[lru]
        
        self._cache[constraint_hash] = recipe_hash
        self._access_order.append(constraint_hash)
    
    def get(self, constraint_hash: str) -> Optional[str]:
        """Look up a recipe hash by constraint hash."""
        if constraint_hash in self._cache:
            # Update access order
            self._access_order.remove(constraint_hash)
            self._access_order.append(constraint_hash)
            return self._cache[constraint_hash]
        return None
    
    def has(self, constraint_hash: str) -> bool:
        """Check if constraint is cached."""
        return constraint_hash in self._cache
    
    def invalidate(self, constraint_hash: str):
        """Invalidate a cache entry."""
        if constraint_hash in self._cache:
            del self._cache[constraint_hash]
            self._access_order.remove(constraint_hash)
    
    def clear(self):
        """Clear the entire cache."""
        self._cache.clear()
        self._access_order.clear()
    
    def __len__(self) -> int:
        return len(self._cache)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY FACADE
# ═══════════════════════════════════════════════════════════════════════════════

class Registry:
    """
    High-level registry facade.
    
    Combines:
    - Recipe storage
    - Dependency tracking
    - Caching
    - Verification status
    """
    
    def __init__(self):
        self.store = RecipeStore()
        self.dag = DependencyDAG()
        self.cache = RecipeCache()
    
    def register(self, recipe: Recipe) -> str:
        """
        Register a recipe.
        
        Stores the recipe and updates dependency graph.
        """
        # Store recipe
        recipe_hash = self.store.store(recipe)
        
        # Add to DAG
        self.dag.add_node(recipe_hash, "recipe")
        
        # Add blueprint dependency
        blueprint_hash = recipe.blueprint.content_hash()
        self.dag.add_node(blueprint_hash, "blueprint")
        self.dag.add_dependency(recipe_hash, blueprint_hash)
        
        # Cache constraint -> recipe mapping
        constraint_hash = recipe.blueprint.constraint.content_hash()
        self.cache.put(constraint_hash, recipe_hash)
        
        return recipe_hash
    
    def lookup(self, constraint_hash: str) -> Optional[Recipe]:
        """Look up a recipe by constraint hash."""
        recipe_hash = self.cache.get(constraint_hash)
        if recipe_hash:
            return self.store.get(recipe_hash)
        return None
    
    def get(self, recipe_hash: str) -> Optional[Recipe]:
        """Get a recipe by hash."""
        return self.store.get(recipe_hash)
    
    def is_valid(self, recipe_hash: str) -> bool:
        """Check if a recipe and its dependencies are valid."""
        return self.dag.is_valid(recipe_hash)
    
    def invalidate(self, recipe_hash: str, reason: str = "") -> Set[str]:
        """Invalidate a recipe and all dependents."""
        return self.dag.invalidate(recipe_hash, reason)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            'recipes': len(self.store),
            'dag_nodes': len(self.dag._nodes),
            'cache_entries': len(self.cache),
            'verified_recipes': len(self.store.get_verified_recipes()),
        }
