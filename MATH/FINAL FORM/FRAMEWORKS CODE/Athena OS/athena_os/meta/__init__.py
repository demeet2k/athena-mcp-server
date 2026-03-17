"""ATHENA OS Meta Package - Package Registry and Organization."""
from .registry import (
    PACKAGE_REGISTRY, PackageInfo, MetroLine, Tradition,
    get_packages_by_metro_line, get_packages_by_tradition,
    get_dependency_graph, get_total_lines, get_total_files,
    get_metro_statistics
)
__all__ = [
    'PACKAGE_REGISTRY', 'PackageInfo', 'MetroLine', 'Tradition',
    'get_packages_by_metro_line', 'get_packages_by_tradition',
    'get_dependency_graph', 'get_total_lines', 'get_total_files',
    'get_metro_statistics'
]

try:
    from .correspondences import (
        Tradition, FourFoldCorrespondence, FOUR_FOLD_TABLE,
        NumericalCorrespondence, SACRED_NUMBERS,
        ProcessCorrespondence, TRANSFORMATION_STAGES,
        LensCorrespondence, LENS_TABLE,
        CauseCorrespondence, CAUSE_TABLE,
        TreeCorrespondence, WORLD_TREES,
        translate_element, translate_number, get_transformation_stage,
        print_four_fold_table,
    )

    __all__ += [
        'Tradition', 'FourFoldCorrespondence', 'FOUR_FOLD_TABLE',
        'NumericalCorrespondence', 'SACRED_NUMBERS',
        'ProcessCorrespondence', 'TRANSFORMATION_STAGES',
        'LensCorrespondence', 'LENS_TABLE',
        'CauseCorrespondence', 'CAUSE_TABLE',
        'TreeCorrespondence', 'WORLD_TREES',
        'translate_element', 'translate_number', 'get_transformation_stage',
        'print_four_fold_table',
    ]
except Exception:
    pass

try:
    from .coordinates import (
        MetroLine, PackageCoordinate,
        ALL_PACKAGES, PACKAGE_MAP,
        RED_LINE_PACKAGES, ORANGE_LINE_PACKAGES, YELLOW_LINE_PACKAGES,
        GREEN_LINE_PACKAGES, BLUE_LINE_PACKAGES, PURPLE_LINE_PACKAGES,
        WHITE_LINE_PACKAGES, GOLD_LINE_PACKAGES, SILVER_LINE_PACKAGES,
        COSMIC_LINE_PACKAGES,
        get_package_coordinate, get_packages_by_metro, get_packages_by_lens,
        get_package_at_index, print_metro_map, print_coordinate_table,
    )

    __all__ += [
        'MetroLine', 'PackageCoordinate',
        'ALL_PACKAGES', 'PACKAGE_MAP',
        'RED_LINE_PACKAGES', 'ORANGE_LINE_PACKAGES', 'YELLOW_LINE_PACKAGES',
        'GREEN_LINE_PACKAGES', 'BLUE_LINE_PACKAGES', 'PURPLE_LINE_PACKAGES',
        'WHITE_LINE_PACKAGES', 'GOLD_LINE_PACKAGES', 'SILVER_LINE_PACKAGES',
        'COSMIC_LINE_PACKAGES',
        'get_package_coordinate', 'get_packages_by_metro', 'get_packages_by_lens',
        'get_package_at_index', 'print_metro_map', 'print_coordinate_table',
    ]
except Exception:
    pass
