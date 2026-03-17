"""
ATHENA OS — UNIFIED TYPES PACKAGE
=================================

The Single Source of Truth for all type definitions.

This package exports all canonical types used across
the 66 packages of ATHENA OS.
"""

from .core import (
    # BIT4 Foundation
    B4, Klein4Op,
    
    # Universal Types
    Element, Humor, Cause, Category,
    
    # Crystal Address System
    Lens, Facet, Atom, CrystalAddress,
    
    # QHC Regime System
    QHCConstant, QHCShape, QHCElement, QHCLevel, QHCPole, QHCRegime,
    
    # Holographic Address
    HolographicAddress,
    
    # Truth and Verification
    TypedTruth, Certificate, CertificateLevel, CertificateType,
    
    # Protocols
    Corridor, StandardCorridor, Operator, LambdaOperator,
    
    # Ledger
    Ledger, LedgerEntry,
    
    # Totality
    ZResult,
    
    # Constants
    Constants,
    
    # Type Variables
    T, S, R,
)

__all__ = [
    # BIT4
    'B4', 'Klein4Op',
    
    # Elements
    'Element', 'Humor', 'Cause', 'Category',
    
    # Crystal
    'Lens', 'Facet', 'Atom', 'CrystalAddress',
    
    # QHC
    'QHCConstant', 'QHCShape', 'QHCElement', 'QHCLevel', 'QHCPole', 'QHCRegime',
    
    # Holographic
    'HolographicAddress',
    
    # Truth
    'TypedTruth', 'Certificate', 'CertificateLevel', 'CertificateType',
    
    # Protocols
    'Corridor', 'StandardCorridor', 'Operator', 'LambdaOperator',
    
    # Ledger
    'Ledger', 'LedgerEntry',
    
    # Totality
    'ZResult',
    
    # Constants
    'Constants',
    
    # Generics
    'T', 'S', 'R',
]

__version__ = "1.0.0"

# State Protocol
from .state import (
    StateCategory, ProcessPhase, ModalPhase, OntologicalPhase,
    UnifiedState, BaseState, ElementalState, HumoralState, QuantumState,
    StateTransition, StateMachine, StateProjector,
)

__all__ += [
    'StateCategory', 'ProcessPhase', 'ModalPhase', 'OntologicalPhase',
    'UnifiedState', 'BaseState', 'ElementalState', 'HumoralState', 'QuantumState',
    'StateTransition', 'StateMachine', 'StateProjector',
]
