from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ATHENA_OS_ROOT = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "FRAMEWORKS CODE" / "Athena OS"
OUTPUT_PATH = WORKSPACE_ROOT / "self_actualize" / "qshrink_runtime_verification.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    sys.path.insert(0, str(ATHENA_OS_ROOT))

    payload = {
        "generated_at": utc_now(),
        "entrypoint": "athena_os.qshrink",
        "truth": "FAIL",
        "checks": [],
    }

    try:
        from athena_os.qshrink import (
            compress,
            create_archive,
            create_lossless_codec,
            create_lossy_codec,
            create_synchronized_container,
            decompress,
            validate_qshrink,
        )
        from athena_os.qshrink.container import AccessMode, QShrinkContainer, TopologyType
    except Exception as exc:
        payload["checks"].append(
            {
                "name": "import_entrypoint",
                "truth": "FAIL",
                "detail": repr(exc),
            }
        )
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    payload["checks"].append(
        {
            "name": "import_entrypoint",
            "truth": "OK",
            "detail": "Imported athena_os.qshrink without ad hoc package patching beyond root path insertion.",
        }
    )

    validate_ok = bool(validate_qshrink())
    payload["checks"].append(
        {
            "name": "validate_qshrink",
            "truth": "OK" if validate_ok else "FAIL",
            "detail": "validate_qshrink() returned a truthy result.",
        }
    )

    sample = (b"QSHRINK runtime verification payload " * 8) + bytes(range(64))
    blob = compress(sample, lossless=True)
    restored = decompress(blob)
    roundtrip_ok = restored == sample
    payload["checks"].append(
        {
            "name": "lossless_roundtrip",
            "truth": "OK" if roundtrip_ok else "FAIL",
            "detail": {
                "compressed_bytes": len(blob),
                "input_bytes": len(sample),
                "restored_match": roundtrip_ok,
            },
        }
    )

    container = QShrinkContainer.deserialize(blob)
    is_valid, diagnostics = container.verify_integrity()
    payload["checks"].append(
        {
            "name": "container_integrity",
            "truth": "OK" if is_valid else "FAIL",
            "detail": diagnostics,
        }
    )

    lossless_codec = create_lossless_codec()
    lossy_codec = create_lossy_codec()
    archive = create_archive()
    lossy_sample = np.linspace(-3.0, 3.0, 24, dtype=np.float64).reshape(-1, 1)
    lossy_decoded = lossy_codec.decode(lossy_codec.encode(lossy_sample))
    lossy_max_error = float(np.max(np.abs(lossy_sample.flatten() - lossy_decoded.flatten())))
    lossy_bound = float(lossy_codec.Q.error_bound())
    lossy_ok = lossy_max_error <= lossy_bound + 1e-6
    payload["checks"].append(
        {
            "name": "lossy_bound",
            "truth": "OK" if lossy_ok else "FAIL",
            "detail": {
                "max_error": lossy_max_error,
                "declared_bound": lossy_bound,
            },
        }
    )

    sync = create_synchronized_container(n_streams=2)
    sync.manifest.access_mode = AccessMode.SEEKABLE_INDEXED
    sync.add_synchronized_chunks([b"video-frame-000", b"audio-frame-000"])
    sync.add_synchronized_chunks([b"video-frame-001", b"audio-frame-001"])
    sync_blob = sync.serialize()
    sync_restored = QShrinkContainer.deserialize(sync_blob)
    sync_ok = (
        sync_restored.topology == TopologyType.KRONECKER
        and sync_restored.manifest.access_mode == AccessMode.SEEKABLE_INDEXED
        and len(sync_restored.domains) == 2
        and sum(len(domain.chunks) for domain in sync_restored.domains) == 4
    )
    payload["checks"].append(
        {
            "name": "synchronized_container",
            "truth": "OK" if sync_ok else "FAIL",
            "detail": {
                "topology": sync_restored.topology.value,
                "access_mode": sync_restored.manifest.access_mode.name,
                "domain_count": len(sync_restored.domains),
                "chunk_count": sum(len(domain.chunks) for domain in sync_restored.domains),
                "seek_entries": len(sync_restored._global_seek_table._entries),
            },
        }
    )

    payload["checks"].append(
        {
            "name": "factory_surface",
            "truth": "OK",
            "detail": {
                "lossless_codec": lossless_codec.__class__.__name__,
                "lossy_codec": lossy_codec.__class__.__name__,
                "archive": archive.__class__.__name__,
                "synchronized_container": sync.__class__.__name__,
            },
        }
    )

    payload["truth"] = "OK" if all(check["truth"] == "OK" for check in payload["checks"]) else "FAIL"
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
