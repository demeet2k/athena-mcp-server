"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Registry System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

The registry provides content-addressed storage for all artifacts.

"Store generators, not enumerations" - We store recipes that can reproduce
results rather than caching all possible outputs.

Components:
- RecipeStore: Content-addressed recipe storage
- ResultCache: LRU cache for computed results
- DependencyDAG: Tracks dependencies between artifacts
- Ledger: Immutable append-only log of all operations
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, Iterator, List, Optional,
    Set, Tuple, Type, TypeVar, Union
)
from datetime import datetime
from collections import OrderedDict
import hashlib
import json
import os
import pickle

from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import CertificateLevel
from atlasforge.recipes.recipe import Recipe, RecipeOutput, Blueprint
from atlasforge.certificates.certificate import Certificate, ProofPack


T = TypeVar('T', bound=ContentAddressed)


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE BACKEND
# ═══════════════════════════════════════════════════════════════════════════════

class StorageBackend(ABC):
    """Abstract storage backend."""
    
    @abstractmethod
    def put(self, key: str, value: bytes) -> bool:
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        pass


class MemoryBackend(StorageBackend):
    """In-memory storage backend."""
    
    def __init__(self):
        self._store: Dict[str, bytes] = {}
    
    def put(self, key: str, value: bytes) -> bool:
        self._store[key] = value
        return True
    
    def get(self, key: str) -> Optional[bytes]:
        return self._store.get(key)
    
    def exists(self, key: str) -> bool:
        return key in self._store
    
    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        return [k for k in self._store.keys() if k.startswith(prefix)]


class FileBackend(StorageBackend):
    """File-based storage backend."""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _path(self, key: str) -> str:
        # Use first 2 chars as directory for sharding
        prefix = key[:2] if len(key) >= 2 else key
        dir_path = os.path.join(self.base_path, prefix)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, key)
    
    def put(self, key: str, value: bytes) -> bool:
        try:
            with open(self._path(key), 'wb') as f:
                f.write(value)
            return True
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[bytes]:
        try:
            with open(self._path(key), 'rb') as f:
                return f.read()
        except Exception:
            return None
    
    def exists(self, key: str) -> bool:
        return os.path.exists(self._path(key))
    
    def delete(self, key: str) -> bool:
        try:
            os.remove(self._path(key))
            return True
        except Exception:
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        keys = []
        for root, dirs, files in os.walk(self.base_path):
            for f in files:
                if f.startswith(prefix):
                    keys.append(f)
        return keys


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT STORE
# ═══════════════════════════════════════════════════════════════════════════════

class ContentStore(Generic[T]):
    """
    Generic content-addressed store for any ContentAddressed type.
    
    Objects are stored by their content hash, enabling:
    - Automatic deduplication
    - Integrity verification
    - Reproducible retrieval
    """
    
    def __init__(self, backend: StorageBackend, prefix: str = ""):
        self.backend = backend
        self.prefix = prefix
    
    def _key(self, content_hash: str) -> str:
        return f"{self.prefix}{content_hash}" if self.prefix else content_hash
    
    def store(self, obj: T) -> str:
        """Store an object, returning its content hash."""
        content_hash = obj.content_hash()
        key = self._key(content_hash)
        
        if not self.backend.exists(key):
            data = pickle.dumps(obj.to_dict())
            self.backend.put(key, data)
        
        return content_hash
    
    def retrieve(self, content_hash: str, cls: Type[T]) -> Optional[T]:
        """Retrieve an object by content hash."""
        key = self._key(content_hash)
        data = self.backend.get(key)
        
        if data is None:
            return None
        
        try:
            obj_dict = pickle.loads(data)
            if hasattr(cls, 'from_dict'):
                return cls.from_dict(obj_dict)
            return None
        except Exception:
            return None
    
    def exists(self, content_hash: str) -> bool:
        """Check if an object exists."""
        return self.backend.exists(self._key(content_hash))
    
    def delete(self, content_hash: str) -> bool:
        """Delete an object."""
        return self.backend.delete(self._key(content_hash))
    
    def list_all(self) -> List[str]:
        """List all stored content hashes."""
        keys = self.backend.list_keys(self.prefix)
        return [k[len(self.prefix):] if self.prefix else k for k in keys]


# ═══════════════════════════════════════════════════════════════════════════════
# RECIPE STORE
# ═══════════════════════════════════════════════════════════════════════════════

