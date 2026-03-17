"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Transport System                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Transport of mathematical objects through charts.
Core Transport Law: f_T := T⁻¹ ∘ f ∘ T
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, TypeVar
import math
import numpy as np

from atlasforge.lenses.chart import Chart

T = TypeVar('T')
S = TypeVar('S')


class Transport(ABC, Generic[T, S]):
    """Abstract base class for transport mechanisms."""
    
    @property
    @abstractmethod
    def source_chart(self) -> Chart:
        pass
    
    @property
    @abstractmethod
    def target_chart(self) -> Chart:
        pass
    
    @abstractmethod
    def transport_forward(self, obj: T) -> S:
        pass
    
    @abstractmethod
    def transport_backward(self, obj: S) -> T:
        pass


@dataclass
class FieldTransport(Transport[Callable, Callable]):
    """Transport of scalar/vector fields through charts."""
    chart: Chart
    
    @property
    def source_chart(self) -> Chart:
        return self.chart
    
    @property
    def target_chart(self) -> Chart:
        from atlasforge.lenses.canonical import IdentityLens
        return IdentityLens()
    
    def transport_forward(self, f: Callable) -> Callable:
        """f_T(y) = f(T⁻¹(y))"""
        def transported(y):
            x = self.chart.inverse(y)
            return f(x)
        return transported
    
    def transport_backward(self, f_T: Callable) -> Callable:
        """f(x) = f_T(T(x))"""
        def original(x):
            y = self.chart.forward(x)
            return f_T(y)
        return original


@dataclass
class OperatorTransport(Transport[Callable, Callable]):
    """Transport of operators through charts via conjugation: A_T = T⁻¹ ∘ A ∘ T"""
    chart: Chart
    
    @property
    def source_chart(self) -> Chart:
        return self.chart
    
    @property
    def target_chart(self) -> Chart:
        from atlasforge.lenses.canonical import IdentityLens
        return IdentityLens()
    
    def transport_forward(self, A: Callable[[Callable], Callable]) -> Callable:
        def transported_op(h: Callable) -> Callable:
            def h_source(x):
                y = self.chart.forward(x)
                return h(y)
            Ah_source = A(h_source)
            def result(y):
                x = self.chart.inverse(y)
                return Ah_source(x)
            return result
        return transported_op
    
    def transport_backward(self, A_T: Callable) -> Callable:
        def original_op(f: Callable) -> Callable:
            def f_chart(y):
                x = self.chart.inverse(y)
                return f(x)
            Af_chart = A_T(f_chart)
            def result(x):
                y = self.chart.forward(x)
                return Af_chart(y)
            return result
        return original_op


@dataclass
class ConstraintTransport(Transport[Any, Any]):
    """Transport of constraints: H(x)=0 becomes H_T(y)=H(T⁻¹(y))=0"""
    chart: Chart
    
    @property
    def source_chart(self) -> Chart:
        return self.chart
    
    @property
    def target_chart(self) -> Chart:
        from atlasforge.lenses.canonical import IdentityLens
        return IdentityLens()
    
    def transport_forward(self, H: Callable) -> Callable:
        def H_T(y):
            x = self.chart.inverse(y)
            return H(x)
        return H_T
    
    def transport_backward(self, H_T: Callable) -> Callable:
        def H(x):
            y = self.chart.forward(x)
            return H_T(y)
        return H
    
    def transport_root(self, x_star: float) -> float:
        return self.chart.forward(x_star)
    
    def transport_root_back(self, y_star: float) -> float:
        return self.chart.inverse(y_star)


@dataclass
class FlowTransport(Transport[Callable, Callable]):
    """Transport of flows: (φ_t)_T = T ∘ φ_t ∘ T⁻¹"""
    chart: Chart
    
    @property
    def source_chart(self) -> Chart:
        return self.chart
    
    @property
    def target_chart(self) -> Chart:
        from atlasforge.lenses.canonical import IdentityLens
        return IdentityLens()
    
    def transport_forward(self, phi: Callable[[float, Any], Any]) -> Callable:
        def transported_flow(t: float, y):
            x = self.chart.inverse(y)
            x_evolved = phi(t, x)
            return self.chart.forward(x_evolved)
        return transported_flow
    
    def transport_backward(self, phi_T: Callable) -> Callable:
        def original_flow(t: float, x):
            y = self.chart.forward(x)
            y_evolved = phi_T(t, y)
            return self.chart.inverse(y_evolved)
        return original_flow
    
    def transport_vector_field(self, V: Callable) -> Callable:
        """V_T(y) = T'(T⁻¹(y)) · V(T⁻¹(y))"""
        def V_T(y):
            x = self.chart.inverse(y)
            return self.chart.jacobian(x) * V(x)
        return V_T


@dataclass
class TransportChain:
    """A chain of transports for multi-step coordinate changes."""
    transports: List[Transport] = field(default_factory=list)
    
    def add(self, transport: Transport) -> 'TransportChain':
        self.transports.append(transport)
        return self
    
    def transport_forward(self, obj):
        result = obj
        for t in self.transports:
            result = t.transport_forward(result)
        return result
    
    def transport_backward(self, obj):
        result = obj
        for t in reversed(self.transports):
            result = t.transport_backward(result)
        return result
