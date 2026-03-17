"""Categorical Translation Module - SKF functor, boundary realization."""

from atlasforge.categorical.categorical import (
    CategoryError,
    CategoricalObject,
    Morphism,
    BoundaryObject,
    BoundaryMorphism,
    HybridObject,
    HybridMorphism,
    SKFFunctor,
    NaturalTransformation,
    KernelPreservingCategory,
    TranslationPipeline,
    create_boundary_object,
    create_skf_functor,
    translate_to_hybrid,
    verify_kernel_preservation,
)

__all__ = [
    'CategoryError',
    'CategoricalObject',
    'Morphism',
    'BoundaryObject',
    'BoundaryMorphism',
    'HybridObject',
    'HybridMorphism',
    'SKFFunctor',
    'NaturalTransformation',
    'KernelPreservingCategory',
    'TranslationPipeline',
    'create_boundary_object',
    'create_skf_functor',
    'translate_to_hybrid',
    'verify_kernel_preservation',
]
