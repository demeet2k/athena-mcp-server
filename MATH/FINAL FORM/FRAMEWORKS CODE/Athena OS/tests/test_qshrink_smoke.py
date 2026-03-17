import unittest
import numpy as np

from athena_os.qshrink import (
    compress,
    create_lossless_codec,
    create_lossy_codec,
    create_synchronized_container,
    decompress,
    validate_qshrink,
)
from athena_os.qshrink.container import (
    AccessMode,
    ContainerManifest,
    TopologyType,
    QShrinkContainer,
)


class QShrinkSmokeTests(unittest.TestCase):
    def test_entrypoint_imports(self) -> None:
        from athena_os import qshrink

        self.assertTrue(hasattr(qshrink, "validate_qshrink"))
        self.assertTrue(hasattr(qshrink, "compress"))
        self.assertTrue(hasattr(qshrink, "decompress"))

    def test_validate_qshrink(self) -> None:
        self.assertTrue(validate_qshrink())

    def test_lossless_roundtrip(self) -> None:
        payload = (b"QSHRINK test payload " * 16) + bytes(range(32))
        blob = compress(payload, lossless=True)
        restored = decompress(blob)
        self.assertEqual(restored, payload)

    def test_lossless_codec_numeric_roundtrip(self) -> None:
        codec = create_lossless_codec(n_petals=8)
        payload = np.linspace(-2.0, 2.0, 24, dtype=np.float64).reshape(-1, 1)
        decoded = codec.decode(codec.encode(payload))
        self.assertTrue(np.allclose(decoded, payload, atol=1e-9))

    def test_lossy_codec_respects_declared_bound(self) -> None:
        codec = create_lossy_codec(quality_tier=1, quality_refinement=1, n_petals=8)
        payload = np.linspace(-3.0, 3.0, 24, dtype=np.float64).reshape(-1, 1)
        decoded = codec.decode(codec.encode(payload))
        max_error = float(np.max(np.abs(decoded.flatten() - payload.flatten())))
        self.assertLessEqual(max_error, codec.Q.error_bound() + 1e-6)

    def test_container_integrity_after_roundtrip(self) -> None:
        payload = b"container integrity check" * 8
        blob = compress(payload, lossless=True)
        container = QShrinkContainer.deserialize(blob)
        is_valid, diagnostics = container.verify_integrity()
        self.assertTrue(is_valid, diagnostics)
        self.assertEqual(len(container.domains), 1)

    def test_manifest_roundtrip(self) -> None:
        manifest = ContainerManifest(
            topology=TopologyType.DIRECT_SUM,
            access_mode=AccessMode.SEEKABLE_INDEXED,
            n_domains=1,
            n_chunks=2,
            total_size=512,
            domain_types=["bytes"],
            domain_offsets=[128],
            content_hash="abc123",
        )
        recovered = ContainerManifest.from_bytes(manifest.to_bytes())
        self.assertEqual(recovered.version, manifest.version)
        self.assertEqual(recovered.topology, manifest.topology)
        self.assertEqual(recovered.access_mode, manifest.access_mode)
        self.assertEqual(recovered.n_domains, manifest.n_domains)
        self.assertEqual(recovered.domain_types, manifest.domain_types)
        self.assertEqual(recovered.domain_offsets, manifest.domain_offsets)
        self.assertEqual(recovered.content_hash, manifest.content_hash)

    def test_seekable_synchronized_container_roundtrip(self) -> None:
        container = create_synchronized_container(n_streams=2)
        container.manifest.access_mode = AccessMode.SEEKABLE_INDEXED
        container.add_synchronized_chunks([b"video-frame-000", b"audio-frame-000"])
        container.add_synchronized_chunks([b"video-frame-001", b"audio-frame-001"])

        blob = container.serialize()
        restored = QShrinkContainer.deserialize(blob)

        self.assertEqual(restored.topology, TopologyType.KRONECKER)
        self.assertEqual(restored.manifest.access_mode, AccessMode.SEEKABLE_INDEXED)
        self.assertEqual(len(restored.domains), 2)
        self.assertEqual(sum(len(domain.chunks) for domain in restored.domains), 4)
        self.assertEqual(len(restored._global_seek_table._entries), 4)


if __name__ == "__main__":
    unittest.main()