class RecipeStore:
    """
    Central store for recipes and their outputs.
    
    Implements the principle: "Store generators, not enumerations"
    """
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        self.backend = backend or MemoryBackend()
        self.recipes = ContentStore[Recipe](self.backend, "recipe:")
        self.outputs = ContentStore[RecipeOutput](self.backend, "output:")
        self.blueprints = ContentStore[Blueprint](self.backend, "blueprint:")
        self.certificates = ContentStore[Certificate](self.backend, "cert:")
        
        # Index: recipe_hash -> output_hash
        self._recipe_outputs: Dict[str, str] = {}
        
        # Index: blueprint_hash -> recipe_hash
        self._blueprint_recipes: Dict[str, List[str]] = {}
    
    def store_recipe(self, recipe: Recipe) -> str:
        """Store a recipe."""
        recipe_hash = self.recipes.store(recipe)
        
        # Update blueprint index
        if recipe.blueprint:
            bp_hash = recipe.blueprint.content_hash()
            if bp_hash not in self._blueprint_recipes:
                self._blueprint_recipes[bp_hash] = []
            if recipe_hash not in self._blueprint_recipes[bp_hash]:
                self._blueprint_recipes[bp_hash].append(recipe_hash)
        
        return recipe_hash
    
    def store_output(self, output: RecipeOutput, recipe_hash: Optional[str] = None) -> str:
        """Store a recipe output.

        Note: earlier versions attempted to read `output.recipe_hash`, but
        RecipeOutput is content-addressed and doesn't embed its parent recipe.
        Callers should pass `recipe_hash` explicitly when they want indexing.
        """
        output_hash = self.outputs.store(output)

        # Update recipe-output index (optional)
        if recipe_hash:
            self._recipe_outputs[recipe_hash] = output_hash

        return output_hash
    
    def get_recipe(self, recipe_hash: str) -> Optional[Recipe]:
        """Retrieve a recipe by hash."""
        return self.recipes.retrieve(recipe_hash, Recipe)
    
    def get_output(self, output_hash: str) -> Optional[RecipeOutput]:
        """Retrieve an output by hash."""
        return self.outputs.retrieve(output_hash, RecipeOutput)
    
    def get_output_for_recipe(self, recipe_hash: str) -> Optional[RecipeOutput]:
        """Get the output for a recipe if it exists."""
        output_hash = self._recipe_outputs.get(recipe_hash)
        if output_hash:
            return self.get_output(output_hash)
        return None
    
    def get_recipes_for_blueprint(self, blueprint_hash: str) -> List[Recipe]:
        """Get all recipes derived from a blueprint."""
        recipe_hashes = self._blueprint_recipes.get(blueprint_hash, [])
        recipes = []
        for h in recipe_hashes:
            recipe = self.get_recipe(h)
            if recipe:
                recipes.append(recipe)
        return recipes
    
    def has_cached_output(self, recipe_hash: str) -> bool:
        """Check if a recipe has a cached output."""
        return recipe_hash in self._recipe_outputs


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY DAG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DependencyNode:
    """A node in the dependency graph."""
    content_hash: str
    node_type: str  # 'recipe', 'output', 'certificate', etc.
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyDAG:
    """
    Directed Acyclic Graph of dependencies between artifacts.
    
    Tracks:
    - What recipes depend on what constraints
    - What outputs depend on what recipes
    - What certificates depend on what outputs
    """
    
    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
    
    def add_node(self, content_hash: str, node_type: str, **metadata) -> DependencyNode:
        """Add a node to the graph."""
        if content_hash not in self.nodes:
            self.nodes[content_hash] = DependencyNode(
                content_hash=content_hash,
                node_type=node_type,
                metadata=metadata,
            )
        return self.nodes[content_hash]
    
    def add_dependency(self, from_hash: str, to_hash: str):
        """Add a dependency edge: from_hash depends on to_hash."""
        if from_hash in self.nodes and to_hash in self.nodes:
            self.nodes[from_hash].dependencies.add(to_hash)
            self.nodes[to_hash].dependents.add(from_hash)
    
    def get_dependencies(self, content_hash: str) -> Set[str]:
        """Get all direct dependencies of a node."""
        if content_hash in self.nodes:
            return self.nodes[content_hash].dependencies
        return set()
    
    def get_dependents(self, content_hash: str) -> Set[str]:
        """Get all direct dependents of a node."""
        if content_hash in self.nodes:
            return self.nodes[content_hash].dependents
        return set()
    
    def get_all_dependencies(self, content_hash: str) -> Set[str]:
        """Get transitive closure of dependencies."""
        visited = set()
        to_visit = [content_hash]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            for dep in self.get_dependencies(current):
                if dep not in visited:
                    to_visit.append(dep)
        
        visited.discard(content_hash)  # Don't include self
        return visited
    
    def get_all_dependents(self, content_hash: str) -> Set[str]:
        """Get transitive closure of dependents."""
        visited = set()
        to_visit = [content_hash]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            for dep in self.get_dependents(current):
                if dep not in visited:
                    to_visit.append(dep)
        
        visited.discard(content_hash)
        return visited
    
    def topological_order(self) -> List[str]:
        """Return nodes in topological order (dependencies before dependents)."""
        in_degree = {h: len(n.dependencies) for h, n in self.nodes.items()}
        queue = [h for h, d in in_degree.items() if d == 0]
        order = []
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            for dependent in self.get_dependents(current):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(order) != len(self.nodes):
            raise ValueError("Cycle detected in dependency graph")
        
        return order
    
    def invalidate(self, content_hash: str) -> Set[str]:
        """
        Invalidate a node and all its dependents.
        
        Returns the set of invalidated nodes.
        """
        return self.get_all_dependents(content_hash) | {content_hash}


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LedgerEntry:
    """An entry in the append-only ledger."""
    
    timestamp: str
    operation: str  # 'store', 'compute', 'verify', 'invalidate'
    artifact_type: str
    artifact_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'operation': self.operation,
            'artifact_type': self.artifact_type,
            'artifact_hash': self.artifact_hash,
            'metadata': self.metadata,
        }


