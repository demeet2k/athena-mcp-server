from __future__ import annotations

from rosetta_machine_lib import parse_args, validate_rosetta_machine


def main() -> None:
    parse_args("Validate the machine-readable Voynich Rosetta layer.")
    result = validate_rosetta_machine()
    print(
        "Validated rosetta machine:"
        f" docs_gate={result['docs_gate']}"
        f" folios={result['final_draft_folios']}"
        f" lines={result['line_operator_chains']}"
        f" tokens={result['token_instances']}"
        f" companions={result['companion_rollups']}"
        f" canonical={result['canonical_promotions']}"
        f" giant={result['giant_packages']}"
    )


if __name__ == "__main__":
    main()
