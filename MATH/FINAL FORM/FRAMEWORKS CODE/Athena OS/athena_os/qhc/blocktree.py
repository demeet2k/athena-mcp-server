"""
ATHENA OS - Quantum Holography Computing (QHC)
==============================================
Block-Tree Decompositions

From Quantum_Holography_Computing_(QHC).docx Chapter 3:

BLOCK-TREE:
    T = (V, E) rooted tree
    λ: V → 2^[n] labeling function
    
    Properties:
    - λ(root) = [n]
    - Children partition parent: λ(v) = ⊔ λ(children)

TILE:
    (ℋ_v, ρ_v) for node v
    ℋ_v = ⊗_{j∈λ(v)} ℂ²
    
    Local basis, compression, error descriptor

RECONSTRUCTION:
    ??_T: ∏_v ??_v → ℋ_n
    
    Recursive composition along tree
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Iterator, Any
from enum import Enum, auto

from .hilbert import HilbertSpace, StateVector, QubitIndexSet


# =============================================================================
# TREE NODE
# =============================================================================

@dataclass
class TreeNode:
    """
    Node in a block-tree.
    
    Each node v has:
    - id: unique identifier
    - label λ(v): qubit index subset
    - parent: parent node (None for root)
    - children: child nodes
    """
    
    node_id: int
    label: Set[int]  # λ(v) ⊆ [n]
    parent: Optional['TreeNode'] = None
    children: List['TreeNode'] = field(default_factory=list)
    
    # Metadata
    depth: int = 0
    
    @property
    def is_root(self) -> bool:
        return self.parent is None
    
    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    @property
    def num_qubits(self) -> int:
        """Number of qubits in this node's label."""
        return len(self.label)
    
    @property
    def local_dimension(self) -> int:
        """Dimension of local Hilbert space."""
        return 2 ** self.num_qubits
    
    def add_child(self, child: 'TreeNode') -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)
    
    def siblings(self) -> List['TreeNode']:
        """Get sibling nodes."""
        if self.parent is None:
            return []
        return [c for c in self.parent.children if c.node_id != self.node_id]
    
    def ancestors(self) -> List['TreeNode']:
        """Get all ancestors up to root."""
        result = []
        current = self.parent
        while current is not None:
            result.append(current)
            current = current.parent
        return result
    
    def descendants(self) -> List['TreeNode']:
        """Get all descendants."""
        result = []
        stack = list(self.children)
        while stack:
            node = stack.pop()
            result.append(node)
            stack.extend(node.children)
        return result
    
    def leaves(self) -> List['TreeNode']:
        """Get all leaf descendants."""
        if self.is_leaf:
            return [self]
        return [d for d in self.descendants() if d.is_leaf]
    
    def __repr__(self) -> str:
        return f"Node({self.node_id}, qubits={sorted(self.label)})"


# =============================================================================
# BLOCK-TREE
# =============================================================================

