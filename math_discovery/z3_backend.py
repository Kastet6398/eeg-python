from __future__ import annotations
from typing import Dict, List, Tuple
from dataclasses import dataclass

from z3 import IntVal, Int, ForAll, Not as ZNot, And as ZAnd, Or as ZOr, Implies as ZImplies, Solver, sat, unsat
from .ast import (
    Term, TIntConst, TVar, TAdd, TSub, TMul,
    Fmla, FEq, FLt, FLe, FGt, FGe, FNot, FAnd, FOr, FImpl, FIff, FForall
)

# Translation

def term_to_z3(t: Term, env: Dict[str, object]):
    if isinstance(t, TIntConst):
        return IntVal(t.value)
    if isinstance(t, TVar):
        if t.name not in env:
            env[t.name] = Int(t.name)
        return env[t.name]
    if isinstance(t, TAdd):
        return term_to_z3(t.left, env) + term_to_z3(t.right, env)
    if isinstance(t, TSub):
        return term_to_z3(t.left, env) - term_to_z3(t.right, env)
    if isinstance(t, TMul):
        return term_to_z3(t.left, env) * term_to_z3(t.right, env)
    raise TypeError(f'Unknown term node: {type(t)}')


def fmla_to_z3(f: Fmla, env: Dict[str, object]):
    if isinstance(f, FEq):
        return term_to_z3(f.left, env) == term_to_z3(f.right, env)
    if isinstance(f, FLt):
        return term_to_z3(f.left, env) < term_to_z3(f.right, env)
    if isinstance(f, FLe):
        return term_to_z3(f.left, env) <= term_to_z3(f.right, env)
    if isinstance(f, FGt):
        return term_to_z3(f.left, env) > term_to_z3(f.right, env)
    if isinstance(f, FGe):
        return term_to_z3(f.left, env) >= term_to_z3(f.right, env)
    if isinstance(f, FNot):
        return ZNot(fmla_to_z3(f.inner, env))
    if isinstance(f, FAnd):
        return ZAnd(fmla_to_z3(f.left, env), fmla_to_z3(f.right, env))
    if isinstance(f, FOr):
        return ZOr(fmla_to_z3(f.left, env), fmla_to_z3(f.right, env))
    if isinstance(f, FImpl):
        return ZImplies(fmla_to_z3(f.left, env), fmla_to_z3(f.right, env))
    if isinstance(f, FIff):
        a = fmla_to_z3(f.left, env)
        b = fmla_to_z3(f.right, env)
        return ZAnd(ZImplies(a, b), ZImplies(b, a))
    if isinstance(f, FForall):
        # Create bound vars
        bound = [Int(v) for v in f.vars]
        body = fmla_to_z3(f.body, {**env, **{v: Int(v) for v in f.vars}})
        return ForAll(bound, body)
    raise TypeError(f'Unknown formula node: {type(f)}')


def negate_goal_with_witness(goal: Fmla) -> Tuple[object, Dict[str, object]]:
    # For Not(Forall vars . body) => Exists vars . Not(body)
    # We introduce fresh free constants for those vars to extract witnesses.
    if isinstance(goal, FForall):
        witness_env: Dict[str, object] = {}
        for v in goal.vars:
            witness_env[v] = Int(f"{v}_w")
        # Build Not(body) under env mapping bound vars to witness consts
        z3_body = fmla_to_z3(goal.body, dict(witness_env))
        return ZNot(z3_body), witness_env
    else:
        # quantifier-free goal: just negate it
        env: Dict[str, object] = {}
        return ZNot(fmla_to_z3(goal, env)), env


@dataclass
class MathProverResult:
    status: str
    counterexample: Dict[str, int]


class MathProver:
    def __init__(self) -> None:
        pass

    def prove_or_disprove(self, axioms: List[Fmla], conjecture: Fmla) -> MathProverResult:
        s = Solver()
        # assert axioms
        for ax in axioms:
            z = fmla_to_z3(ax, {})
            s.add(z)
        neg_goal, witness_env = negate_goal_with_witness(conjecture)
        s.add(neg_goal)
        r = s.check()
        if r == unsat:
            return MathProverResult(status='PROVEN', counterexample={})
        if r == sat:
            m = s.model()
            counter: Dict[str, int] = {}
            for name, sym in witness_env.items():
                if m.eval(sym, model_completion=True) is not None:
                    val = m.eval(sym, model_completion=True).as_long()
                    counter[name] = val
            return MathProverResult(status='DISPROVEN', counterexample=counter)
        return MathProverResult(status='UNKNOWN', counterexample={})