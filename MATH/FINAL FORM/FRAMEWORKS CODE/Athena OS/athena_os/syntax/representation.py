"""
ATHENA OS - SYNTAX REPRESENTATION TOWER
=======================================
SPIN/REVERSE-SPIN Dynamics

From SYNTAX.docx:

REPRESENTATION TOWER:
    Txt → Str → Mid → Obs
    
    The arrows are families of partial maps:
    - tokenize/parse/lower/compile/execute (SPIN)
    - decompile/unparse/abstract/infer (REVERSE-SPIN)
    
SPIN (Forward Realization):
    Source → Tokens → AST → IR → Observables
    
REVERSE-SPIN (Backward Abstraction):
    Observables → IR → AST → Tokens → Source
    
COMMUTATION REGIMES:
    Round-trip properties with bounded information loss.
    REVERSE-SPIN is explicitly tracked as non-inverse to SPIN
    except on stated normal-form fragments.
    
INFORMATION LOSS:
    Every transformation has a declared loss functional ℒ
    measuring how much information is discarded.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Set, Optional, Any, Tuple, 
    Callable, Union, TypeVar, Generic
)
from enum import Enum, auto
from abc import ABC, abstractmethod

from .core import (
    Pole, RepLevel, Direction,
    Artifact, SyntaxArtifact, AntiArtifact,
    TextArtifact, StructArtifact, MidArtifact,
    CollapseKind, CollapsePhase, Provenance,
    Observation, WorldState, ExecutionResult
)
from .coordinates import CrystalCoord


# =============================================================================
# TRANSFORMATION RESULT
# =============================================================================

@dataclass
class TransformResult:
    """
    Result of a representation transformation.
    
    Either success with artifact, or failure with anti-artifact.
    """
    
    success: bool
    artifact: Optional[SyntaxArtifact] = None
    failure: Optional[AntiArtifact] = None
    information_loss: float = 0.0
    
    @classmethod
    def ok(cls, artifact: SyntaxArtifact, loss: float = 0.0) -> 'TransformResult':
        """Create successful result."""
        return cls(success=True, artifact=artifact, information_loss=loss)
    
    @classmethod
    def fail(cls, failure: AntiArtifact) -> 'TransformResult':
        """Create failure result."""
        return cls(success=False, failure=failure)


# =============================================================================
# REPRESENTATION TRANSFORM
# =============================================================================

class RepTransform(ABC):
    """
    Abstract base for representation transformations.
    
    Each transform:
    - Has a source and target representation level
    - Has a direction (SPIN or REV)
    - May have information loss
    """
    
    def __init__(self, 
                 source: RepLevel, 
                 target: RepLevel,
                 direction: Direction,
                 name: str = ""):
        self.source = source
        self.target = target
        self.direction = direction
        self.name = name or f"{source.symbol}→{target.symbol}"
    
    @abstractmethod
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Apply the transformation."""
        pass
    
    @property
    def loss_functional(self) -> float:
        """
        Declared information loss ℒ for this transform.
        
        0.0 = lossless
        1.0 = total loss
        """
        return 0.0
    
    def __repr__(self) -> str:
        d_sym = "↓" if self.direction == Direction.SPIN else "↑"
        return f"{self.name} [{self.source.symbol} {d_sym} {self.target.symbol}]"


# =============================================================================
# SPIN TRANSFORMS (Forward)
# =============================================================================

