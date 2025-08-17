from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from .ast import Formula
from .cnf import cnf_with_negated_goal
from .dpll import dpll


@dataclass
class ProverResult:
    status: str  # PROVEN, DISPROVEN, UNKNOWN
    counterexample: Dict[str, bool]


class Prover:
    def __init__(self, sat_node_limit: int = 20000) -> None:
        self.sat_node_limit = sat_node_limit

    def prove_or_disprove(self, axioms: List[Formula], conjecture: Formula) -> ProverResult:
        clauses, id_to_name = cnf_with_negated_goal(axioms, conjecture)
        result = dpll(clauses, assignment=None, node_limit=self.sat_node_limit)
        if result.sat is None:
            return ProverResult(status="UNKNOWN", counterexample={})
        if result.sat is False:
            # UNSAT: axioms ∧ ¬conjecture is UNSAT => axioms |= conjecture
            return ProverResult(status="PROVEN", counterexample={})
        # SAT: counterexample exists
        name_assignment: Dict[str, bool] = {}
        for vid, name in id_to_name.items():
            if vid in result.assignment:
                name_assignment[name] = result.assignment[vid]
        return ProverResult(status="DISPROVEN", counterexample=name_assignment)