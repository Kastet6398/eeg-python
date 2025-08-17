from __future__ import annotations
from typing import Dict, List, Tuple
from .ast import Formula, Var, Not, And, Or, eliminate_implications

Clause = List[int]  # integer literals, positive for var, negative for negated var
CNF = List[Clause]


class TseitinEncoder:
    def __init__(self) -> None:
        self.name_to_id: Dict[str, int] = {}
        self.id_to_name: Dict[int, str] = {}
        self.next_var_id: int = 1
        self.clauses: CNF = []

    def _new_var(self) -> int:
        vid = self.next_var_id
        self.next_var_id += 1
        return vid

    def _var_for_name(self, name: str) -> int:
        if name not in self.name_to_id:
            vid = self._new_var()
            self.name_to_id[name] = vid
            self.id_to_name[vid] = name
        return self.name_to_id[name]

    def encode(self, formula: Formula) -> int:
        f = eliminate_implications(formula)
        return self._encode_internal(f)

    def _encode_internal(self, formula: Formula) -> int:
        if isinstance(formula, Var):
            return self._var_for_name(formula.name)
        if isinstance(formula, Not):
            a = self._encode_internal(formula.operand)
            v = self._new_var()
            # v <-> ¬a  ==  (v ∨ a) ∧ (¬v ∨ ¬a)
            self.clauses.append([v, a])
            self.clauses.append([-v, -a])
            return v
        if isinstance(formula, And):
            a = self._encode_internal(formula.left)
            b = self._encode_internal(formula.right)
            v = self._new_var()
            # v <-> (a ∧ b)  ==  (¬v ∨ a) ∧ (¬v ∨ b) ∧ (¬a ∨ ¬b ∨ v)
            self.clauses.append([-v, a])
            self.clauses.append([-v, b])
            self.clauses.append([-a, -b, v])
            return v
        if isinstance(formula, Or):
            a = self._encode_internal(formula.left)
            b = self._encode_internal(formula.right)
            v = self._new_var()
            # v <-> (a ∨ b)  ==  (v ∨ ¬a) ∧ (v ∨ ¬b) ∧ (¬v ∨ a ∨ b)
            self.clauses.append([v, -a])
            self.clauses.append([v, -b])
            self.clauses.append([-v, a, b])
            return v
        raise TypeError(f"Unsupported formula node in CNF encoding: {type(formula)}")


def cnf_of_conjunction(formulas: List[Formula]) -> Tuple[CNF, Dict[int, str]]:
    encoder = TseitinEncoder()
    top_vars: List[int] = []
    for f in formulas:
        v = encoder.encode(f)
        top_vars.append(v)
        encoder.clauses.append([v])  # assert f is true
    return encoder.clauses, encoder.id_to_name


def cnf_with_negated_goal(axioms: List[Formula], goal: Formula) -> Tuple[CNF, Dict[int, str]]:
    formulas = list(axioms)
    from .ast import Not as NotNode
    formulas.append(NotNode(goal))
    return cnf_of_conjunction(formulas)