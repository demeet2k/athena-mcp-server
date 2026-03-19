# Re-export stub — neural_engine moved to _archive/neural_engine.py
# Kept for backward compatibility with observer_swarm.py, weight_feedback.py
from ._archive.neural_engine import *  # noqa: F401,F403
from ._archive.neural_engine import (  # explicit re-exports
    CrystalNeuralEngine,
    QueryState,
    get_engine,
    _bridge_key,
    BRIDGE_WEIGHTS,
)
