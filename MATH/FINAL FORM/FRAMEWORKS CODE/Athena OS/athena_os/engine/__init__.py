"""
ATHENA OS - Engine Module
=========================
Computational engines for ATHENA OS.

Components:
- paradox: Paradox-Harmonia Zero-Point Computing engine
"""

from .paradox import (
    TruthValue,
    Bilattice,
    Evidence,
    Proposition,
    ParadoxTension,
    ZeroPointResolver,
    CrystalResolution,
    KappaState,
    ParadoxEngine,
)

__all__ = [
    'TruthValue', 'Bilattice', 'Evidence', 'Proposition',
    'ParadoxTension', 'ZeroPointResolver', 'CrystalResolution',
    'KappaState', 'ParadoxEngine',
]
