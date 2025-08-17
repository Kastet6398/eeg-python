from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Union


class Formula:
    def atoms(self) -> Set[str]:
        raise NotImplementedError


@dataclass(frozen=True)
class Var(Formula):
    name: str

    def atoms(self) -> Set[str]:
        return {self.name}


@dataclass(frozen=True)
class Not(Formula):
    operand: Formula

    def atoms(self) -> Set[str]:
        return self.operand.atoms()


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def atoms(self) -> Set[str]:
        return self.left.atoms().union(self.right.atoms())


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def atoms(self) -> Set[str]:
        return self.left.atoms().union(self.right.atoms())


@dataclass(frozen=True)
class Impl(Formula):
    left: Formula
    right: Formula

    def atoms(self) -> Set[str]:
        return self.left.atoms().union(self.right.atoms())


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def atoms(self) -> Set[str]:
        return self.left.atoms().union(self.right.atoms())


def eliminate_implications(formula: Formula) -> Formula:
    if isinstance(formula, Var):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_implications(formula.operand))
    if isinstance(formula, And):
        return And(eliminate_implications(formula.left), eliminate_implications(formula.right))
    if isinstance(formula, Or):
        return Or(eliminate_implications(formula.left), eliminate_implications(formula.right))
    if isinstance(formula, Impl):
        # a -> b ≡ ¬a ∨ b
        return Or(Not(eliminate_implications(formula.left)), eliminate_implications(formula.right))
    if isinstance(formula, Iff):
        # a <-> b ≡ (a -> b) ∧ (b -> a)
        a = eliminate_implications(formula.left)
        b = eliminate_implications(formula.right)
        return And(Or(Not(a), b), Or(Not(b), a))
    raise TypeError(f"Unknown formula type: {type(formula)}")