class Tokenizer(RepTransform):
    """
    Tokenize: Txt → Str
    
    Convert source text to token stream.
    """
    
    def __init__(self, token_rules: Optional[Dict[str, str]] = None):
        super().__init__(RepLevel.TXT, RepLevel.STR, Direction.SPIN, "tokenize")
        self.token_rules = token_rules or {
            r'\s+': 'WHITESPACE',
            r'\d+': 'NUMBER',
            r'[a-zA-Z_]\w*': 'IDENTIFIER',
            r'[+\-*/=]': 'OPERATOR',
            r'[(){}[\]]': 'BRACKET',
        }
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Tokenize text artifact."""
        if artifact.rep_level != RepLevel.TXT:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.LEX,
                message=f"Expected TXT level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            # Simple tokenization
            import re
            text = artifact.content if isinstance(artifact, TextArtifact) else str(artifact.content)
            
            tokens = []
            pos = 0
            while pos < len(text):
                matched = False
                for pattern, token_type in self.token_rules.items():
                    match = re.match(pattern, text[pos:])
                    if match:
                        if token_type != 'WHITESPACE':
                            tokens.append((token_type, match.group()))
                        pos += len(match.group())
                        matched = True
                        break
                
                if not matched:
                    # Unknown character
                    tokens.append(('UNKNOWN', text[pos]))
                    pos += 1
            
            result = StructArtifact(
                content=tokens,
                grammar_id="simple_tokens",
                pole=Pole.S,
                rep_level=RepLevel.STR,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="tokenize"
                )
            )
            
            return TransformResult.ok(result, loss=0.05)  # Whitespace lost
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.LEXICAL,
                phase=CollapsePhase.LEX,
                message=str(e),
                original_artifact_id=artifact.artifact_id,
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    @property
    def loss_functional(self) -> float:
        return 0.05  # Whitespace information lost


class Parser(RepTransform):
    """
    Parse: Str → Str (tokens to AST)
    
    Build abstract syntax tree from tokens.
    """
    
    def __init__(self, grammar: Optional[Dict[str, Any]] = None):
        super().__init__(RepLevel.STR, RepLevel.STR, Direction.SPIN, "parse")
        self.grammar = grammar or {}
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Parse token stream to AST."""
        if artifact.rep_level != RepLevel.STR:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.PARSE,
                message=f"Expected STR level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            tokens = artifact.content
            
            # Simple expression parser
            ast = self._parse_expression(tokens)
            
            result = StructArtifact(
                content=ast,
                grammar_id="simple_ast",
                pole=Pole.S,
                rep_level=RepLevel.STR,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="parse"
                )
            )
            
            return TransformResult.ok(result, loss=0.0)
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SYNTACTIC,
                phase=CollapsePhase.PARSE,
                message=str(e),
                original_artifact_id=artifact.artifact_id,
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    def _parse_expression(self, tokens: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Simple recursive descent parser."""
        if not tokens:
            return {"type": "empty"}
        
        # Build simple AST from tokens
        ast = {"type": "program", "body": []}
        
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == 'NUMBER':
                ast["body"].append({"type": "literal", "value": int(token_value)})
            elif token_type == 'IDENTIFIER':
                ast["body"].append({"type": "identifier", "name": token_value})
            elif token_type == 'OPERATOR':
                ast["body"].append({"type": "operator", "op": token_value})
            elif token_type == 'BRACKET':
                ast["body"].append({"type": "bracket", "value": token_value})
            else:
                ast["body"].append({"type": "unknown", "value": token_value})
            
            i += 1
        
        return ast
    
    @property
    def loss_functional(self) -> float:
        return 0.0  # Lossless (tokens fully represented in AST)


class Compiler(RepTransform):
    """
    Compile: Str → Mid
    
    Lower AST to intermediate representation.
    """
    
    def __init__(self, target_ir: str = "bytecode"):
        super().__init__(RepLevel.STR, RepLevel.MID, Direction.SPIN, "compile")
        self.target_ir = target_ir
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Compile AST to IR."""
        if artifact.rep_level != RepLevel.STR:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=f"Expected STR level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            ast = artifact.content
            
            # Simple bytecode generation
            bytecode = self._generate_bytecode(ast)
            
            result = MidArtifact(
                content=bytecode,
                ir_type=self.target_ir,
                pole=Pole.S,
                rep_level=RepLevel.MID,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="compile"
                )
            )
            
            return TransformResult.ok(result, loss=0.1)
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=str(e),
                original_artifact_id=artifact.artifact_id,
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    def _generate_bytecode(self, ast: Dict[str, Any]) -> List[Tuple[str, Any]]:
        """Generate simple bytecode from AST."""
        bytecode = []
        
        if isinstance(ast, dict) and "body" in ast:
            for node in ast["body"]:
                if node["type"] == "literal":
                    bytecode.append(("PUSH", node["value"]))
                elif node["type"] == "identifier":
                    bytecode.append(("LOAD", node["name"]))
                elif node["type"] == "operator":
                    bytecode.append(("OP", node["op"]))
        
        return bytecode
    
    @property
    def loss_functional(self) -> float:
        return 0.1  # Some source info lost in compilation


