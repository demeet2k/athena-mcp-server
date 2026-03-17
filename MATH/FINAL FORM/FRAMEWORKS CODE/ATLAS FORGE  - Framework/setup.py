"""
AtlasForge - Universal Harmonic Framework
==========================================

A complete mathematical framework providing:
- Four Poles (D, Ω, Σ, Ψ) - Fundamental mathematical realms
- Four Lenses (□, ✿, ☁, ❋) - Multiple perspectives
- Gateway SL(2,R) - Transformation algebra
- Crystal Structure (4⁴ = 256) - Complete address space
- OICF Coordinates - Emergence measurement
- Crystal Merge Protocol (CM0-CM6) - Problem solving
- Proof Engine - Certificate-carrying verification
- 21 Books - Knowledge organization

Installation:
    pip install atlasforge

Usage:
    import atlasforge as af
    
    # Test Pythagorean addition
    print(af.quadrature(3, 4))  # 5.0
    
    # Check emergence
    coords = af.EmergenceCoordinates(0.8, 0.7, 0.5, 0.9)
    print(coords.emergence_potential)  # 0.252
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
version = "4.0.0"

# Read long description from README
long_description = """
# AtlasForge - Universal Harmonic Framework

## Overview

AtlasForge is a complete mathematical framework implementing the Universal Harmonic Framework,
a unified theory encompassing:

- **AQM (Axiomatic Quantum Mathematics)**: Q-numbers, quantum arithmetic, kernel closure
- **LM (Liminal Mathematics)**: Distinctions, dynamics, renormalization, emergence
- **QCM (Quadrature-Cyclotomic Manifold)**: Wave-lattice duality, interference law
- **Crystal Merge Protocol**: Systematic problem-solving methodology
- **Proof Engine**: Certificate-carrying verification

## Key Discovery

The **Pythagorean Addition Operator**:

```
a ⊞ b = √(a² + b²)
```

This is the orthogonal slice of the interference law:
```
|ψ₁ + ψ₂|² = a² + b² + 2ab·cos(Δθ)
```

When Δθ = π/2, the cross term vanishes.

## Statistics

- **Total Exports**: 1,963
- **Lines of Code**: 87,842
- **Python Files**: 274
- **Documentation Lines**: 7,032

## Installation

```bash
pip install atlasforge
```

## Quick Start

```python
import atlasforge as af

# Pythagorean addition
print(af.quadrature(3, 4))  # 5.0

# Emergence coordinates
coords = af.EmergenceCoordinates(0.8, 0.7, 0.5, 0.9)
print(coords.emergence_potential)  # 0.252

# Crystal Merge Protocol
protocol = af.CrystalMergeProtocol("example")
result = protocol.execute_all()
print(result["passed"])  # True
```

## License

MIT License
"""

setup(
    name="atlasforge",
    version=version,
    author="Universal Harmonic Framework",
    author_email="framework@atlasforge.dev",
    description="Universal Harmonic Framework - Complete Mathematical Architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atlasforge/atlasforge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords=[
        "mathematics",
        "framework",
        "quantum",
        "proof",
        "certification",
        "emergence",
        "harmonic",
        "universal",
    ],
    project_urls={
        "Documentation": "https://atlasforge.readthedocs.io/",
        "Source": "https://github.com/atlasforge/atlasforge",
        "Tracker": "https://github.com/atlasforge/atlasforge/issues",
    },
)
