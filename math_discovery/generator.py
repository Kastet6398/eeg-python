from __future__ import annotations
import random
from typing import List
from .ast import (
    Term, TIntConst, TVar, TAdd, TSub, TMul,
    Fmla, FEq, FLt, FLe, FGt, FGe, FNot, FAnd, FOr, FImpl, FIff, FForall
)


def random_int_const() -> int:
    # small constants
    return random.choice([-2, -1, 0, 1, 2])


def gen_term(vars: List[str], depth: int) -> Term:
    if depth <= 0:
        if random.random() < 0.6:
            return TVar(random.choice(vars))
        else:
            return TIntConst(random_int_const())
    r = random.random()
    if r < 0.3:
        return TVar(random.choice(vars))
    if r < 0.5:
        return TIntConst(random_int_const())
    # binary op
    left = gen_term(vars, depth - 1)
    right = gen_term(vars, depth - 1)
    op = random.random()
    if op < 0.4:
        return TAdd(left, right)
    if op < 0.8:
        return TSub(left, right)
    return TMul(left, right)


def gen_atom(vars: List[str], depth: int) -> Fmla:
    left = gen_term(vars, depth)
    right = gen_term(vars, depth)
    r = random.random()
    if r < 0.5:
        return FEq(left, right)
    if r < 0.7:
        return FLe(left, right)
    if r < 0.85:
        return FGe(left, right)
    if r < 0.925:
        return FLt(left, right)
    return FGt(left, right)


def gen_formula(vars: List[str], depth: int) -> Fmla:
    if depth <= 0:
        return gen_atom(vars, 0)
    choice = random.random()
    if choice < 0.6:
        # binary connective
        left = gen_formula(vars, depth - 1)
        right = gen_formula(vars, depth - 1)
        op = random.random()
        if op < 0.33:
            return FAnd(left, right)
        if op < 0.66:
            return FOr(left, right)
        return FIff(left, right)
    if choice < 0.8:
        return FNot(gen_formula(vars, depth - 1))
    # atomic
    return gen_atom(vars, depth - 1)


def generate_random_conjecture(vars: List[str], max_depth: int, max_forall_vars: int = 2) -> Fmla:
    # Prefer universally quantified equalities to rediscover algebraic truths
    q_vars = random.sample(vars, k=min(len(vars), random.randint(1, max_forall_vars)))
    # Often generate an equality of terms
    if random.random() < 0.75:
        left = gen_term(q_vars, max_depth)
        right = gen_term(q_vars, max_depth)
        body = FEq(left, right)
    else:
        body = gen_formula(q_vars, max_depth)
    return FForall(q_vars, body)