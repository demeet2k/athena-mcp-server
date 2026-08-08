from __future__ import annotations

import argparse
from pathlib import Path

from athena_mcp.kc144_registry_pack import PACK_SHA256, _archive_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconstruct and verify the digest-bound KC144 registry archive")
    parser.add_argument("output", nargs="?", default="kc144-core-registries.tar.xz")
    args = parser.parse_args()
    path = Path(args.output)
    data = _archive_bytes()
    path.write_bytes(data)
    print(f"{path} {len(data)} bytes sha256={PACK_SHA256}")


if __name__ == "__main__":
    main()
