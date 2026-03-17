from __future__ import annotations

from rosetta_machine_lib import build_giant_manuscript, parse_args


def main() -> None:
    parse_args("Build the deterministic giant Voynich manuscript package.")
    result = build_giant_manuscript()
    print(
        "Built giant manuscript:"
        f" targets={len(result['markdown'])}"
        f" archive_snapshot={result['archive_snapshot_path'] or 'none'}"
    )


if __name__ == "__main__":
    main()
