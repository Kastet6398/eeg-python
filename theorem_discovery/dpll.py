from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple

Clause = List[int]
CNF = List[Clause]
Assignment = Dict[int, bool]


class DPLLResult:
    def __init__(self, sat: Optional[bool], assignment: Assignment, nodes: int):
        self.sat = sat
        self.assignment = assignment
        self.nodes = nodes


def unit_propagate(clauses: CNF, assignment: Assignment) -> Tuple[Optional[CNF], Assignment]:
    changed = True
    while changed:
        changed = False
        unit_literals: List[int] = []
        for clause in clauses:
            if len(clause) == 0:
                return None, assignment  # conflict
            if len(clause) == 1:
                unit_literals.append(clause[0])
        if not unit_literals:
            break
        for lit in unit_literals:
            var = abs(lit)
            val = lit > 0
            if var in assignment:
                if assignment[var] != val:
                    return None, assignment  # conflict
                continue
            assignment[var] = val
            changed = True
            new_clauses: CNF = []
            for clause in clauses:
                if lit in clause:
                    continue  # clause satisfied
                if -lit in clause:
                    new_clause = [l for l in clause if l != -lit]
                    if len(new_clause) == 0:
                        return None, assignment
                    new_clauses.append(new_clause)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses
    return clauses, assignment


def pure_literal_elimination(clauses: CNF, assignment: Assignment) -> Tuple[CNF, Assignment]:
    literal_counts: Dict[int, int] = {}
    for clause in clauses:
        for lit in clause:
            literal_counts[lit] = literal_counts.get(lit, 0) + 1
    pures: Set[int] = set()
    vars_seen: Set[int] = set(abs(l) for l in literal_counts)
    for v in vars_seen:
        pos = literal_counts.get(v, 0)
        neg = literal_counts.get(-v, 0)
        if pos > 0 and neg == 0:
            pures.add(v)
        if neg > 0 and pos == 0:
            pures.add(-v)
    if not pures:
        return clauses, assignment
    new_clauses: CNF = []
    for clause in clauses:
        if any(l in pures for l in clause):
            continue
        new_clauses.append(clause)
    for lit in pures:
        assignment[abs(lit)] = lit > 0
    return new_clauses, assignment


def choose_variable(clauses: CNF, assignment: Assignment) -> Optional[int]:
    for clause in clauses:
        for lit in clause:
            v = abs(lit)
            if v not in assignment:
                return v
    return None


def dpll(clauses: CNF, assignment: Optional[Assignment] = None, node_limit: int = 100000) -> DPLLResult:
    if assignment is None:
        assignment = {}

    nodes = 0

    def recurse(clauses: CNF, assignment: Assignment) -> Optional[Assignment]:
        nonlocal nodes
        if nodes >= node_limit:
            return None

        # Unit propagation
        up_result = unit_propagate(clauses, dict(assignment))
        if up_result[0] is None:
            return False  # conflict
        clauses, assignment_after_up = up_result

        # All clauses satisfied
        if not clauses:
            return assignment_after_up

        # Pure literal elimination
        clauses, assignment_after_pure = pure_literal_elimination(clauses, dict(assignment_after_up))
        if not clauses:
            return assignment_after_pure

        var = choose_variable(clauses, assignment_after_pure)
        if var is None:
            return assignment_after_pure

        # Branch True then False
        for val in [True, False]:
            nodes += 1
            trial_assignment = dict(assignment_after_pure)
            trial_assignment[var] = val
            lit = var if val else -var
            new_clauses: CNF = []
            conflict = False
            for clause in clauses:
                if lit in clause:
                    continue
                if -lit in clause:
                    reduced = [l for l in clause if l != -lit]
                    if len(reduced) == 0:
                        conflict = True
                        break
                    new_clauses.append(reduced)
                else:
                    new_clauses.append(clause)
            if conflict:
                continue
            result = recurse(new_clauses, trial_assignment)
            if result is None:
                return None
            if result is not False:
                return result
        return False

    final_assignment = recurse(clauses, assignment)
    if final_assignment is None:
        return DPLLResult(sat=None, assignment=assignment, nodes=nodes)
    if final_assignment is False:
        return DPLLResult(sat=False, assignment=assignment, nodes=nodes)
    return DPLLResult(sat=True, assignment=final_assignment, nodes=nodes)