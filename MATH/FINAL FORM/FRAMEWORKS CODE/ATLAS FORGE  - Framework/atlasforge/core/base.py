"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Base Classes                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Abstract base classes that define the fundamental contracts for all objects
in the AtlasForge framework. These ensure consistent behavior for hashing,
serialization, and content-addressing across the entire system.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import (
    Any, ClassVar, Dict, Generic, List, Optional, 
    Set, Tuple, Type, TypeVar, Union
)
from datetime import datetime, timezone
import hashlib
import json
import uuid


T = TypeVar('T')
Self = TypeVar('Self', bound='AtlasObject')


class Hashable(ABC):
    """
    Protocol for objects that can produce a canonical hash.
    
    The hash must be deterministic: identical objects must produce
    identical hashes, and the hash computation must be platform-independent.
    """
    
    @abstractmethod
    def canonical_repr(self) -> str:
        """
        Produce a canonical string representation suitable for hashing.
        
        This representation must be:
        - Deterministic (same object → same string)
        - Platform-independent (same result on any system)
        - Complete (captures all semantic content)
        - Normalized (equivalent objects have identical repr)
        """
        pass
    
    def content_hash(self, algorithm: str = "sha256") -> str:
        """
        Compute the content hash of this object.
        
        Args:
            algorithm: Hash algorithm to use (default: sha256)
        
        Returns:
            Hexadecimal hash string
        """
        canonical = self.canonical_repr()
        if algorithm == "sha256":
            return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(canonical.encode('utf-8')).hexdigest()
        elif algorithm == "blake2b":
            return hashlib.blake2b(canonical.encode('utf-8')).hexdigest()
        else:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")
    
    def short_hash(self, length: int = 12) -> str:
        """
        Compute a shortened content hash for display purposes.
        
        Args:
            length: Number of hex characters to return
        
        Returns:
            Truncated hash string
        """
        return self.content_hash()[:length]


class Serializable(ABC):
    """
    Protocol for objects that can be serialized to and from JSON.
    
    Serialization must be:
    - Lossless (round-trip preserves all information)
    - Deterministic (same object → same JSON)
    - Human-readable when possible
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this object to a dictionary representation.
        
        Returns:
            Dictionary containing all object state
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls: Type[Self], data: Dict[str, Any]) -> Self:
        """
        Reconstruct an object from its dictionary representation.
        
        Args:
            data: Dictionary produced by to_dict()
        
        Returns:
            Reconstructed object
        """
        pass
    
    def to_json(self, indent: Optional[int] = None, sort_keys: bool = True) -> str:
        """
        Serialize this object to JSON string.
        
        Args:
            indent: Indentation level (None for compact)
            sort_keys: Whether to sort dictionary keys
        
        Returns:
            JSON string representation
        """
        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=sort_keys,
            default=str,
            ensure_ascii=False
        )
    
    @classmethod
    def from_json(cls: Type[Self], json_str: str) -> Self:
        """
        Deserialize an object from JSON string.
        
        Args:
            json_str: JSON string produced by to_json()
        
        Returns:
            Reconstructed object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class ContentAddressed(Hashable, Serializable):
    """
    Protocol for objects that are identified by their content hash.
    
    Content-addressed objects can be:
    - Stored and retrieved by hash
    - Verified for integrity
    - Deduplicated (identical content → same address)
    - Tamper-evident (any change → different address)
    """
    
    _cached_hash: Optional[str] = None
    
    @property
    def content_address(self) -> str:
        """
        The content address (hash) of this object.
        
        This is the primary identifier used in registries.
        """
        if self._cached_hash is None:
            self._cached_hash = self.content_hash()
        return self._cached_hash
    
    def verify_integrity(self, expected_hash: str) -> bool:
        """
        Verify that this object's content matches an expected hash.
        
        Args:
            expected_hash: The expected content hash
        
        Returns:
            True if hashes match, False otherwise
        """
        return self.content_hash() == expected_hash
    
    def invalidate_cache(self):
        """
        Invalidate the cached hash (call after mutation).
        
        Note: ContentAddressed objects should generally be immutable.
        """
        self._cached_hash = None