class Executor(RepTransform):
    """
    Execute: Mid → Obs
    
    Run IR and produce observations.
    """
    
    def __init__(self, initial_state: Optional[WorldState] = None):
        super().__init__(RepLevel.MID, RepLevel.OBS, Direction.SPIN, "execute")
        self.initial_state = initial_state or WorldState(state_id="default")
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Execute IR and produce observations."""
        if artifact.rep_level != RepLevel.MID:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.RUNTIME,
                message=f"Expected MID level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            bytecode = artifact.content
            
            # Simple stack-based execution
            stack = []
            traces = []
            
            for op, arg in bytecode:
                if op == "PUSH":
                    stack.append(arg)
                    traces.append(f"PUSH {arg}")
                elif op == "LOAD":
                    val = self.initial_state.variables.get(arg, 0)
                    stack.append(val)
                    traces.append(f"LOAD {arg} = {val}")
                elif op == "OP":
                    if len(stack) >= 2:
                        b, a = stack.pop(), stack.pop()
                        if arg == '+':
                            result = a + b
                        elif arg == '-':
                            result = a - b
                        elif arg == '*':
                            result = a * b
                        elif arg == '/':
                            result = a / b if b != 0 else 0
                        else:
                            result = 0
                        stack.append(result)
                        traces.append(f"OP {a} {arg} {b} = {result}")
            
            observation = Observation(
                return_value=stack[-1] if stack else None,
                traces=traces
            )
            
            # Create observation artifact (special case)
            result = SyntaxArtifact(
                content=observation,
                pole=Pole.S,
                rep_level=RepLevel.OBS,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="execute"
                )
            )
            
            return TransformResult.ok(result, loss=0.5)  # Significant info loss
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.DYNAMIC,
                phase=CollapsePhase.RUNTIME,
                message=str(e),
                original_artifact_id=artifact.artifact_id,
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    @property
    def loss_functional(self) -> float:
        return 0.5  # Execution loses most source info


# =============================================================================
# REVERSE-SPIN TRANSFORMS (Backward)
# =============================================================================

class Decompiler(RepTransform):
    """
    Decompile: Mid → Str
    
    Lift IR back to AST (partial inverse of compile).
    """
    
    def __init__(self):
        super().__init__(RepLevel.MID, RepLevel.STR, Direction.REV, "decompile")
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Decompile IR to AST."""
        if artifact.rep_level != RepLevel.MID:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=f"Expected MID level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            bytecode = artifact.content
            
            # Reconstruct AST from bytecode
            ast = {"type": "program", "body": []}
            
            for op, arg in bytecode:
                if op == "PUSH":
                    ast["body"].append({"type": "literal", "value": arg})
                elif op == "LOAD":
                    ast["body"].append({"type": "identifier", "name": arg})
                elif op == "OP":
                    ast["body"].append({"type": "operator", "op": arg})
            
            result = StructArtifact(
                content=ast,
                grammar_id="decompiled_ast",
                pole=Pole.S,
                rep_level=RepLevel.STR,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="decompile"
                )
            )
            
            return TransformResult.ok(result, loss=0.2)
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=str(e),
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    @property
    def loss_functional(self) -> float:
        return 0.2  # Some structure lost in decompilation


