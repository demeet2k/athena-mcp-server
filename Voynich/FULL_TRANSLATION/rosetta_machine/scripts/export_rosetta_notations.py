from __future__ import annotations

from rosetta_machine_lib import export_rosetta_notations, parse_args


def main() -> None:
    parse_args("Export machine-readable Voynich algorithms into notation families.")
    result = export_rosetta_notations()
    print(
        "Exported rosetta notations:"
        f" exports={len(result['exports'])}"
        f" roundtrip_examples={len(result['roundtrip_examples'])}"
    )


if __name__ == "__main__":
    main()
