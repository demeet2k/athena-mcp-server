"""
ATHENA OS - Q-SHRINK CONTAINER SYSTEM
=====================================
Container Topology, Repair, and Seek Legality (Chapters 13-15)

The container is a LENS ENGINE with:
- Locally survivable chunks with self-repair prefix
- Self-delimiting payload spans
- Checksums for integrity
- Direct-sum topology (independent items)
- Kronecker topology (coupled streams)
- Seek lattices for random access
- Multi-root archives

CONTAINER INVARIANTS:
1. Determinism: legal bitstream → unique decode
2. Bounded damage: corruption is locally contained
3. Seek legality: random access requires seek lattice
4. Streaming legality: monotone parsing with bounded lookahead
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
import hashlib
import struct
from datetime import datetime

from .lenses import SeekLattice, LensType


# =============================================================================
# CONTAINER TOPOLOGY TYPES
# =============================================================================

class TopologyType(Enum):
    """Container topology types."""
    
    DIRECT_SUM = "direct_sum"     # Independent items (file trees)
    KRONECKER = "kronecker"       # Coupled streams (synchronized AV)
    HYBRID = "hybrid"             # Mixed topology


class ChunkType(Enum):
    """Standard chunk types."""
    
    # Header chunks
    MAGIC = "QSHR"          # Magic number
    VERSION = "VERS"        # Version info
    MANIFEST = "MNFT"       # Manifest/TOC
    
    # Data chunks
    BULK = "BULK"           # Bulk coefficients
    ESCAPE = "ESCP"         # Escape coefficients
    TAGS = "TAGS"           # Tag stream
    
    # Metadata chunks
    SEEK = "SEEK"           # Seek lattice
    INDEX = "INDX"          # Index table
    HASH = "HASH"           # Content hashes
    
    # Control chunks
    REPAIR = "REPR"         # Repair prefix
    ECC = "ECCD"            # Error correction
    END = "ENDS"            # End marker


class AccessMode(Enum):
    """Stream access modes."""
    
    STREAM_ONLY = 0         # Forward decode only
    SEEKABLE_LINEAR = 1     # Seek via linear scan
    SEEKABLE_INDEXED = 2    # Fast indexed seek


TOPOLOGY_TYPE_CODES = {
    TopologyType.DIRECT_SUM: 0,
    TopologyType.KRONECKER: 1,
    TopologyType.HYBRID: 2,
}
TOPOLOGY_CODE_TYPES = {value: key for key, value in TOPOLOGY_TYPE_CODES.items()}


# =============================================================================
# CHUNK STRUCTURES
# =============================================================================

@dataclass
class ChunkHeader:
    """
    Chunk header with self-repair capability.
    
    Layout (16 bytes):
    - type: 4 bytes (chunk type)
    - length: 4 bytes (payload length)
    - checksum: 4 bytes (CRC32)
    - flags: 2 bytes (compression, encryption, etc.)
    - reserved: 2 bytes
    """
    
    chunk_type: ChunkType
    payload_length: int
    checksum: int  # CRC32
    flags: int = 0
    
    HEADER_SIZE = 16
    
    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        type_bytes = self.chunk_type.value.encode('ascii')[:4].ljust(4, b'\x00')
        return struct.pack(
            '<4sIIHH',
            type_bytes,
            self.payload_length,
            self.checksum,
            self.flags,
            0  # reserved
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ChunkHeader':
        """Deserialize header from bytes."""
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Insufficient header data")
        
        type_bytes, length, checksum, flags, _ = struct.unpack('<4sIIHH', data[:16])
        type_str = type_bytes.decode('ascii').rstrip('\x00')
        
        # Find matching chunk type
        chunk_type = ChunkType.BULK  # Default
        for ct in ChunkType:
            if ct.value == type_str:
                chunk_type = ct
                break
        
        return cls(
            chunk_type=chunk_type,
            payload_length=length,
            checksum=checksum,
            flags=flags
        )
    
    def verify_payload(self, payload: bytes) -> bool:
        """Verify payload against checksum."""
        computed = self._compute_crc32(payload)
        return computed == self.checksum
    
    @staticmethod
    def _compute_crc32(data: bytes) -> int:
        """Compute CRC32 checksum."""
        import zlib
        return zlib.crc32(data) & 0xFFFFFFFF


@dataclass
class Chunk:
    """A container chunk with header and payload."""
    
    header: ChunkHeader
    payload: bytes
    offset: int = 0  # Offset in container
    
    def to_bytes(self) -> bytes:
        """Serialize complete chunk."""
        return self.header.to_bytes() + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> Tuple['Chunk', int]:
        """
        Deserialize chunk from bytes.
        
        Returns (chunk, bytes_consumed).
        """
        header = ChunkHeader.from_bytes(data)
        payload_start = ChunkHeader.HEADER_SIZE
        payload_end = payload_start + header.payload_length
        
        if len(data) < payload_end:
            raise ValueError("Insufficient payload data")
        
        payload = data[payload_start:payload_end]
        
        chunk = cls(header=header, payload=payload, offset=offset)
        return chunk, payload_end
    
    def verify(self) -> bool:
        """Verify chunk integrity."""
        return self.header.verify_payload(self.payload)
    
    @property
    def total_size(self) -> int:
        """Total chunk size including header."""
        return ChunkHeader.HEADER_SIZE + len(self.payload)


# =============================================================================
# REPAIR SYSTEM
# =============================================================================

@dataclass
class RepairPrefix:
    """
    Compact self-repair prefix for error correction.
    
    Stores redundant information to correct small header errors.
    """
    
    header_copy: bytes  # Redundant header copy
    parity: bytes       # Parity bytes for correction
    
    PREFIX_SIZE = 32
    
    def to_bytes(self) -> bytes:
        """Serialize repair prefix."""
        data = self.header_copy[:16] + self.parity[:16]
        return data.ljust(self.PREFIX_SIZE, b'\x00')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'RepairPrefix':
        """Deserialize repair prefix."""
        return cls(
            header_copy=data[:16],
            parity=data[16:32]
        )
    
    @classmethod
    def create_for_header(cls, header: ChunkHeader) -> 'RepairPrefix':
        """Create repair prefix for a header."""
        header_bytes = header.to_bytes()
        # Simple XOR parity
        parity = bytes(b ^ 0xFF for b in header_bytes)
        return cls(header_copy=header_bytes, parity=parity)
    
    def repair_header(self, corrupted: bytes) -> Optional[bytes]:
        """
        Attempt to repair a corrupted header.
        
        Returns repaired header or None if unrepairable.
        """
        # Check if repair copy matches expected
        if corrupted == self.header_copy:
            return corrupted  # Already correct
        
        # Try to repair using parity
        repaired = bytes(c ^ p ^ 0xFF for c, p in zip(corrupted, self.parity))
        
        # Verify repair
        if repaired == self.header_copy:
            return repaired
        
        return None


# =============================================================================
# SEEK SYSTEM
# =============================================================================

@dataclass
class SeekEntry:
    """Entry in seek lattice."""
    
    unit_id: int          # Unit identifier
    byte_offset: int      # Byte offset in container
    payload_length: int   # Payload length
    dependency_ids: List[int] = field(default_factory=list)  # Dependencies
    
    def to_bytes(self) -> bytes:
        """Serialize seek entry."""
        n_deps = len(self.dependency_ids)
        deps_data = struct.pack(f'<{n_deps}I', *self.dependency_ids) if n_deps > 0 else b''
        return struct.pack('<IQI', self.unit_id, self.byte_offset, self.payload_length) + \
               struct.pack('<H', n_deps) + deps_data
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Tuple['SeekEntry', int]:
        """Deserialize seek entry."""
        unit_id, offset, length = struct.unpack('<IQI', data[:16])
        n_deps = struct.unpack('<H', data[16:18])[0]
        
        deps = []
        if n_deps > 0:
            deps = list(struct.unpack(f'<{n_deps}I', data[18:18 + n_deps*4]))
        
        entry = cls(
            unit_id=unit_id,
            byte_offset=offset,
            payload_length=length,
            dependency_ids=deps
        )
        
        return entry, 18 + n_deps * 4


class SeekTable:
    """
    Seek table for random access.
    
    Supports parity compression for reduced metadata size.
    """
    
    def __init__(self, use_parity: bool = True):
        self.use_parity = use_parity
        self._entries: List[SeekEntry] = []
        self._by_id: Dict[int, SeekEntry] = {}
    
    def add_entry(self, entry: SeekEntry) -> None:
        """Add a seek entry."""
        self._entries.append(entry)
        self._by_id[entry.unit_id] = entry
    
    def lookup(self, unit_id: int) -> Optional[SeekEntry]:
        """Look up entry by unit ID."""
        return self._by_id.get(unit_id)
    
    def get_dependency_closure(self, unit_id: int) -> Set[int]:
        """Get complete dependency closure for unit."""
        closure = set()
        to_process = [unit_id]
        
        while to_process:
            current = to_process.pop()
            if current in closure:
                continue
            
            closure.add(current)
            entry = self._by_id.get(current)
            if entry:
                to_process.extend(entry.dependency_ids)
        
        return closure
    
    def to_bytes(self) -> bytes:
        """Serialize seek table."""
        data = struct.pack('<I', len(self._entries))
        
        for entry in self._entries:
            data += entry.to_bytes()
        
        # Add checksum
        checksum = hashlib.sha256(data).digest()[:8]
        return data + checksum
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'SeekTable':
        """Deserialize seek table."""
        n_entries = struct.unpack('<I', data[:4])[0]
        
        table = cls()
        offset = 4
        
        for _ in range(n_entries):
            entry, consumed = SeekEntry.from_bytes(data[offset:])
            table.add_entry(entry)
            offset += consumed
        
        return table
    
    def to_seek_lattice(self) -> SeekLattice:
        """Convert to SeekLattice lens."""
        entries = [(e.byte_offset, e.payload_length) for e in self._entries]
        return SeekLattice(entries=entries)


# =============================================================================
# CONTAINER STRUCTURE
# =============================================================================

@dataclass
class ContainerManifest:
    """
    Container manifest (table of contents).
    """
    
    version: Tuple[int, int, int] = (1, 0, 0)
    topology: TopologyType = TopologyType.DIRECT_SUM
    access_mode: AccessMode = AccessMode.STREAM_ONLY
    
    n_domains: int = 1
    n_chunks: int = 0
    total_size: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)
    
    # Domain metadata
    domain_types: List[str] = field(default_factory=list)
    domain_offsets: List[int] = field(default_factory=list)
    
    # Content hashes
    content_hash: str = ""

    HEADER_FORMAT = '<3sBBIIQ'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    DOMAIN_TYPE_SIZE = 16
    HASH_SIZE = 64
    
    def to_bytes(self) -> bytes:
        """Serialize manifest."""
        version_bytes = struct.pack('<BBB', *self.version)
        self.n_domains = max(self.n_domains, len(self.domain_types))
        padded_offsets = list(self.domain_offsets)
        if len(padded_offsets) < self.n_domains:
            padded_offsets.extend([0] * (self.n_domains - len(padded_offsets)))
        
        header = struct.pack(
            self.HEADER_FORMAT,
            version_bytes,
            TOPOLOGY_TYPE_CODES.get(self.topology, 0),
            int(self.access_mode.value),
            self.n_domains,
            self.n_chunks,
            self.total_size
        )
        
        # Serialize domain info
        domain_data = b''
        for dtype, doffset in zip(self.domain_types[:self.n_domains], padded_offsets[:self.n_domains]):
            dtype_bytes = dtype.encode()[:self.DOMAIN_TYPE_SIZE].ljust(self.DOMAIN_TYPE_SIZE, b'\x00')
            domain_data += dtype_bytes + struct.pack('<Q', doffset)
        
        # Content hash
        hash_bytes = self.content_hash.encode('ascii', errors='ignore')[:self.HASH_SIZE].ljust(self.HASH_SIZE, b'\x00')
        
        return header + domain_data + hash_bytes
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ContainerManifest':
        """Deserialize manifest."""
        if len(data) < cls.HEADER_SIZE + cls.HASH_SIZE:
            raise ValueError("Insufficient manifest data")
        version_bytes, topo_code, access_byte, n_domains, n_chunks, total_size = struct.unpack(
            cls.HEADER_FORMAT, data[:cls.HEADER_SIZE]
        )
        version = tuple(version_bytes)

        manifest = cls(
            version=version,
            topology=TOPOLOGY_CODE_TYPES.get(topo_code, TopologyType.DIRECT_SUM),
            access_mode=AccessMode(access_byte) if access_byte in {mode.value for mode in AccessMode} else AccessMode.STREAM_ONLY,
            n_domains=n_domains,
            n_chunks=n_chunks,
            total_size=total_size
        )

        offset = cls.HEADER_SIZE
        for _ in range(n_domains):
            if len(data) < offset + cls.DOMAIN_TYPE_SIZE + 8:
                raise ValueError("Insufficient domain metadata in manifest")
            dtype = data[offset:offset + cls.DOMAIN_TYPE_SIZE].rstrip(b'\x00').decode('utf-8', errors='ignore') or "domain"
            offset += cls.DOMAIN_TYPE_SIZE
            doffset = struct.unpack('<Q', data[offset:offset + 8])[0]
            offset += 8
            manifest.domain_types.append(dtype)
            manifest.domain_offsets.append(doffset)

        hash_end = offset + cls.HASH_SIZE
        if len(data) < hash_end:
            raise ValueError("Insufficient manifest hash data")
        manifest.content_hash = data[offset:hash_end].rstrip(b'\x00').decode('ascii', errors='ignore')
        
        return manifest


@dataclass
class Domain:
    """
    A domain within the container.
    
    Represents a logical unit (file, stream, asset).
    """
    
    domain_id: int
    domain_type: str
    chunks: List[Chunk] = field(default_factory=list)
    seek_table: Optional[SeekTable] = None
    
    access_mode: AccessMode = AccessMode.STREAM_ONLY
    
    def add_chunk(self, chunk: Chunk) -> None:
        """Add chunk to domain."""
        self.chunks.append(chunk)
    
    def total_size(self) -> int:
        """Total size of domain."""
        return sum(c.total_size for c in self.chunks)
    
    def verify_all(self) -> Tuple[bool, List[int]]:
        """
        Verify all chunks.
        
        Returns (all_valid, list_of_invalid_indices).
        """
        invalid = []
        for i, chunk in enumerate(self.chunks):
            if not chunk.verify():
                invalid.append(i)
        
        return len(invalid) == 0, invalid


class QShrinkContainer:
    """
    Complete Q-SHRINK Container.
    
    A robust, seekable, repairable container for compressed data.
    """
    
    MAGIC = b'QSHR'
    VERSION = (1, 0, 0)
    
    def __init__(self, topology: TopologyType = TopologyType.DIRECT_SUM):
        self.topology = topology
        self.manifest = ContainerManifest(topology=topology)
        self.domains: List[Domain] = []
        self._global_seek_table = SeekTable()
    
    def add_domain(self, domain: Domain) -> int:
        """Add domain to container."""
        domain_id = len(self.domains)
        domain.domain_id = domain_id
        self.domains.append(domain)
        
        self.manifest.n_domains = len(self.domains)
        self.manifest.domain_types.append(domain.domain_type)
        
        return domain_id
    
    def build_seek_table(self) -> None:
        """Build global seek table from all domains."""
        unit_id = 0
        current_offset = 0
        
        for domain in self.domains:
            for chunk in domain.chunks:
                chunk.offset = current_offset
                entry = SeekEntry(
                    unit_id=unit_id,
                    byte_offset=current_offset,
                    payload_length=chunk.header.payload_length
                )
                self._global_seek_table.add_entry(entry)
                
                current_offset += chunk.total_size
                unit_id += 1
        
        self.manifest.access_mode = AccessMode.SEEKABLE_INDEXED
    
    def serialize(self) -> bytes:
        """Serialize complete container."""
        self.manifest.topology = self.topology
        self.manifest.n_domains = len(self.domains)
        self.manifest.n_chunks = sum(len(domain.chunks) for domain in self.domains)
        self.manifest.domain_types = [domain.domain_type for domain in self.domains]
        self.manifest.domain_offsets = [0] * len(self.domains)

        if self.manifest.access_mode == AccessMode.SEEKABLE_INDEXED:
            self.build_seek_table()

        domain_blobs = [b''.join(chunk.to_bytes() for chunk in domain.chunks) for domain in self.domains]

        if self.manifest.access_mode == AccessMode.SEEKABLE_INDEXED:
            seek_bytes = self._global_seek_table.to_bytes()
        else:
            seek_bytes = b''

        self.manifest.total_size = 0
        self.manifest.content_hash = ""
        manifest_bytes = self.manifest.to_bytes()
        preamble_size = 4 + 3 + 4 + len(manifest_bytes) + 4 + len(seek_bytes)
        domain_offsets = []
        cursor = preamble_size
        for blob in domain_blobs:
            domain_offsets.append(cursor)
            cursor += len(blob)
        self.manifest.domain_offsets = domain_offsets
        self.manifest.content_hash = hashlib.sha256(b"".join(domain_blobs)).hexdigest()
        manifest_bytes = self.manifest.to_bytes()

        end_chunk = Chunk(
            header=ChunkHeader(
                chunk_type=ChunkType.END,
                payload_length=0,
                checksum=0
            ),
            payload=b''
        )
        end_bytes = end_chunk.to_bytes()

        data = b''.join(
            [
                self.MAGIC,
                struct.pack('<BBB', *self.VERSION),
                struct.pack('<I', len(manifest_bytes)),
                manifest_bytes,
                struct.pack('<I', len(seek_bytes)),
                seek_bytes,
                *domain_blobs,
                end_bytes,
            ]
        )

        self.manifest.total_size = len(data)
        manifest_bytes = self.manifest.to_bytes()
        data = b''.join(
            [
                self.MAGIC,
                struct.pack('<BBB', *self.VERSION),
                struct.pack('<I', len(manifest_bytes)),
                manifest_bytes,
                struct.pack('<I', len(seek_bytes)),
                seek_bytes,
                *domain_blobs,
                end_bytes,
            ]
        )

        return data
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'QShrinkContainer':
        """Deserialize container from bytes."""
        offset = 0
        
        # Verify magic
        magic = data[offset:offset+4]
        if magic != cls.MAGIC:
            raise ValueError(f"Invalid magic: {magic}")
        offset += 4
        
        # Version
        version = struct.unpack('<BBB', data[offset:offset+3])
        offset += 3
        
        # Manifest
        manifest_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        manifest = ContainerManifest.from_bytes(data[offset:offset+manifest_len])
        offset += manifest_len
        
        # Seek table
        seek_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        if seek_len > 0:
            seek_table = SeekTable.from_bytes(data[offset:offset+seek_len])
            offset += seek_len
        else:
            seek_table = None
        
        # Create container
        container = cls(topology=manifest.topology)
        container.manifest = manifest
        if seek_table:
            container._global_seek_table = seek_table
        
        # Parse chunks into domains
        domain_offsets = list(manifest.domain_offsets) if manifest.domain_offsets else [offset]
        domain_end_offsets = domain_offsets[1:] + [len(data)]

        for domain_id, domain_offset in enumerate(domain_offsets):
            if domain_offset < offset:
                domain_offset = offset
            domain_end = domain_end_offsets[domain_id] if domain_id < len(domain_end_offsets) else len(data)
            domain_type = manifest.domain_types[domain_id] if domain_id < len(manifest.domain_types) else f"domain_{domain_id}"
            domain = Domain(domain_id=domain_id, domain_type=domain_type)

            local_offset = domain_offset
            while local_offset < min(domain_end, len(data)):
                chunk, consumed = Chunk.from_bytes(data[local_offset:], local_offset)
                if chunk.header.chunk_type == ChunkType.END:
                    local_offset = len(data)
                    break
                domain.add_chunk(chunk)
                local_offset += consumed

            if domain.chunks:
                container.domains.append(domain)
            offset = max(offset, local_offset)

        if not container.domains:
            current_domain = Domain(domain_id=0, domain_type="default")
            while offset < len(data):
                chunk, consumed = Chunk.from_bytes(data[offset:], offset)
                if chunk.header.chunk_type == ChunkType.END:
                    break
                current_domain.add_chunk(chunk)
                offset += consumed
            if current_domain.chunks:
                container.domains.append(current_domain)

        return container
    
    def seek(self, unit_id: int) -> Optional[Chunk]:
        """
        Seek to a specific unit.
        
        Returns chunk or None if not found.
        """
        if self.manifest.access_mode != AccessMode.SEEKABLE_INDEXED:
            return None
        
        entry = self._global_seek_table.lookup(unit_id)
        if entry is None:
            return None
        
        # Find chunk at offset
        for domain in self.domains:
            for chunk in domain.chunks:
                if chunk.offset == entry.byte_offset:
                    return chunk
        
        return None
    
    def verify_integrity(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify container integrity.
        
        Returns (is_valid, diagnostics).
        """
        diagnostics = {
            "n_domains": len(self.domains),
            "n_chunks": sum(len(d.chunks) for d in self.domains),
            "invalid_chunks": [],
            "total_size": self.manifest.total_size
        }
        
        all_valid = True
        
        for domain in self.domains:
            valid, invalid = domain.verify_all()
            if not valid:
                all_valid = False
                diagnostics["invalid_chunks"].extend(
                    (domain.domain_id, idx) for idx in invalid
                )
        
        diagnostics["is_valid"] = all_valid
        return all_valid, diagnostics
    
    def salvage(self) -> List[Chunk]:
        """
        Salvage valid chunks from corrupted container.
        
        Returns list of valid chunks.
        """
        valid_chunks = []
        
        for domain in self.domains:
            for chunk in domain.chunks:
                if chunk.verify():
                    valid_chunks.append(chunk)
        
        return valid_chunks