class Unparser(RepTransform):
    """
    Unparse: Str → Txt
    
    Print AST back to source text (partial inverse of parse).
    """
    
    def __init__(self):
        super().__init__(RepLevel.STR, RepLevel.TXT, Direction.REV, "unparse")
    
    def transform(self, artifact: SyntaxArtifact) -> TransformResult:
        """Unparse AST to source text."""
        if artifact.rep_level != RepLevel.STR:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=f"Expected STR level, got {artifact.rep_level}",
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
        
        try:
            ast = artifact.content
            
            # Reconstruct source from AST
            parts = []
            
            if isinstance(ast, dict) and "body" in ast:
                for node in ast["body"]:
                    if node["type"] == "literal":
                        parts.append(str(node["value"]))
                    elif node["type"] == "identifier":
                        parts.append(node["name"])
                    elif node["type"] == "operator":
                        parts.append(f" {node['op']} ")
                    elif node["type"] == "bracket":
                        parts.append(node["value"])
            elif isinstance(ast, list):
                # Token list
                for token_type, token_value in ast:
                    parts.append(token_value)
            
            source = "".join(parts)
            
            result = TextArtifact(
                content=source,
                pole=Pole.S,
                rep_level=RepLevel.TXT,
                provenance=Provenance(
                    source_id=artifact.artifact_id,
                    operation="unparse"
                )
            )
            
            return TransformResult.ok(result, loss=0.1)
            
        except Exception as e:
            return TransformResult.fail(AntiArtifact(
                kind=CollapseKind.SEMANTIC,
                phase=CollapsePhase.VALIDATE,
                message=str(e),
                pole=Pole.A,
                rep_level=RepLevel.OBS
            ))
    
    @property
    def loss_functional(self) -> float:
        return 0.1  # Formatting lost


# =============================================================================
# REPRESENTATION TOWER
# =============================================================================

