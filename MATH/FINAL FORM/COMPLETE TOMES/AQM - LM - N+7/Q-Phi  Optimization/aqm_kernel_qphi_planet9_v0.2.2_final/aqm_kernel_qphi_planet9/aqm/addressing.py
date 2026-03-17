from __future__ import annotations

import re
from dataclasses import dataclass

_LENS = {"S", "F", "C", "R"}

def base4(n: int, width: int = 4) -> str:
    if n < 0:
        raise ValueError("base4 expects non-negative integer")
    digits = []
    if n == 0:
        digits.append("0")
    else:
        while n:
            n, r = divmod(n, 4)
            digits.append(str(r))
    s = "".join(reversed(digits))
    return s.zfill(width)

def unbase4(s: str) -> int:
    if not re.fullmatch(r"[0-3]+", s):
        raise ValueError(f"Invalid base4 string: {s!r}")
    n = 0
    for ch in s:
        n = n * 4 + int(ch)
    return n

@dataclass(frozen=True, slots=True)
class TileAddress:
    chapter: int  # 1..21 (not enforced by kernel)
    digits4: str  # 4 digits base4(chapter-1)
    lens: str     # S/F/C/R
    facet: int    # 1..4

    @staticmethod
    def for_chapter(chapter: int, lens: str, facet: int) -> "TileAddress":
        if chapter < 1:
            raise ValueError("chapter must be >= 1")
        lens = lens.upper()
        if lens not in _LENS:
            raise ValueError(f"lens must be one of {_LENS}")
        if facet not in (1,2,3,4):
            raise ValueError("facet must be 1..4")
        digits4 = base4(chapter - 1, width=4)
        return TileAddress(chapter=chapter, digits4=digits4, lens=lens, facet=facet)

    def to_ascii(self) -> str:
        # Ch01.<0000>_4.S.1
        return f"Ch{self.chapter:02d}.<{self.digits4}>_4.{self.lens}.{self.facet}"

    def to_unicode(self) -> str:
        # Ch01.⟨0000⟩₄.S.1
        return f"Ch{self.chapter:02d}.⟨{self.digits4}⟩₄.{self.lens}.{self.facet}"

    @staticmethod
    def parse(s: str) -> "TileAddress":
        s = s.strip()
        # Accept either <0000>_4 or ⟨0000⟩₄
        m = re.fullmatch(r"Ch(?P<ch>\d{2})\.(?:<(?P<d1>[0-3]{4})>_4|⟨(?P<d2>[0-3]{4})⟩₄)\.(?P<lens>[SFCR])\.(?P<facet>[1-4])", s)
        if not m:
            raise ValueError(f"Unrecognized TileAddress: {s!r}")
        ch = int(m.group("ch"))
        digits4 = m.group("d1") or m.group("d2")
        lens = m.group("lens")
        facet = int(m.group("facet"))
        # Cross-check digits4 against chapter if possible
        expected = base4(ch - 1, width=4)
        if digits4 != expected:
            # Keep strict: address mismatch likely indicates an error.
            raise ValueError(f"Address digits mismatch: chapter={ch} expects {expected} but got {digits4}")
        return TileAddress(chapter=ch, digits4=digits4, lens=lens, facet=facet)