# =============================================================================
# DIRECT-SUM TOPOLOGY (ARCHIVES)
# =============================================================================

class DirectSumContainer(QShrinkContainer):
    """
    Direct-sum topology container for archives.
    
    Independent items with block-diagonal structure,
    deduplication by shared references, and maximal salvageability.
    """
    
    def __init__(self):
        super().__init__(topology=TopologyType.DIRECT_SUM)
        self._dedup_index: Dict[str, int] = {}  # hash -> chunk index
    
    def add_item(self, data: bytes, item_type: str = "file") -> int:
        """Add an item to the archive."""
        # Check for deduplication
        data_hash = hashlib.sha256(data).hexdigest()
        
        if data_hash in self._dedup_index:
            # Return reference to existing
            return self._dedup_index[data_hash]
        
        # Create new chunk
        import zlib
        checksum = zlib.crc32(data) & 0xFFFFFFFF
        
        header = ChunkHeader(
            chunk_type=ChunkType.BULK,
            payload_length=len(data),
            checksum=checksum
        )
        
        chunk = Chunk(header=header, payload=data)
        
        # Add to domain
        if not self.domains:
            domain = Domain(domain_id=0, domain_type="archive")
            self.add_domain(domain)
        
        chunk_idx = len(self.domains[0].chunks)
        self.domains[0].add_chunk(chunk)
        
        self._dedup_index[data_hash] = chunk_idx
        
        return chunk_idx
    
    def get_item(self, item_id: int) -> Optional[bytes]:
        """Get an item by ID."""
        if not self.domains:
            return None
        
        if item_id >= len(self.domains[0].chunks):
            return None
        
        chunk = self.domains[0].chunks[item_id]
        if chunk.verify():
            return chunk.payload
        
        return None


