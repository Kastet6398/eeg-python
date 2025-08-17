from __future__ import annotations
import random
from typing import List
from .ast import Formula, Var, Not, And, Or, Impl, Iff


def generate_random_formula(variables: List[str], max_depth: int = 3) -> Formula:
    if max_depth <= 0:
        v = random.choice(variables)
        return Var(v)

    choice = random.random()
    if choice < 0.2:  # variable
        return Var(random.choice(variables))
    if choice < 0.35:  # negation
        return Not(generate_random_formula(variables, max_depth - 1))

    # binary operator
    left = generate_random_formula(variables, max_depth - 1)
    right = generate_random_formula(variables, max_depth - 1)
    op = random.random()
    if op < 0.33:
        return And(left, right)
    elif op < 0.66:
        return Or(left, right)
    elif op < 0.83:
        return Impl(left, right)
    else:
        return Iff(left, right)


def formula_to_string(f: Formula) -> str:
    if isinstance(f, Var):
        return f.name
    if isinstance(f, Not):
        return f"~{formula_to_string(f.operand)}"
    if isinstance(f, And):
        return f"({formula_to_string(f.left)} & {formula_to_string(f.right)})"
    if isinstance(f, Or):
        return f"({formula_to_string(f.left)} | {formula_to_string(f.right)})"
    if isinstance(f, Impl):
        return f"({formula_to_string(f.left)} -> {formula_to_string(f.right)})"
    if isinstance(f, Iff):
        return f"({formula_to_string(f.left)} <-> {formula_to_string(f.right)})"
    raise TypeError(f"Unknown formula type: {type(f)}")