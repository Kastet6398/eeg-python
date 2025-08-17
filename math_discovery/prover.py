from __future__ import annotations
from typing import List
from dataclasses import dataclass

from .parser import parse_math_formula
from .ast import Fmla
from .z3_backend import MathProver, MathProverResult


def parse_axioms(axioms_str: str) -> List[Fmla]:
    if not axioms_str:
        return []
    parts = [p.strip() for p in axioms_str.split(';') if p.strip()]
    return [parse_math_formula(p) for p in parts]


__all__ = [
    'parse_math_formula', 'parse_axioms', 'MathProver', 'MathProverResult'
]