# =============================================================================
# KRONECKER TOPOLOGY (SYNCHRONIZED STREAMS)
# =============================================================================

class KroneckerContainer(QShrinkContainer):
    """
    Kronecker (tensor) topology container for synchronized streams.
    
    Coupled streams with implicit cell lattice and stripe scheduling.
    Only seek-legal if accompanied by seek lattice.
    """
    
    def __init__(self, n_streams: int = 2):
        super().__init__(topology=TopologyType.KRONECKER)
        self.n_streams = n_streams
        
        # Create domains for each stream
        for i in range(n_streams):
            domain = Domain(
                domain_id=i,
                domain_type=f"stream_{i}"
            )
            self.add_domain(domain)
    
    def add_synchronized_chunks(self, stream_data: List[bytes]) -> None:
        """Add synchronized chunks across streams."""
        if len(stream_data) != self.n_streams:
            raise ValueError(f"Expected {self.n_streams} streams")
        
        import zlib
        
        for i, data in enumerate(stream_data):
            checksum = zlib.crc32(data) & 0xFFFFFFFF
            
            header = ChunkHeader(
                chunk_type=ChunkType.BULK,
                payload_length=len(data),
                checksum=checksum
            )
            
            chunk = Chunk(header=header, payload=data)
            self.domains[i].add_chunk(chunk)
    
    def get_synchronized(self, frame_id: int) -> List[Optional[bytes]]:
        """Get synchronized chunks from all streams."""
        result = []
        
        for domain in self.domains:
            if frame_id < len(domain.chunks):
                chunk = domain.chunks[frame_id]
                if chunk.verify():
                    result.append(chunk.payload)
                else:
                    result.append(None)
            else:
                result.append(None)
        
        return result


