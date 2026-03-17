"""
athena_process_compiler -- The Athena Process Language Compiler.

A multi-backend compiler pipeline that transforms Voynich manuscript
glyph sequences through parsing, intermediate representation, rendering,
verification, and storage.

Pipeline stages:
    1. Tokenisation    (schemas.tokens)
    2. Parsing         (parsers)
    3. IR lowering     (schemas.ir)
    4. Rendering       (renderers / compilers)
    5. Verification    (verifiers)
    6. Storage / GAWM  (storage)
    7. Runtime query   (runtime)
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
