"""
ATHENA OS - Types Module
========================
Type systems for ATHENA computation.

Components:
- aristotelian: The 10 Categories + 4 Causes type system
"""

from .aristotelian import (
    Category,
    Cause,
    ActualityMode,
    ActualityState,
    Predicate,
    Entity,
    Syllogism,
    TypeRegistry,
)

__all__ = [
    'Category', 'Cause', 'ActualityMode', 'ActualityState',
    'Predicate', 'Entity', 'Syllogism', 'TypeRegistry',
]
