"""ATHENA OS Integration Layer - Cross-Package Glue."""
from .core import (
    PackageLoader, load_package, get_metro_packages, get_tradition_packages,
    TypeCoercer, coerce,
    RuntimeLoop, RuntimeContext, RuntimeResult, execute,
    SystemVerifier, VerificationReport, verify_system,
    system_info, quick_boot
)
__all__ = [
    'PackageLoader', 'load_package', 'get_metro_packages', 'get_tradition_packages',
    'TypeCoercer', 'coerce',
    'RuntimeLoop', 'RuntimeContext', 'RuntimeResult', 'execute',
    'SystemVerifier', 'VerificationReport', 'verify_system',
    'system_info', 'quick_boot'
]

try:
    from .kernel import (
        GrandUnifiedKernel, KernelPhase,
        get_kernel, boot_kernel,
    )

    from .kernel import execute as kernel_execute, translate, status as kernel_status

    __all__ += [
        'GrandUnifiedKernel', 'KernelPhase',
        'get_kernel', 'boot_kernel',
        'kernel_execute', 'translate', 'kernel_status',
    ]
except Exception:
    pass