@dataclass
class BlockTree:
    """
    Block-tree decomposition of Hilbert space.
    
    T = (V, E, root) with labeling λ: V → 2^[n]
    """
    
    root: TreeNode
    n_qubits: int
    
    # Index mappings
    _nodes: Dict[int, TreeNode] = field(default_factory=dict)
    _next_id: int = 0
    
    def __post_init__(self):
        # Build node index
        self._index_tree(self.root)
    
    def _index_tree(self, node: TreeNode) -> None:
        """Index all nodes in tree."""
        self._nodes[node.node_id] = node
        for child in node.children:
            self._index_tree(child)
    
    @property
    def num_nodes(self) -> int:
        return len(self._nodes)
    
    @property
    def num_leaves(self) -> int:
        return len(self.leaves())
    
    @property
    def height(self) -> int:
        """Maximum depth of tree."""
        return max(node.depth for node in self._nodes.values())
    
    def get_node(self, node_id: int) -> Optional[TreeNode]:
        """Get node by ID."""
        return self._nodes.get(node_id)
    
    def leaves(self) -> List[TreeNode]:
        """Get all leaf nodes."""
        return [n for n in self._nodes.values() if n.is_leaf]
    
    def internal_nodes(self) -> List[TreeNode]:
        """Get all internal (non-leaf) nodes."""
        return [n for n in self._nodes.values() if not n.is_leaf]
    
    def nodes_at_depth(self, depth: int) -> List[TreeNode]:
        """Get all nodes at given depth."""
        return [n for n in self._nodes.values() if n.depth == depth]
    
    def iter_preorder(self) -> Iterator[TreeNode]:
        """Iterate nodes in preorder (root first)."""
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))
    
    def iter_postorder(self) -> Iterator[TreeNode]:
        """Iterate nodes in postorder (leaves first)."""
        result = []
        stack = [(self.root, False)]
        while stack:
            node, visited = stack.pop()
            if visited:
                result.append(node)
            else:
                stack.append((node, True))
                for child in reversed(node.children):
                    stack.append((child, False))
        return iter(result)
    
    def iter_levelorder(self) -> Iterator[TreeNode]:
        """Iterate nodes level by level (BFS)."""
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            yield node
            queue.extend(node.children)
    
    def verify_partition(self) -> bool:
        """
        Verify that children partition parent labels.
        
        For each internal node v with children {u_1,...,u_k}:
        λ(v) = λ(u_1) ⊔ λ(u_2) ⊔ ... ⊔ λ(u_k)
        """
        for node in self._nodes.values():
            if node.children:
                # Check disjoint union
                child_union = set()
                for child in node.children:
                    if child.label & child_union:
                        return False  # Not disjoint
                    child_union |= child.label
                
                if child_union != node.label:
                    return False  # Not a partition
        
        return True
    
    def verify_root_coverage(self) -> bool:
        """Verify root label is [n]."""
        expected = set(range(self.n_qubits))
        return self.root.label == expected
    
    @classmethod
    def binary_tree(cls, n_qubits: int) -> 'BlockTree':
        """
        Create balanced binary block-tree.
        
        Recursively splits qubits in half.
        """
        node_id = [0]
        
        def build(qubits: Set[int], depth: int) -> TreeNode:
            node = TreeNode(
                node_id=node_id[0],
                label=qubits,
                depth=depth
            )
            node_id[0] += 1
            
            if len(qubits) > 1:
                # Split in half
                sorted_q = sorted(qubits)
                mid = len(sorted_q) // 2
                left_q = set(sorted_q[:mid])
                right_q = set(sorted_q[mid:])
                
                left_child = build(left_q, depth + 1)
                right_child = build(right_q, depth + 1)
                
                node.add_child(left_child)
                node.add_child(right_child)
            
            return node
        
        root = build(set(range(n_qubits)), 0)
        tree = cls(root=root, n_qubits=n_qubits)
        return tree
    
    @classmethod
    def linear_tree(cls, n_qubits: int) -> 'BlockTree':
        """
        Create linear (MPS-like) block-tree.
        
        Each node has one single-qubit child and rest.
        """
        node_id = [0]
        
        def build(qubits: Set[int], depth: int) -> TreeNode:
            node = TreeNode(
                node_id=node_id[0],
                label=qubits,
                depth=depth
            )
            node_id[0] += 1
            
            if len(qubits) > 1:
                sorted_q = sorted(qubits)
                first = {sorted_q[0]}
                rest = set(sorted_q[1:])
                
                left_child = build(first, depth + 1)
                right_child = build(rest, depth + 1)
                
                node.add_child(left_child)
                node.add_child(right_child)
            
            return node
        
        root = build(set(range(n_qubits)), 0)
        tree = cls(root=root, n_qubits=n_qubits)
        return tree
    
    @classmethod
    def flat_tree(cls, n_qubits: int) -> 'BlockTree':
        """
        Create flat tree (root with all leaves).
        
        Each qubit is its own leaf.
        """
        root = TreeNode(
            node_id=0,
            label=set(range(n_qubits)),
            depth=0
        )
        
        for i in range(n_qubits):
            child = TreeNode(
                node_id=i + 1,
                label={i},
                depth=1
            )
            root.add_child(child)
        
        tree = cls(root=root, n_qubits=n_qubits)
        return tree
    
    def summary(self) -> Dict[str, Any]:
        """Get tree summary."""
        return {
            "n_qubits": self.n_qubits,
            "num_nodes": self.num_nodes,
            "num_leaves": self.num_leaves,
            "height": self.height,
            "is_valid": self.verify_partition() and self.verify_root_coverage()
        }


# =============================================================================
# BIPARTITION
# =============================================================================

@dataclass
class Bipartition:
    """
    Bipartition of qubit indices A|B.
    """
    
    left: Set[int]   # A
    right: Set[int]  # B
    
    @property
    def size_left(self) -> int:
        return len(self.left)
    
    @property
    def size_right(self) -> int:
        return len(self.right)
    
    @property
    def is_trivial(self) -> bool:
        """Check if one side is empty."""
        return len(self.left) == 0 or len(self.right) == 0
    
    def induced_by_edge(self, parent: TreeNode, child: TreeNode) -> bool:
        """Check if this bipartition is induced by tree edge."""
        child_qubits = child.label
        rest = parent.label - child_qubits
        return (self.left == child_qubits and self.right == rest) or \
               (self.right == child_qubits and self.left == rest)
    
    def __repr__(self) -> str:
        return f"{sorted(self.left)} | {sorted(self.right)}"


@dataclass
class BipartitionAnalyzer:
    """
    Analyze bipartitions induced by block-tree.
    """
    
    tree: BlockTree
    
    def edge_bipartitions(self) -> List[Bipartition]:
        """
        Get all bipartitions induced by tree edges.
        
        Each edge (v, child) induces bipartition λ(child) | rest.
        """
        result = []
        for node in self.tree._nodes.values():
            for child in node.children:
                left = child.label
                right = self.tree.root.label - left
                result.append(Bipartition(left, right))
        return result
    
    def cut_weight(self, bipartition: Bipartition) -> int:
        """
        Compute cut weight (number of edges crossing bipartition).
        
        Simplified: returns min(|A|, |B|) as proxy.
        """
        return min(len(bipartition.left), len(bipartition.right))
    
    def max_cut_weight(self) -> int:
        """Maximum cut weight across all edge bipartitions."""
        biparts = self.edge_bipartitions()
        if not biparts:
            return 0
        return max(self.cut_weight(b) for b in biparts)


