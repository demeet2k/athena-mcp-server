"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Lenses Module                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Lens/Chart transformation system for coordinate transport.
"""

from atlasforge.lenses.chart import (
    Chart,
    Lens,
    ComposedChart,
    CorridorCondition,
    CorridorViolation,
    ChartError,
    ChartCertificate,
    ChartFactory,
)

from atlasforge.lenses.transport import (
    Transport,
    FieldTransport,
    OperatorTransport,
    ConstraintTransport,
    FlowTransport,
    TransportChain,
)

from atlasforge.lenses.canonical import (
    IdentityLens,
    LogLens,
    ExpLens,
    TrigLens,
    PhiLens,
    FourierLens,
    LogitLens,
    BoxCoxLens,
    LensCatalog,
)

__all__ = [
    # Charts
    "Chart",
    "Lens",
    "ComposedChart",
    "CorridorCondition",
    "CorridorViolation",
    "ChartError",
    "ChartCertificate",
    "ChartFactory",
    
    # Transport
    "Transport",
    "FieldTransport",
    "OperatorTransport",
    "ConstraintTransport",
    "FlowTransport",
    "TransportChain",
    
    # Canonical Lenses
    "IdentityLens",
    "LogLens",
    "ExpLens",
    "TrigLens",
    "PhiLens",
    "FourierLens",
    "LogitLens",
    "BoxCoxLens",
    "LensCatalog",
]