@dataclass
class AtlasObject(ContentAddressed):
    """
    Base class for all major objects in the AtlasForge framework.
    
    Provides:
    - Unique identifier generation
    - Creation timestamp tracking
    - Content-addressing infrastructure
    - Metadata storage
    - Version tracking
    
    Subclasses should override canonical_repr() and to_dict()/from_dict()
    to define their specific serialization behavior.
    """
    
    # Class-level type identifier
    _type_id: ClassVar[str] = "AtlasObject"
    _version: ClassVar[str] = "1.0.0"
    
    # Instance fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize cached hash to None."""
        self._cached_hash = None
    
    @property
    def type_id(self) -> str:
        """Return the type identifier for this object class."""
        return self.__class__._type_id
    
    @property
    def version(self) -> str:
        """Return the version string for this object class."""
        return self.__class__._version
    
    def canonical_repr(self) -> str:
        """
        Produce canonical string representation.
        
        Default implementation uses sorted JSON; subclasses may override
        for more efficient or specialized serialization.
        """
        # Build canonical dict excluding id and timestamps (content-only)
        content = self._canonical_content()
        return json.dumps(content, sort_keys=True, default=str, ensure_ascii=False)
    
    def _canonical_content(self) -> Dict[str, Any]:
        """
        Return the content to be included in canonical representation.
        
        Override in subclasses to customize what's included in the hash.
        By default, excludes id, created_at, and metadata.
        """
        d = self.to_dict()
        # Remove non-content fields
        d.pop('id', None)
        d.pop('created_at', None)
        d.pop('metadata', None)
        return d
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Default implementation uses dataclass fields.
        """
        return {
            '_type': self.type_id,
            '_version': self.version,
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls: Type[Self], data: Dict[str, Any]) -> Self:
        """
        Reconstruct from dictionary.
        
        Subclasses must override this with their specific construction logic.
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement from_dict()"
        )
    
    def with_metadata(self: Self, **kwargs) -> Self:
        """
        Return a copy with additional metadata.
        
        Args:
            **kwargs: Metadata key-value pairs to add
        
        Returns:
            New object with updated metadata
        """
        import copy
        new_obj = copy.deepcopy(self)
        new_obj.metadata.update(kwargs)
        new_obj.invalidate_cache()
        return new_obj
    
    def tag(self: Self, tag: str) -> Self:
        """
        Add a tag to this object's metadata.
        
        Args:
            tag: Tag string to add
        
        Returns:
            New object with tag added
        """
        tags = set(self.metadata.get('tags', []))
        tags.add(tag)
        return self.with_metadata(tags=list(tags))
    
    def has_tag(self, tag: str) -> bool:
        """Check if this object has a specific tag."""
        return tag in self.metadata.get('tags', [])
    
    def __eq__(self, other: object) -> bool:
        """
        Equality based on content hash.
        
        Two AtlasObjects are equal if they have the same content hash.
        """
        if not isinstance(other, AtlasObject):
            return NotImplemented
        return self.content_hash() == other.content_hash()
    
    def __hash__(self) -> int:
        """Hash based on content hash."""
        return hash(self.content_hash())
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.short_hash()})"


@dataclass
class ImmutableObject(AtlasObject):
    """
    Base class for immutable AtlasForge objects.
    
    Immutable objects cannot be modified after creation.
    Any "modification" returns a new object.
    """
    
    _type_id: ClassVar[str] = "ImmutableObject"
    _frozen: bool = field(default=False, init=False, repr=False)
    
    def __post_init__(self):
        super().__post_init__()
        self._frozen = True
    
    def __setattr__(self, name: str, value: Any):
        if hasattr(self, '_frozen') and self._frozen and name != '_cached_hash':
            raise AttributeError(
                f"Cannot modify immutable {self.__class__.__name__}"
            )
        super().__setattr__(name, value)


@dataclass
class VersionedObject(AtlasObject):
    """
    Base class for objects that track version history.
    
    Each modification creates a new version, maintaining
    a chain of previous versions.
    """
    
    _type_id: ClassVar[str] = "VersionedObject"
    
    version_number: int = field(default=1)
    previous_version: Optional[str] = field(default=None)  # Content hash of previous
    
    def new_version(self: Self, **changes) -> Self:
        """
        Create a new version of this object with specified changes.
        
        Args:
            **changes: Fields to change in the new version
        
        Returns:
            New version with incremented version number
        """
        import copy
        new_obj = copy.deepcopy(self)
        
        # Apply changes
        for key, value in changes.items():
            if hasattr(new_obj, key):
                setattr(new_obj, key, value)
            else:
                raise AttributeError(f"Unknown attribute: {key}")
        
        # Update version tracking
        new_obj.previous_version = self.content_hash()
        new_obj.version_number = self.version_number + 1
        new_obj.id = str(uuid.uuid4())
        new_obj.created_at = datetime.now(timezone.utc)
        new_obj.invalidate_cache()
        
        return new_obj
    
    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            'version_number': self.version_number,
            'previous_version': self.previous_version,
        })
        return d


@dataclass
class CompositeObject(AtlasObject):
    """
    Base class for objects composed of other AtlasObjects.
    
    Maintains references to child objects and ensures
    proper hash computation including children.
    """
    
    _type_id: ClassVar[str] = "CompositeObject"
    
    children: List[str] = field(default_factory=list)  # Content hashes of children
    
    def add_child(self, child: AtlasObject) -> 'CompositeObject':
        """Add a child object reference."""
        import copy
        new_obj = copy.deepcopy(self)
        new_obj.children.append(child.content_hash())
        new_obj.invalidate_cache()
        return new_obj
    
    def _canonical_content(self) -> Dict[str, Any]:
        d = super()._canonical_content()
        d['children'] = sorted(self.children)  # Sort for determinism
        return d
    
    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['children'] = self.children
        return d


# Registry for type lookup during deserialization
_TYPE_REGISTRY: Dict[str, Type[AtlasObject]] = {}


def register_type(cls: Type[AtlasObject]) -> Type[AtlasObject]:
    """
    Decorator to register a type for deserialization.
    
    Usage:
        @register_type
        class MyObject(AtlasObject):
            _type_id = "MyObject"
            ...
    """
    _TYPE_REGISTRY[cls._type_id] = cls
    return cls


def deserialize(data: Dict[str, Any]) -> AtlasObject:
    """
    Deserialize an AtlasObject from its dictionary representation.
    
    Uses the _type field to determine the correct class.
    
    Args:
        data: Dictionary with _type field
    
    Returns:
        Deserialized object
    """
    type_id = data.get('_type', 'AtlasObject')
    if type_id not in _TYPE_REGISTRY:
        raise ValueError(f"Unknown type: {type_id}")
    
    cls = _TYPE_REGISTRY[type_id]
    return cls.from_dict(data)


# Register base types
register_type(AtlasObject)
register_type(ImmutableObject)
register_type(VersionedObject)
register_type(CompositeObject)