# =============================================================================
# PARTITION OPERATIONS
# =============================================================================

@dataclass
class PartitionOperations:
    """
    Operations on block-tree partitions.
    """
    
    @staticmethod
    def refine(tree: BlockTree, node: TreeNode, 
               new_labels: List[Set[int]]) -> BlockTree:
        """
        Refine a node by splitting it into multiple children.
        """
        # Verify partition
        union = set()
        for label in new_labels:
            if union & label:
                raise ValueError("New labels must be disjoint")
            union |= label
        
        if union != node.label:
            raise ValueError("New labels must cover original label")
        
        # Remove existing children
        old_children = list(node.children)
        node.children = []
        
        # Add new children
        next_id = max(n.node_id for n in tree._nodes.values()) + 1
        for label in new_labels:
            child = TreeNode(
                node_id=next_id,
                label=label,
                depth=node.depth + 1
            )
            node.add_child(child)
            tree._nodes[next_id] = child
            next_id += 1
        
        return tree
    
    @staticmethod
    def coarsen(tree: BlockTree, nodes: List[TreeNode]) -> BlockTree:
        """
        Coarsen by merging sibling nodes.
        """
        if not nodes:
            return tree
        
        # Verify all siblings
        parent = nodes[0].parent
        if parent is None:
            raise ValueError("Cannot merge root")
        
        for node in nodes[1:]:
            if node.parent != parent:
                raise ValueError("Nodes must be siblings")
        
        # Merge labels
        merged_label = set()
        for node in nodes:
            merged_label |= node.label
        
        # Remove old nodes
        for node in nodes:
            parent.children.remove(node)
            del tree._nodes[node.node_id]
        
        # Add merged node
        next_id = max(n.node_id for n in tree._nodes.values()) + 1
        merged = TreeNode(
            node_id=next_id,
            label=merged_label,
            depth=parent.depth + 1
        )
        parent.add_child(merged)
        tree._nodes[next_id] = merged
        
        return tree


# =============================================================================
# VALIDATION
# =============================================================================

def validate_blocktree() -> bool:
    """Validate block-tree module."""
    
    # Test TreeNode
    root = TreeNode(node_id=0, label={0, 1, 2, 3})
    child1 = TreeNode(node_id=1, label={0, 1})
    child2 = TreeNode(node_id=2, label={2, 3})
    root.add_child(child1)
    root.add_child(child2)
    
    assert root.is_root
    assert not child1.is_root
    assert child1.is_leaf
    assert child1.depth == 1
    
    # Test BlockTree factories
    binary = BlockTree.binary_tree(4)
    assert binary.n_qubits == 4
    assert binary.verify_partition()
    assert binary.verify_root_coverage()
    
    linear = BlockTree.linear_tree(4)
    assert linear.verify_partition()
    
    flat = BlockTree.flat_tree(4)
    assert flat.num_leaves == 4
    assert flat.verify_partition()
    
    # Test iteration
    preorder = list(binary.iter_preorder())
    postorder = list(binary.iter_postorder())
    assert len(preorder) == binary.num_nodes
    assert len(postorder) == binary.num_nodes
    
    # Test bipartitions
    analyzer = BipartitionAnalyzer(binary)
    biparts = analyzer.edge_bipartitions()
    assert len(biparts) > 0
    
    return True


if __name__ == "__main__":
    print("Validating QHC Block-Tree Module...")
    assert validate_blocktree()
    print("✓ Block-Tree module validated")
    
    # Demo
    print("\n=== QHC Block-Tree Demo ===")
    
    # Binary tree for 8 qubits
    tree = BlockTree.binary_tree(8)
    summary = tree.summary()
    
    print(f"\nBinary Block-Tree for {tree.n_qubits} qubits:")
    print(f"  Nodes: {summary['num_nodes']}")
    print(f"  Leaves: {summary['num_leaves']}")
    print(f"  Height: {summary['height']}")
    print(f"  Valid: {summary['is_valid']}")
    
    # Show structure
    print("\nTree structure (preorder):")
    for node in tree.iter_preorder():
        indent = "  " * node.depth
        print(f"{indent}Node {node.node_id}: qubits {sorted(node.label)}")
    
    # Bipartitions
    analyzer = BipartitionAnalyzer(tree)
    biparts = analyzer.edge_bipartitions()
    print(f"\nEdge-induced bipartitions: {len(biparts)}")
    for bp in biparts[:3]:
        print(f"  {bp} (cut weight: {analyzer.cut_weight(bp)})")