# =============================================================================
# VALIDATION
# =============================================================================

def validate_container() -> bool:
    """Validate Q-SHRINK container system."""
    
    # Test chunk header
    header = ChunkHeader(
        chunk_type=ChunkType.BULK,
        payload_length=100,
        checksum=12345
    )
    header_bytes = header.to_bytes()
    assert len(header_bytes) == ChunkHeader.HEADER_SIZE
    
    recovered = ChunkHeader.from_bytes(header_bytes)
    assert recovered.chunk_type == ChunkType.BULK
    assert recovered.payload_length == 100
    
    # Test chunk
    payload = b"test payload data"
    import zlib
    checksum = zlib.crc32(payload) & 0xFFFFFFFF
    
    chunk = Chunk(
        header=ChunkHeader(
            chunk_type=ChunkType.BULK,
            payload_length=len(payload),
            checksum=checksum
        ),
        payload=payload
    )
    assert chunk.verify()
    
    chunk_bytes = chunk.to_bytes()
    recovered_chunk, consumed = Chunk.from_bytes(chunk_bytes)
    assert recovered_chunk.verify()
    assert recovered_chunk.payload == payload
    
    # Test repair prefix
    repair = RepairPrefix.create_for_header(header)
    repaired = repair.repair_header(header.to_bytes())
    assert repaired is not None
    
    # Test seek table
    seek_table = SeekTable()
    seek_table.add_entry(SeekEntry(0, 0, 100))
    seek_table.add_entry(SeekEntry(1, 100, 100))
    seek_table.add_entry(SeekEntry(2, 200, 100, [0, 1]))
    
    entry = seek_table.lookup(1)
    assert entry is not None
    assert entry.byte_offset == 100
    
    closure = seek_table.get_dependency_closure(2)
    assert 0 in closure
    assert 1 in closure
    assert 2 in closure
    
    # Test container manifest
    manifest = ContainerManifest(
        topology=TopologyType.DIRECT_SUM,
        n_domains=1,
        n_chunks=3
    )
    manifest_bytes = manifest.to_bytes()
    assert len(manifest_bytes) > 0
    
    # Test complete container
    container = QShrinkContainer()
    domain = Domain(domain_id=0, domain_type="test")
    domain.add_chunk(chunk)
    container.add_domain(domain)
    
    container_bytes = container.serialize()
    assert container_bytes.startswith(QShrinkContainer.MAGIC)
    
    # Deserialize
    recovered_container = QShrinkContainer.deserialize(container_bytes)
    assert len(recovered_container.domains) == 1
    
    # Verify integrity
    is_valid, diagnostics = recovered_container.verify_integrity()
    assert is_valid
    
    # Test direct-sum container
    archive = DirectSumContainer()
    item1 = archive.add_item(b"file 1 content")
    item2 = archive.add_item(b"file 2 content")
    item3 = archive.add_item(b"file 1 content")  # Duplicate
    
    assert item1 != item2
    assert item1 == item3  # Deduplicated
    
    content = archive.get_item(item1)
    assert content == b"file 1 content"
    
    # Test kronecker container
    sync = KroneckerContainer(n_streams=2)
    sync.add_synchronized_chunks([b"video frame", b"audio frame"])
    
    frames = sync.get_synchronized(0)
    assert len(frames) == 2
    assert frames[0] == b"video frame"
    assert frames[1] == b"audio frame"
    
    return True


if __name__ == "__main__":
    print("Validating Q-SHRINK Container System...")
    assert validate_container()
    print("✓ Q-SHRINK Container System validated")
