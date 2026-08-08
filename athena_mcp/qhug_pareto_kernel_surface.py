from __future__ import annotations

from typing import Any,Dict

from .qhug_pareto_kernel import QhugParetoKernelRuntime
from .qhug_pareto_kernel_protocol import (
    QHUG_PARETO_KERNEL_RESOURCE,
    QHUG_PARETO_KERNEL_TOOLS,
    QHUG_PARETO_KERNEL_TOOL_NAMES,
)


class QhugParetoKernelSurface:
    def __init__(self):
        self.runtime=QhugParetoKernelRuntime()

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_qhug_kernel_analyze':return True,self.runtime.analyze(args)
        if name=='athena_qhug_pareto_solve':return True,self.runtime.solve(args)
        if name=='athena_qhug_decomposition_verify':return True,self.runtime.verify_decomposition(args)
        return False,None

    def read_resource(self,uri:str):
        if uri!=QHUG_PARETO_KERNEL_RESOURCE['uri']:raise KeyError(uri)
        return self.runtime.describe()

    def benchmark(self):
        return {'qhug_pareto_kernel':self.runtime.describe()}