class RepresentationTower:
    """
    The complete representation tower with SPIN and REVERSE-SPIN paths.
    
    Txt ⇌ Str ⇌ Mid ⇌ Obs
    """
    
    def __init__(self):
        # SPIN transforms
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.compiler = Compiler()
        self.executor = Executor()
        
        # REVERSE-SPIN transforms
        self.decompiler = Decompiler()
        self.unparser = Unparser()
        
        # Transform registry
        self._spin: Dict[Tuple[RepLevel, RepLevel], RepTransform] = {
            (RepLevel.TXT, RepLevel.STR): self.tokenizer,
            (RepLevel.STR, RepLevel.MID): self.compiler,
            (RepLevel.MID, RepLevel.OBS): self.executor,
        }
        
        self._reverse: Dict[Tuple[RepLevel, RepLevel], RepTransform] = {
            (RepLevel.MID, RepLevel.STR): self.decompiler,
            (RepLevel.STR, RepLevel.TXT): self.unparser,
        }
    
    def spin(self, artifact: SyntaxArtifact, 
             target: RepLevel) -> TransformResult:
        """
        Apply SPIN transforms to reach target level.
        
        Returns the final artifact or failure.
        """
        current = artifact
        
        while current.rep_level < target:
            # Find next level
            levels = list(RepLevel)
            current_idx = levels.index(current.rep_level)
            next_level = levels[current_idx + 1]
            
            # Find transform
            transform = self._spin.get((current.rep_level, next_level))
            if transform is None:
                # Try parser for STR→STR
                if current.rep_level == RepLevel.STR and next_level == RepLevel.MID:
                    # Parse then compile
                    result = self.parser.transform(current)
                    if not result.success:
                        return result
                    current = result.artifact
                    continue
                
                return TransformResult.fail(AntiArtifact(
                    kind=CollapseKind.SEMANTIC,
                    phase=CollapsePhase.VALIDATE,
                    message=f"No transform from {current.rep_level} to {next_level}",
                    pole=Pole.A,
                    rep_level=RepLevel.OBS
                ))
            
            result = transform.transform(current)
            if not result.success:
                return result
            
            current = result.artifact
        
        return TransformResult.ok(current)
    
    def reverse_spin(self, artifact: SyntaxArtifact,
                     target: RepLevel) -> TransformResult:
        """
        Apply REVERSE-SPIN transforms to reach target level.
        """
        current = artifact
        
        while current.rep_level > target:
            # Find previous level
            levels = list(RepLevel)
            current_idx = levels.index(current.rep_level)
            prev_level = levels[current_idx - 1]
            
            # Find transform
            transform = self._reverse.get((current.rep_level, prev_level))
            if transform is None:
                return TransformResult.fail(AntiArtifact(
                    kind=CollapseKind.SEMANTIC,
                    phase=CollapsePhase.VALIDATE,
                    message=f"No reverse transform from {current.rep_level} to {prev_level}",
                    pole=Pole.A,
                    rep_level=RepLevel.OBS
                ))
            
            result = transform.transform(current)
            if not result.success:
                return result
            
            current = result.artifact
        
        return TransformResult.ok(current)
    
    def round_trip(self, artifact: SyntaxArtifact,
                   via: RepLevel) -> Tuple[TransformResult, float]:
        """
        Perform round-trip: artifact → via → back.
        
        Returns (result, total_loss).
        """
        original_level = artifact.rep_level
        
        # Spin down to target
        spin_result = self.spin(artifact, via)
        if not spin_result.success:
            return spin_result, 1.0
        
        # Spin back up
        reverse_result = self.reverse_spin(spin_result.artifact, original_level)
        if not reverse_result.success:
            return reverse_result, 1.0
        
        # Calculate total loss
        total_loss = min(1.0, spin_result.information_loss + reverse_result.information_loss)
        
        return reverse_result, total_loss
    
    def total_loss(self, source: RepLevel, target: RepLevel) -> float:
        """
        Calculate declared total information loss for path.
        """
        loss = 0.0
        
        levels = list(RepLevel)
        start_idx = levels.index(source)
        end_idx = levels.index(target)
        
        if start_idx < end_idx:
            # SPIN path
            for i in range(start_idx, end_idx):
                transform = self._spin.get((levels[i], levels[i+1]))
                if transform:
                    loss += transform.loss_functional
        else:
            # REVERSE-SPIN path
            for i in range(start_idx, end_idx, -1):
                transform = self._reverse.get((levels[i], levels[i-1]))
                if transform:
                    loss += transform.loss_functional
        
        return min(1.0, loss)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_representation() -> bool:
    """Validate representation tower module."""
    
    # Create tower
    tower = RepresentationTower()
    
    # Create source artifact
    source = TextArtifact(
        content="x + 1",
        pole=Pole.S,
        rep_level=RepLevel.TXT
    )
    
    # Test tokenization
    tok_result = tower.tokenizer.transform(source)
    assert tok_result.success
    assert tok_result.artifact.rep_level == RepLevel.STR
    
    # Test parsing
    parse_result = tower.parser.transform(tok_result.artifact)
    assert parse_result.success
    
    # Test compilation
    compile_result = tower.compiler.transform(parse_result.artifact)
    assert compile_result.success
    assert compile_result.artifact.rep_level == RepLevel.MID
    
    # Test execution
    tower.executor.initial_state = WorldState(
        state_id="test",
        variables={"x": 5}
    )
    exec_result = tower.executor.transform(compile_result.artifact)
    assert exec_result.success
    
    # Check result
    obs = exec_result.artifact.content
    assert obs.return_value == 6  # 5 + 1 = 6
    
    # Test decompilation
    decompile_result = tower.decompiler.transform(compile_result.artifact)
    assert decompile_result.success
    
    # Test unparsing
    unparse_result = tower.unparser.transform(decompile_result.artifact)
    assert unparse_result.success
    assert unparse_result.artifact.rep_level == RepLevel.TXT
    
    # Test SPIN path
    spin_result = tower.spin(source, RepLevel.MID)
    assert spin_result.success
    
    # Test round-trip
    mid_result = tower.spin(source, RepLevel.MID)
    if mid_result.success:
        round_result, loss = tower.round_trip(source, RepLevel.MID)
        assert round_result.success
        assert 0.0 <= loss <= 1.0
    
    # Test loss calculation
    loss = tower.total_loss(RepLevel.TXT, RepLevel.OBS)
    assert loss > 0.0  # Should have some loss
    
    return True


if __name__ == "__main__":
    print("Validating SYNTAX representation tower...")
    assert validate_representation()
    print("✓ SYNTAX representation tower validated")
