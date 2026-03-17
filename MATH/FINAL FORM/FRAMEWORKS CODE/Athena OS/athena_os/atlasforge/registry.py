"""
ATHENA OS - AtlasForge
======================
Recipe Registry: DAG-Based Artifact Store

From AtlasForge.docx §19:

REGISTRY INVARIANTS:
    1. Immutability by content addressing
    2. Verifier-gated promotion
    3. DAG compositionality
    4. Generator-first storage
    5. Atomicity and crash consistency

OPERATIONS:
    - Put: store recipe → id
    - Get: retrieve by id
    - Has: check existence
    - Query: search by features

DEPENDENCY DAG:
    Recipes form DAG via explicit dependencies.
    Verified artifacts can be reused as dependencies.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import hashlib
import json
import time

from .recipes import Recipe, ProofPack


# =============================================================================
# VERIFICATION STATUS
# =============================================================================

class VerificationStatus(Enum):
    """Recipe verification states."""
    
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    REVOKED = "revoked"


# =============================================================================
# INDEX KEYS
# =============================================================================

@dataclass
class IndexKeys:
    """
    Index basis for registry queries.
    """
    
    # Identity
    recipe_id: str = ""
    schema_version: str = ""
    
    # Constraint signature
    constraint_type: str = ""
    constraint_hash: str = ""
    
    # Chart keys
    chart_kinds: List[str] = field(default_factory=list)
    
    # Obligation keys
    required_obligations: List[str] = field(default_factory=list)
    
    # Outcome keys
    verification_status: str = ""
    certificate_levels: List[int] = field(default_factory=list)
    
    # Domain keys
    domain_kind: str = ""
    
    @classmethod
    def from_recipe(cls, recipe: Recipe) -> 'IndexKeys':
        """Extract index keys from recipe."""
        keys = cls(
            recipe_id=recipe.recipe_id,
            schema_version=recipe.schema_version,
            verification_status=recipe.verification_status
        )
        
        if recipe.ir:
            keys.constraint_type = recipe.ir.normal_form
            keys.required_obligations = [
                o["type"] for o in recipe.ir.obligations
            ]
        
        if recipe.domain:
            keys.domain_kind = recipe.domain.kind.value
        
        if recipe.proofpack:
            keys.certificate_levels = [
                c.level.value for c in recipe.proofpack.certificates
            ]
        
        return keys


# =============================================================================
# REGISTRY ENTRY
# =============================================================================

@dataclass
class RegistryEntry:
    """
    A single entry in the registry.
    """
    
    recipe: Recipe
    status: VerificationStatus = VerificationStatus.UNVERIFIED
    
    # Index keys
    index: IndexKeys = None
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    verified_at: Optional[float] = None
    
    # Provenance
    parent_id: Optional[str] = None  # For migrations
    
    def __post_init__(self):
        if self.index is None:
            self.index = IndexKeys.from_recipe(self.recipe)
    
    @property
    def recipe_id(self) -> str:
        return self.recipe.recipe_id
    
    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================

@dataclass
class DependencyGraph:
    """
    DAG of recipe dependencies.
    """
    
    # Adjacency: recipe_id → list of dependency ids
    edges: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_recipe(self, recipe_id: str, dependencies: List[str] = None) -> None:
        """Add recipe to graph."""
        self.edges[recipe_id] = dependencies or []
    
    def get_dependencies(self, recipe_id: str) -> List[str]:
        """Get direct dependencies."""
        return self.edges.get(recipe_id, [])
    
    def get_all_dependencies(self, recipe_id: str) -> Set[str]:
        """Get transitive closure of dependencies."""
        result = set()
        queue = self.get_dependencies(recipe_id)
        
        while queue:
            dep = queue.pop(0)
            if dep not in result:
                result.add(dep)
                queue.extend(self.get_dependencies(dep))
        
        return result
    
    def get_dependents(self, recipe_id: str) -> List[str]:
        """Get recipes that depend on this one."""
        return [
            rid for rid, deps in self.edges.items()
            if recipe_id in deps
        ]
    
    def is_acyclic(self) -> bool:
        """Check if graph is DAG (no cycles)."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for dep in self.get_dependencies(node):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.edges:
            if node not in visited:
                if has_cycle(node):
                    return False
        
        return True
    
    def topological_sort(self) -> List[str]:
        """Topological ordering of recipes."""
        in_degree = {node: 0 for node in self.edges}
        
        for deps in self.edges.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] = in_degree.get(dep, 0)
        
        # Actually compute in-degrees properly
        for node, deps in self.edges.items():
            for dep in deps:
                if dep not in in_degree:
                    in_degree[dep] = 0
        
        for node, deps in self.edges.items():
            for dep in deps:
                pass  # deps are what node depends on
        
        # Kahn's algorithm
        queue = [n for n, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for dependent in self.get_dependents(node):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result


# =============================================================================
# REGISTRY
# =============================================================================

@dataclass
class Registry:
    """
    Content-addressed recipe registry.
    
    Append-only store with verification gating.
    """
    
    # Main storage: recipe_id → entry
    entries: Dict[str, RegistryEntry] = field(default_factory=dict)
    
    # Dependency graph
    dag: DependencyGraph = field(default_factory=DependencyGraph)
    
    # Indices
    by_constraint_type: Dict[str, Set[str]] = field(default_factory=dict)
    by_status: Dict[str, Set[str]] = field(default_factory=dict)
    by_domain_kind: Dict[str, Set[str]] = field(default_factory=dict)
    
    def put(self, recipe: Recipe) -> str:
        """
        Store recipe and return id.
        
        Enforces content-addressing.
        """
        recipe_id = recipe.recipe_id
        
        # Check for duplicate
        if recipe_id in self.entries:
            return recipe_id
        
        # Create entry
        entry = RegistryEntry(recipe=recipe)
        
        # Check dependencies exist
        for dep_id in recipe.dependencies:
            if dep_id not in self.entries:
                raise ValueError(f"Missing dependency: {dep_id}")
        
        # Store
        self.entries[recipe_id] = entry
        
        # Update DAG
        self.dag.add_recipe(recipe_id, recipe.dependencies)
        
        # Update indices
        self._index_entry(entry)
        
        return recipe_id
    
    def _index_entry(self, entry: RegistryEntry) -> None:
        """Add entry to indices."""
        recipe_id = entry.recipe_id
        index = entry.index
        
        # By constraint type
        if index.constraint_type:
            if index.constraint_type not in self.by_constraint_type:
                self.by_constraint_type[index.constraint_type] = set()
            self.by_constraint_type[index.constraint_type].add(recipe_id)
        
        # By status
        status = entry.status.value
        if status not in self.by_status:
            self.by_status[status] = set()
        self.by_status[status].add(recipe_id)
        
        # By domain kind
        if index.domain_kind:
            if index.domain_kind not in self.by_domain_kind:
                self.by_domain_kind[index.domain_kind] = set()
            self.by_domain_kind[index.domain_kind].add(recipe_id)
    
    def get(self, recipe_id: str) -> Optional[Recipe]:
        """Retrieve recipe by id."""
        entry = self.entries.get(recipe_id)
        return entry.recipe if entry else None
    
    def has(self, recipe_id: str) -> bool:
        """Check if recipe exists."""
        return recipe_id in self.entries
    
    def verify(self, recipe_id: str) -> bool:
        """
        Mark recipe as verified.
        
        Returns success status.
        """
        if recipe_id not in self.entries:
            return False
        
        entry = self.entries[recipe_id]
        
        # Check proofpack
        if not entry.recipe.proofpack.is_verified:
            entry.status = VerificationStatus.FAILED
            return False
        
        # Check dependencies are verified
        for dep_id in entry.recipe.dependencies:
            dep_entry = self.entries.get(dep_id)
            if not dep_entry or not dep_entry.is_verified:
                entry.status = VerificationStatus.FAILED
                return False
        
        # Mark verified
        entry.status = VerificationStatus.VERIFIED
        entry.verified_at = time.time()
        
        # Update index
        self.by_status["unverified"].discard(recipe_id)
        if "verified" not in self.by_status:
            self.by_status["verified"] = set()
        self.by_status["verified"].add(recipe_id)
        
        return True
    
    def query(self, 
              constraint_type: str = None,
              status: str = None,
              domain_kind: str = None) -> List[str]:
        """
        Query recipes by features.
        """
        results = set(self.entries.keys())
        
        if constraint_type:
            results &= self.by_constraint_type.get(constraint_type, set())
        
        if status:
            results &= self.by_status.get(status, set())
        
        if domain_kind:
            results &= self.by_domain_kind.get(domain_kind, set())
        
        return list(results)
    
    def get_verified(self) -> List[str]:
        """Get all verified recipe ids."""
        return list(self.by_status.get("verified", set()))
    
    @property
    def count(self) -> int:
        """Total recipe count."""
        return len(self.entries)
    
    @property
    def verified_count(self) -> int:
        """Verified recipe count."""
        return len(self.by_status.get("verified", set()))
    
    def export(self) -> Dict[str, Any]:
        """Export registry state."""
        return {
            "count": self.count,
            "verified_count": self.verified_count,
            "recipes": [
                {
                    "id": e.recipe_id,
                    "status": e.status.value,
                    "constraint": e.index.constraint_type,
                    "dependencies": e.recipe.dependencies
                }
                for e in self.entries.values()
            ]
        }


# =============================================================================
# VERIFIED CORPUS
# =============================================================================

@dataclass
class VerifiedCorpus:
    """
    Collection of verified recipes for reuse.
    """
    
    registry: Registry = field(default_factory=Registry)
    
    # Guarantees extracted from verified recipes
    guarantees: Dict[str, Set[str]] = field(default_factory=dict)
    
    def add_recipe(self, recipe: Recipe) -> str:
        """Add and verify recipe."""
        recipe_id = self.registry.put(recipe)
        
        if recipe.proofpack.is_verified:
            self.registry.verify(recipe_id)
            self._extract_guarantees(recipe_id)
        
        return recipe_id
    
    def _extract_guarantees(self, recipe_id: str) -> None:
        """Extract guarantees from verified recipe."""
        recipe = self.registry.get(recipe_id)
        if not recipe:
            return
        
        self.guarantees[recipe_id] = set()
        
        for cert in recipe.proofpack.certificates:
            if cert.is_verified:
                self.guarantees[recipe_id].add(cert.cert_type.value)
    
    def can_use_guarantee(self, recipe_id: str, 
                         guarantee_type: str) -> bool:
        """Check if guarantee is available from recipe."""
        return guarantee_type in self.guarantees.get(recipe_id, set())
    
    def get_recipes_with_guarantee(self, guarantee_type: str) -> List[str]:
        """Find recipes providing specific guarantee."""
        return [
            rid for rid, guarantees in self.guarantees.items()
            if guarantee_type in guarantees
        ]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_registry() -> bool:
    """Validate registry module."""
    
    from .recipes import Recipe, RecipeOutput, SolvePlan, ProofPack, Certificate, CertificateLevel
    from .constraints import CertificateType
    
    # Create test recipes
    recipe1 = Recipe(
        blueprint_hash="hash1",
        plan=SolvePlan(),
        output=RecipeOutput(output_type="scalar", value=1.0)
    )
    
    recipe2 = Recipe(
        blueprint_hash="hash2",
        plan=SolvePlan(),
        output=RecipeOutput(output_type="scalar", value=2.0)
    )
    
    # Add certificates to make verifiable
    recipe1.proofpack.add_certificate(
        Certificate(CertificateType.ENCLOSURE, CertificateLevel.LEVEL_2)
    )
    recipe2.proofpack.add_certificate(
        Certificate(CertificateType.CORRIDOR, CertificateLevel.LEVEL_2)
    )
    recipe2.dependencies.append(recipe1.recipe_id)
    
    # Test Registry
    registry = Registry()
    
    id1 = registry.put(recipe1)
    assert registry.has(id1)
    assert registry.get(id1) == recipe1
    
    # Verify first
    assert registry.verify(id1)
    
    # Now can add dependent
    id2 = registry.put(recipe2)
    assert registry.verify(id2)
    
    # Test query
    verified = registry.query(status="verified")
    assert len(verified) == 2
    
    # Test DependencyGraph
    deps = registry.dag.get_dependencies(id2)
    assert id1 in deps
    
    all_deps = registry.dag.get_all_dependencies(id2)
    assert id1 in all_deps
    
    assert registry.dag.is_acyclic()
    
    # Test IndexKeys
    keys = IndexKeys.from_recipe(recipe1)
    assert keys.recipe_id == id1
    
    # Test VerifiedCorpus
    corpus = VerifiedCorpus()
    corpus.add_recipe(recipe1)
    
    assert corpus.registry.verified_count == 1
    
    return True


if __name__ == "__main__":
    print("Validating AtlasForge Registry...")
    assert validate_registry()
    print("✓ Registry module validated")
