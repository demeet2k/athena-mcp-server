from __future__ import annotations

from rosetta_machine_lib import build_rosetta_machine, parse_args


def main() -> None:
    parse_args("Build the machine-readable Voynich Rosetta layer.")
    result = build_rosetta_machine()
    print(
        "Built rosetta machine:"
        f" docs_gate={result['docs_gate']}"
        f" folios={len(result['folio_records'])}"
        f" lines={len(result['line_records'])}"
        f" tokens={len(result['token_records'])}"
    )


if __name__ == "__main__":
    main()
