#!/usr/bin/env python3
"""
ATHENA OS - COMPREHENSIVE TEST RUNNER
=====================================
Validates all modules and generates test report.

Usage:
    python run_tests.py [--verbose] [--module MODULE]
"""

import sys
import time
import traceback
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TestResult:
    """Result of a single test."""
    module: str
    passed: bool
    duration: float
    error: Optional[str] = None


@dataclass
class TestReport:
    """Complete test report."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def total_tests(self) -> int:
        return len(self.results)
    
    @property
    def passed_tests(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed_tests(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests
    
    @property
    def total_duration(self) -> float:
        return sum(r.duration for r in self.results)
    
    def summary(self) -> str:
        """Generate summary string."""
        lines = [
            "=" * 70,
            "ATHENA OS TEST REPORT",
            "=" * 70,
            f"Started:  {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Finished: {self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else 'N/A'}",
            "",
            f"Total Tests:  {self.total_tests}",
            f"Passed:       {self.passed_tests}",
            f"Failed:       {self.failed_tests}",
            f"Success Rate: {self.success_rate * 100:.1f}%",
            f"Duration:     {self.total_duration:.3f}s",
            "",
            "Results:",
        ]
        
        for r in self.results:
            status = "✓" if r.passed else "✗"
            lines.append(f"  {status} {r.module}: {r.duration:.3f}s")
            if r.error:
                lines.append(f"      Error: {r.error[:60]}...")
        
        lines.append("=" * 70)
        return "\n".join(lines)


class AthenaTestRunner:
    """Test runner for ATHENA OS modules."""
    
    # Module validation functions
    MODULES = {
        # Core modules
        "syntax": "syntax.validate_syntax",
        "aetheric": "aetheric.validate_aetheric",
        "gin": "gin.validate_gin",
        "hrp": "hrp.validate_hrp",
        "bit4": "bit4.validate_bit4",
        "atlasforge": "atlasforge.validate_atlasforge",
        "deep_crystal": "deep_crystal.validate_deep_crystal",
        
        # Infrastructure
        "governance": "governance.validate_governance",
        "zeropoint": "zeropoint.validate_zeropoint",
        "crystal_computing": "crystal_computing.validate_crystal_computing",
        "qhc": "qhc.validate_qhc",
        "hdcs": "hdcs.validate_hdcs",
        "mathfund": "mathfund.validate_mathfund",
        "mathcore": "mathcore.validate_mathcore",
        
        # Supporting
        "hugging": "hugging.validate_hugging",
        "hololens": "hololens.validate_hololens",
        "emcrystal": "emcrystal.validate_emcrystal",
        "seed": "seed.validate_seed",
        "quantum": "quantum.validate_quantum",
        "fractal": "fractal.validate_fractal",
        "biophysics": "biophysics.validate_biophysics",
        "superposition": "superposition.validate_superposition",
        "philosophical": "philosophical.validate_philosophical",
        "forces": "forces.validate_forces",
        "crystal": "crystal.validate_crystal",
        "primes": "primes.validate_primes",
        "athena": "athena.validate_athena",
        
        # Core integration
        "core.integration": "core.integration.validate_integration",
        
        # Water sector
        "gin.water_sector": "gin.water_sector.validate_water_sector",
        
        # Deep crystal submodules
        "deep_crystal.kernel_spec": "deep_crystal.kernel_spec.validate_kernel_spec",
        "deep_crystal.bio_os": "deep_crystal.bio_os.validate_bio_os",
        "deep_crystal.tse": "deep_crystal.tse.validate_tse",
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.report = TestReport(started_at=datetime.now())
    
    def run_single(self, module: str) -> TestResult:
        """Run test for a single module."""
        if module not in self.MODULES:
            return TestResult(
                module=module,
                passed=False,
                duration=0.0,
                error=f"Unknown module: {module}"
            )
        
        validator_path = self.MODULES[module]
        
        if self.verbose:
            print(f"  Testing {module}...", end=" ", flush=True)
        
        start = time.time()
        
        try:
            # Dynamic import
            parts = validator_path.rsplit(".", 1)
            module_name = parts[0]
            func_name = parts[1]
            
            mod = __import__(module_name, fromlist=[func_name])
            validator = getattr(mod, func_name)
            
            result = validator()
            passed = bool(result)
            error = None
            
        except Exception as e:
            passed = False
            error = str(e)
            if self.verbose:
                traceback.print_exc()
        
        duration = time.time() - start
        
        if self.verbose:
            status = "✓" if passed else "✗"
            print(f"{status} ({duration:.3f}s)")
        
        return TestResult(
            module=module,
            passed=passed,
            duration=duration,
            error=error
        )
    
    def run_all(self, modules: Optional[List[str]] = None) -> TestReport:
        """Run all tests."""
        if modules is None:
            modules = list(self.MODULES.keys())
        
        if self.verbose:
            print("=" * 70)
            print("ATHENA OS TEST SUITE")
            print("=" * 70)
            print(f"Running {len(modules)} tests...\n")
        
        for module in modules:
            result = self.run_single(module)
            self.report.results.append(result)
        
        self.report.completed_at = datetime.now()
        
        return self.report
    
    def run_core(self) -> TestReport:
        """Run core module tests only."""
        core_modules = [
            "syntax", "aetheric", "gin", "hrp", "bit4",
            "atlasforge", "deep_crystal", "core.integration"
        ]
        return self.run_all(core_modules)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ATHENA OS Test Runner")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Verbose output")
    parser.add_argument("-m", "--module", type=str, 
                       help="Test specific module")
    parser.add_argument("--core", action="store_true",
                       help="Test core modules only")
    parser.add_argument("--list", action="store_true",
                       help="List available modules")
    
    args = parser.parse_args()
    
    runner = AthenaTestRunner(verbose=args.verbose)
    
    if args.list:
        print("Available modules:")
        for module in sorted(runner.MODULES.keys()):
            print(f"  {module}")
        return 0
    
    if args.module:
        result = runner.run_single(args.module)
        if result.passed:
            print(f"✓ {args.module} passed ({result.duration:.3f}s)")
            return 0
        else:
            print(f"✗ {args.module} failed: {result.error}")
            return 1
    
    if args.core:
        report = runner.run_core()
    else:
        report = runner.run_all()
    
    print("\n" + report.summary())
    
    return 0 if report.failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
