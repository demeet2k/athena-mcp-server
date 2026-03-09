from __future__ import annotations

import json
import re
from pathlib import Path


FULL_TRANSLATION_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = FULL_TRANSLATION_ROOT.parent
SOURCE = REPO_ROOT / "eva" / "EVA TRANSCRIPTION ORIGIONAL.txt"
OUTPUT = FULL_TRANSLATION_ROOT / "framework" / "registry" / "folio_sequence.json"


def classify_folio(folio: str) -> dict[str, str]:
    number = int(folio[1:4])
    side = folio[4]

    if 1 <= number <= 57:
        return {
            "book": "Book I - Herbal / materia medica",
            "section": "sections/FULL_PLANT.md",
            "crystal": "crystals/PLANT_CRYSTAL.md",
        }
    if 58 <= number <= 74:
        return {
            "book": "Book II - Astronomical / astrological",
            "section": "sections/FULL_ASTROLOGY.md",
            "crystal": "crystals/ASTROLOGY_CRYSTAL.md",
        }
    if 75 <= number <= 84:
        return {
            "book": "Book III - Bath / balneological",
            "section": "sections/FULL_BATH.md",
            "crystal": "crystals/BATH_CRYSTAL.md",
        }
    if 85 <= number <= 86:
        return {
            "book": "Book IV - Cosmological / rosette",
            "section": "sections/FULL_COSMOLOGY.md",
            "crystal": "crystals/COSMOLOGY_CRYSTAL.md",
        }
    if 87 <= number <= 105 or (number == 106 and side == "R"):
        return {
            "book": "Book V - Pharmaceutical 1",
            "section": "sections/PHARMACEUTICAL_1_FULL.md",
            "crystal": "crystals/PHARMACEUTICAL_1_CRYSTAL.md",
        }
    if (number == 106 and side == "V") or 107 <= number <= 116:
        return {
            "book": "Book V - Pharmaceutical 2",
            "section": "sections/PHARMACEUTICAL_2_FULL.md",
            "crystal": "crystals/PHARMACEUTICAL_2_CRYSTAL.md",
        }
    return {
        "book": "Unknown / unresolved section",
        "section": "sections/FULL_PLANT.md",
        "crystal": "crystals/VOYNICH_FULL_CRYSTAL.md",
    }


def build_registry() -> dict[str, object]:
    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"^<f(\d+)([rv])\.", re.IGNORECASE | re.MULTILINE)

    seen: set[str] = set()
    folios: list[dict[str, object]] = []

    for match in pattern.finditer(text):
        number = int(match.group(1))
        side = match.group(2).upper()
        folio = f"F{number:03d}{side}"
        if folio in seen:
            continue
        seen.add(folio)
        meta = classify_folio(folio)
        folios.append(
            {
                "order": len(folios) + 1,
                "folio": folio,
                **meta,
            }
        )

    return {
        "version": "1.0.0",
        "source": str(SOURCE),
        "count": len(folios),
        "first": folios[0]["folio"] if folios else None,
        "last": folios[-1]["folio"] if folios else None,
        "folios": folios,
    }


def main() -> None:
    registry = build_registry()
    OUTPUT.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Folio count: {registry['count']}")
    print(f"Range: {registry['first']} -> {registry['last']}")


if __name__ == "__main__":
    main()
