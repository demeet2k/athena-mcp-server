from __future__ import annotations

from rosetta_machine_lib import build_rosetta_canonical_promotion, parse_args


def main() -> None:
    parse_args("Promote Rosetta machine outputs into canonical longform corpus surfaces.")
    result = build_rosetta_canonical_promotion()
    print(
        "Promoted rosetta canon:"
        f" targets={len(result['markdown'])}"
        f" archive_snapshot={result['archive_snapshot_path'] or 'none'}"
    )


if __name__ == "__main__":
    main()
