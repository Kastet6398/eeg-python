from __future__ import annotations
from dataclasses import dataclass
from typing import List

# Terms
class Term:
    pass

@dataclass(frozen=True)
class TIntConst(Term):
    value: int

@dataclass(frozen=True)
class TVar(Term):
    name: str

@dataclass(frozen=True)
class TAdd(Term):
    left: Term
    right: Term

@dataclass(frozen=True)
class TSub(Term):
    left: Term
    right: Term

@dataclass(frozen=True)
class TMul(Term):
    left: Term
    right: Term

# Formulas
class Fmla:
    pass

@dataclass(frozen=True)
class FEq(Fmla):
    left: Term
    right: Term

@dataclass(frozen=True)
class FLt(Fmla):
    left: Term
    right: Term

@dataclass(frozen=True)
class FLe(Fmla):
    left: Term
    right: Term

@dataclass(frozen=True)
class FGt(Fmla):
    left: Term
    right: Term

@dataclass(frozen=True)
class FGe(Fmla):
    left: Term
    right: Term

@dataclass(frozen=True)
class FNot(Fmla):
    inner: Fmla

@dataclass(frozen=True)
class FAnd(Fmla):
    left: Fmla
    right: Fmla

@dataclass(frozen=True)
class FOr(Fmla):
    left: Fmla
    right: Fmla

@dataclass(frozen=True)
class FImpl(Fmla):
    left: Fmla
    right: Fmla

@dataclass(frozen=True)
class FIff(Fmla):
    left: Fmla
    right: Fmla

@dataclass(frozen=True)
class FForall(Fmla):
    vars: List[str]
    body: Fmla