class Ledger:
    """
    Append-only ledger of all operations.
    
    Part of the Universal Invariant Spine:
    Ledger → Corridor → Proof → Replay
    
    The ledger provides:
    - Complete audit trail
    - Temporal ordering of operations
    - Basis for replay verification
    """
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        self.backend = backend or MemoryBackend()
        self.entries: List[LedgerEntry] = []
        self._sequence: int = 0
    
    def append(
        self,
        operation: str,
        artifact_type: str,
        artifact_hash: str,
        **metadata
    ) -> LedgerEntry:
        """Append an entry to the ledger."""
        entry = LedgerEntry(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            artifact_type=artifact_type,
            artifact_hash=artifact_hash,
            metadata=metadata,
        )
        
        self.entries.append(entry)
        self._sequence += 1
        
        # Persist entry
        key = f"ledger:{self._sequence:012d}"
        self.backend.put(key, pickle.dumps(entry.to_dict()))
        
        return entry
    
    def log_store(self, artifact_type: str, artifact_hash: str, **metadata):
        """Log a store operation."""
        return self.append("store", artifact_type, artifact_hash, **metadata)
    
    def log_compute(self, recipe_hash: str, output_hash: str, **metadata):
        """Log a compute operation."""
        return self.append("compute", "output", output_hash, 
                          recipe_hash=recipe_hash, **metadata)
    
    def log_verify(self, artifact_hash: str, result: str, **metadata):
        """Log a verification operation."""
        return self.append("verify", "certificate", artifact_hash,
                          result=result, **metadata)
    
    def get_history(
        self,
        artifact_hash: Optional[str] = None,
        operation: Optional[str] = None,
        since: Optional[str] = None
    ) -> List[LedgerEntry]:
        """Query ledger history."""
        results = self.entries
        
        if artifact_hash:
            results = [e for e in results if e.artifact_hash == artifact_hash]
        
        if operation:
            results = [e for e in results if e.operation == operation]
        
        if since:
            results = [e for e in results if e.timestamp >= since]
        
        return results
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __iter__(self) -> Iterator[LedgerEntry]:
        return iter(self.entries)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY (UNIFIED ACCESS)
# ═══════════════════════════════════════════════════════════════════════════════

class Registry:
    """
    Unified registry providing access to all storage components.
    
    This is the main interface for persistent storage in AtlasForge.
    """
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        self.backend = backend or MemoryBackend()
        self.store = RecipeStore(self.backend)
        self.dag = DependencyDAG()
        self.ledger = Ledger(self.backend)
    
    def register_recipe(self, recipe: Recipe) -> str:
        """Register a recipe and track dependencies."""
        recipe_hash = self.store.store_recipe(recipe)
        
        # Add to DAG
        self.dag.add_node(recipe_hash, 'recipe')
        
        # Add dependency on constraint
        if recipe.blueprint and recipe.blueprint.constraint:
            constraint_hash = recipe.blueprint.constraint.content_hash()
            self.dag.add_node(constraint_hash, 'constraint')
            self.dag.add_dependency(recipe_hash, constraint_hash)
        
        # Log
        self.ledger.log_store('recipe', recipe_hash)
        
        return recipe_hash
    
    def register_output(self, output: RecipeOutput, recipe_hash: Optional[str] = None) -> str:
        """Register an output and track dependencies.

        RecipeOutput is deliberately content-addressed and does not embed a
        parent recipe hash; pass `recipe_hash` explicitly if you want DAG +
        ledger linkage.
        """
        output_hash = self.store.store_output(output, recipe_hash=recipe_hash)
        
        # Add to DAG
        self.dag.add_node(output_hash, 'output')
        
        # Add dependency on recipe (optional)
        if recipe_hash:
            self.dag.add_dependency(output_hash, recipe_hash)
        
        # Log
        self.ledger.log_compute(recipe_hash or "", output_hash)
        
        return output_hash
    
    def lookup(self, content_hash: str) -> Optional[Any]:
        """Look up any artifact by content hash."""
        # Try each store
        recipe = self.store.get_recipe(content_hash)
        if recipe:
            return recipe
        
        output = self.store.get_output(content_hash)
        if output:
            return output
        
        return None
    
    def get_provenance(self, content_hash: str) -> Dict[str, Any]:
        """Get full provenance information for an artifact."""
        return {
            'hash': content_hash,
            'dependencies': list(self.dag.get_all_dependencies(content_hash)),
            'dependents': list(self.dag.get_all_dependents(content_hash)),
            'history': [e.to_dict() for e in self.ledger.get_history(content_hash)],
        }
