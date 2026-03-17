"""
ATHENA OS - Agent Module
========================
The Distinguished Agent (Â) and agent-related systems.

Components:
- distinguished: The Distinguished Agent at the Zero Point
"""

from .distinguished import (
    AgentState,
    VoidAlignment,
    WorldEngagement,
    UpdateOperator,
    UpdateResult,
    AgentUpdater,
    DistinguishedAgent,
)

__all__ = [
    'AgentState', 'VoidAlignment', 'WorldEngagement',
    'UpdateOperator', 'UpdateResult', 'AgentUpdater',
    'DistinguishedAgent',
]
