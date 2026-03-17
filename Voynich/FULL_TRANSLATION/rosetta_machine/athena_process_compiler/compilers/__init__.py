"""
compilers -- IR construction, corridor routing, and artifact packaging for
the Athena Process Language.

Pipeline:
    list[ParsedToken]
      -> ir_builder.build()           -> list[OperatorIR]
      -> corridor_router.route()      -> list[RoutedToken]  (crystal coords + metro edges)
      -> packager.package()           -> PackagedArtifact   (content-addressed bundle)

Exports:
    ir_builder:       IRBuilder, build_ir()
    corridor_router:  CorridorRouter, route()
    packager:         ArtifactPackager, package_artifact()
"""

from athena_process_compiler.compilers.ir_builder import IRBuilder, build_ir
from athena_process_compiler.compilers.corridor_router import CorridorRouter, route
from athena_process_compiler.compilers.packager import ArtifactPackager, package_artifact
