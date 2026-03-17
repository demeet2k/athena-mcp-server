#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Demonstration                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import math
import sys
sys.path.insert(0, '/home/claude')

from atlasforge import *


def demo_root_finding():
    """Demonstrate various root-finding methods."""
    print("\n" + "="*60)
    print("Root Finding Solvers")
    print("="*60)
    
    H = lambda x: x**2 - 2
    domain = Interval.closed(1, 2)
    exact = math.sqrt(2)
    
    print(f"\nSolving: x² - 2 = 0, exact = √2 = {exact:.15f}\n")
    
    solvers = [
        ("Bisection", BisectionSolver(tol=1e-12)),
        ("Newton", NewtonSolver(tol=1e-12)),
        ("Brent", BrentSolver(tol=1e-12)),
        ("Interval Newton", IntervalNewtonSolver(tol=1e-12)),
    ]
    
    for name, solver in solvers:
        result = solver.solve(H, domain)
        error = abs(result.solution - exact)
        v = "✓" if result.enclosure_verified else " "
        print(f"{name:15s}: {result.solution:.15f} (err: {error:.2e}) [{v}]")


def demo_recipe_pipeline():
    """Demonstrate the full recipe pipeline."""
    print("\n" + "="*60)
    print("Recipe Pipeline")
    print("="*60)
    
    H = lambda x: x**3 - x - 2
    constraint = RootConstraint(H=H, domain=Interval.closed(1, 2))
    blueprint = Blueprint(constraint=constraint)
    recipe = RecipeExecutor().execute(blueprint, SolvePlan.verified())
    
    print(f"\nSolving: x³ - x - 2 = 0")
    print(f"Solution: {recipe.solution:.15f}")
    print(f"Verified: {recipe.verified}")
    print(f"Level: L{recipe.certificate_level.value}")


def demo_crystal():
    """Crystal Combat solver."""
    print("\n" + "="*60)
    print("Crystal Combat")
    print("="*60)
    
    H = lambda x: x**2 - 2
    solver = CrystalSolver(tolerance=1e-10, max_turns=100)
    result = solver.solve(H, x0=1.5, domain=Interval.closed(1, 2))
    
    print(f"\nSolution: {result.solution:.15f}")
    print(f"Turns: {result.turns}, Cards: {result.cards_played}")


def main():
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "ATLAS FORGE v1.0.0-final" + " "*19 + "║")
    print("╚" + "═"*58 + "╝")
    
    demo_root_finding()
    demo_recipe_pipeline()
    demo_crystal()
    
    print("\n" + "="*60)
    print("AtlasForge: 179 symbols, 9 modules, proof-carrying recipes")
    print("="*60)


if __name__ == "__main__":
    main()
