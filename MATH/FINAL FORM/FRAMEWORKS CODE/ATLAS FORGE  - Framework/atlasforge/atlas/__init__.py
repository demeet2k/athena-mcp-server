"""High-level orchestration: Atlas = solve + remember + retrieve.

The lower-level AtlasForge subsystems are powerful, but the user-facing
workflow you described is:

> "this is the full understanding of all the math we've been doing"

That is exactly what the :class:`~atlasforge.atlas.atlas.Atlas` object is for.

`Atlas` binds together:
- the Recipe executor (compute → certify → verify)
- the Memory bank (remember → search → link)
- optional sessions and graph linking
"""

from atlasforge.atlas.atlas import Atlas, AtlasConfig
from atlasforge.atlas.book import AtlasBookBuilder, AtlasBookConfig
from atlasforge.atlas.navigator import CrystalNavigator, CrystalCell

__all__ = [
    "Atlas",
    "AtlasConfig",
    "AtlasBookBuilder",
    "AtlasBookConfig",
    "CrystalNavigator",
    "CrystalCell",
]
