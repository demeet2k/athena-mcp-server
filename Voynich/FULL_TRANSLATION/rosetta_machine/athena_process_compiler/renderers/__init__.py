"""
renderers -- Domain-native backend renderers for the Athena Process Compiler.

Each renderer accepts OperatorIR nodes (individually or as a chain) and
produces a NativeRender artefact expressed in the language of a specific
domain: natural English, chemistry, category-theoretic mathematics, or
Western music theory.

Public API
----------
    EnglishRenderer
    ChemistryRenderer
    MathNativeRenderer
    MusicNativeRenderer

    RENDERERS          -- name -> class registry for dynamic dispatch
    render_all_backends -- convenience: run every registered renderer on a chain
"""

from athena_process_compiler.renderers.chemistry import ChemistryRenderer
from athena_process_compiler.renderers.english import EnglishRenderer
from athena_process_compiler.renderers.math_native import MathNativeRenderer
from athena_process_compiler.renderers.music_native import MusicNativeRenderer

# Name -> renderer-class registry for programmatic iteration.
RENDERERS: dict[str, type] = {
    "english": EnglishRenderer,
    "chemistry": ChemistryRenderer,
    "math": MathNativeRenderer,
    "music": MusicNativeRenderer,
}


def render_all_backends(
    chain: list,
) -> dict[str, "NativeRender"]:  # noqa: F821 (forward ref)
    """Run every registered renderer on *chain* and return {name: NativeRender}.

    Parameters
    ----------
    chain : list[OperatorIR]
        The operator chain to render.

    Returns
    -------
    dict[str, NativeRender]
        Keyed by backend name.
    """
    from athena_process_compiler.schemas.artifacts import NativeRender  # noqa: F811

    results: dict[str, NativeRender] = {}
    for name, cls in RENDERERS.items():
        renderer = cls()
        results[name] = renderer.render_chain(chain)
    return results


__all__ = [
    "EnglishRenderer",
    "ChemistryRenderer",
    "MathNativeRenderer",
    "MusicNativeRenderer",
    "RENDERERS",
    "render_all_backends",
]
