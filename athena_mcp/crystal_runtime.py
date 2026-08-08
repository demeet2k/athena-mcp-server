from __future__ import annotations
from .crystal_schema import CrystalBase
from .crystal_graph import CrystalGraphMixin
from .crystal_compile import CrystalCompileMixin
from .emission import EmissionMixin

class CrystalRuntime(CrystalBase,CrystalGraphMixin,CrystalCompileMixin,EmissionMixin):
    def __init__(self,core):
        self.core=core;self.s=core.s;self._install();self._install_emission()
    def benchmark_extension(self):
        q=lambda t:self.s.one(f"SELECT COUNT(*) n FROM {t}")['n']
        return {k:q(k) for k in ['hyperedges','math_objects','coordinate_charts','coordinates','transforms','transform_programs','transform_executions','holonomy_observations','crystals','emissions']}
