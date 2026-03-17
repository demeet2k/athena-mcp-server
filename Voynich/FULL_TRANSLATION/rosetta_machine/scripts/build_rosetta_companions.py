from __future__ import annotations

from rosetta_machine_lib import build_rosetta_companions, parse_args


def main() -> None:
    parse_args("Build Rosetta machine companion rollups and markdown surfaces.")
    result = build_rosetta_companions()
    print(
        "Built rosetta companions:"
        f" manuscript={len(result['manuscript_order_rollup'])}"
        f" books={len(result['book_operator_rollup'])}"
        f" nodes={len(result['neural_node_rollup'])}"
        f" edges={len(result['metro_edge_rollup'])}"
    )


if __name__ == "__main__":
    main()
