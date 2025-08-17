from typing import List, Tuple, Optional
from dataclasses import dataclass
from time import perf_counter
from z3 import Solver, BoolRef, Not, sat, unsat, unknown, set_param


@dataclass
class ProverResult:
	status: str  # PROVEN | DISPROVEN | UNKNOWN
	elapsed_ms: int
	model_sexpr: Optional[str] = None


class TheoremProver:
	def __init__(self, axioms: List[BoolRef], global_timeout_ms: Optional[int] = None):
		self.axioms = axioms
		self.global_timeout_ms = global_timeout_ms

	def prove_or_disprove(self, conjecture: BoolRef, timeout_ms: int) -> ProverResult:
		# prefer per-solver timeout; do not set global unless needed
		solver = Solver()
		if timeout_ms:
			set_param("timeout", timeout_ms)
		solver.add(self.axioms)

		start = perf_counter()
		# Try to prove: axioms ∧ ¬phi is UNSAT
		solver.push()
		solver.add(Not(conjecture))
		res = solver.check()
		if res == unsat:
			elapsed = int((perf_counter() - start) * 1000)
			solver.pop()
			return ProverResult(status="PROVEN", elapsed_ms=elapsed)
		elif res == sat:
			# Disproven: model satisfies axioms ∧ ¬phi
			m = solver.model()
			model_str = m.sexpr() if m is not None else None
			elapsed = int((perf_counter() - start) * 1000)
			solver.pop()
			return ProverResult(status="DISPROVEN", elapsed_ms=elapsed, model_sexpr=model_str)
		else:
			elapsed = int((perf_counter() - start) * 1000)
			solver.pop()
			return ProverResult(status="UNKNOWN", elapsed_ms=elapsed)