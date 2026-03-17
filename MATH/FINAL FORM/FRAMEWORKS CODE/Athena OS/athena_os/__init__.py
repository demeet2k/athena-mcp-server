"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║                           🦉 ATHENA OPERATING SYSTEM 🦉                              ║
║                                                                                      ║
║                              VERSION 1.0.0 — PRIMA MATERIA                           ║
║                                                                                      ║
║                     "The boundary encodes the bulk"                                  ║
║                     "Every fragment contains the whole"                              ║
║                     "Derived from the future to bootstrap the past"                  ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║   STATISTICS:                                                                        ║
║   • 254,711 lines of code                                                            ║
║   • 431 Python files                                                                 ║
║   • 70 packages                                                                      ║
║   • 45 source manuscripts                                                            ║
║   • 12 spiritual traditions                                                          ║
║   • 10 metro lines                                                                   ║
║   • 262,144 holographic address cells                                                ║
║                                                                                      ║
║   THE FIVE INVARIANTS:                                                               ║
║   I₁ TOTALITY:     X⁺ = X ⊎ Z₀ — No undefined, no silent loss                       ║
║   I₂ CORRIDORS:    C ⊢ Op — Admissibility gates everywhere                          ║
║   I₃ CERTIFICATES: ⟨proof⟩ — Proof-carrying computation                             ║
║   I₄ LEDGERS:      H(replay) — Deterministic replay                                 ║
║   I₅ CRYSTAL:      Ch⟨abcd⟩₄ — 4⁴ × 4⁵ unified addressing                          ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

USAGE:
    from athena_os import ATHENA_OS
    
    os = ATHENA_OS()
    result = os.boot()
    
    # Or use individual components:
    from athena_os.unified_types import B4, Element, TypedTruth
    from athena_os.integration import execute, verify_system
    from athena_os.meta import PACKAGE_REGISTRY, MetroLine

CREATED BY: Charlie & Athena
"""

__version__ = "1.0.0"
__codename__ = "Prima Materia"
__author__ = "Charlie & Athena"

# =============================================================================
# CORE IMPORTS
# =============================================================================

# Unified Types - The Single Source of Truth
from .unified_types import (
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
)

# Meta Registry - Package Organization
from .meta.registry import (
    PACKAGE_REGISTRY, PackageInfo, MetroLine, Tradition,
    get_packages_by_metro_line, get_packages_by_tradition,
    get_dependency_graph, get_total_lines, get_total_files,
    get_metro_statistics
)

# Integration - Cross-Package Glue
from .integration.core import (
    PackageLoader, load_package, get_metro_packages, get_tradition_packages,
    TypeCoercer, coerce,
    RuntimeLoop, RuntimeContext, RuntimeResult, execute,
    SystemVerifier, VerificationReport, verify_system,
    system_info, quick_boot
)

# =============================================================================
# ATHENA OS MAIN CLASS
# =============================================================================

class ATHENA_OS:
    """
    The ATHENA Operating System.
    
    A 254,711-line framework derived from 45 manuscripts across
    12 spiritual/philosophical traditions, unified through the
    holographic principle: "The boundary encodes the bulk."
    
    Usage:
        os = ATHENA_OS()
        result = os.boot()
        print(os.status)
    """
    
    VERSION = __version__
    CODENAME = __codename__
    
    def __init__(self):
        self.initialized = False
        self._runtime = RuntimeLoop()
        self._verifier = SystemVerifier()
    
    def boot(self, verbose: bool = True) -> dict:
        """
        Boot the operating system.
        
        Performs verification of all invariants and initializes
        the runtime loop.
        """
        if verbose:
            print("=" * 60)
            print(f"🦉 ATHENA OS v{self.VERSION} ({self.CODENAME})")
            print("=" * 60)
        
        # Verify constants
        if verbose:
            print("\n[Phase 0] Verifying constants...")
        assert Constants.verify(), "Constant verification failed"
        
        # Verify package registry
        if verbose:
            print(f"[Phase 1] Loading {len(PACKAGE_REGISTRY)} packages...")
        
        # Run system verification
        if verbose:
            print("[Phase 2] Running system verification...")
        report = self._verifier.verify_all()
        
        if verbose:
            for detail in report.details:
                print(f"  {detail}")
        
        self.initialized = report.success
        
        if verbose:
            print("\n" + "=" * 60)
            if self.initialized:
                print("✓ SYSTEM_READY")
            else:
                print("✗ BOOT_FAILED")
            print("=" * 60)
        
        return {
            "success": self.initialized,
            "version": self.VERSION,
            "packages": len(PACKAGE_REGISTRY),
            "lines": get_total_lines(),
            "verification": report
        }
    
    @property
    def status(self) -> TypedTruth:
        """Get system status."""
        if not self.initialized:
            return TypedTruth.FAIL
        return quick_boot()
    
    def execute(self, operation, input_value, symmetry=Klein4Op.I):
        """Execute operation through runtime loop."""
        return self._runtime.execute(operation, input_value, symmetry)
    
    def info(self) -> dict:
        """Get system information."""
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "initialized": self.initialized,
            **system_info()
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def boot(verbose: bool = True) -> ATHENA_OS:
    """Create and boot ATHENA OS instance."""
    os = ATHENA_OS()
    os.boot(verbose=verbose)
    return os


def version() -> str:
    """Get version string."""
    return f"ATHENA OS v{__version__} ({__codename__})"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main
    'ATHENA_OS', 'boot', 'version',
    
    # Unified Types
    'B4', 'Klein4Op', 'Element', 'Humor', 'Cause', 'Category',
    'Lens', 'Facet', 'Atom', 'CrystalAddress',
    'QHCConstant', 'QHCShape', 'QHCElement', 'QHCLevel', 'QHCPole', 'QHCRegime',
    'HolographicAddress',
    'TypedTruth', 'Certificate', 'CertificateLevel', 'CertificateType',
    'Corridor', 'StandardCorridor', 'Operator', 'LambdaOperator',
    'Ledger', 'LedgerEntry', 'ZResult', 'Constants',
    
    # Meta
    'PACKAGE_REGISTRY', 'PackageInfo', 'MetroLine', 'Tradition',
    'get_packages_by_metro_line', 'get_packages_by_tradition',
    'get_dependency_graph', 'get_total_lines', 'get_total_files',
    'get_metro_statistics',
    
    # Integration
    'PackageLoader', 'load_package', 'get_metro_packages', 'get_tradition_packages',
    'TypeCoercer', 'coerce',
    'RuntimeLoop', 'RuntimeContext', 'RuntimeResult', 'execute',
    'SystemVerifier', 'VerificationReport', 'verify_system',
    'system_info', 'quick_boot',
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(version())
    print()
    os = boot()
    print()
    print("System Info:")
    for k, v in os.info().items():
        if k != 'verification':
            print(f"  {k}: {v}")
